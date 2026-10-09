import fs from 'node:fs';
const r=JSON.parse(fs.readFileSync('test-results/lighthouse.report.json'));
const results=Object.fromEntries(['performance','accessibility','best-practices'].map(k=>[k,Math.round(r.categories[k].score*100)]));
fs.writeFileSync('test-results/lighthouse-scores.json',JSON.stringify(results,null,2));console.log(results);
if(Object.values(results).some(v=>v<90))process.exitCode=1;
