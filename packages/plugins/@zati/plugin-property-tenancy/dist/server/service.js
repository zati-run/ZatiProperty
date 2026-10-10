'use strict';
const d=require('./domain');
const {randomUUID}=require('node:crypto');
const {safeFailure}=require('./errors');
const TERMINAL_CODES=new Set(['STALE_VERSION','PARTY_ACCOUNT_NOT_PERMITTED','OCCUPANCY_OVERLAP','OWNER_SCOPE_MIGRATION_REQUIRED','PARTY_SCOPE_MIGRATION_REQUIRED','INVALID_TEXT','UNKNOWN_INPUT','INVALID_DATE','INVALID_INTERVAL','INVALID_INTEGER','INVALID_TERMS','INVALID_PARTIES','TERM_PERIOD_MISMATCH','NOT_DRAFT','NOT_ACTIVE','COMPLETE_SET_CONFIRMATION','INVALID_REASON_CODE','DUPLICATE_OWNER','DUPLICATE_PARTY_USER','INVALID_ID','INVALID_INTERESTS','INVALID_PARTY_ROLE','OWNERSHIP_TOTAL','PARTY_PERIOD_MISMATCH','PRIMARY_PARTY_REQUIRED','PRIMARY_USER_REQUIRED','OWNERSHIP_OVERLAP','END_EXTENSION_FORBIDDEN','PRIMARY_IDENTITY_IMMUTABLE']);
function receiptOutcome(row) {
 let value;try{value=JSON.parse(row.resultJSON);}catch{d.deny('COMMAND_CORRUPT');}
 if(value?.commandReceiptVersion===1) {
  if(value.outcome!=='rejected'||!TERMINAL_CODES.has(value.code))d.deny('COMMAND_CORRUPT');
  return {outcome:'rejected',code:value.code};
 }
 return {outcome:'committed',result:value};
}
function deliver(row) {
 const outcome=receiptOutcome(row);
 if(outcome.outcome==='committed')return outcome.result;
 const error=new Error(outcome.code);error.code=outcome.code;
 error.terminalProof={outcome:'rejected',requestId:row.requestId,requestDigest:row.requestDigest};
 throw error;
}
const ACTIONS=['createDraftTenancy','updateDraftTenancy','activateTenancy','endTenancy','createOwnershipSet','setOwnershipInterests','approveOwnershipSet','auditHealth','createProperty','createBuilding','createUnit','createOwnerContact','authorizeTenantAccount','reconcileCommand','draftTenancyProposal'];
const ZERO='0'.repeat(64);
function commandKey(actor,action,requestId) {
  if(typeof requestId!=='string'||! /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(requestId))d.deny('INVALID_REQUEST_ID');
  return d.hash(d.canonical([actor,action,requestId]));
}
class Service {
  constructor(store) {this.store=store;}
  async execute(action,input,actor,authority={}) {
    if(!ACTIONS.includes(action))d.deny('UNKNOWN_ACTION');
    actor=d.id(actor);
    if(action==='authorizeTenantAccount'&&!authority.constructor)d.deny('CONSTRUCTOR_REQUIRED');
    if(action==='draftTenancyProposal'){
      d.keys(input,['tenancyId']);
      return this.store.transaction(async tx=>{
        const row=await tx.get('zp_tenancies',d.id(input.tenancyId));
        if(!row)d.deny('NOT_FOUND');
        await this.unit(tx,row.unitId,actor);
        if(row.leaseState!=='draft'||row.version==null||!row.draftRevision)d.deny('NOT_DRAFT');
        d.integer(row.version,0,2147483647);d.integer(row.draftRevision,1,2147483647);
        const terms=await tx.list('zp_tenancy_terms',{tenancyId:row.id,revision:row.draftRevision},2);
        const parties=await tx.list('zp_tenancy_parties',{tenancyId:row.id,revision:row.draftRevision},21);
        if(terms.length!==1)d.deny('INVALID_TERMS');
        const pick=(v,keys)=>Object.fromEntries(keys.filter(k=>v[k]!==undefined).map(k=>[k,v[k]]));
        const values={startDate:row.startDate,endDate:row.endDate||null,
          term:pick(terms[0],['effectiveFrom','effectiveTo','currency','rentMinor','depositMinor','rentFrequency','dueDay','prorationPolicy']),
          parties:parties.map(p=>pick(p,['displayName','userId','partyRole','effectiveFrom','effectiveTo']))};
        d.tenancyInput(values);
        const envelope={proposalVersion:1,tenancyId:String(row.id),expectedVersion:row.version,revision:row.draftRevision,values};
        return {...envelope,proposalDigest:d.hash(d.canonical(envelope))};
      });
    }
    if(action==='reconcileCommand'){
      d.keys(input,['action','requestId']);
      if(!ACTIONS.includes(input.action)||['auditHealth','reconcileCommand','draftTenancyProposal'].includes(input.action))d.deny('UNKNOWN_ACTION');
      const found=await this.store.lookupCommand(commandKey(actor,input.action,input.requestId));
      if(found.length>1)d.deny('COMMAND_CORRUPT');
      if(!found.length)return {status:'not_observed',requestId:input.requestId,retryAuthorized:false};
      const outcome=receiptOutcome(found[0]);
      return {receiptVersion:1,actorId:String(actor),commandAction:input.action,status:outcome.outcome,...outcome,requestId:input.requestId,requestDigest:found[0].requestDigest,...(outcome.outcome==='rejected'?{message:safeFailure({code:outcome.code}).message}: {})};
    }
    let key,requestId,requestDigest;
    if(action!=='auditHealth'){
      if(!input||typeof input!=='object'||Array.isArray(input))d.deny('UNKNOWN_INPUT');
      requestId=input.requestId;key=commandKey(actor,action,requestId);
      input={...input};delete input.requestId;requestDigest=d.hash(d.canonical(input));
    }
    let businessFailureEligible=false;
    try { return await this.store.transaction(async tx=>{
      // One lock order across every domain mutation; head serializes audit ordering.
      const head=await tx.head(action!=='auditHealth')||{headSequence:0,headHash:ZERO};
      if(key){
        const prior=await tx.list('zp_domain_commands',{commandKey:key},2);
        if(prior.length>1)d.deny('COMMAND_CORRUPT');
        if(prior.length){
          if(prior[0].requestDigest!==requestDigest)d.deny('REQUEST_ID_COLLISION');
          return deliver(prior[0]);
        }
      }
      if(action==='auditHealth') {
        d.keys(input,['propertyId']);
        await this.property(tx,input.propertyId,actor);
        const events=await tx.list('zp_domain_events',{},10001);
        if(events.length>10000)d.deny('AUDIT_VERIFICATION_LIMIT');
        events.sort((a,b)=>Number(a.sequence)-Number(b.sequence));
        return d.verifyEvents(events,head);
      }
      businessFailureEligible=true;
      if(!Object.hasOwn(d.REASONS,input.reasonCode))d.deny('INVALID_REASON_CODE');
      let result,previous=null;
      let entityCollection=action.includes('Tenancy')?'zp_tenancies':'zp_ownership_sets';
      if(['createProperty','createBuilding','createUnit','createOwnerContact','authorizeTenantAccount'].includes(action)) {
        result=await this.context(tx,action,input,actor,authority);
        entityCollection=result._collection;delete result._collection;
      } else if(action==='createDraftTenancy') {
        d.keys(input,['unitId','code','startDate','endDate','term','parties','reasonCode']);
        d.tenancyInput(input);
        const unit=await this.unit(tx,input.unitId,actor);
        const row=await tx.create('zp_tenancies',{unitId:unit.id,code:d.string(input.code,64),status:'open',tenantUserId:null,leaseState:'draft',startDate:input.startDate,endDate:input.endDate||null,version:0,draftRevision:1});
        await this.proposals(tx,row,input,1,actor);
        result={id:row.id,propertyId:unit.propertyId,leaseState:'draft',version:0};
      } else if(['updateDraftTenancy','activateTenancy','endTenancy'].includes(action)) {
        const allowed=action==='updateDraftTenancy'?['tenancyId','expectedVersion','adoptLegacy','startDate','endDate','term','parties','reasonCode']:action==='endTenancy'?['tenancyId','expectedVersion','endDate','reasonCode']:['tenancyId','expectedVersion','reasonCode'];
        d.keys(input,allowed);
        const row=await tx.get('zp_tenancies',d.id(input.tenancyId));
        if(!row)d.deny('NOT_FOUND');
        const unit=await this.unit(tx,row.unitId,actor);
        previous=this.snapshot('zp_tenancies',row);
        if(input.expectedVersion!==row.version)d.deny('STALE_VERSION');
        let next={version:(row.version===null?0:d.integer(row.version,0,2147483646))+1};
        if(action==='updateDraftTenancy') {
          const adopt=row.leaseState==null&&row.version==null&&input.adoptLegacy===true;
          if(row.leaseState!=='draft'&&!adopt)d.deny('NOT_DRAFT');
          if(!adopt && input.adoptLegacy)d.deny('ALREADY_ADOPTED');
          d.tenancyInput(input);
          const primaryUser=input.parties.find(p=>p.partyRole==='primary').userId;
          if(row.tenantUserId && !d.same(row.tenantUserId,primaryUser))d.deny('PRIMARY_IDENTITY_IMMUTABLE');
          // Existing legacy identity is preserved; new drafts remain unpublished.
          const revision=(row.draftRevision||0)+1;
          Object.assign(next,{leaseState:'draft',startDate:input.startDate,endDate:input.endDate||null,draftRevision:revision});
          await this.proposals(tx,row,input,revision,actor);
        } else if(action==='activateTenancy') {
          if(row.leaseState!=='draft')d.deny('NOT_DRAFT');
          const terms=await tx.list('zp_tenancy_terms',{tenancyId:row.id,revision:row.draftRevision},2);
          const parties=await tx.list('zp_tenancy_parties',{tenancyId:row.id,revision:row.draftRevision},21);
          if(terms.length!==1)d.deny('INVALID_TERMS');
          const pick=(v,keys)=>Object.fromEntries(keys.filter(k=>v[k]!==undefined).map(k=>[k,v[k]]));
          d.tenancyInput({...row,term:pick(terms[0],['effectiveFrom','effectiveTo','currency','rentMinor','depositMinor','rentFrequency','dueDay','prorationPolicy']),parties:parties.map(p=>pick(p,['displayName','userId','partyRole','effectiveFrom','effectiveTo']))});
          await this.accounts(tx,parties,actor);
          const primaryUser=parties.find(p=>p.partyRole==='primary').userId;
          if(row.tenantUserId&&!d.same(row.tenantUserId,primaryUser))d.deny('PRIMARY_IDENTITY_IMMUTABLE');
          if(parties.some(p=>p.userId&&!d.same(p.userId,primaryUser)))d.deny('PARTY_SCOPE_MIGRATION_REQUIRED');
          next.tenantUserId=primaryUser;
          const all=await tx.list('zp_tenancies',{unitId:unit.id},1001);
          if(all.length>1000)d.deny('OCCUPANCY_LIMIT');
          for(const other of all) {
            if(d.same(other.id,row.id))continue;
            if(other.leaseState==null)d.deny('LEGACY_OCCUPANCY_UNQUALIFIED');
            if(['active','ended'].includes(other.leaseState)&&d.overlaps(d.interval(row.startDate,row.endDate),d.interval(other.startDate,other.endDate)))d.deny('OCCUPANCY_OVERLAP');
          }
          next.leaseState='active';
        } else {
          if(row.leaseState!=='active')d.deny('NOT_ACTIVE');
          d.interval(row.startDate,input.endDate);
          if(!input.endDate || (row.endDate && input.endDate>row.endDate))d.deny('END_EXTENSION_FORBIDDEN');
          Object.assign(next,{leaseState:'ended',endDate:input.endDate});
        }
        await tx.update('zp_tenancies',row.id,next);
        result={id:row.id,propertyId:unit.propertyId,leaseState:next.leaseState,version:next.version};
      } else {
        let set;
        if(action==='createOwnershipSet') {
          d.keys(input,['propertyId','effectiveFrom','effectiveTo','reasonCode']);
          const property=await this.property(tx,input.propertyId,actor);
          d.interval(input.effectiveFrom,input.effectiveTo);
          set=await tx.create('zp_ownership_sets',{propertyId:property.id,effectiveFrom:input.effectiveFrom,effectiveTo:input.effectiveTo||null,state:'draft',version:0});
        } else {
          d.keys(input,action==='setOwnershipInterests'?['ownershipSetId','expectedVersion','interests','reasonCode']:['ownershipSetId','expectedVersion','completeSet','reasonCode']);
          set=await tx.get('zp_ownership_sets',d.id(input.ownershipSetId));
          if(!set)d.deny('NOT_FOUND');
          const property=await this.property(tx,set.propertyId,actor);
          previous=this.snapshot('zp_ownership_sets',set);
          if(set.state!=='draft')d.deny('OWNERSHIP_IMMUTABLE');
          if(input.expectedVersion!==set.version)d.deny('STALE_VERSION');
          const nextVersion=d.integer(set.version,0,2147483646)+1;
          if(action==='setOwnershipInterests') {
            d.interestsInput(input.interests);
            for(const value of input.interests) {
              const owner=await tx.get('zp_owner_contacts',value.ownerContactId);
              if(!owner||!d.same(owner.managerUserId,actor))d.deny('OWNER_SCOPE');
              await tx.create('zp_property_interests',{...value,ownershipSetId:set.id,revision:nextVersion});
            }
            await tx.update('zp_ownership_sets',set.id,{version:nextVersion,interestsRevision:nextVersion});
          } else {
            if(input.completeSet!==true)d.deny('COMPLETE_SET_CONFIRMATION');
            const interests=await tx.list('zp_property_interests',{ownershipSetId:set.id,revision:set.interestsRevision},21);
            d.interestsInput(interests.map(v=>({ownerContactId:v.ownerContactId,shareBasisPoints:v.shareBasisPoints})));
            const accountIds=new Set();
            for(const interest of interests) {
              const owner=await tx.get('zp_owner_contacts',interest.ownerContactId);
              if(!owner||!d.same(owner.managerUserId,actor))d.deny('OWNER_SCOPE');
              if(owner.userId) {if(!await tx.get('users',owner.userId))d.deny('OWNER_ACCOUNT_MISSING');accountIds.add(String(owner.userId));}
            }
            if(property.ownerUserId ? accountIds.size!==1||!accountIds.has(String(property.ownerUserId)) : accountIds.size!==0)d.deny('OWNER_SCOPE_MIGRATION_REQUIRED');
            const existing=await tx.list('zp_ownership_sets',{propertyId:set.propertyId,state:'approved'},1001);
            if(existing.length>1000)d.deny('OWNERSHIP_HISTORY_LIMIT');
            for(const other of existing)if(d.overlaps(d.interval(set.effectiveFrom,set.effectiveTo),d.interval(other.effectiveFrom,other.effectiveTo)))d.deny('OWNERSHIP_OVERLAP');
            await tx.update('zp_ownership_sets',set.id,{state:'approved',version:nextVersion});
          }
          set={...set,state:action==='approveOwnershipSet'?'approved':'draft',version:nextVersion};
        }
        result={id:set.id,propertyId:set.propertyId,state:set.state,version:set.version};
      }
      businessFailureEligible=false;
      const sequence=d.integer(Number(head.headSequence),0,2147483646)+1;
      const resulting=this.snapshot(entityCollection,await tx.get(entityCollection,result.id));
      const canonicalPayload=d.canonical({sequence,actorId:String(actor),action,entityId:String(result.id),propertyId:String(result.propertyId),version:result.version,entityCollection,previous,resulting,reasonCode:input.reasonCode,reason:d.REASONS[input.reasonCode],occurredAt:new Date().toISOString(),correlationId:randomUUID(),requestDigest:d.hash(d.canonical(input))});
      const eventHash=d.hash(head.headHash+'\n'+canonicalPayload);
      const event=await tx.create('zp_domain_events',{sequence,previousHash:head.headHash,eventHash,canonicalPayload});
      await tx.create('zp_domain_outbox',{eventId:event.id,topic:'property-tenancy.'+action,payload:canonicalPayload,status:'pending'});
      await tx.update('zp_audit_heads',1,{headSequence:sequence,headHash:eventHash});
      await tx.create('zp_domain_commands',{commandKey:key,actorId:actor,action,requestId,requestDigest,resultJSON:d.canonical(result),eventId:event.id});
      return result;
    }); } catch(error) {
      if(!businessFailureEligible||action==='auditHealth'||error.terminalProof||!TERMINAL_CODES.has(error.code))throw error;
      // The failed business transaction has fully rolled back before this fence begins.
      const receipt=await this.store.transaction(async tx=>{
        const head=await tx.head(true);
        const prior=await tx.list('zp_domain_commands',{commandKey:key},2);
        if(prior.length>1)d.deny('COMMAND_CORRUPT');
        if(prior.length) {
          if(prior[0].requestDigest!==requestDigest)d.deny('REQUEST_ID_COLLISION');
          return prior[0];
        }
        const sequence=d.integer(Number(head.headSequence),0,2147483646)+1;
        const canonicalPayload=d.canonical({sequence,actorId:String(actor),action:'commandRejected',commandAction:action,code:error.code,requestDigest,occurredAt:new Date().toISOString(),correlationId:randomUUID()});
        const eventHash=d.hash(head.headHash+'\n'+canonicalPayload);
        const event=await tx.create('zp_domain_events',{sequence,previousHash:head.headHash,eventHash,canonicalPayload});
        await tx.create('zp_domain_outbox',{eventId:event.id,topic:'property-tenancy.commandRejected',payload:canonicalPayload,status:'suppressed'});
        await tx.update('zp_audit_heads',1,{headSequence:sequence,headHash:eventHash});
        return tx.create('zp_domain_commands',{commandKey:key,actorId:actor,action,requestId,requestDigest,eventId:event.id,resultJSON:d.canonical({commandReceiptVersion:1,outcome:'rejected',code:error.code})});
      });
      return deliver(receipt);
    }
  }

  snapshot(collection,row) {
    const fields={
      zp_tenancies:['id','unitId','tenantUserId','startDate','endDate','draftRevision','version','status'],
      zp_ownership_sets:['id','propertyId','effectiveFrom','effectiveTo','interestsRevision','version'],
      zp_properties:['id','managerUserId','ownerUserId'],
      zp_units:['id','propertyId','buildingId'],
      zp_buildings:['id','propertyId'],
      zp_owner_contacts:['id','managerUserId','userId'],
      zp_tenant_account_permissions:['id','managerUserId','userId','mappingKey']
    }[collection];
    if(!row||!fields)d.deny('AUDIT_SNAPSHOT_UNAVAILABLE');
    const value=Object.fromEntries(fields.map(key=>[key,row[key]??null]));
    value.state=row.leaseState??row.state??'created';
    return value;
  }
  async property(tx,propertyId,actor) {
    const property=await tx.get('zp_properties',d.id(propertyId));
    if(!property||!d.same(property.managerUserId,actor))d.deny('PROPERTY_SCOPE');
    if(property.perRoomLeasing===true)d.deny('PER_ROOM_UNSUPPORTED');
    return property;
  }
  async unit(tx,unitId,actor) {
    const unit=await tx.get('zp_units',d.id(unitId));if(!unit)d.deny('NOT_FOUND');
    await this.property(tx,unit.propertyId,actor);
    if(unit.buildingId) {const building=await tx.get('zp_buildings',unit.buildingId);if(!building||!d.same(building.propertyId,unit.propertyId))d.deny('BUILDING_CONTEXT');}
    return unit;
  }

  async context(tx,action,input,actor,authority) {
    let property,row;
    if(action==='createProperty') {
      d.keys(input,['name','reasonCode']);
      row=await tx.create('zp_properties',{name:d.string(input.name),managerUserId:actor});
      return {id:row.id,propertyId:row.id,state:'created',version:0,_collection:'zp_properties'};
    }
    if(action==='authorizeTenantAccount') {
      d.keys(input,['propertyId','managerUserId','userId','displayName','reasonCode']);
      if(authority.constructor!==true)d.deny('CONSTRUCTOR_REQUIRED');
      property=await tx.get('zp_properties',d.id(input.propertyId));
      if(!property||!d.same(property.managerUserId,d.id(input.managerUserId))||!await tx.get('users',d.id(input.userId)))d.deny('ACCOUNT_CONTEXT');
      const existing=await tx.list('zp_tenant_account_permissions',{managerUserId:input.managerUserId,userId:input.userId},1);
      if(existing.length)d.deny('ACCOUNT_ALREADY_PERMITTED');
      const account=await tx.get('users',d.id(input.userId));
      const displayName=d.string(typeof account.nickname==='string'&&account.nickname.trim()?account.nickname.trim():input.displayName,160);
      row=await tx.create('zp_tenant_account_permissions',{managerUserId:input.managerUserId,userId:input.userId,mappingKey:d.id(input.managerUserId)+':'+d.id(input.userId),displayName});
    } else {
      d.keys(input,action==='createBuilding'?['propertyId','name','reasonCode']:action==='createUnit'?['propertyId','buildingId','name','reasonCode']:['propertyId','displayName','userId','reasonCode']);
      property=await this.property(tx,input.propertyId,actor);
      if(action==='createBuilding')row=await tx.create('zp_buildings',{propertyId:property.id,name:d.string(input.name)});
      if(action==='createUnit') {
        if(input.buildingId) {const building=await tx.get('zp_buildings',d.id(input.buildingId));if(!building||!d.same(building.propertyId,property.id))d.deny('BUILDING_CONTEXT');}
        row=await tx.create('zp_units',{propertyId:property.id,buildingId:input.buildingId||null,name:d.string(input.name)});
      }
      if(action==='createOwnerContact') {
        // Until owner-account scope migration is qualified, only the existing
        // property's owner identity may be attached through this action.
        if(input.userId&&(!property.ownerUserId||!d.same(input.userId,property.ownerUserId)||!await tx.get('users',d.id(input.userId))))d.deny('OWNER_SCOPE_MIGRATION_REQUIRED');
        row=await tx.create('zp_owner_contacts',{displayName:d.string(input.displayName),userId:input.userId||null,managerUserId:actor});
      }
    }
    return {id:row.id,propertyId:property.id,state:'created',version:0,_collection:({createBuilding:'zp_buildings',createUnit:'zp_units',createOwnerContact:'zp_owner_contacts',authorizeTenantAccount:'zp_tenant_account_permissions'})[action]};
  }
  async accounts(tx,parties,actor) {
    for(const party of parties)if(party.userId) {
      const permissions=await tx.list('zp_tenant_account_permissions',{managerUserId:actor,userId:party.userId},2);
      if(permissions.length!==1||!await tx.get('users',party.userId))d.deny('PARTY_ACCOUNT_NOT_PERMITTED');
    }
  }
  async proposals(tx,row,input,revision,actor) {
    await this.accounts(tx,input.parties,actor);
    await tx.create('zp_tenancy_terms',{...input.term,tenancyId:row.id,revision});
    for(const party of input.parties)await tx.create('zp_tenancy_parties',{...party,tenancyId:row.id,revision});
  }
}
module.exports={Service,ACTIONS,ZERO};
