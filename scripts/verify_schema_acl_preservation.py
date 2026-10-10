#!/usr/bin/env python3
"""Bounded Loom-only schema acceptance. Capture first; explicit reviewed apply once."""
import argparse,json,pathlib,re
from loom_mcp import Loom
from apply_property_ui import Apply,ROLE,PORTALS,load_manifest
from property_ui_journal import sha,sync_write,dispatch_once
ROOT=pathlib.Path(__file__).resolve().parents[1]
TARGET={'collection':'zp_buildings','name':'units','target':'zp_units','foreignKey':'buildingId'}
def unwrap(v):
 while isinstance(v,dict) and set(v)=={'data'}:v=v['data']
 return v
def semantic(row):
 # Remove only native row metadata; nested predicates/options are product state.
 if isinstance(row,dict):return {k:v for k,v in row.items() if k not in ('createdAt','updatedAt')}
 return row
def role_snapshot(snapshot):
 result=dict(snapshot)
 for key in ('role','strategy'):result[key]=semantic(snapshot.get(key))
 result['routes']=[semantic(row) for row in snapshot.get('routes',[])]
 result['permissions']=[]
 for resource in snapshot.get('permissions',[]):
  row=semantic(resource)
  if isinstance(row.get('actions'),list):row['actions']=[semantic(action) for action in row['actions']]
  result['permissions'].append(row)
 return result
SCHEMA_OPERATIONS={
 'loom_schema_authoring_create_has_many':('loom_schema_authoring_create_has_ma','Executes POST /loomSchemaAuthoring:createHasMany'),
 'loom_schema_authoring_preview_has_many':('loom_schema_authoring_preview_has_m','Execute bounded schema preview and confirm transactional rollback; not read-only'),
}
def tool(c,stem):
 if stem in SCHEMA_OPERATIONS:
  observed,description=SCHEMA_OPERATIONS[stem];matches=[]
  for name,metadata in c.by_name.items():
   if not re.fullmatch('loom_native_(?:'+re.escape(stem)+'|'+re.escape(observed)+')_[a-f0-9]+',name):continue
   if metadata.get('description')!=description:continue
   schema=metadata.get('inputSchema',{});body=schema.get('properties',{}).get('requestBody',{})
   required={'collection','name','target','foreignKey','expectedAclDigest'}
   if schema.get('type')!='object' or schema.get('required')!=['requestBody'] or body.get('type')!='object' or body.get('additionalProperties') is not False:continue
   if set(body.get('required',[]))!=required or set(body.get('properties',{}))!=required:continue
   if any(body['properties'][key].get('type')!='string' for key in required):continue
   matches.append(name)
 else:matches=[name for name in c.by_name if re.fullmatch('loom_native_'+re.escape(stem)+'_[a-f0-9]+',name)]
 if len(matches)!=1:raise RuntimeError('Missing or ambiguous discovered operation: '+stem)
 return matches[0]
def call(c,stem,args=None):return unwrap(c.call(tool(c,stem),args or {}))
def checked_role(client):
 value=call(client,'roles_check')
 # This native action adds top-level dataSources metadata. Do not broaden
 # generic response unwrapping for unrelated tools or error envelopes.
 if isinstance(value,dict) and set(value)=={'data','meta'}:
  if not isinstance(value['meta'],dict) or set(value['meta'])!={'dataSources'} or not isinstance(value['meta']['dataSources'],dict):
   raise RuntimeError('Unqualified roles_check metadata envelope')
  value=value['data']
 if not isinstance(value,dict) or type(value.get('allowAll')) is not bool:
  raise RuntimeError('Unqualified roles_check authority response')
 role=value.get('role');roles=value.get('roles')
 if not isinstance(role,str) or not role or not isinstance(roles,list) or roles!=[role]:
  raise RuntimeError('Singular effective role not qualified')
 return value
def native_acl_denial(error):
 prefix='Loom tool error: '
 text=str(error)
 if not text.startswith(prefix):return False
 try:
  envelope=json.loads(text[len(prefix):])
  if not isinstance(envelope,dict) or envelope.get('isError') is not True:return False
  content=envelope.get('content')
  if not isinstance(content,list) or len(content)!=1 or not isinstance(content[0],dict) or content[0].get('type')!='text':return False
  packet=json.loads(content[0]['text'])
 except (ValueError,TypeError,KeyError):return False
 return packet=={'statusCode':403,'body':{'errors':[{'message':'No permissions'}]}}
def denied(c,stem,args,code,allow_native_acl=False):
 try:call(c,stem,args)
 except RuntimeError as error:
  if allow_native_acl and code=='CONSTRUCTOR_REQUIRED' and native_acl_denial(error):
   return {'passed':True,'code':'NATIVE_ACL_DENIED','httpStatus':403,'rejectionLayer':'native-acl'}
  prefix='Loom tool error: '
  if not str(error).startswith(prefix):raise RuntimeError('Uncertain rejection; inspect private native result') from None
  envelope=json.loads(str(error)[len(prefix):]);texts=[x.get('text','') for x in envelope.get('content',[]) if x.get('type')=='text']
  if len(texts)!=1:raise RuntimeError('Unqualified native rejection shape') from None
  response=json.loads(texts[0]);errors=response.get('body',{}).get('errors',[])
  if response.get('statusCode') not in (403,409) or not any(x.get('code')==code for x in errors):raise RuntimeError('Expected native denial code not established') from None
  return {'passed':True,'code':code,'httpStatus':response['statusCode']}
 raise RuntimeError('Unexpected success; stop without retry')
class Acceptance:
 def __init__(self,client):
  self.c=client;manifest=load_manifest();self.roles=Apply(client,{},manifest,None)
 def capture(self):
  effective=checked_role(self.c)
  if effective.get('allowAll') is not True:raise RuntimeError('Constructor effective role not qualified')
  inspect=call(self.c,'loom_schema_authoring_inspect',TARGET)
  fields=call(self.c,'collections_fields_list',{'collectionName':TARGET['collection'],'filter':{'name':TARGET['name']},'paginate':False})
  if not isinstance(fields,list) or len(fields)>1:raise RuntimeError('Unexpected field inventory')
  fk=call(self.c,'collections_fields_get',{'collectionName':TARGET['target'],'filterByTk':TARGET['foreignKey']})
  belongs=call(self.c,'collections_fields_get',{'collectionName':'zp_units','filterByTk':'building'})
  return {'target':TARGET,'inspect':inspect,'field':fields[0] if fields else None,'foreignKey':fk,'belongsTo':belongs,'roles':{r:role_snapshot(self.roles.snapshot(r)) for r in [ROLE,*PORTALS]}}
 def negatives(self,before,manager,scoped=None):
  if self.capture()!=before:raise RuntimeError('Baseline drift')
  role=checked_role(manager)
  if role.get('role')!=ROLE or role.get('allowAll') is not False:raise RuntimeError('Manager bridge not qualified')
  cases=[denied(manager,'loom_schema_authoring_inspect',TARGET,'CONSTRUCTOR_REQUIRED',allow_native_acl=True)]
  stale='0'*64 if before['inspect']['aclDigest']!='0'*64 else '1'*64
  cases.append(denied(manager,'loom_schema_authoring_create_has_many',{'requestBody':{**TARGET,'expectedAclDigest':stale}},'CONSTRUCTOR_REQUIRED',allow_native_acl=True))
  cases.append(denied(self.c,'loom_schema_authoring_create_has_many',{'requestBody':{**TARGET,'expectedAclDigest':stale}},'ACL_BASELINE_CHANGED'))
  if scoped:
   role=checked_role(scoped)
   if role.get('allowAll') is not False:raise RuntimeError('Scoped constructor fixture not qualified')
   cases.append(denied(scoped,'loom_schema_authoring_inspect',TARGET,'CONSTRUCTOR_REQUIRED',allow_native_acl=True))
  if self.capture()!=before:raise RuntimeError('Negative checks changed baseline')
  return {'cases':cases,'scopedConstructorGate':'denial-observed-fixture-scope-proof-required' if scoped else 'blocked-no-qualified-role-fixture','runtimeConcurrencyGate':'unverified'}
 def apply(self,before,journal):
  if before['field'] is not None or before['inspect'].get('field') is not None:raise RuntimeError('Target already exists; never replay schema creation')
  if self.capture()!=before:raise RuntimeError('Baseline drift')
  def verify(after):
   field=after['field'] or {}
   if any(field.get(k)!=v for k,v in {'name':'units','type':'hasMany','target':'zp_units','foreignKey':'buildingId','sourceKey':'id','targetKey':'id'}.items()):return False
   return after['inspect']['aclDigest']==before['inspect']['aclDigest'] and all(after[k]==before[k] for k in ['foreignKey','belongsTo','roles'])
  return dispatch_once(self.c,tool(self.c,'loom_schema_authoring_create_has_many'),{'requestBody':{**TARGET,'expectedAclDigest':before['inspect']['aclDigest']}},pathlib.Path(journal),before,self.capture,verify)
def main():
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['capture','negatives','apply']);p.add_argument('--runtime',required=True);p.add_argument('--baseline',required=True);p.add_argument('--reviewed-baseline-digest');p.add_argument('--manager-runtime');p.add_argument('--scoped-runtime');p.add_argument('--journal');p.add_argument('--receipt');a=p.parse_args();api=Acceptance(Loom(a.runtime));path=pathlib.Path(a.baseline)
 if a.phase=='capture':sync_write(path,api.capture(),True);return
 before=json.loads(path.read_text())
 if sha(before)!=a.reviewed_baseline_digest:raise RuntimeError('Exact independently reviewed baseline digest required')
 if a.phase=='negatives':
  if not a.manager_runtime or not a.receipt:raise RuntimeError('Manager bridge and new receipt required')
  sync_write(pathlib.Path(a.receipt),api.negatives(before,Loom(a.manager_runtime),Loom(a.scoped_runtime) if a.scoped_runtime else None),True)
 else:
  if not a.journal:raise RuntimeError('Durable no-replay journal required')
  api.apply(before,a.journal)
if __name__=='__main__':main()
