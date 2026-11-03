# !/usr/bin/env python3
"""Enter the two names and IDs once; refresh every HTML/PDF afterward."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
members=[]
for i in [1,2]:
    name=input(f'Name and surname for member {i}: ').strip()
    sid=input(f'Student ID for member {i}: ').strip()
    if not name or not sid:raise SystemExit('All four fields are required. No changes were saved.')
    members.append({'name':name,'student_id':sid})
(ROOT/'content/team.json').write_text(json.dumps({'members':members},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if shutil.which('xelatex') and shutil.which('bibtex'):
    subprocess.run([sys.executable,str(ROOT/'tools/refresh.py')],check=True)
else:
    subprocess.run([sys.executable,str(ROOT/'tools/build.py')],check=True)
    subprocess.run([sys.executable,str(ROOT/'tools/package.py')],check=True)
    print('Names saved and HTML rebuilt. PDF still has the earlier identity fields.')
    print('Install full TeX Live/MiKTeX, then run: python tools/refresh.py')
