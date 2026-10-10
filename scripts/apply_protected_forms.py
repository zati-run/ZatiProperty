#!/usr/bin/env python3
"""Qualify and apply one reviewed protected native form through Loom MCP only."""
import argparse,json,os,pathlib,re
from loom_mcp import Loom
from property_ui_journal import dispatch_once,sha,sync_write
ROOT=pathlib.Path(__file__).resolve().parents[1]
DESIRED=ROOT/'generation/pages/property-protected-forms.json'
HEX=re.compile(r'^[a-f0-9]{64}$')
IMMUTABLE=('actionPackage','resource','action','schemaDigest','packageVersion','implementationDigest','commandContract','context','bindings','fixedInputs','readback','reconcileAction')
def unwrap(value):
    for _ in range(3):
        if isinstance(value,dict) and set(value)=={'data'}:value=value['data']
        else:break
    return value

def missing_model(error):
    prefix='Loom tool error: '
    if not str(error).startswith(prefix):return False
    try:
        envelope=json.loads(str(error)[len(prefix):]);content=envelope['content']
        if envelope.get('isError') is not True or len(content)!=1 or content[0].get('type')!='text':return False
        value=json.loads(content[0]['text'])
        return value.get('statusCode')==404 and value.get('body',{}).get('errors')==[{'message':'MODEL_NOT_FOUND'}]
    except (ValueError,KeyError,TypeError):return False

def attached(tree,grid_uid,form_uid):
    if not isinstance(tree,dict) or tree.get('uid')!=grid_uid:return False
    items=tree.get('subModels',{}).get('items',[])
    if isinstance(items,dict):items=list(items.values())
    matches=[v for v in items if isinstance(v,dict) and v.get('uid')==form_uid and v.get('use')=='LoomActionFormModel']
    return len(matches)==1

class Forms:
    def __init__(self,client):self.c=client
    def tool(self,stem):
        names=[t['name'] for t in self.c.tools if re.fullmatch(re.escape('loom_native_'+stem+'_')+r'[a-f0-9]+',t['name'])]
        if len(names)!=1:raise RuntimeError('Missing or ambiguous discovered operation: '+stem)
        return names[0]
    def read(self,stem,args):return unwrap(self.c.call(self.tool(stem),args))
    def get(self,uid,allow_missing=False):
        try:return self.read('loom_action_forms_get',{'uid':uid})
        except RuntimeError as error:
            if allow_missing and missing_model(error):return None
            raise
    def description(self,config):return self.read('loom_action_forms_describe',{k:config[k] for k in ('actionPackage','resource','action','reconcileAction')})
    def placement_proof(self,grid_uid,config):
        if not any('recordField' in value for value in config.get('bindings',{}).values()):return {'kind':'context-free','gridUid':grid_uid}
        if config.get('context',{}).get('recordPath')!='popup.record':raise RuntimeError('Unsupported contextual form placement')
        expected=['BlockGridModel','ChildPageTabModel','ChildPageModel','ViewActionModel','TableActionsColumnModel','TableBlockModel'];chain=[];uid=grid_uid;seen=set()
        for use in expected:
            if not uid or uid in seen:raise RuntimeError('Invalid/cyclic native context ancestry')
            seen.add(uid);tree=self.read('flow_surfaces_get',{'uid':uid}).get('tree',{})
            if tree.get('uid')!=uid or tree.get('use')!=use:raise RuntimeError('Unsupported native context ancestry')
            step=tree.get('stepParams',{});chain.append({'uid':uid,'use':use,'parentId':tree.get('parentId') or tree.get('parent'),'openView':step.get('popupSettings',{}).get('openView'),'resource':step.get('resourceSettings',{}).get('init')});uid=chain[-1]['parentId']
        popup=chain[3]['openView'] or {};resource=chain[-1]['resource'] or {};collection=config['context']['collection']
        if any(v.get('dataSourceKey')!='main' or v.get('collectionName')!=collection for v in [popup,resource]):raise RuntimeError('Native record context collection mismatch')
        if resource.get('associationName') or resource.get('associationPathName'):raise RuntimeError('Association context requires separate qualification')
        if re.sub(r'\s','',str(popup.get('filterByTk','')))!='{{ctx.record.id}}':raise RuntimeError('Popup is not bound to the selected native row')
        context=self.read('flow_surfaces_context',{'requestBody':{'target':{'uid':grid_uid},'path':'popup.record','maxDepth':1}})
        if context.get('vars',{}).get('popup.record',{}).get('type')!='object':raise RuntimeError('Native popup.record context unavailable')
        return {'kind':'native-popup-record','collection':collection,'chain':chain}
    def qualify(self,desired,bindings,key):
        forms=[v for v in desired['forms'] if v['key']==key]
        if len(forms)!=1:raise RuntimeError('Unknown form key')
        form=forms[0];placement=bindings.get(form['placement'])
        if not isinstance(placement,dict) or not isinstance(placement.get('gridUid'),str):raise RuntimeError('Missing reviewed native grid binding')
        config=dict(form['config']);grid=self.get(placement['gridUid']);proof=self.placement_proof(placement['gridUid'],config)
        if grid.get('type')!='BlockGridModel' or not HEX.fullmatch(grid.get('nodeHash','')):raise RuntimeError('Native grid identity/digest unavailable')
        for name,version in [('@loom/plugin-action-form',desired['requiredCompanionVersion']),('@zati/plugin-property-tenancy',desired['requiredDomainVersion'])]:
            plugin=self.read('pm_get',{'filterByTk':name})
            if plugin.get('version')!=version or plugin.get('enabled') is not True or plugin.get('installed') is not True or plugin.get('isCompatible') is not True:raise RuntimeError('Required enabled compatible package version unavailable: '+name)
        found=self.description(config)
        if found.get('packageVersion')!=desired['requiredDomainVersion'] or found.get('commandContract')!='idempotent-terminal-v1':raise RuntimeError('Qualified terminal command contract unavailable')
        for field in ('schemaDigest','implementationDigest'):
            if not HEX.fullmatch(found.get(field,'')):raise RuntimeError('Missing native action identity')
        schema=found.get('schema',{})
        if 'requestId' not in schema.get('required',[]) or schema.get('properties',{}).get('requestId',{}).get('format')!='uuid':raise RuntimeError('Missing required command identity')
        config.update({k:found[k] for k in ('schemaDigest','implementationDigest','packageVersion','commandContract')})
        return {'key':key,'uid':form['uid'],'gridUid':placement['gridUid'],'expectedGridHash':grid['nodeHash'],'config':config,'schema':schema,'desiredHash':sha(desired),'bindingHash':sha(placement),'placementProof':proof,'tools':{name:self.tool('loom_action_forms_'+name) for name in ('get','create','set','describe')}}
    def observe(self,qualified):
        form=self.get(qualified['uid'],True)
        surface=self.read('flow_surfaces_get',{'uid':qualified['gridUid']})
        return {'form':form,'attached':attached(surface.get('tree'),qualified['gridUid'],qualified['uid'])}
    @staticmethod
    def matches(observed,qualified):
        value=observed['form']
        return bool(value and value.get('uid')==qualified['uid'] and value.get('type')=='LoomActionFormModel' and value.get('config')==qualified['config'] and observed['attached'])
    def apply(self,qualified,journal):
        journal=pathlib.Path(journal)
        if journal.exists():raise RuntimeError('Existing authoring intent is fenced; use verify and independent reconciliation, never replay')
        if self.placement_proof(qualified['gridUid'],qualified['config'])!=qualified.get('placementProof'):raise RuntimeError('Native placement context changed; repeat qualification and review')
        before=self.observe(qualified)
        if self.matches(before,qualified):return {'state':'already-present-native-verified','after':before}
        fresh=self.description(qualified['config'])
        if any(fresh.get(k)!=qualified['config'][k] for k in ('schemaDigest','implementationDigest','packageVersion','commandContract')):raise RuntimeError('Action qualification changed')
        grid=self.get(qualified['gridUid'])
        if grid.get('nodeHash')!=qualified['expectedGridHash']:raise RuntimeError('Grid changed; repeat read-only qualification and review')
        if before['form']:
            if not before['attached']:raise RuntimeError('Existing form is outside the reviewed grid')
            prior=before['form']['config']
            if any(prior.get(k)!=qualified['config'].get(k) for k in IMMUTABLE):raise RuntimeError('Action binding changed; reviewed replacement migration required')
            name=self.tool('loom_action_forms_set');body={'uid':qualified['uid'],'expectedNodeHash':before['form']['nodeHash'],'config':qualified['config']}
        else:
            name=self.tool('loom_action_forms_create');body={k:qualified[k] for k in ('uid','gridUid','expectedGridHash','config')}
        return dispatch_once(self.c,name,{'requestBody':body},journal,before,lambda:self.observe(qualified),lambda after:self.matches(after,qualified))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['qualify','apply','verify']);parser.add_argument('--key',required=True);parser.add_argument('--bindings',required=True);parser.add_argument('--qualification',required=True);parser.add_argument('--journal');args=parser.parse_args()
    desired=json.loads(DESIRED.read_text());bindings=json.loads(pathlib.Path(args.bindings).read_text());api=Forms(Loom());path=pathlib.Path(args.qualification)
    if args.phase=='qualify':
        value=api.qualify(desired,bindings,args.key);sync_write(path,value,True);print(json.dumps({'state':'qualified-read-only','key':args.key,'configDigest':sha(value['config'])}));return
    value=json.loads(path.read_text())
    if value.get('key')!=args.key or value.get('desiredHash')!=sha(desired):raise RuntimeError('Desired specification differs from qualification')
    form=next(v for v in desired['forms'] if v['key']==args.key)
    if value.get('bindingHash')!=sha(bindings.get(form['placement'])):raise RuntimeError('Native placement binding changed')
    if args.phase=='verify':
        observed=api.observe(value);print(json.dumps({'state':'native-match' if api.matches(observed,value) else 'native-mismatch','observed':observed}));return
    evidence=ROOT/value['config']['qualification']['evidenceRef']
    if not evidence.is_file():raise RuntimeError('Independent protected-form review receipt missing')
    if not args.journal:raise RuntimeError('Durable private journal path required')
    print(json.dumps(api.apply(value,args.journal)))
if __name__=='__main__':main()
