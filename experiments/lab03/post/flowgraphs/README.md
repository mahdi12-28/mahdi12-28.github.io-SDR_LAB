# مسیر بلوک‌های FM

کد `fm_offline_reference.py` بازسازی مرجع از دستورکار برای GNU Radio 3.10 است؛ فایل اصلی اجرای جلسه محسوب نمی‌شود. کد فقط با فایل کار می‌کند و سخت‌افزار RF را باز یا فعال نمی‌کند. نحو پایتون بررسی شده است؛ اجرای این نسخه به نصب GNU Radio نیاز دارد.

| مسیر | بلوک‌ها / پارامترهای اصلی |
| --- | --- |
| ورودی زنده در طراحی دستورکار | Source در 2.4 MS/s، فرکانس `fc−250e3`؛ فیلتر Frequency Xlating با کاهش نرخ ۱۰ |
| ورودی نسخهٔ آفلاین | File Source، complex64، 240 kS/s؛ پس از انتخاب کانال و انتقال به باند پایه |
| فیلتر کانال | `chan_bw=min(2*(dev+audio_bw),200e3)`، قطع `chan_bw/2`، گذار `chan_bw/8` |
| تمایزگر | `gain=240000/(2*pi*dev)` |
| PLL | `loop_bw=pll_bw`، حدود فرکانس `±min(2*pi*1.5*dev/240000,3)`، سپس ضرب در gain |
| مسیر صوت هر آشکارساز | LPF با کاهش نرخ ۵، قطع audio_bw، گذار `0.25*audio_bw+250`؛ DC Blocker طول ۵۱۲؛ Deemphasis با τ=75 μs |
| تولید مرجع تک‌تن | Cosine(am=1) → Frequency Modulator(kf=2*pi*dev/240000) → ضریب دامنهٔ 0.5 → File Sink |

نمونهٔ اجرای آفلاین برای ایستگاه:

```bash
python flowgraphs/fm_offline_reference.py rx iq/actual_capture.cf32 --dev 75000 --pll-bw 0.15
```

ساخت یک سیگنال **نظری** برای مقایسه یا بررسی ابزار:

```bash
python flowgraphs/fm_offline_reference.py tx theoretical_tone.cf32 --fm 1000 --dev 5000 --seconds 5
```

خروجی نظری را در manifest اندازه‌گیری‌های واقعی جلسه وارد نکنید. نسخه‌های اصلی GRC جلسه را می‌توان با همان نام اصلی در این پوشه اضافه کرد.
