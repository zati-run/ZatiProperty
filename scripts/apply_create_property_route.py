#!/usr/bin/env python3
"""Grant only the focused protected create-property route after native form readback."""
import argparse,json,pathlib,os
from loom_mcp import Loom
from apply_property_ui import Apply,Journal,ROLE,PORTALS,page_binding,data
from apply_protected_forms import Forms,sync_write
from property_ui_journal import sha
ROOT=pathlib.Path(__file__).resolve().parents[1]
ROLES=[ROLE,*PORTALS]
def wanted_routes(before,binding):
 ids={str(row['id']) for row in before['routes']}
 return sorted(ids|{str(binding['menuRouteId']),str(binding['tabRouteId'])})
def verify_roles(before,after,wanted):
 for role in ROLES:
  if role!=ROLE:
   if after[role]!=before[role]:raise RuntimeError('Portal role changed')
  else:
   if {str(row['id']) for row in after[role]['routes']}!=set(wanted):raise RuntimeError('Manager route readback mismatch')
   if {k:v for k,v in after[role].items() if k!='routes'}!={k:v for k,v in before[role].items() if k!='routes'}:raise RuntimeError('Manager authority changed')
class FocusedRoute:
 def __init__(self,client):self.c=client;self.api=Apply(client,{},json.loads((ROOT/'generation/roles/property-tenancy.json').read_text()),None);self.forms=Forms(client)
 def snapshots(self):return {role:self.api.snapshot(role) for role in ROLES}
 def gate(self,qualified):
  desired=json.loads((ROOT/'generation/pages/create-property.json').read_text())
  if qualified.get('key')!='create-property' or qualified.get('uid')!='zp_property_create_form_v1' or qualified.get('config',{}).get('action')!='createProperty':raise RuntimeError('Wrong protected form qualification')
  surface=self.forms.read('flow_surfaces_get',{'pageSchemaUid':desired['page']['pageSchemaUid']});binding=page_binding(surface,desired['page'])
  if binding['gridUid']!=qualified.get('gridUid'):raise RuntimeError('Focused page grid changed')
  observed=self.forms.observe(qualified)
  if not observed.get('attached') or not observed.get('form') or observed['form'].get('config')!=qualified['config']:raise RuntimeError('Protected form is not saved and attached')
  return {'binding':binding,'formConfigDigest':sha(qualified['config']),'formNodeHash':observed['form']['nodeHash']}
 def capture(self,qualified):return {'roles':self.snapshots(),'gate':self.gate(qualified)}
 def apply(self,qualified,baseline,journal):
  current=self.capture(qualified)
  if current!=baseline:raise RuntimeError('Role or form drift; repeat read-only qualification and review')
  wanted=wanted_routes(baseline['roles'][ROLE],baseline['gate']['binding'])
  def verify(_):
   if self.gate(qualified)!=baseline['gate']:raise RuntimeError('Form changed during route grant')
   after=self.snapshots();verify_roles(baseline['roles'],after,wanted);return {'roles':after,'gate':baseline['gate'],'managerOnly':True}
  return Journal(pathlib.Path(journal)).run('focused-create-property-route',self.c,self.api.tool('loom_native_roles_desktop_routes_set_'),{'roleName':ROLE,'requestBody':wanted},verify)
def main():
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['capture','apply']);p.add_argument('--qualification',required=True);p.add_argument('--baseline',required=True);p.add_argument('--journal',required=True);a=p.parse_args()
 api=FocusedRoute(Loom());qualified=json.loads(pathlib.Path(a.qualification).read_text());path=pathlib.Path(a.baseline)
 if a.phase=='capture':sync_write(path,api.capture(qualified),True)
 else:api.apply(qualified,json.loads(path.read_text()),a.journal)
if __name__=='__main__':main()
