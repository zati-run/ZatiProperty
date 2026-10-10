import pathlib,sys,tempfile,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import verify_property_invariants as s
class Safety(unittest.TestCase):
 def client(self,error=None):
  class Client:
   tools=[{"name":"loom_native_resource_update_test"}]
   by_name={"loom_native_resource_update_test":{"inputSchema":{"type":"object"}}}
   def call(self,name,args):
    if error:raise error
    return {"data":{}}
  return Client()
 def test_unexpected_success_stops(self):
  with tempfile.TemporaryDirectory() as d:
   class Q:path=pathlib.Path(d)
   with patch.object(s,"snapshot",return_value={}):
    with self.assertRaisesRegex(AssertionError,"unexpectedly succeeded"):s.denied_generic(None,Q(),self.client(),"root","update",{},"probe")
 def test_transport_failure_is_not_denial(self):
  with tempfile.TemporaryDirectory() as d:
   class Q:
    path=pathlib.Path(d)
    def record(self,x):pass
   with patch.object(s,"snapshot",return_value={}):
    with self.assertRaisesRegex(RuntimeError,"Unexpected generic denial"):s.denied_generic(None,Q(),self.client(TimeoutError()),"root","update",{},"probe")
 def test_rollback_snapshot_includes_nested_and_audit(self):
  class Q:
   def audit(self):return {"head":11}
  with patch.object(s.v,"read_rows",side_effect=lambda root,name:[{"id":1}]) as r:
   result=s.snapshot(None,Q())
   self.assertEqual(set(result["rows"]),set(s.WATCH))
   self.assertEqual(result["audit"],{"head":11})
   self.assertIn("zp_property_interests",result["rows"])
if __name__=="__main__":unittest.main()
