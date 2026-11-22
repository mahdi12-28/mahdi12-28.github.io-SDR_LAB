(() => {
  const rows=window.LAB03_IQ_RESULTS||[];
  if(!rows.length)return;
  const container=document.querySelector('#iq-audio');
  const tableRows=document.querySelectorAll('#iq-results-table tbody tr');
  const ids=['station_90mhz','gain40','gain27','gain20','tone1k_dev5k','tone3k_dev5k'];
  for(const r of rows){
    const i=ids.indexOf(r.id);
    if(i>=0&&tableRows[i]){
      tableRows[i].children[1].textContent=(r.B99_hz/1000).toFixed(2)+' kHz';
      const c=tableRows[i].children[2];c.replaceChildren();
      const a=document.createElement('a');a.href=r.psd_path;a.textContent='نمودار';c.append(a);
    }
    const card=document.createElement('div');card.className='iq-card';
    const h=document.createElement('h3');h.textContent=r.id;h.dir='ltr';card.append(h);
    const audio=document.createElement('audio');audio.controls=true;audio.preload='none';audio.src=r.audio_path;card.append(audio);
    const img=document.createElement('img');img.src=r.psd_path;img.alt='طیف ضبط '+r.id;img.loading='lazy';card.append(img);container.append(card);
  }
})();
