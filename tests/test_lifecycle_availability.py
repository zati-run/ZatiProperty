import json,os,pathlib,subprocess,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class LifecycleAvailability(unittest.TestCase):
 def test_desired_states_and_native_typed_contract(self):
  server=os.environ.get('LOOM_ACTION_FORM_SERVER_DIR')
  if not server:self.fail('LOOM_ACTION_FORM_SERVER_DIR required for actual companion qualification')
  names=['property-protected-forms.json','tenancy-draft-amendment-form.json','hierarchy-task-forms.json'];forms=[]
  for name in names:
   desired=json.loads((ROOT/'generation/pages'/name).read_text());self.assertEqual(desired['requiredCompanionVersion'],'0.2.0');forms+=desired['forms']
  selected={f['config']['action']:f['config'] for f in forms if 'availableWhen' in f['config']}
  self.assertEqual(set(selected),{'activateTenancy','endTenancy','updateDraftTenancy'})
  for action,config in selected.items():
   self.assertEqual(config['context']['collection'],'zp_tenancies')
   self.assertEqual(config['availableWhen']['recordField'],'leaseState')
   self.assertEqual(config['availableWhen']['values'],['active' if action=='endTenancy' else 'draft'])
  script="const a=require(process.env.LOOM_ACTION_FORM_SERVER_DIR+'/availability');const forms=JSON.parse(require('fs').readFileSync(0,'utf8'));for(const c of forms){a.normalize(c.availableWhen,c.context);for(const value of ['draft','active','ended',null]){const got=a.state(c,{leaseState:value});if(got.available!==c.availableWhen.values.includes(value))throw Error('state mismatch');}}"
  subprocess.run(['node','-e',script],input=json.dumps(list(selected.values())),text=True,check=True)
 def test_only_presentation_rules_added(self):
  for name in ['property-protected-forms.json','tenancy-draft-amendment-form.json','hierarchy-task-forms.json']:
   before=json.loads(subprocess.check_output(['git','show','2cd376d:generation/pages/'+name],cwd=ROOT,text=True));after=json.loads((ROOT/'generation/pages'/name).read_text())
   after['requiredCompanionVersion']=before['requiredCompanionVersion']
   for form in after['forms']:form['config'].pop('availableWhen',None)
   self.assertEqual(after,before)
if __name__=='__main__':unittest.main()
