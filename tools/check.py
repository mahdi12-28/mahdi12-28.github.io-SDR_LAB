#!/usr/bin/env python3
"""Check local links, fragments, published files and source archive integrity."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        self.links.extend(a[k] for k in ['href','src','data-image'] if k in a)
pages={}
for p in ROOT.rglob('*.html'):
    page=Page();page.feed(p.read_text(encoding='utf-8'));pages[p]=page
errors=[]
for p,page in pages.items():
    for url in page.links:
        u=urlsplit(url)
        if u.scheme or u.netloc:continue
        target=(p.parent/unquote(u.path)).resolve() if u.path else p
        if target.is_dir():target/='index.html'
        if not target.is_file():errors.append(f'{p.relative_to(ROOT)}: missing {url}')
        if u.fragment and target in pages and u.fragment not in pages[target].ids:
            errors.append(f'{p.relative_to(ROOT)}: missing fragment {url}')
for rec in json.loads((ROOT/'content/generated.json').read_text(encoding='utf-8')):
    for ext,key in [('pdf','pdf'),('zip','source_zip')]:
        path=ROOT/'downloads'/(rec[key]+'.'+ext)
        if not path.is_file():errors.append('Missing '+str(path.relative_to(ROOT)))
        elif ext=='zip':
            with zipfile.ZipFile(path) as z:
                bad=z.testzip()
                if bad:errors.append('Corrupt archive member '+bad)
                if 'report.tex' not in z.namelist():errors.append('Source archive lacks report.tex')
if errors:raise SystemExit('\n'.join(errors))
print(f'Checked {len(pages)} HTML pages: local links, anchors and source archives passed.')
