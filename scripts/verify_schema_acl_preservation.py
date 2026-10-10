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
def semantic(v):
 if isinstance(v,dict):return {k:semantic(x) for k,x in v.items() if k not in ('createdAt','updatedAt')}
 if isinstance(v,list):return [semantic(x) for x in v]
 return v
def tool(c,stem):
 matches=[name for name in c.by_name if re.fullmatch('loom_native_'+re.escape(stem)+'_[a-f0-9]+',name)]
 if len(matches)!=1:raise RuntimeError('Missing or ambiguous discovered operation: '+stem)
 return matches[0]
def call(c,stem,args=None):return unwrap(c.call(tool(c,stem),args or {}))
def denied(c,stem,args,code):
 try:call(c,stem,args)
 except RuntimeError as error:
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
  effective=call(self.c,'roles_check')
  if effective.get('allowAll') is not True:raise RuntimeError('Constructor effective role not qualified')
  inspect=call(self.c,'loom_schema_authoring_inspect',TARGET)
  fields=call(self.c,'collections_fields_list',{'collectionName':TARGET['collection'],'filter':{'name':TARGET['name']},'paginate':False})
  if not isinstance(fields,list) or len(fields)>1:raise RuntimeError('Unexpected field inventory')
  fk=call(self.c,'collections_fields_get',{'collectionName':TARGET['target'],'filterByTk':TARGET['foreignKey']})
  belongs=call(self.c,'collections_fields_get',{'collectionName':'zp_units','filterByTk':'building'})
  return {'target':TARGET,'inspect':inspect,'field':fields[0] if fields else None,'foreignKey':fk,'belongsTo':belongs,'roles':semantic({r:self.roles.snapshot(r) for r in [ROLE,*PORTALS]})}
 def negatives(self,before,manager,scoped=None):
  if self.capture()!=before:raise RuntimeError('Baseline drift')
  role=call(manager,'roles_check')
  if role.get('role')!=ROLE or role.get('allowAll') is not False:raise RuntimeError('Manager bridge not qualified')
  cases=[denied(manager,'loom_schema_authoring_inspect',TARGET,'CONSTRUCTOR_REQUIRED')]
  stale='0'*64 if before['inspect']['aclDigest']!='0'*64 else '1'*64
  cases.append(denied(self.c,'loom_schema_authoring_create_has_many',{'requestBody':{**TARGET,'expectedAclDigest':stale}},'ACL_BASELINE_CHANGED'))
  if scoped:
   role=call(scoped,'roles_check')
   if role.get('allowAll') is not False:raise RuntimeError('Scoped constructor fixture not qualified')
   cases.append(denied(scoped,'loom_schema_authoring_inspect',TARGET,'CONSTRUCTOR_REQUIRED'))
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
