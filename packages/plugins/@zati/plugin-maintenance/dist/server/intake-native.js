'use strict';
const {IntakeService,ACTIONS,fail}=require('./intake');
const RECEIPTS='zp_maintenance_commands';
const ownedTransactions=new WeakSet();
const plain=x=>x?.toJSON?x.toJSON():x;
function effectiveRole(ctx){
 const roles=Array.isArray(ctx.state.currentRoles)?ctx.state.currentRoles:[ctx.state.currentRole].filter(Boolean);
 if(!ctx.state.currentUser?.id)ctx.throw(401,'Authentication required.');
 if(roles.length!==1||typeof roles[0]!=='string')ctx.throw(403,'One effective role is required.');
 return roles[0];
}
function permitted(plugin,ctx,action){
 const role=effectiveRole(ctx);
 if(!plugin.app.acl.can({role,resource:'zpMaintenance',action}))ctx.throw(403,'No permissions');
 return ctx.state.currentUser.id;
}
function nativeStore(db){
 const model=name=>{const m=db.getCollection(name)?.model;if(!m)fail('SCHEMA_UNAVAILABLE');return m;};
 const methods=transaction=>({
  get:async(name,id)=>plain(await model(name).findByPk(id,{transaction,lock:transaction?.LOCK.UPDATE})),
  commands:async key=>(await model(RECEIPTS).findAll({where:{commandKey:key},transaction})).map(plain),
  createCommand:async values=>plain(await model(RECEIPTS).create(values,{transaction})),
  createRequest:async values=>plain(await model('zp_maintenance_requests').create(values,{transaction})),
  createOrder:async values=>plain(await model('zp_work_orders').create(values,{transaction})),
  markTriaged:async id=>{const row=await model('zp_maintenance_requests').findByPk(id,{transaction,lock:transaction.LOCK.UPDATE});await row.update({status:'triaged'},{transaction});},
  update:async(name,id,values)=>{const row=await model(name).findByPk(id,{transaction,lock:transaction.LOCK.UPDATE});if(!row)fail('CONTEXT_MISMATCH');return plain(await row.update(values,{transaction}));},
  workOrders:async requestId=>(await model('zp_work_orders').findAll({where:{requestId},transaction,lock:transaction.LOCK.UPDATE})).map(plain),
  attachments:async requestId=>{
   const request=await model('zp_maintenance_requests').findByPk(requestId,{transaction,lock:transaction.LOCK.UPDATE});
   if(typeof request?.getAttachments!=='function')fail('SCHEMA_UNAVAILABLE');
   return (await request.getAttachments({transaction})).map(plain);
  },
  linkAttachments:async(orderId,ids)=>{
   const order=await model('zp_work_orders').findByPk(orderId,{transaction});
   if(typeof order?.setAttachments!=='function')fail('SCHEMA_UNAVAILABLE');
   await order.setAttachments(ids,{transaction});
  }
 });
 return {
  lookup:async key=>(await model(RECEIPTS).findAll({where:{commandKey:key}})).map(plain),
  transaction:async(actor,fn)=>db.sequelize.transaction(async transaction=>{
   ownedTransactions.add(transaction);
   try{
    const user=await model('users').findByPk(actor,{transaction,lock:transaction.LOCK.UPDATE});
    if(!user)fail('PROPERTY_DENIED');
    return await fn(methods(transaction));
   }finally{ownedTransactions.delete(transaction);}
  })
 };
}
function protect(db){
 const guard=(_row,options={})=>{if(!options.transaction||!ownedTransactions.has(options.transaction))fail('DOMAIN_ACTION_REQUIRED');};
 const bulk=options=>guard(null,options);
 for(const event of ['beforeCreate','beforeUpdate','beforeSave','beforeDestroy'])db.on(RECEIPTS+'.'+event,guard);
 for(const event of ['beforeBulkCreate','beforeBulkUpdate','beforeBulkDestroy'])db.on(RECEIPTS+'.'+event,event==='beforeBulkCreate'?guard:bulk);
 for(const table of ['zp_maintenance_requests','zp_work_orders'])db.on(table+'.beforeCreate',guard);
 db.on('zp_maintenance_requests.afterSaveWithAssociations',async(row,options={})=>{
  if(ownedTransactions.has(options.transaction))return;
  const actor=options.context?.state?.currentUser?.id;
  if(typeof row.getAttachments!=='function')fail('SCHEMA_UNAVAILABLE');
  const files=await row.getAttachments({transaction:options.transaction});
  if(files.length&&(!actor||files.some(file=>String(plain(file).createdById)!==String(actor))))fail('ATTACHMENT_DENIED');
 });
}
function register(plugin){
 const service=new IntakeService(nativeStore(plugin.db));
 plugin.app.resourceManager.define({name:'zpMaintenance',actions:{
  ...Object.fromEntries(ACTIONS.map(action=>[action,async(ctx,next)=>{
   const actor=permitted(plugin,ctx,action);
   try{ctx.body=await service.execute(action,ctx.action.params.values||{},actor);}catch(error){writeError(ctx,error);}
   await next();
  }])),
  reconcileCommand:async(ctx,next)=>{
   const params=ctx.action.params||{},action=params.commandAction;
   if(!ACTIONS.includes(action))ctx.throw(422,'Unknown maintenance command.');
   const actor=permitted(plugin,ctx,action);
   if(!plugin.app.acl.can({role:effectiveRole(ctx),resource:'zpMaintenance',action:'reconcileCommand'}))ctx.throw(403,'No permissions');
   try{ctx.body=await service.reconcile(actor,action,params.requestId);}catch(error){writeError(ctx,error);}
   await next();
  }
 }});
 plugin.app.acl.registerSnippet({name:'pm.@zati/plugin-maintenance.manager',actions:['zpMaintenance:createRequest','zpMaintenance:convertRequest','zpMaintenance:reconcileCommand']});
 plugin.app.acl.registerSnippet({name:'pm.@zati/plugin-maintenance.constructor',actions:['zpMaintenance:createRequest','zpMaintenance:convertRequest','zpMaintenance:reconcileCommand']});
 plugin.app.getPlugin('api-doc').swagger.add('@zati/plugin-maintenance',require('../swagger/index.json'));
 protect(plugin.db);
 return service;
}
function writeError(ctx,error){
 const known=Object.prototype.hasOwnProperty.call(require('./intake').messages,error?.code);
 ctx.status=known?(error.status||422):503;
 ctx.body={code:known?error.code:'ZP_MAINTENANCE_COMMAND_UNAVAILABLE',message:known?error.message:'The command could not be confirmed. Check its saved result before retrying.',...(known&&error.terminalProof?{terminalProof:error.terminalProof}:{})};
}
module.exports={register,nativeStore,protect,effectiveRole,permitted,writeError,ownedTransactions};
