import {e,eur,sign,table} from './format.js';

const signed = v => (v > .005 ? '+' : '') + eur(v);
export function waterfall(p) {
  const c=p.core;
  const steps=[
    {label:'Handelsergebnis brutto',value:c.gross},
    {label:'Gebühren',value:-p.costs.realized_fees},
    {label:'Dividenden + Zinsen',value:c.dividends+c.interest},
    {label:'Steuern',value:c.tax_signed},
    {label:'Ergebnis unter dem Strich',value:c.result,total:true}
  ];
  let running=0;
  steps.forEach(s=>{s.from=s.total?0:running;s.to=s.total?s.value:running+s.value;running=s.to;});
  const min=Math.min(0,...steps.flatMap(s=>[s.from,s.to]));
  const max=Math.max(0,...steps.flatMap(s=>[s.from,s.to]));
  const range=max-min || 1;
  const x=v=>8+(v-min)/range*84;
  const y=v=>8+(max-v)/range*84;
  const description='Wasserfalldiagramm: '+steps.map(s=>s.label+' '+signed(s.value)).join(', ')+'.';
  return `<div class="waterfall"><h3>Vom Handelsergebnis zum Ergebnis</h3><p class="small">Wie sich das Ergebnis zusammensetzt. Gebühren offener Positionen sind noch nicht enthalten.</p><div class="waterfall-chart" role="img" aria-label="${e(description)}">${steps.map((s,i)=>`<div class="waterfall-step" style="--delay:${i*90}ms;--top:${Math.min(y(s.from),y(s.to))}%;--left:${Math.min(x(s.from),x(s.to))}%;--length:${Math.abs(s.value)/range*84}%;--end-y:${y(s.to)}%;--end-x:${x(s.to)}%;--zero-y:${y(0)}%;--zero-x:${x(0)}%"><strong class="waterfall-value ${sign(s.value)}">${e(signed(s.value))}</strong><div class="waterfall-track" aria-hidden="true"><span class="waterfall-zero"></span>${i<steps.length-1?'<span class="waterfall-connector"></span>':''}<span class="waterfall-bar ${s.total?'waterfall-total':sign(s.value)} ${Math.abs(s.value)<.005?'waterfall-null':''}"></span></div><span class="waterfall-label">${e(s.label)}</span></div>`).join('')}</div><details><summary>Daten als Tabelle</summary>${table(['Schritt','Betrag','Zwischenstand'],steps.map(s=>[e(s.label),e(signed(s.value)),e(signed(s.to))]),'Vom Handelsergebnis zum Ergebnis')}</details></div>`;
}
