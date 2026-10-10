import copy,json,tempfile,unittest
from pathlib import Path
from apply_property_ui import Apply,Journal,page_binding,atomic_receipt,digest,ROOT
class RepairTests(unittest.TestCase):
 def setUp(self):
  self.desired=json.loads((ROOT/'generation/pages/portfolio.json').read_text())['page']
  route={'id':2,'parentId':1,'schemaUid':'tab','title':'Untitled','hidden':True,'type':'tabs'}
  self.surface={'pageRoute':{'id':1,'schemaUid':'zp-portfolio','title':'Portfolio','icon':'HomeOutlined','enableHeader':True,'children':[route]},'tree':{'uid':'zp-portfolio-page','use':'RootPageModel','props':{'title':'Portfolio','icon':'HomeOutlined','enableHeader':True},'subModels':{'tabs':[{'uid':'tab','use':'RootPageTabModel','props':{'route':route},'subModels':{'grid':{'uid':'grid','use':'BlockGridModel','parentId':'tab'}}}]}}}
 def test_native_binding(self):
  self.assertEqual(page_binding(self.surface,self.desired,True)['gridUid'],'grid')
 def test_drift_and_nonempty_block(self):
  for mutate in [lambda s:s['pageRoute'].update(title='Other'),lambda s:s['tree']['subModels']['tabs'].append({}),lambda s:s['tree']['subModels']['tabs'][0]['subModels']['grid'].update(subModels={'items':[{}]})]:
   s=copy.deepcopy(self.surface);mutate(s)
   with self.assertRaises(RuntimeError):page_binding(s,self.desired,True)
 def test_readonly_reconcile_preserves_intent_and_resume_never_calls_write(self):
  with tempfile.TemporaryDirectory() as temp:
   journal=Journal(Path(temp));baseline={'roles':{}}
   class Client:
    tools=[{'name':'loom_native_flow_surfaces_create_page_test'},{'name':'loom_native_flow_surfaces_get_test'}]
    def call(inner,name,args):
     self.assertEqual(name,'loom_native_flow_surfaces_get_test');return self.surface
   api=Apply(Client(),baseline,{},journal)
   intent={'state':'pending-or-unknown','tool':'loom_native_flow_surfaces_create_page_test','arguments':{'requestBody':self.desired},'beforeHash':digest(baseline)}
   path=journal.path/'page-portfolio.json';path.write_text(json.dumps(intent));original=path.read_bytes()
   with self.assertRaises(RuntimeError):api.resume_created('portfolio',{'page':self.desired})
   api.reconcile_page('portfolio');self.assertEqual(path.read_bytes(),original)
   self.assertEqual(api.resume_created('portfolio',{'page':self.desired})['binding']['gridUid'],'grid')
   with self.assertRaises(FileExistsError):api.reconcile_page('portfolio')
   intent['beforeHash']='changed';path.write_text(json.dumps(intent))
   with self.assertRaises(RuntimeError):api.resume_created('portfolio',{'page':self.desired})
 def test_unknown_compose_blocks_before_any_native_call(self):
  with tempfile.TemporaryDirectory() as temp:
   journal=Journal(Path(temp));(journal.path/'compose-tenancies.json').write_text('{}')
   class Client:
    def call(self,*args):raise AssertionError('No native call allowed')
   with self.assertRaisesRegex(RuntimeError,'Prior compose'):Apply(Client(),{}, {},journal).pages(True)
 def test_atomic_receipt_never_overwrites(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'receipt.json';atomic_receipt(path,{'a':1})
   with self.assertRaises(FileExistsError):atomic_receipt(path,{'a':2})
   self.assertEqual(json.loads(path.read_text()),{'a':1})
if __name__=='__main__':unittest.main()
