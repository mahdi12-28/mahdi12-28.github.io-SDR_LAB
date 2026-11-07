#!/usr/bin/env python3
"""Add real offline analysis output to the report; never changes conclusions."""
from pathlib import Path
import json
import shutil
R=Path(__file__).resolve().parents[1];out=R/'data/lab01/analysis';summary=out/'summary.json'
if not summary.is_file():raise SystemExit('Run analyze_iq.py on real data before publishing analysis')
records=json.loads(summary.read_text())
if not records:raise SystemExit('Empty results')
d=json.loads((R/'content/lab01/post.json').read_text());blocks=[]
for rec in records:
    # Reject stale outputs whose source bytes no longer match the analysis.
    import hashlib
    src=R/rec['file'];h=hashlib.sha256()
    with src.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    if h.hexdigest()!=rec['sha256']:raise SystemExit('Source changed: rerun analysis for '+rec['id'])
    blocks.append({'type':'paragraph','text':f"فایل {rec['file']}؛ {rec['samples']} نمونه؛ مدت اسمی {rec['nominal_duration_s']:.6f} ثانیه؛ SHA-256: {rec['sha256']}. پیوستگی مستقل تأیید شده: {rec['continuous_verified']}. این اعداد خروجی کد هستند و تشخیص فناوری نیازمند بازبینی است."})
    for signal in rec['signals']:
        bx='نامعتبر: لبه خارج ROI' if signal['bx_clipped'] else f"{signal['bx_hz']/1000:.3f}"
        blocks.append({'type':'table','label':'tab:iq-'+rec['id']+'-'+signal['id'],'caption':'خروجی محاسبه برای '+signal['id'],'headers':['OBW99 (kHz)','مرکز B99 (MHz)','Bx (kHz)','x (dB)'],'rows':[[f"{signal['obw99_hz']/1000:.3f}",f"{signal['obw99_midpoint_hz']/1e6:.6f}",bx,str(signal['x_db'])]]})
    if 'tone' in rec:
        t=rec['tone'];blocks.append({'type':'paragraph','text':f"تن: برآورد {t['estimate_hz']:.3f} Hz؛ مقدار انتظار برچسب {t['expected_label_hz']:.3f} Hz؛ اختلاف {t['error_hz']:.3f} Hz؛ فاصلهٔ خانهٔ FFT {t['fft_bin_hz']:.3f} Hz (عدم قطعیت کل نیست)."})
    if 'bursts' in rec:
        b=rec['bursts'];complete=[e for e in b['events'] if not e['left_censored'] and not e['right_censored']]
        durations=[e['duration_s'] for e in complete]
        blocks.append({'type':'paragraph','text':f"عبورهای آستانه: {len(b['events'])} رویداد، شامل {len(complete)} رویداد کامل؛ مدت رویدادهای کامل (s): {durations}. فاصلهٔ شروع‌ها (s): {b['start_to_start_intervals_s']}. آستانه {b['threshold_db_relative']} dB نسبی و گام زمانی {b['time_step_s']} s؛ این شمارش الزاماً شمار بسته‌های رمزگشایی‌شده نیست."})
    for suffix in ['psd','waterfall','bursts']:
        source=out/(rec['id']+'-'+suffix+'.png')
        if source.is_file():
            target=R/'assets/images/lab01/analysis'/source.name;target.parent.mkdir(exist_ok=True);shutil.copy2(source,target)
            blocks.append({'type':'figure','path':str(target.relative_to(R)),'caption':rec['id']+' / '+suffix+'؛ ساخته‌شده از IQ با کد همراه.'})
sec={'id':'iq-results','title':'خروجی تحلیل فایل‌های IQ افزوده‌شده','blocks':blocks}
d['sections']=[s for s in d['sections'] if s['id']!='iq-results'];pos=next(i for i,s in enumerate(d['sections']) if s['id']=='completion');d['sections'].insert(pos,sec)
(R/'content/lab01/post.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
print('Imported real results. Review scientific conclusions and completion status, then rebuild.')
