#!/usr/bin/env python3
"""Live synthetic invariant checks; every attempted write goes through Loom MCP."""
import json,pathlib
from loom_mcp import Loom
c=Loom();root=pathlib.Path(__file__).resolve().parents[1]
read=lambda resource,id:c.call('loom_native_resource_get_2b75c05e90349502',{'resource':resource,'filterByTk':id})['data']
def update(resource,id,values):return c.call('loom_native_resource_update_00ad6183c57a0c48',{'resource':resource,'filterByTk':id,'values':values})
fixtures=json.loads((c.runtime/'maintenance-fixture-ids.json').read_text());one=fixtures['1'];two=fixtures['2']
checks=[]
for name,resource,id,values in [
 ('unpermitted-vendor','zp_work_orders',one['zp_work_orders'],{'vendorId':two['zp_vendors']}),
 ('nested-unpermitted-vendor','zp_work_orders',one['zp_work_orders'],{'vendor':{'id':two['zp_vendors']}}),
 ('forged-approval','zp_work_orders',one['zp_work_orders'],{'approvalGranted':True}),
 ('approval-gate','zp_work_orders',one['zp_work_orders'],{'state':'progress'}),
 ('immutable-property-context','zp_work_orders',one['zp_work_orders'],{'propertyId':two['zp_properties']}),
 ('immutable-parent-unit-context','zp_units',one['zp_units'],{'propertyId':two['zp_properties']}),
]:
 before=read(resource,id);error=None
 try:update(resource,id,values)
 except Exception as e:error=str(e)
 after=read(resource,id)
 passed=error is not None and before==after
 checks.append({'case':name,'passed':passed,'error':error,'unchanged':before==after})
 (c.runtime/'maintenance-guard-results.json').write_text(json.dumps(checks,indent=2))
 print(name,passed)
 if not passed:raise RuntimeError('Domain guard failed; stop dependent writes: '+name)
# Bounded expired-vendor fixture is retained; it has no associated login/account.
p=c.runtime/'expired-vendor.json'
if p.exists():expired=json.loads(p.read_text())
else:
 existing=c.call('loom_native_resource_list_5bf3e99ab707b2a5',{'resource':'zp_vendors','filter':{'name':'Expired synthetic vendor'}})['data']
 if existing:raise RuntimeError('Unbound expired-vendor fixture needs reconciliation')
 expired=c.call('loom_native_resource_create_8a2640bf1cd9e1e5',{'resource':'zp_vendors','values':{'name':'Expired synthetic vendor','active':True,'insuranceExpiresAt':'2000-01-01','licenseExpiresAt':'2099-12-31'}})['data'];p.write_text(json.dumps(expired));p.chmod(0o600)
 c.call('loom_native_resource_create_8a2640bf1cd9e1e5',{'resource':'zp_vendor_properties','values':{'vendorId':expired['id'],'propertyId':one['zp_properties']}})
before=read('zp_work_orders',one['zp_work_orders']);error=None
try:update('zp_work_orders',one['zp_work_orders'],{'vendorId':expired['id']})
except Exception as e:error=str(e)
after=read('zp_work_orders',one['zp_work_orders']);passed=error is not None and before==after
checks.append({'case':'expired-vendor','passed':passed,'error':error,'unchanged':before==after})
(root/'docs/generation/receipts/maintenance-guards.json').write_text(json.dumps({'evidence':'live-Loom-MCP','checks':checks},indent=2)+'\n')
print('expired-vendor',passed)
if not passed:raise RuntimeError('expired vendor guard failed')
