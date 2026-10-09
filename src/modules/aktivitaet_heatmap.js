import {e,eur,num,pct,date,month,sign,hours,value,metric,table,bars,node} from '../ui/format.js';
import {plot} from '../ui/charts.js';
export const id='aktivitaet_heatmap';
export const title='Wann gehandelt wurde';
export function render(data,period) {
const p=data.periods[period];

const h=p.activity.heatmap;const days=['Mo','Di','Mi','Do','Fr','Sa','So'];const max=Math.max(1,...h.flat());const twoMax=Math.max(1,...h.flatMap(row=>Array.from({length:12},(_,i)=>row[2*i]+row[2*i+1])));
const grid=(step,maximum)=>`<div class="heatmap heat-${step}" role="img" aria-label="Handelszeilen nach Wochentag und Uhrzeit, Europe/Berlin. Tabelle darunter."><span></span>${Array.from({length:24/step},(_,i)=>`<span class="heat-hour">${String(i*step).padStart(2,'0')}</span>`).join('')}${days.map((d,di)=>`<span class="heat-day">${d}</span>${Array.from({length:24/step},(_,i)=>{const n=h[di].slice(i*step,(i+1)*step).reduce((a,b)=>a+b,0);return `<span class="heat-cell" style="--intensity:${n/maximum};--delay:${(di*24/step+i)*3}ms" title="${d}, ${i*step}–${(i+1)*step} Uhr: ${num(n)} Handelszeilen"></span>`;}).join('')}`).join('')}</div>`;
return node(`<div class="metrics">${metric('Handelstage',p.activity.trading_days,'num')}${metric('Längste Pause',p.activity.longest_pause.full_days,'num','Volle Tage zwischen zwei Handelstagen')}</div><p class="small">Berliner Ortszeit. Mobil sind jeweils zwei Stunden zusammengefasst. Dunklere Felder bedeuten mehr Handelszeilen.</p>${grid(1,max)}${grid(2,twoMax)}<details><summary>Heatmap als Tabelle</summary>${table(['Tag',...Array.from({length:24},(_,i)=>i+' Uhr')],h.map((row,i)=>[days[i],...row.map(num)]),'Handelszeilen nach Berliner Uhrzeit')}</details><h3>Aktivste Tage</h3>${table(['Datum','Orders'],p.activity.active_days.map(d=>[date(d.date),num(d.orders)]))}${plot('Handelszeilen pro Tag',p.activity.daily.map(d=>d.date),[{label:'Orders',values:p.activity.daily.map(d=>d.orders),format:'num'}],'bar')}<p class="small">Längste Pause: ${date(p.activity.longest_pause.from)} bis ${date(p.activity.longest_pause.to)}. Pausen am Exportanfang und -ende werden nicht als beobachtete Handelspause gewertet.</p>`);

}
