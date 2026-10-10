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
 page.on('response',response=>{if(response.status()>=400){const url=new URL(response.url());console.log(JSON.stringify({failedRequest:url.pathname+url.search,status:response.status()}));}});
 await page.goto(base);await page.getByPlaceholder('Username/Email').fill(account.email);
 await page.getByPlaceholder('Password',{exact:true}).fill(account.password);await page.locator('button[type=submit]').click();
 await page.waitForURL(u=>u.pathname.startsWith('/admin'));await page.goto(base+'/admin/zp-maintenance');
 await page.getByText('Leaking kitchen tap',{exact:true}).waitFor();
 await page.screenshot({path:join(output,`maintenance-manager-queue-${width}.png`),fullPage:true,animations:'disabled'});
 await page.getByRole('button',{name:'View',exact:true}).focus();await page.keyboard.press('Enter');
 await page.getByText('Assign vendor',{exact:true}).waitFor({timeout:10000});
 const contextText=await page.locator('body').innerText();
 const contextLabels=['Demo Property 1','Unit 1','DEMO-T1'];
 const contextChecks=contextLabels.map(text=>({text,visible:contextText.includes(text)}));assert.ok(contextChecks.every(check=>check.visible),'all property/unit/tenancy context must render');checks.push({context:contextChecks});
 await page.screenshot({path:join(output,`maintenance-manager-context-${width}.png`),fullPage:true,animations:'disabled'});
 if(process.env.ZP_RUN_JOURNEY==='1'||process.env.ZP_INSPECT_PICKER==='1'){
  await page.getByRole('button',{name:'Assign vendor',exact:true}).focus();await page.keyboard.press('Enter');await page.getByRole('button',{name:'Save assignment',exact:true}).waitFor();
  // IDs observed on native rendered controls; labels currently include punctuation.
  const pendingOptions=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/zp_vendors:list');
  if(width<500){await page.locator('.ant-select-selector').filter({has:page.locator('input#vendor')}).click();}else{await page.locator('input#vendor').focus();await page.keyboard.press('ArrowDown');}const pickerResponse=await pendingOptions;assert.equal(pickerResponse.status(),200,'live picker list must succeed; cached selection is not acceptance');const pickerData=await pickerResponse.json();assert.deepEqual(pickerData.data.map(record=>record.name),['Demo Vendor 1'],'exact native eligible option records required');checks.push({livePickerHTTP:pickerResponse.status(),eligibleNames:pickerData.data.map(record=>record.name)});await page.getByText('Demo Vendor 1',{exact:true}).last().waitFor();
  if(width<500){await page.getByText('Demo Vendor 1',{exact:true}).last().scrollIntoViewIfNeeded();}
  const options=width<500?pickerData.data.map(record=>record.name).join('\n'):await page.locator('.ant-select-dropdown:not(.ant-select-dropdown-hidden)').innerText();
  console.log(JSON.stringify({vendorOptions:options}));checks.push({vendorOptions:options});await page.screenshot({path:join(output,`maintenance-manager-picker-${width}.png`),fullPage:true,animations:'disabled'});assert.ok(options.includes('Demo Vendor 1'));assert.ok(!options.includes('Demo Vendor 2'),'foreign vendor visible');
  if(process.env.ZP_RUN_JOURNEY==='1'){
  if(width<500){await page.getByText('Demo Vendor 1',{exact:true}).last().click();}else{await page.locator('.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option-content').filter({hasText:'Demo Vendor 1'}).click();}
  if(width<500){await page.locator('.ant-select').filter({has:page.locator('input#state')}).locator('..').click();await page.getByText('Quote',{exact:true}).last().click();}else{await page.locator('input#state').focus();await page.keyboard.press('ArrowDown');await page.locator('.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option-content').filter({hasText:/^Quote$/}).click();}
  await page.screenshot({path:join(output,`maintenance-manager-before-save-${width}.png`),fullPage:true,animations:'disabled'});
  await page.getByRole('button',{name:'Save assignment',exact:true}).focus();await page.keyboard.press('Enter');
  await page.getByRole('button',{name:'Save assignment',exact:true}).waitFor({state:'hidden'});
  await page.reload();await page.goto(base+'/admin/zp-maintenance');await page.getByRole('button',{name:'View',exact:true}).focus();await page.keyboard.press('Enter');await page.getByText('Assign vendor',{exact:true}).waitFor({timeout:10000});
  await page.getByText('Quote',{exact:true}).first().waitFor();await page.getByText('Demo Vendor 1',{exact:true}).first().waitFor();
  checks.push({save:'completed',reload:'Quote and Demo Vendor 1 rendered',vendorOptions:options,keyboard:width<500?'Native View, Assign vendor and Save assignment buttons activated with Enter; mobile selectors used pointer':'Native View, Assign vendor and Save assignment buttons activated with Enter; selectors opened with ArrowDown'});
  await page.screenshot({path:join(output,`maintenance-manager-saved-reload-${width}.png`),fullPage:true,animations:'disabled'});
  }
 }
 if(process.env.ZP_VERIFY_SAVED==='1'){await page.getByText('Quote',{exact:true}).first().waitFor();await page.getByText('Demo Vendor 1',{exact:true}).first().waitFor();checks.push({freshSession:'Quote and Demo Vendor 1 visible',keyboard:'native View activated with Enter'});await page.screenshot({path:join(output,`maintenance-manager-saved-reload-${width}.png`),fullPage:true,animations:'disabled'});}
 const report={observedAt:new Date().toISOString(),width,checks,limits:['Root-independent manager session.','Full journey acceptance requires all context checks plus independent visual review.','Backend deny and portal checks are separate.']};
 await writeFile(join(output,`maintenance-manager-${width}.json`),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
}catch(error){const current=browser.contexts()[0]?.pages()[0];if(current){console.log(JSON.stringify({failure:error.name,body:(await current.locator('body').innerText()).slice(-6000)}));await current.screenshot({path:join(output,`maintenance-manager-failure-${width}.png`),fullPage:true,animations:'disabled'});}throw error;}finally{await browser.close();}
