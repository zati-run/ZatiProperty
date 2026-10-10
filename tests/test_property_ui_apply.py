import copy, importlib.util, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from apply_property_ui import Apply, Journal, SNIPPET, action_clean
class Client:
 def __init__(self):self.calls=[]
 def call(self,name,args):self.calls.append((name,args));return {'data':{'saved':True}}
class Tests(unittest.TestCase):
 def test_exact_operation_alias_excludes_longer_operation_names(self):
  class Catalog:
   tools=[{"name":"loom_native_flow_surfaces_get_5ce19daccb56cc79"}, {"name":"loom_native_flow_surfaces_get_settings_1234567890abcdef"}]
  self.assertEqual(Apply(Catalog(),{}, {},None).tool("loom_native_flow_surfaces_get_"),"loom_native_flow_surfaces_get_5ce19daccb56cc79")
 def test_fresh_baseline_drift_prevents_dispatch(self):
  c=Client();api=Apply(c,{'roles':{'manager':{'value':1}}},{},None)
  api.snapshot=lambda _: {'value':2}
  with self.assertRaisesRegex(RuntimeError,'baseline drift'):api.guard()
  self.assertEqual(c.calls,[])
 def test_snippet_requires_exact_qualified_identifier(self):
  c=Client();api=Apply(c,{}, {},None)
  with self.assertRaisesRegex(RuntimeError,'qualified'):api.snippet('pm.*')
  self.assertEqual(c.calls,[])
 def test_action_projection_preserves_business_write_boundary(self):
  source=[{'id':5,'name':'update','fields':['state','vendorId'],'scopeId':7},{'name':'view','fields':['id'],'scopeId':8}]
  after=action_clean(source)
  self.assertEqual(after,[{'name':'update','fields':['state','vendorId'],'scopeId':7},{'name':'view','fields':['id'],'scopeId':8}])
 def test_readonly_ui_gate_rejects_unknown_actions(self):
  api=Apply(None,{}, {},None)
  self.assertEqual(api.unsafe({'data':{'nodeMap':{'v':{'use':'ViewActionModel'},'e':{'use':'EditActionModel'}}}}),['e'])
  with self.assertRaisesRegex(RuntimeError,'Unqualified'):api.unsafe({'data':{'nodeMap':{'x':{'use':'PaymentActionModel'}}}})
  with self.assertRaisesRegex(RuntimeError,'executable'):api.unsafe({'data':{'nodeMap':{'x':{'use':'JSBlockModel'}}}})
 def test_journal_unknown_response_blocks_replay(self):
  with tempfile.TemporaryDirectory() as tmp:
   journal=Journal(Path(tmp)/'journal');c=Client()
   def fail(_):raise RuntimeError('readback unavailable')
   with self.assertRaisesRegex(RuntimeError,'readback unavailable'):journal.run('once',c,'qualified-tool',{},fail)
   with self.assertRaisesRegex(RuntimeError,'prior'):journal.run('once',c,'qualified-tool',{},lambda _:True)
   self.assertEqual(len(c.calls),1)
 def test_journal_verified_response_preserved(self):
  with tempfile.TemporaryDirectory() as tmp:
   journal=Journal(Path(tmp)/'journal');c=Client();wanted={'id':123,'scope':'unchanged'}
   self.assertEqual(journal.run('once',c,'qualified-tool',{},lambda _:wanted),wanted)
   self.assertTrue((Path(tmp)/'journal/once.json').exists())
if __name__=='__main__':unittest.main()

