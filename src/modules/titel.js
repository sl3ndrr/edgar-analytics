import {e,eur,num,pct,date,month,sign,hours,value,metric,table,bars,node} from '../ui/format.js';
import {plot} from '../ui/charts.js';
export const id='titel';
export const title='Instrumente & Konzentration';
export function render(data,period) {
const p=data.periods[period];

return node(`<div class="metrics">${metric('Gehandelte Instrumente',p.titles.length,'num')}${metric('Volumenanteil der Top 10',p.concentration_top10_percent,'pct')}</div><h3>Meistgehandelte Instrumente</h3>${bars([...p.titles].sort((a,b)=>b.orders-a.orders).slice(0,10).map(s=>({label:s.name,value:s.orders})),'num')}<h3>Aufteilung nach Anlageklasse</h3>${table(['Anlageklasse','Volumen','Orders','Realisiert netto'],Object.entries(p.classes).map(([k,v])=>[e(k),eur(v.volume),num(v.orders),`<span class="${sign(v.net)}">${eur(v.net)}</span>`]))}<details><summary>Alle Instrumente: Volumen und Gewinn / Verlust</summary>${table(['Instrument / ISIN','Volumen','Orders','Netto','Netto %'],p.titles.map(t=>[`${e(t.name)}<span class="small block">${e(t.isin)}</span>`,eur(t.volume),num(t.orders),`<span class="${sign(t.net)}">${eur(t.net)}</span>`,pct(t.net_percent)]))}</details><p class="small">Prozentwerte je Instrument: realisiertes Netto-Ergebnis ÷ zugeordneter Einstand inkl. Kaufgebühren; bei mehrfach gehandeltem Kapital keine Depotrendite.</p>`);

}
