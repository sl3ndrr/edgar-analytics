import {e,eur,num,pct,date,month,sign,hours,value,metric,table,bars,node} from '../ui/format.js';
import {plot} from '../ui/charts.js';
export const id='kosten';
export const title='Was Gebühren verändert haben';
export function render(data,period) {
const p=data.periods[period];

return node(`<div class="metrics">${metric('Transaktionskosten',p.costs.fees)}${metric('Pro Handelszeile',p.costs.fees_per_order)}${metric('Basispunkte des Volumens',p.costs.basis_points,'num')}${metric('Erst durch Gebühren negativ',p.costs.fee_caused_losses,'num')}</div>${bars([{label:'Brutto-Handelsergebnis',value:p.core.gross},{label:'Nach realisierten Gebühren',value:p.core.net}])}<p class="small">Gebührenanteil am positiven Brutto-Gewinn: ${p.costs.fees_share_gross_percent==null?'nicht sinnvoll berechenbar, da kein positiver Brutto-Gewinn vorliegt.':pct(p.costs.fees_share_gross_percent)+'.'} Gezahlt und realisiert sind unterschiedliche Größen: offene Kaufgebühren sind noch nicht im realisierten Ergebnis enthalten.</p>`);

}
