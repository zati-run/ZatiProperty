'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const native=require('../dist/server/intake-native');
function app(allow=true){
 const listeners=new Map(),resources=[],snippets=[],schemas=[];
 const plugin={db:{getCollection(){throw Error('unexpected database access');},on:(name,fn)=>listeners.set(name,fn)},app:{acl:{can:()=>allow,registerSnippet:x=>snippets.push(x)},resourceManager:{define:x=>resources.push(x)},getPlugin:()=>({swagger:{add:(...x)=>schemas.push(x)}})}};
 native.register(plugin);return {plugin,listeners,resources,snippets,schemas};
}
function ctx(role='manager'){return {state:{currentUser:{id:7},currentRoles:[role]},action:{params:{values:{}}},throw(status,message){throw Object.assign(Error(message),{status});}};}
test('actual registered actions and native Swagger agree; no generic create grant',()=>{
 const f=app(),actions=Object.keys(f.resources[0].actions);assert.deepEqual(actions,['createRequest','convertRequest','reconcileCommand']);
 const swagger=f.schemas[0][1];assert.equal(swagger.paths['/zpMaintenance:createRequest'].post['x-loom-command-contract'],'idempotent-terminal-v1');
 assert.equal(swagger.paths['/zpMaintenance:reconcileCommand'].get.parameters.find(x=>x.name==='commandAction').schema.enum.length,2);
 assert.ok(f.snippets.every(s=>s.actions.every(a=>a.startsWith('zpMaintenance:'))));
});
test('actual registered adapter denies unauthenticated, union role and disallowed action before model access',async()=>{
 const f=app(false),run=f.resources[0].actions.createRequest;
 await assert.rejects(run(ctx(),async()=>{}),{status:403});
 const union=ctx();union.state.currentRoles=['manager','root'];await assert.rejects(run(union,async()=>{}),{status:403});
 const anon=ctx();delete anon.state.currentUser;await assert.rejects(run(anon,async()=>{}),{status:401});
});
test('reconciliation checks both original action and reconciliation permission, not database by arbitrary key',async()=>{
 const f=app(),c=ctx();c.action.params={commandAction:'destroy',requestId:'anything'};
 await assert.rejects(f.resources[0].actions.reconcileCommand(c,async()=>{}),{status:422});
 let calls=[];f.plugin.app.acl.can=x=>{calls.push(x.action);return x.action!=='reconcileCommand';};
 c.action.params.commandAction='createRequest';await assert.rejects(f.resources[0].actions.reconcileCommand(c,async()=>{}),{status:403});
 assert.deepEqual(calls,['createRequest','reconcileCommand']);
});
test('generic single and bulk receipt mutation and generic intake creation deny without owned transaction',()=>{
 const f=app();
 for(const event of ['beforeCreate','beforeUpdate','beforeSave','beforeDestroy','beforeBulkCreate'])assert.throws(()=>f.listeners.get('zp_maintenance_commands.'+event)({},{}),{code:'DOMAIN_ACTION_REQUIRED'});
 for(const event of ['beforeBulkUpdate','beforeBulkDestroy'])assert.throws(()=>f.listeners.get('zp_maintenance_commands.'+event)({}),{code:'DOMAIN_ACTION_REQUIRED'});
 for(const table of ['zp_maintenance_requests','zp_work_orders'])assert.throws(()=>f.listeners.get(table+'.beforeCreate')({},{}),{code:'DOMAIN_ACTION_REQUIRED'});
});
test('attachment association hook requires current actor to own linked native files',async()=>{
 const f=app(),hook=f.listeners.get('zp_maintenance_requests.afterSaveWithAssociations'),transaction={};
 await hook({getAttachments:async()=>[{createdById:7}]},{transaction,context:{state:{currentUser:{id:7}}}});
 await assert.rejects(hook({getAttachments:async()=>[{createdById:8}]},{transaction,context:{state:{currentUser:{id:7}}}}),{code:'ATTACHMENT_DENIED'});
 await assert.rejects(hook({getAttachments:async()=>[{createdById:7}]},{transaction}),{code:'ATTACHMENT_DENIED'});
});
test('safe response preserves terminal proof but strips unknown exception details',()=>{
 const c={};native.writeError(c,Object.assign(Error('credential-secret'),{code:'UNKNOWN'}));assert.equal(c.status,503);assert.ok(!JSON.stringify(c.body).includes('credential-secret'));
 native.writeError(c,Object.assign(Error('Select a valid context'),{code:'CONTEXT_MISMATCH',status:422,terminalProof:{outcome:'rejected'}}));assert.equal(c.status,422);assert.equal(c.body.terminalProof.outcome,'rejected');
});
