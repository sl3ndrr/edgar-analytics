import {e} from './format.js';

// Owns its DOM, scroll frame, dialog and listeners; call dispose before each render.
export function mountChapterNav(modules, {onNavigate}={}) {
  if(modules.length<2)return {dispose(){}};
  const nav=document.createElement('nav');
  nav.className='chapter-nav';nav.setAttribute('aria-label','Kapitel');
  const number=i=>String(i+1).padStart(2,'0');
  const items=kind=>`<ol class="chapter-${kind}">${modules.map((m,i)=>`<li><button type="button" data-chapter="${i}" aria-label="${number(i)} ${e(m.title)}" title="${e(m.title)}"><span class="chapter-dot" aria-hidden="true"></span><span class="chapter-label">${number(i)} ${e(m.title)}</span></button></li>`).join('')}</ol>`;
  nav.innerHTML=`${items('points')}<span class="chapter-counter" aria-hidden="true"></span><button type="button" class="chapter-trigger" aria-haspopup="dialog" aria-controls="chapter-sheet"><span class="chapter-rail" aria-hidden="true"><span class="chapter-fill"></span>${modules.map((_,i)=>`<span class="chapter-dot" style="top:${i/(modules.length-1)*100}%"></span>`).join('')}</span></button><span class="chapter-toast" aria-hidden="true"></span>`;
  const sheet=document.createElement('dialog');sheet.id='chapter-sheet';sheet.className='chapter-sheet';sheet.setAttribute('aria-labelledby','chapter-sheet-title');
  sheet.innerHTML=`<div class="sheet-head"><h2 id="chapter-sheet-title">Kapitel</h2><button type="button" class="icon-button" aria-label="Kapitelliste schließen">×</button></div><nav aria-label="Kapitelauswahl">${items('list')}</nav>`;
  document.body.append(nav,sheet);
  const trigger=nav.querySelector('.chapter-trigger'),toast=nav.querySelector('.chapter-toast');
  const buttons=[...nav.querySelectorAll('[data-chapter]'),...sheet.querySelectorAll('[data-chapter]')];
  let active=-1,frame=0,timer=0;
  function update(){
    frame=0;
    const line=innerHeight*.35;
    let next=0;
    modules.forEach((m,i)=>{if(m.element.getBoundingClientRect().top<=line)next=i;});
    if(scrollY+innerHeight>=document.documentElement.scrollHeight-2)next=modules.length-1;
    const main=document.querySelector('main');
    const edge=main.getBoundingClientRect().right-parseFloat(getComputedStyle(main).paddingRight);
    nav.querySelectorAll('.chapter-points button').forEach(b=>b.classList.toggle('label-fits',b.querySelector('.chapter-label').getBoundingClientRect().left>=edge));
    if(next===active)return;
    active=next;
    buttons.forEach(b=>{const i=+b.dataset.chapter;b.classList.toggle('passed',i<active);if(i===active)b.setAttribute('aria-current','location');else b.removeAttribute('aria-current');});
    [...nav.querySelectorAll('.chapter-rail>.chapter-dot')].forEach((dot,i)=>{dot.classList.toggle('passed',i<active);dot.classList.toggle('current',i===active);});
    nav.style.setProperty('--chapter-progress',String(active/(modules.length-1)));
    nav.querySelector('.chapter-counter').textContent=`${number(active)} / ${String(modules.length).padStart(2,'0')}`;
    const label=`${number(active)} ${modules[active].title}`;
    trigger.setAttribute('aria-label',`Kapitelliste öffnen; aktuell ${label}`);
    toast.textContent=label;toast.classList.add('visible');clearTimeout(timer);timer=setTimeout(()=>toast.classList.remove('visible'),1500);
  }
  function schedule(){if(!frame)frame=requestAnimationFrame(update);}
  function navigate(event){
    const button=event.target.closest('[data-chapter]');if(!button)return;
    const m=modules[+button.dataset.chapter];
    if(sheet.open)sheet.close();
    m.element.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
    // Make the destination reachable to keyboard and screen-reader users without changing the hash.
    const heading=m.element.querySelector('h2');heading.setAttribute('tabindex','-1');heading.focus({preventScroll:true});
    onNavigate?.(m);schedule();
  }
  function open(){sheet.showModal();sheet.querySelector('[aria-current]')?.focus();}
  function close(event){if(event.target.closest('.icon-button'))sheet.close();else if(event.target===sheet){const r=sheet.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)sheet.close();}}
  nav.addEventListener('click',navigate);sheet.addEventListener('click',navigate);sheet.addEventListener('click',close);trigger.addEventListener('click',open);
  addEventListener('scroll',schedule,{passive:true});addEventListener('resize',schedule);update();
  return {dispose(){removeEventListener('scroll',schedule);removeEventListener('resize',schedule);cancelAnimationFrame(frame);clearTimeout(timer);if(sheet.open)sheet.close();nav.remove();sheet.remove();}};
}
