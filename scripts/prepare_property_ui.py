#!/usr/bin/env python3
"""Read-only E3 planner. Apply requires a reviewed plan, fresh readback and coordinator."""
import argparse, hashlib, json, pathlib
from loom_mcp import Loom
ROOT=pathlib.Path(__file__).resolve().parents[1]

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()

def merge_actions(existing, fields, scope_id):
    """Add bounded view fields; preserve every non-view action and its exact scope."""
    result=[]; found=False
    for action in existing:
        copy={k:v for k,v in action.items() if k not in {"id","createdAt","updatedAt","rolesResourceId"}}
        if copy["name"]=="view":
            if found: raise ValueError("duplicate view action")
            found=True
            if copy.get("scopeId")!=scope_id: raise ValueError("view scope changed")
            if not isinstance(copy.get("fields"),list) or "*" in copy["fields"]: raise ValueError("unbounded prior view")
            copy["fields"]=sorted(set(copy["fields"])|set(fields))
        result.append(copy)
    if not found:result.append({"name":"view","fields":sorted(set(fields)),"scopeId":scope_id})
    return result

def native(client,prefix,args):
    names=[t["name"] for t in client.tools if t["name"].startswith(prefix)]
    if len(names)!=1: raise ValueError("ambiguous/missing native tool "+prefix)
    return client.call(names[0],args)

def prepare(client):
    overlay=json.loads((ROOT/"generation/roles/property-tenancy.json").read_text())
    snapshots={}; roles=[overlay["role"],"zp_owner","zp_tenant","zp_vendor"]
    for role in roles:
        snapshots[role]={"role":native(client,"loom_native_roles_get_",{"filterByTk":role}),"resources":{}}
        for resource in overlay["resources"]:
            snapshots[role]["resources"][resource["name"]]=native(client,"loom_native_roles_data_source_resources_get_",{"roleName":role,"dataSourceKey":"main","name":resource["name"],"appends":["actions"]})
    return {"status":"captured-not-applied","manifestHash":digest(overlay),"baselineHash":digest(snapshots),"baseline":snapshots,"overlay":overlay,"pages":{key:json.loads((ROOT/("generation/pages/"+key+".json")).read_text()) for key in ["portfolio","tenancies"]}}

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--output",type=pathlib.Path,required=True);args=parser.parse_args()
    if args.output.exists():parser.error("preserve existing snapshot; choose a new output")
    result=prepare(Loom());args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("x") as f:json.dump(result,f,indent=2);f.write("\n")
    print("Read-only plan captured; hash "+result["baselineHash"])
