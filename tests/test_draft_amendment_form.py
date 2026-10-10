import copy,json,pathlib,sys,tempfile,unittest,os,subprocess
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from apply_protected_forms import Forms,IMMUTABLE
ROOT=pathlib.Path(__file__).resolve().parents[1]
DESIRED=json.loads((ROOT/'generation/pages/tenancy-draft-amendment-form.json').read_text())
class Client:
 tools=[{'name':'loom_native_'+name+'_abcdef12','inputSchema':{'type':'object'}} for name in ['loom_action_forms_get','loom_action_forms_create','loom_action_forms_set','loom_action_forms_describe']]
class Fixture(Forms):
 def __init__(self):
  super().__init__(Client());self.calls=[];self.drift=False
 def observe(self,qualified):return {'form':None,'attached':False}
 def get(self,uid):return {'uid':uid,'type':'BlockGridModel','nodeHash':'a'*64}
 def placement_proof(self,grid,config):return {'kind':'qualified-popup','gridUid':grid,'collection':'zp_tenancies'}
 def read(self,stem,args):
  self.calls.append((stem,args))
  if stem=='pm_get':return {'version':'0.1.6' if args['filterByTk']=='@loom/plugin-action-form' else '0.1.4','enabled':True,'installed':True,'isCompatible':True}
  if stem=='loom_action_forms_describe':return {'packageVersion':'0.1.4','commandContract':'idempotent-terminal-v1','schemaDigest':'b'*64,'implementationDigest':'c'*64,'schema':{'required':['requestId'],'properties':{'requestId':{'format':'uuid'}}},'prefillContract':{'contract':'scoped-proposal-v1','parameter':'tenancyId','schemaDigest':('d' if not self.drift else 'e')*64}}
  raise AssertionError(stem)
class Tests(unittest.TestCase):
 def test_template_preserves_complete_proposal_and_currency_without_hidden_decisions(self):
  c=DESIRED['forms'][0]['config'];self.assertEqual(c['action'],'updateDraftTenancy')
  self.assertEqual(c['prefill']['fields'],['startDate','endDate','term','parties'])
  self.assertNotIn('fixedInputs',c);self.assertNotIn('formats',c)
  self.assertNotIn('reasonCode',c['bindings']);self.assertNotIn('adoptLegacy',c['bindings'])
  self.assertEqual(c['choices']['/parties/*/userId']['collection'],'zp_tenant_account_permissions')
  self.assertIn('exclusive',c['labels']['/endDate']);self.assertIn('minor units',c['labels']['/term/rentMinor'])
 def test_qualification_uses_actual_describe_prefill_schema_and_includes_immutable_pin(self):
  f=Fixture();q=f.qualify(DESIRED,{'manager-tenancy-amendment-grid':{'gridUid':'grid0001'}},'amend-draft-tenancy')
  self.assertEqual(q['config']['prefill']['schemaDigest'],'d'*64);self.assertIn('prefill',IMMUTABLE)
  self.assertEqual(next(args for stem,args in f.calls if stem=='loom_action_forms_describe')['prefillAction'],'draftTenancyProposal')
 def test_changed_read_contract_stops_before_any_intent_or_write(self):
  f=Fixture();q=f.qualify(DESIRED,{'manager-tenancy-amendment-grid':{'gridUid':'grid0001'}},'amend-draft-tenancy');f.drift=True
  with tempfile.TemporaryDirectory() as directory:
   intent=pathlib.Path(directory)/'intent.json'
   with self.assertRaisesRegex(RuntimeError,'prefill qualification changed'):f.apply(q,intent)
   self.assertFalse(intent.exists())
class ActualPolicy(unittest.TestCase):
 def test_desired_amendment_normalizes_with_actual_companion_policy_and_domain_swagger(self):
  source=os.environ.get('LOOM_ACTION_FORM_SERVER_DIR')
  self.assertTrue(source,'LOOM_ACTION_FORM_SERVER_DIR must name the independently reviewed companion source')
  script=r"""
const assert=require('node:assert/strict'),path=require('node:path');
const p=require(path.join(process.env.LOOM_ACTION_FORM_SERVER_DIR,'policy.js'));
const prefill=require(path.join(process.env.LOOM_ACTION_FORM_SERVER_DIR,'prefill.js'));
const desired=require('./generation/pages/tenancy-draft-amendment-form.json'),config=structuredClone(desired.forms[0].config);
const spec=require('./packages/plugins/@zati/plugin-property-tenancy/dist/swagger/index.json');
const schema=spec.paths['/zpPropertyTenancy:updateDraftTenancy'].post.requestBody.content['application/json'].schema;
const read=prefill.contract(spec,'zpPropertyTenancy','updateDraftTenancy','reconcileCommand','draftTenancyProposal');
Object.assign(config,{schemaDigest:p.hash(schema),implementationDigest:'a'.repeat(64),packageVersion:'0.1.4'});
config.prefill.schemaDigest=read.schemaDigest;
const fields={zp_tenancies:['id','version','code','leaseState','draftRevision'],zp_tenant_account_permissions:['id','userId','displayName']};
const metadata=(name,names)=>{assert.ok(fields[name]);for(const field of names)assert.ok(fields[name].includes(field));return {model:{primaryKeyAttribute:'id'}};};
p.normalizeConfig(config,schema,metadata);prefill.normalize(config,schema);
const bad=structuredClone(config);bad.readback.idPath=bad.readback.resultIdField;delete bad.readback.resultIdField;
assert.throws(()=>p.normalizeConfig(bad,schema,metadata),/INVALID_SHAPE/);
"""
  result=subprocess.run(['node','-e',script],cwd=ROOT,capture_output=True,text=True)
  self.assertEqual(result.returncode,0,result.stderr)
if __name__=='__main__':unittest.main()
