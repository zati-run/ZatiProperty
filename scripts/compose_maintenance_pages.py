#!/usr/bin/env python3
"""First native page composition; refuse replay and preserve every returned UID."""
import json,pathlib
from loom_mcp import Loom
root=pathlib.Path(__file__).resolve().parents[1];c=Loom()
pages=json.loads((root/'generation/bindings/pages.json').read_text())
context=['property','unit','tenancy']
defaults={'collections':{'zp_work_orders':{'fieldGroups':[{'title':'Work and context','fields':['title','request',*context,'priority']},{'title':'Assignment','fields':['vendor','state']},{'title':'Approval','fields':['estimatedAmount','currency','approvalRequired','approvalGranted']}]}}}
requests={'key':'requests','type':'table','resource':{'dataSourceKey':'main','collectionName':'zp_maintenance_requests'},'fields':['title','property','unit','tenancy','priority','status'],'recordActions':[{'type':'view','popup':{'title':'Maintenance request','blocks':[{'key':'requestContext','type':'details','resource':{'binding':'currentRecord'},'fields':['title','description',*context,'priority','permissionToEnter','status',{'fieldPath':'workOrders','fieldType':'subTable','fields':['title','vendor','state']}]}]}}]}
orders={'key':'orders','type':'table','resource':{'dataSourceKey':'main','collectionName':'zp_work_orders'},'fields':['title','property','unit','tenancy','vendor','state'],'recordActions':[{'type':'view','popup':{'title':'Work order','blocks':[{'key':'workContext','type':'details','resource':{'binding':'currentRecord'},'fields':['title','request',*context,'vendor','state','approvalRequired','approvalGranted']}]}},{'type':'edit','popup':{'title':'Assign vendor','blocks':[{'key':'assignmentContext','type':'details','resource':{'binding':'currentRecord'},'fields':['title',*context]},{'key':'assignment','type':'editForm','resource':{'binding':'currentRecord'},'fields':['vendor','state']}]}}]}
for key,block in [('maintenance',requests),('work-orders',orders)]:
 receipt=root/f'generation/bindings/{key}-composition.json'
 if receipt.exists():raise RuntimeError('existing composition: reconcile; do not replay '+key)
 args={'requestBody':{'target':{'uid':pages[key]['data']['gridUid']},'mode':'append','blocks':[block],'defaults':defaults}}
 (root/f'generation/pages/{key}.json').write_text(json.dumps(args,indent=2)+'\n')
 result=c.call('loom_native_flow_surfaces_compose_fcc21dedb4accf41',args)
 receipt.write_text(json.dumps(result,indent=2)+'\n');print(key,json.dumps(result)[:2500])
 readback=c.call('loom_native_flow_surfaces_get_5ce19daccb56cc79',{'pageSchemaUid':pages[key]['data']['pageSchemaUid']})
 (c.runtime/f'{key}-composed-readback.json').write_text(json.dumps(readback,indent=2))
 print('native tree readback',key,len(readback['data'].get('nodeMap',{})))
