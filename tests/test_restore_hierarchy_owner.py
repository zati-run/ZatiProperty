import copy,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from restore_hierarchy_owner import payload_for
class Restore(unittest.TestCase):
 def fixture(self):
  return {"role":{},"strategy":{},"routes":[],"permissions":[{"name":"zp_properties","usingActionsConfig":True,"actions":[{"name":"view","fields":["id","name"],"scopeId":7}]}]}
 def test_only_reviewed_added_field_is_restored(self):
  before=self.fixture();after=copy.deepcopy(before);after["permissions"][0]["actions"][0]["fields"].append("units")
  result=payload_for(before,after)
  self.assertEqual(result[0]["actions"][0]["fields"],["id","name"])
  self.assertEqual(result[0]["actions"][0]["scopeId"],7)
 def test_unplanned_field_fails(self):
  before=self.fixture();after=copy.deepcopy(before);after["permissions"][0]["actions"][0]["fields"].append("secret")
  with self.assertRaisesRegex(RuntimeError,"Unplanned field"):payload_for(before,after)
 def test_scope_drift_fails(self):
  before=self.fixture();after=copy.deepcopy(before);after["permissions"][0]["actions"][0]["scopeId"]=8
  with self.assertRaisesRegex(RuntimeError,"scope drift"):payload_for(before,after)
 def test_routes_drift_fails(self):
  before=self.fixture();after=copy.deepcopy(before);after["routes"]=[{"id":1}]
  with self.assertRaisesRegex(RuntimeError,"Non-permission"):payload_for(before,after)
if __name__=="__main__":unittest.main()
