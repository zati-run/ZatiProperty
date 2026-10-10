#!/usr/bin/env python3
"""Loom-only native invariant qualification; --execute requires exclusive handoff."""
import argparse,datetime,json,pathlib,sys,uuid
import jsonschema
import verify_property_commands as v
from loom_mcp import Loom

WATCH=["zp_ownership_sets","zp_property_interests","zp_tenancies","zp_tenancy_terms","zp_tenancy_parties"]
def snapshot(root,q):
    return {"audit":{name:v.read_rows(root,name) for name in v.AUDIT},"rows":{name:v.read_rows(root,name) for name in WATCH}}
def denied_generic(root,q,client,actor,operation,args,label):
    before=snapshot(root,q);name=v.tool(client,"loom_native_resource_"+operation+"_")
    jsonschema.validate(args,client.by_name[name]["inputSchema"])
    v.durable(q.path/(label+"-intent.json"),{"tool":name,"args":args,"before":before})
    try:client.call(name,args)
    except Exception as exc:
        v.durable(q.path/(label+"-error-private.json"),{"error":str(exc)})
        # Root proves the domain guard; manager proves native ACL only.
        code="DOMAIN_ACTION_REQUIRED" if actor=="root" else "DOMAIN_ACTION_DENIED"
        if not v.expected_failure(exc,code):
            q.record({"label":label,"status":"blocked-unclassified","actor":actor})
            raise RuntimeError("Unexpected generic denial; inspect private journal")
    else:raise AssertionError("Generic write unexpectedly succeeded; stop and reconcile")
    if snapshot(root,q)!=before:raise AssertionError("Denied generic write changed state")
    q.record({"label":label,"status":"denied-unchanged","actor":actor,"boundary":code,"snapshotDigest":v.hashlib.sha256(json.dumps(before,sort_keys=True,separators=(",",":")).encode()).hexdigest()})

def run(root,q,checkpoint=None):
    properties=v.read_rows(root,"zp_properties",filter={"id":4})
    units=v.read_rows(root,"zp_units",filter={"id":3})
    contacts=v.read_rows(root,"zp_owner_contacts",filter={"id":1})
    tenancies=v.read_rows(root,"zp_tenancies",filter={"id":4})
    if len(properties)!=1 or len(units)!=1 or len(contacts)!=1 or len(tenancies)!=1:raise RuntimeError("Expected owned fixture absent")
    if str(units[0]["propertyId"])!="4" or str(tenancies[0]["unitId"])!="3" or tenancies[0]["leaseState"]!="draft":raise RuntimeError("Fixture drift")
    if str(properties[0]["managerUserId"])!=str(contacts[0]["managerUserId"]):raise RuntimeError("Owner contact scope drift")
    allcontacts=v.read_rows(root,"zp_owner_contacts",fields=["id"])
    absent=max([int(x["id"]) for x in allcontacts]+[1000000])+1
    with v.role_client(root,q,"invariant_manager_resume" if checkpoint else "invariant_manager","zp_property_manager","1",18462) as manager:
        create={"propertyId":4,"effectiveFrom":"2040-01-01","effectiveTo":"2040-12-31","reasonCode":"initial-setup"}
        if checkpoint:
            a=checkpoint;aid=a["id"];av=0
            interests={"ownershipSetId":aid,"expectedVersion":av,"interests":[{"ownerContactId":1,"shareBasisPoints":10000}],"reasonCode":"correction"}
            approval={"ownershipSetId":aid,"expectedVersion":v.expected_version(a),"completeSet":True,"reasonCode":"ownership-reviewed"}
        else:
            a,_=q.command(manager,"manager1","createOwnershipSet",create,"ownership-a")
            aid=a["id"];av=v.expected_version(a)
            interests={"ownershipSetId":aid,"expectedVersion":av,"interests":[{"ownerContactId":1,"shareBasisPoints":10000}],"reasonCode":"correction"}
            q.command(manager,"manager1","setOwnershipInterests",{**interests,"interests":[{"ownerContactId":1,"shareBasisPoints":9999}]},"ownership-sum-denied",expected_error="OWNERSHIP_TOTAL")
            before=snapshot(root,q)
            q.command(manager,"manager1","setOwnershipInterests",{**interests,"interests":[{"ownerContactId":1,"shareBasisPoints":5000},{"ownerContactId":absent,"shareBasisPoints":5000}]},"ownership-partial-rollback",expected_error="OWNER_SCOPE")
            if snapshot(root,q)!=before:raise AssertionError("Partial nested transaction did not roll back")
            q.record({"label":"partial-nested-rollback","status":"native-state-unchanged","failureKind":"domain validation after first nested insertion; not injected database constraint"})
            a,_=q.command(manager,"manager1","setOwnershipInterests",interests,"ownership-interests")
            approval={"ownershipSetId":aid,"expectedVersion":v.expected_version(a),"completeSet":True,"reasonCode":"ownership-reviewed"}
            q.command(manager,"manager1","approveOwnershipSet",{**approval,"expectedVersion":av},"ownership-stale",expected_error="STALE_VERSION")
        name=v.tool(manager,v.PREFIX+v.ACTIONS["approveOwnershipSet"])
        try:jsonschema.validate({"requestBody":{**approval,"completeSet":False,"requestId":str(uuid.uuid4())}},manager.by_name[name]["inputSchema"])
        except jsonschema.ValidationError:q.record({"label":"ownership-incomplete","status":"local-schema-rejected-no-native-call"})
        else:raise AssertionError("Expected qualified completeSet schema restriction")
        a,_=q.command(manager,"manager1","approveOwnershipSet",approval,"ownership-approved")
        q.command(manager,"manager1","setOwnershipInterests",{**interests,"expectedVersion":v.expected_version(a)},"ownership-immutable",expected_error="OWNERSHIP_IMMUTABLE")
        b,_=q.command(manager,"manager1","createOwnershipSet",create,"ownership-b")
        b,_=q.command(manager,"manager1","setOwnershipInterests",{**interests,"ownershipSetId":b["id"],"expectedVersion":v.expected_version(b)},"ownership-b-interests")
        q.command(manager,"manager1","approveOwnershipSet",{**approval,"ownershipSetId":b["id"],"expectedVersion":v.expected_version(b)},"ownership-overlap",expected_error="OWNERSHIP_OVERLAP")
        q.command(manager,"manager1","createOwnershipSet",{**create,"propertyId":2},"ownership-foreign",expected_error="PROPERTY_SCOPE")
        cases=[
            ("update",{"resource":"zp_tenancies","filterByTk":4,"values":{"leaseState":"active"}},"direct"),
            ("update",{"resource":"zp_tenancies","filter":{"id":{"$in":[4,5]}},"values":{"leaseState":"active"}},"bulk-filter"),
            ("update",{"resource":"zp_tenancies","filterByTk":4,"values":{"parties":[{"displayName":"Synthetic forbidden nested party","partyRole":"occupant"}]},"updateAssociationValues":["parties"]},"nested"),
            ("create",{"resource":"zp_tenancies.terms","sourceId":4,"values":{"currency":"NZD","rentMinor":1,"revision":999}},"association")]
        audit=q.audit()
        for resource,field,value in [("zp_domain_events","eventHash","f"*64),("zp_domain_outbox","status","delivered"),("zp_domain_commands","resultJSON","{}"),("zp_audit_heads","headHash","f"*64)]:
            row=audit[resource][-1]
            cases.append(("update",{"resource":resource,"filterByTk":row["id"],"values":{field:value}},resource))
        for actor,client in [("root",root),("manager",manager)]:
            for op,args,label in cases:denied_generic(root,q,client,actor,op,args,actor+"-"+label)
        health=v.call(manager,"auditHealth",{"propertyId":4})
        if health.get("valid") is not True:raise AssertionError("Audit invalid")
        q.record({"label":"final-audit-health","status":"qualified","result":health})

def resume_checkpoint(root,q):
    stopped=[e for e in q.events if e.get("label")=="ownership-incomplete" and e.get("status")=="blocked-unknown-or-unexpected"]
    if len(stopped)!=1:raise RuntimeError("Expected stopped checkpoint absent")
    prior=stopped[0]
    if q.audit()!=prior["after"] or prior["before"]!=prior["after"]:raise RuntimeError("Audit drift before resume")
    commands=v.read_rows(root,"zp_domain_commands",filter={"requestId":prior["requestId"]})
    if commands:raise RuntimeError("Unexpected command receipt for locally rejected request")
    rows=v.read_rows(root,"zp_ownership_sets",filter={"id":1})
    if len(rows)!=1 or rows[0]["state"]!="draft" or rows[0]["version"]!=1 or str(rows[0]["propertyId"])!="4":raise RuntimeError("Ownership checkpoint drift")
    interests=v.read_rows(root,"zp_property_interests",filter={"ownershipSetId":1})
    if len(interests)!=1 or interests[0]["shareBasisPoints"]!=10000 or str(interests[0]["ownerContactId"])!="1" or interests[0]["revision"]!=1:raise RuntimeError("Interest checkpoint drift")
    if q.audit()!=prior["after"]:raise RuntimeError("Audit changed during checkpoint")
    q.record({"label":"explicit-resume-after-schema-check","status":"native-readback-unchanged"})
    return {"id":1,"version":1}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--execute",action="store_true");p.add_argument("--resume-incomplete",action="store_true");p.add_argument("--run-id",required=True);p.add_argument("--receipt",type=pathlib.Path);a=p.parse_args()
    if not v.re.fullmatch(r"[A-Za-z0-9-]{1,60}",a.run_id):p.error("invalid run ID")
    root=Loom();v.schema_gate(root)
    if not a.execute:
        print(json.dumps({"status":"source-schema-preflight-only","plannedWrites":27,"successfulCommands":5,"domainDenials":6,"genericDenials":16}));return
    if not a.receipt or a.receipt.exists():p.error("fresh receipt required")
    q=v.Qualification(root,a.run_id,resume=a.resume_incomplete)
    try:
        checkpoint=resume_checkpoint(root,q) if a.resume_incomplete else None
        run(root,q,checkpoint);status="passed"
    except Exception as exc:q.record({"label":"stopped","status":"blocked","errorType":type(exc).__name__});raise
    finally:
        a.receipt.parent.mkdir(parents=True,exist_ok=True)
        a.receipt.write_text(json.dumps({"status":locals().get("status","blocked"),"checks":q.events,"observedAt":datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+"\n")
if __name__=="__main__":main()

