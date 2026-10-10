import copy,json,pathlib,tempfile,unittest
from unittest.mock import Mock,patch
from verify_schema_acl_preservation import Acceptance,TARGET,denied,semantic,tool,role_snapshot,checked_role
def native_metadata(description='Executes POST /loomSchemaAuthoring:createHasMany'):
 fields=['collection','name','target','foreignKey','expectedAclDigest']
 return {'description':description,'inputSchema':{'type':'object','required':['requestBody'],'properties':{'requestBody':{'type':'object','additionalProperties':False,'required':fields,'properties':{key:{'type':'string'} for key in fields}}}}}
class Tests(unittest.TestCase):
 def fixture(self):
  c=Mock();c.call.return_value={'data':{'ok':True}};c.by_name={'loom_native_loom_schema_authoring_create_has_many_ab12':native_metadata()}
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
class DiscoveryTests(unittest.TestCase):
 def test_actual_truncated_create_and_preview_are_distinct(self):
  c=Mock();create='loom_native_loom_schema_authoring_create_has_ma_3dbe18cc301e153e';preview='loom_native_loom_schema_authoring_preview_has_m_0166cd2ed89617d4';c.by_name={create:native_metadata(),preview:native_metadata('Execute bounded schema preview and confirm transactional rollback; not read-only')}
  self.assertEqual(tool(c,'loom_schema_authoring_create_has_many'),create);self.assertEqual(tool(c,'loom_schema_authoring_preview_has_many'),preview)
 def test_wrong_operation_or_schema_never_resolves(self):
  c=Mock();name='loom_native_loom_schema_authoring_create_has_ma_3dbe18cc301e153e'
  for metadata in [native_metadata('Executes POST /other:createHasMany'),{'description':'Executes POST /loomSchemaAuthoring:createHasMany','inputSchema':{}},native_metadata('Execute bounded schema preview and confirm transactional rollback; not read-only')]:
   c.by_name={name:metadata}
   with self.assertRaisesRegex(RuntimeError,'Missing or ambiguous'):tool(c,'loom_schema_authoring_create_has_many')
 def test_ambiguous_matching_catalog_is_rejected(self):
  c=Mock();c.by_name={name:native_metadata() for name in ['loom_native_loom_schema_authoring_create_has_ma_3dbe18cc301e153e','loom_native_loom_schema_authoring_create_has_many_abc123']}
  with self.assertRaisesRegex(RuntimeError,'Missing or ambiguous'):tool(c,'loom_schema_authoring_create_has_many')
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
  with patch('verify_schema_acl_preservation.call',return_value={'roles':[ROLE],'role':ROLE,'allowAll':False}),patch('verify_schema_acl_preservation.denied',return_value={'passed':True}) as deny:
   result=a.negatives(before,manager)
  self.assertEqual(len(result['cases']),3)
  args=deny.call_args_list[1].args
  self.assertIs(args[0],manager);self.assertEqual(args[1],'loom_schema_authoring_create_has_many');self.assertEqual(args[3],'CONSTRUCTOR_REQUIRED')
  self.assertEqual(args[2]['requestBody']['expectedAclDigest'],'0'*64)

class NativeRoleEnvelopeTests(unittest.TestCase):
 def test_actual_native_metadata_envelope_keeps_constructor_authority(self):
  c=Mock();c.by_name={'loom_native_roles_check_ab12':{}};c.call.return_value={'data':{'roles':['root'],'role':'root','allowAll':True,'resources':{}},'meta':{'dataSources':{}}}
  result=checked_role(c);self.assertIs(result['allowAll'],True);self.assertEqual(result['roles'],['root'])
 def test_direct_qualified_role_and_metadata_envelope_manager(self):
  for role in [{'roles':['manager'],'role':'manager','allowAll':False},{'data':{'roles':['manager'],'role':'manager','allowAll':False},'meta':{'dataSources':{}}}]:
   with patch('verify_schema_acl_preservation.call',return_value=role):
    self.assertIs(checked_role(Mock())['allowAll'],False)
 def test_malformed_or_ambiguous_roles_cannot_be_constructor(self):
  good={'roles':['root'],'role':'root','allowAll':True}
  cases=[{**good,'roles':['root','manager']},{**good,'role':'manager'},{**good,'allowAll':'true'},{**good,'roles':None},{'data':good,'meta':{}},{'data':good,'meta':{'dataSources':[]}}, {'data':good,'meta':{'dataSources':{}},'errors':[]}]
  for value in cases:
   with self.subTest(value=value),patch('verify_schema_acl_preservation.call',return_value=value):
    with self.assertRaises(RuntimeError):checked_role(Mock())

class NativeAclDenial(unittest.TestCase):
 def packet(self,status=403,message='No permissions',extra=None):
  import json
  packet={'statusCode':status,'body':{'errors':[{'message':message}]}}
  if extra:packet.update(extra)
  return RuntimeError('Loom tool error: '+json.dumps({'content':[{'type':'text','text':json.dumps(packet)}],'isError':True}))
 def test_only_exact_native_acl_shape_is_qualified(self):
  from verify_schema_acl_preservation import native_acl_denial
  self.assertTrue(native_acl_denial(self.packet()))
  for error in [self.packet(500),self.packet(401),self.packet(message='Forbidden'),self.packet(extra={'extra':True}),RuntimeError('No permissions'),RuntimeError('403 No permissions'),RuntimeError('Loom tool error: malformed')]:
   self.assertFalse(native_acl_denial(error))
 def test_native_acl_mode_is_explicit_and_cannot_satisfy_stale_digest_case(self):
  from verify_schema_acl_preservation import denied
  from unittest.mock import patch
  with patch('verify_schema_acl_preservation.call',side_effect=self.packet()):
   self.assertEqual(denied(None,'inspect',{},'CONSTRUCTOR_REQUIRED',allow_native_acl=True)['rejectionLayer'],'native-acl')
   for code,enabled in [('CONSTRUCTOR_REQUIRED',False),('ACL_BASELINE_CHANGED',True)]:
    with self.assertRaises(RuntimeError):denied(None,'inspect',{},code,allow_native_acl=enabled)
