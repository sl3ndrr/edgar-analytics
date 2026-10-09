import {e,eur,num,pct,date,month,sign,hours,value,metric,table,bars,node} from '../ui/format.js';
import {plot} from '../ui/charts.js';
export const id='trefferquote';
export const title='Qualität der Ergebnisse';
export function render(data,period) {
const p=data.periods[period];

const q=p.quality;
return node(`<div class="metrics">${metric('Trefferquote',q.hit_rate,'pct')}${metric('Ø Gewinn',q.average_win,'eur','Je positivem Verkauf',true)}${metric('Ø Verlust',q.average_loss,'eur','Je negativem Verkauf',true)}${metric('Gewinn / Verlust-Verhältnis',q.win_loss_ratio,'num')}${metric('Erwartungswert je Verkauf',q.expected_value,'eur','Historischer Mittelwert',true)}${metric('Profit-Faktor',q.profit_factor,'num','Summe Gewinne ÷ Summe Verluste')}${metric('Gewinn je Handelstag',q.net_per_trading_day,'eur','Nur realisiertes Handelsergebnis',true)}${metric('Profitable Handelstage',q.profitable_days_percent,'pct')}</div>${bars([{label:'Gewinn-Verkäufe',value:q.wins},{label:'Verlust-Verkäufe',value:q.losses},{label:'Nahe null (±0,005 €)',value:q.breakeven}],'num')}<div class="accounting-line"><span>Längste Gewinnserie <strong>${num(q.winning_streak)}</strong></span><span>Längste Verlustserie <strong>${num(q.losing_streak)}</strong></span><span>Zuordenbare Verkäufe <strong>${num(q.closed_trades)}</strong></span></div>`);

}
