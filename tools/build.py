#!/usr/bin/env python3
"""Build static HTML and LaTeX from one editable report.json. No third-party modules."""
from pathlib import Path
from html import escape as e
import json

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'content/report.json').read_text(encoding='utf-8'))
PHOTOS = [
 ('pingingSDR.png','network','خروجی آزمون ping در ویندوز'),
 ('gnuRadoWindowsVersion.png','gnu','پنجرهٔ نسخهٔ GNU Radio Companion'),
 ('GNUradioWindows_Spectrum.png','gnu','پنجرهٔ نمایش طیف در GNU Radio ویندوز'),
 ('MATLAB1.png','matlab','کد دریافت و پنجرهٔ Spectrum Analyzer در MATLAB'),
 ('MATLAB2.png','matlab','نمای نزدیک Spectrum Analyzer و نمایش آبشاری'),
 ('MATLAB3.png','matlab','نمای محیط MATLAB همراه با طیف و آبشار'),
 ('MATLAB4.png','matlab','ثبت دیگر از اجرای گیرنده در MATLAB'),
 ('Python_output.png','python','اسکریپت پایتون، نمودار و خروجی تعداد نمونه‌ها'),
 ('SDRpp.png','ready','رابط SDR++ با فرکانس نمایشی ۹۲۴ مگاهرتز'),
 ('SDRpp_2.png','ready','رابط SDR++ با فرکانس نمایشی ۹۶ مگاهرتز'),
 ('SDRpp_3.png','ready','ثبت دیگر SDR++ در ۹۲۴ مگاهرتز'),
 ('SDRpp_4.png','ready','نمای طیف و آبشار SDR++'),
 ('SDRpp_5.png','ready','نمای دیگر طیف و آبشار SDR++'),
 ('SDR_angle1.png','ready','نمای بزرگ طیف و آبشار SDRangel در ۹۰ مگاهرتز'),
 ('SDR_angle2.png','ready','محیط SDRangel و پنجرهٔ دریافت'),
 ('SDR_angle3.png','ready','تنظیم منبع ورودی در SDRangel'),
 ('SDR_angle4.png','ready','ثبت دیگر تنظیمات منبع و نمایش طیف SDRangel')
]

def tech(s): return '<bdi class="technical" dir="ltr">'+e(str(s))+'</bdi>'
def table(headers, rows, caption):
 return '<div class="table-box"><table><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(c)+'</td>' for c in r)+'</tr>' for r in rows)+'</tbody><caption>'+caption+'</caption></table></div>'
def figure(file,caption,num=None,group=None,base='../../'):
 prefix=f'<b>شکل {str(num).translate(str.maketrans("0123456789","۰۱۲۳۴۵۶۷۸۹"))}.</b> ' if num else ''
 attr=f' data-group="{group}"' if group else ''
 return f'<figure class="report-figure"{attr}><button type="button" class="figure-button" data-image="{base}assets/images/{file}" data-caption="{e(caption,quote=True)}" aria-label="بزرگ‌نمایی: {e(caption,quote=True)}"><img src="{base}assets/images/{file}" alt="{e(caption,quote=True)}" loading="lazy" width="1920" height="1080"><span class="zoom-hint">بزرگ‌نمایی ↗</span></button><figcaption>{prefix}{e(caption)}</figcaption></figure>'
def student(key,title,prompt):
 text=D.get(key,'').strip()
 return f'<div class="student-text">{e(text)}</div>' if text else f'<div class="blank"><b>{title} — در انتظار نوشتهٔ تیم</b><p>{prompt}</p></div>'
def section(id,no,title,body):
 return f'<section class="report-section" id="{id}"><span class="section-index">{no} / LAB 00</span><h2>{title}</h2>{body}</section>'
def shell(title,body,report=False):
 base='../../' if report else ''
 lablink='#overview' if report else 'reports/lab00/'
 return f'''<!doctype html>
<html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="گزارش آزمایش صفر آزمایشگاه رادیو نرم‌افزار؛ راه‌اندازی محیط، مدارک اجرای نرم‌افزارها و فایل‌های گزارش."><meta name="theme-color" content="#142d3d"><title>{e(title)}</title><link rel="stylesheet" href="{base}assets/css/site.css"><link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<script defer src="{base}assets/js/config.js"></script><script defer src="{base}assets/js/site.js"></script>
{'''<script>window.MathJax={tex:{inlineMath:[['\\(','\\)']]},options:{skipHtmlTags:['script','noscript','style','textarea','pre','code']}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"></script>''' if report else ''}
</head><body><a class="skip" href="#main">رفتن به محتوای اصلی</a><header class="topbar"><div class="wrap nav"><a class="brand" href="{base}index.html"><span class="brand-mark">sdr.</span><span>دفتر آزمایش رادیو نرم‌افزار<small dir="ltr">SOFTWARE DEFINED RADIO LAB</small></span></a><nav class="nav-links" aria-label="پیمایش اصلی"><a href="{base}index.html#experiments">آزمایش‌ها</a><a href="{lablink}">آزمایش صفر</a><a href="{base}reports/lab00/#downloads">فایل‌های گزارش ↙</a></nav></div></header>
{body}
<footer class="footer"><div class="wrap"><span>{e(D['team_name'])} · {e(D['semester'])}</span><span>تهیه‌شده برای آزمایشگاه رادیو نرم‌افزار · {e(D['instructor'])}</span></div></footer>
<dialog class="lightbox" id="image-dialog" aria-labelledby="dialog-title"><div class="dialog-top"><b id="dialog-title">تصویر آزمایش</b><div><button type="button" data-zoom>اندازهٔ اصلی</button> <button type="button" data-close aria-label="بستن تصویر">بستن ×</button></div></div><p class="dialog-help">برای خواندن جزئیات، اندازهٔ اصلی را انتخاب کنید. با کلید Escape می‌توانید این پنجره را ببندید.</p><div class="zoom-area"><img alt="" src="{base}assets/images/MATLAB2.png"></div></dialog>
</body></html>'''

home=f'''<main id="main"><section class="hero wrap"><div class="hero-grid"><div><p class="eyebrow">آزمایشگاه مخابرات / دفتر گزارش‌های تیم</p><span class="pill pending">{e(D['status'])}</span><h1>اولین اتصال،<br><span>شروع کار با رادیو نرم‌افزار.</span></h1><p class="lead">آزمایش صفر به آماده‌کردن ابزارها اختصاص دارد؛ از تنظیم شبکه و اتصال به دستگاه تا اجرای محیط‌های دریافت. مستندات این صفحه، عکس‌های ثبت‌شده در جلسه و وضعیت تکمیل هر مسیر را یک‌جا جمع می‌کند.</p><div class="actions"><a class="btn primary" href="reports/lab00/">خواندن گزارش آزمایش صفر <span>←</span></a><a class="btn" href="reports/lab00/#gallery">دیدن تصاویر جلسه ↗</a></div></div><div class="hero-art"><div class="instrument-heading"><span><i class="dot"></i> LAB 00 / CAPTURE ARCHIVE</span><span>MATLAB</span></div><a href="reports/lab00/#matlab" aria-label="مشاهدهٔ تصویر MATLAB در گزارش"><img src="assets/images/MATLAB2.png" alt="تصویر واقعی Spectrum Analyzer در MATLAB از فایل‌های جلسه" width="1061" height="657"></a><div class="instrument-footer"><span>fₛ 2.6 MS/s</span><span>SCREENSHOT / ORIGINAL EVIDENCE</span></div></div></div><div class="facts"><div class="fact"><b>00</b><span>شمارهٔ آزمایش</span></div><div class="fact"><b>04</b><span>مسیر در دستورکار</span></div><div class="fact"><b>17</b><span>تصویر در آرشیو جلسه</span></div><div class="fact"><b>945 MHz</b><span>فرکانس خواسته‌شده در دستورکار</span></div></div></section>
<section class="section wrap" id="experiments"><div class="section-head"><div><div class="section-label">EXPERIMENT INDEX</div><h2>فهرست آزمایش‌ها</h2></div><p>وضعیت تحویل و تاریخ ثبت هر گزارش</p></div>'''+table(['شماره','عنوان آزمایش','وضعیت تحویل','تاریخ جلسه / تحویل','گزارش'],[['<span class="lab-number">00</span>','راه‌اندازی محیط و نصب نرم‌افزارها<small>Environment and Toolchain Setup</small>','<span class="pill pending">'+e(D['status'])+'</span>',e(D['session_date'])+' / '+e(D['submission_date']),'<a href="reports/lab00/">مشاهدهٔ گزارش ←</a>']],'جدول ۱. فهرست گزارش‌های موجود؛ گزارش‌های بعدی پس از تهیه به این جدول اضافه می‌شوند.')+f'''</section><section class="section wrap overview"><div><p class="eyebrow">از آماده‌سازی تا مستندسازی</p><h2>یک دستگاه، چند مسیر نرم‌افزاری</h2><p>در دستورکار، ارتباط داده از راه LAN انجام می‌شود و کابل USB برای تغذیه است. MATLAB، GNU Radio و پایتون از نشانی اتصال مشترک استفاده می‌کنند. گزارش هر مسیر، تنظیمات ثبت‌شده و تصویر مرتبط را جداگانه نشان می‌دهد.</p><a class="btn" href="reports/lab00/#readiness">دیدن جدول آمادگی ←</a></div><div class="route-list"><a class="route" href="reports/lab00/#matlab"><b><span class="mini-id">A</span>MATLAB</b><span>تصاویر اجرا موجود است ↗</span></a><a class="route" href="reports/lab00/#windows"><b><span class="mini-id">B</span>GNU Radio و ابزارهای ویندوز</b><span>تصاویر اجرا موجود است ↗</span></a><a class="route" href="reports/lab00/#ubuntu"><b><span class="mini-id">C</span>Ubuntu / GNU Radio</b><span>مدرک ارائه نشده ↗</span></a><a class="route" href="reports/lab00/#python"><b><span class="mini-id">D</span>Python / pyadi-iio</b><span>تصویر خروجی موجود است ↗</span></a></div></section><section class="wrap section" id="team"><div class="section-head"><div><div class="section-label">THE TEAM</div><h2>{e(D['team_name'])}</h2></div><p>{e(D['instructor'])}</p></div><p>{e(' | '.join(D['members']))}</p><div class="note"><p>این نسخه هنوز برای تحویل نهایی کامل نیست. نوشته‌های تحلیلی تیم، مشخصات اعضا، مدارک باقی‌مانده و تنظیمات داوری باید پیش از انتشار تکمیل شوند.</p></div></section></main>'''

parts=[]
parts.append(section('overview','01','هدف و محدودهٔ گزارش',f'''<p>در آزمایش صفر، هدف این است که محیط‌های نرم‌افزاری درس پیش از آزمایش‌های اصلی آماده باشند. دستورکار چهار مسیر را تعیین کرده است: MATLAB، ابزارهای ویندوز، اوبونتو و پایتون. معیارهای تحویل در جدول ۱۰ دستورکار آمده‌اند <a href="#references">[۱، ص. ۱۱]</a>.</p><p>این نسخه بر اساس ۱۷ تصویر موجود در پوشهٔ جلسه تنظیم شده است. متن زیر، تنظیمات و خروجی‌های قابل‌خواندن را ثبت می‌کند؛ بخش‌های تحلیل و نتیجه‌گیری برای نوشتهٔ اعضای تیم در نظر گرفته شده‌اند.</p><div class="note neutral"><p><b>مشخصات جلسه:</b> تاریخ: {e(D['session_date'])}<br>اعضا: {e(' / '.join(D['members']))}<br>وضعیت تحویل: {e(D['status'])}</p></div>'''))
parts[0]=parts[0].replace('</section>', '<p>در فایل خام، هر نمونهٔ مختلط با دو مؤلفهٔ هم‌فاز و متعامد نمایش داده می‌شود. رابطهٔ (۱) فقط تعریف نمادگذاری است و نتیجهٔ اندازه‌گیری این جلسه نیست.</p><div class="equation">\\begin{equation} x[n] = I[n] + j Q[n] \\end{equation}</div></section>')
parts.append(section('network','02','اتصال شبکه و آزمون اولیه','''<p>طبق دستورکار، نشانی دستگاه <code>192.168.1.10</code> و نشانی پیشنهادی کارت شبکهٔ لپ‌تاپ <code>192.168.1.20</code> است. ماسک زیرشبکه <code>255.255.255.0</code> در نظر گرفته می‌شود و Gateway و DNS کارت سیمی خالی می‌مانند [۱، ص. ۲–۳]. شکل ۱ خروجی آزمون ثبت‌شده را نشان می‌دهد.</p>'''+table(['مورد','مقدار','منشأ ثبت'],[
 ['نشانی مقصد',tech('192.168.1.10'),'تصویر خروجی ping'],['بسته‌های ارسال / دریافت / ازدست‌رفته',tech('4 / 4 / 0'),'تصویر خروجی ping'],['کمینه / بیشینه / میانگین زمان پاسخ',tech('1 / 2 / 1 ms'),'تصویر خروجی ping'],['IPv4 کارت شبکهٔ لپ‌تاپ',e(D['network_ipv4']),'مدرک جداگانه لازم است'],['نشانی اتصال در نرم‌افزارها',tech('ip:192.168.1.10'),'مقدار خواسته‌شده در دستورکار']],'جدول ۱. ثبت اطلاعات شبکه؛ اعداد ping از شکل ۱ رونویسی شده‌اند.')+figure('pingingSDR.png','خروجی دستور ping 192.168.1.10 در ویندوز',1)))
parts.append(section('matlab','03','مسیر الف؛ دریافت در MATLAB','''<p>شکل ۲ هم کد دریافت و هم پنجرهٔ Spectrum Analyzer را در محیط MATLAB نشان می‌دهد. تنظیمات قابل‌خواندن کد در جدول ۲ آمده‌اند. تصاویر رابط نرم‌افزار برای مستندسازی اجرا نگه داشته شده‌اند؛ نمودار برداری حاصل از دادهٔ خام هنوز ارائه نشده است.</p>'''+table(['پارامتر','مقدار ثبت‌شده'],[
 ['RadioID',tech('ip:192.168.1.10')],['CenterFrequency',tech('945e6 Hz')],['BasebandSampleRate',tech('2.6e6 sample/s')],['GainSource / Gain',tech('Manual / 20 dB')],['SamplesPerFrame / OutputDataType',tech('4096 / double')],['نسخهٔ MATLAB',e(D['matlab_version'])],['شمارهٔ سریال',e(D['serial'])],['نسخهٔ سفت‌افزار',e(D['firmware'])],['بازهٔ فرکانسی فعال',e(D['rf_range'])]
 ],'جدول ۲. تنظیمات دیده‌شده در MATLAB و فیلدهای جدول ۵ دستورکار.')+figure('MATLAB1.png','کد دریافت و پنجرهٔ Spectrum Analyzer در MATLAB',2)+'''<p>برای تکمیل جدول ۵ دستورکار، خروجی متنی <code>info(rx)</code> و پاسخ خود تیم به پرسش «آیا طیف GSM900 دیده شد؟» باید افزوده شود.</p>'''))
parts.append(section('windows','04','مسیر ب؛ GNU Radio و نرم‌افزارهای آماده','''<p>در پنجرهٔ About، نسخهٔ GNU Radio Companion برابر <bdi dir="ltr">3.10.12.0</bdi> و نسخهٔ Python همراه آن <bdi dir="ltr">3.12.9</bdi> نوشته شده است (شکل ۳). پنجرهٔ طیف نیز در شکل ۴ آمده است. فایل فلوگراف مسیر دوم با نام <a href="../../flowgraphs/Lab00App2.grc" download><bdi dir="ltr">Lab00App2.grc</bdi></a> به گزارش افزوده شده است.</p>'''+figure('gnuRadoWindowsVersion.png','نسخهٔ GNU Radio Companion در پنجرهٔ About',3)+figure('GNUradioWindows_Spectrum.png','پنجرهٔ نمایش طیف در GNU Radio ویندوز',4)+table(['مورد','ثبت موجود','مورد لازم برای تکمیل'],[
 ['GNU Radio',tech('3.10.12.0'),'فایل Lab00App2.grc موجود است؛ تصویر تنظیمات Source لازم است'],['دو نرم‌افزار آماده','تصاویر SDR++ و SDRangel موجود است','نسخه، نشانی اتصال و آزمون خواسته‌شده در 945 MHz'],['نسخهٔ SDR++',tech('1.3.2'),'نوشته‌شده در نوار عنوان SDRpp_2.png'],['نسخهٔ SDRangel',tech('8.0.0'),'نوشته‌شده در نوار پایین SDR_angle1.png']
 ],'جدول ۳. مدارک مسیر ویندوز و اطلاعات مربوط به جدول ۷ دستورکار.')+'''<h3>فلوگراف مسیر دوم؛ Lab00App2.grc</h3><p>این فایل با GNU Radio Companion نسخهٔ <bdi dir="ltr">3.10.12.0</bdi> ذخیره شده و خروجی مختلط <bdi dir="ltr">PlutoSDR Source</bdi> را مستقیم به <bdi dir="ltr">QT GUI Frequency Sink</bdi> متصل می‌کند.</p><ul><li>تنظیمات منبع: فرکانس مرکزی ۹۴۵ مگاهرتز، نرخ نمونه‌برداری ۲٫۶ مگاسمپل‌برثانیه، پهنای باند ۲ مگاهرتز، بهرهٔ دستی ۲۰ دسی‌بل و اندازهٔ بافر ۳۲۷۶۸ نمونه.</li><li>مقدار URI ذخیره‌شده: <code>192.168.1.10</code>.</li><li>تنظیمات نمایش طیف: مرکز محور ۹۰ مگاهرتز، پهنای محور برابر متغیر <code>samp_rate = 20000000</code>، اندازهٔ FFT برابر ۱۰۲۴ و پنجرهٔ Blackman–Harris.</li></ul><div class="note"><p><b>تطبیق تنظیمات پیش از اجرا:</b> مرکز و پهنای محور نمایش در فایل ذخیره‌شده با فرکانس و نرخ نمونه‌برداری منبع یکسان نیستند. برای نمایش محور فرکانس متناظر با منبع، مرکز Frequency Sink را روی <code>945e6</code> و پهنای آن را روی <code>2.6e6</code> تنظیم کنید. URI منبع را نیز با نشانی اتصال قابل‌استفاده در نصب خود، مانند <code>ip:192.168.1.10</code>، بررسی کنید. فایل پیوست بدون تغییر بارگذاری شده و اجرای سخت‌افزاری آن در این به‌روزرسانی آزموده نشده است.</p></div><h3>ثبت تنظیمات نرم‌افزارهای آماده</h3><p>برای حفظ جزئیات جلسه، تنظیمات دیده‌شده در تصاویر همراه با مقادیر خواسته‌شده در دستورکار در جدول ۴ آمده است. علت انتخاب این تنظیمات و وضعیت آزمون نهایی را اعضای تیم در بخش تحلیل توضیح می‌دهند.</p>'''+table(['پارامتر','در تصویر SDRpp_2','در تصویر SDR_angle1','در دستورکار'],[
 ['فرکانس نمایشی',tech('96 MHz'),tech('90 MHz'),tech('945 MHz')],['بهرهٔ گیرنده',tech('45 dB'),'در این نما مشخص نیست','دستی؛ حداکثر 30 dB با آنتن'],['منبع / مسیر اتصال',tech('PlutoSDR / (usb)'),'برچسب PlutoSDR؛ URI در این نما مشخص نیست',tech('ip:192.168.1.10')]
 ],'جدول ۴. رونویسی تنظیمات از تصاویر؛ این جدول تأیید معیار پذیرش آزمایش نیست.')+figure('SDRpp_2.png','ثبت SDR++ با فرکانس نمایشی ۹۶ مگاهرتز؛ جزئیات در جدول ۴',5)+figure('SDR_angle1.png','ثبت SDRangel با فرکانس نمایشی ۹۰ مگاهرتز؛ جزئیات در جدول ۴',6)))
parts.append(section('ubuntu','05','مسیر ج؛ اوبونتو و GNU Radio',student('ubuntu','ثبت مسیر اوبونتو','نسخهٔ اوبونتو و GNU Radio، خروجی iio_info، تصویر اجرای GRC و نام ابزار اضافی آزموده‌شده را اضافه کنید. در فایل‌های دریافت‌شده مدرکی برای این مسیر موجود نیست.')+table(['موردِ جدول ۸ دستورکار','وضعیت مدرک'],[['نسخهٔ Ubuntu و GNU Radio','ارائه نشده'],['خروجی iio_info و شناسایی دستگاه','ارائه نشده'],['اجرای GRC روی اوبونتو','ارائه نشده'],['آزمون iio-oscilloscope یا GQRX','ارائه نشده']],'جدول ۵. فیلدهای ثبت مسیر اوبونتو؛ انجام‌نشدن آزمایش از نبود مدرک استنباط نشده است.')))
parts.append(section('python','06','مسیر د؛ دریافت نمونه‌ها در پایتون','''<p>تصویر VS Code، فایل <code>pluto_test.py</code>، نمودار رسم‌شده و خروجی ترمینال را کنار هم نشان می‌دهد (شکل ۷). خروجی قابل‌خواندن ترمینال به این صورت است:</p><pre>samples: (4096,)  sample_rate: 2600000</pre>'''+table(['مورد','مقدار قابل‌خواندن از تصویر'],[
 ['نشانی دستگاه',tech('ip:192.168.1.10')],['فرکانس مرکزی',tech('945e6 Hz')],['نرخ نمونه‌برداری / پهنای باند',tech('2.6e6 / 2e6 Hz')],['حالت و بهرهٔ گیرنده',tech('manual / 20 dB')],['اندازهٔ بافر / شکل آرایه',tech('4096 / (4096,)')],['نسخهٔ pyadi-iio',e(D['pyadi_version'])],['محیط اجرا','مسیر Python در ترمینال شامل radioconda است']
 ],'جدول ۶. ثبت پارامترهای پایتون برای جدول ۹ دستورکار.')+figure('Python_output.png','کد پایتون، نمودار رسم‌شده و خروجی تعداد نمونه‌ها',7)+'''<p>نسخهٔ کتابخانه با خروجی <code>pip show pyadi-iio</code> و فایل اصلی اسکریپت باید ضمیمه شوند. فایل کد موجود در این بسته، بازنویسی آموزشی از دستورکار است و به‌عنوان فایل اصلی جلسه معرفی نمی‌شود.</p>'''))
parts.append(section('readiness','07','جدول آمادگی و مدارک باقی‌مانده','''<p>جدول زیر بر اساس معیارهای جدول ۱۰ دستورکار تنظیم شده است. وضعیت‌ها، وجود مدرک در فایل‌های این نسخه را نشان می‌دهند و جای امضای دستیار آموزشی را نمی‌گیرند.</p>'''+table(['مسیر','مدرک موجود','وضعیت تکمیل'],[
 ['شبکه','تصویر ping','تصویر IPv4 و تأیید دستیار لازم است'],['الف؛ MATLAB','۴ تصویر اجرا','خروجی info(rx)، نسخه و پاسخ تیم لازم است'],['ب؛ ویندوز','نسخه و طیف GNU Radio؛ تصاویر دو نرم‌افزار','فایل Lab00App2.grc موجود است؛ مستند آزمون در تنظیمات خواسته‌شده لازم است'],['ج؛ اوبونتو','مدرکی در فایل‌ها نیست','مستندات مسیر ج لازم است'],['د؛ پایتون','تصویر خروجی و نمودار','نسخهٔ کتابخانه، کد اصلی و دادهٔ خام لازم است']
 ],'جدول ۷. مرور مدارک آمادگی؛ هیچ ردیفی به‌جای امضای دستیار تکمیل نشده است.')+'''<div class="note"><p><b>داده و بازتولید:</b> فایل <a href="../../flowgraphs/Lab00App2.grc" download>Lab00App2.grc</a> برای مسیر دوم موجود است. فایل خام I/Q، لاگ کامل و مشخصات دستگاه هنوز ارائه نشده‌اند. از روی اسکرین‌شات‌ها عددی برای توان، SNR یا کیفیت دریافت محاسبه نشده است.</p></div><h3>یادداشت ایمنی</h3><p>جدول ۳ دستورکار، بهرهٔ دستی گیرنده را برای دریافت با آنتن حداکثر ۳۰ دسی‌بل تعیین می‌کند. برای این گزارش، فقط دریافت مطرح است و هیچ کد ارسال RF در بسته قرار ندارد [۱، ص. ۴].</p>'''))
parts.append(section('analysis','08','تحلیل نتایج و عیب‌یابی',student('analysis','تحلیل نتایج','توضیح خودتان را دربارهٔ تفاوت تنظیمات ثبت‌شده با دستورکار، معیار تشخیص سیگنال و نتیجهٔ آزمون هر مسیر بنویسید. هر ادعای عددی باید به فایل خام مشخصی متکی باشد؛ از روی این تصاویر، نوع سیگنال یا توان مطلق را قطعی معرفی نکنید.')+'<h3>عیب‌یابی جلسه</h3>'+student('troubleshooting','یادداشت عیب‌یابی','نشانهٔ خطا، کاری که واقعاً انجام دادید و نتیجهٔ آزمون مجدد را ثبت کنید. در تصویر پایتون پیام مربوط به مسیر نمونهٔ your_script.py دیده می‌شود؛ شرح اتفاق و راه‌حل را خودتان تأیید و تکمیل کنید. اگر لاگ موجود نیست، همین محدودیت را صریح بنویسید.')))
parts.append(section('conclusion','09','جمع‌بندی و پاسخ نهایی تیم',student('conclusion','نتیجه‌گیری','در چند جمله و با بیان خودتان بنویسید کدام معیارهای تحویل را آزمودید، برای کدام مورد مدرک دارید و چه کاری باقی مانده است. این بخش طبق بند ۷-۵ آیین‌نامه باید حاصل کار اعضای تیم باشد.')))
parts.append(section('gallery','10','آرشیو تصاویر جلسه','''<p>تمام ۱۷ تصویر با نام اصلی نگه داشته شده‌اند. روی هر تصویر بزنید تا نسخهٔ کامل باز شود؛ فیلترها فقط نمایش آرشیو را تغییر می‌دهند.</p><div class="gallery-tools"><div class="filters" role="group" aria-label="فیلتر تصاویر">'''+''.join(f'<button class="filter" type="button" data-filter="{key}" aria-pressed="{str(key=="all").lower()}">{label}</button>' for key,label in [('all','همه'),('network','شبکه'),('matlab','MATLAB'),('gnu','GNU Radio'),('python','پایتون'),('ready','ابزارهای آماده')])+'''</div><span class="small text-muted" id="gallery-count" aria-live="polite">۱۷ تصویر</span></div><div class="gallery">'''+''.join(figure(f,c,i+8,g) for i,(f,g,c) in enumerate(PHOTOS))+'''</div><p class="small text-muted">تصاویر، ثبت رابط نرم‌افزار هستند. نمودار علمی نهایی باید از دادهٔ خام تولید و ترجیحاً به‌صورت PDF برداری منتشر شود [۲، بند ۴-۲].</p>'''))
parts.append(section('downloads','11','فایل‌های گزارش و بازتولید','''<div class="files"><a class="file" href="../../downloads/lab00-report.pdf"><b>گزارش PDF ↙</b><small>پیش‌نویس ساخته‌شده با LaTeX؛ دارای بخش‌های نیازمند تکمیل</small></a><a class="file" href="../../downloads/lab00-latex-source.zip"><b>منبع کامل LaTeX ↙</b><small>فایل tex، مراجع BibTeX، قلم و تصاویر گزارش</small></a><a class="file" href="../../latex/report.tex"><b>فایل اصلی TEX ↙</b><small>برای مشاهده و بازبینی منبع گزارش</small></a><a class="file" href="../../latex/references.bib"><b>مراجع BibTeX ↙</b><small>دستورکار و آیین‌نامهٔ ارائه‌شدهٔ درس</small></a><a class="file" href="../../code/pluto_receive_template.py"><b>قالب کد دریافت پایتون ↙</b><small>بازنویسی آموزشی؛ کد اصلی جلسه نیست</small></a><a class="file" href="../../code/matlab_receive_template.m"><b>قالب کد دریافت MATLAB ↙</b><small>بازنویسی آموزشی؛ کد اصلی جلسه نیست</small></a><a class="file" href="../../data/README.md"><b>وضعیت دادهٔ خام ↗</b><small>دادهٔ I/Q ارائه نشده؛ راهنمای افزودن فایل واقعی</small></a><a class="file" href="../../flowgraphs/Lab00App2.grc" download><b>فلوگراف مسیر دوم؛ Lab00App2.grc ↙</b><small>فایل ارائه‌شدهٔ تیم برای GNU Radio Companion</small></a><a class="file" href="../../flowgraphs/README.md"><b>تنظیمات و راهنمای فلوگراف ↗</b><small>پارامترهای ذخیره‌شده و نکتهٔ تنظیم محور فرکانس</small></a></div>'''))
parts.append(section('comments','12','داوری همتا','''<p>داوری می‌تواند شامل یک نکتهٔ فنی مثبت، یک ادعای نیازمند مدرک، یک پرسش دقیق و امتیاز خوانایی از ۱ تا ۵ همراه با دلیل باشد [۲، بند ۳-۴]. کامنت‌های داوری نباید توسط تیم میزبان حذف یا ویرایش شوند.</p><div class="comment-status" id="comment-status">بخش داوری پس از اتصال این صفحه به مخزن GitHub تیم فعال می‌شود. تنظیمات giscus در این نسخه هنوز وارد نشده‌اند؛ در حال حاضر امکان ثبت کامنت فعال نیست.</div><div class="giscus"></div><noscript><p>برای ثبت کامنت از طریق giscus باید JavaScript فعال باشد.</p></noscript>'''))
parts.append(section('references','13','مراجع و اعلام استفاده از ابزارها','''<ol class="source-list"><li><b>دستورکار آزمایش ۰: راه‌اندازی محیط و نصب نرم‌افزارها.</b> آزمایشگاه رادیو نرم‌افزار، دانشکدهٔ مهندسی برق. فایل ارائه‌شده با نام <bdi dir="ltr">lab_00_setup(1).pdf</bdi>؛ به‌ویژه صفحات ۲–۴، ۶–۱۱.</li><li><b>آیین‌نامه، مقررات و سناریوی اجرایی آزمایشگاه رادیو نرم‌افزار.</b> نسخهٔ ۱٫۰، نیمسال اول ۱۴۰۵–۱۴۰۶؛ فایل <bdi dir="ltr">regulations(1).pdf</bdi>، بندهای ۳ تا ۵ و ۷-۵.</li><li><b>تصاویر جلسهٔ تیم.</b> فایل <bdi dir="ltr">Lab0_photos(1).zip</bdi>؛ ۱۷ تصویر رابط نرم‌افزار. فهرست و نام فایل‌ها در آرشیو همین صفحه موجود است.</li></ol><h3>اعلام استفاده از هوش مصنوعی</h3><p>در تهیهٔ این نسخه از ChatGPT برای ساخت قالب HTML/CSS و LaTeX، ویرایش نگارشی، سامان‌دهی تصاویر، رونویسی تنظیمات قابل‌خواندن و آماده‌کردن قالب کد استفاده شده است. بخش‌های تحلیل، تفسیر داده و نتیجه‌گیری در این نسخه خالی مانده‌اند تا اعضای تیم آن‌ها را بنویسند. مسئولیت بررسی نهایی متن و تطبیق آن با اجرای واقعی بر عهدهٔ اعضای تیم است.</p><a class="top-link" href="#main">بازگشت به ابتدای گزارش ↑</a>'''))

toc=[('overview','هدف و محدوده'),('network','شبکه'),('matlab','مسیر الف؛ MATLAB'),('windows','مسیر ب؛ ویندوز'),('ubuntu','مسیر ج؛ اوبونتو'),('python','مسیر د؛ پایتون'),('readiness','جدول آمادگی'),('analysis','تحلیل و عیب‌یابی'),('conclusion','جمع‌بندی'),('gallery','آرشیو تصاویر'),('downloads','فایل‌ها'),('comments','داوری همتا'),('references','مراجع')]
report=f'''<main id="main"><div class="page-heading"><div class="wrap"><div class="crumb"><a href="../../index.html">دفتر آزمایش</a> / گزارش آزمایش صفر</div><div class="title-line"><div><p class="eyebrow">LAB 00 / ENVIRONMENT & TOOLCHAIN SETUP</p><h1>راه‌اندازی محیط و نصب نرم‌افزارها</h1><div class="meta"><span>{e(D['team_name'])}</span><span>تاریخ جلسه: {e(D['session_date'])}</span><span>تاریخ تحویل: {e(D['submission_date'])}</span></div></div><span class="large-id" aria-hidden="true">00</span></div><div class="actions"><a class="btn primary" href="../../downloads/lab00-report.pdf">دریافت PDF ↙</a><a class="btn" href="#downloads">منبع و کدها ↙</a><button class="print-button" type="button" data-print>چاپ صفحه</button></div><div class="note"><p><b>{e(D['status'])}.</b> این نسخه شامل مدارک موجود و جای مشخص برای نوشته‌های اعضای تیم است؛ تأیید نهایی آزمایش هنوز ثبت نشده است.</p></div></div></div><div class="wrap report-layout"><aside class="toc" aria-label="فهرست گزارش"><p>در این گزارش</p>'''+''.join(f'<a href="#{k}">{v}</a>' for k,v in toc)+'''</aside><article>'''+''.join(parts)+'''</article></div></main>'''
(ROOT/'index.html').write_text(shell('دفتر آزمایش رادیو نرم‌افزار | آزمایش صفر',home),encoding='utf-8')
(ROOT/'reports/lab00/index.html').write_text(shell('آزمایش صفر؛ راه‌اندازی محیط | گزارش تیم',report,True),encoding='utf-8')
(ROOT/'assets/js/config.js').write_text('window.LAB_GISCUS = '+json.dumps(D['giscus'],ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
(ROOT/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="15" fill="#142d3d"/><path d="M12 35h7l5-17 10 30 6-24 5 11h7" fill="none" stroke="#d7ef92" stroke-width="4" stroke-linejoin="round"/></svg>')

# LaTeX keeps scientific text authored by the students in the same editable JSON.
def tex(s):
 return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in str(s))
def ltr(s): return r'\lr{'+tex(s)+'}'
def para(s): return '\\rp{'+tex(s)+'}\n\n'
def heading(s): return '\\section{\\rtl{'+tex(s)+'}}\n'
def latex_fig(file,caption,label):
 height='0.17' if file=='gnuRadoWindowsVersion.png' else '0.29'
 return '\\begin{figure}[H]\n\\centering\n\\includegraphics[width=0.96\\linewidth,height='+height+'\\textheight,keepaspectratio]{../assets/images/'+file+'}\n\\caption{\\rtl{'+tex(caption)+'}}\\label{'+label+'}\n\\end{figure}\n'
def ltable(rows,caption,label):
 return '\\begin{table}[H]\\centering\n\\renewcommand{\\arraystretch}{1.2}\n\\begin{tabular}{|p{0.55\\linewidth}|p{0.32\\linewidth}|}\\hline\n'+''.join('\\rtl{'+v+'} & \\rtl{'+k+'} \\\\ \\hline\n' for k,v in rows)+'\\end{tabular}\n\\caption{\\rtl{'+tex(caption)+'}}\\label{'+label+'}\\end{table}\n'
def student_tex(key,title,prompt):
 return para(D[key]) if D.get(key,'').strip() else '\\begin{quote}\\rp{\\textbf{'+tex(title)+'؛ در انتظار نوشتهٔ تیم.} '+tex(prompt)+'}\\end{quote}\n'
latex=r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=22mm,headheight=14pt]{geometry}
\usepackage{fontspec}
\usepackage{graphicx}
\usepackage{float}
\usepackage{titlesec}
\usepackage{amsmath}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage[numbers]{natbib}
\setmainfont[Path=../assets/fonts/,BoldFont=DejaVuSans-Bold.ttf,ItalicFont=DejaVuSans.ttf,Script=Arabic,Language=Persian]{DejaVuSans.ttf}
\newfontfamily\latinfont[Path=../assets/fonts/,BoldFont=DejaVuSans-Bold.ttf]{DejaVuSans.ttf}
\TeXXeTstate=1
\newcommand{\rtl}[1]{\beginR #1\endR}
\newcommand{\lr}[1]{\beginL{\latinfont #1}\endL}
\newcommand{\rp}[1]{\par\begingroup\rightskip=0pt\leftskip=0pt plus 1fil\parfillskip=0pt\noindent\beginR #1\endR\par\endgroup}
\renewcommand{\figurename}{\rtl{شکل}}
\renewcommand{\tablename}{\rtl{جدول}}
\renewcommand{\refname}{\rtl{مراجع}}
\renewcommand{\contentsname}{\rtl{فهرست مطالب}}
\hypersetup{hidelinks,pdftitle={Lab 00 - Draft report},pdfauthor={SDR Lab Team}}
\setlength{\parindent}{0pt}
\setlength{\parskip}{8pt}
\linespread{1.35}
\titleformat{\section}{\large\bfseries\raggedleft}{\thesection}{1em}{}
\pagestyle{fancy}\fancyhf{}
\fancyhead[R]{\small\rtl{آزمایش صفر | راه‌اندازی محیط}}
\fancyhead[L]{\small\lr{SDR LAB}}
\fancyfoot[C]{\thepage}
\begin{document}
\begin{titlepage}
\vspace*{15mm}
\begin{center}
{\color{teal}\Large\lr{SDR LAB / 00}}\\[12mm]
{\Huge\bfseries\rtl{گزارش آزمایش صفر}}\\[7mm]
{\Large\rtl{راه‌اندازی محیط و نصب نرم‌افزارها}}\\[4mm]
{\large\lr{Environment and Toolchain Setup}}\\[15mm]
'''
latex+='\\rtl{'+tex(D['team_name'])+'}\\\\[6mm]\n'
for m in D['members']: latex+='\\rtl{'+tex(m)+'}\\\\[3mm]\n'
latex+='\\vspace{8mm}\n\\rtl{مدرس: '+tex(D['instructor'])+'}\\\\[3mm]\n\\rtl{'+tex(D['semester'])+'}\\\\[5mm]\n\\rtl{تاریخ جلسه: '+tex(D['session_date'])+'}\\\\[3mm]\n\\rtl{تاریخ تحویل: '+tex(D['submission_date'])+'}\\\\[12mm]\n'
latex+='\\fbox{\\parbox{0.85\\linewidth}{\\rp{\\textbf{'+tex(D['status'])+'}\\par این نسخه برای تحویل نهایی کامل نیست. تحلیل، نتیجه‌گیری و مدارک باقی‌مانده باید توسط اعضای تیم تکمیل شوند.}}}\n\\end{center}\\end{titlepage}\n'
latex+=heading('هدف و مستندات گزارش')+para('هدف آزمایش صفر، آماده‌سازی محیط نرم‌افزاری درس و ثبت آزمون اتصال در چهار مسیر مستقل است. این نسخه، تنظیمات قابل‌خواندن از تصاویر ارسالی را گردآوری می‌کند. تحلیل و نتیجه‌گیری در این پیش‌نویس نوشته نشده‌اند.')
latex+='\\rp{معیارهای ثبت از دستورکار \\citep{labmanual} و الزامات مستندسازی از آیین‌نامهٔ درس \\citep{regulations} استخراج شده‌اند. تصاویر، رابط نرم‌افزارها را مستند می‌کنند و جایگزین دادهٔ خام نیستند.}\n'
latex+=para('برای نمادگذاری فایل خام، هر نمونهٔ مختلط از دو مؤلفهٔ هم‌فاز و متعامد تشکیل می‌شود. رابطهٔ زیر تعریف نمادگذاری است و نتیجهٔ اندازه‌گیری نیست.')+r'\begin{equation} x[n] = I[n] + jQ[n] \end{equation}'+'\n'
latex+=heading('شبکه و آزمون اتصال')+'\\rp{شکل \\ref{fig:ping} خروجی آزمون شبکه را نشان می‌دهد. مقادیر جدول \\ref{tab:network} از همین تصویر رونویسی شده‌اند.}\n'
latex+=ltable([('نشانی مقصد',ltr('192.168.1.10')),('ارسال / دریافت / اتلاف بسته',ltr('4 / 4 / 0')),('کمینه / بیشینه / میانگین پاسخ',ltr('1 / 2 / 1 ms')),('نشانی کارت شبکه',tex(D['network_ipv4']))],'ثبت اطلاعات شبکه','tab:network')+latex_fig('pingingSDR.png','خروجی ثبت‌شدهٔ آزمون شبکه','fig:ping')+'\\clearpage\n'
latex+=heading('مسیر الف؛ MATLAB')+'\\rp{شکل \\ref{fig:matlab} کد دریافت و پنجرهٔ تحلیل‌گر را نشان می‌دهد. تنظیمات خوانده‌شده در جدول \\ref{tab:matlab} ثبت شده‌اند.}\n'
latex+=ltable([('نشانی اتصال',ltr('ip:192.168.1.10')),('فرکانس مرکزی',ltr('945 MHz')),('نرخ نمونه‌برداری',ltr('2.6 MS/s')),('حالت و بهرهٔ گیرنده',ltr('Manual / 20 dB')),('نمونه در هر فریم',ltr('4096')),('نسخهٔ MATLAB',tex(D['matlab_version'])),('سریال دستگاه',tex(D['serial'])),('سفت‌افزار',tex(D['firmware'])),('بازهٔ فعال',tex(D['rf_range']))],'تنظیمات MATLAB و فیلدهای تکمیلی','tab:matlab')+latex_fig('MATLAB1.png','محیط MATLAB و اجرای کد دریافت','fig:matlab')+'\\clearpage\n'
latex+=heading('مسیر ب؛ GNU Radio و نرم‌افزارهای ویندوز')+'\\rp{نسخهٔ محیط در شکل \\ref{fig:gnu} و پنجرهٔ طیف در شکل \\ref{fig:grspec} مستند شده‌اند. فایل اصلی فلوگراف در ورودی موجود نبود. جدول \\ref{tab:windows} اطلاعات قابل‌خواندن را ثبت می‌کند.}\n'
latex+=ltable([('نسخهٔ GNU Radio',ltr('3.10.12.0')),('نسخهٔ Python همراه',ltr('3.12.9')),('نرم‌افزارهای آماده',ltr('SDR++ 1.3.2 / SDRangel 8.0.0')),(r'فرکانس نمایشی در SDRpp\_2',ltr('96 MHz')),(r'بهره در SDRpp\_2',ltr('45 dB')),(r'مسیر نمایش‌داده‌شده در SDRpp\_2',ltr('(usb)')),(r'فرکانس در SDR\_angle1',ltr('90 MHz'))],'ثبت اطلاعات مسیر ویندوز','tab:windows')
latex+=para('دستورکار، فرکانس ۹۴۵ مگاهرتز و بهرهٔ دستی حداکثر ۳۰ دسی‌بل با آنتن را تعیین می‌کند. توضیح انتخاب تنظیمات ثبت‌شده و پاسخ به معیار پذیرش، در بخش تحلیل توسط تیم تکمیل می‌شود.')+latex_fig('gnuRadoWindowsVersion.png','پنجرهٔ نسخهٔ GNU Radio Companion','fig:gnu')+latex_fig('GNUradioWindows_Spectrum.png','پنجرهٔ طیف در GNU Radio ویندوز','fig:grspec')+'\\clearpage\n'
latex+='\\rp{شکل‌های \\ref{fig:sdpp} و \\ref{fig:angle} تصاویر دو نرم‌افزار آماده را نشان می‌دهند. این تصاویر به‌خودی‌خود تأیید انجام آزمون خواسته‌شده در دستورکار نیستند.}\n'+latex_fig('SDRpp_2.png','رابط SDR++ و تنظیمات ثبت‌شده','fig:sdpp')+latex_fig('SDR_angle1.png','رابط SDRangel و تنظیمات ثبت‌شده','fig:angle')+'\\clearpage\n'
latex+=heading('مسیر ج؛ اوبونتو')+student_tex('ubuntu','ثبت مسیر اوبونتو','در فایل‌های ورودی، مدرکی از این مسیر وجود ندارد. نسخهٔ اوبونتو، نسخهٔ GNU Radio، خروجی iio_info، تصویر GRC و آزمون ابزار اضافی باید افزوده شوند.')
latex+=heading('مسیر د؛ پایتون')+'\\rp{خروجی قابل‌خواندن ترمینال در شکل \\ref{fig:python} برابر \\lr{samples: (4096,) sample\\_rate: 2600000} است. جدول \\ref{tab:python} تنظیمات کد را ثبت می‌کند.}\n'
latex+=ltable([('نشانی اتصال',ltr('ip:192.168.1.10')),('فرکانس مرکزی',ltr('945 MHz')),('نرخ نمونه / پهنای باند',ltr('2.6 / 2 MHz')),('حالت و بهرهٔ گیرنده',ltr('manual / 20 dB')),('اندازهٔ بافر',ltr('4096')),('نسخهٔ pyadi-iio',tex(D['pyadi_version'])),('محیط اجرا','مسیر ترمینال شامل '+ltr('radioconda')+' است')],'تنظیمات قابل‌خواندن پایتون','tab:python')+latex_fig('Python_output.png','اسکریپت، نمودار و خروجی ترمینال در VS Code','fig:python')+'\\clearpage\n'
latex+=heading('وضعیت آمادگی و داده‌های خام')+'\\rp{جدول \\ref{tab:ready} وضعیت مدارک را بر اساس جدول ۱۰ دستورکار نشان می‌دهد. این جدول جای امضای دستیار را نمی‌گیرد.}\n'
latex+=ltable([('شبکه','تصویر پاسخ موجود؛ تصویر IPv4 لازم است'),('الف','تصویر اجرا موجود؛ مشخصات دستگاه لازم است'),('ب','تصاویر موجود؛ فلوگراف و ثبت آزمون نهایی لازم است'),('ج','مدرک ارائه نشده'),('د','تصویر خروجی موجود؛ نسخه و فایل خام لازم است')],'وضعیت مدارک آمادگی','tab:ready')
latex+=para('فایل خام I/Q، فایل اصلی GRC، کد اصلی جلسه و لاگ کامل همراه ورودی نبودند. هیچ عددی برای توان، SNR یا کیفیت دریافت از روی تصاویر استخراج نشده است. اسکرین‌شات رابط نرم‌افزار فقط به‌عنوان مدرک رابط نگه داشته شده است؛ نمودار علمی نهایی باید از دادهٔ خام و ترجیحاً به‌صورت برداری تولید شود.')
latex+=heading('تحلیل و عیب‌یابی')+student_tex('analysis','تحلیل نتایج','اعضای تیم توضیح خود را دربارهٔ معیار پذیرش، تنظیمات و شواهد هر مسیر می‌نویسند. ادعاهای عددی باید به فایل خام مشخص متصل باشند.')+student_tex('troubleshooting','عیب‌یابی','نشانهٔ خطا، اقدام واقعی و نتیجهٔ آزمون مجدد را از لاگ جلسه وارد کنید.')
latex+=heading('نتیجه‌گیری')+student_tex('conclusion','جمع‌بندی','اعضای تیم جمع‌بندی خود را دربارهٔ آزمون‌های انجام‌شده، مدارک موجود و کارهای باقی‌مانده می‌نویسند.')
latex+=heading('اعلام استفاده از هوش مصنوعی')+para('در تهیهٔ این نسخه از ChatGPT برای ساخت قالب HTML/CSS و LaTeX، ویرایش نگارشی، سامان‌دهی تصاویر، رونویسی تنظیمات قابل‌خواندن و آماده‌کردن قالب کد استفاده شده است. بخش‌های تحلیل، تفسیر داده و نتیجه‌گیری در این نسخه خالی مانده‌اند تا اعضای تیم آن‌ها را بنویسند. مسئولیت بررسی نهایی با اعضای تیم است.')
latex+='\\begin{minipage}{\\linewidth}\n\\small\n\\bibliographystyle{plainnat}\n\\bibliography{references}\n\\end{minipage}\n\\end{document}\n'
(ROOT/'latex/report.tex').write_text(latex,encoding='utf-8')
print('Generated index.html, reports/lab00/index.html, config.js, favicon.svg, latex/report.tex')
