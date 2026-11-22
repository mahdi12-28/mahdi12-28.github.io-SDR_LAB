#!/usr/bin/env python3
"""Reproduce measurements from original screenshot pixels and explicit axes.

FFT trace readings are approximate dB relative, never calibrated dBm or dB/Hz.
The number-sink transcription is retained separately at its displayed precision.
"""
from pathlib import Path
import csv
import json
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import jv, jn_zeros

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
FIG = ROOT / 'figures'
FIG.mkdir(exist_ok=True)

# name, x(0 kHz), pixels/kHz, y(reference), dB(reference), pixels/dB, plot y range
AXES = [
 ('Part2_PLL_0.5.png',839,607/100,155,-50,109/50,10,420),
 ('Part2_PLL_0.3.png',812,615/40,348,-40,85.3/10,242,738),
 ('Part2_PLL_0.15.png',813,615/40,424,-40,80.7/20,242,738),
 ('Part2_PLL_0.08.png',813,615/40,417,-40,80.7/20,235,733),
 ('Part2_PLL_0.04.png',842,581/40,287,-40,119.7/20,239,735),
 ('Part2_PLL_0.02.png',826,577/40,280,-40,118/20,233,730),
 ('Part2_3_gain_40.png',886,490/40,367,-40,100.3/20,240,735),
 ('Part2_3_gain_27.png',890,490/40,369,-40,100.5/20,242,738),
 ('Part2_3_gain_20.png',890,490/40,363,-40,100.5/20,236,733),
]

def traces(axis):
    name,x0,sx,yref,dbref,sy,ylo,yhi=axis
    a=np.asarray(Image.open(ROOT/'assets'/'screenshots'/name).convert('RGB')).astype(int)
    x=np.arange(108,min(1565,a.shape[1]-1))
    out={}
    for color in ['blue','red']:
        c=a[:,:,2] if color=='blue' else a[:,:,0]
        other=np.maximum(a[:,:,0],a[:,:,1]) if color=='blue' else np.maximum(a[:,:,1],a[:,:,2])
        mask=(c>160)&(c-other>90)
        med=[];top=[]
        for xx in x:
            yy=np.flatnonzero(mask[ylo:yhi,xx])+ylo
            med.append(dbref-(np.median(yy)-yref)/sy if len(yy) else np.nan)
            top.append(dbref-(yy.min()-yref)/sy if len(yy) else np.nan)
        out[color]=(np.array(med),np.array(top))
    return (x-x0)/sx,out

def read_spectrum(axis):
    f,t=traces(axis)
    ans={'source':axis[0]}
    for color in t:
        median,top=t[color]
        peaks=[]
        floors=[]
        for sign in [-1,1]:
            p=top[np.abs(f-sign*19)<.45]
            peaks.append(float(np.nanmax(p)))
            floors.append(float(np.nanmedian(median[np.abs(f-sign*17)<.5])))
        ans[color+'_pilot_db']=float(np.mean(peaks))
        ans[color+'_noise17_db']=float(np.mean(floors))
        ans[color+'_pilot_margin_db']=ans[color+'_pilot_db']-ans[color+'_noise17_db']
    ans['delta_pilot_pll_minus_quad_db']=ans['red_pilot_db']-ans['blue_pilot_db']
    return ans

def write_csv(path, rows):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    rows=[read_spectrum(a) for a in AXES]
    # At 0.5 the coincident red trace obscures parts of the blue pilot.
    # Report the visible coincidence as approximately zero difference.
    rows[0]['delta_pilot_pll_minus_quad_db']=0.0
    bws=[.5,.3,.15,.08,.04,.02]
    quality=['خوب','خوب','خوب','متوسط','متوسط رو به پایین','بسیار ضعیف؛ بازیابی مفید صدا از بین رفت']
    pll=[]
    for r,b,q in zip(rows[:6],bws,quality):
        pll.append({'pll_bw':b,'BL_khz_manual_convention':1.06*b*240,'quality':q,**r})
    weak=[]
    for r,g,p,q in zip(rows[6:],[40,27,20],[-63.996273,-74.915482,-77.269608],['خوب','لب مرزی','نویز غالب؛ صدا قابل تشخیص نبود']):
        weak.append({'rf_gain_db':g,'channel_power_dbfs':p,'quality':q,**r})
    write_csv(DATA/'table05_pll.csv',pll)
    write_csv(DATA/'table06_weak_signal.csv',weak)
    (DATA/'spectrum_axes.json').write_text(json.dumps(AXES,indent=2))
    scalar=[
        {'quantity':'broadcast_fc_hz','value':90000000,'unit':'Hz','source':'Part1_f_finetune.png'},
        {'quantity':'carrier_offset_hz','value':1276.110229,'unit':'Hz','source':'Part1_freq_offset.png'},
        {'quantity':'fine_tuning_hz','value':-1350,'unit':'Hz','source':'Part1_f_finetune.png'},
        {'quantity':'broadcast_Pon','value':-70.692451,'unit':'dBFS','source':'Part1_channelPower.png'},
        {'quantity':'broadcast_Poff_adjacent','value':-72.003181,'unit':'dBFS','source':'Part1_emptyChannel_channelpower.png'},
        {'quantity':'tx_fc_hz','value':434000000,'unit':'Hz','source':'Part3_3_tx.png'},
        {'quantity':'tx_atten_db','value':70,'unit':'dB','source':'Part3_3_tx.png'},
        {'quantity':'tx_digital_amplitude','value':0.5,'unit':'relative','source':'Part3_7_fm=1000_dev=5000_tx.png'},
        {'quantity':'tx_tone_amplitude','value':1.0,'unit':'relative','source':'Part3_3_tx.png'},
        {'quantity':'cable_Poff','value':-78.250565,'unit':'dBFS','source':'Part3_3_rxPower.png'},
        {'quantity':'cable_Pon','value':-47.432655,'unit':'dBFS','source':'Part3_5.png'},
        {'quantity':'cable_SINAD','value':34.196014,'unit':'dB','source':'Part3_5.png'},
        {'quantity':'cable_fine_hz','value':2,'unit':'Hz','source':'Part3_4_rxsettings.png'},
        {'quantity':'cable_rx_dev_hz','value':75000,'unit':'Hz','source':'Part3_4_rxsettings.png'},
    ]
    write_csv(DATA/'number_sink_readings.csv',scalar)
    cnr=lambda on,off:float(10*np.log10(np.expm1((on-off)*np.log(10)/10)))
    bandwidth=[]
    txaxes=[('Part3_7_fm=1000_dev=5000_tx.png',885,647/100,422,131.25/50),
            ('Part3_7_fm=3000_dev=5000_tx.png',862,647/100,414,131.25/50)]
    spectra=[]
    for fm,axis in zip([1000,3000],txaxes):
        name,x0,sx,yzero,sy=axis
        a=np.asarray(Image.open(ROOT/'assets'/'screenshots'/name).convert('RGB')).astype(int)
        mask=(a[:,:,2]>160)&(a[:,:,2]-np.maximum(a[:,:,0],a[:,:,1])>90)
        lines=[]
        for n in range(-15,16):
            xs=int(round(x0+n*fm/1000*sx))
            y,x=np.where(mask[440:890,max(108,xs-2):xs+3])
            if len(y):lines.append((n,-(y.min()+440-yzero)/sy))
        maxdb=max(v for n,v in lines)
        # Equal FFT windows cancel in line-to-line relative levels.
        selected=[n for n,v in lines if v>=maxdb-20]
        b20=(max(selected)-min(selected))*fm
        n=np.arange(0,80);power=jv(n,5000/fm)**2
        enclosed=power[0]+2*np.cumsum(power[1:])
        n99=int(np.flatnonzero(enclosed>=.99)[0]+1)
        bandwidth.append({'fm_hz':fm,'dev_hz':5000,'beta':5000/fm,
            'B_carson_hz':2*(5000+fm),'B20_screenshot_hz':b20,
            'B99_bessel_theory_hz':2*n99*fm,'B99_measured_hz':None,
            'source':name,'threshold_db_below_strongest_line':20})
        spectra.append((fm,lines,maxdb))
    roots=jn_zeros(0,2)
    result={'broadcast_cnr_db_conditional_equal_gain_bandwidth':cnr(-70.692451,-72.003181),
            'broadcast_offset_ppm_apparent':1276.110229/90e6*1e6,
            'fine_tuning_magnitude_ppm':1350/90e6*1e6,
            'cable_cnr_db_conditional_equal_gain_bandwidth':cnr(-47.432655,-78.250565),
            'audio_gain_change_db':20*np.log10(2),
            'fft_bin_hz_4096':240000/4096,'fft_bin_hz_1024':240000/1024,
            'bessel_deviation_roots_hz_at_fm_1000':(roots*1000).tolist(),
            'bandwidth':bandwidth,'pll':pll,'weak_signal':weak}
    (DATA/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    write_csv(DATA/'table07_bandwidth.csv',bandwidth)
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,
                         'axes.titleweight':'bold','axes.labelcolor':'#234154','text.color':'#142d3d'})
    fig,ax=plt.subplots(figsize=(8,4.1),layout='constrained')
    ax.plot(bws,[r['delta_pilot_pll_minus_quad_db'] for r in pll],'o-',color='#087f8c',lw=2)
    ax.invert_xaxis();ax.set(xlabel='PLL loop parameter (rad/sample)',ylabel='Pilot level: PLL - discriminator (dB)',title='Pilot suppression from original screenshots')
    ax.grid(alpha=.2);fig.savefig(FIG/'pll_pilot.png',dpi=200);plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(10,3.7),layout='constrained')
    for ax,(fm,lines,mx) in zip(axs,spectra):
        xx=np.array([n*fm/1000 for n,v in lines]);yy=np.array([v-mx for n,v in lines])
        ax.vlines(xx,-100,yy,color='#087f8c');ax.plot(xx,yy,'o',ms=3,color='#087f8c')
        ax.axhline(-20,color='#c46532',ls='--');bc=2*(5000+fm)/1000
        ax.axvspan(-bc/2,bc/2,color='#087f8c',alpha=.1,label='Carson interval')
        ax.set(xlim=(-20,20),ylim=(-65,4),xlabel='Baseband frequency (kHz)',ylabel='Relative line power (dB)',title=f'Measured TX lines: fm = {fm/1000:g} kHz')
        ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.savefig(FIG/'measured_sidebands.png',dpi=200);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4),layout='constrained')
    for col,label in [('blue','Discriminator'),('red','PLL')]:
        ax.plot([40,27,20],[r[col+'_pilot_margin_db'] for r in weak],'o-',label=label,lw=2,color='#2375bb' if col=='blue' else '#c46532')
    ax.invert_xaxis();ax.set(xlabel='RX gain (dB)',ylabel='Visible peak - local noise floor (dB)',title='Pilot contrast in weak-signal records')
    ax.grid(alpha=.2);ax.legend();fig.savefig(FIG/'pilot_margin.png',dpi=200);plt.close(fig)
    print(json.dumps({k:v for k,v in result.items() if k not in ['pll','weak_signal']},indent=2))
    print('PLL',[(r['pll_bw'],round(r['delta_pilot_pll_minus_quad_db'],1)) for r in pll])
    print('WEAK',weak)

if __name__=='__main__': main()
