#!/usr/bin/env python3
"""Create reviewed synthetic graphs through Loom. Never retry uncertain writes."""
import json,pathlib
from loom_mcp import Loom
root=pathlib.Path(__file__).resolve().parents[1];c=Loom()
accounts=json.loads((c.runtime/'maintenance-test-accounts.json').read_text())
path=c.runtime/'maintenance-fixture-ids.json'
bindings=json.loads(path.read_text()) if path.exists() else {}
graphs=json.loads((root/'generation/fixtures/maintenance.json').read_text())['graphs']
order=[('property','zp_properties'),('unit','zp_units'),('tenancy','zp_tenancies'),('vendor','zp_vendors'),('vendorProperty','zp_vendor_properties'),('request','zp_maintenance_requests'),('workOrder','zp_work_orders')]
for index,graph in enumerate(graphs,1):
 key=str(index);ids=bindings.setdefault(key,{})
 for local,collection in order:
  if collection in ids:continue
  values=dict(graph[local])
  for f,v in list(values.items()):
   if isinstance(v,str) and v.startswith('$user.'):values[f]=accounts[v[6:]]['id']
   elif isinstance(v,str) and v.startswith('$'):
    target=dict(order)[v[1:]];values[f]=ids[target]
  if local=='workOrder':
   values.pop('approvalRequired',None);values.pop('approvalGranted',None)
  journal=c.runtime/f'seed-{index}-{collection}.json'
  if journal.exists():raise RuntimeError('Prior attempt must be reconciled before retry: '+journal.name)
  journal.write_text(json.dumps({'values':values,'outcome':'unknown'}));journal.chmod(0o600)
  result=c.call('loom_native_resource_create_8a2640bf1cd9e1e5',{'resource':collection,'values':values})
  record=result['data'];ids[collection]=record['id'];path.write_text(json.dumps(bindings,indent=2));path.chmod(0o600)
  observed=c.call('loom_native_resource_get_2b75c05e90349502',{'resource':collection,'filterByTk':record['id']})
  assert observed['data']['id']==record['id']
  journal.write_text(json.dumps({'id':record['id'],'outcome':'readback-confirmed'}));print('persisted',key,collection,record['id'])
(root/'generation/bindings/fixtures.json').write_text(json.dumps(bindings,indent=2)+'\n')
