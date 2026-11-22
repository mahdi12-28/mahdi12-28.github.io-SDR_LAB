#!/usr/bin/env python3
"""Render local report with WeasyPrint; all fonts and figures are bundled."""
from pathlib import Path
from weasyprint import HTML, CSS
R=Path(__file__).resolve().parents[1]
footer=CSS(string='''@page{
  @bottom-left{content:"SDR LAB / LAB 03 / FM RADIO";font:8pt sans-serif;color:#647580;direction:ltr}
  @bottom-right{content:counter(page) " / " counter(pages);font:8pt sans-serif;color:#647580;direction:ltr}
}''')
HTML(filename=str(R/'index.html')).write_pdf(str(R/'report.pdf'),stylesheets=[footer])
print(R/'report.pdf')
