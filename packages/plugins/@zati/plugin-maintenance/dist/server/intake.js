'use strict';
const crypto=require('node:crypto');
const canonical=v=>JSON.stringify(v,(_,x)=>x&&typeof x==='object'&&!Array.isArray(x)?Object.fromEntries(Object.keys(x).sort().map(k=>[k,x[k]])):x);
const hash=v=>crypto.createHash('sha256').update(canonical(v)).digest('hex');
const ACTIONS=['createRequest','convertRequest'];
const messages={
 DOMAIN_ACTION_REQUIRED:'Use the protected maintenance action.',SCHEMA_UNAVAILABLE:'Maintenance setup is not ready. No changes were saved.',
 INVALID_INPUT:'Check the request details and try again.',CONTEXT_MISMATCH:'Choose a unit and tenancy belonging to the selected property.',
 PROPERTY_DENIED:'This property is not available to your account.',REQUEST_DENIED:'This request is not available to your account.',
 REQUEST_CLOSED:'This request is closed. Review it before creating work.',REQUEST_ID_COLLISION:'This submission reference was already used for different details. Check the saved result.',
 ATTACHMENT_DENIED:'One or more attachments are not available for this request.',AMBIGUOUS_CONVERSION:'More than one job is linked. Review the existing jobs.',
 COMMAND_CORRUPT:'The saved result could not be verified. Ask an administrator to review it.'
};
function fail(code){const e=Error(messages[code]||'The request could not be saved. Check the saved result before trying again.');e.code=code;e.status=['PROPERTY_DENIED','REQUEST_DENIED','ATTACHMENT_DENIED','DOMAIN_ACTION_REQUIRED'].includes(code)?403:422;throw e;}
const id=v=>{if(!/^[1-9][0-9]{0,15}$/.test(String(v))||!Number.isSafeInteger(Number(v)))fail('INVALID_INPUT');return Number(v);};
const text=(v,max,required=false)=>{if(typeof v!=='string'||v.length>max||(required&&!v.trim()))fail('INVALID_INPUT');return v.trim();};
function payload(action,v){
 const allowed=action==='createRequest'?['propertyId','unitId','tenancyId','title','description','category','priority','preferredTimes','permissionToEnter','petInformation']:['maintenanceRequestId'];
 if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).some(k=>!allowed.includes(k)))fail('INVALID_INPUT');
 if(action==='convertRequest')return {maintenanceRequestId:id(v.maintenanceRequestId)};
 const p={propertyId:id(v.propertyId),title:text(v.title,200,true),description:text(v.description,5000,true),category:text(v.category,80,true),priority:v.priority,preferredTimes:text(v.preferredTimes===undefined?'':v.preferredTimes,500),permissionToEnter:v.permissionToEnter,petInformation:text(v.petInformation===undefined?'':v.petInformation,1000)};
 if(!['plumbing','electrical','appliance','structural','pest','general'].includes(p.category)||!['low','medium','high','urgent'].includes(p.priority)||typeof p.permissionToEnter!=='boolean')fail('INVALID_INPUT');
 for(const key of ['unitId','tenancyId'])p[key]=v[key]===undefined||v[key]===null?null:id(v[key]);
 if(p.tenancyId&&!p.unitId)fail('CONTEXT_MISMATCH');
 return p;
}
function identity(actor,action,requestId){
 actor=id(actor);
 if(!ACTIONS.includes(action)||typeof requestId!=='string'||! /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(requestId))fail('INVALID_INPUT');
 return {actor,action,requestId,commandKey:hash([actor,action,requestId])};
}
function deliver(row){
 if(row.outcome==='committed')return JSON.parse(row.resultJSON);
 if(row.outcome!=='rejected'||!['INVALID_INPUT','CONTEXT_MISMATCH','REQUEST_CLOSED','AMBIGUOUS_CONVERSION'].includes(row.errorCode))fail('COMMAND_CORRUPT');
 try{fail(row.errorCode);}catch(e){e.terminalProof={outcome:'rejected',requestId:row.requestId,requestDigest:row.requestDigest};throw e;}
}
class IntakeService{
 constructor(store){this.store=store;}
 async reconcile(actor,action,requestId){
  const key=identity(actor,action,requestId),rows=await this.store.lookup(key.commandKey);
  if(rows.length>1)fail('COMMAND_CORRUPT');
  if(!rows.length)return {status:'not_observed',requestId,retryAuthorized:false};
  const row=rows[0];
  if(!['committed','rejected'].includes(row.outcome)||row.commandKey!==key.commandKey||String(row.actorId)!==String(key.actor)||row.action!==action||row.requestId!==requestId||!/^[a-f0-9]{64}$/.test(row.requestDigest)||row.outcome==='rejected'&&!['INVALID_INPUT','CONTEXT_MISMATCH','REQUEST_CLOSED','AMBIGUOUS_CONVERSION'].includes(row.errorCode))fail('COMMAND_CORRUPT');
  return {receiptVersion:1,actorId:String(key.actor),commandAction:action,status:row.outcome,outcome:row.outcome,requestId,requestDigest:row.requestDigest,...(row.outcome==='committed'?{result:JSON.parse(row.resultJSON)}:{code:row.errorCode,message:messages[row.errorCode]})};
 }
 async execute(action,values,actor){
  const {requestId,...input}=values||{},key=identity(actor,action,requestId),digest=hash(input);
  const record=(tx,outcome,result,errorCode)=>tx.createCommand({action:key.action,requestId:key.requestId,commandKey:key.commandKey,actorId:key.actor,requestDigest:digest,outcome,resultJSON:JSON.stringify(result||null),errorCode:errorCode||null});
  const prior=async tx=>{const rows=await tx.commands(key.commandKey);if(rows.length>1)fail('COMMAND_CORRUPT');if(rows.length&&rows[0].requestDigest!==digest)fail('REQUEST_ID_COLLISION');return rows[0];};
  try{
   return await this.store.transaction(key.actor,async tx=>{
    const previous=await prior(tx);if(previous)return deliver(previous);
    const p=payload(action,input);let result;
    if(action==='createRequest'){
     const property=await tx.get('zp_properties',p.propertyId);
     if(!property||Number(property.managerUserId)!==key.actor)fail('PROPERTY_DENIED');
     const unit=p.unitId?await tx.get('zp_units',p.unitId):null,tenancy=p.tenancyId?await tx.get('zp_tenancies',p.tenancyId):null;
     if(p.unitId&&(!unit||Number(unit.propertyId)!==p.propertyId)||p.tenancyId&&(!tenancy||Number(tenancy.unitId)!==p.unitId))fail('CONTEXT_MISMATCH');
     const row=await tx.createRequest({...p,status:'open'});
     result={id:row.id,propertyId:p.propertyId,status:'open'};
    }else{
     const request=await tx.get('zp_maintenance_requests',p.maintenanceRequestId);
     if(!request)fail('REQUEST_DENIED');
     const property=await tx.get('zp_properties',request.propertyId);
     if(!property||Number(property.managerUserId)!==key.actor)fail('REQUEST_DENIED');
     const existing=await tx.workOrders(request.id);
     if(existing.length>1)fail('AMBIGUOUS_CONVERSION');
     if(existing.length)result={id:existing[0].id,requestId:request.id,state:existing[0].state,alreadyConverted:true};
     else{
      if(request.status==='closed')fail('REQUEST_CLOSED');
      const attachments=await tx.attachments(request.id);
      const snapshot=Object.fromEntries(['title','description','category','priority','preferredTimes','permissionToEnter','petInformation','propertyId','unitId','tenancyId'].map(k=>[k,request[k]??null]));
      const row=await tx.createOrder({...snapshot,requestId:request.id,state:'new',vendorId:null,approvalRequired:true,approvalGranted:false,requestSnapshot:JSON.stringify({...snapshot,attachmentIds:attachments.map(a=>a.id)})});
      await tx.linkAttachments(row.id,attachments.map(a=>a.id));
      await tx.markTriaged(request.id);
      result={id:row.id,requestId:request.id,state:'new',alreadyConverted:false};
     }
    }
    await record(tx,'committed',result);return result;
   });
  }catch(error){
   if(error.terminalProof)throw error;
   if(!['INVALID_INPUT','CONTEXT_MISMATCH','REQUEST_CLOSED','AMBIGUOUS_CONVERSION'].includes(error.code))throw error;
   return this.store.transaction(key.actor,async tx=>{const previous=await prior(tx);if(previous)return deliver(previous);const row=await record(tx,'rejected',null,error.code);return {rejection:row};}).then(value=>value.rejection?deliver(value.rejection):value);
  }
 }
}
module.exports={IntakeService,ACTIONS,canonical,hash,payload,identity,messages,fail};
