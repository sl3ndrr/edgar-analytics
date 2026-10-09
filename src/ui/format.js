const nf = new Intl.NumberFormat('de-DE', {maximumFractionDigits: 2});
const ef = new Intl.NumberFormat('de-DE', {style:'currency', currency:'EUR'});
const cf = new Intl.NumberFormat('de-DE', {notation:'compact',maximumFractionDigits:1,style:'currency',currency:'EUR'});
const df = new Intl.DateTimeFormat('de-DE',{day:'2-digit',month:'2-digit',year:'numeric'});
const mf = new Intl.DateTimeFormat('de-DE',{month:'long',year:'numeric'});
export const e = v => String(v ?? '').replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]));
export const eur = v => v == null ? 'Nicht ermittelbar' : ef.format(Math.abs(v)<0.005?0:v);
export const num = v => v == null ? '—' : nf.format(v);
export const pct = v => v == null ? '—' : num(v)+' %';
export const date = v => v ? df.format(new Date(v+'T12:00:00')) : '—';
export const month = v => mf.format(new Date(v+'-01T12:00:00'));
export const sign = v => v > .005 ? 'positive' : v < -.005 ? 'negative' : '';
export const hours = v => v == null ? '—' : v < 24 ? num(v)+' h' : num(v/24)+' Tage';
export function value(v,format='eur',cls='') {const text=format==='eur'?eur(v):format==='pct'?pct(v):num(v);return `<span class="numeric ${cls}" ${v==null?'':`data-count="${v}" data-format="${format}"`} title="${e(text)}">${e(text)}</span>`;}
export function metric(label,v,format='eur',note='',signed=false){return `<div class="metric"><div class="metric-label">${e(label)}</div><div class="metric-value">${value(v,format,signed?sign(v):'')}</div>${note?`<p class="small">${e(note)}</p>`:''}</div>`;}
export function table(headers,rows,caption=''){return `<div class="table-wrap"><table>${caption?`<caption>${e(caption)}</caption>`:''}<thead><tr>${headers.map(h=>`<th scope="col">${e(h)}</th>`).join('')}</tr></thead><tbody>${rows.length?rows.map(row=>`<tr>${row.map((v,i)=>`<${i?'td':'th scope="row"'}>${v}</${i?'td':'th'}>`).join('')}</tr>`).join(''):`<tr><td colspan="${headers.length}">Keine Daten in diesem Zeitraum.</td></tr>`}</tbody></table></div>`;}
export function bars(rows,format='eur') {const max=Math.max(1,...rows.map(r=>Math.abs(r.value)));return `<div class="bars">${rows.map(r=>`<div class="bar-row"><div class="bar-label">${e(r.label)}</div><div class="bar-track"><div class="bar-fill ${sign(r.value)}" style="--size:${Math.abs(r.value)/max};" aria-hidden="true"></div></div><div class="bar-value ${sign(r.value)}">${format==='eur'?eur(r.value):num(r.value)}</div></div>`).join('')}</div>`;}
export function node(html){const div=document.createElement('div');div.innerHTML=html;return div;}
export function compact(v, format){return format==='eur' && window.innerWidth<600 && Math.abs(v)>=100000 ? cf.format(v) : format==='eur'?eur(v):format==='pct'?pct(v):num(v);}
