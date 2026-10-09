import {chromium} from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const summary=JSON.parse(await readFile('data/summary.json','utf8'));
const expectedSpread=new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR'}).format(summary.periods.all.core.total_volume*0.003);
const url=process.env.TEST_URL||'http://127.0.0.1:8000';
await mkdir('test-results',{recursive:true});
const browser=await chromium.launch({headless:true});
const results=[];
async function inspectLayout(page,width) {
  const geometry=await page.evaluate(()=>{
    const rect=s=>document.querySelector(s).getBoundingClientRect();
    const main=rect('main'),style=getComputedStyle(document.querySelector('main'));
    const headerLeft=rect('.brand').left,headerRight=rect('#customize').right;
    const contentLeft=main.left+parseFloat(style.paddingLeft),contentRight=main.right-parseFloat(style.paddingRight);
    const smallTargets=[...document.querySelectorAll('button,a,input,select,summary,[tabindex="0"]')].filter(el=>{
      const r=el.getBoundingClientRect();
      return el.getClientRects().length && getComputedStyle(el).visibility!=='hidden' && (r.width<43.99 || r.height<43.99);
    }).map(el=>({tag:el.tagName,text:el.textContent.trim().slice(0,60),width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height}));
    const labels=[...document.querySelectorAll('.waterfall-value,.waterfall-label')].map(el=>el.getBoundingClientRect());
    const overlap=labels.some((a,i)=>labels.slice(i+1).some(b=>a.left<b.right && a.right>b.left && a.top<b.bottom && a.bottom>b.top));
    return {headerLeft,headerRight,contentLeft,contentRight,smallTargets,overlap,overflow:document.documentElement.scrollWidth>innerWidth};
  });
  assert.ok(Math.abs(geometry.headerLeft-geometry.contentLeft)<=1,'Header left at '+width);
  assert.ok(Math.abs(geometry.headerRight-geometry.contentRight)<=1,'Header right at '+width);
  assert.deepEqual(geometry.smallTargets,[],'Touch targets at '+width);
  assert.equal(geometry.overlap,false,'Waterfall label overlap at '+width);
  assert.equal(geometry.overflow,false,'Horizontal overflow at '+width);
  return geometry;
}
async function inspectWaterfall(page,key,width,theme) {
  const p=summary.periods[key],c=p.core;
  const values=[c.gross,-p.costs.realized_fees,c.dividends+c.interest,c.tax_signed,c.result];
  const signed=v=>(v>.005?'+':'')+new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR'}).format(Math.abs(v)<.005?0:v);
  assert.deepEqual(await page.locator('.waterfall-value').allTextContents(),values.map(signed));
  assert.equal(await page.locator('.waterfall-chart[role="img"]').count(),1);
  assert.match(await page.locator('.waterfall-chart').getAttribute('aria-label'),/Handelsergebnis brutto.*Gebühren.*Steuern/);
  assert.equal(await page.locator('.waterfall details summary').textContent(),'Daten als Tabelle');
  await page.locator('.waterfall summary').click();
  assert.equal(await page.locator('.waterfall tbody tr').count(),5);
  assert.deepEqual(await page.locator('.waterfall tbody tr td:first-of-type').allTextContents(),values.map(signed));
  await page.locator('.waterfall summary').click();
  const taxes=page.locator('.module-kernzahlen .accounting-line span').last().locator('strong');
  assert.equal(await taxes.textContent(),new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR'}).format(Math.abs(c.tax_signed)<.005?0:c.tax_signed));
  assert.equal(await taxes.getAttribute('class'),c.tax_signed<-.005?'negative':c.tax_signed>.005?'positive':'');
  const pause=page.locator('.module-aktivitaet_heatmap .metric').nth(1).locator('.numeric');
  assert.equal(await pause.textContent(),String(p.activity.longest_pause.full_days));
  assert.match(await page.locator('.module-aktivitaet_heatmap').textContent(),/Gewertet ab 01.05.2025 \(Beginn des regelmäßigen Handelns\)/);
  const motion=await page.locator('.waterfall-bar').evaluateAll(els=>els.map(el=>({duration:getComputedStyle(el).transitionDuration,opacity:getComputedStyle(el).opacity})));
  assert.ok(motion.every(s=>s.duration==='0s' && s.opacity==='1'),'Reduced motion');
  const geometry=await inspectLayout(page,width);
  if([390,1440].includes(width)){
    await page.locator('.waterfall').screenshot({path:`test-results/waterfall-${key}-${width}-${theme}.png`});
    await page.locator('.module-kernzahlen').screenshot({path:`test-results/core-${key}-${width}-${theme}.png`});
    await page.locator('.module-aktivitaet_heatmap').screenshot({path:`test-results/activity-${key}-${width}-${theme}.png`});
  }
  return {period:key,taxes:await taxes.textContent(),waterfall:values.map(signed),pause:p.activity.longest_pause,geometry};
}
try {
  for(const [width,height] of [[360,640],[390,844],[768,1024],[1440,900],[1920,1080]]) {
    const context=await browser.newContext({viewport:{width,height},reducedMotion:'reduce',colorScheme:'light'});
    const page=await context.newPage();
    const errors=[],external=[];
    page.on('pageerror',error=>{errors.push(error.message);console.error('PAGEERROR',error.message);});
    page.on('console',message=>{if(message.type()==='error'){errors.push(message.text());console.error('BROWSER',message.text());}});
    page.on('request',req=>{if(!req.url().startsWith(url))external.push(req.url());});
    await page.goto(url);await page.locator('.module').last().waitFor();
    assert.equal(await page.locator('.module').count(),13);
    assert.equal(await page.locator('#status.error').count(),0,await page.locator('#status').textContent());
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'Horizontal overflow at '+width);
    const accessibility=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
    await writeFile(`test-results/axe-${width}.json`,JSON.stringify(accessibility,null,2));
    await page.screenshot({path:`test-results/${width}x${height}-light.png`,fullPage:true});
    await page.getByRole('button',{name:/Farbmodus wechseln/}).click();
    assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
    const darkAccessibility=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
    await writeFile(`test-results/axe-${width}-dark.json`,JSON.stringify(darkAccessibility,null,2));
    await page.screenshot({path:`test-results/${width}x${height}-dark.png`,fullPage:true});
    const periodChecks=[];
    for(const theme of ['light','dark']){
      if(await page.locator('html').getAttribute('data-theme')!==theme)await page.getByRole('button',{name:/Farbmodus wechseln/}).click();
      for(const key of ['all','2025-04','2025-05','2025','2025-08','2026-10']){
        if(key==='all')await page.getByRole('button',{name:'Gesamt',exact:true}).click();
        else {await page.getByRole('button',{name:key.length===4?'Jahr':'Monat',exact:true}).click();await page.locator('#period').selectOption(key);}
        periodChecks.push({theme,...await inspectWaterfall(page,key,width,theme)});
      }
    }
    await page.getByRole('button',{name:'Monat',exact:true}).click();
    await page.getByRole('combobox',{name:'Zeitraum',exact:true}).selectOption('2026-03');
    assert.match(page.url(),/period=2026-03/);
    await page.getByRole('button',{name:'Vorheriger Zeitraum'}).click();
    assert.match(page.url(),/period=2026-02/);
    await page.getByRole('button',{name:'Jahr',exact:true}).click();
    assert.match(page.url(),/period=2026$/);
    await page.getByRole('button',{name:/Ansicht anpassen/}).click();
    await page.getByRole('button',{name:'Nur Kernzahlen',exact:true}).click();
    assert.equal(await page.locator('.module').count(),1);
    await page.getByRole('button',{name:'Nur Trade Republic',exact:true}).click();
    assert.equal(await page.locator('.module-trade_republic').count(),1);
    await page.getByRole('button',{name:'Alles',exact:true}).click();
    assert.equal(await page.locator('.module').count(),13);
    const ids=await page.locator('#feature-switches input').evaluateAll(els=>els.map(el=>el.value));
    for(const id of ids){await page.locator(`#feature-switches input[value="${id}"]`).uncheck();assert.equal(await page.locator(`.module-${id}`).count(),0);await page.locator(`#feature-switches input[value="${id}"]`).check();assert.equal(await page.locator(`.module-${id}`).count(),1);}
    await page.getByRole('button',{name:'Einstellungen schließen'}).click();
    await page.getByRole('button',{name:'Gesamt',exact:true}).click();
    await page.locator('#spread').focus();await page.locator('#spread').press('End');
    assert.match(await page.locator('#spread-label').textContent(),/0,3/);
    assert.equal(await page.locator('#spread-amount').textContent(),expectedSpread);
    await page.goto(url+'/#modules=core,fees&period=2026-03');
    await page.locator('.module-kosten').waitFor();assert.equal(await page.locator('.module').count(),2);
    await page.reload();await page.locator('.module-kosten').waitFor();assert.equal(await page.locator('.module').count(),2);
    assert.equal(external.length,0,'Unexpected external requests');assert.deepEqual(errors,[]);
    results.push({width,height,overflow:false,modules:13,errors,external,periodChecks,axeViolations:accessibility.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),darkAxeViolations:darkAccessibility.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))});
    await context.close();
  }
  const blocked=await browser.newPage({viewport:{width:390,height:844}});
  await blocked.addInitScript(()=>{Storage.prototype.getItem=function(){throw new Error('blocked');};Storage.prototype.setItem=function(){throw new Error('blocked');};});
  await blocked.goto(url);await blocked.locator('.module').last().waitFor();assert.equal(await blocked.locator('.module').count(),13);await blocked.close();
  const missing=await browser.newPage();await missing.route('**/data/summary.json',r=>r.fulfill({status:404,body:'missing'}));await missing.goto(url);await missing.locator('#status.error').waitFor();assert.match(await missing.locator('#status').textContent(),/konnte nicht geladen/);await missing.close();
  const normal=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'no-preference'});await normal.goto(url);await normal.locator('.module').last().waitFor();await normal.locator('.waterfall').scrollIntoViewIfNeeded();
  await normal.waitForFunction(()=>document.querySelector('.module-kernzahlen').classList.contains('revealed'));
  assert.deepEqual(await normal.locator('.waterfall-bar').evaluateAll(els=>els.map(el=>getComputedStyle(el).transitionDelay)),['0s','0.09s','0.18s','0.27s','0.36s']);
  await normal.waitForFunction(()=>[...document.querySelectorAll('.waterfall-bar')].every(el=>getComputedStyle(el).opacity==='1'));
  await normal.screenshot({path:'test-results/390x844-animated.png'});await normal.close();
  const refund=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
  await refund.route('**/data/summary.json',r=>{const data=structuredClone(summary);const c=data.periods['2025-08'].core;c.result+=25-c.tax_signed;c.tax_signed=25;r.fulfill({json:data});});
  await refund.goto(url+'/#period=2025-08');await refund.locator('.waterfall').waitFor();
  assert.equal(await refund.locator('.module-kernzahlen .accounting-line span').last().locator('strong.positive').textContent(),'25,00 €');
  assert.equal(await refund.locator('.waterfall-value').nth(3).textContent(),'+25,00 €');
  assert.equal(await refund.locator('.waterfall-bar').nth(3).getAttribute('class'),'waterfall-bar positive ');
  await refund.close();
  await writeFile('test-results/browser-results.json',JSON.stringify(results,null,2));
  assert.equal(results.flatMap(r=>[...r.axeViolations,...r.darkAxeViolations]).length,0,'Accessibility violations; inspect saved reports.');
  console.log(JSON.stringify(results,null,2));
} finally {await writeFile('test-results/browser-results.json',JSON.stringify(results,null,2));await browser.close();}
