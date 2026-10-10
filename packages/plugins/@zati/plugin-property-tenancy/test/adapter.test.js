'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const base=path.join(__dirname,'../dist');
async function load() {
 const hooks=new Map();let resource,snippet;
 const Plugin=class {};
 const module={exports:{}};
 const source=fs.readFileSync(path.join(base,'server/index.js'),'utf8');
 vm.runInNewContext(source,{module,exports:module.exports,WeakSet,Object,Array,require:name=>name==='@nocobase/server'?{Plugin}:require(path.join(base,'server',name))});
 const p=new module.exports();
 p.db={on:(name,fn)=>{const old=hooks.get(name);hooks.set(name,old? (...args)=>{old(...args);return fn(...args);}:fn);},getModel:()=>null};
 p.app={resourcer:{define:value=>resource=value},acl:{registerSnippet:value=>snippet=value}};
 await p.load();return {hooks,resource,snippet};
}
test('native resource defines only fixed typed actions and explicit ACL snippet',async()=>{
 const {resource,snippet}=await load();
 assert.equal(resource.name,'zpPropertyTenancy');
 assert.equal(resource.only.length,13);assert.equal(Object.keys(resource.actions).length,13);
 assert.equal(snippet.actions.length,13);
 const spec=require('../dist/swagger/index.json');
 for(const name of resource.only) {
   const body=spec.paths['/zpPropertyTenancy:'+name].post.requestBody;
   assert.equal(body.required,true);
   assert.equal(body.content['application/json'].schema.additionalProperties,false);
 }
});
test('generic creates updates destroys bulk and nested save paths denied',async()=>{
 const {hooks}=await load();
 for(const collection of ['zp_tenancies','zp_tenancy_terms','zp_tenancy_parties','zp_ownership_sets','zp_property_interests','zp_domain_events','zp_audit_heads','zp_domain_outbox','zp_properties','zp_units','zp_buildings','zp_owner_contacts','zp_tenant_account_permissions']) {
   for(const hook of ['beforeCreate','beforeUpdate','beforeDestroy','beforeSave','afterSave','beforeBulkCreate'])assert.throws(()=>hooks.get(collection+'.'+hook)({}, {transaction:{}}),/DOMAIN_ACTION_REQUIRED/);
   for(const hook of ['beforeBulkUpdate','beforeBulkDestroy'])assert.throws(()=>hooks.get(collection+'.'+hook)({transaction:{}}),/DOMAIN_ACTION_REQUIRED/);
 }
});
test('identity and hierarchy reassignment and deletes denied',async()=>{
 const {hooks}=await load();
 assert.throws(()=>hooks.get('zp_units.beforeUpdate')({changed:key=>key==='propertyId'},{}),/DOMAIN_ACTION_REQUIRED/);
 assert.throws(()=>hooks.get('zp_properties.beforeBulkUpdate')({attributes:{managerUserId:20}}),/DOMAIN_ACTION_REQUIRED/);
 assert.throws(()=>hooks.get('zp_owner_contacts.beforeDestroy')(),/DOMAIN_ACTION_REQUIRED/);
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
