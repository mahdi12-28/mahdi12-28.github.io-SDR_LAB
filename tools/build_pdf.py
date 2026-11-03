#!/usr/bin/env python3
"""Compile generated LaTeX and copy each matching PDF into downloads."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--lab')
    p.add_argument('--kind',choices=['pre','post'])
    a=p.parse_args()
    for tool in ['xelatex','bibtex']:
        if not shutil.which(tool):raise SystemExit(f'{tool} is required: install a full TeX Live or MiKTeX distribution.')
    records=json.loads((ROOT/'content/generated.json').read_text(encoding='utf-8'))
    selected=[r for r in records if (not a.lab or r['lab']==a.lab) and (not a.kind or r['kind']==a.kind)]
    if not selected:raise SystemExit('No included report matches the selection; run build.py first.')
    (ROOT/'downloads').mkdir(exist_ok=True)
    for r in selected:
        cmd=['xelatex','-interaction=nonstopmode','-halt-on-error',r['tex']+'.tex']
        for command in [cmd,['bibtex',r['tex']],cmd,cmd]:subprocess.run(command,cwd=ROOT/'latex',check=True)
        target=ROOT/'downloads'/(r['pdf']+'.pdf')
        shutil.copyfile(ROOT/'latex'/(r['tex']+'.pdf'),target)
        print('Built '+str(target.relative_to(ROOT)))
if __name__=='__main__':main()
