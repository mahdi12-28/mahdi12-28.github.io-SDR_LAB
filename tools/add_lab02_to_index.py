#!/usr/bin/env python3
"""Run at the repository root: python3 tools/add_lab02_to_index.py"""
from pathlib import Path
import re
p = Path('index.html')
if not p.exists():
    raise SystemExit('index.html not found. Run this script from the repository root.')
s = p.read_text(encoding='utf-8')
if 'experiments/lab02/pre/' in s:
    print('Lab02 entry already exists; nothing changed.')
    raise SystemExit(0)
row = '<tr><td><span class="lab-number">02</span></td><td>عدد نویز و پارامترهای RF<small>Noise Figure, P1dB and IIP3 — راهنمای مدرس: آزمایش ۸</small></td><td><a href="experiments/lab02/pre/">پیش‌گزارش ←</a><small>تکالیف ۱، ۲، ۳ و ۶؛ تکالیف ۴ و ۵ در انتظار تکمیل</small></td><td><span class="text-muted">هنوز منتشر نشده</span><small>گزارش پس از جلسه آماده نیست</small></td><td>اعلام نشده</td></tr>'
# Insert within the specific experiments table immediately before its closing tbody.
pat = r'(<section\b[^>]*\bid=["\']experiments["\'][\s\S]*?<tbody>)([\s\S]*?)(</tbody>)'
m = re.search(pat, s)
if not m:
    raise SystemExit('Could not locate experiments table; edit index.html manually.')
s = s[:m.start()] + m.group(1) + m.group(2) + row + m.group(3) + s[m.end():]
s = s.replace('<b>02</b><span>آزمایش در آرشیو</span>', '<b>03</b><span>آزمایش در آرشیو</span>', 1)
s = s.replace('<b>03</b><span>گزارش قابل مشاهده</span>', '<b>04</b><span>گزارش قابل مشاهده</span>', 1)
p.write_text(s, encoding='utf-8')
print('Updated index.html with Lab02 pre-lab entry.')
