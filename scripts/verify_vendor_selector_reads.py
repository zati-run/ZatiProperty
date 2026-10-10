#!/usr/bin/env python3
"""Read-only same-related-row and dynamic date selector qualification.

Precondition: vendor1 has mapping rows to both properties; vendor2 to property2.
The coordinator creates fixtures through Loom. This verifier performs only GETs
and Loom authentication/readback, never mapping or permission writes.
"""
import json,os,sys,urllib.request,urllib.parse,urllib.error
from pathlib import Path
from loom_mcp import Loom
from maintenance_roles import private_write
from verify_maintenance_writes import tool,unwrap
r=Path(os.environ['ZP_RUNTIME_DIR']);ids=json.loads((r/'maintenance-fixture-ids.json').read_text());accounts=json.loads((r/'maintenance-test-accounts.json').read_text());base=json.loads((r/'loom.json').read_text())['backendURL'].rstrip('/');root=Loom()
mappings=unwrap(root.call(tool(root,'resource_list'),{'resource':'zp_vendor_properties','pageSize':50}))
if isinstance(mappings,dict):mappings=mappings.get('rows',mappings.get('data'))
if not isinstance(mappings,list):raise RuntimeError('Cannot qualify mapping fixture readback')
pairs={(m['vendorId'],m['propertyId']) for m in mappings}
v1,v2=ids['1']['zp_vendors'],ids['2']['zp_vendors'];p1,p2=ids['1']['zp_properties'],ids['2']['zp_properties']
if not {(v1,p1),(v1,p2),(v2,p2)}<=pairs:raise RuntimeError('Mixed-map fixture precondition missing; no writes performed')
def response_shape(value):
    if isinstance(value,dict):return {key:response_shape(item) for key,item in value.items()}
    if isinstance(value,list):return {'count':len(value),'items':[response_shape(item) for item in value[:3]]}
    return type(value).__name__
results=[]
for actor,own,foreign,expected in [('zp_property_manager.1',p1,p2,{v1}),('zp_property_manager.2',p2,p1,{v1,v2})]:
    account=accounts[actor]
    token=unwrap(root.call(tool(root,'auth_sign_in'),{'X-Authenticator':'basic','requestBody':{'email':account['email'],'password':account['password']}}))['token']
    for label,prop,want in [('own',own,expected),('foreign',foreign,set()),('unresolved',None,set())]:
        for style in ['dotted','native-nested']:
            for dated in [False,True]:
                relation={'propertyPermissions.propertyId':{'$eq':prop}} if style=='dotted' else {'propertyPermissions':{'propertyId':{'$eq':prop}}}
                clauses=[relation]
                if dated:clauses += [{'active':{'$eq':True}},{'insuranceExpiresAt':{'$dateNotBefore':{'type':'today'}}},{'licenseExpiresAt':{'$dateNotBefore':{'type':'today'}}}]
                # Native picker wraps configured clauses in two enclosing groups.
                query_filter={'$and':[{'$and':clauses}]} if style=='native-nested' else {'$and':clauses}
                params={'filter':json.dumps(query_filter),'pageSize':40}
                request=urllib.request.Request(base+'/zp_vendors:list?'+urllib.parse.urlencode(params),headers={'Authorization':'Bearer '+token,'X-Role':account['role']},method='GET')
                try:
                    with urllib.request.urlopen(request,timeout=30) as response:status=response.status;body=json.load(response)
                except urllib.error.HTTPError as error:status=error.code;body={}
                data=body.get('data',[]);returned={v['id'] for v in data} if isinstance(data,list) else set()
                if label=='unresolved':valid=status in (400,403) and not returned
                else:valid=status==200 and (returned==want if dated or label=='foreign' else want<=returned)
                results.append({'account':actor,'scope':label,'queryStyle':style,'dynamicToday':dated,'httpStatus':status,'recordCount':len(returned),'expectedFixtureVendorsPresent':want<=returned,'passed':valid,'responseShape':response_shape(body)})
    del token
out={'status':'passed' if all(x['passed'] for x in results) else 'blocked','requestCount':len(results),'mixedMapPrecondition':'confirmed via Loom native readback','results':results}
private_write(r/'vendor-selector-read-results.json',out);print(json.dumps(out));sys.exit(0 if out['status']=='passed' else 2)
