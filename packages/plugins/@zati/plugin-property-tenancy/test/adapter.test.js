'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const base=path.join(__dirname,'../dist');
async function load(can=()=>true,ServiceOverride=null) {
 const hooks=new Map();const snippets=[];let resource,snippet;
 const Plugin=class {};
 const module={exports:{}};
 const source=fs.readFileSync(path.join(base,'server/index.js'),'utf8');
 vm.runInNewContext(source,{module,exports:module.exports,WeakSet,Object,Array,require:name=>name==='@nocobase/server'?{Plugin}:name==='./service'&&ServiceOverride?{...require(path.join(base,'server',name)),Service:ServiceOverride}:require(path.join(base,'server',name))});
 const p=new module.exports();
 p.db={on:(name,fn)=>{const old=hooks.get(name);hooks.set(name,old? (...args)=>{old(...args);return fn(...args);}:fn);},getModel:()=>null};
 p.app={resourcer:{define:value=>resource=value},acl:{can,registerSnippet:value=>{snippet=value;snippets.push(value);}}};
 await p.load();return {hooks,resource,snippet,snippets};
}
test('native resource defines only fixed typed actions and explicit ACL snippet',async()=>{
 const {resource,snippet}=await load();
 assert.equal(resource.name,'zpPropertyTenancy');
 assert.equal(resource.only.length,14);assert.equal(Object.keys(resource.actions).length,14);
 assert.equal(snippet.actions.length,2);assert.deepEqual(Array.from(snippet.actions),['zpPropertyTenancy:authorizeTenantAccount','zpPropertyTenancy:reconcileCommand']);
 const spec=require('../dist/swagger/index.json');
 for(const name of resource.only) {
   if(name==='reconcileCommand'){assert.ok(spec.paths['/zpPropertyTenancy:'+name].get);continue;}
   const body=spec.paths['/zpPropertyTenancy:'+name].post.requestBody;
   assert.equal(body.required,true);
   assert.equal(body.content['application/json'].schema.additionalProperties,false);
 }
});
test('generic creates updates destroys bulk and nested save paths denied',async()=>{
 const {hooks}=await load();
 for(const collection of ['zp_tenancies','zp_tenancy_terms','zp_tenancy_parties','zp_ownership_sets','zp_property_interests','zp_domain_events','zp_audit_heads','zp_domain_outbox','zp_properties','zp_units','zp_buildings','zp_owner_contacts','zp_tenant_account_permissions']) {
   for(const hook of ['beforeCreate','beforeUpdate','beforeDestroy','beforeSave','afterSave','beforeBulkCreate'])assert.throws(()=>hooks.get(collection+'.'+hook)({}, {transaction:{}}),error=>error.code==='DOMAIN_ACTION_REQUIRED'&&error.status===403&&error.expose===true);
   for(const hook of ['beforeBulkUpdate','beforeBulkDestroy'])assert.throws(()=>hooks.get(collection+'.'+hook)({transaction:{}}),error=>error.code==='DOMAIN_ACTION_REQUIRED'&&error.status===403&&error.expose===true);
 }
});
test('identity and hierarchy reassignment and deletes denied',async()=>{
 const {hooks}=await load();
 assert.throws(()=>hooks.get('zp_units.beforeUpdate')({changed:key=>key==='propertyId'},{}),error=>error.code==='DOMAIN_ACTION_REQUIRED'&&error.status===403&&error.expose===true);
 assert.throws(()=>hooks.get('zp_properties.beforeBulkUpdate')({attributes:{managerUserId:20}}),error=>error.code==='DOMAIN_ACTION_REQUIRED'&&error.status===403&&error.expose===true);
 assert.throws(()=>hooks.get('zp_owner_contacts.beforeDestroy')(),error=>error.code==='DOMAIN_ACTION_REQUIRED'&&error.status===403&&error.expose===true);
});
test('no implicit root business role or union-role bypass',async()=>{
 const {resource}=await load();
 const ctx={state:{currentUser:{id:1},currentRoles:['root','member']},acl:{can:()=>true},throw:(status,message)=>{throw Error(status+':'+message);}};
 await assert.rejects(resource.actions.createDraftTenancy(ctx,async()=>{}),/403:DOMAIN_ACTION_DENIED/);
 ctx.state.currentRoles=['root'];ctx.acl.can=()=>false;
 await assert.rejects(resource.actions.createDraftTenancy(ctx,async()=>{}),/403:DOMAIN_ACTION_DENIED/);
});
test('no-op client entry loads with pinned native dependency',()=>{
 const pkg=require('../package.json'),versions=require('../dist/externalVersion.js');
 assert.equal(pkg.main,'dist/server/index.js');
 assert.ok(versions);
 const source=fs.readFileSync(path.join(base,'client/index.js'),'utf8');
 assert.match(source,/@nocobase\/client/);
});

test('reconciliation requires original action ACL before any repository lookup',async()=>{
 const {resource}=await load(({action})=>action==='reconcileCommand');
 let next=false;
 const ctx={state:{currentUser:{id:10},currentRole:'manager'},action:{params:{commandAction:'createDraftTenancy',requestId:'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'}},throw(status,message){const e=new Error(message);e.status=status;throw e;}};
 await assert.rejects(resource.actions.reconcileCommand(ctx,async()=>{next=true;}),e=>e.status===403&&e.message==='DOMAIN_ACTION_DENIED');
 assert.equal(next,false);
});
test('manager snippet excludes constructor account mapping action',async()=>{
 const {snippets}=await load();
 const manager=snippets.find(s=>s.name.endsWith('.manager'));
 assert.ok(manager.actions.includes('zpPropertyTenancy:reconcileCommand'));
 assert.equal(manager.actions.includes('zpPropertyTenancy:authorizeTenantAccount'),false);
});

async function constructorProbe(role,can) {
 const calls=[];
 class CapturingService {async execute(action,input,actor,authority){calls.push({action,authority});if(!authority.constructor){const e=new Error('CONSTRUCTOR_REQUIRED');e.code='CONSTRUCTOR_REQUIRED';throw e;}return {ok:true};}}
 const {resource}=await load(can,CapturingService);
 const ctx={state:{currentUser:{id:1},currentRoles:[role]},action:{params:{values:{}}},throw(status,message,extra){const e=new Error(message);e.status=status;e.code=extra?.code;throw e;}};
 return {calls,ctx,invoke:()=>resource.actions.authorizeTenantAccount(ctx,async()=>{})};
}
test('stored role allowAll null does not block effective unrestricted constructor',async()=>{
 const p=await constructorProbe('custom-constructor',({resource})=>resource==='flowSurfaces'?{params:{}}:true);
 await p.invoke();assert.equal(p.ctx.body.data.ok,true);assert.equal(p.calls[0].authority.constructor,true);
});
test('named root without native authoring authority is denied',async()=>{
 const p=await constructorProbe('root',({resource})=>resource==='zpPropertyTenancy');
 await assert.rejects(p.invoke(),e=>e.status===403&&e.code==='CONSTRUCTOR_REQUIRED');
});
test('all domain actions do not imply constructor authority',async()=>{
 const p=await constructorProbe('manager',({resource})=>resource==='zpPropertyTenancy');
 await assert.rejects(p.invoke(),e=>e.status===403&&e.code==='CONSTRUCTOR_REQUIRED');
});
test('restricted native authoring authority cannot authorize accounts',async()=>{
 const p=await constructorProbe('scoped-constructor',({resource})=>resource==='flowSurfaces'?{params:{filter:{id:1}}}:true);
 await assert.rejects(p.invoke(),e=>e.status===403&&e.code==='CONSTRUCTOR_REQUIRED');
});
test('constructor authoring capability still requires explicit action ACL',async()=>{
 const p=await constructorProbe('constructor',({resource})=>resource==='flowSurfaces'?{params:{}}:false);
 await assert.rejects(p.invoke(),e=>e.status===403&&e.message==='DOMAIN_ACTION_DENIED');assert.equal(p.calls.length,0);
});
