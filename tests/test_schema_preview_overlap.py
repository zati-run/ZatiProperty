import pathlib,sys,unittest,copy
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import verify_schema_preview_overlap as v
class OverlapLink(unittest.TestCase):
 def setup_case(self):
  actors={c[0]:i+1 for i,c in enumerate(v.CASES)}
  results=[{'alias':alias,'outcome':expected} for alias,role,graph,expected in v.CASES for _ in range(6)]
  samples=[{'roleDigest':v.sha({'role':role}),'actorDigest':v.sha({'actor':str(actors[alias])}),'resource':'zp_buildings','action':'get','argumentDigest':v.sha({'filterByTk':'1','fields':['id','name']}),'status':403 if expected=='denied' else 200,'outcome':expected,'startNs':'200','endNs':'300'} for alias,role,graph,expected in v.CASES]
  return {'captureQualified':True,'invalidSamples':0,'startNs':'100','endNs':'5000000100','samples':samples},results,actors
 def test_exact_account_cases_link(self):
  o,r,a=self.setup_case();self.assertEqual(len(v.link_samples(o,r,a)),8)
 def test_foreign_actor_role_arguments_and_out_of_window_rejected(self):
  for key,value in [('actorDigest','0'*64),('roleDigest','0'*64),('argumentDigest','0'*64),('endNs','6000000000'),('status',500)]:
   o,r,a=self.setup_case();o['samples'][0][key]=value
   with self.assertRaises(RuntimeError):v.link_samples(o,r,a)
 def test_missing_http_checks_or_unqualified_capture_rejected(self):
  o,r,a=self.setup_case()
  with self.assertRaises(RuntimeError):v.link_samples(o,r[:-1],a)
  o['invalidSamples']=1
  with self.assertRaises(RuntimeError):v.link_samples(o,r,a)
if __name__=='__main__':unittest.main()
