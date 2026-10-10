#!/usr/bin/env python3
"""Additive Loom-only schema preparation. Default inspection; explicit --apply.
Unresolved durable intents block all replay and require independent reconciliation.
"""
import argparse, hashlib, json, os
from pathlib import Path
from loom_mcp import Loom
ROOT=Path(__file__).resolve().parents[1]
def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def durable(path,value):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as out:
        json.dump(value,out,indent=2); out.flush(); os.fsync(out.fileno())
    syncdir(path.parent)
def syncdir(path):
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)
def subset(want,got):
    if isinstance(want,dict):
        if not isinstance(got,dict): raise RuntimeError('Metadata shape mismatch')
        for key,value in want.items():
            if key not in got: raise RuntimeError('Metadata key missing: '+key)
            subset(value,got[key])
    elif want != got: raise RuntimeError('Metadata drift')
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--apply',action='store_true'); p.add_argument('--reconcile',action='store_true'); p.add_argument('--commands',action='store_true',help='Separate reviewed command-receipt migration with immutable parent ownership chain'); args=p.parse_args()
    if args.apply and args.reconcile: p.error('--reconcile is read-only')
    parent_spec=json.loads((ROOT/'generation/collections/property-tenancy.json').read_text())
    spec=json.loads((ROOT/'generation/collections/property-tenancy-commands.json').read_text()) if args.commands else parent_spec
    runtime=Path(os.environ['ZP_RUNTIME_DIR'])
    prefix='property-command-schema' if args.commands else 'property-schema'
    intent=runtime/(prefix+'-intent.json'); binding=runtime/(prefix+'-bindings.json')
    parent=None
    if args.commands:
        if (runtime/'property-schema-intent.json').exists(): raise RuntimeError('Parent migration has unresolved intent')
        parent=json.loads((runtime/'property-schema-bindings.json').read_text())
        if parent['specDigest']!=spec['parentSpecDigest'] or digest(parent_spec)!=spec['parentSpecDigest']: raise RuntimeError('Parent specification/ownership digest mismatch')
    if intent.exists() and not args.reconcile: raise RuntimeError('Unresolved intent: independent native readback required before any retry')
    state=json.loads(binding.read_text()) if binding.exists() else {'specDigest':digest(spec),'collections':{},'fields':{}}
    if state['specDigest']!=digest(spec): raise RuntimeError('Specification changed; separate migration review required')
    base={x['name']:x['key'] for x in json.loads((ROOT/'generation/bindings/collections.json').read_text()).values()}
    if parent: base.update(parent['collections'])
    client=Loom()
    def tool(prefix):
        names=[x['name'] for x in client.tools if x['name'].startswith(prefix)]
        if len(names)!=1: raise RuntimeError('Missing/ambiguous capability: '+prefix)
        return names[0]
    get=tool('loom_native_collections_get_')
    listing=tool('loom_native_collections_list_b')
    create=tool('loom_native_collections_create_')
    add=tool('loom_native_collections_fields_create_')
    def data(value): return value.get('data',value)
    rows=data(client.call(listing,{'paginate':False}))
    if not isinstance(rows,list): raise RuntimeError('Unexpected inventory')
    inventory={x['name']:x for x in rows}
    def read(name):
        row=data(client.call(get,{'filterByTk':name,'appends':['fields']}))
        if row.get('name')!=name or not isinstance(row.get('fields'),list): raise RuntimeError('Invalid collection readback')
        return row
    if args.reconcile:
        if not intent.exists(): raise RuntimeError('No unresolved intent')
        attempt=json.loads(intent.read_text())
        if attempt['specDigest']!=digest(spec): raise RuntimeError('Intent specification changed')
        name=attempt['collection']; desired=attempt['desired']
        outcome='absent'
        if name in inventory:
            row=read(name)
            if attempt['kind']=='collection':
                subset({k:v for k,v in desired.items() if k!='fields'},row)
                fields={f['name']:f for f in row['fields']}
                for field in desired['fields']: subset(field,fields.get(field['name']))
                outcome='present-matching-unadopted'
            else:
                if row['key']!=attempt['before']['key']: raise RuntimeError('Collection identity changed')
                fields={f['name']:f for f in row['fields']}
                for old in attempt['before']['fields']:
                    if fields.get(old['name'])!=old: raise RuntimeError('Preexisting field drift')
                if desired['name'] in fields:
                    subset(desired,fields[desired['name']]); outcome='present-matching-unadopted'
        print(json.dumps({'reconciliation':outcome,'intentRetained':True,'retryAuthorized':False}))
        return
    def owned(name):
        row=read(name); key=base.get(name) or state['collections'].get(name)
        if key is None or row.get('key')!=key: raise RuntimeError('Unowned collection collision: '+name)
        return row
    if parent:
        # Parent IDs and all explicitly authored metadata must still match.
        for collection in parent_spec['collections']:
            row=owned(collection['name'])
            subset({k:v for k,v in collection.items() if k!='fields'},row)
            fields={f['name']:f for f in row['fields']}
            for field in collection['fields']: subset(field,fields.get(field['name']))
        for item in parent_spec['addFields']:
            row=owned(item['collection']); fields={f['name']:f for f in row['fields']}
            identity=item['collection']+'.'+item['field']['name']
            if fields.get(item['field']['name'],{}).get('key')!=parent['fields'].get(identity): raise RuntimeError('Parent field identity drift')
            subset(item['field'],fields.get(item['field']['name']))
    pending=[]
    for desired in spec['collections']:
        name=desired['name']
        if name not in inventory: pending.append(('collection',name,desired)); continue
        row=owned(name)
        subset({k:v for k,v in desired.items() if k!='fields'},row)
        fields={f['name']:f for f in row['fields']}
        for field in desired['fields']: subset(field,fields.get(field['name']))
    for addition in spec['addFields']:
        name,field=addition['collection'],addition['field']; identity=name+'.'+field['name']
        if name not in inventory:
            if name not in {c['name'] for c in spec['collections']}: raise RuntimeError('Missing base collection')
            pending.append(('field',name,field)); continue
        row=owned(name); fields={f['name']:f for f in row['fields']}
        if field['name'] not in fields: pending.append(('field',name,field)); continue
        if identity not in state['fields'] or state['fields'][identity]!=fields[field['name']]['key']: raise RuntimeError('Unowned field collision: '+identity)
        subset(field,fields[field['name']])
    print(json.dumps({'mode':'apply' if args.apply else 'inspect','pendingOperations':len(pending),'specDigest':digest(spec)}))
    if not args.apply: return
    for kind,name,desired in pending:
        before=owned(name) if kind=='field' else None
        if before and any(f['name']==desired['name'] for f in before['fields']): raise RuntimeError('Concurrent field collision')
        durable(intent,{'kind':kind,'collection':name,'desired':desired,'before':before,'specDigest':digest(spec)})
        client.call(create if kind=='collection' else add,{'requestBody':desired} if kind=='collection' else {'collectionName':name,'requestBody':desired})
        row=read(name); fields={f['name']:f for f in row['fields']}
        if kind=='collection':
            subset({k:v for k,v in desired.items() if k!='fields'},row)
            for field in desired['fields']: subset(field,fields.get(field['name']))
            state['collections'][name]=row['key']
        else:
            subset(desired,fields.get(desired['name']))
            for old in before['fields']:
                if fields.get(old['name'])!=old: raise RuntimeError('Existing field changed during additive operation')
            state['fields'][name+'.'+desired['name']]=fields[desired['name']]['key']
        tmp=binding.with_suffix('.tmp'); durable(tmp,state); os.replace(tmp,binding); syncdir(runtime)
        intent.unlink(); syncdir(runtime)
    print(json.dumps({'completedOperations':len(pending),'appAcceptance':False}))
if __name__=='__main__': main()

