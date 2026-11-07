#!/usr/bin/env python3
"""Package one self-contained LaTeX source archive per included report."""
from pathlib import Path
import json
import argparse
import zipfile
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--lab')
parser.add_argument('--kind',choices=['pre','post'])
args=parser.parse_args()
for r in json.loads((ROOT/'content/generated.json').read_text(encoding='utf-8')):
    if (args.lab and r['lab']!=args.lab) or (args.kind and r['kind']!=args.kind):continue
    target=ROOT/'downloads'/(r['source_zip']+'.zip')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        source=(ROOT/'latex'/(r['tex']+'.tex')).read_text(encoding='utf-8').replace('../assets/','assets/')
        z.writestr('report.tex',source)
        z.write(ROOT/'latex/references.bib','references.bib')
        # Include all local images and fonts so figure paths remain exact.
        for p in sorted((ROOT/'assets').rglob('*')):
            if p.is_file() and p.suffix.lower() in ['.png','.jpg','.jpeg','.webp','.ttf','.otf','.txt']:
                z.write(p,p.relative_to(ROOT))
        bib='bibtex report\n' if r'\bibliography{' in source else ''
        z.writestr('README.txt','From this directory run:\nxelatex report.tex\n'+bib+'xelatex report.tex\nxelatex report.tex\nCompiler: XeLaTeX. A full TeX Live/MiKTeX distribution is required. For Overleaf, select report.tex as the main document and XeLaTeX as compiler.\n')
    print('Built '+str(target.relative_to(ROOT)))
