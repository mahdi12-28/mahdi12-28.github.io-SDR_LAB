#!/usr/bin/env python3
"""Bundle the current LaTeX source; run after build.py / build-pdf.sh."""
from pathlib import Path
import zipfile
R=Path(__file__).resolve().parents[1]
with zipfile.ZipFile(R/'downloads/lab00-latex-source.zip','w',zipfile.ZIP_DEFLATED) as z:
    for folder in ['latex','assets/images','assets/fonts']:
        for p in sorted((R/folder).rglob('*')):
            if p.is_file() and (p.suffix in ['.tex','.bib','.png','.ttf','.txt']):
                z.write(p,p.relative_to(R))
    z.write(R/'tools/build-pdf.sh','tools/build-pdf.sh')
    z.writestr('README.txt','Run bash tools/build-pdf.sh from a full TeX Live environment. The bundled font is DejaVu Sans. This draft requires student-authored analysis and conclusion. See the main site README for completion requirements.\n')
print('Built downloads/lab00-latex-source.zip')
