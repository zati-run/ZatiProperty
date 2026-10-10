#!/usr/bin/env python3
"""Only the owned synthetic work-order1 baseline. Every reset is Loom MCP mediated."""
import argparse,datetime,json,os
from pathlib import Path
from loom_mcp import Loom
from verify_maintenance_writes import tool,record,safe_error
p=argparse.ArgumentParser();p.add_argument('--stage',required=True);p.add_argument('--reset',action='store_true');a=p.parse_args()
root=Loom();runtime=Path(os.environ['ZP_RUNTIME_DIR']);receipt=Path(__file__).resolve().parents[1]/'docs/generation/receipts/manager-final-native-readbacks.json'
entries=json.loads(receipt.read_text()) if receipt.exists() else []
def sync_directory(path):
 fd=os.open(path,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def save_receipt():
 temporary=receipt.with_suffix('.json.pending')
 with temporary.open('x') as stream:
  json.dump(entries,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
 os.replace(temporary,receipt);sync_directory(receipt.parent)
def compact(row):return {key:row.get(key) for key in ['id','title','state','vendorId','requestId','propertyId','unitId','tenancyId']}
before=record(root,'zp_work_orders',1)
if before.get('title')!='Inspect kitchen tap':raise RuntimeError('unexpected synthetic binding')
event={'observedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':a.stage,'before':compact(before),'mutation':'none'}
if a.reset:
 if before.get('state')!='quote' or before.get('vendorId')!=1:raise RuntimeError('baseline drift: reconcile before reset')
 journal=runtime/'browser-reset-pending.json'
 if journal.exists():raise RuntimeError('pending reset requires explicit reconciliation')
 fd=os.open(journal,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 with os.fdopen(fd,'w') as stream:
  json.dump({'stage':a.stage,'before':compact(before),'status':'outcome-unknown'},stream);stream.flush();os.fsync(stream.fileno())
 sync_directory(runtime)
 error=None
 try:root.call(tool(root,'resource_update'),{'resource':'zp_work_orders','filterByTk':1,'values':{'state':'new','vendorId':None}})
 except Exception as failure:error=safe_error(failure)
 after=record(root,'zp_work_orders',1);event.update({'mutation':'Loom resource_update','after':compact(after),'transportError':error})
 entries.append(event);save_receipt()
 if after.get('state')!='new' or after.get('vendorId') is not None:raise RuntimeError('reset outcome differs: journal retained; no retry')
 journal.unlink();sync_directory(runtime)
else:
 entries.append(event);save_receipt()
print(json.dumps(event))
