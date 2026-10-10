'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),{Service}=require('../dist/server/service'),d=require('../dist/server/domain');
function fixture(){
 const rows={users:[{id:30}],zp_tenant_account_permissions:[{id:1,managerUserId:10,userId:30}],zp_properties:[{id:1,managerUserId:10}],zp_units:[{id:2,propertyId:1}],zp_tenancies:[{id:3,unitId:2,tenantUserId:null,leaseState:'draft',version:2,draftRevision:3,startDate:'2030-01-01',endDate:null,privateNote:'never-return'}],
 zp_tenancy_terms:[{id:1,tenancyId:3,revision:2,rentMinor:1},{id:2,tenancyId:3,revision:3,effectiveFrom:'2030-01-01',effectiveTo:null,currency:'USD',rentMinor:12345,depositMinor:0,rentFrequency:'monthly',dueDay:1,prorationPolicy:'calendar-days',privateNote:'never-return'}],
 zp_tenancy_parties:[{id:2,tenancyId:3,revision:3,displayName:'Synthetic tenant',partyRole:'primary',userId:30,effectiveFrom:'2030-01-01',effectiveTo:null,privateNote:'never-return'}]};
 let writes=0;
 const forbidden=()=>{writes++;throw Error('READ_MUST_NOT_WRITE');};
 const service=new Service({transaction:async fn=>fn({get:async(n,id)=>rows[n]?.find(r=>d.same(r.id,id)),list:async(n,where,limit)=>(rows[n]||[]).filter(r=>Object.entries(where).every(([k,v])=>d.same(r[k],v))).slice(0,limit),head:forbidden,create:forbidden,update:forbidden}),lookupCommand:forbidden});
 return {service,rows,get writes(){return writes;}};
}
test('current revision read returns complete whitelisted proposal and stable digest with zero writes',async()=>{
 const f=fixture(),before=structuredClone(f.rows);
 const a=await f.service.execute('draftTenancyProposal',{tenancyId:3},10),b=await f.service.execute('draftTenancyProposal',{tenancyId:3},10);
 assert.deepEqual(a,b);assert.equal(a.revision,3);assert.equal(a.values.term.rentMinor,12345);assert.equal(a.values.parties.length,1);assert.equal(f.writes,0);assert.deepEqual(f.rows,before);
 assert.ok(!JSON.stringify(a).includes('privateNote'));assert.equal(a.values.term.id,undefined);assert.equal(a.values.parties[0].tenancyId,undefined);assert.equal(a.values.reasonCode,undefined);assert.equal(a.values.adoptLegacy,undefined);
});
test('foreign manager, missing record, active/legacy state and unknown inputs deny without writes',async()=>{
 for(const mutate of [f=>f.rows.zp_properties[0].managerUserId=20,f=>f.rows.zp_tenancies=[],f=>f.rows.zp_tenancies[0].leaseState='active',f=>f.rows.zp_tenancies[0].version=null]){
  const f=fixture();mutate(f);await assert.rejects(f.service.execute('draftTenancyProposal',{tenancyId:3},10));assert.equal(f.writes,0);
 }
 const f=fixture();await assert.rejects(f.service.execute('draftTenancyProposal',{tenancyId:3,requestId:'unexpected'},10),/UNKNOWN_INPUT/);assert.equal(f.writes,0);
});
test('ambiguous or invalid current revision fails closed and digest changes with version/proposals',async()=>{
 const f=fixture(),a=await f.service.execute('draftTenancyProposal',{tenancyId:3},10);
 f.rows.zp_tenancies[0].version++;f.rows.zp_tenancy_terms[1].rentMinor++;
 const b=await f.service.execute('draftTenancyProposal',{tenancyId:3},10);assert.notEqual(a.proposalDigest,b.proposalDigest);
 f.rows.zp_tenancy_terms.push({...f.rows.zp_tenancy_terms[1],id:4});await assert.rejects(f.service.execute('draftTenancyProposal',{tenancyId:3},10),/INVALID_TERMS/);assert.equal(f.writes,0);
});

test('current party account authorization is rechecked without writes',async()=>{
 for(const change of [f=>f.rows.users=[],f=>f.rows.zp_tenant_account_permissions=[],f=>f.rows.zp_tenant_account_permissions[0].managerUserId=20,f=>f.rows.zp_tenant_account_permissions.push({...f.rows.zp_tenant_account_permissions[0],id:2})]){
  const f=fixture();change(f);const before=structuredClone(f.rows);
  await assert.rejects(f.service.execute('draftTenancyProposal',{tenancyId:3},10),/PARTY_ACCOUNT_NOT_PERMITTED/);assert.equal(f.writes,0);assert.deepEqual(f.rows,before);
 }
});
test('canonical safe bigint party IDs normalize for typed write schema, unsafe IDs fail closed',async()=>{
 const f=fixture();f.rows.zp_tenancy_parties[0].userId='30';
 const a=await f.service.execute('draftTenancyProposal',{tenancyId:3},10);assert.equal(a.values.parties[0].userId,30);assert.equal(f.writes,0);
 for(const id of ['030','9007199254740992']){f.rows.zp_tenancy_parties[0].userId=id;await assert.rejects(f.service.execute('draftTenancyProposal',{tenancyId:3},10),/INVALID_ID/);assert.equal(f.writes,0);}
});
