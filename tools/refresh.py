#!/usr/bin/env python3
"""Refresh HTML, LaTeX, PDFs and source archives in the required order."""
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
for script in ['build.py','build_pdf.py','package.py','check.py']:
    subprocess.run([sys.executable,str(ROOT/'tools'/script)],cwd=ROOT,check=True)
print('HTML, PDF and source ZIP files are now synchronized.')
