'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {Service,ZERO}=require('../dist/server/service');
const d=require('../dist/server/domain');
function fixture() {
 let rows={zp_tenancies:[],zp_domain_events:[],zp_domain_outbox:[],zp_properties:[{id:1,managerUserId:10},{id:2,managerUserId:20}],zp_units:[{id:1,propertyId:1},{id:2,propertyId:2}],users:[{id:30,nickname:'Synthetic tenant30'}],zp_owner_contacts:[{id:1,managerUserId:10},{id:2,managerUserId:10},{id:3,managerUserId:20}],zp_domain_commands:[],zp_tenant_account_permissions:[{id:1,managerUserId:10,userId:30}],zp_audit_heads:[{id:1,headSequence:0,headHash:ZERO}]};
 let queue=Promise.resolve(),fail=null;
 const store={lookupCommand:async key=>structuredClone(rows.zp_domain_commands.filter(r=>r.commandKey===key)),transaction:async cb=>{
   let release;const prior=queue;queue=new Promise(r=>release=r);await prior;
   const copy=structuredClone(rows);
   const table=name=>copy[name]||(copy[name]=[]);
   const tx={
     head:async()=>table('zp_audit_heads')[0],
     get:async(name,id)=>table(name).find(r=>d.same(r.id,id)),
     list:async(name,where,limit)=>table(name).filter(r=>Object.entries(where).every(([k,v])=>d.same(r[k],v))).slice(0,limit),
     create:async(name,value)=>{if(fail===name)throw Error('simulated storage failure');const row={...value,id:Math.max(0,...table(name).map(r=>r.id))+1};table(name).push(row);return row;},
     update:async(name,id,value)=>{const r=table(name).find(r=>d.same(r.id,id));Object.assign(r,value);return r;}
   };
   try{const result=await cb(tx);rows=copy;return result;}finally{release();}
 }};
 const service=new Service(store),execute=service.execute.bind(service);service.execute=(action,input,actor,authority)=>execute(action,['auditHealth','reconcileCommand'].includes(action)?input:{requestId:require('node:crypto').randomUUID(),...input},actor,authority);return {service,get rows(){return rows;},fail:name=>fail=name};
}
const draft=()=>({unitId:1,code:'T-1',startDate:'2030-01-01',endDate:'2031-01-01',term:{effectiveFrom:'2030-01-01',effectiveTo:'2031-01-01',currency:'USD',rentMinor:100000,depositMinor:50000,rentFrequency:'monthly',dueDay:1,prorationPolicy:'calendar-days'},parties:[{displayName:'Synthetic tenant',userId:30,partyRole:'primary',effectiveFrom:'2030-01-01',effectiveTo:'2031-01-01'}],reasonCode:'initial-setup'});
test('draft persists immutable proposal revision and atomic audit/outbox without posting',async()=>{
 const f=fixture(),r=await f.service.execute('createDraftTenancy',draft(),10);
 assert.equal(r.leaseState,'draft');assert.equal(f.rows.zp_tenancies[0].tenantUserId,null);assert.equal(f.rows.zp_tenancies[0].status,'open');
 assert.equal(f.rows.zp_tenancy_terms[0].revision,1);assert.equal(f.rows.zp_domain_outbox.length,1);
 assert.ok(!f.rows.journal_lines);
 assert.equal(d.verifyEvents(f.rows.zp_domain_events,f.rows.zp_audit_heads[0]).sequence,1);
 assert.ok(!f.rows.zp_domain_events[0].canonicalPayload.includes('Synthetic tenant'));
});
test('foreign manager and extra nested payload denied without changes',async()=>{
 const f=fixture();await assert.rejects(f.service.execute('createDraftTenancy',draft(),20),/PROPERTY_SCOPE/);
 await assert.rejects(f.service.execute('createDraftTenancy',{...draft(),unit:{propertyId:2}},10),/UNKNOWN_INPUT/);
 assert.equal(f.rows.zp_domain_events.length,0);
});
test('activation and end preserve status, proposal history, and chain',async()=>{
 const f=fixture();await f.service.execute('createDraftTenancy',draft(),10);
 await f.service.execute('activateTenancy',{tenancyId:1,expectedVersion:0,reasonCode:'initial-setup'},10);
 await f.service.execute('endTenancy',{tenancyId:1,expectedVersion:1,endDate:'2030-06-01',reasonCode:'initial-setup'},10);
 assert.equal(f.rows.zp_tenancies[0].tenantUserId,30);assert.equal(f.rows.zp_tenancies[0].leaseState,'ended');assert.equal(f.rows.zp_tenancies[0].status,'open');
 assert.equal(f.rows.zp_tenancy_terms[0].effectiveTo,'2031-01-01');
 assert.equal(d.verifyEvents(f.rows.zp_domain_events,f.rows.zp_audit_heads[0]).sequence,3);
});
test('draft edits append proposal versions and stale writes rollback',async()=>{
 const f=fixture();await f.service.execute('createDraftTenancy',draft(),10);
 const {unitId,code,...input}=draft();
 await f.service.execute('updateDraftTenancy',{...input,tenancyId:1,expectedVersion:0},10);
 assert.deepEqual(f.rows.zp_tenancy_terms.map(r=>r.revision),[1,2]);
 await assert.rejects(f.service.execute('activateTenancy',{tenancyId:1,expectedVersion:0,reasonCode:'initial-setup'},10),/STALE_VERSION/);
 assert.equal(f.rows.zp_domain_events.length,2);
});
test('serialized concurrent activations produce one winner and no partial loser',async()=>{
 const f=fixture();await f.service.execute('createDraftTenancy',draft(),10);
 await f.service.execute('createDraftTenancy',{...draft(),code:'T-2'},10);
 const results=await Promise.allSettled([1,2].map(tenancyId=>f.service.execute('activateTenancy',{tenancyId,expectedVersion:0,reasonCode:'initial-setup'},10)));
 assert.equal(results.filter(r=>r.status==='fulfilled').length,1);
 assert.match(results.find(r=>r.status==='rejected').reason.message,/OCCUPANCY_OVERLAP/);
 assert.equal(f.rows.zp_domain_events.length,3);
});
test('outbox failure rolls back tenancy and audit in same transaction',async()=>{
 const f=fixture();f.fail('zp_domain_outbox');
 await assert.rejects(f.service.execute('createDraftTenancy',draft(),10),/storage failure/);
 assert.equal(f.rows.zp_tenancies.length,0);assert.equal(f.rows.zp_domain_events.length,0);
 assert.equal(f.rows.zp_audit_heads[0].headSequence,0);
});
test('ownership complete set revisions sum exactly and approval is immutable',async()=>{
 const f=fixture();await f.service.execute('createOwnershipSet',{propertyId:1,effectiveFrom:'2030-01-01',reasonCode:'initial-setup'},10);
 await assert.rejects(f.service.execute('setOwnershipInterests',{ownershipSetId:1,expectedVersion:0,interests:[{ownerContactId:1,shareBasisPoints:9999}],reasonCode:'initial-setup'},10),/OWNERSHIP_TOTAL/);
 await f.service.execute('setOwnershipInterests',{ownershipSetId:1,expectedVersion:0,interests:[{ownerContactId:1,shareBasisPoints:6000},{ownerContactId:2,shareBasisPoints:4000}],reasonCode:'initial-setup'},10);
 await f.service.execute('approveOwnershipSet',{ownershipSetId:1,expectedVersion:1,completeSet:true,reasonCode:'initial-setup'},10);
 await assert.rejects(f.service.execute('setOwnershipInterests',{ownershipSetId:1,expectedVersion:2,interests:[{ownerContactId:1,shareBasisPoints:10000}],reasonCode:'initial-setup'},10),/OWNERSHIP_IMMUTABLE/);
 assert.equal(f.rows.zp_property_interests.length,2);assert.equal(f.rows.zp_domain_events.length,3);
});
test('audit tamper, reorder and missing tail fail independent chain verification',async()=>{
 const f=fixture();await f.service.execute('createDraftTenancy',draft(),10);
 assert.throws(()=>d.verifyEvents([] ,f.rows.zp_audit_heads[0]),/AUDIT_HEAD/);
 const rows=structuredClone(f.rows.zp_domain_events);rows[0].canonicalPayload='{}';
 assert.throws(()=>d.verifyEvents(rows,f.rows.zp_audit_heads[0]),/AUDIT_CHAIN/);
});
test('date, money, primary party and interval bounds reject malformed inputs',()=>{
 for(const change of [{startDate:'2030-02-30'},{endDate:'2029-01-01'},{parties:[]}])assert.throws(()=>d.tenancyInput({...draft(),...change}));
 const value=draft();value.term.rentMinor=1.5;assert.throws(()=>d.tenancyInput(value),/INVALID_INTEGER/);
 assert.equal(d.overlaps(['2030-01-01','2030-02-01'],['2030-02-01',null]),false);
});
test('legacy tenancy needs explicit complete adoption and preserves primary identity',async()=>{
 const f=fixture();f.rows.zp_tenancies=[{id:1,unitId:1,code:'LEGACY',status:'open',tenantUserId:30,leaseState:null,version:null}];
 await assert.rejects(f.service.execute('activateTenancy',{tenancyId:1,expectedVersion:null,reasonCode:'initial-setup'},10),/NOT_DRAFT/);
 const {unitId,code,...input}=draft();
 await assert.rejects(f.service.execute('updateDraftTenancy',{...input,tenancyId:1,expectedVersion:null},10),/NOT_DRAFT/);
 await f.service.execute('updateDraftTenancy',{...input,tenancyId:1,expectedVersion:null,adoptLegacy:true},10);
 assert.equal(f.rows.zp_tenancies[0].tenantUserId,30);
 assert.equal(f.rows.zp_tenancies[0].version,1);
 const changed=structuredClone(input);changed.parties[0].userId=99;
 await assert.rejects(f.service.execute('updateDraftTenancy',{...changed,tenancyId:1,expectedVersion:1},10),/PRIMARY_IDENTITY_IMMUTABLE/);
});
test('unqualified legacy occupancy blocks activation rather than silently treating unit vacant',async()=>{
 const f=fixture();f.rows.zp_tenancies=[{id:1,unitId:1,code:'LEGACY',leaseState:null}];
 await f.service.execute('createDraftTenancy',draft(),10);
 await assert.rejects(f.service.execute('activateTenancy',{tenancyId:2,expectedVersion:0,reasonCode:'initial-setup'},10),/LEGACY_OCCUPANCY_UNQUALIFIED/);
 assert.equal(f.rows.zp_domain_events.length,1);
});
test('ended historical occupancy prevents backdated overlapping activation',async()=>{
 const f=fixture();await f.service.execute('createDraftTenancy',draft(),10);
 await f.service.execute('activateTenancy',{tenancyId:1,expectedVersion:0,reasonCode:'initial-setup'},10);
 await f.service.execute('endTenancy',{tenancyId:1,expectedVersion:1,endDate:'2030-06-01',reasonCode:'initial-setup'},10);
 await f.service.execute('createDraftTenancy',{...draft(),code:'T-2'},10);
 await assert.rejects(f.service.execute('activateTenancy',{tenancyId:2,expectedVersion:0,reasonCode:'initial-setup'},10),/OCCUPANCY_OVERLAP/);
});
test('foreign owner linkage and missing complete-set confirmation denied atomically',async()=>{
 const f=fixture();await f.service.execute('createOwnershipSet',{propertyId:1,effectiveFrom:'2030-01-01',reasonCode:'initial-setup'},10);
 await assert.rejects(f.service.execute('setOwnershipInterests',{ownershipSetId:1,expectedVersion:0,interests:[{ownerContactId:3,shareBasisPoints:10000}],reasonCode:'initial-setup'},10),/OWNER_SCOPE/);
 await assert.rejects(f.service.execute('approveOwnershipSet',{ownershipSetId:1,expectedVersion:0,reasonCode:'initial-setup'},10),/COMPLETE_SET_CONFIRMATION/);
 assert.equal(f.rows.zp_property_interests,undefined);assert.equal(f.rows.zp_domain_events.length,1);
});
test('simultaneous overlapping ownership approvals have one winner',async()=>{
 const f=fixture();
 for(let i=1;i<=2;i++){
  await f.service.execute('createOwnershipSet',{propertyId:1,effectiveFrom:'2030-01-01',reasonCode:'initial-setup'},10);
  await f.service.execute('setOwnershipInterests',{ownershipSetId:i,expectedVersion:0,interests:[{ownerContactId:1,shareBasisPoints:10000}],reasonCode:'initial-setup'},10);
 }
 const results=await Promise.allSettled([1,2].map(ownershipSetId=>f.service.execute('approveOwnershipSet',{ownershipSetId,expectedVersion:1,completeSet:true,reasonCode:'initial-setup'},10)));
 assert.equal(results.filter(r=>r.status==='fulfilled').length,1);
 assert.match(results.find(r=>r.status==='rejected').reason.message,/OWNERSHIP_OVERLAP/);
 assert.equal(f.rows.zp_domain_events.length,5);
});
test('unsupported per-room leasing and over-limit monetary values fail closed',async()=>{
 const f=fixture();f.rows.zp_properties[0].perRoomLeasing=true;
 await assert.rejects(f.service.execute('createDraftTenancy',draft(),10),/PER_ROOM_UNSUPPORTED/);
 const input=draft();input.term.rentMinor=2147483648;
 assert.throws(()=>d.tenancyInput(input),/INVALID_INTEGER/);
});
test('protected context creation binds actor and rejects cross-property building',async()=>{
 const f=fixture();
 const property=await f.service.execute('createProperty',{name:'Synthetic new property',reasonCode:'initial-setup'},10);
 assert.equal(f.rows.zp_properties.find(r=>r.id===property.id).managerUserId,'10');
 await f.service.execute('createBuilding',{propertyId:1,name:'Building A',reasonCode:'initial-setup'},10);
 await assert.rejects(f.service.execute('createUnit',{propertyId:2,buildingId:1,name:'Unit X',reasonCode:'initial-setup'},10),/PROPERTY_SCOPE/);
 f.rows.zp_properties[1].managerUserId=10;
 await assert.rejects(f.service.execute('createUnit',{propertyId:2,buildingId:1,name:'Unit X',reasonCode:'initial-setup'},10),/BUILDING_CONTEXT/);
});
test('every linked party requires explicit constructor-owned manager/account permission',async()=>{
 const f=fixture();f.rows.users.push({id:31});
 const input=draft();input.parties.push({displayName:'Unrelated user',userId:31,partyRole:'occupant',effectiveFrom:input.startDate,effectiveTo:input.endDate});
 await assert.rejects(f.service.execute('createDraftTenancy',input,10),/PARTY_ACCOUNT_NOT_PERMITTED/);
 assert.equal(f.rows.zp_tenancies.length,0);
 await assert.rejects(f.service.execute('authorizeTenantAccount',{propertyId:1,managerUserId:10,userId:31,displayName:'Authorized synthetic tenant31',reasonCode:'account-authorized'},10),/CONSTRUCTOR_REQUIRED/);
 await f.service.execute('authorizeTenantAccount',{propertyId:1,managerUserId:10,userId:31,displayName:'Authorized synthetic tenant31',reasonCode:'account-authorized'},1,{constructor:true});
 await f.service.execute('createDraftTenancy',input,10);
 await assert.rejects(f.service.execute('activateTenancy',{tenancyId:1,expectedVersion:0,reasonCode:'activation-reviewed'},10),/PARTY_SCOPE_MIGRATION_REQUIRED/);
});
test('changed owner membership fails closed without rewriting legacy portal binding',async()=>{
 const f=fixture();f.rows.zp_properties[0].ownerUserId=30;f.rows.zp_owner_contacts[0].userId=31;f.rows.users.push({id:31});
 await f.service.execute('createOwnershipSet',{propertyId:1,effectiveFrom:'2030-01-01',reasonCode:'initial-setup'},10);
 await f.service.execute('setOwnershipInterests',{ownershipSetId:1,expectedVersion:0,interests:[{ownerContactId:1,shareBasisPoints:10000}],reasonCode:'ownership-reviewed'},10);
 await assert.rejects(f.service.execute('approveOwnershipSet',{ownershipSetId:1,expectedVersion:1,completeSet:true,reasonCode:'ownership-reviewed'},10),/OWNER_SCOPE_MIGRATION_REQUIRED/);
 assert.equal(f.rows.zp_properties[0].ownerUserId,30);
});
test('audit stores recoverable safe reason and prior/current state but no supplied names',async()=>{
 const f=fixture();await f.service.execute('createDraftTenancy',draft(),10);
 await f.service.execute('activateTenancy',{tenancyId:1,expectedVersion:0,reasonCode:'activation-reviewed'},10);
 const event=JSON.parse(f.rows.zp_domain_events[1].canonicalPayload);
 assert.equal(event.previous.state,'draft');assert.equal(event.previous.version,0);assert.equal(event.previous.tenantUserId,null);assert.equal(event.previous.draftRevision,1);
 assert.equal(event.resulting.state,'active');assert.equal(event.resulting.version,1);assert.equal(event.resulting.tenantUserId,30);assert.equal(event.resulting.startDate,'2030-01-01');
 assert.equal(event.reason,'Activation reviewed');
 assert.match(event.occurredAt,/Z$/);assert.ok(event.correlationId);
 assert.ok(!f.rows.zp_domain_events[0].canonicalPayload.includes('Synthetic tenant'));
 await assert.rejects(f.service.execute('createProperty',{name:'Other',reasonCode:'Some private text'},10),/INVALID_REASON_CODE/);
});
test('activation revalidates account existence before publishing identity',async()=>{
 const f=fixture();await f.service.execute('createDraftTenancy',draft(),10);
 f.rows.users=[];
 await assert.rejects(f.service.execute('activateTenancy',{tenancyId:1,expectedVersion:0,reasonCode:'activation-reviewed'},10),/PARTY_ACCOUNT_NOT_PERMITTED/);
 assert.equal(f.rows.zp_tenancies[0].tenantUserId,null);
 assert.equal(f.rows.zp_domain_events.length,1);
 const input=draft();input.term.currency=['USD'];
 assert.throws(()=>d.tenancyInput(input),/INVALID_TERMS/);
});

test('same request retry after lost response returns committed result without duplicate effects',async()=>{
 const f=fixture();const input={...draft(),requestId:'11111111-1111-4111-8111-111111111111'};
 const first=await f.service.execute('createDraftTenancy',input,10);
 const second=await f.service.execute('createDraftTenancy',input,10);
 assert.deepEqual(second,first);assert.equal(f.rows.zp_tenancies.length,1);assert.equal(f.rows.zp_domain_events.length,1);assert.equal(f.rows.zp_domain_outbox.length,1);assert.equal(f.rows.zp_domain_commands.length,1);
 const receipt=await f.service.execute('reconcileCommand',{action:'createDraftTenancy',requestId:input.requestId},10);
 assert.deepEqual(receipt,{status:'committed',requestId:input.requestId,result:first});
});
test('concurrent identical commands return one committed effect and audit',async()=>{
 const f=fixture();const input={...draft(),requestId:'22222222-2222-4222-8222-222222222222'};
 const results=await Promise.all([f.service.execute('createDraftTenancy',input,10),f.service.execute('createDraftTenancy',input,10)]);
 assert.deepEqual(results[0],results[1]);assert.equal(f.rows.zp_domain_events.length,1);assert.equal(f.rows.zp_domain_commands.length,1);
});
test('same command identity with different payload is collision and no new effect',async()=>{
 const f=fixture();const input={...draft(),requestId:'33333333-3333-4333-8333-333333333333'};
 await f.service.execute('createDraftTenancy',input,10);
 await assert.rejects(f.service.execute('createDraftTenancy',{...input,code:'DIFFERENT'},10),/REQUEST_ID_COLLISION/);
 assert.equal(f.rows.zp_tenancies.length,1);assert.equal(f.rows.zp_domain_events.length,1);
});
test('receipt lookup is actor and action scoped and absent never authorizes replay',async()=>{
 const f=fixture();const requestId='44444444-4444-4444-8444-444444444444';
 await f.service.execute('createDraftTenancy',{...draft(),requestId},10);
 const before=structuredClone(f.rows);
 for(const [actor,action] of [[20,'createDraftTenancy'],[10,'createProperty']]){
  assert.deepEqual(await f.service.execute('reconcileCommand',{action,requestId},actor),{status:'not_observed',requestId,retryAuthorized:false});
 }
 assert.deepEqual(f.rows,before);
});
test('absent lookup on fresh installation does not initialize audit head',async()=>{
 const f=fixture();const before=structuredClone(f.rows);
 await f.service.execute('reconcileCommand',{action:'createProperty',requestId:'55555555-5555-4555-8555-555555555555'},10);
 assert.deepEqual(f.rows,before);
});
test('rejected command rolls back receipt and domain effects',async()=>{
 const f=fixture();const requestId='66666666-6666-4666-8666-666666666666';
 await assert.rejects(f.service.execute('createDraftTenancy',{...draft(),unitId:2,requestId},10),/PROPERTY_SCOPE/);
 assert.equal(f.rows.zp_domain_commands.length,0);assert.equal(f.rows.zp_domain_events.length,0);
 assert.equal((await f.service.execute('reconcileCommand',{action:'createDraftTenancy',requestId},10)).status,'not_observed');
});
test('missing or malformed request IDs cannot initiate writes',async()=>{
 const f=fixture();
 for(const requestId of [undefined,null,'','not-a-uuid','77777777-7777-1777-8777-777777777777']){
  await assert.rejects(f.service.execute('createDraftTenancy',{...draft(),requestId},10),/INVALID_REQUEST_ID/);
 }
 assert.equal(f.rows.zp_tenancies.length,0);assert.equal(f.rows.zp_audit_heads.length,1);
});


test('command receipt insertion failure rolls back business audit and outbox atomically',async()=>{
 const f=fixture();f.fail('zp_domain_commands');
 await assert.rejects(f.service.execute('createDraftTenancy',draft(),10),/simulated storage failure/);
 assert.equal(f.rows.zp_tenancies.length,0);assert.equal(f.rows.zp_domain_events.length,0);assert.equal(f.rows.zp_domain_outbox.length,0);assert.equal(f.rows.zp_domain_commands.length,0);
});
test('permitted account choice label derives from nickname, with explicit constructor fallback',async()=>{
 const f=fixture();f.rows.users.push({id:300,nickname:'Readable synthetic tenant'},{id:301});
 await f.service.execute('authorizeTenantAccount',{propertyId:1,managerUserId:10,userId:300,displayName:'Ignored label',reasonCode:'account-authorized'},99,{constructor:true});
 await f.service.execute('authorizeTenantAccount',{propertyId:1,managerUserId:10,userId:301,displayName:'Approved fallback',reasonCode:'account-authorized'},99,{constructor:true});
 assert.equal(f.rows.zp_tenant_account_permissions.find(r=>r.userId===300).displayName,'Readable synthetic tenant');
 assert.equal(f.rows.zp_tenant_account_permissions.find(r=>r.userId===301).displayName,'Approved fallback');
});


test('audit health on an empty store remains read-only and reports zero chain',async()=>{
 const f=fixture();f.rows.zp_audit_heads.splice(0);
 const before=structuredClone(f.rows);
 const result=await f.service.execute('auditHealth',{propertyId:1},10);
 assert.equal(result.valid,true);assert.equal(result.sequence,0);assert.deepEqual(f.rows,before);
});
