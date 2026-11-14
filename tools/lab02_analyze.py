#!/usr/bin/env python3
"""Reproduce Lab 02 calculations and plots. Requires numpy, matplotlib, openpyxl."""
from pathlib import Path
import json
import csv
import numpy as np
import openpyxl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/lab02/post'
DATA = OUT / 'data'
FIG = OUT / 'figures'
FIG.mkdir(parents=True, exist_ok=True)
raw = json.loads((DATA / 'readings.json').read_text())
enr = raw['provenance']['nominal_enr_db']
noise = []
for r in raw['noise']:
    y = r['on_dbfs'] - r['off_dbfs']
    Y = 10 ** (y / 10)
    q = 10 * np.log10(Y - 1)
    direct = r['open_dbfs'] - 20 - 10 * np.log10(400000) + 174
    noise.append(dict(r, y_db=y, y_linear=Y, q_db=q,
                      nf_y_algebraic_db=enr-q, nf_y_physical=bool(enr-q >= 0),
                      nf_direct_gfs20_db=direct,
                      nf_direct_gain_adjusted_db=direct-(r['gain_db']-40.2),
                      sensitivity=Y/(Y-1),
                      nf_shift_y_plus_point1_db=-10*np.log10((10**((y+.1)/10)-1)/(Y-1)),
                      nf_shift_y_minus_point1_db=-10*np.log10((10**((y-.1)/10)-1)/(Y-1))))
wb = openpyxl.load_workbook(DATA / 'P1db.xlsx', data_only=True)
v = np.array(list(wb.active.values)[1:], dtype=float)
# Workbook stores attenuation with a negative sign. Use its positive magnitude.
A = -v[:, 0]
pin = -35.5 - A
pout = v[:, 1]
# Unit-slope small-signal reference, fitted to the first 3 low-input points.
C = float(np.mean(pout[:3] - pin[:3]))
compression = pin + C - pout
sweep_slope = float(np.polyfit(pin, pout, 1)[0])
sweep = [dict(attenuation_db=float(a), input_nominal_dbm=float(x), output_dbfs=float(y),
              mixed_scale_offset_db=float(y-x), compression_db=float(c))
         for a,x,y,c in zip(A,pin,pout,compression)]
two = raw['two_tone']
ta = np.array([r['attenuation_db'] for r in two])
tx = -35.5-ta
t = np.array([[r['f1_dbfs'],r['f2_dbfs']] for r in two])
im = np.array([[r['im3_low_dbfs'],r['im3_high_dbfs']] for r in two])
powermean = lambda z: 10*np.log10(np.mean(10**(z/10),axis=1))
tm, imm = powermean(t), powermean(im)
delta = tm-imm
floors = np.array(raw['two_tone_floor_dbfs'][2:])
im_corrected = 10*np.log10(10**(im/10)-10**(floors/10))
two_results = [dict(r,input_nominal_per_tone_dbm=float(x),fundamental_powermean_dbfs=float(a),
                    im3_powermean_dbfs=float(b),delta_db=float(d),
                    apparent_iip3_dbm=float(x+d/2))
               for r,x,a,b,d in zip(two,tx,tm,imm,delta)]
f,p = np.loadtxt(DATA/'Part5_antenna_response.csv',delimiter=',',skiprows=1).T
f = f/1e6
k = int(np.argmax(p))
def crossings(drop):
    threshold=p[k]-drop
    lo=hi=k
    while lo>0 and p[lo]>=threshold: lo-=1
    while hi<len(p)-1 and p[hi]>=threshold: hi+=1
    fl=float(np.interp(threshold,p[lo:lo+2],f[lo:lo+2]))
    fh=float(np.interp(threshold,p[hi-1:hi+1][::-1],f[hi-1:hi+1][::-1]))
    return dict(drop_db=drop,threshold_db=float(threshold),f_low_mhz=fl,f_high_mhz=fh,
                bandwidth_mhz=fh-fl,bracket_low_mhz=f[lo:lo+2].tolist(),
                bracket_high_mhz=f[hi-1:hi+1].tolist())
antenna=dict(samples=len(f),step_mhz=float(f[1]-f[0]),peak_mhz=float(f[k]),
             peak_db_relative=float(p[k]),link_3db=crossings(3),pair_6db=crossings(6))
results=dict(noise=noise,single_tone=sweep,small_signal_offset=C,
             single_tone_slope=sweep_slope,max_observed_compression_db=float(max(compression)),
             two_tone=two_results,fundamental_slopes=np.polyfit(tx,t,1)[0].tolist(),
             im3_slopes=np.polyfit(tx,im,1)[0].tolist(),
             im3_slopes_noise_subtracted=np.polyfit(tx,im_corrected,1)[0].tolist(),
             delta_mean_db=float(delta.mean()),delta_std_across_levels_db=float(delta.std()),
             max_tone_imbalance_db=float(abs(t[:,0]-t[:,1]).max()),
             minimum_im3_margin_above_floor_db=float((im-floors).min()),antenna=antenna)
(DATA/'analysis_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
for name,rows in [('single_tone_analysis.csv',sweep),('two_tone_analysis.csv',two_results)]:
    with (DATA/name).open('w',newline='') as fcsv:
        w=csv.DictWriter(fcsv,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,
                     'svg.fonttype':'none'})
colors=['#146a54','#cb7d34','#355c8c','#9c536d']
def save(fig,name):
    fig.savefig(FIG/(name+'.svg'),bbox_inches='tight')
    fig.savefig(FIG/(name+'.png'),dpi=190,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(8.2,3.7))
g=[r['gain_db'] for r in noise]
ax.plot(g,[r['nf_direct_gfs20_db'] for r in noise],'o-',color=colors[0],label='Direct, fixed GFS = 20 dB (guide calculation)')
ax.plot(g,[r['nf_direct_gain_adjusted_db'] for r in noise],'s--',color=colors[2],label='Direct, GFS = 20 + (gain - 40.2), conditional')
ax.scatter([40.2],[noise[1]['nf_y_algebraic_db']],s=85,marker='D',color=colors[1],label='Y-factor, ENR = 15 dB, gain 40.2')
ax.set(xlabel='RX gain setting (dB)',ylabel='Noise figure (dB)',xticks=g,ylim=(15,39))
ax.legend(fontsize=8,loc='upper right');fig.tight_layout();save(fig,'noise-vs-gain')

fig,(ax,bx)=plt.subplots(2,1,figsize=(8.2,5.8),sharex=True,gridspec_kw={'height_ratios':[2,1]})
ax.plot(pin,pout,'o-',color=colors[0],label='Single-tone workbook')
ax.plot(pin,pin+C,'--',color=colors[2],label='Unit-slope small-signal reference')
ax.plot(pin,pin+C-1,':',color=colors[1],label='1 dB compression criterion')
ax.set(ylabel='Output meter (dBFS)');ax.legend(fontsize=8)
bx.plot(pin,compression,'o-',color=colors[0]);bx.axhline(1,color=colors[1],ls=':')
bx.set(xlabel='Nominal single-tone input (dBm), guide mapping',ylabel='Compression (dB)',ylim=(-.2,1.2))
fig.tight_layout();save(fig,'single-tone')

fig,ax=plt.subplots(figsize=(8.2,4.3))
ax.plot(pin,pout,'o-',color='#7c8b81',label='Single-tone workbook')
for i,label in enumerate(['f1','f2']):
    ax.plot(tx,t[:,i],['o-','s--'][i],color=colors[i],ms=4,label=f'Two-tone {label}, slope {results["fundamental_slopes"][i]:.3f}')
for i,label in enumerate(['2f1-f2','2f2-f1']):
    ax.plot(tx,im[:,i],['^-','v--'][i],color=colors[i+2],ms=4,label=f'{label}, slope {results["im3_slopes"][i]:.3f}')
ax.axhline(float(floors.mean()),ls=':',color='#777',label='10 kHz sideband noise floor')
ax.set(xlabel='Nominal input per tone (dBm), guide mapping',ylabel='Output meter (dBFS)')
ax.legend(fontsize=8,ncol=2);fig.tight_layout();save(fig,'single-and-two-tone')

fig,(ax,bx)=plt.subplots(1,2,figsize=(8.6,3.4))
ax.plot(tx,delta,'o-',color=colors[0]);ax.set(xlabel='Nominal input per tone (dBm)',ylabel='Fundamental / sideband (dB)',ylim=(45.5,46.6))
bx.plot(tx,[r['apparent_iip3_dbm'] for r in two_results],'s-',color=colors[1]);bx.set(xlabel='Nominal input per tone (dBm)',ylabel='Algebraic Pin + delta/2 (dBm)')
bx.set_title('Diagnostic only: not an intrinsic IIP3',fontsize=9)
fig.tight_layout();save(fig,'two-tone-diagnostic')

fig,(ax,bx)=plt.subplots(2,1,figsize=(8.2,6),gridspec_kw={'height_ratios':[1,1.2]})
ax.plot(f,p,'-',lw=1.2,color=colors[0]);ax.plot(f[k],p[k],'o',color=colors[1]);ax.set(xlabel='RF frequency (MHz)',ylabel='Received level (dB relative)',xlim=(400,3000))
sel=(f>=1480)&(f<=1820);bx.plot(f[sel],p[sel]-p[k],'o-',color=colors[0],ms=4)
for drop,col in [(3,colors[1]),(6,colors[2])]:
    cr=crossings(drop);bx.axhline(-drop,color=col,ls='--',lw=1)
    bx.plot([cr['f_low_mhz'],cr['f_high_mhz']],[-drop,-drop],'s',color=col,label=f'-{drop} dB pair: BW = {cr["bandwidth_mhz"]:.1f} MHz')
bx.set(xlabel='RF frequency (MHz)',ylabel='Normalized link response (dB)',ylim=(-12,1),xlim=(1480,1820));bx.legend(fontsize=8)
fig.tight_layout();save(fig,'antenna-response')
print(json.dumps({k:v for k,v in results.items() if k in ['single_tone_slope','max_observed_compression_db','im3_slopes','minimum_im3_margin_above_floor_db','antenna']},indent=2))
