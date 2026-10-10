import pathlib,sys,unittest,copy,tempfile
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from apply_create_property_route import wanted_routes,verify_roles,FocusedRoute,ROLE,ROLES
class Route(unittest.TestCase):
 def baseline(self):return {r:{'role':{'name':r},'permissions':[{'name':'kept'}],'snippets':['kept'],'routes':[{'id':1}]} for r in ROLES}
 def test_manager_union_preserves_existing_routes_and_portals(self):
  before=self.baseline();wanted=wanted_routes(before[ROLE],{'menuRouteId':2,'tabRouteId':3});after=copy.deepcopy(before);after[ROLE]['routes']=[{'id':int(i)} for i in wanted];verify_roles(before,after,wanted);self.assertEqual(wanted,['1','2','3'])
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
   def call(self,name,args):self.calls.append(args);return {'data':'ok'}
  class Names:
   def tool(self,prefix):return 'qualified-route-set'
  api.c=Client();api.api=Names()
  with tempfile.TemporaryDirectory() as directory:
   result=api.apply({},baseline,directory);self.assertTrue(result['managerOnly']);self.assertEqual(api.c.calls,[{'roleName':ROLE,'requestBody':['1','2','3']}])
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
