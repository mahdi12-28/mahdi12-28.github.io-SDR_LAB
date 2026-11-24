(() => {
  const rows=window.LAB03_IQ_RESULTS||[];
  if(!rows.length)return;
  const container=document.querySelector('#iq-audio');
  for(const r of rows){
    const card=document.createElement('div');card.className='iq-card';
    const h=document.createElement('h3');h.textContent=r.title_fa||r.id;card.append(h);
    const audio=document.createElement('audio');audio.controls=true;audio.preload='none';audio.src=r.audio_path;card.append(audio);
    const img=document.createElement('img');img.src=r.psd_path;img.alt='طیف ضبط '+r.id;img.loading='lazy';card.append(img);container.append(card);
  }
})();
