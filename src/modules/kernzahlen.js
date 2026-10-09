import {e,eur,num,pct,date,month,sign,hours,value,metric,table,bars,node} from '../ui/format.js';
import {plot} from '../ui/charts.js';
export const id='kernzahlen';
export const title='Kernzahlen';
export function render(data,period) {
const p=data.periods[period];

const c=p.core;
return node(`<div class="hero-result"><div class="eyebrow">Das Ergebnis unter dem Strich</div><div class="hero-number ${sign(c.result)}">${value(c.result)}</div><p>Realisierte Ergebnisse, Dividenden und Zinsen, nach Gebühren und ausgewiesenen Steuern.</p><span class="pill">${p.capital.positions.length?'Offene Positionen: '+(p.capital.valuation==='not_valued'?'nicht bewertet':p.capital.valuation==='partial'?'teilweise bewertet':'mit Nutzerkursen bewertet'):'Keine offenen Positionen am Periodenende'}</span></div><div class="metrics core-grid">${metric('Handelsvolumen',c.total_volume,'eur','Käufe + Verkäufe')}${metric('Gezahlte Gebühren',p.costs.fees)}${metric('Handelszeilen / Orders',c.orders,'num','Ausführungszeilen im Export')}${metric('Trefferquote',p.quality.hit_rate,'pct','Zuordenbare Verkäufe')}</div><div class="accounting-line"><span>Brutto <strong class="${sign(c.gross)}">${eur(c.gross)}</strong></span><span>Nach realisierten Gebühren <strong class="${sign(c.net)}">${eur(c.net)}</strong></span><span>Dividenden + Zinsen <strong>${eur(c.dividends+c.interest)}</strong></span><span>Steuern netto <strong>${eur(c.taxes_net)}</strong></span></div><p class="small">Die Ergebnisrechnung enthält ${eur(p.costs.realized_fees)} realisierte Gebühren. Noch offene Kaufgebühren bleiben im Einstand. Alle Kennzahlen beziehen sich auf den gewählten Zeitraum.</p>`);

}
