#!/usr/bin/env python3
"""One observed rollback preview with bounded concurrent native role GETs."""
import argparse,contextlib,concurrent.futures,json,pathlib,time,types
from loom_mcp import Loom
from verify_property_commands import role_client,unwrap
from verify_schema_acl_preservation import Acceptance,TARGET,native_acl_denial
from property_ui_journal import sha,sync_write,dispatch_once
DESCRIPTION='Execute one bounded five-second rollback preview and observe overlapping native reads; not read-only'
ARGS={'resource':'zp_buildings','filterByTk':'1','fields':['id','name']}
CASES=[(role+'.'+str(graph),role,graph,'record' if role=='zp_property_manager' and graph==1 else 'scoped-null' if role=='zp_property_manager' else 'denied') for role in ['zp_property_manager','zp_owner','zp_tenant','zp_vendor'] for graph in [1,2]]
def preview_tool(c):
 matches=[(n,t) for n,t in c.by_name.items() if n.startswith('loom_native_loom_schema_authoring_preview_') and t.get('description')==DESCRIPTION]
 if len(matches)!=1:raise RuntimeError('Observed preview unavailable or ambiguous')
 name,tool=matches[0];schema=tool.get('inputSchema',{});body=schema.get('properties',{}).get('requestBody',{})
 if schema.get('required')!=['requestBody'] or body.get('additionalProperties') is not False or set(body.get('required',[]))!=set(TARGET)|{'expectedAclDigest'} or set(body.get('properties',{}))!=set(TARGET)|{'expectedAclDigest'}:
  raise RuntimeError('Unqualified observed-preview schema')
 return name
def classify(value):
 value=unwrap(value)
 if value is None:return 'scoped-null'
 if isinstance(value,dict) and value.get('id')==1 and set(value)<={'id','name'}:return 'record'
 raise RuntimeError('Unexpected native record shape')
def link_samples(observation,results,actors):
 if observation.get('captureQualified') is not True or observation.get('invalidSamples')!=0:raise RuntimeError('Native capture not qualified')
 start,end=int(observation['startNs']),int(observation['endNs'])
 if end-start!=5_000_000_000:raise RuntimeError('Wrong native interval')
 argument=sha({'filterByTk':'1','fields':['id','name']})
 linked=[]
 for alias,role,graph,expected in CASES:
  rows=[r for r in results if r['alias']==alias]
  if len(rows)!=6 or any(r['outcome']!=expected for r in rows):raise RuntimeError('Role HTTP result mismatch')
  samples=[s for s in observation['samples'] if s['roleDigest']==sha({'role':role}) and s['actorDigest']==sha({'actor':str(actors[alias])}) and s['resource']=='zp_buildings' and s['action']=='get' and s['argumentDigest']==argument and s['outcome']==expected and s['status']==(403 if expected=='denied' else 200) and start<=int(s['startNs'])<=int(s['endNs'])<=end]
  if not samples:raise RuntimeError('No matching in-window native role sample')
  linked.append({'alias':alias,'role':role,'expected':expected,'matchingSamples':len(samples),'accountSpecificOverlap':True})
 return linked
def run(root,path,ports):
 path=pathlib.Path(path);path.mkdir(mode=0o700,parents=True,exist_ok=False)
 if len(ports)!=8 or len(set(ports))!=8 or any(p<1024 or p>65535 for p in ports):raise RuntimeError('Eight distinct reserved role-bridge ports required')
 actors={alias:value['id'] for alias,value in json.loads((root.runtime/'maintenance-test-accounts.json').read_text()).items()}
 before=Acceptance(root).capture();sync_write(path/'before.json',before,True)
 tool=preview_tool(root);q=types.SimpleNamespace(path=path)
 with contextlib.ExitStack() as stack:
  clients=[stack.enter_context(role_client(root,q,alias,role,str(graph),port)) for (alias,role,graph,_),port in zip(CASES,ports)]
  if Acceptance(root).capture()!=before:raise RuntimeError('Baseline changed while bridges initialized')
  def reads(case,c):
   alias,role,graph,expected=case;name=next(n for n in c.by_name if n.startswith('loom_native_resource_get_'));out=[]
   for attempt in range(6):
    time.sleep(.6)
    try:
     response=c.call(name,ARGS);outcome=classify(response)
     sync_write(path/(alias+'-'+str(attempt)+'.json'),{'response':response},True)
    except RuntimeError as error:
     sync_write(path/(alias+'-'+str(attempt)+'.json'),{'error':str(error)},True)
     if not native_acl_denial(error):raise
     outcome='denied'
    if outcome!=expected:raise RuntimeError('Unexpected role read outcome')
    out.append({'alias':alias,'attempt':attempt,'outcome':outcome})
   return out
  def preview():
   return dispatch_once(root,tool,{'requestBody':{**TARGET,'expectedAclDigest':before['inspect']['aclDigest']}},path/'preview.json',before,lambda:Acceptance(root).capture(),lambda after:after==before)
  with concurrent.futures.ThreadPoolExecutor(max_workers=9) as pool:
   write=pool.submit(preview);read_futures=[pool.submit(reads,case,c) for case,c in zip(CASES,clients)]
   results=[row for future in read_futures for row in future.result()]
   receipt=write.result()
  response=unwrap(receipt['response'])
  if not response.get('rolledBack') or not response.get('fieldAbsent'):raise RuntimeError('Preview rollback not verified')
  linked=link_samples(response.get('httpObservation',{}),results,actors)
  final={'readChecks':len(results),'linked':linked,'baselineUnchanged':receipt['after']==before,'roleLevelOverlap':True,'accountSpecificOverlap':True,'appAcceptance':False}
  sync_write(path/'result.json',final,True);return final
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--journal',required=True);p.add_argument('--ports',required=True)
 a=p.parse_args();print(json.dumps(run(Loom(a.runtime),a.journal,[int(x) for x in a.ports.split(',')])))
