import {e,eur,num,pct,date,month,sign,hours,value,metric,table,bars,node} from '../ui/format.js';
import {plot} from '../ui/charts.js';
export const id='haltedauer';
export const title='Wie lange Positionen gehalten wurden';
export function render(data,period,config={}) {
const p=data.periods[period];
const minimum=config.shortest_hold_min_proceeds??5;
const shortest=p.holding.shortest?.length?`<h3>Kürzeste Haltedauern</h3><p class="small">${minimum>0?`nur Verkäufe ab ${num(minimum)} €`:'Alle zugeordneten Verkäufe'}. Haltedauer nach Stückzahl gewichtet. Mehrere Ausführungen derselben Order können getrennte Zeilen sein.</p><ol class="ranking">${p.holding.shortest.map(t=>`<li><div><strong>${e(t.name)}</strong><span class="small">${e(t.isin)} · ${date(t.date)}</span></div><div class="rank-value">${hours(t.hours,true)}<span class="small ${sign(t.net)}">${eur(t.net)} · ${pct(t.net_percent)}</span></div></li>`).join('')}</ol>`:'';

return node(`<div class="metrics">${metric('Daytrade-Anteil',p.holding.daytrade_percent,'pct','Alle zugeordneten Lots am selben Berliner Tag gekauft')}<div class="metric"><div class="metric-label">Median</div><div class="metric-value">${hours(p.holding.median_hours)}</div></div><div class="metric"><div class="metric-label">Mittelwert</div><div class="metric-value">${hours(p.holding.mean_hours)}</div></div></div>${bars(Object.entries(p.holding.buckets).map(([label,value])=>({label,value})),'num')}${shortest}<p class="small">Bei Verkäufen aus mehreren Lots wird die Haltedauer nach Stückzahl gewichtet. Die Buckets sind disjunkt; 1–7 Tage schließt genau 7 Tage ein.</p>`);

}
