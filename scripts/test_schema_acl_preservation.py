import copy,json,pathlib,tempfile,unittest
from unittest.mock import Mock,patch
from verify_schema_acl_preservation import Acceptance,TARGET,denied,semantic,tool,role_snapshot
class Tests(unittest.TestCase):
 def fixture(self):
  c=Mock();c.call.return_value={'data':{'ok':True}};c.by_name={'loom_native_loom_schema_authoring_create_has_many_ab12':{}}
  a=Acceptance(c)
  before={'field':None,'inspect':{'field':None,'aclDigest':'a'*64},'foreignKey':{'name':'buildingId'},'belongsTo':{'name':'building'},'roles':{'manager':{'fields':['id']}}}
  after=copy.deepcopy(before);after['field']={'name':'units','type':'hasMany','target':'zp_units','foreignKey':'buildingId','sourceKey':'id','targetKey':'id'}
  return c,a,before,after
 def test_canonical_manifest(self):
  _,a,_,_=self.fixture();self.assertIsInstance(a.roles.manifest['resources'],dict)
 def test_drift_before_write(self):
  c,a,before,after=self.fixture();a.capture=lambda:after
  with self.assertRaisesRegex(RuntimeError,'Baseline drift'):a.apply(before,'unused')
  c.call.assert_not_called()
 def test_existing_field_no_replay(self):
  c,a,before,_=self.fixture();before['field']={'name':'units'}
  with self.assertRaisesRegex(RuntimeError,'already exists'):a.apply(before,'unused')
  c.call.assert_not_called()
 def test_verified_once_journal_fences_replay(self):
  c,a,before,after=self.fixture();a.capture=Mock(side_effect=[before,after,before])
  with tempfile.TemporaryDirectory() as d:
   journal=pathlib.Path(d)/'intent.json';a.apply(before,journal)
   self.assertEqual(json.loads(journal.read_text())['state'],'verified')
   with self.assertRaises(FileExistsError):a.apply(before,journal)
  self.assertEqual(c.call.call_count,1)
 def test_permission_drift_retains_unknown(self):
  c,a,before,after=self.fixture();after['roles']['manager']['fields'].append('units');a.capture=Mock(side_effect=[before,after])
  with tempfile.TemporaryDirectory() as d:
   journal=pathlib.Path(d)/'intent.json'
   with self.assertRaisesRegex(RuntimeError,'readback mismatch'):a.apply(before,journal)
   self.assertEqual(json.loads(journal.read_text())['state'],'pending-or-unknown')
  self.assertEqual(c.call.call_count,1)
 def test_fk_drift_retains_unknown(self):
  c,a,before,after=self.fixture();after['foreignKey']['allowNull']=False;a.capture=Mock(side_effect=[before,after])
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(RuntimeError,'readback mismatch'):a.apply(before,pathlib.Path(d)/'intent.json')
 def test_exact_operation(self):
  c=Mock();c.by_name={'loom_native_get_ab12':{},'loom_native_get_settings_ef34':{}}
  self.assertEqual(tool(c,'get'),'loom_native_get_ab12')
 def test_unknown_error_not_denial(self):
  c=Mock();c.by_name={'loom_native_inspect_ab12':{}};c.call.side_effect=RuntimeError('timeout')
  with self.assertRaisesRegex(RuntimeError,'Uncertain rejection'):denied(c,'inspect',{},'DENIED')
 def test_semantic_only_timestamps(self):
  self.assertEqual(semantic({'createdAt':'x','fields':['id'],'filter':{'id':1}}),{'fields':['id'],'filter':{'id':1}})
if __name__=='__main__':unittest.main()

class SecurityRegressions(unittest.TestCase):
 def test_filter_timestamps_remain_permission_state(self):
  snapshot={'role':{'updatedAt':'metadata','options':{'updatedAt':'keep'}},'permissions':[{'createdAt':'metadata','actions':[{'updatedAt':'metadata','params':{'filter':{'createdAt':{'$gt':'2026-01-01'},'updatedAt':{'$lt':'2027-01-01'}}}}]}]}
  actual=role_snapshot(snapshot)
  self.assertEqual(actual['role']['options'],{'updatedAt':'keep'})
  self.assertEqual(actual['permissions'][0]['actions'][0]['params'],snapshot['permissions'][0]['actions'][0]['params'])
  self.assertNotIn('createdAt',actual['permissions'][0])
 def test_manager_mutation_denied_before_stale_cas(self):
  from verify_schema_acl_preservation import ROLE
  client=Mock();manager=Mock();a=Acceptance(client);before={'inspect':{'aclDigest':'a'*64}};a.capture=lambda:before
  with patch('verify_schema_acl_preservation.call',return_value={'role':ROLE,'allowAll':False}),patch('verify_schema_acl_preservation.denied',return_value={'passed':True}) as deny:
   result=a.negatives(before,manager)
  self.assertEqual(len(result['cases']),3)
  args=deny.call_args_list[1].args
  self.assertIs(args[0],manager);self.assertEqual(args[1],'loom_schema_authoring_create_has_many');self.assertEqual(args[3],'CONSTRUCTOR_REQUIRED')
  self.assertEqual(args[2]['requestBody']['expectedAclDigest'],'0'*64)
