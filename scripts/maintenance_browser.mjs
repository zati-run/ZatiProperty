// Synthetic end-user acceptance only; never use builder controls or direct API writes.
// Private runtime files: role-accounts.json = {manager:{email,password},tenant:{...},...}
// browser-acceptance.json = {origin, route, expectedContext:[text], savedText,
//   steps:[{action:"click|fill|select|press", target:{role,name}|{label}|{text},value?}],
//   denied:[{role,route,message}]}. Bind these from observed generated page state.
import assert from 'node:assert/strict';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
for (const key of ['ZP_RUNTIME_DIR','ZP_BROWSER_MODULE']) assert.ok(process.env[key],`${key} required`);
const runtime=resolve(process.env.ZP_RUNTIME_DIR);
const spec=JSON.parse(await readFile(join(runtime,'browser-acceptance.json'),'utf8'));
const accounts=JSON.parse(await readFile(join(runtime,'role-accounts.json'),'utf8'));
const base=new URL(spec.origin);
assert.ok(['127.0.0.1','localhost','[::1]'].includes(base.hostname),'synthetic loopback only');
const route=(value)=>{const url=new URL(value,base);assert.equal(url.origin,base.origin);assert.ok(url.pathname.startsWith('/admin/'));return url.href;};
assert.ok(Array.isArray(spec.expectedContext)&&spec.expectedContext.length,'context assertions required');
const output=resolve(process.env.ZP_BROWSER_OUTPUT||'docs/generation/receipts/screenshots');
await mkdir(output,{recursive:true});
const {chromium}=await import(pathToFileURL(resolve(process.env.ZP_BROWSER_MODULE)).href);
const browser=await chromium.launch({headless:true});
const checks=[];
function target(page,t){
 if(t.role)return page.getByRole(t.role,{name:t.name,exact:true});
 if(t.label)return page.getByLabel(t.label,{exact:true});
 if(t.text)return page.getByText(t.text,{exact:true});
 throw Error('accessible locator required');
}
async function login(page,role){
 const account=accounts[role];assert.ok(account?.email&&account?.password,`account unavailable: ${role}`);
 await page.goto(base.href);
 await page.getByPlaceholder('Username/Email').fill(account.email);
 await page.getByPlaceholder('Password',{exact:true}).fill(account.password);
 await page.locator('button[type=submit]').click();
 await page.waitForURL(url=>url.pathname.startsWith('/admin'),{timeout:30000});
}
try{
 for(const viewport of [{width:1365,height:900},{width:390,height:844}]){
  const context=await browser.newContext({viewport});const page=await context.newPage();
  try{
   await login(page,'manager');await page.goto(route(spec.route));
   for(const text of spec.expectedContext)await page.getByText(text,{exact:true}).first().waitFor();
   await page.keyboard.press('Tab');
   assert.ok(await page.evaluate(()=>document.activeElement!==document.body),'keyboard focus enters page');
   let journey='not-run';
   if(process.env.ZP_RUN_JOURNEY==='1'){
    assert.ok(spec.steps?.length&&spec.savedText,'bound journey steps and saved result required');
    for(const step of spec.steps){
     const locator=target(page,step.target);await locator.waitFor();
     if(step.action==='click'){await locator.focus();await locator.press('Enter');}
     else if(step.action==='fill')await locator.fill(step.value);
     else if(step.action==='select')await locator.selectOption({label:step.value});
     else if(step.action==='press')await locator.press(step.value);
     else throw Error('unsupported journey action');
    }
    await page.getByText(spec.savedText,{exact:true}).first().waitFor();
    await page.reload();await page.getByText(spec.savedText,{exact:true}).first().waitFor();journey='saved-and-reloaded';
   }
   const screenshot=`maintenance-manager-${viewport.width}.png`;
   await page.screenshot({path:join(output,screenshot),fullPage:true});
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
   checks.push({role:'manager',viewport,contextVisible:true,keyboardFocus:true,journey,screenshot,horizontalOverflow:overflow});
  }finally{await context.close();}
 }
 for(const denied of spec.denied||[]){
  assert.ok(denied.role!=='manager'&&denied.message,'explicit denied state required');
  const context=await browser.newContext({viewport:{width:1365,height:900}});const page=await context.newPage();
  try{await login(page,denied.role);await page.goto(route(denied.route));await page.getByText(denied.message,{exact:true}).first().waitFor();
   const screenshot=`maintenance-denied-${denied.role.replace(/[^a-z0-9_-]/gi,'_')}.png`;await page.screenshot({path:join(output,screenshot),fullPage:true});
   checks.push({role:denied.role,deniedStateVisible:true,screenshot});
  }finally{await context.close();}
 }
 await writeFile(join(output,'maintenance-browser.json'),JSON.stringify({observedAt:new Date().toISOString(),checks,limits:['Screenshots require independent visual review.','UI denied state does not establish server-side ACL enforcement.','Unsampled empty, error and loading states remain unverified.']},null,2)+'\n');
 console.log(JSON.stringify({completed:true,checks}));
}finally{await browser.close();}
