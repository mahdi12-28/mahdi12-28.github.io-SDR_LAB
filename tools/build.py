#!/usr/bin/env python3
"""Build the semester archive and matching LaTeX from JSON. Standard library only."""
from pathlib import Path
from html import escape
import json
import re

ROOT=Path(__file__).resolve().parents[1]
def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def write(path,text):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
SITE=read('content/site.json');TEAM=read('content/team.json');LABS=read('content/experiments.json')
if len(TEAM['members'])!=2: raise ValueError('team.json must contain exactly two members')
PHOTOS=[('pingingSDR.png','network','آزمون ping'),('gnuRadoWindowsVersion.png','gnu','نسخهٔ GNU Radio'),('GNUradioWindows_Spectrum.png','gnu','پنجرهٔ طیف GNU Radio'),('MATLAB1.png','matlab','کد و پنجرهٔ MATLAB'),('MATLAB2.png','matlab','نمای نزدیک Spectrum Analyzer'),('MATLAB3.png','matlab','محیط MATLAB و آبشار'),('MATLAB4.png','matlab','ثبت دیگر MATLAB'),('Python_output.png','python','کد و خروجی پایتون'),('SDRpp.png','ready','SDR++ در ۹۲۴ مگاهرتز'),('SDRpp_2.png','ready','SDR++ در ۹۶ مگاهرتز'),('SDRpp_3.png','ready','ثبت دیگر SDR++ در ۹۲۴ مگاهرتز'),('SDRpp_4.png','ready','طیف و آبشار SDR++'),('SDRpp_5.png','ready','نمای دیگر SDR++'),('SDR_angle1.png','ready','طیف SDRangel در ۹۰ مگاهرتز'),('SDR_angle2.png','ready','محیط SDRangel'),('SDR_angle3.png','ready','تنظیم منبع در SDRangel'),('SDR_angle4.png','ready','نمای دیگر SDRangel')]
REFS=['دستورکار آزمایش ۰: راه‌اندازی محیط و نصب نرم‌افزارها. آزمایشگاه رادیو نرم‌افزار؛ فایل lab_00_setup(1).pdf، ۱۳ صفحه؛ به‌ویژه صفحات ۲–۴ و ۶–۱۲.','آیین‌نامه، مقررات و سناریوی اجرایی آزمایشگاه رادیو نرم‌افزار. نسخهٔ ۱٫۰، نیمسال اول ۱۴۰۵–۱۴۰۶؛ فایل regulations(1).pdf؛ بخش‌های ۳، ۴، ۵، ۷-۵ و ۸-۱.','آرشیو تصاویر جلسهٔ گروه، Lab0_photos(1).zip؛ ۱۷ تصویر رابط نرم‌افزار با نام و محتوای اصلی.']
def fa(x):return str(x).translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹'))
def esc(x):return escape(str(x),quote=True)
def inline(text):return ''.join('<bdi class="technical" dir="ltr">'+esc(p)+'</bdi>' if i%2 else esc(p) for i,p in enumerate(str(text).split('`')))
def route(lab,kind):return f'experiments/{lab["id"]}/{kind}/'
def stem(lab,kind):return 'report' if lab['id']=='lab00' and kind=='post' else lab['id']+'-'+kind
def pdf_name(lab,kind):return 'lab00-report' if lab['id']=='lab00' and kind=='post' else lab['id']+'-'+kind
def source_name(lab,kind):return 'lab00-latex-source' if lab['id']=='lab00' and kind=='post' else lab['id']+'-'+kind+'-latex-source'
def members_html():
    rows=[]
    for i,m in enumerate(TEAM['members'],1):
        name=esc(m['name']) if m['name'].strip() else '<span class="identity-blank" aria-label="نام عضو خالی است">&nbsp;</span>'
        sid='<bdi dir="ltr">'+esc(m['student_id'])+'</bdi>' if m['student_id'].strip() else '<span class="identity-blank" aria-label="شمارهٔ دانشجویی خالی است">&nbsp;</span>'
        rows.append('<tr><th scope="row">عضو '+fa(i)+'</th><td>'+name+'</td><td>'+sid+'</td></tr>')
    return '<div class="table-box identity-table"><table><thead><tr><th>عضو</th><th>نام و نام خانوادگی</th><th>شمارهٔ دانشجویی</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'
def shell(title,body,base='',term='',math=False):
    scripts=f'<script defer src="{base}assets/js/config.js"></script><script defer src="{base}assets/js/site.js"></script>'
    if math:scripts+='<script>window.MathJax={tex:{tags:"ams",inlineMath:[["\\\\(","\\\\)"]]}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"></script>'
    return f'''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="آرشیو پیش‌گزارش‌ها، گزارش‌ها و مدارک آزمایشگاه رادیو نرم‌افزار"><meta name="theme-color" content="#142d3d"><title>{esc(title)}</title><link rel="stylesheet" href="{base}assets/css/site.css"><link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">{scripts}</head><body data-comment-term="{esc(term)}"><a class="skip" href="#main">رفتن به محتوا</a><header class="topbar"><div class="wrap nav"><a class="brand" href="{base}index.html"><span class="brand-mark">sdr.</span><span>دفتر آزمایش رادیو نرم‌افزار<small dir="ltr">SOFTWARE DEFINED RADIO LAB</small></span></a><nav class="nav-links" aria-label="پیمایش اصلی"><a href="{base}index.html#experiments">آرشیو نیمسال</a><a href="{base}experiments/lab00/post/">آزمایش صفر</a><a href="{base}index.html#team">اعضای گروه</a></nav></div></header>{body}<footer class="footer"><div class="wrap"><span>{esc(SITE['team_name'])} · {esc(SITE['semester'])}</span><span>{esc(SITE['instructor'])} · آزمایشگاه رادیو نرم‌افزار</span></div></footer><dialog class="lightbox" id="image-dialog" aria-labelledby="dialog-title"><div class="dialog-top"><b id="dialog-title">تصویر آزمایش</b><div><button type="button" data-zoom>اندازهٔ اصلی</button> <button type="button" data-close>بستن ×</button></div></div><p class="dialog-help">برای خواندن جزئیات، اندازهٔ اصلی را انتخاب کنید. کلید Escape پنجره را می‌بندد.</p><div class="zoom-area"><img alt=""></div></dialog></body></html>'''
def image_path(b):
    p=b.get('path','assets/images/'+b.get('file',''));resolved=(ROOT/p).resolve()
    if ROOT not in resolved.parents or not resolved.is_file():raise ValueError('Missing project image: '+p)
    return p
def html_figure(b,num=None,group=None):
    p='../../../'+image_path(b);cap=b['caption'];attr=f' data-group="{group}"' if group else '';label='شکل '+fa(num)+'. ' if num else ''
    return f'<figure class="report-figure"{attr}><button type="button" class="figure-button" data-image="{esc(p)}" data-caption="{esc(cap)}" aria-label="بزرگ‌نمایی: {esc(cap)}"><img src="{esc(p)}" alt="{esc(cap)}" loading="lazy"><span class="zoom-hint">بزرگ‌نمایی ↗</span></button><figcaption><b>{label}</b>{esc(cap)}</figcaption></figure>'
def html_table(b,num):
    return '<div class="table-box"><table><thead><tr>'+''.join('<th scope="col">'+inline(h)+'</th>' for h in b['headers'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in row)+'</tr>' for row in b['rows'])+'</tbody><caption>جدول '+fa(num)+'. '+inline(b['caption'])+'</caption></table></div>'
def gallery():
    filters=''.join(f'<button type="button" class="filter" data-filter="{k}" aria-pressed="{str(k=="all").lower()}">{v}</button>' for k,v in [('all','همه'),('network','شبکه'),('matlab','MATLAB'),('gnu','GNU Radio'),('python','پایتون'),('ready','ابزارهای آماده')])
    return '<p>هر ۱۷ تصویر با نام و محتوای اصلی نگه داشته شده‌اند. روی تصویر بزنید تا نسخهٔ کامل باز شود.</p><div class="gallery-tools"><div class="filters" role="group" aria-label="فیلتر تصاویر">'+filters+'</div><span id="gallery-count" class="small text-muted" aria-live="polite">۱۷ تصویر</span></div><div class="gallery">'+''.join(html_figure({'file':f,'caption':c},group=g) for f,g,c in PHOTOS)+'</div>'
def downloads(lab,kind,doc):
    files=[(f'downloads/{pdf_name(lab,kind)}.pdf','گزارش PDF','ساخته‌شده با LaTeX'),(f'downloads/{source_name(lab,kind)}.zip','منبع LaTeX و تصاویر','قابل بازبینی و کامپایل'),(f'latex/{stem(lab,kind)}.tex','فایل TEX','منبع همین گزارش'),('latex/references.bib','مراجع BibTeX','مراجع مشترک')]
    if doc.get('attachments_only'):files=[]
    if lab['id']=='lab00':files += [('code/pluto_receive_template.py','قالب دریافت پایتون','بازنویسی آموزشی؛ فایل اصلی جلسه نیست'),('code/matlab_receive_template.m','قالب دریافت MATLAB','بازنویسی آموزشی؛ فایل اصلی جلسه نیست'),('data/README.md','وضعیت دادهٔ خام','دادهٔ I/Q در ورودی موجود نبود'),('flowgraphs/README.md','وضعیت فلوگراف','فایل اصلی GRC در ورودی موجود نبود')]
    files += [(a['path'],a['title'],a.get('description','فایل همراه')) for a in doc.get('attachments',[])]
    return '<div class="files">'+''.join(f'<a class="file" href="../../../{esc(p)}"><b>{esc(t)} ↙</b><small>{esc(d)}</small></a>' for p,t,d in files)+'</div>'
def comments():return '<p>داوری شامل نکتهٔ فنی مثبت، ادعای نیازمند مدرک، پرسش دقیق و امتیاز خوانایی از ۱ تا ۵ همراه با دلیل است. کامنت‌های داوری نباید توسط گروه میزبان حذف یا ویرایش شوند [۲، بندهای ۳-۴ و ۵-۲].</p><div id="comment-status" class="comment-status">اتصال داوری به مخزن GitHub هنوز پیکربندی نشده است. پس از ثبت شناسه‌های مخزن در تنظیمات سایت، کامنت‌های واقعی همین گزارش نمایش داده می‌شوند.</div><div class="giscus"></div><noscript><p>برای ثبت کامنت، JavaScript را فعال کنید.</p></noscript>'
def html_document(lab,kind,doc):
    parts=[];fig=tab=0
    for i,sec in enumerate(doc['sections'],1):
        blocks=[]
        for b in sec['blocks']:
            t=b['type']
            if t=='paragraph':blocks.append('<p>'+inline(b['text'])+'</p>')
            elif t=='bullets':blocks.append('<ul>'+''.join('<li>'+inline(x)+'</li>' for x in b['items'])+'</ul>')
            elif t=='code':blocks.append('<pre>'+esc(b['text'])+'</pre>')
            elif t=='equation':blocks.append('<div class="equation">\\begin{equation}'+esc(b['latex'])+'\\end{equation}</div>')
            elif t=='table':tab+=1;blocks.append(html_table(b,tab))
            elif t=='figure':fig+=1;blocks.append(html_figure(b,fig))
            elif t=='gallery':blocks.append(gallery())
            elif t=='downloads':blocks.append(downloads(lab,kind,doc))
            elif t=='comments':blocks.append(comments())
            elif t=='references':blocks.append('<ol class="source-list">'+''.join('<li>'+inline(r)+'</li>' for r in doc.get('references',REFS))+'</ol>')
            else:raise ValueError('Unknown block type: '+t)
        parts.append(f'<section class="report-section" id="{esc(sec["id"])}"><span class="section-index">{i:02} / {lab["id"].upper()}</span><h2>{esc(sec["title"])}</h2>'+''.join(blocks)+'</section>')
    if doc.get('attachments_only'):
        body='<main id="main" class="wrap section"><h1>'+esc(doc['title'])+'</h1>'+''.join(parts)+'<a class="top-link" href="../../../index.html#experiments">بازگشت به فهرست آزمایش‌ها ←</a></main>'
        return shell(doc['title'],body,'../../../')
    name='پیش‌گزارش' if kind=='pre' else 'گزارش پس از جلسه';rec=lab[kind]
    note='<div class="note neutral"><p>'+inline(doc['document_note'])+'</p></div>' if doc.get('document_note') else ''
    toc=''.join('<a href="#'+esc(s['id'])+'">'+esc(s['title'])+'</a>' for s in doc['sections'])
    other='post' if kind=='pre' else 'pre';related=f'<a class="btn" href="../{other}/">'+('گزارش پس از جلسه' if other=='post' else 'پیش‌گزارش')+' ←</a>' if lab[other]['publish'] else ''
    body=f'''<main id="main"><div class="page-heading"><div class="wrap"><div class="crumb"><a href="../../../index.html#experiments">آرشیو نیمسال</a> / آزمایش {fa(lab['number'])} / {name}</div><div class="title-line"><div><p class="eyebrow">{lab['id'].upper()} / {kind.upper()}-SESSION</p><h1>{esc(doc['title'])}</h1><p class="lead">{inline(doc.get('summary',''))}</p><div class="meta"><span>تاریخ جلسه: {esc(lab['session_date'])}</span><span>وضعیت: {esc(rec['status'])}</span><span>تحویل: {esc(rec['date'])}</span></div></div><span class="large-id" aria-hidden="true">{lab['number']:02}</span></div><div class="actions"><a class="btn primary" href="../../../downloads/{pdf_name(lab,kind)}.pdf">دریافت PDF ↙</a><a class="btn" href="#downloads">منبع و فایل‌ها ↙</a>{related}<button type="button" class="print-button" data-print>چاپ صفحه</button></div>{note}<h2 class="small">مشخصات اعضای گروه</h2>{members_html()}</div></div><div class="wrap report-layout"><aside class="toc" aria-label="فهرست گزارش"><p>در این گزارش</p>{toc}</aside><article>{''.join(parts)}<a class="top-link" href="#main">بازگشت به ابتدا ↑</a></article></div></main>'''
    return shell(doc['title']+' | '+name,body,'../../../',lab['id']+'-'+kind,True)
def homepage():
    rows=[]
    for lab in LABS:
        cells=[]
        for kind in ['pre','post']:
            rec=lab[kind]
            link=f'<a href="{route(lab,kind)}">'+('پیش‌گزارش' if kind=='pre' else 'گزارش')+' ←</a>' if rec['publish'] else '<span class="text-muted">'+esc(rec['status'])+'</span>'
            cells.append(link+'<small>'+esc(rec['date'])+'</small>')
        rows.append(f'<tr><td><span class="lab-number">{lab["number"]:02}</span></td><td>{esc(lab["title"])}<small>{esc(lab.get("subtitle",""))}</small></td><td>{cells[0]}</td><td>{cells[1]}</td><td>{esc(lab["session_date"])}</td></tr>')
    count=sum(lab[k]['publish'] for lab in LABS for k in ['pre','post'])
    body=f'''<main id="main"><section class="hero wrap"><div class="hero-grid"><div><p class="eyebrow">دفتر گزارش‌های آزمایشگاه / {esc(SITE['semester'])}</p><h1>از اولین اتصال<br><span>تا ثبت تجربهٔ آزمایش.</span></h1><p class="lead">پیش‌گزارش‌ها، تنظیمات اجرا، تصاویر جلسه و گزارش‌ها در یک آرشیو مشترک. برای هر آزمایش، مسیر آمادگی پیش از جلسه از مستندات پس از اجرا جداست.</p><div class="actions"><a class="btn primary" href="experiments/lab00/post/">گزارش آزمایش صفر ←</a><a class="btn" href="#experiments">آرشیو نیمسال ↓</a></div></div><div class="hero-art"><div class="instrument-heading"><span><i class="dot"></i> LAB 00 / CAPTURE ARCHIVE</span><span>MATLAB</span></div><a href="experiments/lab00/post/#matlab"><img src="assets/images/MATLAB2.png" alt="تصویر اصلی Spectrum Analyzer از آزمایش صفر" width="1061" height="657"></a><div class="instrument-footer"><span>fₛ 2.6 MS/s</span><span>ORIGINAL SCREENSHOT</span></div></div></div><div class="facts"><div class="fact"><b>{len(LABS):02}</b><span>آزمایش در آرشیو</span></div><div class="fact"><b>{count:02}</b><span>گزارش قابل مشاهده</span></div><div class="fact"><b>PRE / POST</b><span>دو مسیر مستقل هر جلسه</span></div><div class="fact"><b>17</b><span>تصویر از آزمایش صفر</span></div></div></section><section class="wrap section" id="experiments"><div class="section-head"><div><div class="section-label">SEMESTER ARCHIVE</div><h2>پیش‌گزارش‌ها و گزارش‌ها</h2></div><p>تاریخ، وضعیت و فایل‌های هر آزمایش</p></div><div class="table-box"><table><thead><tr><th>آزمایش</th><th>عنوان</th><th>پیش از جلسه</th><th>پس از جلسه</th><th>تاریخ جلسه</th></tr></thead><tbody>{''.join(rows)}</tbody><caption>وضعیت انتشار یک گزارش، جای تأیید آزمایش یا ثبت تحویل در فرم درس را نمی‌گیرد.</caption></table></div></section><section class="section wrap"><div class="section-head"><div><div class="section-label">FROM PREPARATION TO REVIEW</div><h2>روند ثبت هر آزمایش</h2></div></div><div class="semester-flow"><div><b>01</b><h3>پیش از جلسه</h3><p>هدف، مبانی، پرسش‌ها و محاسبات آمادگی.</p></div><div><b>02</b><h3>هنگام اجرا</h3><p>تنظیمات واقعی، دادهٔ خام و یادداشت خطاها.</p></div><div><b>03</b><h3>پس از جلسه</h3><p>گزارش، فایل‌ها و تحلیل اعضای گروه.</p></div><div><b>04</b><h3>داوری همتا</h3><p>پرسش و بازخورد فنی در صفحهٔ همان گزارش.</p></div></div></section><section class="section wrap overview"><div><p class="eyebrow">آزمایش صفر</p><h2>یک دستگاه، چهار مسیر نرم‌افزاری</h2><p class="text-muted">روش‌های مندرج در دستورکار و تنظیمات قابل‌خواندن از تصاویر جلسه در گزارش ثبت شده‌اند. نبود اطلاعات نیز صریح نوشته شده است.</p><a class="btn" href="experiments/lab00/post/#readiness">جدول وضعیت مدارک ←</a></div><div class="route-list">'''+''.join(f'<a class="route" href="experiments/lab00/post/#{key}"><b>{title}</b><span>{status} ↗</span></a>' for key,title,status in [('matlab','MATLAB','تصاویر و تنظیمات'),('windows','GNU Radio و ابزارهای آماده','نسخه‌ها و تصاویر'),('ubuntu','Ubuntu / GNU Radio','مدرک ارائه نشده'),('python','Python / pyadi-iio','خروجی نمونه‌ها')])+f'''</div></section><section class="section wrap" id="team"><div class="section-head"><div><div class="section-label">THE TEAM</div><h2>{esc(SITE['team_name'])}</h2></div><p>{esc(SITE['instructor'])}</p></div>{members_html()}</section></main>'''
    return shell('دفتر آزمایش رادیو نرم‌افزار | آرشیو نیمسال',body)
def tescape(x):
    r={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(r.get(c,c) for c in str(x))
def tin(text):
    return ''.join(r'\lr{'+tescape(p)+'}' if i%2 or (p and all(ord(c)<128 for c in p)) else tescape(p) for i,p in enumerate(str(text).split('`')))
def para(text):return '\\rp{'+tin(text)+'}\n\n'
PREAMBLE=r'''\documentclass[10pt,a4paper]{article}
\usepackage[margin=21mm,headheight=14pt]{geometry}
\usepackage{fontspec,graphicx,float,amsmath,xcolor,titlesec,needspace}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage[numbers]{natbib}
\setmainfont[Path=../assets/fonts/,BoldFont=Estedad-Bold.ttf,ItalicFont=Estedad-Medium.ttf,Script=Arabic,Language=Persian]{Estedad-Medium.ttf}
\newfontfamily\latinfont[Path=../assets/fonts/,BoldFont=Estedad-Bold.ttf]{Estedad-Medium.ttf}
\TeXXeTstate=1
\newcommand{\rtl}[1]{\beginR #1\endR}
\newcommand{\lr}[1]{\beginL{\latinfont #1}\endL}
\newcommand{\rp}[1]{\par\begingroup\rightskip=0pt\leftskip=0pt plus 1fil\parfillskip=0pt\noindent\beginR #1\endR\par\endgroup}
\renewcommand{\figurename}{\rtl{شکل}}
\renewcommand{\tablename}{\rtl{جدول}}
\renewcommand{\refname}{\rtl{مراجع}}
\hypersetup{hidelinks,pdftitle={SDR Laboratory Report},pdfauthor={SDR Lab Team}}
\pdfstringdefDisableCommands{\def\rtl#1{#1}\def\lr#1{#1}}
\setlength{\parindent}{0pt}\setlength{\parskip}{7pt}
\linespread{1.32}
\titleformat{\section}{\large\bfseries\raggedleft}{\thesection}{1em}{}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small\lr{SDR LAB}}\fancyfoot[C]{\thepage}
\begin{document}
'''
def latex_document(lab,kind,doc):
    name='پیش‌گزارش' if kind=='pre' else 'گزارش پس از جلسه'
    s=PREAMBLE+'\\fancyhead[R]{\\small\\rtl{آزمایش '+fa(lab['number'])+' | '+name+'}}\n'
    s+='\\begin{titlepage}\\begin{center}\\vspace*{12mm}\n{\\color{teal}\\Large\\lr{'+lab['id'].upper()+' / '+kind.upper()+'}}\\\\[12mm]\n{\\LARGE\\bfseries\\rtl{'+tescape(doc['title'])+'}}\\\\[9mm]\n'
    for line in [SITE['team_name'],SITE['instructor'],SITE['semester']]:s+='\\rtl{'+tescape(line)+'}\\\\[4mm]\n'
    s+='\\vspace{10mm}\n'
    for i,m in enumerate(TEAM['members'],1):
        who=tescape(m['name']) if m['name'].strip() else r'\rule{45mm}{0.3pt}'
        sid=r'\lr{'+tescape(m['student_id'])+'}' if m['student_id'].strip() else r'\rule{35mm}{0.3pt}'
        s+='\\rtl{عضو '+fa(i)+'؛ نام و نام خانوادگی: '+who+'}\\\\[5mm]\n\\rtl{شمارهٔ دانشجویی: '+sid+'}\\\\[9mm]\n'
    s+='\\rtl{تاریخ جلسه: '+tescape(lab['session_date'])+'}\\\\[4mm]\n\\rtl{تحویل: '+tescape(lab[kind]['date'])+'}\\\\[8mm]\n\\end{center}\n'
    if doc.get('document_note'):s+='\\begin{quote}'+para(doc['document_note'])+'\\end{quote}\n'
    s+='\\end{titlepage}\n';count=0
    for sec in doc['sections']:
        if sec.get('pdf') is False:continue
        blocks=[b for b in sec['blocks'] if b['type'] not in ['gallery','comments','references']]
        if not blocks:continue
        s+='\\Needspace{6\\baselineskip}\n\\section{\\rtl{'+tescape(sec['title'])+'}}\n'
        for b in blocks:
            t=b['type']
            if t=='paragraph':s+=para(b['text'])
            elif t=='bullets':s+='\\begin{itemize}\n'+''.join('\\item \\rtl{'+tin(x)+'}\n' for x in b['items'])+'\\end{itemize}\n'
            elif t=='code':s+='\\begin{quote}\\begin{flushleft}\\small\n'+''.join(r'\lr{'+tescape(line)+'}\\\\\n' for line in b['text'].splitlines())+'\\end{flushleft}\\end{quote}\n'
            elif t=='equation':s+='\\begin{equation}'+b['latex']+'\\label{'+b['label']+'}\\end{equation}\n'
            elif t=='figure':
                count+=1;label=b.get('label','fig:'+str(count));height='0.14' if b.get('compact') else '0.29'
                s+='\\rp{تصویر ثبت‌شده در شکل \\ref{'+label+'} آمده است.}\n\\begin{figure}[H]\\centering\\includegraphics[width=0.96\\linewidth,height='+height+'\\textheight,keepaspectratio]{../'+image_path(b)+'}\\caption{\\rtl{'+tin(b['caption'])+'}}\\label{'+label+'}\\end{figure}\n'
            elif t=='table':
                n=len(b['headers']);width=(0.94-0.025*n)/n;label=b['label']
                s+='\\rp{جدول \\ref{'+label+'} اطلاعات این بخش را ثبت می‌کند.}\n\\begin{table}[H]\\centering\\small\\renewcommand{\\arraystretch}{1.25}\n\\begin{tabular}{|'+('|'.join('p{'+str(round(width,3))+'\\linewidth}' for _ in range(n)))+'|}\\hline\n'
                s+=' & '.join(r'\rtl{\textbf{'+tin(x)+'}}' for x in reversed(b['headers']))+' \\\\ \\hline\n'
                s+=''.join(' & '.join(r'\rtl{'+tin(x)+'}' for x in reversed(row))+' \\\\ \\hline\n' for row in b['rows'])
                s+='\\end{tabular}\\caption{\\rtl{'+tin(b['caption'])+'}}\\label{'+label+'}\\end{table}\n'
            elif t=='downloads':s+=para('نسخهٔ HTML همین گزارش، PDF، منبع LaTeX، مراجع BibTeX و فایل‌های همراه از صفحهٔ گزارش در وب‌سایت قابل دریافت‌اند. در آرشیو نیمسال، پیش‌گزارش و گزارش هر آزمایش مسیرهای مستقلی دارند.')
    s+='\\Needspace{9\\baselineskip}\n\\nocite{'+','.join(doc.get('bib_keys',['regulations']))+'}\\bibliographystyle{plainnat}\\bibliography{references}\n\\end{document}\n'
    return s

def build():
    generated=[]
    for lab in LABS:
        if not re.fullmatch(r'lab\d{2,}',lab['id']):raise ValueError('Invalid lab id')
        for kind in ['pre','post']:
            dest=route(lab,kind)+'index.html'
            if not lab[kind]['publish']:
                (ROOT/dest).unlink(missing_ok=True)
                continue
            doc=read(f'content/{lab["id"]}/{kind}.json')
            if not any(b['type'] in ['paragraph','bullets','code','equation','table','figure'] for sec in doc['sections'] for b in sec.get('blocks',[])):raise ValueError('Cannot include a report with no substantive content')
            write(dest,html_document(lab,kind,doc))
            if doc.get('attachments_only'):continue
            write('latex/'+stem(lab,kind)+'.tex',latex_document(lab,kind,doc))
            generated.append({'lab':lab['id'],'kind':kind,'tex':stem(lab,kind),'pdf':pdf_name(lab,kind),'source_zip':source_name(lab,kind)})
    write('index.html',homepage());write('content/generated.json',json.dumps(generated,ensure_ascii=False,indent=2))
    write('assets/js/config.js','window.LAB_GISCUS = '+json.dumps(SITE['giscus'],ensure_ascii=False,indent=2)+';\n')
    write('reports/lab00/index.html','<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=../../experiments/lab00/post/"><title>گزارش آزمایش صفر</title><p><a href="../../experiments/lab00/post/">رفتن به گزارش آزمایش صفر</a></p></html>')
    print(f'Built homepage and {len(generated)} report(s); identity: content/team.json')
if __name__=='__main__':build()
