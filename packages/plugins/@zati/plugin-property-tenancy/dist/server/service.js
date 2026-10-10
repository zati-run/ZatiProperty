'use strict';
const d=require('./domain');
const {randomUUID}=require('node:crypto');
const ACTIONS=['createDraftTenancy','updateDraftTenancy','activateTenancy','endTenancy','createOwnershipSet','setOwnershipInterests','approveOwnershipSet','auditHealth'];
const ZERO='0'.repeat(64);
class Service {
  constructor(store) {this.store=store;}
  async execute(action,input,actor) {
    if(!ACTIONS.includes(action))d.deny('UNKNOWN_ACTION');
    d.id(actor);
    return this.store.transaction(async tx=>{
      // One lock order across every domain mutation; head serializes audit ordering.
      const head=await tx.head();
      if(action==='auditHealth') {
        d.keys(input,['propertyId']);
        await this.property(tx,input.propertyId,actor);
        const events=await tx.list('zp_domain_events',{},10001);
        if(events.length>10000)d.deny('AUDIT_VERIFICATION_LIMIT');
        events.sort((a,b)=>Number(a.sequence)-Number(b.sequence));
        return d.verifyEvents(events,head);
      }
      d.string(input.reason,240);
      let result;
      if(action==='createDraftTenancy') {
        d.keys(input,['unitId','code','startDate','endDate','term','parties','reason']);
        d.tenancyInput(input);
        const unit=await this.unit(tx,input.unitId,actor);
        const row=await tx.create('zp_tenancies',{unitId:unit.id,code:d.string(input.code,64),status:'open',tenantUserId:input.parties.find(p=>p.partyRole==='primary').userId,leaseState:'draft',startDate:input.startDate,endDate:input.endDate||null,version:0,draftRevision:1});
        await this.proposals(tx,row,input,1);
        result={id:row.id,propertyId:unit.propertyId,leaseState:'draft',version:0};
      } else if(['updateDraftTenancy','activateTenancy','endTenancy'].includes(action)) {
        const allowed=action==='updateDraftTenancy'?['tenancyId','expectedVersion','adoptLegacy','startDate','endDate','term','parties','reason']:action==='endTenancy'?['tenancyId','expectedVersion','endDate','reason']:['tenancyId','expectedVersion','reason'];
        d.keys(input,allowed);
        const row=await tx.get('zp_tenancies',d.id(input.tenancyId));
        if(!row)d.deny('NOT_FOUND');
        const unit=await this.unit(tx,row.unitId,actor);
        if(input.expectedVersion!==row.version)d.deny('STALE_VERSION');
        let next={version:(row.version===null?0:d.integer(row.version,0,2147483646))+1};
        if(action==='updateDraftTenancy') {
          const adopt=row.leaseState==null&&row.version==null&&input.adoptLegacy===true;
          if(row.leaseState!=='draft'&&!adopt)d.deny('NOT_DRAFT');
          if(!adopt && input.adoptLegacy)d.deny('ALREADY_ADOPTED');
          d.tenancyInput(input);
          const primaryUser=input.parties.find(p=>p.partyRole==='primary').userId;
          if(row.tenantUserId && !d.same(row.tenantUserId,primaryUser))d.deny('PRIMARY_IDENTITY_IMMUTABLE');
          next.tenantUserId=primaryUser;
          const revision=(row.draftRevision||0)+1;
          Object.assign(next,{leaseState:'draft',startDate:input.startDate,endDate:input.endDate||null,draftRevision:revision});
          await this.proposals(tx,row,input,revision);
        } else if(action==='activateTenancy') {
          if(row.leaseState!=='draft')d.deny('NOT_DRAFT');
          const terms=await tx.list('zp_tenancy_terms',{tenancyId:row.id,revision:row.draftRevision},2);
          const parties=await tx.list('zp_tenancy_parties',{tenancyId:row.id,revision:row.draftRevision},21);
          if(terms.length!==1)d.deny('INVALID_TERMS');
          const pick=(v,keys)=>Object.fromEntries(keys.filter(k=>v[k]!==undefined).map(k=>[k,v[k]]));
          d.tenancyInput({...row,term:pick(terms[0],['effectiveFrom','effectiveTo','currency','rentMinor','depositMinor','rentFrequency','dueDay','prorationPolicy']),parties:parties.map(p=>pick(p,['displayName','userId','partyRole','effectiveFrom','effectiveTo']))});
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
          d.keys(input,['propertyId','effectiveFrom','effectiveTo','reason']);
          const property=await this.property(tx,input.propertyId,actor);
          d.interval(input.effectiveFrom,input.effectiveTo);
          set=await tx.create('zp_ownership_sets',{propertyId:property.id,effectiveFrom:input.effectiveFrom,effectiveTo:input.effectiveTo||null,state:'draft',version:0});
        } else {
          d.keys(input,action==='setOwnershipInterests'?['ownershipSetId','expectedVersion','interests','reason']:['ownershipSetId','expectedVersion','completeSet','reason']);
          set=await tx.get('zp_ownership_sets',d.id(input.ownershipSetId));
          if(!set)d.deny('NOT_FOUND');
          await this.property(tx,set.propertyId,actor);
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
            const existing=await tx.list('zp_ownership_sets',{propertyId:set.propertyId,state:'approved'},1001);
            if(existing.length>1000)d.deny('OWNERSHIP_HISTORY_LIMIT');
            for(const other of existing)if(d.overlaps(d.interval(set.effectiveFrom,set.effectiveTo),d.interval(other.effectiveFrom,other.effectiveTo)))d.deny('OWNERSHIP_OVERLAP');
            await tx.update('zp_ownership_sets',set.id,{state:'approved',version:nextVersion});
          }
          set={...set,state:action==='approveOwnershipSet'?'approved':'draft',version:nextVersion};
        }
        result={id:set.id,propertyId:set.propertyId,state:set.state,version:set.version};
      }
      const sequence=d.integer(Number(head.headSequence),0,2147483646)+1;
      const canonicalPayload=d.canonical({sequence,actorId:String(actor),action,entityId:String(result.id),propertyId:String(result.propertyId),version:result.version,state:result.leaseState||result.state,occurredAt:new Date().toISOString(),correlationId:randomUUID(),reasonDigest:d.hash(input.reason),requestDigest:d.hash(d.canonical(input))});
      const eventHash=d.hash(head.headHash+'\n'+canonicalPayload);
      const event=await tx.create('zp_domain_events',{sequence,previousHash:head.headHash,eventHash,canonicalPayload});
      await tx.create('zp_domain_outbox',{eventId:event.id,topic:'property-tenancy.'+action,payload:canonicalPayload,status:'pending'});
      await tx.update('zp_audit_heads',1,{headSequence:sequence,headHash:eventHash});
      return result;
    });
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
  async proposals(tx,row,input,revision) {
    for(const party of input.parties)if(party.userId&&!await tx.get('users',party.userId))d.deny('PARTY_USER_MISSING');
    await tx.create('zp_tenancy_terms',{...input.term,tenancyId:row.id,revision});
    for(const party of input.parties)await tx.create('zp_tenancy_parties',{...party,tenancyId:row.id,revision});
  }
}
module.exports={Service,ACTIONS,ZERO};
