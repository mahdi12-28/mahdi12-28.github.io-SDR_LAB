#!/usr/bin/env python3
"""Print the same offline HTML report to PDF. Requires WeasyPrint >= 68."""
from pathlib import Path
import shutil
import logging
from weasyprint import HTML, CSS

ROOT=Path(__file__).resolve().parents[1]
POST=ROOT/'experiments/lab02/post'
logging.getLogger('weasyprint').setLevel(logging.ERROR)
footer=CSS(string='''
@page {
 @bottom-center {
  content: "SDR LAB 02  /  " counter(page) " / " counter(pages);
  font-family: sans-serif; font-size: 8pt; color: #596e77; direction: ltr;
 }
}
''')
HTML(filename=str(POST/'index.html')).write_pdf(str(POST/'report.pdf'),stylesheets=[footer])
shutil.copyfile(POST/'report.pdf',ROOT/'lab02/report.pdf')
shutil.copyfile(POST/'report.pdf',ROOT/'downloads/lab02-post.pdf')
print('Built report.pdf and compatibility copies.')
