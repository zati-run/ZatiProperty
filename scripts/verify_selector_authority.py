#!/usr/bin/env python3
"""Bounded selector companion constructor/CAS tests exclusively via Loom MCP."""
import argparse,datetime,json,os,pathlib,re,secrets
from loom_mcp import Loom
import verify_maintenance_writes as helpers
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--uid',default='bj2lik9byrf');args=p.parse_args()
if not args.run:
    print('Prepared six constructor/CAS negative cases; --run requires synthetic authority.')
    raise SystemExit(0)
runtime=pathlib.Path(os.environ['ZP_RUNTIME_DIR']);loom_dir=pathlib.Path(os.environ['ZP_LOOM_DIR']);config=json.loads((runtime/'loom.json').read_text());accounts=json.loads((runtime/'maintenance-test-accounts.json').read_text());root=Loom()
run_dir=runtime/'selector-auth-probes'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(3));run_dir.mkdir(parents=True,mode=0o700)
def read():return helpers.unwrap(root.call('lrs_scope_get',{'uid':args.uid}))
before=read();helpers.private_json(run_dir/'before.json',before)
predicates=[]
for item in before['scope']['filter']['items']:
    value=item['value']
    if item['operator']=='$dateNotBefore' and value=={'type':'today'}:predicate={'field':item['path'],'operator':'notExpired','value':{'today':True}}
    elif item['operator']=='$eq':
        if isinstance(value,str) and re.fullmatch(r'{{ ctx.record.[A-Za-z][A-Za-z0-9_]* }}',value):value={'currentRecordField':value[len('{{ ctx.record.'):-len(' }}')]}
        else:value={'literal':value}
        predicate={'field':item['path'],'operator':'eq','value':value}
    else:raise RuntimeError('Existing predicate not qualified for unchanged negative probe')
    predicates.append(predicate)
results=[]
def denied(client,case,tool,arguments,expected):
    status=None
    try:client.call(tool,arguments)
    except Exception as failure:
        match=re.search(r'(?:backend-error: |selector-scope-http-)(\d{3})',str(failure))
        status=int(match.group(1)) if match else None
    after=read()
    passed=status==expected and before==after
    result={'case':case,'expectedStatus':expected,'observedBackendStatus':status,'hashAndScopeUnchanged':before==after,'passed':passed}
    results.append(result);helpers.private_json(run_dir/(case+'.json'),result)
    if not passed:raise RuntimeError('Constructor/CAS probe failed; stop without retries')
denied(root,'root-stale-cas','lrs_scope_set',{'uid':args.uid,'expectedHash':'0'*64,'predicates':predicates},409)
helpers.ROLES['zp_owner.1']='zp_owner'
for actor in ['zp_property_manager.1','zp_owner.1','zp_tenant.1','zp_vendor.1']:
    with helpers.role_bridge(root,runtime,loom_dir,config,actor,accounts[actor],run_dir) as bridge:
        denied(bridge,actor+'-get-denied','lrs_scope_get',{'uid':args.uid},403)
        if actor=='zp_property_manager.1':denied(bridge,actor+'-set-denied','lrs_scope_set',{'uid':args.uid,'expectedHash':before['hash'],'predicates':predicates},403)
report={'status':'passed','caseCount':len(results),'results':results,'nativeSelectorUid':args.uid,'hash':before['hash'],'scopeUnchanged':read()==before,'transport':'role-specific Loom MCP only'}
helpers.private_json(run_dir/'result.json',report)
fd=os.open(runtime/'selector-authority-results.json',os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
with os.fdopen(fd,'w') as stream:json.dump(report,stream,indent=2)
print(json.dumps(report))
