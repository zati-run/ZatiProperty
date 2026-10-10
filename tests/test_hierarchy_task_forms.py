import json,os,pathlib,subprocess,unittest
import jsonschema
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Tests(unittest.TestCase):
 def test_actual_domain_policy_and_every_constructor_schema(self):
  server=os.environ.get('LOOM_ACTION_FORM_SERVER_DIR');self.assertTrue(server)
  script=r"""
const path=require('node:path'),p=require(path.join(process.env.LOOM_ACTION_FORM_SERVER_DIR,'policy.js'));
const desired=require('./generation/pages/hierarchy-task-forms.json'),domain=require('./packages/plugins/@zati/plugin-property-tenancy/dist/swagger/index.json');
const output=[];for(const form of desired.forms){const c=structuredClone(form.config),schema=domain.paths['/zpPropertyTenancy:'+c.action].post.requestBody.content['application/json'].schema;Object.assign(c,{schemaDigest:p.hash(schema),implementationDigest:'a'.repeat(64),packageVersion:'0.1.4'});p.normalizeConfig(c,schema,()=>({model:{primaryKeyAttribute:'id'}}));output.push(c);}console.log(JSON.stringify(output));
"""
  result=subprocess.run(['node','-e',script],cwd=ROOT,text=True,capture_output=True);self.assertEqual(result.returncode,0,result.stderr)
  swagger=json.loads((pathlib.Path(server).parent/'swagger/index.json').read_text())
  for config in json.loads(result.stdout):
   for action in ['create','set','migrateContract']:
    schema=swagger['paths']['/loomActionForms:'+action]['post']['requestBody']['content']['application/json']['schema'];body={'uid':'form0001','config':config}
    for key in schema['required']:
     if key in body:continue
     body[key]=({'packageVersion':'0.1.3','implementationDigest':'b'*64,'schemaDigest':config['schemaDigest'],'commandContract':config['commandContract']} if key=='expectedOldPins' else {'reviewDigest':'c'*64,'reason':'equivalent-command-schema-response-envelope-correction'} if key=='compatibilityProof' else 'grid0001' if key=='gridUid' else 'a'*64)
    jsonschema.validate(body,schema)
 def test_no_invented_bindings_or_unscoped_identity_choices(self):
  desired=json.loads((ROOT/'generation/pages/hierarchy-task-forms.json').read_text());self.assertEqual(len(desired['forms']),2)
  for form in desired['forms']:
   self.assertNotIn('gridUid',form);self.assertNotIn('choices',form['config']);self.assertEqual(form['config']['context']['recordPath'],'popup.record')
  self.assertEqual(desired['forms'][1]['config']['bindings'],{'propertyId':{'recordField':'propertyId'},'buildingId':{'recordField':'id'}})
if __name__=='__main__':unittest.main()
