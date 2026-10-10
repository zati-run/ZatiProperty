'use strict';
const {Plugin}=require('@nocobase/server');
const {Service,ACTIONS,ZERO}=require('./service');
const {deny}=require('./domain');
const PROTECTED=['zp_tenancies','zp_tenancy_terms','zp_tenancy_parties','zp_ownership_sets','zp_property_interests','zp_domain_events','zp_audit_heads','zp_domain_outbox','zp_properties','zp_units','zp_buildings','zp_owner_contacts','zp_tenant_account_permissions'];
const plain=row=>row ? (typeof row.toJSON==='function'?row.toJSON():row) : null;
class PropertyTenancyPlugin extends Plugin {
  async load() {
    const db=this.db;
    const authorized=new WeakSet();
    const model=name=>{const m=db.getModel(name);if(!m)deny('SCHEMA_UNAVAILABLE');return m;};
    const service=new Service({
      transaction:async callback=>db.sequelize.transaction(async transaction=>{
        authorized.add(transaction);
        const options={transaction,lock:transaction.LOCK.UPDATE};
        const store={
          head:async()=>{
            // Unique PK makes initialization races fail/serialize in native DB;
            // no caller-provided head, sequence or hash is accepted.
            let head=await model('zp_audit_heads').findByPk(1,options);
            if(!head)head=await model('zp_audit_heads').create({id:1,headSequence:0,headHash:ZERO},{transaction});
            return plain(head);
          },
          get:async(name,id)=>plain(await model(name).findByPk(id,options)),
          list:async(name,where,limit)=>(await model(name).findAll({...options,where,limit,order:[['id','ASC']]})).map(plain),
          create:async(name,values)=>plain(await model(name).create(values,{transaction})),
          update:async(name,id,values)=>{
            const row=await model(name).findByPk(id,options);if(!row)deny('NOT_FOUND');
            await row.update(values,{transaction});return plain(row);
          }
        };
        try{return await callback(store);}finally{authorized.delete(transaction);}
      })
    });
    const guard=(_row,options)=>{if(!options?.transaction||!authorized.has(options.transaction))deny('DOMAIN_ACTION_REQUIRED');};
    const bulkGuard=options=>{if(!options?.transaction||!authorized.has(options.transaction))deny('DOMAIN_ACTION_REQUIRED');};
    for(const name of PROTECTED) {
      for(const hook of ['beforeCreate','beforeUpdate','beforeDestroy','beforeSave','afterSave'])db.on(name+'.'+hook,guard);
      for(const hook of ['beforeBulkCreate','beforeBulkUpdate','beforeBulkDestroy']) {
        db.on(name+'.'+hook,hook==='beforeBulkCreate'?guard:bulkGuard);
      }
    }
    // Preserve hierarchy/scope references even if a generic update bypasses a UI.
    for(const [name,fields] of Object.entries({zp_properties:['managerUserId','ownerUserId'],zp_units:['propertyId','buildingId'],zp_buildings:['propertyId'],zp_owner_contacts:['userId','managerUserId']})) {
      db.on(name+'.beforeUpdate',(row,options)=>{
        if(fields.some(field=>row.changed(field)))deny('CONTEXT_IMMUTABLE');
      });
      db.on(name+'.beforeBulkUpdate',options=>{
        if(fields.some(field=>Object.hasOwn(options.attributes||{},field)))deny('CONTEXT_IMMUTABLE');
      });
      for(const hook of ['beforeDestroy','beforeBulkDestroy'])db.on(name+'.'+hook,()=>deny('CONTEXT_DELETE_PROTECTED'));
    }
    const actions={};
    for(const action of ACTIONS) {
      actions[action]=async(ctx,next)=>{
        const roles=ctx.state?.currentRoles || (ctx.state?.currentRole ? [ctx.state.currentRole] : []);
        const actor=ctx.state?.currentUser?.id;
        const acl=ctx.acl||this.app.acl;
        if(!actor||!Array.isArray(roles)||roles.length!==1||typeof roles[0]!=='string'||!acl.can({roles,resource:'zpPropertyTenancy',action}))ctx.throw(403,'DOMAIN_ACTION_DENIED');
        try {
          let constructor=false;
          if(action==='authorizeTenantAccount') {
            const role=await model('roles').findByPk(roles[0]);
            constructor=role?.get('allowAll')===true;
          }
          ctx.body={data:await service.execute(action,ctx.action.params.values||{},actor,{constructor})};
        } catch(error) {
          // Only bounded domain codes; never echo SQL, values, credentials or PII.
          const code=typeof error.code==='string'&&/^[A-Z_]{3,64}$/.test(error.code)?error.code:'DOMAIN_OPERATION_FAILED';
          ctx.throw(code==='PROPERTY_SCOPE'?403:409,code);
        }
        await next();
      };
    }
    this.app.resourcer.define({name:'zpPropertyTenancy',type:'single',actions,only:ACTIONS});
    this.app.acl.registerSnippet({name:'pm.'+this.name,actions:ACTIONS.map(action=>'zpPropertyTenancy:'+action)});
  }
}
module.exports=PropertyTenancyPlugin;module.exports.default=PropertyTenancyPlugin;
module.exports.PROTECTED=PROTECTED;
