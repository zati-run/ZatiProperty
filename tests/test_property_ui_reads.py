import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_property_ui_reads import projections,ids
class ReadAssertions(unittest.TestCase):
 def test_nested_projection_rejects_private_target_identity(self):
  fields={'zp_units':{'id','property'},'zp_properties':{'id','name'}}
  self.assertEqual(projections({'id':3,'property':{'id':4,'name':'Synthetic'}},'zp_units',fields),[])
  self.assertIn('$.property.managerUserId',projections({'id':3,'property':{'id':4,'managerUserId':1}},'zp_units',fields))
 def test_list_projections_check_every_row(self):
  self.assertEqual(projections([{'id':1},{'id':2,'private':'hidden'}],'x',{'x':{'id'}}),['$[].private'])
 def test_ids_accept_native_string_ids_without_coercing_precision(self):
  self.assertEqual(ids([{'id':'9007199254740993'},{'id':2}]),['2','9007199254740993'])
 def test_unexpected_scalar_record_is_rejected(self):
  self.assertEqual(projections('unexpected','x',{'x':{'id'}}),['unexpected-record-shape'])
if __name__=='__main__':unittest.main()
