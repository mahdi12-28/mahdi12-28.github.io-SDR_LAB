#!/usr/bin/env python3
"""Export the authoritative lab01 JSON into an editable review copy."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'content/lab01/post.json').read_text())
lines=['# '+d['title'],'',d['summary'],'', '> '+d['document_note'],'']
for sec in d['sections']:
    lines+=['## '+sec['title'],'']
    for b in sec['blocks']:
        t=b['type']
        if t=='paragraph':lines +=[b['text'],'']
        elif t=='bullets':lines +=['- '+x for x in b['items']]+['']
        elif t=='table':
            lines+=['| '+' | '.join(b['headers'])+' |','| '+' | '.join(['---']*len(b['headers']))+' |']
            lines+=['| '+' | '.join(str(x).replace('|','\\|') for x in row)+' |' for row in b['rows']]+['',b['caption'],'']
        elif t=='figure':lines +=['!['+b['caption']+'](../../'+b['path'].replace(' ','%20')+')','']
        elif t=='references':lines +=d['references']+['']
        elif t=='downloads':lines +=['- ['+a['title']+'](../../'+a['path']+')' for a in d['attachments']]+['']
(R/'reports/lab01-post/report.md').write_text('\n'.join(lines))
print('Exported reports/lab01-post/report.md')
