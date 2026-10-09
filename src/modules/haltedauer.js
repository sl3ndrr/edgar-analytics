import {e,eur,num,pct,date,month,sign,hours,value,metric,table,bars,node} from '../ui/format.js';
import {plot} from '../ui/charts.js';
export const id='haltedauer';
export const title='Wie lange Positionen gehalten wurden';
export function render(data,period) {
const p=data.periods[period];

return node(`<div class="metrics">${metric('Daytrade-Anteil',p.holding.daytrade_percent,'pct','Alle zugeordneten Lots am selben Berliner Tag gekauft')}<div class="metric"><div class="metric-label">Median</div><div class="metric-value">${hours(p.holding.median_hours)}</div></div><div class="metric"><div class="metric-label">Mittelwert</div><div class="metric-value">${hours(p.holding.mean_hours)}</div></div></div>${bars(Object.entries(p.holding.buckets).map(([label,value])=>({label,value})),'num')}<p class="small">Bei Verkäufen aus mehreren Lots wird die Haltedauer nach Stückzahl gewichtet. Die Buckets sind disjunkt; 1–7 Tage schließt genau 7 Tage ein.</p>`);

}
