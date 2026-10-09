import {compact} from './format.js';
export function animate(root){
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  root.querySelectorAll('[data-count]').forEach(el=>el.textContent=compact(+el.dataset.count,el.dataset.format));
  if(reduced || !('IntersectionObserver' in window))return ()=>{};
  root.classList.add('animate');
  const frames=new Set();
  const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(!entry.isIntersecting)return;const el=entry.target;observer.unobserve(el);el.classList.add('revealed');el.querySelectorAll('[data-count]').forEach(span=>{const target=+span.dataset.count;const start=performance.now();let id;function frame(now){frames.delete(id);const t=Math.min(1,(now-start)/650);span.textContent=compact(target*(1-Math.pow(1-t,3)),span.dataset.format);if(t<1){id=requestAnimationFrame(frame);frames.add(id);}}id=requestAnimationFrame(frame);frames.add(id);});}),{threshold:.08});
  root.querySelectorAll('.module').forEach(el=>observer.observe(el));
  return ()=>{observer.disconnect();frames.forEach(cancelAnimationFrame);};
}
