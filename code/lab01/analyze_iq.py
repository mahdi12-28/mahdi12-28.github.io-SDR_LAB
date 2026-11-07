#!/usr/bin/env python3
"""Reproducible, offline analysis of little-endian complex float32 recordings.
No SDR is accessed. No example measurement is substituted for a missing file.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import re
import numpy as np
from scipy import signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def positive(value, name):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f'{name} must be positive and finite')
    return value


def load_record(root, rec):
    if not rec.get('file'):
        raise ValueError(f'{rec.get("id")}: set a real file path first')
    path = (root / rec['file']).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Recording must be inside the repository')
    if not path.is_file():
        raise ValueError(f'Recording not found: {path}')
    if path.stat().st_size % 8:
        raise ValueError('cf32 size must be a multiple of 8 bytes')
    fs = positive(rec['fs_hz'], 'fs_hz')
    fc = positive(rec['fc_hz'], 'fc_hz')
    x = np.memmap(path, dtype='<c8', mode='r')
    nfft = int(rec.get('nfft', 4096))
    if nfft < 16 or nfft % 2 or len(x) < nfft:
        raise ValueError('Use an even nfft >=16 and a recording >=nfft samples')
    if 'continuous_verified' not in rec:
        raise ValueError('Set continuous_verified explicitly; file size alone is insufficient')
    return path, x, fs, fc, nfft


def spectra(x, fs, nfft, max_rows=1200):
    """Welch with 50% overlap; display aggregates ALL disjoint full frames.
    A final partial frame is zero-padded only in the waterfall, with its actual
    support retained. Welch discards a terminal partial frame as documented.
    """
    win = signal.windows.hann(nfft, sym=False)
    scale = fs * np.sum(win * win)
    hop = nfft // 2
    total = np.zeros(nfft)
    peak = np.zeros(nfft)
    nwin = 0
    # Batching limits memory independently of recording size.
    for first in range(0, len(x)-nfft+1, hop*128):
        starts = np.arange(first, min(first+hop*128, len(x)-nfft+1), hop)
        a = np.array([x[s:s+nfft] for s in starts])
        if not np.isfinite(a).all():
            raise ValueError('NaN/Inf in samples')
        power = abs(np.fft.fft(a*win, axis=1))**2 / scale
        total += power.sum(axis=0)
        peak = np.maximum(peak, power.max(axis=0))
        nwin += len(starts)
    nframes = math.ceil(len(x)/nfft)
    group = max(1, math.ceil(nframes/max_rows))
    waterfall, edges = [], [0.0]
    for start in range(0, len(x), group*nfft):
        end = min(start+group*nfft, len(x))
        a = np.asarray(x[start:end])
        if not np.isfinite(a).all():
            raise ValueError('NaN/Inf in samples')
        full, rem = divmod(len(a), nfft)
        rows = []
        if full:
            rows.extend(abs(np.fft.fft(a[:full*nfft].reshape(full,nfft)*win,axis=1))**2/scale)
        if rem:
            # Rectangular final window: Hann could erase a very short tail.
            tail = np.zeros(nfft, complex);tail[:rem] = a[-rem:]
            rows.append(abs(np.fft.fft(tail))**2/(fs*rem))
        waterfall.append(np.max(rows,axis=0))
        edges.append(end/fs)
    return (np.fft.fftshift(total/nwin), np.fft.fftshift(peak),
            np.fft.fftshift(np.asarray(waterfall), axes=1),
            np.asarray(edges), nwin, (len(x)-nfft)%hop)


def measure_roi(f, psd, maxpsd, roi, df):
    lo, hi = map(float, roi['roi_hz'])
    if not (f[0] <= lo < hi <= f[-1]+df):
        raise ValueError(f'ROI {roi["id"]} is outside recorded band')
    mask = (f>=lo)&(f<=hi)
    rf, power, hold = f[mask], psd[mask], maxpsd[mask]
    if len(rf)<5:
        raise ValueError('ROI must span at least five bins')
    mass = np.maximum(power,0)*df
    if mass.sum()<=0:
        raise ValueError('ROI has no positive power')
    # Quantiles interpolated within equal-width frequency bins.
    cdf = np.r_[0,np.cumsum(mass)]/mass.sum()
    boundaries = np.r_[rf-df/2,rf[-1]+df/2]
    f005,f995 = np.interp([.005,.995],cdf,boundaries)
    pk = int(np.argmax(hold))
    xdb = float(roi.get('x_db',6))
    if xdb not in (6,20):
        raise ValueError('x_db must be 6 or 20; choose using measured SNR')
    threshold = hold[pk]*10**(-xdb/10)
    left=pk;right=pk
    while left>0 and hold[left-1]>=threshold:left-=1
    while right<len(hold)-1 and hold[right+1]>=threshold:right+=1
    clipped = left==0 or right==len(hold)-1
    fl=fu=None
    if not clipped:
        db = 10*np.log10(np.maximum(hold,1e-30));target=db[pk]-xdb
        fl=float(np.interp(target, db[left-1:left+1],rf[left-1:left+1]))
        fu=float(np.interp(target, db[right:right+2][::-1],rf[right:right+2][::-1]))
    return {'id':roi['id'],'roi_hz':[lo,hi], 'obw99_hz':float(f995-f005),
            'obw99_lower_hz':float(f005),'obw99_upper_hz':float(f995),
            'obw99_midpoint_hz':float((f005+f995)/2),
            'power_centroid_hz':float(np.sum(rf*mass)/mass.sum()),
            'peak_hz':float(rf[np.argmax(power)]),
            'peak_psd_relative_db_per_hz':float(10*np.log10(max(power.max(),1e-30))),
            'x_db':xdb,'bx_hz':None if clipped else fu-fl,
            'bx_lower_hz':fl,'bx_upper_hz':fu,
            'bx_clipped':clipped,
            'notes':'B99 includes noise inside ROI; Bx uses maximum of Hann-windowed overlapping FFTs, not QT GUI Blackman-Harris.'}


def tone_estimate(x, fs, fc, tone):
    n = min(len(x),int(tone.get('fft_samples',1048576)))
    a = np.asarray(x[:n]);win=signal.windows.hann(n,sym=False)
    s = np.fft.fftshift(abs(np.fft.fft(a*win))**2)
    f = fc+np.fft.fftshift(np.fft.fftfreq(n,1/fs))
    lo,hi=map(float,tone['search_hz'])
    candidates=np.flatnonzero((f>=lo)&(f<=hi))
    if not len(candidates):raise ValueError('Tone search range outside band')
    k=int(candidates[np.argmax(s[candidates])])
    offset=0.
    if 0<k<n-1:
        y=np.log(np.maximum(s[k-1:k+2],1e-30));den=y[0]-2*y[1]+y[2]
        if den<0:offset=float(np.clip(.5*(y[0]-y[2])/den,-.5,.5))
    estimate=float(f[k]+offset*fs/n)
    expected=fc+float(tone['f_tx_hz'])-float(tone.get('rx_lo_shift_hz',0))
    # fc is ACTUAL RX label center. TX carrier is fc - rx_lo_shift.
    return {'estimate_hz':estimate,'expected_label_hz':expected,
            'error_hz':estimate-expected,'fft_bin_hz':fs/n,'samples_used':n,
            'method':'Hann FFT with log-parabolic peak interpolation; bin spacing is not an uncertainty bound.'}


def burst_envelope(x,fs,fc,cfg):
    """Stateful channel filtering and nonoverlapping power windows; no skips."""
    center=float(cfg['center_hz']);bw=positive(cfg['bandwidth_hz'],'bandwidth_hz')
    if abs(center-fc)+bw/2>=fs/2:raise ValueError('Burst channel is outside the band')
    step=max(1,round(fs*float(cfg.get('step_s',.0001))))
    sos=signal.butter(6,bw/2,fs=fs,output='sos')
    zi=np.zeros((len(sos),2),dtype=complex)
    pending=np.empty(0);powers=[];counts=[]
    for start in range(0,len(x),262144):
        a=np.asarray(x[start:start+262144]);idx=np.arange(start,start+len(a))
        y,zi=signal.sosfilt(sos,a*np.exp(-2j*np.pi*(center-fc)*idx/fs),zi=zi)
        z=np.r_[pending,abs(y)**2];n=len(z)//step
        if n:
            powers.extend(z[:n*step].reshape(n,step).mean(axis=1));counts.extend([step]*n)
        pending=z[n*step:]
    if len(pending):powers.append(pending.mean());counts.append(len(pending))
    power=np.asarray(powers);counts=np.asarray(counts)
    edges=np.r_[0,np.cumsum(counts)/fs];db=10*np.log10(np.maximum(power,1e-30))
    warmup=float(cfg.get('warmup_s',.002));threshold=float(cfg['threshold_db_relative'])
    valid=edges[:-1]>=warmup
    active=(db>=threshold)&valid
    events=[];begin=None
    for i,on in enumerate(np.r_[active,False]):
        if on and begin is None:begin=i
        if not on and begin is not None:
            events.append({'start_s':float(edges[begin]),'end_s':float(edges[i]),
                           'duration_s':float(edges[i]-edges[begin]),
                           'left_censored':begin==0 or not valid[begin-1],
                           'right_censored':i==len(active)})
            begin=None
    starts=np.array([e['start_s'] for e in events if not e['left_censored']])
    periods=np.diff(starts).tolist()
    return db,edges,{'events':events,'start_to_start_intervals_s':periods,
                     'threshold_db_relative':threshold,'time_step_s':step/fs,
                     'warmup_s':warmup,'channel_center_hz':center,'channel_bandwidth_hz':bw,
                     'notes':'Threshold crossings, not decoded packets; intervals may include missed/merged bursts. Censored events must not be used as complete durations.'}


def analyze(root,rec,out):
    path,x,fs,fc,nfft=load_record(root,rec)
    avg,hold,wf,tedges,nwin,discard=spectra(x,fs,nfft)
    f=fc+np.fft.fftshift(np.fft.fftfreq(nfft,1/fs));df=fs/nfft
    rid=rec['id'];out.mkdir(parents=True,exist_ok=True)
    def db(a):return 10*np.log10(np.maximum(a,1e-30))
    plt.rcParams.update({'font.size':10})
    fig,ax=plt.subplots(figsize=(10,4));ax.plot(f/1e6,db(hold),alpha=.6,label='Maximum over FFT frames');ax.plot(f/1e6,db(avg),label='Welch mean')
    ax.set(xlabel='RF label frequency (MHz)',ylabel='Relative PSD (dB / Hz)',title=rid+' | Hann, N='+str(nfft));ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(out/(rid+'-psd.png'),dpi=160);plt.close(fig)
    fedges=np.r_[f-df/2,f[-1]+df/2]/1e6
    fig,ax=plt.subplots(figsize=(10,5));im=ax.pcolormesh(fedges,tedges,db(wf),shading='flat',cmap='viridis');ax.set(xlabel='RF label frequency (MHz)',ylabel='Sample time (s)',title=rid+' | all samples; grouped frame maxima');fig.colorbar(im,ax=ax,label='Relative PSD (dB / Hz)');fig.tight_layout();fig.savefig(out/(rid+'-waterfall.png'),dpi=160);plt.close(fig)
    with (out/(rid+'-psd.csv')).open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['rf_label_hz','mean_psd_relative_per_hz','max_psd_relative_per_hz']);writer.writerows(zip(f,avg,hold))
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    result={'id':rid,'file':rec['file'],'sha256':h.hexdigest(),'samples':len(x),'size_bytes':path.stat().st_size,'fs_hz':fs,'fc_hz':fc,'nominal_duration_s':len(x)/fs,'continuous_verified':bool(rec['continuous_verified']), 'nfft':nfft,'fft_bin_hz':df,'welch_frames':nwin,'welch_tail_samples_not_used':discard,'waterfall_samples_used':len(x),'waterfall_display_rows':len(wf),'signals':[measure_roi(f,avg,hold,r,df) for r in rec.get('signals',[])], 'warnings':['No absolute RF power calibration. B99 includes in-ROI noise. File continuity requires independent evidence.']}
    if rec.get('tone'):result['tone']=tone_estimate(x,fs,fc,rec['tone'])
    if rec.get('bursts'):
        env,edges,b=burst_envelope(x,fs,fc,rec['bursts']);result['bursts']=b
        if not rec['continuous_verified']:result['warnings'].append('Burst timing uses sample count only; continuity is unverified.')
        fig,ax=plt.subplots(figsize=(10,4));ax.stairs(env,edges);ax.axhline(b['threshold_db_relative'],color='r',linestyle='--');ax.set(xlabel='Sample time (s)',ylabel='Relative channel power (dB)',title=rid+' | threshold crossings');fig.tight_layout();fig.savefig(out/(rid+'-bursts.png'),dpi=160);plt.close(fig)
        with (out/(rid+'-events.csv')).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=['start_s','end_s','duration_s','left_censored','right_censored']);writer.writeheader();writer.writerows(b['events'])
    (out/(rid+'.json')).write_text(json.dumps(result,indent=2,ensure_ascii=False))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('manifest',type=Path);parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);parser.add_argument('--out',type=Path)
    args=parser.parse_args();root=args.root.resolve();out=args.out or root/'data/lab01/analysis'
    manifest=json.loads(args.manifest.read_text());records=manifest.get('recordings',[])
    if not records:raise SystemExit('No recordings configured; add actual IQ files and metadata first.')
    ids=[r['id'] for r in records]
    if len(set(ids))!=len(ids) or any(not re.fullmatch(r'[a-zA-Z0-9_-]+',i) for i in ids):raise SystemExit('Recording ids must be unique ASCII slugs')
    results=[analyze(root,r,out) for r in records]
    (out/'summary.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
    print(f'Analyzed {len(results)} recording(s): {out}')
if __name__=='__main__':main()
