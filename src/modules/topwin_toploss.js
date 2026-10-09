import {e,eur,num,pct,date,month,sign,hours,value,metric,table,bars,node} from '../ui/format.js';
import {plot} from '../ui/charts.js';
export const id='topwin_toploss';
export const title='Beste und schwächste Ergebnisse';
export function render(data,period) {
const p=data.periods[period];

function ranking(rows,head){return `<div><h3>${head}</h3>${rows.length?`<ol class="ranking">${rows.map(t=>`<li><div><strong>${e(t.name)}</strong><span class="small">${t.date?date(t.date)+' · ':''}${e(t.isin)}${t.partial?' · teilweise zugeordnet':''}</span></div><div class="rank-value ${sign(t.net)}">${eur(t.net)}<span class="small">${pct(t.net_percent)}</span></div></li>`).join('')}</ol>`:'<p class="small">Keine passenden Ergebnisse.</p>'}</div>`;}
return node(`<p class="small">Nach Gebühren. Je Verkaufszeile und je Instrument; Prozentwerte beziehen sich auf die zugeordneten Einstandskosten einschließlich Kaufgebühren.</p><details open><summary>Verkäufe nach Euro-Ergebnis</summary><div class="two-col">${ranking(p.top.wins,'Top 5 Gewinne')}${ranking(p.top.losses,'Top 5 Verluste')}</div></details><details><summary>Instrumente nach Euro-Ergebnis</summary><div class="two-col">${ranking(p.top.titles_wins,'Top 5 Gewinne je Instrument')}${ranking(p.top.titles_losses,'Top 5 Verluste je Instrument')}</div></details><details><summary>Verkäufe nach Prozent-Ergebnis</summary><div class="two-col">${ranking(p.top.wins_percent,'Top 5 in %')}${ranking(p.top.losses_percent,'Schwächste 5 in %')}</div></details><details><summary>Instrumente nach Prozent-Ergebnis</summary><div class="two-col">${ranking(p.top.titles_wins_percent,'Top 5 in %')}${ranking(p.top.titles_losses_percent,'Schwächste 5 in %')}</div></details>`);

}
