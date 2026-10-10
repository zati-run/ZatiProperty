#!/usr/bin/env python3
"""Bounded read-navigation apply through Loom. Capture, review, then explicit phase.
Fresh-read drift fences are not atomic server CAS; require one mutation lane.
"""
import argparse, copy, json, os
from pathlib import Path
from loom_mcp import Loom
from prepare_property_ui import merge_actions
from property_ui_journal import dispatch_once, sha as digest
ROOT=Path(__file__).resolve().parents[1]
ROLE='zp_property_manager'
PORTALS=['zp_owner','zp_tenant','zp_vendor']
SNIPPET='pm.@zati/plugin-property-tenancy.manager'

def rows(value):
    value=value.get('data',value) if isinstance(value,dict) else value
    if not isinstance(value,list):raise RuntimeError('Unexpected list readback')
    return value

def data(value):
    return value.get('data',value)

def resource_map(value):
    return {r['name']:r for r in rows(value)}

def action_clean(actions):
    result=[]
    for action in actions:
        result.append({k:v for k,v in action.items() if k in ['name','fields','scopeId']})
    return sorted(result,key=lambda x:x['name'])

def canonical_resource(resource):
    return {'name':resource['name'],'usingActionsConfig':resource.get('usingActionsConfig',False),
            'actions':action_clean(resource.get('actions',[]))}


def page_binding(surface,desired,empty=False):
    value=data(surface);page=value.get('pageRoute',{});tree=value.get('tree',{})
    if page.get('schemaUid')!=desired['pageSchemaUid'] or tree.get('uid')!=desired['pageUid'] or tree.get('use')!='RootPageModel':raise RuntimeError('Page identity mismatch')
    for key in ['title','icon','enableHeader']:
        if page.get(key)!=desired.get(key) or tree.get('props',{}).get(key)!=desired.get(key):raise RuntimeError('Page presentation mismatch')
    tabs=tree.get('subModels',{}).get('tabs',[]);children=page.get('children',[])
    if len(tabs)!=1 or len(children)!=1:raise RuntimeError('Expected single native tab')
    tab=tabs[0];route=tab.get('props',{}).get('route',{});grid=tab.get('subModels',{}).get('grid',{})
    if tab.get('use')!='RootPageTabModel' or route.get('parentId')!=page.get('id') or route.get('schemaUid')!=tab.get('uid') or children[0].get('id')!=route.get('id') or grid.get('use')!='BlockGridModel' or grid.get('parentId')!=tab.get('uid'):raise RuntimeError('Page relation mismatch')
    if route.get('title')!='Untitled' or route.get('hidden') is not True or route.get('type')!='tabs':raise RuntimeError('Unexpected default tab')
    if empty and grid.get('subModels'):raise RuntimeError('Owned grid is not empty')
    binding={'pageSchemaUid':desired['pageSchemaUid'],'pageUid':tree['uid'],'gridUid':grid.get('uid'),'menuRouteId':page.get('id'),'tabRouteId':route.get('id'),'tabUid':tab.get('uid')}
    if not all(binding.values()):raise RuntimeError('Incomplete native binding')
    return binding

def atomic_receipt(path,value):
    import tempfile
    fd,temp=tempfile.mkstemp(prefix='.reconcile-',dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
        os.link(temp,path) # exclusive publication: never overwrite another observation
        directory=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:os.unlink(temp)

class Journal:
    def __init__(self,path):
        self.path=path;self.path.mkdir(mode=0o700,exist_ok=True);self.before={}
    def run(self,key,client,name,args,verify):
        if (self.path/(key+'.json')).exists():raise RuntimeError('prior intent/result exists; reconcile before replay')
        box={}
        class Capture:
            def call(self,tool,payload):
                box['response']=client.call(tool,payload);return box['response']
        receipt=dispatch_once(Capture(),name,args,self.path/(key+'.json'),self.before,
                              lambda:verify(box['response']),lambda _:True)
        return receipt['after']

class Apply:
    def __init__(self,client,baseline,manifest,journal):
        self.c=client;self.baseline=baseline;self.manifest=manifest;self.journal=journal
    def tool(self,prefix):
        names=[t['name'] for t in self.c.tools if t['name'].startswith(prefix) and '_' not in t['name'][len(prefix):]]
        if len(names)!=1:raise RuntimeError('Missing/ambiguous native capability: '+prefix)
        return names[0]
    def read(self,prefix,args):return self.c.call(self.tool(prefix),args)
    def snapshot(self,role):
        resources=[]
        names=set(self.manifest['resources'])|{'zp_maintenance_requests','zp_work_orders','zp_vendors','zp_vendor_properties','zp_domain_events','zp_domain_outbox','zp_audit_heads','zp_domain_commands'}
        for name in sorted(names):
            result=data(self.read('loom_native_roles_data_source_resources_get_',{'roleName':role,'dataSourceKey':'main','name':name,'appends':['actions']}))
            if result:resources.append(result)
        return {'role':data(self.read('loom_native_roles_get_',{'filterByTk':role})),
          'permissions':resources,
          'strategy':data(self.read('loom_native_data_sources_roles_get_',{'dataSourceKey':'main','filterByTk':role})),
          'routes':rows(self.read('loom_native_roles_desktop_routes_list_',{'roleName':role,'paginate':False}))}
    def guard(self):
        for role,expected in self.baseline['roles'].items():
            if digest(self.snapshot(role))!=digest(expected):raise RuntimeError('Role baseline drift: '+role)
    def scope_rows(self):
        return rows(self.c.call('loom_native_data_sources_roles_resources_scopes_beaae09b053b48e0',{'dataSourceKey':'main','pageSize':200}))
    def scopes(self,apply=False):
        inventory=self.scope_rows();found={};pending=[]
        for name,desired in self.manifest['resources'].items():
            matches=[s for s in inventory if s.get('resourceName')==name and s.get('scope')==desired['scope']]
            if len(matches)>1:raise RuntimeError('Ambiguous scope: '+name)
            if matches:found[name]=matches[0]['id']
            else:pending.append(name)
        if not apply:return found,pending
        for name in pending:
            self.guard()
            desired={'name':'E3 manager '+name,'resourceName':name,'scope':self.manifest['resources'][name]['scope']}
            def verify(_response,name=name,desired=desired):
                matches=[s for s in self.scope_rows() if s.get('resourceName')==name and s.get('scope')==desired['scope']]
                if len(matches)!=1:raise RuntimeError('Uncertain scope creation')
                return matches[0]
            result=self.journal.run('scope-'+name,self.c,'loom_native_data_sources_roles_resources_scopes_03b123eabb11e89c',{'dataSourceKey':'main','requestBody':desired},verify)
            found[name]=result['id']
        return found,pending
    def permissions(self):
        scope_ids,_=self.scopes(apply=True);self.guard()
        before=self.baseline['roles'][ROLE];existing={r['name']:r for r in before['permissions']}
        payload=[]
        for name,desired in self.manifest['resources'].items():
            old=existing.get(name,{'name':name,'actions':[]})
            if old.get('actions') and old.get('usingActionsConfig') is not True:raise RuntimeError('Existing resource uses inherited strategy')
            payload.append({'name':name,'usingActionsConfig':True,'actions':merge_actions(old.get('actions',[]),desired['fields'],scope_ids[name])})
        def verify(_):
            after=self.snapshot(ROLE);actual={r['name']:r for r in after['permissions']}
            for wanted in payload:
                if canonical_resource(actual.get(wanted['name'],{}))!=canonical_resource(wanted):raise RuntimeError('Permission readback mismatch')
            for name,prior in existing.items():
                if name not in self.manifest['resources'] and canonical_resource(actual.get(name,{}))!=canonical_resource(prior):raise RuntimeError('Unrelated permission changed')
            for key in ['role','strategy','routes']:
                if after[key]!=before[key]:raise RuntimeError('Unrelated role state changed')
            for role in PORTALS:
                if self.snapshot(role)!=self.baseline['roles'][role]:raise RuntimeError('Portal changed')
            return after
        return self.journal.run('manager-read-permissions',self.c,self.tool('loom_native_roles_apply_data_permissions_'),{'filterByTk':ROLE,'requestBody':{'dataSourceKey':'main','resources':payload}},verify)
    def snippet(self,qualified):
        if qualified!=SNIPPET:raise RuntimeError('Installed manager snippet must be qualified explicitly')
        self.guard();before=self.baseline['roles'][ROLE];role=before['role']
        snippets=role.get('snippets',[])
        if not isinstance(snippets,list) or any('constructor' in s for s in snippets):raise RuntimeError('Unexpected constructor permission in manager')
        wanted=list(dict.fromkeys([*snippets,SNIPPET]))
        def verify(_):
            after=self.snapshot(ROLE)
            if set(after['role'].get('snippets',[]))!=set(wanted):raise RuntimeError('Snippet readback mismatch')
            for key in ['allowConfigure','allowNewMenu','allowNewAiEmployee','allowAll','strategy']:
                if after['role'].get(key)!=role.get(key):raise RuntimeError('Role authority drift')
            for key in ['permissions','strategy','routes']:
                if after[key]!=before[key]:raise RuntimeError('Unexpected role side effect')
            for portal in PORTALS:
                if self.snapshot(portal)!=self.baseline['roles'][portal]:raise RuntimeError('Portal changed')
            return after
        return self.journal.run('manager-domain-snippet',self.c,self.tool('loom_native_roles_update_'),{'filterByTk':ROLE,'requestBody':{'snippets':wanted}},verify)
    def reconcile_page(self,key):
        if key not in ['portfolio','tenancies']:raise RuntimeError('Unknown owned page')
        desired=json.loads((ROOT/f'generation/pages/{key}.json').read_text())
        path=self.journal.path/('page-'+key+'.json')
        original=json.loads(path.read_text())
        expected={'requestBody':desired['page']}
        if original.get('tool')!=self.tool('loom_native_flow_surfaces_create_page_') or original.get('arguments')!=expected or original.get('beforeHash')!=digest(self.baseline):raise RuntimeError('Pending intent ownership mismatch')
        if original.get('state')!='pending-or-unknown':raise RuntimeError('Expected pending create intent')
        if (self.journal.path/('compose-'+key+'.json')).exists():raise RuntimeError('Compose intent requires separate reconciliation')
        surface=self.read('loom_native_flow_surfaces_get_',{'pageSchemaUid':desired['page']['pageSchemaUid']})
        result={'binding':page_binding(surface,desired['page'],True),'surface':surface}
        atomic_receipt(self.journal.path/('page-'+key+'-reconciled.json'),{'originalHash':digest(original),'beforeHash':digest(self.baseline),'arguments':expected,'after':result})
        return result

    def resume_created(self,key,desired):
        path=self.journal.path/('page-'+key+'.json')
        original=json.loads(path.read_text())
        if original.get('tool')!=self.tool('loom_native_flow_surfaces_create_page_') or original.get('arguments')!={'requestBody':desired['page']} or original.get('beforeHash')!=digest(self.baseline):raise RuntimeError('Create journal mismatch')
        observed=self.journal.path/('page-'+key+'-reconciled.json')
        if observed.exists():
            receipt=json.loads(observed.read_text())
            if receipt.get('originalHash')!=digest(original) or receipt.get('beforeHash')!=digest(self.baseline) or receipt.get('arguments')!=original['arguments']:raise RuntimeError('Reconciliation receipt mismatch')
        elif original.get('state')=='verified':receipt=original
        else:raise RuntimeError('Pending create requires explicit read-only reconciliation')
        surface=self.read('loom_native_flow_surfaces_get_',{'pageSchemaUid':desired['page']['pageSchemaUid']})
        binding=page_binding(surface,desired['page'],True)
        if binding!=receipt.get('after',{}).get('binding'):raise RuntimeError('Observed binding changed')
        return {'binding':binding,'surface':surface}

    def pages(self,resume=False):
        results={}
        for key in ['portfolio','tenancies']:
            if (self.journal.path/('compose-'+key+'.json')).exists():raise RuntimeError('Prior compose intent/result requires separate reconciliation')
        all_routes=data(self.read('loom_native_desktop_routes_list_accessible_',{'tree':True}))
        def schema_uids(value):
            if isinstance(value,dict):
                return ([value['schemaUid']] if 'schemaUid' in value else [])+[x for v in value.values() for x in schema_uids(v)]
            if isinstance(value,list):return [x for v in value for x in schema_uids(v)]
            return []
        occupied=schema_uids(all_routes)
        for key in ['portfolio','tenancies']:
            desired=json.loads((ROOT/f'generation/pages/{key}.json').read_text())
            pending=(self.journal.path/('page-'+key+'.json')).exists()
            if (self.journal.path/('compose-'+key+'.json')).exists():raise RuntimeError('Prior compose intent/result requires separate reconciliation')
            if pending:
                if not resume:raise RuntimeError('Prior create requires explicit resume')
                created=self.resume_created(key,desired)
            else:
                if desired['page']['pageSchemaUid'] in occupied:raise RuntimeError('Unowned page collision')
                def verify(response):
                    surface=self.read('loom_native_flow_surfaces_get_',{'pageSchemaUid':desired['page']['pageSchemaUid']})
                    return {'binding':page_binding(surface,desired['page'],True),'surface':surface}
                created=self.journal.run('page-'+key,self.c,self.tool('loom_native_flow_surfaces_create_page_'),{'requestBody':desired['page']},verify)
            binding=created['binding']
            before=data(self.read('loom_native_flow_surfaces_get_',{'uid':binding['gridUid']}))
            if before['tree'].get('subModels',{}).get('items'):raise RuntimeError('New target grid not empty')
            args={'requestBody':{'target':{'uid':binding['gridUid']},**desired['compose']}}
            composed=self.journal.run('compose-'+key,self.c,self.tool('loom_native_flow_surfaces_compose_'),args,lambda _:self.read('loom_native_flow_surfaces_get_',{'pageSchemaUid':binding['pageSchemaUid']}))
            results[key]={'binding':binding,'surface':composed}
        return results


    def owned_pages(self):
        saved=json.loads((self.c.runtime/'property-ui-pages-result.json').read_text())
        output={}
        for key,record in saved.items():
            if key not in ['portfolio','tenancies']:raise RuntimeError('Unexpected page binding')
            binding=record['binding'];surface=self.read('loom_native_flow_surfaces_get_',{'pageSchemaUid':binding['pageSchemaUid']})
            page=data(surface).get('pageRoute',{})
            if str(page.get('id'))!=str(binding['menuRouteId']):raise RuntimeError('Page route identity changed')
            output[key]={'binding':binding,'surface':surface}
        if set(output)!={'portfolio','tenancies'}:raise RuntimeError('Incomplete owned page bindings')
        return output
    def unsafe(self,surface):
        nodes=data(surface).get('nodeMap',{})
        if not isinstance(nodes,dict) or len(nodes)>1000:raise RuntimeError('Unexpected/bounded node readback exceeded')
        safe={'ViewActionModel','FilterActionModel','RefreshActionModel'}
        removable={'AddNewActionModel','CreateActionModel','EditActionModel','DeleteActionModel','BulkDeleteActionModel','UpdateActionModel','FormSubmitActionModel'}
        found=[]
        for uid,node in nodes.items():
            use=node.get('use','')
            if use.endswith('ActionModel') and use not in safe:
                if use not in removable:raise RuntimeError('Unqualified action model: '+use)
                found.append(uid)
            if use in ['JSBlockModel','JSActionModel','IframeBlockModel']:raise RuntimeError('Unexpected executable UI')
        return found
    def cleanup(self):
        pages=self.owned_pages()
        for key,page in pages.items():
            unsafe=self.unsafe(page['surface'])
            if len(unsafe)>50:raise RuntimeError('Unexpected autogenerated action count')
            for uid in unsafe:
                current=self.read('loom_native_flow_surfaces_get_',{'pageSchemaUid':page['binding']['pageSchemaUid']})
                if uid not in data(current)['nodeMap']:continue
                def verify(_,page=page,uid=uid):
                    after=self.read('loom_native_flow_surfaces_get_',{'pageSchemaUid':page['binding']['pageSchemaUid']})
                    if uid in data(after)['nodeMap']:raise RuntimeError('Action removal uncertain')
                    return after
                self.journal.run('remove-'+uid,self.c,self.tool('loom_native_flow_surfaces_remove_node_'),{'requestBody':{'target':{'uid':uid}}},verify)
        after=self.owned_pages()
        for page in after.values():
            if self.unsafe(page['surface']):raise RuntimeError('Mutable UI action remains')
        return after
    def routes(self,approved):
        pages=self.owned_pages()
        if digest(pages)!=approved:raise RuntimeError('Reviewed native page digest required')
        for page in pages.values():
            if self.unsafe(page['surface']):raise RuntimeError('Mutable UI actions block route grants')
        self.guard();before=self.baseline['roles'][ROLE]
        wanted=sorted(set([int(r['id']) for r in before['routes']]+[int(p['binding'][key]) for p in pages.values() for key in ['menuRouteId','tabRouteId']]))
        def verify(_):
            after=self.snapshot(ROLE)
            if sorted(int(r['id']) for r in after['routes'])!=wanted:raise RuntimeError('Route grant readback mismatch')
            for key in ['role','permissions','strategy']:
                if after[key]!=before[key]:raise RuntimeError('Route update changed role authority')
            for role in PORTALS:
                if self.snapshot(role)!=self.baseline['roles'][role]:raise RuntimeError('Portal changed')
            return after
        return self.journal.run('manager-page-routes',self.c,self.tool('loom_native_roles_desktop_routes_set_'),{'roleName':ROLE,'requestBody':wanted},verify)

def result_path(runtime,phase,checkpoint,journal_suffix=''):
    if phase not in ['permissions','snippet','pages','cleanup','routes']:raise RuntimeError('Invalid result phase')
    if not checkpoint or not checkpoint.replace('-','').isalnum():raise RuntimeError('Invalid checkpoint label')
    if journal_suffix and (phase!='permissions' or not journal_suffix.replace('-','').isalnum()):raise RuntimeError('Separate result only supports bounded permissions overlay')
    qualifier='-'+checkpoint+'-'+journal_suffix if journal_suffix else ''
    return runtime/('property-ui-'+phase+qualifier+'-result.json')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--capture',action='store_true');p.add_argument('--baseline');p.add_argument('--checkpoint',required=True)
    p.add_argument('--journal-suffix',default='',help='Reviewed separate additive overlay journal; never use to replay an uncertain operation')
    p.add_argument('--phase',choices=['permissions','snippet','pages','cleanup','routes'])
    p.add_argument('--reconcile-page',choices=['portfolio','tenancies']);p.add_argument('--resume-pages',action='store_true')
    p.add_argument('--qualified-manager-snippet');p.add_argument('--approved-page-digest')
    args=p.parse_args();client=Loom();runtime=Path(os.environ['ZP_RUNTIME_DIR'])
    manifest=json.loads((ROOT/'generation/roles/property-tenancy.json').read_text())
    manifest['resources']={r['name']:{'fields':r['addViewFields'],'scope':r['scope']} for r in manifest['resources']}
    # Add only the constructor-managed account chooser read scope.
    manifest['resources']['zp_tenant_account_permissions']={'fields':['id','userId','displayName'],'scope':{'managerUserId':{'$eq':'{{ ctx.state.currentUser.id }}'}}}
    if not args.checkpoint.replace('-','').isalnum():raise RuntimeError('Invalid checkpoint label')
    baseline_path=runtime/('property-ui-'+args.checkpoint+'-baseline.json')
    if args.journal_suffix and (args.phase not in [None,'permissions'] or not args.journal_suffix.replace('-','').isalnum()):raise RuntimeError('Separate journal only supports a bounded permissions overlay')
    journal=Journal(runtime/('property-ui-apply-journal'+('-'+args.journal_suffix if args.journal_suffix else '')))
    api=Apply(client,{},manifest,journal)
    if args.capture:
        if args.phase:raise RuntimeError('Capture cannot mutate')
        baseline={'roles':{r:api.snapshot(r) for r in [ROLE,*PORTALS]},'manifestDigest':digest(manifest)}
        # Immutable capture; a new phase requires an explicitly reviewed new baseline file.
        fd=os.open(baseline_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f:json.dump(baseline,f,indent=2);f.flush();os.fsync(f.fileno())
        print(json.dumps({'baselineDigest':digest(baseline),'roles':4,'permissionsResources':len(manifest['resources'])}));return
    baseline=json.loads(baseline_path.read_text())
    if digest(baseline)!=args.baseline or baseline['manifestDigest']!=digest(manifest):raise RuntimeError('Reviewed baseline digest required')
    api.baseline=baseline;api.journal.before=baseline;api.guard()
    if args.reconcile_page:
        if args.phase or args.resume_pages:raise RuntimeError('Reconciliation is read-only')
        api.reconcile_page(args.reconcile_page);print(json.dumps({'reconciled':args.reconcile_page,'appAcceptance':False}));return
    if args.resume_pages and args.phase!='pages':raise RuntimeError('Resume requires pages phase')
    if not args.phase:
        if (runtime/'property-ui-pages-result.json').exists(): print(json.dumps({'pageDigest':digest(api.owned_pages())}))
        _,missing=api.scopes();print(json.dumps({'newScopes':missing,'permissionWrites':1,'snippetWrites':1,'pageCreates':2,'pageComposes':2,'routeWrites':1,'cleanup':'native node inspection required before grants'}));return
    output=result_path(runtime,args.phase,args.checkpoint,args.journal_suffix)
    if output.exists():raise RuntimeError('Result already exists; reconcile existing journal and receipt without replay')
    result=api.permissions() if args.phase=='permissions' else api.snippet(args.qualified_manager_snippet) if args.phase=='snippet' else api.pages(resume=args.resume_pages) if args.phase=='pages' else api.cleanup() if args.phase=='cleanup' else api.routes(args.approved_page_digest)
    print(json.dumps({'phase':args.phase,'returned':True,'appAcceptance':False}))
    # Full results stay private; source receipts must be sanitized after review.
    fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(result,f,indent=2);f.flush();os.fsync(f.fileno())
if __name__=='__main__':main()

