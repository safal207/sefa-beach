import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';

const root=new URL('../',import.meta.url);
const files={'/':'index.html','/revenue-dashboard-local.html':'revenue-dashboard-local.html','/sales-context-template.csv':'sales-context-template.csv'};
const server=createServer(async(req,res)=>{
  const path=files[new URL(req.url,'http://localhost').pathname];
  if(!path){res.writeHead(404);res.end();return}
  try{res.setHeader('Content-Type',path.endsWith('.csv')?'text/csv; charset=utf-8':'text/html; charset=utf-8');res.end(await readFile(fileURLToPath(new URL(path,root))))}
  catch{res.writeHead(500);res.end()}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true});
const check=async(name,fn)=>{await fn();console.log('PASS '+name)};
async function session(width){
  const context=await browser.newContext({viewport:{width,height:850},locale:'en-US',timezoneId:'Europe/Istanbul',reducedMotion:'reduce'});
  await context.route('**/*',route=>route.request().url().startsWith(base+'/')?route.continue():route.abort());
  const page=await context.newPage(),errors=[];
  page.on('pageerror',err=>errors.push(String(err)));
  return {context,page,errors};
}
const cardCount=p=>p.locator('#menuContent .menu-card').count();
const waitCards=(p,n)=>p.waitForFunction(n=>document.querySelectorAll('#menuContent .menu-card').length===n,n);
const read=(p,id)=>p.locator(id).textContent();
try{
 for(const width of [320,390,1440]){
  const {context,page:p,errors}=await session(width);
  try{
   await p.goto(base+'/');
   await check(width+' initial render',async()=>{await waitCards(p,12);assert.equal(await cardCount(p),12);assert.equal(await p.locator('html').getAttribute('lang'),'en')});
   await check(width+' pagination and reset',async()=>{await p.locator('#loadMore').click();await waitCards(p,24);await p.locator('[data-quick="seafood"]').click();await waitCards(p,6);assert.equal(await cardCount(p),6)});
   await check(width+' item budget excludes expensive and unpriced items',async()=>{await p.locator('#budgetChoice').selectOption('500');await waitCards(p,0);await p.locator('#budgetChoice').selectOption('0');await waitCards(p,6);assert.equal(await p.locator('[data-add="79"]').isDisabled(),true)});
   await check(width+' saved selection, pairings and repricing',async()=>{
     await p.locator('[data-add="74"]').click();
     await p.locator('#openCart').click();
     assert.match(await read(p,'#footerTotal'),/650/);
     assert.ok(await p.locator('[data-upsell="95"]').count());
     await p.locator('[data-upsell="95"]').click();
     assert.equal(await p.locator('[data-upsell="95"]').count(),0);
     await p.locator('#clubSave').click();
     await p.keyboard.press('Escape');
     await p.reload();await p.locator('#clubRestore').waitFor({state:'visible'});
     assert.equal(await p.locator('#clubItems li').count(),2);
     p.once('dialog',d=>d.accept());await p.locator('#clubRestore').click();
     assert.match(await read(p,'#cartTotal'),/750/);
     p.once('dialog',d=>d.accept());await p.locator('#clubClear').click();assert.equal(await p.locator('#clubItems li').count(),0);
   });
   await check(width+' favorites and localization',async()=>{
     await p.locator('[data-quick="seafood"]').click();
     await p.locator('[data-fav="74"]').click();await p.locator('#clubFavorites').click();await waitCards(p,1);
     assert.equal(await p.locator('#menuContent [data-id="74"]').count(),1);
     await p.locator('#langSwitch').click();assert.equal(await p.locator('html').getAttribute('lang'),'ru');
     await p.locator('#langSwitch').click();assert.equal(await p.locator('html').getAttribute('lang'),'tr');
   });
   await check(width+' viewport and runtime integrity',async()=>{assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.deepEqual(errors,[])});
  }finally{await context.close()}
 }
 const {context,page:p,errors}=await session(390);
 try{
  await p.goto(base+'/revenue-dashboard-local.html');
  const header='order_id,item_id,qty,paid_unit_price_try,unit_food_cost_try,unit_packaging_cost_try,discount_try,payment_fee_try,refund_try,service_date,service_hour,service_zone';
  const fixture=(month,price)=>header+'\n'+Array.from({length:12},(_,i)=>['o'+i,i%4+1,1,price,20,0,0,0,0,month+'-15',18,'terrace'].join(',')).join('\n');
  const upload=(id,name,text,type='text/csv')=>p.locator(id).setInputFiles({name,mimeType:type,buffer:Buffer.from(text)});
  await check('owner: empty dashboard is not a result',async()=>{assert.equal(await p.locator('#journal-add').isDisabled(),true);assert.equal((await read(p,'#orders')).trim(),'—')});
  await check('owner: valid context and baseline',async()=>{
   await upload('#csv','before.csv',fixture('2026-09',100));
   await p.waitForFunction(()=>document.querySelector('#orders').textContent==='12');
   assert.equal(await p.locator('#journal-context option').count(),2);
   await p.locator('#journal-context').selectOption('0');
   await p.locator('#journal-hypothesis').fill('Synthetic receipt comparison');
   await p.locator('#journal-action').fill('Move one menu card');
   await p.locator('#journal-add').click();
   await p.waitForFunction(()=>document.querySelectorAll('#trace-items tr').length===1);
  });
  await check('owner: action and comparable observation',async()=>{
   await p.locator('#journal-entries input[type=date]').fill('2026-10-12');
   await p.locator('#journal-entries button').click();
   await p.waitForFunction(()=>document.querySelectorAll('#trace-items tr').length===2);
   await upload('#csv','after.csv',fixture('2026-11',120));
   await p.waitForFunction(()=>document.querySelector('#journal-entries select')?.options.length===2);
   await p.locator('#journal-entries select').selectOption('0');
   await p.locator('#journal-entries input[type=checkbox]').check();
   await p.locator('#journal-entries button').click();
   await p.waitForFunction(()=>document.querySelectorAll('#trace-items tr').length===3);
  });
  let saved;
  await check('owner: replay after reload and rejected import',async()=>{
   saved=await p.evaluate(()=>localStorage.getItem('sefa:decision-journal-v1'));
   assert.ok(saved);await p.reload();
   await p.waitForFunction(()=>document.querySelectorAll('#trace-items tr').length===3);
   await upload('#journal-import','bad.json','{"schema":"invalid"}','application/json');
   await p.waitForFunction(()=>document.querySelector('#journal-status').textContent.includes('отклонена'));
   assert.equal(await p.evaluate(()=>localStorage.getItem('sefa:decision-journal-v1')),saved);
  });
  await check('owner: restore confirmed backup and reject stale CSV',async()=>{
   p.once('dialog',d=>d.accept());await p.locator('#journal-clear').click();
   await p.waitForFunction(()=>document.querySelectorAll('#trace-items tr').length===0);
   p.once('dialog',d=>d.accept());await upload('#journal-import','backup.json',saved,'application/json');
   await p.waitForFunction(()=>document.querySelectorAll('#trace-items tr').length===3);
   await upload('#csv','invalid.csv','wrong,header\n1,2');
   await p.waitForFunction(()=>document.querySelector('#issues').textContent.includes('Ошибка импорта'));
   assert.equal((await read(p,'#orders')).trim(),'—');
   assert.equal(await p.locator('#journal-add').isDisabled(),true);
  });
  await check('owner: mobile viewport and runtime integrity',async()=>{assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.deepEqual(errors,[])});
 }finally{await context.close()}
}finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
