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
   self.assertEqual(set(result["audit"]),set(s.v.AUDIT))
   self.assertEqual(result["audit"]["zp_domain_commands"],[{"id":1}])
   self.assertIn("zp_property_interests",result["rows"])
 def test_changed_command_payload_is_detected(self):
  with tempfile.TemporaryDirectory() as d:
   class Q:
    path=pathlib.Path(d)
    def record(self,x):pass
   before={"audit":{"zp_domain_commands":[{"id":1,"resultJSON":"original"}]}}
   after={"audit":{"zp_domain_commands":[{"id":1,"resultJSON":"tampered"}]}}
   with patch.object(s,"snapshot",side_effect=[before,after]),patch.object(s.v,"expected_failure",return_value=True):
    with self.assertRaisesRegex(AssertionError,"changed state"):s.denied_generic(None,Q(),self.client(RuntimeError("denied")),"root","update",{},"probe")
 def test_complete_audit_snapshot_uses_no_field_projection(self):
  class Q:
   def audit(self):raise AssertionError("Projected audit must not be used")
  with patch.object(s.v,"read_rows",return_value=[]) as read:
   s.snapshot(None,Q())
   for name in s.v.AUDIT:self.assertIn(((None,name),{}),[(c.args,c.kwargs) for c in read.call_args_list])
 def test_resume_missing_checkpoint_fails(self):
  class Q:events=[]
  with self.assertRaisesRegex(RuntimeError,"checkpoint absent"):s.resume_checkpoint(None,Q())
 def test_resume_changed_audit_stops_before_reads(self):
  class Q:
   events=[{"label":"ownership-incomplete","status":"blocked-unknown-or-unexpected","before":{"head":13},"after":{"head":13}}]
   def audit(self):return {"head":14}
  with patch.object(s.v,"read_rows") as read:
   with self.assertRaisesRegex(RuntimeError,"Audit drift"):s.resume_checkpoint(None,Q())
   read.assert_not_called()
 def test_resume_rejects_existing_receipt(self):
  class Q:
   events=[{"label":"ownership-incomplete","status":"blocked-unknown-or-unexpected","before":{},"after":{},"requestId":"original"}]
   def audit(self):return {}
  with patch.object(s.v,"read_rows",return_value=[{"id":1}]):
   with self.assertRaisesRegex(RuntimeError,"Unexpected command receipt"):s.resume_checkpoint(None,Q())
if __name__=="__main__":unittest.main()
