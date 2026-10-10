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
def observe(client,uid):
 form=read(client,uid)
 if form.get('uid')!=uid or form.get('type')!='LoomActionFormModel':raise RuntimeError('Native form identity unavailable')
 tree=Forms(client).read('flow_surfaces_get',{'uid':uid}).get('tree')
 if not isinstance(tree,dict) or tree.get('uid')!=uid:raise RuntimeError('Native model tree identity unavailable')
 settings=tree.get('stepParams',{}).get('loomActionForm',{})
 if settings.get('owner')!='@loom/plugin-action-form' or settings.get('config')!=form.get('config'):raise RuntimeError('Native form and surface readback disagree')
 return {'form':form,'contractHistory':settings.get('contractHistory',[])}
def verified(plan,after):
 args=plan['arguments']
 if after['form']['config']!=args['config']:return False
 history=after['contractHistory']
 if not isinstance(history,list) or not history:return False
 entry=history[-1]
 return entry.get('configDigest')==args['expectedConfigDigest'] and entry.get('oldPins')==args['expectedOldPins'] and entry.get('newPins')=={key:args['config'][key] for key in PINS} and entry.get('reviewDigest')==args['compatibilityProof']['reviewDigest'] and entry.get('reason')==args['compatibilityProof']['reason']
def apply(client,plan,journal):
 args=plan['arguments'];uid=args['uid']
 if read(client,uid)!=plan['before']:raise RuntimeError('Form drift before migration')
 return dispatch_once(client,tool(client,'migrate_contract'),{'requestBody':args},pathlib.Path(journal),plan['before'],lambda:observe(client,uid),lambda after:verified(plan,after))
def main():
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['prepare','apply','verify']);p.add_argument('--runtime',required=True);p.add_argument('--uid');p.add_argument('--review-digest');p.add_argument('--plan',required=True);p.add_argument('--plan-digest');p.add_argument('--journal');p.add_argument('--receipt');a=p.parse_args();client=Loom(a.runtime);path=pathlib.Path(a.plan)
 if a.phase=='prepare':sync_write(path,candidate(client,a.uid,a.review_digest),True)
 else:
  plan=json.loads(path.read_text())
  if sha(plan)!=a.plan_digest:raise RuntimeError('Reviewed plan digest required')
  if a.phase=='verify':
   if not a.receipt:raise RuntimeError('New read-only receipt required')
   after=observe(client,plan['arguments']['uid'])
   if not verified(plan,after):raise RuntimeError('Native migration history mismatch')
   sync_write(pathlib.Path(a.receipt),{'state':'native-readback-verified-no-replay','planDigest':sha(plan),'after':after},True)
  else:
   if not a.journal:raise RuntimeError('New journal required')
   apply(client,plan,a.journal)
if __name__=='__main__':main()
