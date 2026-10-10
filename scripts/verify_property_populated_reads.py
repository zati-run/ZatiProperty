#!/usr/bin/env python3
"""Synthetic E3 read-only role matrix. Authentication through Loom; native GET only."""
import datetime,json,os,sys,urllib.error,urllib.parse,urllib.request
from pathlib import Path
from loom_mcp import Loom
ROOT=Path(__file__).resolve().parents[1]
REL={'property':'zp_properties','unit':'zp_units','building':'zp_buildings','portfolio':'zp_portfolios',
     'buildings':'zp_buildings','ownershipSets':'zp_ownership_sets','interests':'zp_property_interests',
     'ownerContact':'zp_owner_contacts','tenancy':'zp_tenancies','parties':'zp_tenancy_parties','terms':'zp_tenancy_terms'}
OWN={'zp_properties':4,'zp_buildings':1,'zp_units':3,'zp_owner_contacts':1}
FOREIGN={'zp_properties':2,'zp_units':2}
NEW=['zp_portfolios','zp_buildings','zp_owner_contacts','zp_ownership_sets','zp_property_interests','zp_tenancy_parties','zp_tenancy_terms','zp_tenant_account_permissions']
def ids(value):
    if value is None:return []
    if isinstance(value,dict):value=[value]
    return sorted(str(r['id']) for r in value if isinstance(r,dict) and 'id' in r)
def projections(value,resource,allowed,path='$'):
    errors=[]
    if value is None:return errors
    if isinstance(value,list):
        for row in value:errors+=projections(row,resource,allowed,path+'[]')
        return errors
    if not isinstance(value,dict):return ['unexpected-record-shape']
    for key,child in value.items():
        if key not in allowed.get(resource,set()):errors.append(path+'.'+key)
        if key in REL and isinstance(child,(dict,list)):errors+=projections(child,REL[key],allowed,path+'.'+key)
    return errors
def run():
    runtime=Path(os.environ['ZP_RUNTIME_DIR']);client=Loom()
    base=json.loads((runtime/'loom.json').read_text())['backendURL'].rstrip('/')
    accounts=json.loads((runtime/'maintenance-test-accounts.json').read_text())
    auth=[t['name'] for t in client.tools if t['name'].startswith('loom_native_auth_sign_in_')]
    if len(auth)!=1:raise RuntimeError('Missing/ambiguous Loom sign-in')
    overlay=json.loads((ROOT/'generation/roles/property-tenancy.json').read_text())
    maintenance=json.loads((ROOT/'generation/roles/maintenance-native.json').read_text())
    allowed={r['name']:set(r['viewFields']) for r in maintenance['roles']['zp_property_manager']['resources']}
    for r in overlay['resources']:allowed.setdefault(r['name'],set()).update(r['addViewFields'])
    allowed['zp_tenant_account_permissions']={'id','userId','displayName'}
    graph={}
    for resource,fields in [('zp_tenancies','id,unitId,draftRevision,leaseState,tenantUserId'),('zp_tenancy_parties','id,tenancyId,revision'),('zp_tenancy_terms','id,tenancyId,revision'),('zp_tenant_account_permissions','id,userId,managerUserId')]:
        graph[resource]=client.call('loom_native_collectionname_list_fb17e872f68689be',{'collectionName':resource,'fields':fields,'pageSize':50})['data']
    tenants=[r for r in graph['zp_tenancies'] if r['id'] in [4,5]]
    if len(tenants)!=2 or any(r['unitId']!=3 for r in tenants):raise RuntimeError('Fixture identity changed')
    populated={k:[r['id'] for r in graph[k] if r.get('tenancyId') in [4,5]] for k in ['zp_tenancy_parties','zp_tenancy_terms']}
    populated['zp_tenant_account_permissions']=[1]
    if not all(populated.values()):raise RuntimeError('Populated fixture missing')
    results=[]
    for role in ['zp_property_manager','zp_owner','zp_tenant','zp_vendor']:
      for suffix in ['1','2']:
        account_key=role+'.'+suffix;account=accounts[account_key]
        signed=client.call(auth[0],{'X-Authenticator':'basic','requestBody':{'email':account['email'],'password':account['password']}})
        token=signed['data']['token']
        def get(path,params):
            query=urllib.parse.urlencode(params,doseq=True)
            req=urllib.request.Request(base+'/'+path+('?' +query if query else ''),headers={'Authorization':'Bearer '+token,'X-Role':role,'Accept':'application/json'},method='GET')
            try:
                with urllib.request.urlopen(req,timeout=30) as response:return response.status,json.load(response)
            except urllib.error.HTTPError as e:return e.code,{}
        status,context=get('roles:check',{})
        if status!=200 or context.get('data',{}).get('role')!=role or context['data'].get('allowAll') is True or context['data'].get('allowConfigure') is True:
            raise RuntimeError('Unexpected effective role; no data matrix dispatched')
        def probe(label,path,params,resource,expected=None,deny=False,relation_ids=None):
            status,body=get(path,params);value=body.get('data') if isinstance(body,dict) else None
            problems=[]
            if deny:
                if not(status in [403,404] or status==200 and value in [None,[]]):problems.append('denied-data-visible')
            else:
                if status!=200:problems.append('expected-read-unavailable')
                if expected is not None and ids(value)!=sorted(str(x) for x in expected):problems.append('wrong-record-scope')
                problems+=projections(value,resource,allowed)
                if label.startswith('populated-fields:') and expected:
                    selected=value[0] if isinstance(value,list) else value
                    if not set(params['fields[]']).issubset(selected):problems.append('Requested allowed scalar fields missing')
                for relation,expected_ids in (relation_ids or {}).items():
                    if not isinstance(value,dict) or ids(value.get(relation))!=sorted(str(x) for x in expected_ids):problems.append('wrong-associated-scope:'+relation)
            if status>=500:problems.append('server-error')
            observed_keys=sorted(set().union(*(set(r) for r in (value if isinstance(value,list) else [value]) if isinstance(r,dict)))) if value else []
            results.append({'account':account_key,'case':label,'http':status,'recordIds':ids(value),'keys':observed_keys,'passed':not problems,'findings':problems})
        for resource,identifiers in populated.items():
            for identifier in identifiers:
                manager=role=='zp_property_manager' and suffix=='1'
                probe('populated-get:'+resource+':'+str(identifier),resource+':get',{'filterByTk':identifier},resource,expected=[identifier] if manager else None,deny=not manager)
                if role=='zp_property_manager':
                    fields=sorted(allowed[resource]-set(REL))
                    probe('populated-fields:'+resource+':'+str(identifier),resource+':get',{'filterByTk':identifier,'fields[]':fields},resource,expected=[identifier] if manager else None,deny=not manager)
        for resource in ['zp_tenancy_parties','zp_tenancy_terms']:
            for identifier in populated[resource]:
                manager=role=='zp_property_manager' and suffix=='1'
                parent=next(r['tenancyId'] for r in graph[resource] if r['id']==identifier)
                probe('nested-context:'+resource+':'+str(identifier),resource+':get',{'filterByTk':identifier,'appends[]':['tenancy.unit.property']},resource,expected=[identifier] if manager else None,deny=not manager,relation_ids={'tenancy':[parent]} if manager else None)
        for tenancy in tenants:
            for relation,target in [('parties','zp_tenancy_parties'),('terms','zp_tenancy_terms')]:
                expected=[r['id'] for r in graph[target] if r['tenancyId']==tenancy['id']]
                manager=role=='zp_property_manager' and suffix=='1'
                probe('populated-appends:'+str(tenancy['id'])+'.'+relation,'zp_tenancies:get',{'filterByTk':tenancy['id'],'appends[]':[relation]},'zp_tenancies',expected=[tenancy['id']] if manager else None,deny=not manager,relation_ids={relation:expected} if manager else None)
                probe('populated-association:'+str(tenancy['id'])+'.'+relation,'zp_tenancies/'+str(tenancy['id'])+'/'+relation+':list',{'pageSize':20},target,expected=expected if manager else None,deny=not manager)
                if role=='zp_property_manager':
                    current=[r['id'] for r in graph[target] if r['tenancyId']==tenancy['id'] and r['revision']==tenancy['draftRevision']]
                    probe('current-revision:'+str(tenancy['id'])+'.'+relation,target+':list',{'filter':json.dumps({'$and':[{'tenancyId':{'$eq':tenancy['id']}},{'revision':{'$eq':tenancy['draftRevision']}}]}),'pageSize':20},target,expected=current if manager else [])
        for resource,identifier,field in [('zp_tenant_account_permissions',1,'managerUserId'),('zp_tenant_account_permissions',1,'mappingKey'),('zp_tenancy_parties',3,'userId')]:
            probe('private-field:'+resource+'.'+field,resource+':get',{'filterByTk':identifier,'fields[]':['id',field]},resource,deny=True)
        probe('no-generic-user-enumeration','users:list',{'pageSize':20,'fields[]':['id','nickname']},'users',deny=True)
    result={'observedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'native synthetic role GET matrix; no app writes','caseCount':len(results),'passed':sum(r['passed'] for r in results),'cases':results,'fixtureGraph':graph,'limitations':['Ownership fixtures absent; no populated ownership acceptance','No generic writes or rendered UI checks']}
    out=ROOT/'docs/generation/receipts/property-populated-nested-role-read-results.json'
    if out.exists():raise RuntimeError('Preserve prior receipt before rerun')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'caseCount':len(results),'passed':result['passed'],'failed':len(results)-result['passed']}))
    if result['passed']!=len(results):raise SystemExit(2)
if __name__=='__main__':run()

