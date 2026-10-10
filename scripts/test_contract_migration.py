import unittest
from unittest.mock import patch
import migrate_protected_form_contract as m
class Tests(unittest.TestCase):
 def old(self):return {'config':{'actionPackage':'@zati/plugin-property-tenancy','resource':'zpPropertyTenancy','action':'createProperty','reconcileAction':'reconcileCommand','packageVersion':'0.1.3','implementationDigest':'a'*64,'schemaDigest':'b'*64,'commandContract':'idempotent-terminal-v1'},'nodeHash':'c'*64}
 def test_only_package_pins_change(self):
  before=self.old();found={**before['config'],'packageVersion':'0.1.4','implementationDigest':'d'*64}
  with patch.object(m,'read',return_value=before),patch.object(m,'call',return_value=found):plan=m.candidate(None,'form1','e'*64)
  after=plan['arguments']['config'];self.assertEqual({k:v for k,v in after.items() if k not in ('packageVersion','implementationDigest')},{k:v for k,v in before['config'].items() if k not in ('packageVersion','implementationDigest')})
 def test_schema_drift_blocks(self):
  before=self.old();found={**before['config'],'packageVersion':'0.1.4','schemaDigest':'f'*64}
  with patch.object(m,'read',return_value=before),patch.object(m,'call',return_value=found):
   with self.assertRaisesRegex(RuntimeError,'Non-equivalent'):m.candidate(None,'form1','e'*64)
 def test_already_migrated_blocks(self):
  before=self.old();before['config']['packageVersion']='0.1.4'
  with patch.object(m,'read',return_value=before):
   with self.assertRaisesRegex(RuntimeError,'Unqualified'):m.candidate(None,'form1','e'*64)
 def test_drift_stops_before_dispatch(self):
  with patch.object(m,'read',return_value={'changed':True}),patch.object(m,'dispatch_once') as dispatch:
   with self.assertRaisesRegex(RuntimeError,'drift'):m.apply(None,{'arguments':{'uid':'form1'},'before':{}},'unused')
   dispatch.assert_not_called()
 def test_actual_get_shape_uses_native_surface_history(self):
  form={'uid':'form1','type':'LoomActionFormModel','nodeHash':'a'*64,'config':{'x':1},'configDigest':'b'*64}
  tree={'uid':'form1','stepParams':{'loomActionForm':{'owner':'@loom/plugin-action-form','config':form['config'],'contractHistory':[{'proof':1}]}}}
  with patch.object(m,'read',return_value=form),patch.object(m.Forms,'read',return_value={'tree':tree}):
   after=m.observe(None,'form1')
  self.assertEqual(after,{'form':form,'contractHistory':[{'proof':1}]})
 def test_surface_identity_or_config_mismatch_denied(self):
  form={'uid':'form1','type':'LoomActionFormModel','config':{'x':1}}
  for tree in [{'uid':'other'},{'uid':'form1','stepParams':{'loomActionForm':{'owner':'@loom/plugin-action-form','config':{'x':2}}}}]:
   with patch.object(m,'read',return_value=form),patch.object(m.Forms,'read',return_value={'tree':tree}):
    with self.assertRaises(RuntimeError):m.observe(None,'form1')
 def test_wrong_form_identity_denied(self):
  for form in [{'uid':'other','type':'LoomActionFormModel'},{'uid':'form1','type':'BlockGridModel'}]:
   with patch.object(m,'read',return_value=form):
    with self.assertRaisesRegex(RuntimeError,'form identity'):m.observe(None,'form1')
 def test_history_requires_exact_pin_pair(self):
  config={key:key for key in m.PINS};args={'config':config,'expectedConfigDigest':'a'*64,'expectedOldPins':{'old':1},'compatibilityProof':{'reviewDigest':'b'*64,'reason':'reviewed'}}
  entry={'configDigest':'a'*64,'oldPins':{'old':1},'newPins':config,'reviewDigest':'b'*64,'reason':'reviewed'}
  after={'form':{'config':config},'contractHistory':[entry]};self.assertTrue(m.verified({'arguments':args},after));entry['oldPins']={'wrong':1};self.assertFalse(m.verified({'arguments':args},after))
if __name__=='__main__':unittest.main()
