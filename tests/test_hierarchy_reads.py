import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
import verify_hierarchy_reads as h
class Matrix(unittest.TestCase):
 def test_own_binding(self):self.assertEqual(h.cases(True,"1")[0][3],[3,4])
 def test_foreign_always_denied(self):self.assertIsNone(h.cases(True,"2")[5][3])
 def test_portal_no_new_grants(self):self.assertTrue(all(x[3] is None for x in h.cases(False,"1")))
 def test_status_failure_not_denial(self):self.assertFalse(h.validate(500,{},None,"list"))
 def test_exact_ids(self):self.assertFalse(h.validate(200,{"data":[{"id":3},{"id":99}]},[3,4],"list"))
 def test_nested_wrong_unit(self):self.assertFalse(h.validate(200,{"data":{"units":[{"id":3,"tenancies":[{"id":4,"unitId":2}]}]}},[3],"nested"))
if __name__=="__main__":unittest.main()

