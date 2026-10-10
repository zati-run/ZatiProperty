import pathlib,sys,tempfile,unittest,json,subprocess
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import verify_property_commands as v
class GateTests(unittest.TestCase):
 @staticmethod
 def native_error(status,code):
  return RuntimeError("Loom tool error: "+json.dumps({"isError":True,"content":[{"type":"text","text":json.dumps({"statusCode":status,"body":{"errors":[{"code":code}]}})}]}))
 def test_zero_and_returned_versions(self):
  self.assertEqual(v.expected_version({"version":0}),0);self.assertEqual(v.expected_version({"version":7}),7)
  for row in [{},{"version":None},{"version":True},{"version":"1"}]:
   with self.assertRaises(ValueError):v.expected_version(row)
 def test_structured_error_boundary(self):
  self.assertTrue(v.expected_failure(self.native_error(403,"PROPERTY_SCOPE"),"PROPERTY_SCOPE"))
  self.assertFalse(v.expected_failure(self.native_error(500,"PROPERTY_SCOPE"),"PROPERTY_SCOPE"))
  self.assertFalse(v.expected_failure(RuntimeError("transport PROPERTY_SCOPE"),"PROPERTY_SCOPE"))
  self.assertFalse(v.expected_failure(self.native_error(403,"DOMAIN_ACTION_DENIED"),"PROPERTY_SCOPE"))
 def test_native_pagination_max50(self):
  class C:
   tools=[{"name":"loom_native_resource_list_hash"}]
   pages=[]
   def call(self,name,args):
    self.pages.append(args);return {"data":[{"id":i} for i in (range(1,51) if args["page"]==1 else [51])]}
  c=C();self.assertEqual(len(v.read_rows(c,"synthetic")),51);self.assertTrue(all(p["pageSize"]==50 for p in c.pages))
 def test_fixture_matches_actual_domain_enum_rules(self):
  module=ROOT/"packages/plugins/@zati/plugin-property-tenancy/dist/server/domain.js"
  script="const d=require(process.argv[1]);let s=\"\";process.stdin.on(\"data\",x=>s+=x);process.stdin.on(\"end\",()=>{try{d.tenancyInput(JSON.parse(s));process.stdout.write(\"valid\")}catch(e){process.stderr.write(e.code);process.exitCode=1}});"
  result=subprocess.run(["node","-e",script,str(module)],input=json.dumps(v.draft(1,2,"SYNTHETIC")),text=True,capture_output=True)
  self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout,"valid")
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
   with patch.object(v,"call",side_effect=self.native_error(403,"PROPERTY_SCOPE")):
    with self.assertRaisesRegex(AssertionError,"changed audit"):q.command(None,"manager","createProperty",{},"probe",expected_error="PROPERTY_SCOPE")
 def test_scoped_draft_has_single_revision_input(self):
  d=v.draft(4,9,"SYNTHETIC");self.assertEqual(d["unitId"],4);self.assertEqual(len(d["parties"]),1);self.assertNotIn("tenantUserId",d);self.assertNotIn("revision",d["term"])
if __name__=="__main__":unittest.main()
