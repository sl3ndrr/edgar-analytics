import {e,table,date,eur,num} from './format.js';
export function plot(label, dates, series, kind='line') {
  if(!dates.length) return '<p class="small">Keine Diagrammdaten in diesem Zeitraum.</p>';
  const spec = {label,dates,series,kind};
  return `<div class="plot-shell"><div class="plot" role="img" tabindex="0" aria-label="${e(label)}. Die vollständigen Werte stehen in der Tabelle darunter." data-plot="${e(JSON.stringify(spec))}"></div><output class="plot-tooltip" aria-live="off"></output></div><details class="chart-table"><summary>Daten als Tabelle</summary>${table(['Datum',...series.map(s=>s.label)], dates.map((d,i)=>[e(date(d)),...series.map(s=>s.format==='num'?num(s.values[i]):eur(s.values[i]))]),label)}</details>`;
}
export function mountPlots(root) {
  const disposers=[];
  root.querySelectorAll('[data-plot]').forEach(el=>{
    const spec=JSON.parse(el.dataset.plot);const tip=el.nextElementSibling;
    const styles=getComputedStyle(document.documentElement);const foreground=styles.getPropertyValue('--muted').trim();
    const xs=spec.dates.map(d=>Date.parse(d+'T12:00:00Z')/1000);
    const colors=[styles.getPropertyValue('--ink').trim(),styles.getPropertyValue('--muted').trim()];
    const series=[{},...spec.series.map((s,i)=>({label:s.label,stroke:s.color==='result'?styles.getPropertyValue(s.values.at(-1)>=0?'--green':'--red').trim():colors[i%2],width:2,fill:spec.kind==='bar'?colors[i%2]:undefined,points:{show:xs.length===1},paths:spec.kind==='bar'?uPlot.paths.bars({size:[.6,40]}):undefined}))];
    function report(u) {const i=u.cursor.idx;if(i!=null)tip.textContent=date(spec.dates[i])+' · '+spec.series.map(s=>s.label+': '+(s.format==='num'?num(s.values[i]):eur(s.values[i]))).join(' · ');}
    const u=new uPlot({width:Math.max(200,el.clientWidth),height:240,locale:'de-DE',tzDate:ts=>uPlot.tzDate(new Date(ts*1000),'Europe/Berlin'),series,legend:{show:false},axes:[{stroke:foreground,grid:{show:false},size:40,space:window.innerWidth<600?110:80},{stroke:foreground,grid:{stroke:styles.getPropertyValue('--line').trim(),width:1},size:62,values:(u,vals)=>vals.map(v=>new Intl.NumberFormat('de-DE',{notation:'compact',maximumFractionDigits:1}).format(v))}],cursor:{drag:{x:false,y:false}},hooks:{setCursor:[report]}},[xs,...spec.series.map(s=>s.values)],el);
    const ro=new ResizeObserver(()=>u.setSize({width:Math.max(200,el.clientWidth),height:240}));ro.observe(el);
    el.addEventListener('keydown',ev=>{if(ev.key==='ArrowRight'||ev.key==='ArrowLeft'){ev.preventDefault();const step=ev.key==='ArrowRight'?1:-1;const idx=Math.max(0,Math.min(xs.length-1,(u.cursor.idx??0)+step));u.setCursor({left:u.valToPos(xs[idx],'x'),top:120});}});
    el.addEventListener('pointerdown',ev=>{const rect=u.over.getBoundingClientRect();u.setCursor({left:ev.clientX-rect.left,top:ev.clientY-rect.top});});
    disposers.push(()=>{ro.disconnect();u.destroy();});
  });
  return ()=>disposers.forEach(f=>f());
}
