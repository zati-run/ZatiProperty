import copy,json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from apply_protected_forms import Forms,attached,missing_model
class Client:
 def __init__(self):
  self.tools=[{'name':'loom_native_'+name+'_abcdef12'} for name in ['loom_action_forms_get','loom_action_forms_create','loom_action_forms_set','loom_action_forms_describe','flow_surfaces_get']];self.writes=[];self.saved=False;self.fail=False;self.wrong_parent=False
 def call(self,name,args):
  if 'loom_action_forms_describe_' in name:return {'data':dict(QUAL['config'])}
  if 'loom_action_forms_get_' in name:
   if args['uid']=='grid0001':return {'data':{'uid':'grid0001','type':'BlockGridModel','nodeHash':'a'*64}}
   if not self.saved:raise RuntimeError('Loom tool error: '+json.dumps({'content':[{'type':'text','text':json.dumps({'statusCode':404,'body':{'errors':[{'message':'MODEL_NOT_FOUND'}]}})}],'isError':True}))
   return {'data':{'uid':'form0001','type':'LoomActionFormModel','nodeHash':'b'*64,'config':QUAL['config']}}
  if 'flow_surfaces_get_' in name:return {'data':{'tree':{'uid':'grid0001','subModels':{'items':[{'uid':'form0001','use':'LoomActionFormModel'}] if self.saved and not self.wrong_parent else []}}}}
  self.writes.append((name,args));self.saved=True
  if self.fail:raise RuntimeError('outcome unknown')
  return {'data':{'uid':'form0001'}}
QUAL={'uid':'form0001','gridUid':'grid0001','expectedGridHash':'a'*64,'config':{'actionPackage':'@demo/plugin-domain','resource':'demo','action':'createDraft','reconcileAction':'reconcile','schemaDigest':'c'*64,'implementationDigest':'d'*64,'packageVersion':'0.1.3','commandContract':'idempotent-terminal-v1'}}
class Tests(unittest.TestCase):
 def test_create_has_native_cas_and_persists_intent_before_only_dispatch(self):
  c=Client();api=Forms(c)
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'intent.json';original=c.call
   def call(name,args):
    if 'loom_action_forms_create_' in name:self.assertEqual(json.loads(path.read_text())['state'],'pending-or-unknown')
    return original(name,args)
   c.call=call;result=api.apply(copy.deepcopy(QUAL),path);self.assertEqual(result['state'],'verified');self.assertEqual(len(c.writes),1);self.assertEqual(c.writes[0][1]['requestBody']['expectedGridHash'],'a'*64)
   with self.assertRaisesRegex(RuntimeError,'fenced'):api.apply(copy.deepcopy(QUAL),path)
   self.assertEqual(len(c.writes),1)
 def test_unknown_create_reconciles_readonly_and_never_replays(self):
  c=Client();c.fail=True;api=Forms(c)
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'intent.json'
   with self.assertRaisesRegex(RuntimeError,'unknown'):api.apply(copy.deepcopy(QUAL),path)
   self.assertEqual(json.loads(path.read_text())['state'],'pending-or-unknown');self.assertTrue(api.matches(api.observe(QUAL),QUAL))
   with self.assertRaisesRegex(RuntimeError,'fenced'):api.apply(copy.deepcopy(QUAL),path)
   self.assertEqual(len(c.writes),1)
 def test_wrong_grid_attachment_never_counts_as_acceptance(self):
  c=Client();c.wrong_parent=True;api=Forms(c)
  with tempfile.TemporaryDirectory() as d:
   path=pathlib.Path(d)/'intent.json'
   with self.assertRaisesRegex(RuntimeError,'readback mismatch'):api.apply(copy.deepcopy(QUAL),path)
   self.assertEqual(json.loads(path.read_text())['state'],'pending-or-unknown')
 def test_grid_drift_prevents_any_write(self):
  c=Client();q=copy.deepcopy(QUAL);q['expectedGridHash']='f'*64
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(RuntimeError,'Grid changed'):Forms(c).apply(q,pathlib.Path(d)/'intent.json')
   self.assertEqual(c.writes,[])
 def test_missing_classifier_never_treats_permission_or_transport_failure_as_absence(self):
  for error in ['MODEL_NOT_FOUND', 'Loom tool error: '+json.dumps({'content':[{'type':'text','text':json.dumps({'statusCode':403,'body':{'errors':[{'message':'MODEL_NOT_FOUND'}]}})}],'isError':True})]:self.assertFalse(missing_model(RuntimeError(error)))
 def test_desired_forms_do_not_hide_decisions_or_expose_account_id_input(self):
  desired=json.loads((pathlib.Path(__file__).resolve().parents[1]/'generation/pages/property-protected-forms.json').read_text());draft=next(v['config'] for v in desired['forms'] if v['key']=='draft-tenancy')
  self.assertEqual(draft['choices']['/parties/*/userId'],{'collection':'zp_tenant_account_permissions','valueField':'userId','labelField':'displayName'})
  self.assertEqual(draft['formats']['/term/rentMinor'],{'kind':'money','scale':2})
  for form in desired['forms']:self.assertNotIn('reasonCode',form['config']['bindings'])
if __name__=='__main__':unittest.main()
