import json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Hierarchy(unittest.TestCase):
 def test_reverse_relations_reuse_existing_keys(self):
  d=json.loads((ROOT/"generation/collections/property-hierarchy.json").read_text())
  self.assertEqual(d["collections"],[])
  self.assertEqual([(x["collection"],x["field"]["name"],x["field"]["target"],x["field"]["foreignKey"]) for x in d["addFields"]],[("zp_properties","units","zp_units","propertyId"),("zp_units","tenancies","zp_tenancies","unitId")])
 def test_context_tables_use_native_associations(self):
  found=[]
  def walk(x):
   if isinstance(x,dict):
    if x.get("type")=="table" and x.get("key") in ["units","tenancies","terms-history","parties-history"]:
     found.append(x);self.assertEqual(x["resource"]["binding"],"associatedRecords");self.assertNotIn("dataScope",x.get("settings",{}))
    for v in x.values():walk(v)
   elif isinstance(x,list):
    for v in x:walk(v)
  for name in ["portfolio","tenancies"]:walk(json.loads((ROOT/("generation/pages/"+name+".json")).read_text()))
  self.assertEqual(len(found),6)
if __name__=="__main__":unittest.main()

