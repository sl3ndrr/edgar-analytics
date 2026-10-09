import {e,eur,num,pct,date,month,sign,hours,value,metric,table,bars,node} from '../ui/format.js';
import {plot} from '../ui/charts.js';
export const id='equity_drawdown';
export const title='Ergebnis im Verlauf';
export function render(data,period) {
const p=data.periods[period];

return node(`<div class="metrics">${metric('Maximaler Drawdown',p.equity.max_drawdown)}<div class="metric"><div class="metric-label">Vom Hoch zum Tief</div><div class="metric-value compact-text">${date(p.equity.drawdown_start)}<br>→ ${date(p.equity.drawdown_end)}</div></div></div>${plot('Kumuliertes realisiertes Handelsergebnis nach Gebühren',p.equity.daily.map(d=>d.date),[{label:'Realisiertes Ergebnis',values:p.equity.daily.map(d=>d.net_cumulative),color:'result'}])}<p class="small">Die Kurve beginnt im gewählten Zeitraum bei null und enthält realisierte Handelsgewinne nach Gebühren. Sie bildet keinen Depotwert ab und enthält keine Dividenden, Zinsen oder Steuern. Drawdown in Euro; Prozent-Drawdown ist bei einer Ergebnislinie mit Startwert null nicht sinnvoll.</p>`);

}
