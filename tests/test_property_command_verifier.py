import pathlib,sys,tempfile,unittest,json
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import verify_property_commands as v
class GateTests(unittest.TestCase):
 def test_missing_request_identity_rejected(self):
  class C:pass
  c=C();c.tools=[];c.by_name={}
  for action,suffix in v.ACTIONS.items():
   name=v.PREFIX+suffix+"hash";schema={"properties":{"requestBody":{"required":[]}},"required":[]};c.tools.append({"name":name});c.by_name[name]={"inputSchema":schema}
  with self.assertRaisesRegex(RuntimeError,"requestId absent"):v.schema_gate(c)
 def test_journal_exclusive(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d)/"intent.json";v.durable(p,{"requestId":"same"})
   with self.assertRaises(FileExistsError):v.durable(p,{"requestId":"different"})
   self.assertEqual(json.loads(p.read_text())["requestId"],"same")
 def test_unknown_outcome_not_denial(self):
  class Root:pass
  with tempfile.TemporaryDirectory() as d:
   root=Root();root.runtime=pathlib.Path(d);q=v.Qualification(root,"test")
   state={n:[] for n in v.AUDIT};q.audit=lambda:state
   with patch.object(v,"call",side_effect=TimeoutError("unknown")):
    with self.assertRaisesRegex(RuntimeError,"Unclassified"):q.command(None,"manager","createProperty",{},"probe",expected_error="PROPERTY_SCOPE")
   self.assertEqual(q.events[-1]["status"],"blocked-unknown-or-unexpected")
 def test_expected_denial_requires_unchanged_state(self):
  class Root:pass
  with tempfile.TemporaryDirectory() as d:
   root=Root();root.runtime=pathlib.Path(d);q=v.Qualification(root,"test");q.audit=iter([{n:[] for n in v.AUDIT},{n:[1] for n in v.AUDIT}]).__next__
   with patch.object(v,"call",side_effect=RuntimeError("PROPERTY_SCOPE")):
    with self.assertRaisesRegex(AssertionError,"changed audit"):q.command(None,"manager","createProperty",{},"probe",expected_error="PROPERTY_SCOPE")
 def test_scoped_draft_has_single_revision_input(self):
  d=v.draft(4,9,"SYNTHETIC");self.assertEqual(d["unitId"],4);self.assertEqual(len(d["parties"]),1);self.assertNotIn("tenantUserId",d);self.assertNotIn("revision",d["term"])
if __name__=="__main__":unittest.main()
