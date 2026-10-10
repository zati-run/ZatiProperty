import importlib.util,json,pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from prepare_property_ui import merge_actions
from property_ui_journal import dispatch_once
class PreparationTests(unittest.TestCase):
 def test_preserve_writes_and_scope(self):
  prior=[{"name":"view","fields":["id"],"scopeId":7},{"name":"update","fields":["priority"],"scopeId":8}]
  got=merge_actions(prior,["name"],7);self.assertEqual(got[1],prior[1]);self.assertEqual(got[0],{"name":"view","fields":["id","name"],"scopeId":7});self.assertEqual(prior[0]["fields"],["id"])
 def test_different_scope_denied(self):
  with self.assertRaises(ValueError):merge_actions([{"name":"view","fields":["id"],"scopeId":7}],["name"],9)
 def test_unbounded_view_denied(self):
  for fields in [None,["*"]]:
   with self.assertRaises(ValueError):merge_actions([{"name":"view","fields":fields,"scopeId":7}],["name"],7)
 def test_new_resource_read_only(self):self.assertEqual([a["name"] for a in merge_actions([],["id"],7)],["view"])
 def test_manifest_no_users_or_audit(self):
  d=json.loads((ROOT/"generation/roles/property-tenancy.json").read_text());self.assertTrue(d["noGenericWrites"]);self.assertEqual(d["role"],"zp_property_manager")
  for r in d["resources"]:self.assertNotIn(r["name"],d["excludedResources"]);self.assertNotIn("*",r["addViewFields"])
  account=next(r for r in d["resources"] if r["name"]=="zp_tenant_account_permissions");self.assertEqual(account["addViewFields"],["id","userId","displayName"])
 def test_uncertain_write_fences_retry(self):
  class Client:
   calls=0
   def call(self,*args):self.calls+=1;raise TimeoutError("unknown")
  c=Client()
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/"attempt.json"
   with self.assertRaises(TimeoutError):dispatch_once(c,"tool",{},p,{"v":1},lambda:{},lambda x:True)
   with self.assertRaises(FileExistsError):dispatch_once(c,"tool",{},p,{"v":1},lambda:{},lambda x:True)
   self.assertEqual(c.calls,1);self.assertEqual(json.loads(p.read_text())["state"],"pending-or-unknown")
 def test_success_readback_durable(self):
  class Client:
   def call(self,*args):return {"ok":True}
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/"attempt.json";r=dispatch_once(Client(),"tool",{},p,{},lambda:{"v":2},lambda x:x["v"]==2)
   self.assertEqual(json.loads(p.read_text())["state"],"verified");self.assertEqual(r["after"],{"v":2})
if __name__=="__main__":unittest.main()
