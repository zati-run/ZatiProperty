#!/usr/bin/env python3
"""Prepare/apply maintenance roles and synthetic users through discovered Loom MCP.

Default mode is offline inspection. --apply requires a coordinator-reviewed domain
plugin receipt. Does not create domain fixture records or grant arbitrary routes.
Private credentials and mutation journal stay in ZP_RUNTIME_DIR; output is redacted.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import sys
import urllib.request
import urllib.error
import urllib.parse
from loom_mcp import Loom

ROOT = Path(__file__).resolve().parents[1]
ROLE_FILE = ROOT / 'generation/roles/maintenance-native.json'
FIXTURE_FILE = ROOT / 'generation/fixtures/maintenance.json'


def data(value):
    return value.get('data', value) if isinstance(value, dict) else value


def rows(value):
    value = data(value)
    if not isinstance(value, list):
        raise RuntimeError('Expected native list response; reconcile catalog/response before retry')
    return value


def private_write(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(value, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())


class Apply:
    def __init__(self, client, runtime):
        self.client = client
        self.path = runtime / 'maintenance-role-journal.json'
        self.log = json.loads(self.path.read_text()) if self.path.exists() else []
        if any(entry['status'] == 'uncertain' for entry in self.log):
            raise RuntimeError('Previous uncertain mutation exists; coordinator must reconcile native state and journal first')

    def tool(self, prefix, description=None):
        matches = [t['name'] for t in self.client.tools if t['name'].startswith(prefix)
                   and (description is None or t.get('description') == description)]
        if len(matches) != 1:
            raise RuntimeError('Missing or ambiguous discovered tool: ' + prefix)
        return matches[0]

    def read(self, prefix, args=None, description=None):
        return self.client.call(self.tool(prefix, description), args or {})

    def write(self, prefix, args, description=None):
        tool = self.tool(prefix, description)
        # Never journal arguments: user-creation arguments contain credentials.
        entry = {'tool': tool, 'status': 'uncertain'}
        self.log.append(entry)
        private_write(self.path, self.log)
        result = self.client.call(tool, args)
        entry['status'] = 'returned'
        private_write(self.path, self.log)
        return result


def apply_roles(api, manifest, route_ids):
    current = {r['name']: r for r in rows(api.read('loom_native_roles_list_'))}
    for name, spec in manifest['roles'].items():
        expected = {'name': name, 'title': spec['title'], 'description': 'ZatiProperty synthetic maintenance role',
                    'default': False, 'allowConfigure': False, 'allowNewMenu': False,
                    'allowNewMobileMenu': False, 'allowNewAiEmployee': False,
                    'snippets': [], 'strategy': {'actions': []}}
        if name not in current:
            api.write('loom_native_roles_create_', {'requestBody': expected})
        else:
            actual = current[name]
            if any(actual.get(k) != expected[k] for k in ['description','allowConfigure','allowNewMenu','snippets','strategy']):
                raise RuntimeError('Existing role drift requires explicit reconciliation: ' + name)
        # Native role creation can ignore these flags and retain permissive
        # defaults. Re-read both new and existing owned roles, then tighten only.
        observed = data(api.read('loom_native_roles_get_', {'filterByTk': name}))
        if any(observed.get(k) != expected[k] for k in ['description','allowConfigure','allowNewMenu','snippets','strategy']):
            raise RuntimeError('Owned-role metadata drift after create/readback: ' + name)
        if observed.get('allowNewAiEmployee') is not False or observed.get('allowNewMobileMenu') is not False:
            api.write('loom_native_roles_update_', {'filterByTk':name,
                      'requestBody':{'allowNewAiEmployee':False,'allowNewMobileMenu':False}})
            observed = data(api.read('loom_native_roles_get_', {'filterByTk': name}))
        if (observed.get('snippets') or observed.get('strategy',{}).get('actions')
                or any(observed.get(k) is not False for k in ['allowConfigure','allowNewMenu','allowNewMobileMenu','allowNewAiEmployee'])):
            raise RuntimeError('Role has unexpected global permission grants')
        api.write('loom_native_data_sources_roles_update_', {'dataSourceKey':'main','filterByTk':name,
                  'requestBody':{'roleName':name,'dataSourceKey':'main','strategy':{'actions':[]}}})
        resources = []
        for resource in spec['resources']:
            scope_name = 'zp.maintenance.' + name + '.' + resource['name']
            existing = rows(api.read('loom_native_data_sources_roles_resources_scopes_',
                                    {'dataSourceKey':'main','pageSize':200,'filter':{'name':scope_name}},
                                    'List reusable ACL scopes in a data source'))
            if len(existing) > 1:
                raise RuntimeError('Ambiguous existing scope')
            if not existing:
                api.write('loom_native_data_sources_roles_resources_scopes_',
                          {'dataSourceKey':'main','requestBody':{'name':scope_name,'resourceName':resource['name'],
                           'scope':resource['scope']}},
                          'Create a reusable scope definition under the target data source.')
                existing = rows(api.read('loom_native_data_sources_roles_resources_scopes_',
                                          {'dataSourceKey':'main','pageSize':200,'filter':{'name':scope_name}},
                                          'List reusable ACL scopes in a data source'))
            if len(existing) != 1 or existing[0].get('scope') != resource['scope']:
                raise RuntimeError('Scope drift or missing native readback')
            scope_id = existing[0]['id']
            actions = [{'name':'view','fields':resource['viewFields'],'scopeId':scope_id}]
            if resource['updateFields']:
                actions.append({'name':'update','fields':resource['updateFields'],'scopeId':scope_id})
            resources.append({'name':resource['name'],'usingActionsConfig':True,'actions':actions})
        api.write('loom_native_roles_apply_data_permissions_',
                  {'filterByTk':name,'requestBody':{'dataSourceKey':'main','resources':resources}})
        # Route map is caller-supplied generated IDs; absent roles receive no pages.
        api.write('loom_native_roles_desktop_routes_set_', {'roleName':name,'requestBody':route_ids.get(name,[])})
        granted = rows(api.read('loom_native_roles_desktop_routes_list_',{'roleName':name,'paginate':False}))
        if sorted(r['id'] for r in granted) != sorted(route_ids.get(name,[])):
            raise RuntimeError('Route readback differs from explicit generated route IDs')
        # Per-resource effective permissions still require role-authenticated tests.


def apply_accounts(api, fixtures, runtime):
    path = runtime / 'maintenance-test-accounts.json'
    credentials = json.loads(path.read_text()) if path.exists() else {}
    existing_users = rows(api.read('loom_native_users_list_'))
    for fixture in fixtures['accounts']:
        key, email, role = fixture['key'], fixture['email'], fixture['role']
        matches = [u for u in existing_users if u.get('email') == email]
        if len(matches) > 1:
            raise RuntimeError('Duplicate synthetic user email')
        if key not in credentials:
            if matches:
                raise RuntimeError('Existing synthetic user is not owned by private fixture binding')
            credentials[key] = {'email':email,'role':role,'password':secrets.token_urlsafe(32),'status':'planned'}
            private_write(path, credentials)
        account = credentials[key]
        if not matches:
            api.write('loom_native_users_create_', {'requestBody':{'email':email,'username':key.replace('.','_'),
                      'nickname':'Synthetic '+key,'password':account['password']}})
            matches = [u for u in rows(api.read('loom_native_users_list_')) if u.get('email') == email]
        if len(matches) != 1:
            raise RuntimeError('User create outcome not established by readback')
        uid = matches[0]['id']
        if account.get('id') not in (None,uid):
            raise RuntimeError('Synthetic user ID drift')
        account['id'] = uid
        private_write(path, credentials)
        bound = rows(api.read('loom_native_users_roles_list_',{'userId':uid,'pageSize':100}))
        names = [r['name'] for r in bound]
        if 'root' in names or 'admin' in names:
            raise RuntimeError('Privileged user cannot be used as a portal fixture')
        if role not in names:
            api.write('loom_native_users_roles_add_',{'userId':uid,'filterByTk':[role]})
        extras = [r for r in names if r != role]
        if extras:
            api.write('loom_native_users_roles_remove_',{'userId':uid,'filterByTk':extras})
        final = rows(api.read('loom_native_users_roles_list_',{'userId':uid,'pageSize':100}))
        if [r['name'] for r in final] != [role]:
            raise RuntimeError('Fixture user must have exactly its isolated application role')
        account['status'] = 'role-bound-unverified'
        private_write(path, credentials)
    return len(credentials)


def verify_reads(manifest, runtime, binding_path):
    """Role-authenticated GET only; sign-in itself is mediated by Loom MCP.

    Bindings shape: {"1":{"zp_properties":1,...},"2":{...}}.
    Each scoped readable collection needs one native ID per synthetic graph.
    """
    bindings = json.loads(binding_path.read_text())
    accounts = json.loads((runtime / 'maintenance-test-accounts.json').read_text())
    config = json.loads((runtime / 'loom.json').read_text())
    base = config['backendURL'].rstrip('/') + '/'
    client = Loom()
    candidates = [t['name'] for t in client.tools if t['name'].startswith('loom_native_auth_sign_in_')]
    if len(candidates) != 1:
        raise RuntimeError('Missing or ambiguous Loom sign-in capability')
    shared_vendor = False
    eligibility_file = ROOT / 'generation/bindings/eligibility-fixtures.json'
    if eligibility_file.exists():
        rows_ = json.loads(eligibility_file.read_text()).get('records',[])
        mixed = [row for row in rows_ if row.get('key')=='mixedScopePermission' and row.get('state')=='observed']
        if mixed:
            read_tools = [t['name'] for t in client.tools if t['name'].startswith('loom_native_resource_get_')]
            if len(read_tools)!=1 or len(mixed)!=1:
                raise RuntimeError('Ambiguous mixed-scope fixture qualification')
            mapping=data(client.call(read_tools[0],{'resource':'zp_vendor_properties','filterByTk':mixed[0]['id']}))
            shared_vendor = mapping.get('vendorId')==bindings['1']['zp_vendors'] and mapping.get('propertyId')==bindings['2']['zp_properties']
            if not shared_vendor:
                raise RuntimeError('Mixed-scope fixture differs from declared read-sharing precondition')
    results = []
    join_denials = []
    for key, account in accounts.items():
        role = account['role']
        if role not in manifest['roles'] or account.get('status') != 'role-bound-unverified':
            raise RuntimeError('Unqualified synthetic role binding')
        own = key.rsplit('.', 1)[1]
        foreign = '2' if own == '1' else '1'
        signed = data(client.call(candidates[0], {'X-Authenticator':'basic',
                           'requestBody':{'email':account['email'],'password':account['password']}}))
        token = signed.get('token')
        if not isinstance(token,str) or not token:
            raise RuntimeError('Loom sign-in did not return a token')
        def get(resource, action, params=None):
            query = urllib.parse.urlencode(params or {})
            req = urllib.request.Request(base + resource + ':' + action + ('?' + query if query else ''),
                   headers={'Authorization':'Bearer '+token,'X-Role':role,'Accept':'application/json'})
            try:
                with urllib.request.urlopen(req,timeout=30) as response:
                    return response.status,json.loads(response.read())
            except urllib.error.HTTPError as err:
                return err.code,None
        check_status, check = get('roles','check')
        if check_status != 200:
            raise RuntimeError('Authenticated role context check failed')
        for resource in manifest['roles'][role]['resources']:
            collection = resource['name']
            own_id, foreign_id = bindings[own][collection], bindings[foreign][collection]
            status, result = get(collection,'get',{'filterByTk':own_id})
            record = data(result) if result else None
            if status != 200 or not isinstance(record,dict) or record.get('id') != own_id:
                raise RuntimeError('Own-record read denied or mismatched: '+json.dumps({'account':key,'resource':collection,'status':status,'expectedId':own_id,'returnedId':record.get('id') if isinstance(record,dict) else None}))
            forbidden = set(['approvalGranted','invoiceApproved','ownerApproved','managerUserId',
                             'ownerUserId','tenantUserId','userId'])
            if forbidden.intersection(record):
                raise RuntimeError('Protected field exposure')
            status, result = get(collection,'get',{'filterByTk':foreign_id})
            shared = shared_vendor and key=='zp_property_manager.2' and collection=='zp_vendors'
            if shared:
                visible=data(result) if result else None
                if status!=200 or not isinstance(visible,dict) or visible.get('id')!=foreign_id or forbidden.intersection(visible):
                    raise RuntimeError('Explicit shared vendor read or field isolation failed')
            elif status not in (403,404) and not (status == 200 and not data(result)):
                raise RuntimeError('Foreign-record read was not denied')
            foreign_get_status = status
            status, result = get(collection,'list',{'filter':json.dumps({'id':foreign_id})})
            if shared:
                visible=data(result) if result else None
                if status!=200 or not isinstance(visible,list) or len(visible)!=1 or visible[0].get('id')!=foreign_id or forbidden.intersection(visible[0]):
                    raise RuntimeError('Explicit shared vendor list or field isolation failed')
            elif status not in (403,404) and not (status == 200 and data(result) == []):
                raise RuntimeError('Foreign-record filtered list was not denied')
            results.append({'account':key,'resource':collection,'ownGet':'pass',
                            'foreignGet':'explicit-shared-vendor-allowed' if shared else 'denied','foreignList':'explicit-shared-vendor-allowed' if shared else 'denied','protectedFields':'absent',
                            'ownGetHttp':200,'foreignGetHttp':foreign_get_status,'foreignListHttp':status})
            private_write(runtime / 'maintenance-role-read-results.json',
                          {'evidence':'role-authenticated-native-GET','status':'partial','results':results})
        status, result = get('zp_vendor_properties','list')
        if role == 'zp_property_manager':
            if status != 200 or not isinstance(data(result),list):
                raise RuntimeError('Scoped manager vendor mapping read unavailable')
            foreign_id=bindings[foreign]['zp_vendor_properties']
            if any(row.get('id')==foreign_id for row in data(result)):
                raise RuntimeError('Foreign vendor mapping row exposed')
        elif status not in (403,404):
            raise RuntimeError('Constructor-owned vendor permission rows exposed to portal')
        join_denials.append({'account':key,'resource':'zp_vendor_properties','httpStatus':status,'expected':'scoped-manager-read' if role=='zp_property_manager' else 'denied'})
        # No tokens or complete raw responses are persisted.
        del token
    output = {'evidence':'role-authenticated-native-GET','results':results,'constructorJoinChecks':join_denials,
              'writes':'not tested; use role-bound Loom instance or native end-user UI',
              'appendsAndReports':'not tested by this bounded GET suite'}
    private_write(runtime / 'maintenance-role-read-results.json', output)
    print(json.dumps({'roleReadChecks':len(results),'status':'passed','writesVerified':False}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--verify-reads',action='store_true')
    parser.add_argument('--bindings',type=Path)
    parser.add_argument('--guard-receipt',type=Path)
    parser.add_argument('--routes',type=Path,help='JSON map role -> generated numeric native route IDs')
    parser.add_argument('--phase',choices=['roles','accounts','both'],default='both')
    args = parser.parse_args()
    manifest = json.loads(ROLE_FILE.read_text())
    fixtures = json.loads(FIXTURE_FILE.read_text())
    if args.verify_reads:
        if args.apply or not args.bindings or not args.bindings.is_file():
            parser.error('--verify-reads requires --bindings and excludes --apply')
        verify_reads(manifest,Path(os.environ['ZP_RUNTIME_DIR']),args.bindings)
        return
    if not args.apply:
        print(json.dumps({'mode':'offline-preparation','roles':len(manifest['roles']),
                          'accounts':len(fixtures['accounts']),'mutations':0}))
        return
    if not args.guard_receipt or not args.guard_receipt.is_file():
        parser.error('--apply requires a coordinator-reviewed domain plugin guard receipt')
    routes = json.loads(args.routes.read_text()) if args.routes else {}
    if not isinstance(routes,dict) or any(k not in manifest['roles'] or not isinstance(v,list)
           or any(type(i) is not int for i in v) for k,v in routes.items()):
        parser.error('routes must map known roles to explicit generated integer route IDs')
    runtime = Path(os.environ['ZP_RUNTIME_DIR'])
    api = Apply(Loom(), runtime)
    if args.phase in ('roles','both'):
        apply_roles(api,manifest,routes)
    count = apply_accounts(api,fixtures,runtime) if args.phase in ('accounts','both') else 0
    print(json.dumps({'status':'applied-pending-role-authenticated-verification','accounts':count,
                      'guardReceiptSha256':hashlib.sha256(args.guard_receipt.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Backend errors may echo secrets. Keep the diagnostic solely in the
        # already-private runtime directory, never in stdout, receipts or Git.
        runtime = os.environ.get('ZP_RUNTIME_DIR')
        if runtime:
            try:
                private_write(Path(runtime) / 'maintenance-role-private-error.json',
                              {'type':type(error).__name__,'message':str(error)})
            except Exception:
                pass
        print('Maintenance role operation stopped. Reconcile native state and the private mutation journal before retry.',file=sys.stderr)
        sys.exit(1)
