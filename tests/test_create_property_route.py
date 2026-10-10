import pathlib,sys,unittest,copy,tempfile,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from apply_create_property_route import wanted_routes,verify_roles,FocusedRoute,ROLE,ROLES
class Route(unittest.TestCase):
 def baseline(self):return {r:{'role':{'name':r},'permissions':[{'name':'kept'}],'snippets':['kept'],'routes':[{'id':1}]} for r in ROLES}
 def test_manager_union_preserves_existing_routes_and_portals(self):
  before=self.baseline();wanted=wanted_routes(before[ROLE],{'menuRouteId':2,'tabRouteId':3});after=copy.deepcopy(before);after[ROLE]['routes']=[{'id':int(i)} for i in wanted];verify_roles(before,after,wanted);self.assertEqual(wanted,[1,2,3])
 def test_authority_or_portal_drift_denied(self):
  before=self.baseline()
  for role in ROLES:
   after=copy.deepcopy(before);after[role]['permissions']=[]
   with self.assertRaises(RuntimeError):verify_roles(before,after,['1'])
 def test_capture_drift_stops_before_dispatch(self):
  api=object.__new__(FocusedRoute);api.capture=lambda q:{'changed':True}
  with self.assertRaisesRegex(RuntimeError,'drift'):api.apply({}, {'original':True},'/never-used')
 def test_verified_grant_is_journaled_and_cannot_be_replayed(self):
  before=self.baseline();gate={'binding':{'menuRouteId':2,'tabRouteId':3},'formConfigDigest':'fixed','formNodeHash':'fixed'};baseline={'roles':before,'gate':gate};after=copy.deepcopy(before);after[ROLE]['routes']=[{'id':i} for i in [1,2,3]]
  api=object.__new__(FocusedRoute);api.capture=lambda q:copy.deepcopy(baseline);api.gate=lambda q:gate;api.snapshots=lambda:after
  class Client:
   calls=[]
   tools=[json.loads((pathlib.Path(__file__).parent/'fixtures/native-roles-desktop-routes-set.json').read_text())]
   def call(self,name,args):self.calls.append(args);return {'data':'ok'}
  class Names:
   def tool(self,prefix):return 'loom_native_roles_desktop_routes_set_872fd64ca912508a'
  api.c=Client();api.api=Names()
  with tempfile.TemporaryDirectory() as directory:
   result=api.apply({},baseline,directory);self.assertTrue(result['managerOnly']);self.assertEqual(api.c.calls,[{'roleName':ROLE,'requestBody':[1,2,3]}])
   with self.assertRaises(RuntimeError):api.apply({},baseline,directory)
   self.assertEqual(len(api.c.calls),1)
if __name__=='__main__':unittest.main()

class QualificationGate(unittest.TestCase):
 def test_immutable_qualification_changes_fail_before_observation(self):
  q={'key':'create-property','uid':'zp_property_create_form_v1','gridUid':'g','config':{'action':'createProperty'},'desiredHash':'a','bindingHash':'b','placementProof':{}}
  for key in ('uid','gridUid','config','desiredHash','bindingHash','placementProof'):
   class FakeForms:
    def qualify(self,*args):return {**q,key:'changed'}
    def observe(self,*args):raise AssertionError('Must reject before observation')
   api=object.__new__(FocusedRoute);api.forms=FakeForms()
   with self.assertRaisesRegex(RuntimeError,'qualification changed'):api.gate(q)

 def test_native_page_binding_is_derived_before_using_route_ids(self):
  from unittest.mock import patch
  q={'key':'create-property','uid':'zp_property_create_form_v1','gridUid':'g','config':{'action':'createProperty'},'desiredHash':'a','bindingHash':'b','placementProof':{}}
  class FakeForms:
   def __init__(self):self.reads=[]
   def qualify(self,*args):return copy.deepcopy(q)
   def read(self,stem,args):self.reads.append((stem,args));return {'native':'surface'}
   def observe(self,*args):return {'attached':True,'form':{'config':q['config'],'nodeHash':'saved'}}
  api=object.__new__(FocusedRoute);api.forms=FakeForms()
  with patch('apply_create_property_route.page_binding',return_value={'gridUid':'g','menuRouteId':7,'tabRouteId':8}):
   result=api.gate(q);self.assertEqual(result['binding']['menuRouteId'],7)
   self.assertEqual(api.forms.reads,[('flow_surfaces_get',{'pageSchemaUid':'zp-create-property'})])
  with patch('apply_create_property_route.page_binding',return_value={'gridUid':'other'}):
   with self.assertRaisesRegex(RuntimeError,'grid changed'):api.gate(q)

class ActualManifestSnapshot(unittest.TestCase):
 def test_real_constructor_and_all_role_snapshots_share_normalized_manifest(self):
  from apply_property_ui import load_manifest
  class NativeReadStub:
   def __init__(self):
    self.calls=[]
    self.tools=[{'name':prefix+'abc'} for prefix in ['loom_native_roles_data_source_resources_get_','loom_native_roles_get_','loom_native_data_sources_roles_get_','loom_native_roles_desktop_routes_list_']]
   def call(self,name,args):
    self.calls.append((name,args))
    if name.startswith('loom_native_roles_data_source_resources_get_'):return {'data':{'name':args['name'],'actions':[]}}
    if name.startswith('loom_native_roles_desktop_routes_list_'):return {'data':[]}
    return {'data':{'name':args.get('roleName',args.get('filterByTk'))}}
  client=NativeReadStub();api=FocusedRoute(client)
  self.assertEqual(api.api.manifest,load_manifest())
  snapshots=api.snapshots()
  self.assertEqual(set(snapshots),set(ROLES))
  declared=set(load_manifest()['resources'])
  for role,snapshot in snapshots.items():
   self.assertTrue(declared.issubset({r['name'] for r in snapshot['permissions']}))
   self.assertIn('zp_domain_commands',{r['name'] for r in snapshot['permissions']})
  self.assertTrue(all(isinstance(args.get('name',''),str) for _,args in client.calls))

class NativeRouteContract(unittest.TestCase):
 def fixture(self):
  import json
  descriptor=json.loads((pathlib.Path(__file__).parent/'fixtures/native-roles-desktop-routes-set.json').read_text())
  before={r:{'role':{'name':r},'permissions':[],'snippets':[],'routes':[{'id':1}]} for r in ROLES}
  gate={'binding':{'menuRouteId':'391341736787968','tabRouteId':'391341736787969'},'formConfigDigest':'x','formNodeHash':'x'}
  baseline={'roles':before,'gate':gate}
  class Client:
   def __init__(self):self.tools=[descriptor];self.calls=[];self.after=copy.deepcopy(before)
   def call(self,name,args):
    import jsonschema
    jsonschema.Draft202012Validator(descriptor['inputSchema']).validate(args)
    self.calls.append((name,args));self.after[ROLE]['routes']=[{'id':v} for v in args['requestBody']]
    return {'data':args['requestBody']}
  c=Client();api=FocusedRoute(c);api.capture=lambda q:copy.deepcopy(baseline);api.gate=lambda q:gate;api.snapshots=lambda:c.after
  return api,c,baseline
 def test_integer_route_payload_passes_actual_discovered_schema_and_real_journal(self):
  api,c,baseline=self.fixture()
  with tempfile.TemporaryDirectory() as tmp:
   api.apply({},baseline,tmp)
   self.assertEqual(len(c.calls),1)
   self.assertEqual(c.calls[0][1]['requestBody'],[1,391341736787968,391341736787969])
   self.assertTrue((pathlib.Path(tmp)/'focused-create-property-route.json').exists())
 def test_schema_drift_denies_before_journal_or_dispatch(self):
  import jsonschema
  api,c,baseline=self.fixture();c.tools[0]['inputSchema']['properties']['requestBody']['items']['type']='string'
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(jsonschema.ValidationError):api.apply({},baseline,tmp)
   self.assertEqual(c.calls,[]);self.assertEqual(list(pathlib.Path(tmp).iterdir()),[])
 def test_invalid_or_unsafe_route_ids_rejected(self):
  from apply_create_property_route import route_id
  for value in [True,False,0,-1,1.5,'01','1.0','1e3','-1','9007199254740992',9007199254740992,None,'']:
   with self.assertRaises(RuntimeError):route_id(value)
  self.assertEqual(route_id('391341736787968'),391341736787968)
