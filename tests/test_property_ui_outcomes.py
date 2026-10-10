import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from property_ui_journal import dispatch_once
class Tests(unittest.TestCase):
 def test_native_error_is_durable_without_replay(self):
  class Client:
   calls=0
   def call(self,*args):
    self.calls+=1
    raise RuntimeError("native semantic rejection")
  c=Client()
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"intent.json"
   with self.assertRaises(RuntimeError):dispatch_once(c,"tool",{},p,{},lambda:{},lambda _:True)
   self.assertEqual(json.loads(p.read_text())["state"],"pending-or-unknown")
   self.assertEqual(json.loads(Path(str(p)+".failed").read_text())["error"],"native semantic rejection")
   with self.assertRaises(FileExistsError):dispatch_once(c,"tool",{},p,{},lambda:{},lambda _:True)
   self.assertEqual(c.calls,1)
 def test_response_survives_readback_failure(self):
  class Client:
   def call(self,*args):return {"nativeId":9}
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"intent.json"
   with self.assertRaises(RuntimeError):dispatch_once(Client(),"tool",{},p,{},lambda:{},lambda _:False)
   self.assertEqual(json.loads(Path(str(p)+".returned").read_text())["response"],{"nativeId":9})
   self.assertEqual(json.loads(p.read_text())["state"],"pending-or-unknown")
if __name__=="__main__":unittest.main()
