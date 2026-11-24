(() => {
  const rows=window.LAB03_IQ_RESULTS||[];
  if(!rows.length)return;
  const container=document.querySelector('#iq-audio');
  for(const r of rows){
    const card=document.createElement('div');card.className='iq-card';
    const h=document.createElement('h3');const title=(r.title_fa||r.id).replace(/[۰-۹]/g, digit => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(digit)));
    for(const part of title.split(/(\d+(?:[.:]\d+)*)/)){
      if(/^\d/.test(part)){
        const number=document.createElement('bdi');number.className='iq-number';number.dir='ltr';number.textContent=part;h.append(number);
      }else h.append(document.createTextNode(part));
    }
    card.append(h);
    const audio=document.createElement('audio');audio.controls=true;audio.preload='none';audio.src=r.audio_path;card.append(audio);
    const img=document.createElement('img');img.src=r.psd_path;img.alt='طیف ضبط '+r.id;img.loading='lazy';card.append(img);container.append(card);
  }
})();
