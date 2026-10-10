import pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from apply_property_ui import result_path
class Results(unittest.TestCase):
 def test_bounded_overlay_separates_checkpoint_and_journal(self):
  root=pathlib.Path('/private-runtime');self.assertEqual(result_path(root,'permissions','roles-2','hierarchy-reviewed-1').name,'property-ui-permissions-roles-2-hierarchy-reviewed-1-result.json')
  self.assertNotEqual(result_path(root,'permissions','roles-2','hierarchy-reviewed-1'),result_path(root,'permissions','roles-1','hierarchy-reviewed-1'))
 def test_historical_default_paths_preserved(self):
  for phase in ['permissions','snippet','pages','cleanup','routes']:self.assertEqual(result_path(pathlib.Path('/runtime'),phase,'checkpoint').name,'property-ui-'+phase+'-result.json')
 def test_invalid_or_unbounded_suffix_rejected(self):
  for phase,checkpoint,suffix in [('pages','cp','new'),('permissions','../x','new'),('permissions','cp','../new'),('permissions','','')]:
   with self.assertRaises(RuntimeError):result_path(pathlib.Path('/runtime'),phase,checkpoint,suffix)
if __name__=='__main__':unittest.main()
