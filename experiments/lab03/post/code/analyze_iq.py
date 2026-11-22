#!/usr/bin/env python3
"""Analyze actual IQ files specified in data/iq_manifest.json.

No IQ paths are inferred. A blank path is a reserved report slot.
Outputs only derive from existing, explicitly configured captures.
Dependencies: numpy scipy matplotlib. Example: python code/analyze_iq.py
"""
from pathlib import Path
import argparse, json, hashlib
import numpy as np
from scipy import signal
from scipy.io import wavfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]

def load_iq(path,fmt):
    if fmt=='cf32_le':
        if path.stat().st_size%8:raise ValueError('cf32 file size must be divisible by 8')
        x=np.memmap(path,dtype='<c8',mode='r')
    elif fmt=='ci16_le':
        if path.stat().st_size%4:raise ValueError('ci16 file size must be divisible by 4')
        raw=np.fromfile(path,dtype='<i2').reshape(-1,2).astype(np.float32)/32768
        x=raw[:,0]+1j*raw[:,1]
    else:raise ValueError('format must be cf32_le or ci16_le')
    if len(x)<4096 or not np.isfinite(x).all():raise ValueError('IQ requires >=4096 finite samples')
    return x

def psd(x,fs,nfft=16384):
    f,p=signal.welch(x,fs=fs,window='hann',nperseg=min(nfft,len(x)),
                     noverlap=min(nfft,len(x))//2,return_onesided=False,detrend=False,scaling='density')
    return np.fft.fftshift(f),np.fft.fftshift(p)

def occupied_bw(f,p,band):
    m=(f>=band[0])&(f<=band[1]);f=f[m];p=p[m]
    if len(f)<4 or p.sum()<=0:raise ValueError('analysis band contains no positive power')
    c=np.cumsum(p)/p.sum()
    # Frequency boundaries are bin edges, so include the selected bins' width.
    df=f[1]-f[0];lo=f[np.searchsorted(c,.005)]-df/2;hi=f[np.searchsorted(c,.995)]+df/2
    return float(lo),float(hi),float(hi-lo)

def quad_audio(x,fs,dev,audio_bw=15000,tau_us=75):
    cutoff=min(dev+audio_bw,100000)
    channel_sos=signal.butter(8,cutoff,fs=fs,output='sos')
    x=signal.sosfilt(channel_sos,x)
    y=np.angle(x[1:]*np.conj(x[:-1]))*(fs/(2*np.pi*dev))
    y=y-np.mean(y)
    sos=signal.butter(6,audio_bw,fs=fs,output='sos');y=signal.sosfilt(sos,y)
    from fractions import Fraction
    frac=Fraction(48000,int(fs));y=signal.resample_poly(y,frac.numerator,frac.denominator)
    # First-order de-emphasis using the bilinear transform.
    if tau_us:
        b,a=signal.bilinear([1],[tau_us*1e-6,1],fs=48000);y=signal.lfilter(b,a,y)
    peak=np.max(np.abs(y))
    return (y*(.9/peak) if peak else y).astype(np.float32)

def self_test():
    fs=240000;n=np.arange(fs);fm=3000;dev=5000
    x=np.exp(1j*(dev/fm)*np.sin(2*np.pi*fm*n/fs)).astype(np.complex64)
    f,p=psd(x,fs);lo,hi,bw=occupied_bw(f,p,[-30000,30000])
    assert abs(bw-18000)<200,(lo,hi,bw)
    y=np.angle(x[1:]*x[:-1].conj())*fs/(2*np.pi*dev)
    expected=np.cos(2*np.pi*fm*(n[1:]-.5)/fs)*np.sinc(fm/fs)
    assert np.max(np.abs(y-expected))<1e-4
    a=quad_audio(x,fs,dev,3000,0)
    assert np.isfinite(a).all() and len(a)>47000
    print('Synthetic verification passed: known FM B99, discriminator scaling, audio resampling.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=Path,default=ROOT/'data'/'iq_manifest.json')
    ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    if args.self_test:self_test();return
    manifest=json.loads(args.manifest.read_text());result=[]
    outdir=ROOT/'iq'/'analysis';outdir.mkdir(exist_ok=True,parents=True)
    for c in manifest['captures']:
        if not c.get('path'):continue
        path=(ROOT/c['path']).resolve()
        if not path.is_file():raise FileNotFoundError(path)
        if c.get('fs_hz') is None or c.get('dev_hz') is None:raise ValueError('Set actual fs_hz and dev_hz for each capture')
        fs=float(c['fs_hz']);x=load_iq(path,c.get('format','cf32_le'))
        # Apply the explicitly declared residual center correction before analysis.
        if c.get('frequency_shift_hz',0):
            x=x*np.exp(-2j*np.pi*c['frequency_shift_hz']*np.arange(len(x))/fs)
        f,p=psd(x,fs);band=c.get('analysis_band_hz',[-30000,30000]);pn=None
        if c.get('noise_path'):
            if c.get('noise_rf_gain_db')!=c.get('rf_gain_db'):raise ValueError('Signal/noise RX gain must match')
            xn=load_iq((ROOT/c['noise_path']).resolve(),c.get('format','cf32_le'))
            fn,pn=psd(xn,fs)
            if not np.array_equal(fn,f):raise ValueError('Signal/noise PSD grids differ')
        clean=np.maximum(p-pn,0) if pn is not None else p
        lo,hi,bw=occupied_bw(f,clean,band)
        row={'id':c['id'],'path':c['path'],'n_samples':len(x),'duration_s':len(x)/fs,
             'fs_hz':fs,'rf_gain_db':c.get('rf_gain_db'),'dev_hz':c['dev_hz'],
             'analysis_band_hz':band,'B99_hz':bw,'f_low_hz':lo,'f_high_hz':hi,
             'noise_subtracted':pn is not None,'sha256':hashlib.file_digest(path.open('rb'),'sha256').hexdigest()}
        if pn is not None:
            m=(f>=band[0])&(f<=band[1]);ratio=(p[m].sum()-pn[m].sum())/pn[m].sum()
            row['CNR_db']=float(10*np.log10(ratio)) if ratio>0 else None
        stem=c['id'];fig,ax=plt.subplots(figsize=(8,4),layout='constrained')
        ax.plot(f/1000,10*np.log10(np.maximum(p,1e-30)));ax.axvspan(lo/1000,hi/1000,alpha=.15,color='teal')
        ax.set(xlim=np.array(band)/1000,xlabel='Baseband frequency (kHz)',ylabel='PSD (dB relative/Hz)',title=stem+' | measured IQ')
        ax.grid(alpha=.2);fig.savefig(outdir/(stem+'_psd.png'),dpi=180);plt.close(fig)
        audio=quad_audio(x,fs,float(c['dev_hz']),c.get('audio_bw_hz',15000),c.get('tau_us',75))
        wavfile.write(outdir/(stem+'_quad.wav'),48000,audio)
        row['audio_path']='iq/analysis/'+stem+'_quad.wav';row['psd_path']='iq/analysis/'+stem+'_psd.png'
        result.append(row)
    (ROOT/'data'/'iq_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (ROOT/'data'/'iq_results.js').write_text('window.LAB03_IQ_RESULTS = '+json.dumps(result,ensure_ascii=False)+';\n')
    print(f'Analyzed {len(result)} configured captures. Report slots update through data/iq_results.js.')

if __name__=='__main__':main()
