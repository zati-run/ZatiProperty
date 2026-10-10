#!/usr/bin/env python3
"""Reviewed, one-step-at-a-time synthetic scoped constructor fixture through Loom."""
import argparse,json,pathlib,secrets
from loom_mcp import Loom
from verify_property_commands import read_rows,unwrap
from verify_schema_acl_preservation import call,tool,checked_role,role_snapshot,Acceptance,semantic
from apply_property_ui import Apply,load_manifest
from property_ui_journal import sync_write,dispatch_once
ROLE='loom_schema_scoped_probe_20261010'
EMAIL='loom-schema-scoped-probe-20261010@example.invalid'
RESOURCE_ACTIONS={
 'loomSchemaAuthoring':['inspect','createHasMany','previewHasMany','previewObservedHasMany','inspectConstructorAuthority'],
 'flowSurfaces':['updateSettings'],
 'collections.fields':['create'],
}
def native_list(value):
 if isinstance(value,list):return value
 if isinstance(value,dict) and set(value)=={'data','meta'} and isinstance(value['data'],list) and isinstance(value['meta'],dict):
  meta=value['meta']
  if meta.get('page')==1 and meta.get('totalPage') in (0,1) and meta.get('count')==len(value['data']):return value['data']
 raise RuntimeError('Incomplete native inventory envelope')
def permissions():
 return {'dataSourceKey':'main','resources':[{'name':resource,'usingActionsConfig':True,'actions':[{'name':action,**({'fields':['id']} if resource!='loomSchemaAuthoring' else {})} for action in actions]} for resource,actions in RESOURCE_ACTIONS.items()]}
def validate_role(row):
 if row.get('name')!=ROLE or row.get('allowAll') is True or row.get('default') is True or row.get('allowNewMenu') is True or row.get('allowConfigure') is True or row.get('snippets') not in (None,[]) or row.get('strategy',{}).get('actions',[])!=[]:
  raise RuntimeError('Unexpected fixture role authority')
ACL_TABLES=['dataSourcesRolesResources','dataSourcesRolesResourcesActions','dataSourcesRolesResourcesScopes']
def acl_rows(c):return {t:[semantic(r) for r in read_rows(c,t)] for t in ACL_TABLES}
def preserve_acl(before,after):
 for table,old in before.items():
  current={r['id']:r for r in after[table]}
  if any(current.get(r['id'])!=r for r in old):return False
 old_resources={r['id'] for r in before[ACL_TABLES[0]]}
 new_resources=[r for r in after[ACL_TABLES[0]] if r['id'] not in old_resources]
 if any(r['roleName']!=ROLE or r['dataSourceKey']!='main' or r['name'] not in RESOURCE_ACTIONS for r in new_resources):return False
 owned_ids={r['id'] for r in after[ACL_TABLES[0]] if r['roleName']==ROLE}
 old_actions={r['id'] for r in before[ACL_TABLES[1]]}
 if any(r['rolesResourceId'] not in owned_ids for r in after[ACL_TABLES[1]] if r['id'] not in old_actions):return False
 return after[ACL_TABLES[2]]==before[ACL_TABLES[2]]
def verify_permissions(rows):
 resources=[r for r in rows[ACL_TABLES[0]] if r['roleName']==ROLE]
 if len(resources)!=len(RESOURCE_ACTIONS) or len({r['id'] for r in resources})!=len(resources) or {r['name'] for r in resources}!=set(RESOURCE_ACTIONS):return False
 if any(r.get('dataSourceKey')!='main' or r.get('usingActionsConfig') is not True for r in resources):return False
 for resource in resources:
  actions=[a for a in rows[ACL_TABLES[1]] if a['rolesResourceId']==resource['id']]
  if len(actions)!=len(RESOURCE_ACTIONS[resource['name']]) or len({a['id'] for a in actions})!=len(actions) or {a['name'] for a in actions}!=set(RESOURCE_ACTIONS[resource['name']]):return False
  if any(a.get('scopeId') is not None for a in actions):return False
  # Pinned native data-sources-roles-resources-actions fields array defaults [].
  expected=['id'] if resource['name']!='loomSchemaAuthoring' else []
  if any(a.get('fields')!=expected for a in actions):return False
 return True
def journal_path(path,step):
 return pathlib.Path(path)/('create-account.json' if step=='account' else step+'.json')
def run(c,path,step):
 if checked_role(c).get('allowAll') is not True:raise RuntimeError('Root constructor required')
 path=pathlib.Path(path);path.mkdir(mode=0o700,parents=True,exist_ok=True)
 roles=native_list(call(c,'roles_list',{'page':1,'pageSize':50}));users=read_rows(c,'users',fields=['id'])
 if len(roles)>100:raise RuntimeError('Role bound exceeded')
 api=Apply(c,{},load_manifest(),None)
 matches=[r for r in roles if r.get('name')==ROLE]
 before_path=path/'original.json'
 if not before_path.exists():
  if step!='role' or matches or read_rows(c,'users',fields=['id'],filter={'email':EMAIL}):raise RuntimeError('Fixture ownership not established')
  sync_write(before_path,{'roles':{r['name']:role_snapshot(api.snapshot(r['name'])) for r in roles},'users':sorted(u['id'] for u in users),'acl':acl_rows(c)},True)
 original=json.loads(before_path.read_text())
 current={r:role_snapshot(api.snapshot(r)) for r in original['roles']}
 if current!=original['roles'] or not preserve_acl(original['acl'],acl_rows(c)):raise RuntimeError('Existing role state changed')
 if step in ('account','bind','remove-member') and not verify_permissions(acl_rows(c)):raise RuntimeError('Owned fixture permissions changed')
 existing_account=read_rows(c,'users',fields=['id','email'],filter={'email':EMAIL})
 if len(existing_account)>1:raise RuntimeError('Duplicate fixture account')
 if matches:validate_role(matches[0])
 if step!='role' and not matches:raise RuntimeError('Create owned role first')
 creds_path=path/'account.json'
 if not creds_path.exists():
  if existing_account:raise RuntimeError('Unowned account collision')
  sync_write(creds_path,{'email':EMAIL,'role':ROLE,'password':secrets.token_urlsafe(32)},True)
 account=json.loads(creds_path.read_text())
 uid=existing_account[0]['id'] if existing_account else None
 if account.get('id') not in (None,uid):raise RuntimeError('Account identity drift')
 if uid:account['id']=uid;sync_write(creds_path,account)
 expected_users=sorted(original['users']+([uid] if uid else []))
 if sorted(u['id'] for u in users)!=expected_users:raise RuntimeError('Unrelated account inventory changed')
 if step=='role':
  stem='roles_create';args={'requestBody':{'name':ROLE,'title':'Synthetic scoped constructor probe','default':False,'hidden':True,'allowConfigure':False,'allowNewMenu':False,'snippets':[],'strategy':{'actions':[]}}}
 elif step=='permissions':
  stem='roles_apply_data_permissions';args={'filterByTk':ROLE,'requestBody':permissions()}
 elif step=='account':
  if uid:raise RuntimeError('Account already exists; reconcile journal')
  stem='users_create';args={'requestBody':{'username':ROLE,'email':EMAIL,'nickname':'Synthetic scoped constructor probe','password':account['password']}}
 elif step in ('bind','remove-member'):
  if not uid:raise RuntimeError('Create owned account first')
  bound=native_list(call(c,'users_roles_list',{'userId':uid,'pageSize':50}))
  names=sorted(r['name'] for r in bound)
  if any(r not in ('member',ROLE) for r in names):raise RuntimeError('Unexpected account role')
  if step=='bind':
   stem='users_roles_add';args={'userId':uid,'filterByTk':[ROLE]}
  else:
   if names!=sorted(['member',ROLE]):raise RuntimeError('No exact owned member binding to remove')
   stem='users_roles_remove';args={'userId':uid,'filterByTk':['member']}
 else:raise RuntimeError('Unknown explicit step')
 def read_after():
  # Existing role objects, resource permissions, scopes and routes stay exact.
  existing={r:role_snapshot(api.snapshot(r)) for r in original['roles']}
  return {'existingRoles':existing,'fixture':role_snapshot(api.snapshot(ROLE)),
          'account':read_rows(c,'users',fields=['id','email'],filter={'email':EMAIL}),'acl':acl_rows(c),'userIds':sorted(u['id'] for u in read_rows(c,'users',fields=['id']))}
 def verify(after):
  if after['existingRoles']!=original['roles'] or not preserve_acl(original['acl'],after['acl']):return False
  if step in ('permissions','account','bind','remove-member') and not verify_permissions(after['acl']):return False
  after_uid=after['account'][0]['id'] if len(after['account'])==1 else None
  if after['userIds']!=sorted(original['users']+([after_uid] if after_uid else [])):return False
  validate_role(after['fixture']['role'])
  if step=='account' and len(after['account'])!=1:return False
  if step in ('bind','remove-member'):
   names=sorted(r['name'] for r in native_list(call(c,'users_roles_list',{'userId':uid,'pageSize':50})))
   if ROLE not in names or (step=='remove-member' and names!=[ROLE]):return False
  return True
 result=dispatch_once(c,tool(c,stem),args,journal_path(path,step),{'existingRoles':current,'fixture':role_snapshot(api.snapshot(ROLE)) if matches else None,'account':existing_account,'acl':acl_rows(c),'userIds':sorted(u['id'] for u in users)},read_after,verify)
 # Fresh application baseline is separately required after fixture completion.
 return {'verifiedStep':step,'nextRequiresFreshBaseline':True,'appAcceptance':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--journal',required=True);p.add_argument('--step',choices=['role','permissions','account','bind','remove-member'],required=True)
 a=p.parse_args();print(json.dumps(run(Loom(a.runtime),a.journal,a.step)))
