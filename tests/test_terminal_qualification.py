import sys,json,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from verify_terminal_commands import digest,validate_receipt,error_code
class Tests(unittest.TestCase):
 def setUp(self):
  self.payload={'requestId':'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','name':'','reasonCode':'initial-setup'}
  self.receipt={'receiptVersion':1,'actorId':'2','commandAction':'createProperty','requestId':self.payload['requestId'],'requestDigest':digest(self.payload),'status':'rejected','outcome':'rejected','code':'INVALID_TEXT','message':'Enter the required text within the permitted length.'}
 def test_exact_terminal_contract(self):validate_receipt(self.receipt,self.payload,'2','createProperty','rejected')
 def test_binding_mismatches_failclosed(self):
  for field,value in [('actorId','3'),('requestDigest','0'*64),('requestId','other'),('commandAction','createUnit'),('receiptVersion',2),('message','database detail'),('code','UNKNOWN')]:
   with self.assertRaises(AssertionError):validate_receipt({**self.receipt,field:value},self.payload,'2','createProperty','rejected')
 def test_identity_excluded_from_command_digest(self):
  self.assertEqual(digest(self.payload),digest({**self.payload,'requestId':'other'}))
  self.assertNotEqual(digest(self.payload),digest({**self.payload,'name':'changed'}))
 def test_only_typed_native_errors_are_classified(self):
  packet={'statusCode':409,'body':{'errors':[{'code':'INVALID_TEXT'}]}}
  err=RuntimeError('Loom tool error: '+json.dumps({'content':[{'type':'text','text':json.dumps(packet)}]}))
  self.assertEqual(error_code(err),'INVALID_TEXT')
  for error in [RuntimeError('INVALID_TEXT'),RuntimeError('network disconnected'),RuntimeError('Loom tool error: {}')]:
   with self.assertRaises(RuntimeError):error_code(error)
if __name__=='__main__':unittest.main()
