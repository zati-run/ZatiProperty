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
if __name__=='__main__':unittest.main()
