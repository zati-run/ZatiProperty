#!/usr/bin/env python3
"""One bounded synthetic nested mapping update through manager Loom; no replay/reset."""
import argparse,datetime,json,os,pathlib,secrets
from loom_mcp import Loom
from verify_maintenance_writes import role_bridge,record,tool,safe_error,private_json
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true')
if not p.parse_args().run:
    print('Prepared nested vendor mapping negative; --run requires authorized synthetic scope.')
    raise SystemExit(0)
runtime=pathlib.Path(os.environ['ZP_RUNTIME_DIR']);loom_dir=pathlib.Path(os.environ['ZP_LOOM_DIR'])
config=json.loads((runtime/'loom.json').read_text());accounts=json.loads((runtime/'maintenance-test-accounts.json').read_text());ids=json.loads((runtime/'maintenance-fixture-ids.json').read_text());root=Loom()
run_dir=runtime/'nested-vendor-probes'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-mapping-'+secrets.token_hex(3));run_dir.mkdir(parents=True,mode=0o700)
def snapshot():
    return {'order':record(root,'zp_work_orders',ids['1']['zp_work_orders']),
            'vendor':record(root,'zp_vendors',ids['1']['zp_vendors']),
            'mapping1':record(root,'zp_vendor_properties',ids['1']['zp_vendor_properties']),
            'mapping2':record(root,'zp_vendor_properties',ids['2']['zp_vendor_properties']),
            'allMappings':root.call(tool(root,'resource_list'),{'resource':'zp_vendor_properties','pageSize':20})}
before=snapshot();private_json(run_dir/'before.json',before)
error=None
with role_bridge(root,runtime,loom_dir,config,'zp_property_manager.1',accounts['zp_property_manager.1'],run_dir) as manager:
    values={'vendor':{'id':ids['1']['zp_vendors'],'propertyPermissions':[{'id':ids['1']['zp_vendor_properties'],'propertyId':ids['2']['zp_properties']}]}}
    private_json(run_dir/'intent.json',{'status':'uncertain-until-readback','values':values})
    try:manager.call(tool(manager,'resource_update'),{'resource':'zp_work_orders','filterByTk':ids['1']['zp_work_orders'],'values':values})
    except Exception as failure:error=safe_error(failure)
after=snapshot();private_json(run_dir/'after.json',after)
changed=[key for key in before if before[key]!=after[key]]
report={'case':'manager-nested-vendor-propertyPermissions','error':error,'changedSnapshots':changed,'mappingPropertyBefore':before['mapping1']['propertyId'],'mappingPropertyAfter':after['mapping1']['propertyId'],'attemptedPropertyId':ids['2']['zp_properties'],'passed':not changed,'restoration':'none attempted; coordinator owns any restoration'}
private_json(run_dir/'result.json',report);print(json.dumps(report))
