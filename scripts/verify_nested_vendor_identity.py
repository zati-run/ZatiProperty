#!/usr/bin/env python3
"""One-shot synthetic nested vendor identity probe, through manager Loom only.

No retry/reset. Reconcile both work order and vendor after the attempted write.
If identity changes, stop and leave restoration to the coordinator via Loom.
"""
import argparse,datetime,json,os,pathlib,secrets
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--run",action="store_true")
if not parser.parse_args().run:
    print("Prepared one-shot nested vendor probe; supply --run only for authorized synthetic mutation.")
    raise SystemExit(0)
from loom_mcp import Loom
from verify_maintenance_writes import role_bridge,record,tool,safe_error,private_json
runtime=pathlib.Path(os.environ['ZP_RUNTIME_DIR'])
loom_dir=pathlib.Path(os.environ['ZP_LOOM_DIR'])
config=json.loads((runtime/'loom.json').read_text())
accounts=json.loads((runtime/'maintenance-test-accounts.json').read_text())
ids=json.loads((runtime/'maintenance-fixture-ids.json').read_text())
root=Loom()
order_id=ids['1']['zp_work_orders'];vendor_id=ids['1']['zp_vendors'];other_vendor_id=ids['2']['zp_vendors']
run_dir=runtime/'nested-vendor-probes'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(3))
run_dir.mkdir(parents=True,mode=0o700)
before={'order':record(root,'zp_work_orders',order_id),'vendor':record(root,'zp_vendors',vendor_id),'otherVendor':record(root,'zp_vendors',other_vendor_id)}
private_json(run_dir/'before.json',before)
new_user=before['otherVendor']['userId']
assert before['vendor']['userId']!=new_user,'Probe requires distinct existing user identities'
error=None
with role_bridge(root,runtime,loom_dir,config,'zp_property_manager.1',accounts['zp_property_manager.1'],run_dir) as manager:
    private_json(run_dir/'intent.json',{'operation':'workorder-update','status':'uncertain-until-readback','vendorId':vendor_id,'attemptedUserId':new_user})
    try:
        manager.call(tool(manager,'resource_update'),{'resource':'zp_work_orders','filterByTk':order_id,
                       'values':{'vendor':{'id':vendor_id,'userId':new_user}}})
    except Exception as failure:
        error=safe_error(failure)
after={'order':record(root,'zp_work_orders',order_id),'vendor':record(root,'zp_vendors',vendor_id),'otherVendor':record(root,'zp_vendors',other_vendor_id)}
private_json(run_dir/'after.json',after)
changed={entity:sorted(k for k in set(before[entity])|set(after[entity]) if before[entity].get(k)!=after[entity].get(k)) for entity in before}
report={'case':'manager-nested-vendor-userId','error':error,'changedFields':changed,
        'vendorUserIdBefore':before['vendor']['userId'],'vendorUserIdAfter':after['vendor']['userId'],
        'attemptedUserId':new_user,'identityChanged':before['vendor']['userId']!=after['vendor']['userId'],
        'restoration':'not attempted; coordinator owns any restore through Loom'}
private_json(run_dir/'result.json',report)
print(json.dumps(report))
