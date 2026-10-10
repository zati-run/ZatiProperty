#!/usr/bin/env python3
"""Reviewed 0.1.3→0.1.4 action contract migration through typed Loom only."""
import argparse,copy,json,pathlib,re
from loom_mcp import Loom
from apply_protected_forms import Forms
def tool(client,action):return Forms(client).tool("loom_action_forms_"+action)
def read(client,uid):return Forms(client).get(uid)
def call(client,action,args):return Forms(client).read("loom_action_forms_"+action,args)
from property_ui_journal import sha,sync_write,dispatch_once
PINS=('packageVersion','implementationDigest','schemaDigest','commandContract')
def candidate(client,uid,review_digest):
 if not re.fullmatch('[a-f0-9]{64}',review_digest):raise RuntimeError('Review digest required')
 before=read(client,uid);old=before['config']
 if old['actionPackage']!='@zati/plugin-property-tenancy' or old['resource']!='zpPropertyTenancy' or old['packageVersion']!='0.1.3' or old['commandContract']!='idempotent-terminal-v1':raise RuntimeError('Unqualified old contract')
 if old.get('prefill'):raise RuntimeError('Existing baseline forms only')
 describe=call(client,'describe',{k:old[k] for k in ('actionPackage','resource','action','reconcileAction')})
 if describe['packageVersion']!='0.1.4' or describe['schemaDigest']!=old['schemaDigest'] or describe['commandContract']!=old['commandContract']:raise RuntimeError('Non-equivalent new contract')
 config=copy.deepcopy(old)
 for key in ('packageVersion','implementationDigest'):config[key]=describe[key]
 args={'uid':uid,'expectedNodeHash':before['nodeHash'],'expectedConfigDigest':sha(old),'expectedOldPins':{key:old[key] for key in PINS},'config':config,'compatibilityProof':{'reviewDigest':review_digest,'reason':'equivalent-command-schema-response-envelope-correction'}}
 return {'before':before,'arguments':args,'oldIntentPolicy':'reconcile-only; old prepare and submit remain fenced'}
def apply(client,plan,journal):
 args=plan['arguments'];uid=args['uid']
 if read(client,uid)!=plan['before']:raise RuntimeError('Form drift before migration')
 def verify(after):
  if after['config']!=args['config']:return False
  history=after['node']['stepParams']['loomActionForm'].get('contractHistory',[])
  return bool(history) and history[-1]['configDigest']==args['expectedConfigDigest'] and history[-1]['reviewDigest']==args['compatibilityProof']['reviewDigest']
 return dispatch_once(client,tool(client,'migrate_contract'),{'requestBody':args},pathlib.Path(journal),plan['before'],lambda:read(client,uid),verify)
def main():
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['prepare','apply']);p.add_argument('--runtime',required=True);p.add_argument('--uid');p.add_argument('--review-digest');p.add_argument('--plan',required=True);p.add_argument('--plan-digest');p.add_argument('--journal');a=p.parse_args();client=Loom(a.runtime);path=pathlib.Path(a.plan)
 if a.phase=='prepare':sync_write(path,candidate(client,a.uid,a.review_digest),True)
 else:
  plan=json.loads(path.read_text())
  if sha(plan)!=a.plan_digest or not a.journal:raise RuntimeError('Reviewed plan digest and new journal required')
  apply(client,plan,a.journal)
if __name__=='__main__':main()
