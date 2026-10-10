#!/usr/bin/env python3
"""Loom-only MCP client. Private connection configuration stays outside Git.

Usage: ZP_RUNTIME_DIR=<private directory> python3 scripts/loom_mcp.py list
       ... schema <discovered tool name>
       ... call <discovered tool name> '<JSON arguments>'
Never retries mutations. An uncertain response requires native readback.
"""
import json, os, pathlib, ssl, sys, urllib.request

class Loom:
    def __init__(self, runtime=None):
        self.runtime = pathlib.Path(runtime or os.environ['ZP_RUNTIME_DIR'])
        config = json.loads((self.runtime / 'loom.json').read_text())
        self.url = f'https://localhost:{config["port"]}/native/mcp'
        self.token = (self.runtime / 'native-client-token').read_text().strip()
        self.context = ssl.create_default_context(cafile=str(self.runtime / 'tls-cert.pem'))
        self.counter = 0
        self.session = None
        self.rpc('initialize', {'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'zatiproperty-generation','version':'0.1.0'}})
        self.rpc('notifications/initialized', {}, notification=True)
        self.tools = []
        cursor = None
        seen = set()
        while True:
            result = self.rpc('tools/list', {'cursor':cursor} if cursor else {})
            self.tools.extend(result['tools'])
            cursor = result.get('nextCursor')
            if not cursor: break
            if cursor in seen: raise RuntimeError('repeated catalog cursor')
            seen.add(cursor)
        self.by_name = {t['name']:t for t in self.tools}
    def rpc(self, method, params, notification=False):
        self.counter += 1
        payload = {'jsonrpc':'2.0','method':method,'params':params}
        if not notification: payload['id'] = self.counter
        headers = {'Authorization':f'Bearer {self.token}', 'Content-Type':'application/json','Accept':'application/json, text/event-stream','MCP-Protocol-Version':'2025-03-26'}
        if self.session: headers['Mcp-Session-Id'] = self.session
        request = urllib.request.Request(self.url, data=json.dumps(payload).encode(), headers=headers)
        with urllib.request.urlopen(request, context=self.context, timeout=45) as response:
            self.session = response.headers.get('Mcp-Session-Id', self.session)
            raw = response.read().decode()
        if notification: return None
        if raw.startswith('event:') or raw.startswith('data:'):
            entries = [json.loads(line[5:].strip()) for line in raw.splitlines() if line.startswith('data:')]
            result = next((entry for entry in entries if entry.get('id') == self.counter), None)
        else: result = json.loads(raw)
        if not result or 'error' in result: raise RuntimeError('MCP response error: '+json.dumps(result))
        return result['result']
    def call(self, name, arguments=None):
        if name not in self.by_name: raise ValueError('tool absent from live catalog: '+name)
        result = self.rpc('tools/call', {'name':name,'arguments':arguments or {}})
        if result.get('isError'): raise RuntimeError('Loom tool error: '+json.dumps(result))
        texts = [x['text'] for x in result.get('content',[]) if x.get('type')=='text']
        if len(texts)==1:
            try: return json.loads(texts[0])
            except ValueError: return texts[0]
        return result

if __name__ == '__main__':
    client = Loom()
    action = sys.argv[1]
    if action == 'list': result = [{'name':t['name'],'description':t.get('description','')} for t in client.tools]
    elif action == 'schema': result = client.by_name[sys.argv[2]]
    elif action == 'call': result = client.call(sys.argv[2],json.loads(sys.argv[3]) if len(sys.argv)>3 else {})
    else: raise ValueError('expected list, schema, or call')
    print(json.dumps(result,indent=2))
