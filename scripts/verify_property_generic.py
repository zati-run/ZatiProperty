#!/usr/bin/env python3
"""Fresh generic-only Loom guard verification; never replays domain commands."""
import argparse,datetime,hashlib,json,pathlib,re
import jsonschema
from loom_mcp import Loom
import verify_property_commands as base

BUSINESS=["zp_tenancies","zp_tenancy_terms","zp_tenancy_parties","zp_ownership_sets","zp_property_interests","zp_properties","zp_units","zp_buildings","zp_owner_contacts","zp_tenant_account_permissions"]
MESSAGE="Use the approved property or tenancy action to change this record. No changes were saved."
def snapshot(root):
    return {name:base.read_rows(root,name) for name in BUSINESS+base.AUDIT}
def digest(state):return hashlib.sha256(json.dumps(state,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def denial(error,actor):
    prefix="Loom tool error: "
    if not str(error).startswith(prefix):return False
    try:
        outer=json.loads(str(error)[len(prefix):])
        packets=[json.loads(x["text"]) for x in outer.get("content",[]) if x.get("type")=="text"]
    except (ValueError,KeyError,TypeError):return False
    for packet in packets:
        if packet.get("statusCode")!=403:continue
        for entry in packet.get("body",{}).get("errors",[]):
            if actor=="root" and entry.get("code")=="DOMAIN_ACTION_REQUIRED" and entry.get("message")==MESSAGE:return True
            if actor=="manager" and entry.get("message")=="No permissions":return True
    return False

def cases(audit):
    result=[
      ("update",{"resource":"zp_tenancies","filterByTk":4,"values":{"leaseState":"active"}},"direct"),
      ("update",{"resource":"zp_tenancies","filter":{"id":{"$in":[4,5]}},"values":{"leaseState":"active"}},"bulk-filter"),
      ("update",{"resource":"zp_tenancies","filterByTk":4,"values":{"parties":[{"displayName":"Synthetic forbidden nested party","partyRole":"occupant"}]},"updateAssociationValues":["parties"]},"nested"),
      ("create",{"resource":"zp_tenancies.terms","sourceId":4,"values":{"effectiveFrom":"2035-01-01","effectiveTo":"2035-12-31","currency":"NZD","rentMinor":1,"depositMinor":0,"rentFrequency":"monthly","dueDay":1,"prorationPolicy":"actual-calendar-days","revision":999}},"association")]
    for resource,field,value in [("zp_domain_events","eventHash","f"*64),("zp_domain_outbox","status","delivered"),("zp_domain_commands","resultJSON","{}"),("zp_audit_heads","headHash","f"*64)]:
        if not audit[resource]:raise RuntimeError("Protected fixture missing")
        result.append(("update",{"resource":resource,"filterByTk":audit[resource][-1]["id"],"values":{field:value}},resource))
    return result

def probe(root,q,client,actor,operation,args,label):
    name=base.tool(client,"loom_native_resource_"+operation+"_")
    jsonschema.validate(args,client.by_name[name]["inputSchema"])
    before=snapshot(root)
    base.durable(q.path/(label+"-intent.json"),{"tool":name,"args":args,"before":before})
    try:client.call(name,args)
    except Exception as exc:
        base.durable(q.path/(label+"-response-private.json"),{"error":str(exc)})
        after=snapshot(root)
        if after!=before:raise AssertionError("Full protected/business state changed")
        if not denial(exc,actor):raise RuntimeError("Unexpected response; preserved private error and unchanged-state evidence, no retry")
    else:raise AssertionError("Forbidden write returned success; stop and reconcile")
    q.record({"label":label,"status":"denied-unchanged","httpStatus":403,"boundary":"protected-hook" if actor=="root" else "native-role-ACL","snapshotDigest":digest(before)})

def run(root,q):
    before=snapshot(root)
    rows={str(r["id"]):r for r in before["zp_tenancies"]}
    if rows.get("4",{}).get("leaseState")!="draft" or rows.get("5",{}).get("leaseState")!="ended":raise RuntimeError("Tenancy fixture drift")
    selected=cases(before)
    with base.role_client(root,q,"generic_manager","zp_property_manager","1",18462) as manager:
        # Prevalidate all actual schemas before the first intent.
        for client in [root,manager]:
            for operation,args,_ in selected:jsonschema.validate(args,client.by_name[base.tool(client,"loom_native_resource_"+operation+"_")]["inputSchema"])
        for actor,client in [("root",root),("manager",manager)]:
            for operation,args,label in selected:probe(root,q,client,actor,operation,args,actor+"-"+label)
    after=snapshot(root)
    if after!=before:raise AssertionError("Batch changed protected/business state")
    q.record({"label":"whole-batch","status":"unchanged","snapshotDigest":digest(after),"nativeAttempts":16})

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--execute",action="store_true");p.add_argument("--run-id",required=True);p.add_argument("--receipt",type=pathlib.Path);args=p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9-]{1,60}",args.run_id):p.error("invalid run ID")
    root=Loom()
    if not args.execute:
        for operation in ["update","create"]:base.tool(root,"loom_native_resource_"+operation+"_")
        print(json.dumps({"status":"schema-discovery-only","nativeAttempts":16}));return
    if not args.receipt or args.receipt.exists():p.error("new receipt required")
    q=base.Qualification(root,args.run_id)
    try:run(root,q);status="passed"
    except Exception as exc:q.record({"label":"stopped","status":"blocked","errorType":type(exc).__name__});raise
    finally:
        args.receipt.parent.mkdir(parents=True,exist_ok=True)
        args.receipt.write_text(json.dumps({"status":locals().get("status","blocked"),"observedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"checks":q.events},indent=2)+"\n")
if __name__=="__main__":main()

