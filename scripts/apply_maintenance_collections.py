#!/usr/bin/env python3
"""Apply the reviewed maintenance collection batch through discovered Loom MCP.
No retries or adoption of unbound objects. Inspect native state after any failure.
"""
import hashlib,json,pathlib
from loom_mcp import Loom
root=pathlib.Path(__file__).resolve().parents[1]
c=Loom()
def tool(prefix):
 names=[n for n in c.by_name if n.startswith(prefix)]
 if len(names)!=1:raise RuntimeError('ambiguous catalog operation '+prefix)
 return names[0]
listing=tool('loom_native_collections_list_b')
create=tool('loom_native_collections_create_')
get=tool('loom_native_collections_get_')
bindings_file=root/'generation/bindings/collections.json'
bindings=json.loads(bindings_file.read_text()) if bindings_file.exists() else {}
observed={}
page=1
while True:
 result=c.call(listing,{'page':page,'pageSize':200})
 for item in result['data']:observed[item['name']]=item
 if page>=result.get('meta',{}).get('totalPage',page):break
 page+=1
source=root/'generation/collections/maintenance.json'
for values in json.loads(source.read_text()):
 name=values['name']
 if name in observed:
  if name not in bindings or bindings[name]['key']!=observed[name]['key']:raise RuntimeError('unowned collection collision '+name)
  print('already bound',name);continue
 intent={'operation':create,'arguments':{'requestBody':values},'outcome':'unknown-until-readback'}
 journal=c.runtime/(name+'-create.json')
 if journal.exists():raise RuntimeError('prior attempt needs explicit reconciliation '+name)
 journal.write_text(json.dumps(intent,indent=2));journal.chmod(0o600)
 result=c.call(create,{'requestBody':values})
 readback=c.call(get,{'filterByTk':name})
 native=readback['data']
 if native['name']!=name:raise RuntimeError('readback identity mismatch')
 bindings[name]={'logical_id':name.replace('zp_','zp.',1),'name':name,'key':native['key'],'source_sha256':hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest(),'operation':create,'schema_sha256':hashlib.sha256(json.dumps(c.by_name[create]['inputSchema'],sort_keys=True).encode()).hexdigest(),'status':'generated','readback':native}
 bindings_file.write_text(json.dumps(bindings,indent=2)+'\n')
 intent['outcome']='readback-confirmed';intent['native_key']=native['key'];journal.write_text(json.dumps(intent,indent=2))
 print('created and read back',name,native['key'])
print('Schema generation only; no domain, role or browser acceptance implied.')
