'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {IntakeService,hash}=require('../dist/server/intake');
const uuid=n=>'00000000-0000-4000-8000-'+String(n).padStart(12,'0');
const input=n=>({requestId:uuid(n),propertyId:1,unitId:2,tenancyId:3,title:'Kitchen tap leaks',description:'Water drips beneath the sink.',category:'plumbing',priority:'medium',permissionToEnter:true,preferredTimes:'Weekday mornings',petInformation:'Indoor cat'});
function fixture(){
 let state={zp_properties:[{id:1,managerUserId:7},{id:9,managerUserId:8}],zp_units:[{id:2,propertyId:1},{id:10,propertyId:9}],zp_tenancies:[{id:3,unitId:2}],requests:[],orders:[],commands:[],links:[]};
 let chain=Promise.resolve(),writes=0;
 const store={lookup:async k=>state.commands.filter(x=>x.commandKey===k),transaction:async(actor,fn)=>{
  const previous=chain;let release;chain=new Promise(r=>release=r);await previous;
  const next=structuredClone(state);
  const tx={get:async(table,id)=>next[table==='zp_maintenance_requests'?'requests':table].find(x=>x.id===id),commands:async k=>next.commands.filter(x=>x.commandKey===k),
  createCommand:async x=>{next.commands.push(x);writes++;return x;},createRequest:async x=>{const row={id:next.requests.length+1,...x};next.requests.push(row);return row;},
  createOrder:async x=>{const row={id:next.orders.length+1,...x};next.orders.push(row);return row;},workOrders:async id=>next.orders.filter(x=>x.requestId===id),
  attachments:async()=>[{id:21},{id:22}],linkAttachments:async(id,ids)=>{if(store.breakLink)throw Error('Injected link failure');next.links.push({id,ids});},
  markTriaged:async id=>{next.requests.find(x=>x.id===id).status='triaged';}};
  try{const result=await fn(tx);state=next;return result;}finally{release();}
 }};
 return {service:new IntakeService(store),store,state:()=>structuredClone(state),writes:()=>writes};
}
test('intake preserves entered fields and starts Open; conversion keeps request and all native attachment links',async()=>{
 const f=fixture(),r=await f.service.execute('createRequest',input(1),7);
 assert.equal(r.status,'open');const original=f.state().requests[0];
 const job=await f.service.execute('convertRequest',{requestId:uuid(2),maintenanceRequestId:r.id},7);
 const s=f.state();assert.equal(job.state,'new');assert.equal(s.requests.length,1);assert.equal(s.requests[0].description,original.description);assert.equal(s.requests[0].status,'triaged');
 for(const key of ['title','description','propertyId','unitId','tenancyId','category','priority','preferredTimes','permissionToEnter','petInformation'])assert.deepEqual(s.orders[0][key],original[key]);
 assert.deepEqual(s.links,[{id:job.id,ids:[21,22]}]);assert.deepEqual(JSON.parse(s.orders[0].requestSnapshot).attachmentIds,[21,22]);
 assert.equal(s.orders[0].vendorId,null);assert.equal(s.orders[0].approvalRequired,true);assert.equal(s.orders[0].approvalGranted,false);
});
test('same key replays one result; collision rejects; concurrent distinct conversion commands create one job',async()=>{
 const f=fixture(),r=await f.service.execute('createRequest',input(1),7);
 assert.deepEqual(await f.service.execute('createRequest',input(1),7),r);
 await assert.rejects(f.service.execute('createRequest',{...input(1),title:'Changed'},7),{code:'REQUEST_ID_COLLISION'});
 await Promise.all([2,3].map(n=>f.service.execute('convertRequest',{requestId:uuid(n),maintenanceRequestId:r.id},7)));
 assert.equal(f.state().requests.length,1);assert.equal(f.state().orders.length,1);
});
test('foreign property and conversion denied without receipts or changes',async()=>{
 const f=fixture();await assert.rejects(f.service.execute('createRequest',{...input(1),propertyId:9},7),{code:'PROPERTY_DENIED'});assert.equal(f.state().commands.length,0);
 const r=await f.service.execute('createRequest',input(2),7),before=f.state();
 await assert.rejects(f.service.execute('convertRequest',{requestId:uuid(3),maintenanceRequestId:r.id},8),{code:'REQUEST_DENIED'});assert.deepEqual(f.state(),before);
});
test('context mismatch is terminal with no business row; reconcile is actor bound and read only',async()=>{
 const f=fixture();await assert.rejects(f.service.execute('createRequest',{...input(1),unitId:10},7),e=>e.code==='CONTEXT_MISMATCH'&&e.terminalProof?.outcome==='rejected');
 assert.equal(f.state().requests.length,0);assert.equal(f.state().commands.length,1);
 const before=f.state(),writes=f.writes();const rec=await f.service.reconcile(7,'createRequest',uuid(1));
 assert.equal(rec.outcome,'rejected');assert.equal(rec.code,'CONTEXT_MISMATCH');assert.equal(rec.requestDigest,hash({...input(1),unitId:10,requestId:undefined}));
 assert.equal((await f.service.reconcile(8,'createRequest',uuid(1))).status,'not_observed');assert.deepEqual(f.state(),before);assert.equal(f.writes(),writes);
});
test('attachment link failure rolls back job and request status and command receipt',async()=>{
 const f=fixture(),r=await f.service.execute('createRequest',input(1),7),before=f.state();f.store.breakLink=true;
 await assert.rejects(f.service.execute('convertRequest',{requestId:uuid(2),maintenanceRequestId:r.id},7),/Injected/);assert.deepEqual(f.state(),before);
});
test('invalid enum and non-string optional text reject instead of coercion',async()=>{
 for(const patch of [{category:'insurance'},{preferredTimes:false},{petInformation:0},{permissionToEnter:'yes'}]){
  const f=fixture();await assert.rejects(f.service.execute('createRequest',{...input(1),...patch},7),{code:'INVALID_INPUT'});assert.equal(f.state().requests.length,0);
 }
});
