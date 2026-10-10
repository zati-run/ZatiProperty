#!/usr/bin/env python3
"""Read-only authenticated regression for maintenance association isolation.

Authentication runs through Loom. Native requests are exclusively GET. Results
contain keys/types/status/counts, never tokens or returned scalar field values.
Exit 2 means the app remains blocked; this tool does not change permissions.
"""
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
from loom_mcp import Loom
from maintenance_roles import private_write

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = {'managerUserId','ownerUserId','tenantUserId','userId'}
PROTECTED = IDENTITY | {'approvalGranted','approvalRequired','invoiceApproved','ownerApproved'}
RELATIONS = {'property','unit','tenancy','request','vendor','workOrders','propertyPermissions','vendorPermissions'}


def shape(value):
    if isinstance(value,dict):
        return {k:shape(v) for k,v in value.items()}
    if isinstance(value,list):
        return {'count':len(value),'items':[shape(v) for v in value[:3]]}
    return type(value).__name__


def paths(value, prefix=''):
    found=[]
    if isinstance(value,dict):
        for k,v in value.items():
            path=prefix+'.'+k if prefix else k
            found.append((path,k))
            found.extend(paths(v,path))
    elif isinstance(value,list):
        for v in value:
            found.extend(paths(v,prefix+'[]'))
    return found


def run():
    runtime=Path(os.environ['ZP_RUNTIME_DIR'])
    accounts=json.loads((runtime/'maintenance-test-accounts.json').read_text())
    bindings=json.loads((runtime/'maintenance-fixture-ids.json').read_text())
    manifest=json.loads((ROOT/'generation/roles/maintenance-native.json').read_text())
    base=json.loads((runtime/'loom.json').read_text())['backendURL'].rstrip('/')
    client=Loom()
    auth=[t['name'] for t in client.tools if t['name'].startswith('loom_native_auth_sign_in_')]
    if len(auth)!=1:
        raise RuntimeError('Expected one discovered Loom sign-in tool')
    results=[]
    for role,spec in manifest['roles'].items():
        key=role+'.1'; account=accounts[key]
        signed=client.call(auth[0],{'X-Authenticator':'basic','requestBody':{
            'email':account['email'],'password':account['password']}})
        token=signed['data']['token']
        own=bindings['1']['zp_work_orders'];foreign=bindings['2']['zp_work_orders']
        allowed=next(r['viewFields'] for r in spec['resources'] if r['name']=='zp_work_orders')
        def probe(label,path,params,*,empty=False,required=False,allowed_relations=None,required_relations=None):
            query=urllib.parse.urlencode(params)
            request=urllib.request.Request(base+'/'+path+('?' + query if query else ''),
                headers={'Authorization':'Bearer '+token,'X-Role':role,'Accept':'application/json'},method='GET')
            try:
                with urllib.request.urlopen(request,timeout=30) as response:
                    status=response.status; body=json.load(response)
            except urllib.error.HTTPError as error:
                status=error.code;body={}
            value=body.get('data') if isinstance(body,dict) else None
            findings=[]
            if status>=500:findings.append('server-error')
            if required and (status!=200 or not isinstance(value,dict) or value.get('id')!=own):
                findings.append('required-own-record-unavailable')
            for relation in required_relations or []:
                if not isinstance(value,dict) or not isinstance(value.get(relation),dict):
                    findings.append('required-context-unavailable:'+relation)
            if empty and status not in (400,403,404) and value:
                findings.append('foreign-or-forbidden-relation-disclosed')
            for path_name,k in paths(value):
                if k in PROTECTED:findings.append('protected-field:'+path_name)
            if isinstance(value,dict) and allowed_relations is not None:
                for relation in RELATIONS-set(allowed_relations):
                    if relation in value and value[relation] is not None:
                        findings.append('ungranted-relation:'+relation)
            result={'account':key,'case':label,'httpStatus':status,'passed':not findings,
                    'findings':sorted(set(findings)),'responseShape':shape(body)}
            results.append(result)
            private_write(runtime/'maintenance-read-security-results.json',{'status':'partial','results':results})
        appends=['property,unit,tenancy,request,vendor',
                 'request.tenancy,request.property,unit.property,vendor.propertyPermissions.property',
                 'property.vendorPermissions.vendor,request.workOrders.vendor']
        for index,append in enumerate(appends):
            probe('own-appends-'+str(index),'zp_work_orders:get',{'filterByTk':own,'appends':append},
                  allowed_relations=set(allowed)&RELATIONS)
            probe('foreign-appends-'+str(index),'zp_work_orders:get',{'filterByTk':foreign,'appends':append},empty=True)
        for label,field in [('scalars','id,state,approvalGranted,approvalRequired,propertyId,tenancyId,requestId,vendorId'),
                            ('nested','id,state,property.managerUserId,property.ownerUserId,tenancy.tenantUserId,vendor.userId,request.description')]:
            probe('own-fields-'+label,'zp_work_orders:get',{'filterByTk':own,'fields':field},required=True,
                  allowed_relations=set(allowed)&RELATIONS)
            probe('foreign-fields-'+label,'zp_work_orders:get',{'filterByTk':foreign,'fields':field},empty=True)
        for relation in ['property','unit','tenancy','request','vendor']:
            for suffix,row in [('own',own),('foreign',foreign)]:
                # Even an allowed relation must not bypass the parent's record scope.
                probe('association-'+suffix+'-'+relation,f'zp_work_orders/{row}/{relation}:get',{},
                      empty=(suffix=='foreign' or relation not in allowed))
        probe('baseline-own','zp_work_orders:get',{'filterByTk':own},required=True)
        # Manager context remains available via separately authorized native resources.
        if role=='zp_property_manager':
            probe('manager-work-order-context','zp_work_orders:get',
                  {'filterByTk':own,'appends':'property,unit,tenancy,request,vendor'},required=True,
                  allowed_relations=set(allowed)&RELATIONS,
                  required_relations=['property','unit','tenancy','request','vendor'])
            saved=own
            own=bindings['1']['zp_maintenance_requests']
            probe('manager-request-context','zp_maintenance_requests:get',
                  {'filterByTk':own,'appends':'property,unit,tenancy'},required=True,
                  allowed_relations=['property','unit','tenancy'],required_relations=['property','unit','tenancy'])
            own=saved
            for collection in ['zp_properties','zp_units','zp_tenancies','zp_maintenance_requests','zp_vendors']:
                saved=own
                own=bindings['1'][collection]
                probe('manager-context-'+collection,collection+':get',{'filterByTk':own},required=True)
                own=saved
        del token
    failures=[r for r in results if not r['passed']]
    result={'status':'blocked' if failures else 'passed','requestCount':len(results),
            'passedCount':len(results)-len(failures),'failedCount':len(failures),'results':results,
            'scope':'maintenance scalar/projection/append/association GET; no writes or reports'}
    private_write(runtime/'maintenance-read-security-results.json',result)
    print(json.dumps({k:result[k] for k in ['status','requestCount','passedCount','failedCount']}))
    return 2 if failures else 0


if __name__=='__main__':
    try:
        sys.exit(run())
    except Exception:
        print('Security read verification stopped; no raw backend error or credential was printed.',file=sys.stderr)
        sys.exit(1)
