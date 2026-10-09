import {e,eur,num,pct,date,month,sign,hours,value,metric,table,bars,node} from '../ui/format.js';
import {plot} from '../ui/charts.js';
export const id='fazit';
export const title='Was die Zahlen zeigen';
export function render(data,period) {
const p=data.periods[period];

return node(`<div class="conclusions">${p.conclusions.map((text,i)=>`<div class="conclusion"><span class="conclusion-index">0${i+1}</span><p>${e(text)}</p></div>`).join('')}</div><p class="small">Automatisch aus den berechneten Kennzahlen formuliert. Eine Aussage über die Zahlen, keine Bewertung der Person.</p>`);

}
