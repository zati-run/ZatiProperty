import sys,pathlib,json,unittest,tempfile
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
import verify_property_generic as g
class Tests(unittest.TestCase):
 def error(self,status,code,message):
  return RuntimeError("Loom tool error: "+json.dumps({"content":[{"type":"text","text":json.dumps({"statusCode":status,"body":{"errors":[{"code":code,"message":message}]}})}]}))
 def test_exact_safe_403(self):
  self.assertTrue(g.denial(self.error(403,"DOMAIN_ACTION_REQUIRED",g.MESSAGE),"root"))
  self.assertFalse(g.denial(self.error(500,"DOMAIN_ACTION_REQUIRED",g.MESSAGE),"root"))
  self.assertFalse(g.denial(self.error(403,"DOMAIN_ACTION_REQUIRED","raw code"),"root"))
  self.assertFalse(g.denial(self.error(403,"OTHER",g.MESSAGE),"root"))
  self.assertTrue(g.denial(self.error(403,None,"No permissions"),"manager"))
  self.assertFalse(g.denial(TimeoutError(),"root"))
 def test_all_rows_unprojected(self):
  with patch.object(g.base,"read_rows",return_value=[]) as read:
   state=g.snapshot(None)
   self.assertEqual(set(state),set(g.BUSINESS+g.base.AUDIT))
   self.assertTrue(all(len(c.args)==2 and not c.kwargs for c in read.call_args_list))
 def test_digest_detects_protected_payload_change(self):
  self.assertNotEqual(g.digest({"zp_domain_commands":[{"resultJSON":"one"}]}),g.digest({"zp_domain_commands":[{"resultJSON":"two"}]}))
 def test_exact_eight_cases_and_array_query(self):
  cases=g.cases({name:[{"id":1}] for name in g.base.AUDIT})
  self.assertEqual(len(cases),8)
  self.assertEqual(cases[2][1]["updateAssociationValues"],["parties"])
  self.assertEqual(cases[4][1]["values"],{"eventHash":"f"*64})
 def test_unknown_transport_is_not_acceptance(self):
  self.assertFalse(g.denial(self.error(500,None,"list.filter is not a function"),"root"))
if __name__=="__main__":unittest.main()

