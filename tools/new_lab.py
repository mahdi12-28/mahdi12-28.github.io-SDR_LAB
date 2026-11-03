#!/usr/bin/env python3
"""Create independent pre/post sources and register a lab without publishing it."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('number',type=int)
    p.add_argument('--title',required=True)
    a=p.parse_args()
    if not 1<=a.number<=999:p.error('number must be 1..999')
    lab_id=f'lab{a.number:02}'
    registry=ROOT/'content/experiments.json'
    labs=json.loads(registry.read_text(encoding='utf-8'))
    if any(l['id']==lab_id for l in labs) or (ROOT/'content'/lab_id).exists():
        p.error('Lab already exists; existing work was not changed')
    labs.append({'id':lab_id,'number':a.number,'title':a.title,'subtitle':'','session_date':'هنوز ثبت نشده',
        'pre':{'publish':False,'status':'در حال آماده‌سازی','date':'هنوز تحویل نشده'},
        'post':{'publish':False,'status':'در حال آماده‌سازی','date':'هنوز تحویل نشده'}})
    for kind in ['pre','post']:
        titles=['هدف و مبانی','پرسش‌های پیش‌گزارش','محاسبات و شبیه‌سازی','مراجع'] if kind=='pre' else ['هدف و روش اجرا','تنظیمات و داده‌های خام','مشاهدات و نتایج','تحلیل اعضای گروه','عیب‌یابی','نتیجه‌گیری اعضای گروه','فایل‌های همراه','داوری همتا','مراجع']
        sections=[]
        for i,title in enumerate(titles):
            blocks=[]
            if title=='فایل‌های همراه':blocks=[{'type':'downloads'}]
            elif title=='داوری همتا':blocks=[{'type':'comments'}]
            sections.append({'id':'downloads' if title=='فایل‌های همراه' else 'comments' if title=='داوری همتا' else f'section-{i+1}','title':title,'blocks':blocks})
        # The toolbar links to downloads, so pre-reports also need a files section.
        if kind=='pre':sections.insert(-1,{'id':'downloads','title':'فایل‌های همراه','blocks':[{'type':'downloads'}]})
        dump(ROOT/'content'/lab_id/(kind+'.json'),{'title':a.title,'summary':'','document_note':'','attachments':[],'references':[],'bib_keys':['regulations'],'sections':sections})
    dump(registry,sorted(labs,key=lambda x:x['number']))
    (ROOT/'assets'/lab_id).mkdir(parents=True,exist_ok=True)
    (ROOT/'data'/lab_id).mkdir(parents=True,exist_ok=True)
    (ROOT/'code'/lab_id).mkdir(parents=True,exist_ok=True)
    print(f'Created content/{lab_id}/pre.json and post.json; both publish=false.')
    print('Write the report, set publish=true in content/experiments.json when appropriate, then run python tools/refresh.py.')
if __name__=='__main__':main()
