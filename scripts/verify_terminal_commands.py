#!/usr/bin/env python3
"""Source-only by default; coordinator must explicitly schedule --execute after 0.1.3."""
import argparse,concurrent.futures,datetime,hashlib,json,uuid,threading,jsonschema
from pathlib import Path
from loom_mcp import Loom
import verify_property_commands as base

BUSINESS=['zp_properties','zp_buildings','zp_units','zp_owner_contacts','zp_tenancies','zp_tenancy_parties','zp_tenancy_terms','zp_ownership_sets','zp_property_interests','zp_tenant_account_permissions']
def read_rows(client,resource):
    result=[]
    for page in range(1,22):
        response=client.call(base.tool(client,'loom_native_collectionname_list_'),{'collectionName':resource,'pageSize':50,'page':page,'sort':['id']})
        rows=base.unwrap(response)
        if not isinstance(rows,list) or len(rows)>50:raise RuntimeError('Invalid native page')
        result.extend(rows)
        if len(result)>1000:raise RuntimeError('Bounded snapshot cap')
        if len(rows)<50:return result
    raise RuntimeError('Bounded snapshot incomplete')

def digest(payload):
    return hashlib.sha256(json.dumps({k:v for k,v in payload.items() if k!='requestId'},sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def validate_receipt(value,payload,actor,action,outcome):
    expected={'receiptVersion':1,'actorId':str(actor),'commandAction':action,'requestId':payload['requestId'],'requestDigest':digest(payload),'status':outcome,'outcome':outcome}
    if any(value.get(k)!=v for k,v in expected.items()):raise AssertionError('Reconciliation binding mismatch')
    if outcome=='rejected' and value.get('code')!='INVALID_TEXT':raise AssertionError('Unexpected terminal code')
    if outcome=='rejected' and value.get('message')!='Enter the required text within the permitted length.':raise AssertionError('Unsafe or missing human feedback')
def error_code(error):
    prefix='Loom tool error: '
    if not str(error).startswith(prefix):raise RuntimeError('Uncertain transport outcome')
    outer=json.loads(str(error)[len(prefix):])
    for content in outer.get('content',[]):
        if content.get('type')!='text':continue
        packet=json.loads(content['text'])
        if packet.get('statusCode')!=409:continue
        for entry in packet.get('body',{}).get('errors',[]):
            if entry.get('code') in ['INVALID_TEXT','REQUEST_ID_COLLISION']:return entry['code']
    raise RuntimeError('Unclassified native outcome')
class Harness:
    def __init__(self,root):
        self.root=root;self.path=root.runtime/('terminal-native-'+uuid.uuid4().hex);self.path.mkdir(mode=0o700)
        self.results=[]
    def snapshot(self):
        return {r:read_rows(self.root,r) for r in [*base.AUDIT,*BUSINESS]}
    def before(self,label):
        value=self.snapshot();base.durable(self.path/(label+'.before.json'),value);return value
    def write(self,client,label,payload):
        base.durable(self.path/(label+'.intent.json'),{'action':'createProperty','payload':payload})
        try:result={'outcome':'committed','result':base.call(client,'createProperty',payload)}
        except Exception as error:result={'outcome':'error','code':error_code(error)}
        base.durable(self.path/(label+'.returned.json'),result)
        return result
    def lookup(self,client,payload,action='createProperty'):
        before=self.snapshot()
        result=base.call(client,'reconcileCommand',{'action':action,'requestId':payload['requestId']})
        if before!=self.snapshot():raise AssertionError('Read-only reconciliation mutated state')
        return result
    def transition(self,before,after,payload,outcome):
        base.verify_atomic({k:before[k] for k in base.AUDIT},{k:after[k] for k in base.AUDIT},1)
        for key in BUSINESS:
            delta=1 if outcome=='committed' and key=='zp_properties' else 0
            if len(after[key])-len(before[key])!=delta:raise AssertionError('Unexpected business change')
            if delta==0 and before[key]!=after[key]:raise AssertionError('Business values changed')
        old={str(r['id']) for r in before['zp_domain_commands']}
        receipt=next(r for r in after['zp_domain_commands'] if str(r['id']) not in old)
        if receipt['requestDigest']!=digest(payload):raise AssertionError('Stored digest mismatch')
        event=next(r for r in after['zp_domain_events'] if str(r['id'])==str(receipt['eventId']))
        outbox=next(r for r in after['zp_domain_outbox'] if str(r['eventId'])==str(receipt['eventId']))
        if outcome=='rejected':
            if outbox['status']!='suppressed':raise AssertionError('Rejected outbox could dispatch')
            body=json.loads(event['canonicalPayload'])
            if any(k in body for k in ['entityId','propertyId','previous','resulting']):raise AssertionError('Untrusted rejection entity audit')
            if body['requestDigest']!=digest(payload) or body['code']!='INVALID_TEXT':raise AssertionError('Rejection audit mismatch')
        return receipt

def execute(root):
    installed=base.unwrap(root.call(base.tool(root,'loom_native_pm_get_'),{'filterByTk':'@zati/plugin-property-tenancy'}))
    if installed.get('version')!='0.1.3' or installed.get('enabled') is not True:raise RuntimeError('Expected enabled domain0.1.3')
    q=Harness(root);accounts=json.loads((root.runtime/'maintenance-test-accounts.json').read_text())
    actor=str(accounts['zp_property_manager.1']['id'])
    def invalid():return {'requestId':str(uuid.uuid4()),'name':' ','reasonCode':'initial-setup'}
    with base.role_client(root,q,'terminal_manager','zp_property_manager','1',18462) as manager:
        legacy=[r for r in read_rows(root,'zp_domain_commands') if str(r['actorId'])==actor and r['action']=='createProperty' and 'commandReceiptVersion' not in json.loads(r['resultJSON'])]
        if not legacy:raise RuntimeError('Legacy committed fixture absent')
        old=legacy[0];before=q.snapshot()
        lookup=base.call(manager,'reconcileCommand',{'action':old['action'],'requestId':old['requestId']})
        if lookup.get('receiptVersion')!=1 or lookup.get('outcome')!='committed' or lookup.get('requestDigest')!=old['requestDigest'] or q.snapshot()!=before:raise AssertionError('Legacy normalization/read-only failure')
        q.results.append({'case':'legacy012-committed-normalization','passed':True})
        payload=invalid()
        jsonschema.validate({'requestBody':payload},manager.by_name[base.tool(manager,base.PREFIX+base.ACTIONS['createProperty'])]['inputSchema'])
        before=q.before('rejected-first')
        result=q.write(manager,'rejected-first',payload)
        if result!={'outcome':'error','code':'INVALID_TEXT'}:raise AssertionError('Expected validation rejection')
        q.transition(before,q.snapshot(),payload,'rejected')
        validate_receipt(q.lookup(manager,payload),payload,actor,'createProperty','rejected')
        for label in ['duplicate','late-identical']:
            before=q.before(label);result=q.write(manager,label,payload)
            if result!={'outcome':'error','code':'INVALID_TEXT'} or q.snapshot()!=before:raise AssertionError('Rejected replay changed state')
        changed={**payload,'name':'Synthetic collision'}
        before=q.before('changed-payload')
        if q.write(manager,'changed-payload',changed).get('code')!='REQUEST_ID_COLLISION' or q.snapshot()!=before:raise AssertionError('Collision changed state')
        try:validate_receipt(q.lookup(manager,payload),changed,actor,'createProperty','rejected')
        except AssertionError:pass
        else:raise AssertionError('Wrong digest accepted')
        q.results.append({'case':'terminal-rejection-duplicate-late-collision','passed':True})
        for action in ['createBuilding']:
            if q.lookup(manager,payload,action).get('status')!='not_observed':raise AssertionError('Cross-action receipt exposure')
        with base.role_client(root,q,'terminal_foreign','zp_property_manager','2',18463) as foreign:
            if q.lookup(foreign,payload).get('status')!='not_observed':raise AssertionError('Cross-actor receipt exposure')
        q.results.append({'case':'actor-action-digest-isolation','passed':True})
        with base.role_client(root,q,'terminal_parallel','zp_property_manager','1',18463) as parallel:
            for name,mixed in [('identical-invalid',False),('valid-invalid-collision',True)]:
                left=invalid();right={**left,'name':'Synthetic terminal race'} if mixed else dict(left)
                before=q.before(name)
                barrier=threading.Barrier(2)
                def concurrent_write(client,label,payload):
                    barrier.wait(timeout=10);return q.write(client,label,payload)
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                    futures=[pool.submit(concurrent_write,c,name+'-'+str(i),p) for i,(c,p) in enumerate([(manager,left),(parallel,right)])]
                    returned=[f.result() for f in futures]
                observed=q.lookup(manager,left);winner=right if observed.get('requestDigest')==digest(right) else left
                outcome=observed.get('outcome')
                if outcome not in ['rejected','committed'] or (not mixed and outcome!='rejected'):raise AssertionError('Race did not converge')
                validate_receipt(observed,winner,actor,'createProperty',outcome)
                q.transition(before,q.snapshot(),winner,outcome)
                expected_codes={'INVALID_TEXT','REQUEST_ID_COLLISION'} if mixed else {'INVALID_TEXT'}
                if any(r['outcome']=='error' and r['code'] not in expected_codes for r in returned):raise AssertionError('Unexpected race failure')
                q.results.append({'case':name,'outcome':outcome,'passed':True})
    result={'observedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceOnly':False,'cases':q.results,'scope':'Synthetic native Loom command qualification; no external dispatch'}
    base.durable(q.path/'sanitized-receipt.json',result)
    return result
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if not args.execute:print(json.dumps({'sourceOnly':True,'requires':'Coordinator scheduling and installed property-tenancy0.1.3'}));return
    root=Loom()
    print(json.dumps(execute(root)))
if __name__=='__main__':main()

