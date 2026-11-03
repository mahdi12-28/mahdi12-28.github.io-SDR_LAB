'use strict';
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
  document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  const group=button.dataset.filter;
  document.querySelectorAll('.gallery [data-group]').forEach(item=>{item.hidden=group!=='all'&&item.dataset.group!==group;});
  const count=document.querySelectorAll('.gallery [data-group]:not([hidden])').length;
  const output=document.getElementById('gallery-count');if(output)output.textContent=count.toLocaleString('fa-IR')+' تصویر';
}));
const dialog=document.getElementById('image-dialog');
let opener;
if(dialog){
 const large=dialog.querySelector('img'),title=dialog.querySelector('#dialog-title'),area=dialog.querySelector('.zoom-area');
 document.querySelectorAll('[data-image]').forEach(button=>button.addEventListener('click',()=>{
   opener=button;large.src=button.dataset.image;large.alt=button.dataset.caption;title.textContent=button.dataset.caption;area.classList.remove('zoomed');dialog.querySelector('[data-zoom]').textContent='اندازهٔ اصلی';dialog.showModal();
 }));
 dialog.querySelector('[data-close]').addEventListener('click',()=>dialog.close());
 dialog.querySelector('[data-zoom]').addEventListener('click',event=>{const zoomed=area.classList.toggle('zoomed');event.currentTarget.textContent=zoomed?'جا دادن در صفحه':'اندازهٔ اصلی';});
 dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
 dialog.addEventListener('close',()=>{if(opener)opener.focus();});
}
const sections=document.querySelectorAll('.report-section[id]');
if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){document.querySelectorAll('.toc a').forEach(a=>a.classList.toggle('active',a.hash==='#'+entry.target.id));}}),{rootMargin:'-15% 0px -65% 0px'});sections.forEach(s=>observer.observe(s));}
document.querySelectorAll('[data-print]').forEach(b=>b.addEventListener('click',()=>window.print()));
const gc=window.LAB_GISCUS||{},container=document.querySelector('.giscus');
if(container&&gc.repo&&gc.repoId&&gc.category&&gc.categoryId){
 const script=document.createElement('script');script.src='https://giscus.app/client.js';script.async=true;script.crossOrigin='anonymous';
 const attributes={'repo':gc.repo,'repo-id':gc.repoId,'category':gc.category,'category-id':gc.categoryId,'mapping':'specific','term':document.body.dataset.commentTerm||'lab00-post','strict':'1','reactions-enabled':'1','emit-metadata':'0','input-position':'top','theme':'light','lang':'fa','loading':'lazy'};
 Object.entries(attributes).forEach(([key,value])=>script.setAttribute('data-'+key,value));
 const status=document.getElementById('comment-status');status.textContent='در حال بارگذاری داوری از GitHub Discussions…';
 script.onerror=()=>{status.textContent='بارگذاری کامنت‌ها انجام نشد. دسترسی اینترنت و تنظیمات giscus را بررسی کنید.';};
 window.addEventListener('message',event=>{if(event.origin==='https://giscus.app'&&event.data&&event.data.giscus){status.hidden=true;}});
 container.append(script);
}
