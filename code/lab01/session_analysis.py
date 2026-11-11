#!/usr/bin/env python3
"""Analyze the supplied 2026-11-04 session; no SDR or network access.
Usage: python code/lab01/session_analysis.py --recordings PATH
"""
from pathlib import Path
import argparse, hashlib, json, re
import numpy as np
from scipy import signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyze_iq import spectra, measure_roi, tone_estimate, burst_envelope

ROOT=Path(__file__).resolve().parents[2]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--recordings',type=Path,required=True)
    a=p.parse_args()
    out=ROOT/'data/lab01/session';out.mkdir(parents=True,exist_ok=True)
    images=ROOT/'assets/images/lab01/iq';images.mkdir(parents=True,exist_ok=True)
    inventory=[]
    for path in sorted(a.recordings.glob('*.cf32')):
        m=re.search(r'_(\d+)_(\d+)_([\d.]+)_(\d{8}T\d{6})\.cf32$',path.name)
        if not m or path.stat().st_size%8:raise ValueError(path)
        fc,fs,gain,stamp=m.groups();fs=float(fs);fc=float(fc)
        x=np.memmap(path,dtype='<c8',mode='r')
        h=hashlib.sha256();mi=mq=0.;power=0.;above=0
        for first in range(0,len(x),262144):
            z=np.asarray(x[first:first+262144]);h.update(z.tobytes())
            if not np.isfinite(z).all():raise ValueError('Nonfinite sample')
            mi=max(mi,float(abs(z.real).max()));mq=max(mq,float(abs(z.imag).max()))
            above+=int(np.count_nonzero((abs(z.real)>.5)|(abs(z.imag)>.5)))
            power+=float(np.sum(abs(z.astype(np.complex128))**2))
        inventory.append(dict(id=f'R{len(inventory)+1:02}',file=path.name,fc_hz=fc,fs_hz=fs,gain_db=float(gain),stamp=stamp,
            bytes=path.stat().st_size,samples=len(x),duration_s=len(x)/fs,sha256=h.hexdigest(),
            max_i=mi,max_q=mq,above_half_samples=above,mean_power=power/len(x),continuous_verified=False))
    def record(stamp):
        r=next(r for r in inventory if r['stamp'].endswith(stamp))
        return np.memmap(a.recordings/r['file'],dtype='<c8',mode='r'),r
    selections={
        '093112':[('downlink-A',941.85e6,946.65e6),('downlink-B',946.85e6,951.65e6)],
        '101301':[('gsm-9528',952.60e6,953.00e6)],
        '101056':[('remote',433.72e6,433.88e6)],
        '103042':[('uplink',897.7e6,901.4e6)]}
    measurements=[];settings=[]
    for stamp,rois in selections.items():
        x,r=record(stamp);fs=r['fs_hz'];fc=r['fc_hz'];nfft=8192 if fs==2.6e6 else 16384
        mean,hold,wf,edges,frames,tail=spectra(x,fs,nfft,max_rows=450)
        gated=None
        if stamp=='103042':
            # Locate the short broad uplink event using channel-filtered power.
            n=np.arange(len(x));y=signal.sosfilt(signal.butter(6,1.85e6,fs=fs,output='sos'),
                np.asarray(x)*np.exp(-2j*np.pi*(899.55e6-fc)*n/fs))
            step=2000;pwr=(abs(y[:len(y)//step*step])**2).reshape(-1,step).mean(axis=1)
            baseline=np.median(pwr[100:]);active=pwr>baseline*10
            ch=np.diff(np.r_[False,active,False].astype(int));runs=list(zip(np.where(ch==1)[0],np.where(ch==-1)[0]))
            begin,end=max(runs,key=lambda ab:ab[1]-ab[0]);gated=[begin*step/fs,end*step/fs]
            gmean,ghold,*_=spectra(x[begin*step:end*step],fs,nfft,max_rows=20)
        f=fc+np.fft.fftshift(np.fft.fftfreq(nfft,1/fs));df=fs/nfft
        # Conservative noise estimate from the lower fifth of the full-band
        # maximum spectrum. SNR here is a spectral peak/floor ratio, not C/N.
        floor=np.percentile(hold,20)
        fig,axes=plt.subplots(2,1,figsize=(11,6),layout='constrained')
        axes[0].plot(f/1e6,10*np.log10(np.maximum(hold,1e-30)),lw=.65,label='Frame maximum')
        axes[0].plot(f/1e6,10*np.log10(np.maximum(mean,1e-30)),lw=.7,label='Welch mean')
        for name,lo,hi in rois:
            mask=(f>=lo)&(f<=hi);snr=10*np.log10(hold[mask].max()/floor)
            roi=dict(id=name,roi_hz=[lo,hi],x_db=20 if snr>=26 else 6)
            selected_mean,selected_hold=(gmean,ghold) if gated else (mean,hold)
            result=measure_roi(f,selected_mean,selected_hold,roi,df)
            # Outermost threshold crossings bound a possibly notched signal.
            # Keep the original contiguous-peak result separately for auditing.
            result['contiguous_peak_bx_hz']=result['bx_hz']
            local=(f>=lo)&(f<=hi);rf=f[local];h=selected_hold[local]
            threshold=h.max()*10**(-roi['x_db']/10);inside=np.flatnonzero(h>=threshold)
            left,right=int(inside[0]),int(inside[-1]);clipped=left==0 or right==len(h)-1
            fl=fu=None
            if not clipped:
                hd=10*np.log10(h);level=10*np.log10(threshold)
                fl=float(np.interp(level,hd[left-1:left+1],rf[left-1:left+1]))
                fu=float(np.interp(level,hd[right:right+2][::-1],rf[right:right+2][::-1]))
            result.update(bx_lower_hz=fl,bx_upper_hz=fu,bx_hz=None if clipped else fu-fl,
                bx_clipped=clipped,time_gate_s=gated,
                notes='B99 includes ROI noise. Bx is the outer threshold extent of maximum Hann spectra, including internal notches; clipped crossings are not extrapolated.')
            result.update(file=r['file'],stamp=r['stamp'],fs_hz=fs,fc_hz=fc,
                peak_to_floor_db=float(snr),noise_floor_max_psd=float(floor),df_hz=df,
                roi_sensitivity=[])
            width=hi-lo
            for scale in [.9,1.1]:
                mid=(lo+hi)/2;l=mid-width*scale/2;u=mid+width*scale/2
                if l>=f[0] and u<=f[-1]:
                    alt=measure_roi(f,selected_mean,selected_hold,dict(roi,id=name,roi_hz=[l,u]),df)
                    result['roi_sensitivity'].append([scale,alt['obw99_hz']])
            measurements.append(result);axes[0].axvspan(lo/1e6,hi/1e6,alpha=.08)
        axes[0].set(ylabel='Relative PSD (dB/Hz)',title=r['stamp']);axes[0].legend();axes[0].grid(alpha=.2)
        # Maximum pooling retains every sample's frame in the plotted raster.
        view=wf.reshape(len(wf),1024,nfft//1024).max(axis=2)
        db=10*np.log10(np.maximum(view,1e-30))
        axes[1].pcolormesh(np.linspace((fc-fs/2)/1e6,(fc+fs/2)/1e6,1025),edges,db,
            shading='flat',vmin=np.percentile(db,15),vmax=np.percentile(db,99.8))
        axes[1].set(xlabel='Uncorrected RF label (MHz)',ylabel='Sample time (s)')
        fig.savefig(images/f'spectrum-{stamp}.png',dpi=145);plt.close(fig)
        settings.append(dict(stamp=r['stamp'],nfft=nfft,welch_frames=frames,tail_samples=tail,
                             waterfall_end_s=float(edges[-1]),time_rows=len(wf)))
        print('Spectrum',stamp,flush=True)
    loops=[]
    for stamp,search,ftx,shift in [
        ('094843',[433.70e6,433.80e6],-250000,0),('095024',[434.20e6,434.28e6],250000,0),
        ('095058',[434.26e6,434.34e6],250000,100000),
        ('095210',[434.26e6,434.34e6],250000,200000),
        ('095435',[434.26e6,434.34e6],250000,-100000)]:
        x,r=record(stamp)
        result=tone_estimate(x,r['fs_hz'],r['fc_hz'],dict(search_hz=search,f_tx_hz=ftx,rx_lo_shift_hz=shift))
        result.update(file=r['file'],stamp=r['stamp'],fc_hz=r['fc_hz'])
        loops.append(result)
    x,r=record('101056')
    remote={};envelope=None
    for threshold in [-58,-55,-52]:
        db,edges,b=burst_envelope(x,r['fs_hz'],r['fc_hz'],dict(center_hz=433790000,
            bandwidth_hz=80000,threshold_db_relative=threshold,step_s=.0001))
        ev=b['events'];groups=[]
        for event in ev:
            if not groups or event['start_s']-groups[-1]['end_s']>.008:
                groups.append(dict(start_s=event['start_s'],end_s=event['end_s'],pulses=1,
                                   censored=event['left_censored'] or event['right_censored']))
            else:
                groups[-1]['end_s']=event['end_s'];groups[-1]['pulses']+=1
                groups[-1]['censored']|=event['right_censored']
        # A trailing quiet symbol does not prove a whole packet was captured.
        # Conservatively exclude a group ending within 2 ms of the file edge.
        if groups and groups[-1]['end_s']>len(x)/r['fs_hz']-.002:groups[-1]['censored']=True
        complete=[g for g in groups if not g['censored']]
        b.update(groups=groups,complete_groups=len(complete),
                 group_width_median_s=float(np.median([g['end_s']-g['start_s'] for g in complete])),
                 group_period_median_s=float(np.median(np.diff([g['start_s'] for g in groups]))),
                 pulse_duration_median_s=float(np.median([e['duration_s'] for e in ev if not e['right_censored']])))
        remote[str(threshold)]=b
        if threshold==-55:envelope=(db,edges)
    fig,axes=plt.subplots(2,1,figsize=(11,5),layout='constrained');db,edges=envelope
    for ax in axes:ax.plot(edges[:-1],db,lw=.6);ax.axhline(-55,color='red',ls='--');ax.grid(alpha=.2)
    axes[1].set_xlim(.55,.72);axes[0].set(ylabel='Relative channel power (dB)',title='Remote: 80 kHz channel, 0.1 ms windows')
    axes[1].set(xlabel='Sample time (s)',ylabel='Relative channel power (dB)')
    fig.savefig(images/'remote-envelope.png',dpi=145);plt.close(fig)
    x,r=record('101301');fs=r['fs_hz'];fcch=[]
    for carrier in [952800000,953800000,955400000]:
        z=np.asarray(x)*np.exp(-2j*np.pi*(carrier-r['fc_hz'])*np.arange(len(x))/fs)
        y=signal.resample_poly(z,13,240);rate=fs*13/240
        y=signal.sosfilt(signal.butter(6,110000,fs=rate,output='sos'),y)
        tone=signal.sosfilt(signal.butter(5,8000,fs=rate,output='sos'),
            y*np.exp(-2j*np.pi*(1625000/24)*np.arange(len(y))/rate))
        step=54;count=len(y)//step
        whole=(abs(y[:count*step])**2).reshape(count,step).mean(axis=1)
        narrow=(abs(tone[:count*step])**2).reshape(count,step).mean(axis=1)
        active=narrow/np.maximum(whole,1e-30)>.65
        changes=np.diff(np.r_[False,active,False].astype(int));observations=[]
        for first,last in zip(np.where(changes==1)[0],np.where(changes==-1)[0]):
            if (last-first)*step/rate<.00015:continue
            lo=(first+1)*step;hi=(last-1)*step
            if hi-lo<80:continue
            offset=np.angle(np.sum(tone[lo+1:hi]*np.conj(tone[lo:hi-1])))*rate/(2*np.pi)
            observations.append(dict(start_s=first*step/rate,duration_s=(last-first)*step/rate,
                                     residual_hz=float(offset)))
        residual=np.array([v['residual_hz'] for v in observations]);nominal=carrier+1625000/24
        fcch.append(dict(carrier_nominal_hz=carrier,observations=observations,
            residual_median_hz=float(np.median(residual)),residual_std_hz=float(np.std(residual,ddof=1)),
            ppm=float((nominal/(nominal+np.median(residual))-1)*1e6)))
    gain=[r for r in inventory if r['fc_hz']==944530000 and r['fs_hz']==20e6]
    fig,axes=plt.subplots(1,2,figsize=(10,3.8),layout='constrained')
    gain=sorted(gain,key=lambda r:r['gain_db'])
    axes[0].plot([r['gain_db'] for r in gain],[max(r['max_i'],r['max_q']) for r in gain],'o-')
    axes[0].axhline(.5,color='red',ls='--');axes[0].set(xlabel='RX gain (dB)',ylabel='Maximum absolute I or Q');axes[0].grid(alpha=.2)
    for result in fcch:
        axes[1].scatter([v['start_s'] for v in result['observations']],
            [v['residual_hz'] for v in result['observations']],s=12,label=f"{result['carrier_nominal_hz']/1e6:.1f} MHz")
    axes[1].set(xlabel='Sample time (s)',ylabel='FCCH residual (Hz)');axes[1].legend();axes[1].grid(alpha=.2)
    fig.savefig(images/'gain-fcch.png',dpi=145);plt.close(fig)
    result=dict(format='little-endian complex float32, 8 bytes/sample',inventory=inventory,
        measurements=measurements,settings=settings,loopback=loops,remote=remote,fcch=fcch)
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps(dict(recordings=inventory),indent=2)+'\n',encoding='utf-8')
    print('Wrote',out,flush=True)

if __name__=='__main__':main()
