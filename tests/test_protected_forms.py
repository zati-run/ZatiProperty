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
QUAL={'uid':'form0001','gridUid':'grid0001','expectedGridHash':'a'*64,'placementProof':{'kind':'context-free','gridUid':'grid0001'},'config':{'actionPackage':'@demo/plugin-domain','resource':'demo','action':'createDraft','reconcileAction':'reconcile','schemaDigest':'c'*64,'implementationDigest':'d'*64,'packageVersion':'0.1.3','commandContract':'idempotent-terminal-v1'}}
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
  self.assertEqual(draft['formats']['/term/rentMinor'],{'kind':'money','scale':2});self.assertEqual(draft['fixedInputs'],{'/term/currency':'USD'});self.assertIn('USD',draft['labels']['/term/rentMinor'])
  for form in desired['forms']:self.assertNotIn('reasonCode',form['config']['bindings'])
 def test_context_ancestry_rejects_wrong_collection_despite_matching_numeric_record_ids(self):
  config={'context':{'collection':'zp_units','recordPath':'popup.record'},'bindings':{'unitId':{'recordField':'id'}}}
  uses=['BlockGridModel','ChildPageTabModel','ChildPageModel','ViewActionModel','TableActionsColumnModel','TableBlockModel']
  nodes={str(i):{'uid':str(i),'use':use,'parentId':str(i+1),'stepParams':{}} for i,use in enumerate(uses)}
  nodes['3']['stepParams']={'popupSettings':{'openView':{'dataSourceKey':'main','collectionName':'zp_units','filterByTk':'{{ctx.record.id}}'}}};nodes['5']['stepParams']={'resourceSettings':{'init':{'dataSourceKey':'main','collectionName':'zp_units'}}}
  api=Forms(Client());api.read=lambda stem,args: {'vars':{'popup.record':{'type':'object'}}} if stem=='flow_surfaces_context' else {'tree':nodes[args['uid']]}
  proof=api.placement_proof('0',config);self.assertEqual(proof['collection'],'zp_units')
  nodes['3']['stepParams']['popupSettings']['openView']['collectionName']='zp_properties'
  with self.assertRaisesRegex(RuntimeError,'collection mismatch'):api.placement_proof('0',config)
 def test_context_ancestry_rejects_cycle(self):
  config={'context':{'collection':'zp_units','recordPath':'popup.record'},'bindings':{'unitId':{'recordField':'id'}}};api=Forms(Client())
  api.read=lambda stem,args:{'tree':{'uid':'0','use':'BlockGridModel','parentId':'0'}}
  with self.assertRaisesRegex(RuntimeError,'cyclic'):api.placement_proof('0',config)
if __name__=='__main__':unittest.main()

class AssociatedPlacement(unittest.TestCase):
 def fixture(self):
  config={'context':{'collection':'zp_units','recordPath':'popup.record'},'bindings':{'unitId':{'recordField':'id'}}}
  uses=['BlockGridModel','ChildPageTabModel','ChildPageModel','ViewActionModel','TableActionsColumnModel','TableBlockModel'];nodes={}
  for prefix,col in [('child','zp_units'),('parent','zp_properties')]:
   for i,use in enumerate(uses):nodes[prefix+str(i)]={'uid':prefix+str(i),'use':use,'parentId':prefix+str(i+1)}
   nodes[prefix+'3']['stepParams']={'popupSettings':{'openView':{'dataSourceKey':'main','collectionName':col,'filterByTk':'{{ctx.record.id}}'}}}
   nodes[prefix+'5']['stepParams']={'resourceSettings':{'init':{'dataSourceKey':'main','collectionName':col}}}
  nodes['child5']['parentId']='parent0';nodes['child5']['stepParams']['resourceSettings']['init'].update(associationName='zp_properties.units',sourceId='{{ctx.view.inputArgs.filterByTk}}');nodes['child3']['stepParams']['popupSettings']['openView'].update(associationName='zp_properties.units',sourceId='{{ctx.view.inputArgs.sourceId}}')
  metadata={'name':'units','collectionName':'zp_properties','type':'hasMany','target':'zp_units','sourceKey':'id','targetKey':'id','foreignKey':'propertyId'};fk={'name':'propertyId','collectionName':'zp_units','isForeignKey':True,'type':'bigInt'};api=Forms(Client())
  def read(stem,args):
   if stem=='flow_surfaces_get':return {'tree':nodes[args['uid']]}
   if stem=='collections_fields_get':return metadata if args['filterByTk']=='units' else fk
   return {'vars':{'popup.record':{'type':'object'}}}
  api.read=read;return api,config,nodes,metadata,fk
 def test_associated_proof_pins_native_parent_chain_and_metadata(self):
  api,c,n,m,f=self.fixture();proof=api.placement_proof('child0',c);self.assertEqual(proof['kind'],'native-associated-popup-record');self.assertEqual(proof['parentProof']['collection'],'zp_properties');self.assertEqual(proof['association']['foreignKey']['name'],'propertyId')
 def test_foreign_target_source_expression_and_nested_chain_fail_closed(self):
  for mutate in [lambda n,m,f:m.update(target='zp_tenancies'),lambda n,m,f:n['child5']['stepParams']['resourceSettings']['init'].update(sourceId='{{ctx.record.id}}'),lambda n,m,f:n['parent5']['stepParams']['resourceSettings']['init'].update(associationName='zp_portfolios.properties'),lambda n,m,f:f.update(isForeignKey=False)]:
   api,c,n,m,f=self.fixture();mutate(n,m,f)
   with self.assertRaises(RuntimeError):api.placement_proof('child0',c)
