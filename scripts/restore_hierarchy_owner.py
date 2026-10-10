#!/usr/bin/env python3
"""Restore only reviewed hierarchy auto-grants; default is read-only preflight."""
import argparse,json,pathlib,jsonschema
from collections import Counter
from loom_mcp import Loom
from apply_property_ui import Apply,canonical_resource,digest,ROOT,Journal

ROLE="zp_owner"
ADDED={"zp_properties":{"units"},"zp_units":{"tenancies","propertyId"},"zp_tenancies":{"unitId"}}
def payload_for(before,after):
    for key in ["role","strategy","routes"]:
        if before[key]!=after[key]:raise RuntimeError("Non-permission owner drift")
    old={r["name"]:canonical_resource(r) for r in before["permissions"]}
    new={r["name"]:canonical_resource(r) for r in after["permissions"]}
    if set(old)!=set(new):raise RuntimeError("Owner resource set changed")
    payload=[]
    for name,a in old.items():
        b=new[name]
        if a==b:continue
        if name not in ADDED or a["usingActionsConfig"]!=b["usingActionsConfig"]:raise RuntimeError("Unplanned resource drift")
        if [x["name"] for x in a["actions"]]!=[x["name"] for x in b["actions"]]:raise RuntimeError("Action set drift")
        for x,y in zip(a["actions"],b["actions"]):
            if {k:v for k,v in x.items() if k!="fields"}!={k:v for k,v in y.items() if k!="fields"}:raise RuntimeError("Action scope drift")
            left=Counter(x.get("fields",[]));right=Counter(y.get("fields",[]))
            if left-right or set(right-left)-ADDED[name]:raise RuntimeError("Unplanned field drift")
        payload.append(a)
    if not payload:raise RuntimeError("No reviewed auto-grants remain")
    return payload

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--apply",action="store_true");args=p.parse_args()
    client=Loom();runtime=client.runtime
    before=json.loads((runtime/"property-ui-hierarchy-20261010-baseline.json").read_text())
    observed=json.loads((runtime/"property-hierarchy-auto-field-role-readback.json").read_text())
    manifest=json.loads((ROOT/"generation/roles/property-tenancy.json").read_text())
    manifest["resources"]={r["name"]:{"fields":r["addViewFields"],"scope":r["scope"]} for r in manifest["resources"]}
    manifest["resources"]["zp_tenant_account_permissions"]={"fields":["id","userId","displayName"],"scope":{"managerUserId":{"$eq":"{{ ctx.state.currentUser.id }}"}}}
    journal=Journal(runtime/"property-hierarchy-owner-restore-journal")
    app=Apply(client,{"roles":observed},manifest,journal)
    app.guard()
    resources=payload_for(before["roles"][ROLE],observed[ROLE])
    request={"filterByTk":ROLE,"requestBody":{"dataSourceKey":"main","resources":resources}}
    name=app.tool("loom_native_roles_apply_data_permissions_")
    jsonschema.validate(request,client.by_name[name]["inputSchema"])
    if not args.apply:
        print(json.dumps({"status":"read-only-qualified","resources":[r["name"] for r in resources],"beforeDigest":digest(before["roles"][ROLE]),"observedDigest":digest(observed[ROLE])}));return
    def verify(_):
        after=app.snapshot(ROLE)
        if sorted(map(canonical_resource,after["permissions"]),key=lambda x:x["name"])!=sorted(map(canonical_resource,before["roles"][ROLE]["permissions"]),key=lambda x:x["name"]):raise RuntimeError("Owner baseline permissions not restored")
        for key in ["role","strategy","routes"]:
            if after[key]!=before["roles"][ROLE][key]:raise RuntimeError("Owner unrelated state changed")
        for role,state in observed.items():
            if role!=ROLE and app.snapshot(role)!=state:raise RuntimeError("Other role changed")
        return {"ownerDigest":digest(after),"restoredResources":[r["name"] for r in resources]}
    result=journal.run("restore-reviewed-owner-auto-grants",client,app.tool("loom_native_roles_apply_data_permissions_"),request,verify)
    print(json.dumps({"status":"verified-owner-restore","evidence":result}))
if __name__=="__main__":main()

