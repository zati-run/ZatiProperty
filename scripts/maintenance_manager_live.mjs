// End-user synthetic manager flow; no builder or direct API mutations.
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const runtime=process.env.ZP_RUNTIME_DIR;assert.ok(runtime&&process.env.ZP_BROWSER_MODULE);
const {chromium}=await import(pathToFileURL(process.env.ZP_BROWSER_MODULE));
const account=JSON.parse(await readFile(join(runtime,'maintenance-test-accounts.json'),'utf8'))['zp_property_manager.1'];
const base=process.env.ZP_BROWSER_ORIGIN||'http://127.0.0.1:18360';
assert.ok(['localhost','127.0.0.1','[::1]'].includes(new URL(base).hostname));
const width=Number(process.env.ZP_VIEWPORT_WIDTH||1365);
const output=resolve(process.env.ZP_BROWSER_OUTPUT||'docs/generation/receipts/screenshots');await mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true});const checks=[];
try{
 const page=await browser.newPage({viewport:{width,height:width<500?844:900}});
 await page.goto(base);await page.getByPlaceholder('Username/Email').fill(account.email);
 await page.getByPlaceholder('Password',{exact:true}).fill(account.password);await page.locator('button[type=submit]').click();
 await page.waitForURL(u=>u.pathname.startsWith('/admin'));await page.goto(base+'/admin/zp-maintenance');
 await page.getByText('Leaking kitchen tap',{exact:true}).waitFor();
 await page.screenshot({path:join(output,`maintenance-manager-queue-${width}.png`),fullPage:true});
 console.log(JSON.stringify({viewNode:await page.getByText('View',{exact:true}).evaluate(e=>e.outerHTML+' PARENT '+e.parentElement.outerHTML)}));
 await page.getByRole('button',{name:'View',exact:true}).focus();await page.keyboard.press('Enter');
 await page.getByText('Assign vendor',{exact:true}).waitFor();
 const contextText=await page.locator('body').innerText();
 const contextLabels=['Demo Property 1','Unit 1','DEMO-T1'];
 checks.push({context:contextLabels.map(text=>({text,visible:contextText.includes(text)}))});
 await page.screenshot({path:join(output,`maintenance-manager-context-${width}.png`),fullPage:true});
 if(process.env.ZP_RUN_JOURNEY==='1'){
  await page.getByText('Assign vendor',{exact:true}).click();await page.getByRole('button',{name:'Save assignment',exact:true}).waitFor();
  // IDs observed on native rendered controls; labels currently include punctuation.
  await page.locator('input#vendor').click();await page.getByText('Demo Vendor 1',{exact:true}).last().waitFor();
  const options=await page.locator('.ant-select-dropdown:not(.ant-select-dropdown-hidden)').innerText();
  console.log(JSON.stringify({vendorOptions:options}));assert.ok(options.includes('Demo Vendor 1'));assert.ok(!options.includes('Demo Vendor 2'),'foreign vendor visible');
  await page.locator('.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option-content').filter({hasText:'Demo Vendor 1'}).click();
  await page.locator('input#state').focus();await page.keyboard.press('ArrowDown');await page.locator('.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option-content').filter({hasText:/^Quote$/}).click();
  await page.screenshot({path:join(output,`maintenance-manager-before-save-${width}.png`),fullPage:true});
  await page.getByRole('button',{name:'Save assignment',exact:true}).focus();await page.keyboard.press('Enter');
  await page.getByRole('button',{name:'Save assignment',exact:true}).waitFor({state:'hidden'});
  await page.reload();await page.getByRole('button',{name:'View',exact:true}).focus();await page.keyboard.press('Enter');await page.getByText('Assign vendor',{exact:true}).waitFor();
  await page.getByText('Quote',{exact:true}).first().waitFor();await page.getByText('Demo Vendor 1',{exact:true}).first().waitFor();
  checks.push({save:'completed',reload:'Quote and Demo Vendor 1 rendered',vendorOptions:options,keyboard:'Native View and Save assignment buttons activated with Enter; State picker opened with ArrowDown'});
  await page.screenshot({path:join(output,`maintenance-manager-saved-reload-${width}.png`),fullPage:true});
 }
 if(process.env.ZP_VERIFY_SAVED==='1'){await page.getByText('Quote',{exact:true}).first().waitFor();await page.getByText('Demo Vendor 1',{exact:true}).first().waitFor();checks.push({freshSession:'Quote and Demo Vendor 1 visible',keyboard:'native View activated with Enter'});await page.screenshot({path:join(output,`maintenance-manager-saved-reload-${width}.png`),fullPage:true});}
 const report={observedAt:new Date().toISOString(),width,checks,limits:['Root-independent manager session.','Full journey acceptance requires all context checks plus independent visual review.','Backend deny and portal checks are separate.']};
 await writeFile(join(output,`maintenance-manager-${width}.json`),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}finally{await browser.close();}
