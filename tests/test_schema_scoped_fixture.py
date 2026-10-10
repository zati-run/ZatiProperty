import sys,pathlib,unittest,copy
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import schema_scoped_fixture as f
class FixtureSafety(unittest.TestCase):
 def baseline(self):
  return {f.ACL_TABLES[0]:[{'id':1,'roleName':'manager','dataSourceKey':'main','name':'properties'}],f.ACL_TABLES[1]:[{'id':2,'rolesResourceId':1,'name':'view','fields':['id']}],f.ACL_TABLES[2]:[{'id':3,'scope':{'ownerId':'current'}}]}
 def test_native_inventory_envelope(self):
  self.assertEqual(f.native_list({'data':[{'name':'manager'}],'meta':{'count':1,'page':1,'pageSize':20,'totalPage':1}}),[{'name':'manager'}])
  for meta in [{'count':2,'page':1,'totalPage':1},{'count':1,'page':1,'totalPage':2}]:
   with self.assertRaises(RuntimeError):f.native_list({'data':[{}],'meta':meta})
 def test_all_later_steps_require_exact_grants_pre_and_post(self):
  import inspect
  source=inspect.getsource(f.run)
  self.assertIn("step in ('account','bind','remove-member') and not verify_permissions(acl_rows(c))",source)
  self.assertIn("step in ('permissions','account','bind','remove-member') and not verify_permissions(after['acl'])",source)
 def test_no_broad_actions(self):
  p=f.permissions();self.assertEqual(p['dataSourceKey'],'main')
  for r in p['resources']:
   self.assertNotIn('*',r['name'])
   if r['name']!='loomSchemaAuthoring':
    self.assertTrue(all(a['fields']==['id'] for a in r['actions']))
 def test_existing_permission_or_scope_change_fails(self):
  b=self.baseline()
  for table in f.ACL_TABLES:
   a=copy.deepcopy(b);a[table][0]['changed']=True
   self.assertFalse(f.preserve_acl(b,a))
 def test_new_foreign_resource_or_action_fails(self):
  b=self.baseline();a=copy.deepcopy(b)
  a[f.ACL_TABLES[0]].append({'id':4,'roleName':'owner','dataSourceKey':'main','name':'properties'})
  self.assertFalse(f.preserve_acl(b,a))
  a=copy.deepcopy(b);a[f.ACL_TABLES[1]].append({'id':4,'rolesResourceId':1,'name':'create'})
  self.assertFalse(f.preserve_acl(b,a))
 def test_only_owned_expected_resource_addition(self):
  b=self.baseline();a=copy.deepcopy(b)
  a[f.ACL_TABLES[0]].append({'id':4,'roleName':f.ROLE,'dataSourceKey':'main','name':'flowSurfaces'})
  a[f.ACL_TABLES[1]].append({'id':5,'rolesResourceId':4,'name':'updateSettings','fields':['id']})
  self.assertTrue(f.preserve_acl(b,a))
 def test_role_broadness_rejected(self):
  for k,v in [('allowAll',True),('default',True),('allowConfigure',True),('snippets',['*']),('strategy',{'actions':['*']})]:
   with self.assertRaises(RuntimeError):f.validate_role({'name':f.ROLE,k:v})
 def test_complete_exact_permissions_required(self):
  rows={k:[] for k in f.ACL_TABLES}
  for i,r in enumerate(f.permissions()['resources']):
   rows[f.ACL_TABLES[0]].append({'id':i,'roleName':f.ROLE,'name':r['name'],'dataSourceKey':'main','usingActionsConfig':True})
   rows[f.ACL_TABLES[1]] += [dict(a,id=100+len(rows[f.ACL_TABLES[1]])+j,rolesResourceId=i) for j,a in enumerate(r['actions'])]
  self.assertTrue(f.verify_permissions(rows))
  for table in f.ACL_TABLES[:2]:
   duplicate=copy.deepcopy(rows);duplicate[table].append(copy.deepcopy(duplicate[table][0]))
   self.assertFalse(f.verify_permissions(duplicate))
  for key,value in [('dataSourceKey','foreign'),('usingActionsConfig',False)]:
   changed=copy.deepcopy(rows);changed[f.ACL_TABLES[0]][0][key]=value
   self.assertFalse(f.verify_permissions(changed))
  rows[f.ACL_TABLES[1]][0]['name']='destroy'
  self.assertFalse(f.verify_permissions(rows))
if __name__=='__main__':unittest.main()
