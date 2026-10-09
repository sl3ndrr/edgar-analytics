import {e,eur,num,pct,date,month,sign,hours,value,metric,table,bars,node} from '../ui/format.js';
import {plot} from '../ui/charts.js';
export const id='trade_republic';
export const title='Edgar & Trade Republic';
export function render(data,period) {
const p=data.periods[period];

return node(`<p class="lead">Gebühren, die gezahlt wurden.<br>Ergebnis, das erzielt wurde.</p><div class="broker-comparison"><div><span class="eyebrow">Sichtbare Gebühren</span><strong>${value(p.broker.visible_fees)}</strong><span>Von Edgar gezahlt</span></div><div><span class="eyebrow">Ergebnis unter dem Strich</span><strong class="${sign(p.core.result)}">${value(p.core.result)}</strong><span>Nach Erträgen und Steuern</span></div></div><div class="metrics">${metric('Guthabenzinsen gezahlt',p.broker.interest_paid)}${metric('Gebühren minus Zinsen',p.broker.fees_less_interest,'eur','Sichtbare Differenz, kein Anbietergewinn')}</div><div class="scenario"><span class="pill">Annahme · kein beobachteter Wert</span><h3>Was ein angenommener Spread verändern würde</h3><p>Spreads, Rückvergütungen und tatsächlicher Zwischengewinn sind im Export nicht sichtbar. Gebühren können auch Fremdkosten enthalten. Der tatsächliche Gewinn von Trade Republic ist nicht ermittelbar.</p><label for="spread">Angenommener Spread: <output id="spread-label">0 %</output> vom Kauf- und Verkaufsvolumen</label><input id="spread" type="range" min="0" max="0.3" step="0.01" value="0" aria-describedby="spread-note"><div class="scenario-values"><div><span>Hypothetischer Spreadbetrag</span><strong id="spread-amount">${eur(0)}</strong></div><div><span>Gebühren + hypothetischer Betrag</span><strong id="spread-combined">${eur(p.broker.visible_fees)}</strong></div></div><p id="spread-note" class="small">Szenario von 0 % bis 0,3 %, Standard 0 %. Kein Nachweis zusätzlicher Einnahmen. Gebuchte Ergebnisse enthalten bereits die tatsächlichen Ausführungspreise; der Szenariobetrag wird davon nicht erneut abgezogen.</p></div>`);

}
