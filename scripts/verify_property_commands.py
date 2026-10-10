#!/usr/bin/env python3
"""Single-lane synthetic Loom command qualification. Defaults to schema-only.

--execute requires coordinator scheduling. No plugin/role mutations. Every command
has durable unique intent; any unclassified outcome stops, never retries a write.
"""
import argparse, concurrent.futures, contextlib, datetime, hashlib, json, os, pathlib, re, uuid, threading, time
import jsonschema
from loom_mcp import Loom
import verify_maintenance_writes as bridges

PREFIX="loom_native_zp_property_tenancy_"
ACTIONS={"createProperty":"create_property_","createBuilding":"create_building_","createUnit":"create_unit_","createOwnerContact":"create_owner_co_","authorizeTenantAccount":"authorize_tenan_","createDraftTenancy":"create_draft_te_","updateDraftTenancy":"update_draft_te_","activateTenancy":"activate_tenanc_","endTenancy":"end_tenancy_","createOwnershipSet":"create_ownershi_","setOwnershipInterests":"set_ownership_i_","approveOwnershipSet":"approve_ownersh_","auditHealth":"audit_health_","reconcileCommand":"reconcile_comm"}
AUDIT=["zp_domain_events","zp_domain_outbox","zp_domain_commands","zp_audit_heads"]


def unwrap(value):
    while isinstance(value,dict) and "data" in value:value=value["data"]
    return value

def tool(client,prefix):
    names=[t["name"] for t in client.tools if t["name"].startswith(prefix)]
    if len(names)!=1:raise RuntimeError("Missing or ambiguous qualified tool: "+prefix)
    return names[0]

def call(client,action,values):
    args={"commandAction":values["action"],"requestId":values["requestId"]} if action=="reconcileCommand" else {"requestBody":values}
    name=tool(client,PREFIX+ACTIONS[action]);jsonschema.validate(args,client.by_name[name]["inputSchema"])
    return unwrap(client.call(name,args))

def durable(path,value):
    with path.open("x") as f:
        os.chmod(path,0o600);json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)

def read_rows(client,resource,fields=None,filter=None):
    rows=[];seen=set()
    for page in range(1,22):
        args={"resource":resource,"pageSize":50,"page":page,"sort":["id"]}
        if fields:args["fields"]=fields
        if filter:args["filter"]=filter
        batch=unwrap(client.call(tool(client,"loom_native_resource_list_"),args))
        if not isinstance(batch,list) or len(batch)>50:raise RuntimeError("Invalid bounded page")
        for row in batch:
            identity=str(row["id"])
            if identity in seen:raise RuntimeError("Repeated row across pages")
            seen.add(identity)
        rows.extend(batch)
        if len(rows)>1000:raise RuntimeError("Native read cap exceeded")
        if len(batch)<50:return rows
    raise RuntimeError("Native pagination did not terminate")

def expected_version(row):
    value=row.get("version")
    if type(value) is not int or value<0:raise ValueError("Native version missing or invalid")
    return value

def expected_failure(error,code):
    # Accept exact structured native status/code only, never an exception substring.
    text=str(error);prefix="Loom tool error: "
    if not text.startswith(prefix):return False
    try:
        outer=json.loads(text[len(prefix):])
        packets=[json.loads(c["text"]) for c in outer.get("content",[]) if c.get("type")=="text"]
    except (ValueError,KeyError,TypeError):return False
    status=403 if code in ["PROPERTY_SCOPE","DOMAIN_ACTION_DENIED","CONSTRUCTOR_REQUIRED"] else 409
    for packet in packets:
        if not isinstance(packet,dict) or packet.get("statusCode")!=status:continue
        errors=packet.get("body",{}).get("errors",[])
        for entry in errors:
            if entry.get("code")==code or entry.get("message")==code:return True
            if code=="DOMAIN_ACTION_DENIED" and (entry.get("code") in ["FORBIDDEN","ACL_DENIED"] or entry.get("message")=="Forbidden"):return True
    return False

def verify_atomic(before,after,delta):
    created={}
    for name in AUDIT[:3]:
        old={str(r["id"]) for r in before[name]}
        created[name]=[r for r in after[name] if str(r["id"]) not in old]
        if len(after[name])-len(before[name])!=delta or len(created[name])!=delta:raise AssertionError("Atomicity count mismatch")
    events={str(r["id"]) for r in created["zp_domain_events"]}
    for name in ["zp_domain_outbox","zp_domain_commands"]:
        if {str(r["eventId"]) for r in created[name]}!=events:raise AssertionError("Audit/receipt/outbox links differ")
    if delta==0 and before!=after:raise AssertionError("Replay changed protected state")
    if delta:
        old=before["zp_audit_heads"];new=after["zp_audit_heads"]
        if len(new)!=1 or int(new[0]["headSequence"])-(int(old[0]["headSequence"]) if old else 0)!=delta:raise AssertionError("Audit head increment mismatch")

def schema_gate(client):
    selected={}
    for action,suffix in ACTIONS.items():
        name=tool(client,PREFIX+suffix);entry=client.by_name[name];schema=entry["inputSchema"]
        if action not in ["auditHealth","reconcileCommand"]:
            body=schema["properties"]["requestBody"]
            if "requestId" not in body.get("required",[]):raise RuntimeError("Command package/catalog not qualified: requestId absent")
        elif action=="reconcileCommand":
            if not {"commandAction","requestId"}<=set(schema.get("required",[])):raise RuntimeError("Reconcile GET schema differs")
        selected[action]={"name":name,"schema":schema}
    return selected

@contextlib.contextmanager
def role_client(root,q,alias,role,graph,port):
    bridges.ROLES[alias]=role;old=bridges.PORT;bridges.PORT=port
    config=json.loads((root.runtime/"loom.json").read_text())
    accounts=json.loads((root.runtime/"maintenance-test-accounts.json").read_text())
    loom_dir=pathlib.Path(os.environ["ZP_LOOM_DIR"])
    try:
        with bridges.role_bridge(root,root.runtime,loom_dir,config,alias,accounts[role+"."+graph],q.path) as client:yield client
    finally:bridges.PORT=old

class Qualification:
    def __init__(self,root,run_id):
        self.root=root;self.run_id=run_id;self.events=[]
        self.path=root.runtime/("property-command-verification-"+run_id)
        self.path.mkdir(mode=0o700,exist_ok=False)
    def audit(self):
        fields={"zp_domain_events":["id","sequence","eventHash"],"zp_domain_outbox":["id","eventId","status"],"zp_domain_commands":["id","commandKey","actorId","action","requestId","eventId"],"zp_audit_heads":["id","headSequence","headHash"]}
        return {name:read_rows(self.root,name,fields[name]) for name in AUDIT}
    def record(self,event):
        self.events.append(event);durable(self.path/(str(len(self.events)).zfill(3)+"-result.json"),event)
    def command(self,client,actor,action,values,label,expected_error=None,replay=None):
        values={**values,"requestId":replay or str(uuid.uuid4())};before=self.audit()
        durable(self.path/(label+"-intent.json"),{"actor":actor,"action":action,"values":values,"before":before})
        result=None;error=None
        try:result=call(client,action,values)
        except Exception as exc:error=str(exc)
        after=self.audit()
        if error:
            # Never classify a transport failure as a successful deny.
            if not expected_error or not expected_failure(error,expected_error):
                reconciliation=None
                try:reconciliation=call(client,"reconcileCommand",{"action":action,"requestId":values["requestId"]})
                except Exception:pass
                self.record({"label":label,"actor":actor,"action":action,"requestId":values["requestId"],"status":"blocked-unknown-or-unexpected","reconciliation":reconciliation,"before":before,"after":after})
                raise RuntimeError("Unclassified command outcome; inspect private journal and native reconcile: "+label)
            if before!=after:raise AssertionError("Denied command changed audit state: "+label)
            self.record({"label":label,"actor":actor,"action":action,"requestId":values["requestId"],"status":"denied","code":expected_error,"auditUnchanged":True})
            return None,values["requestId"]
        if expected_error:raise AssertionError("Expected denial but command committed: "+label)
        expected_delta=0 if replay else 1
        verify_atomic(before,after,expected_delta)
        reconciliation=call(client,"reconcileCommand",{"action":action,"requestId":values["requestId"]})
        if reconciliation.get("status")!="committed" or reconciliation.get("result")!=result:raise AssertionError("Reconcile differs")
        if after!=self.audit():raise AssertionError("Reconcile wrote data")
        self.record({"label":label,"actor":actor,"action":action,"requestId":values["requestId"],"status":"committed","result":result,"auditDelta":expected_delta,"reconcileReadOnly":True})
        return result,values["requestId"]
    def concurrent(self,left,right,action,payloads,label,expected_successes,error_code=None):
        before=self.audit();payloads=[{**p,"requestId":p.get("requestId",str(uuid.uuid4()))} for p in payloads]
        durable(self.path/(label+"-intent.json"),{"action":action,"payloads":payloads,"before":before})
        barrier=threading.Barrier(2)
        def invoke(item):
            c,v=item;barrier.wait(timeout=10)
            try:return {"ok":True,"result":call(c,action,v)}
            except Exception as exc:
                if error_code and expected_failure(exc,error_code):return {"ok":False,"code":error_code}
                return {"ok":False,"code":"UNCLASSIFIED"}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(invoke,zip([left,right],payloads)))
        after=self.audit();successes=sum(r["ok"] for r in results)
        if successes!=expected_successes or any(r.get("code")=="UNCLASSIFIED" for r in results):raise AssertionError("Concurrent outcome requires reconciliation: "+label)
        delta=1 if payloads[0]["requestId"]==payloads[1]["requestId"] else successes
        verify_atomic(before,after,delta)
        if delta==1 and successes==2 and results[0]["result"]!=results[1]["result"]:raise AssertionError("Idempotent concurrent results differ")
        self.record({"label":label,"action":action,"status":"qualified","requestIds":[p["requestId"] for p in payloads],"results":results,"auditDelta":delta})
        return results

def draft(unit,user,code):
    return {"unitId":unit,"code":code,"startDate":"2035-01-01","endDate":"2035-12-31","term":{"effectiveFrom":"2035-01-01","effectiveTo":"2035-12-31","currency":"NZD","rentMinor":150000,"depositMinor":300000,"rentFrequency":"monthly","dueDay":1,"prorationPolicy":"actual-calendar-days"},"parties":[{"displayName":"Synthetic permitted tenant","userId":user,"partyRole":"primary","effectiveFrom":"2035-01-01","effectiveTo":"2035-12-31"}],"reasonCode":"initial-setup"}

def run(root,q):
    accounts=json.loads((root.runtime/"maintenance-test-accounts.json").read_text());tenant=accounts["zp_tenant.1"]["id"];manager=accounts["zp_property_manager.1"]["id"]
    with role_client(root,q,"property_manager_primary","zp_property_manager","1",18462) as m:
        schema_gate(m)
        existing=read_rows(root,"zp_properties",["id"],{"managerUserId":manager})
        if not existing:raise AssertionError("Existing synthetic manager property required for read-only audit baseline")
        before=q.audit();health=call(m,"auditHealth",{"propertyId":existing[0]["id"]});assert before==q.audit()
        q.record({"label":"pre-mutation-audit-health","status":"readonly","initialAuditCounts":{k:len(v) for k,v in before.items()},"result":health})
        prop,pid=q.command(m,"manager1","createProperty",{"name":"Command qualification "+q.run_id,"reasonCode":"initial-setup"},"create-property")
        property_id=prop["id"]
        q.command(m,"manager1","createProperty",{"name":"Command qualification "+q.run_id,"reasonCode":"initial-setup"},"replay-property",replay=pid)
        q.command(m,"manager1","createProperty",{"name":"Changed collision","reasonCode":"initial-setup"},"collision-property",expected_error="REQUEST_ID_COLLISION",replay=pid)
        building,_=q.command(m,"manager1","createBuilding",{"propertyId":property_id,"name":"Synthetic Building","reasonCode":"initial-setup"},"create-building")
        unit,_=q.command(m,"manager1","createUnit",{"propertyId":property_id,"buildingId":building["id"],"name":"Synthetic Unit","reasonCode":"initial-setup"},"create-unit")
        owner,_=q.command(m,"manager1","createOwnerContact",{"propertyId":property_id,"displayName":"Synthetic owner contact","reasonCode":"initial-setup"},"create-owner-contact")
        mappings=read_rows(root,"zp_tenant_account_permissions",["id","managerUserId","userId"],{"managerUserId":manager,"userId":tenant})
        if not mappings:q.command(root,"constructor","authorizeTenantAccount",{"propertyId":property_id,"managerUserId":manager,"userId":tenant,"displayName":"Synthetic tenant","reasonCode":"account-authorized"},"authorize-account")
        elif len(mappings)!=1:raise AssertionError("Ambiguous account mapping")
        q.command(m,"manager1","authorizeTenantAccount",{"propertyId":property_id,"managerUserId":manager,"userId":tenant,"displayName":"Synthetic tenant","reasonCode":"account-authorized"},"deny-manager-account-authority",expected_error="DOMAIN_ACTION_DENIED")
        bad=draft(unit["id"],accounts["zp_tenant.2"]["id"],"ZP-Q-DENY")
        q.command(m,"manager1","createDraftTenancy",bad,"deny-unpermitted-party",expected_error="PARTY_ACCOUNT_NOT_PERMITTED")
        first,_=q.command(m,"manager1","createDraftTenancy",draft(unit["id"],tenant,"ZP-Q-A-"+q.run_id),"draft-a")
        second,_=q.command(m,"manager1","createDraftTenancy",draft(unit["id"],tenant,"ZP-Q-B-"+q.run_id),"draft-b")
        before=q.audit();unknown=call(m,"reconcileCommand",{"action":"createProperty","requestId":str(uuid.uuid4())})
        assert unknown=={"status":"not_observed","requestId":unknown["requestId"],"retryAuthorized":False} and before==q.audit()
        q.record({"label":"unknown-reconciliation","status":"not-observed-readonly","retryAuthorized":False})
        with role_client(root,q,"property_manager_parallel","zp_property_manager","1",18463) as parallel:
            rid=str(uuid.uuid4());same={"propertyId":property_id,"name":"Concurrent Unit","reasonCode":"initial-setup","requestId":rid}
            q.concurrent(m,parallel,"createUnit",[same,same],"same-command-concurrent",2)
            optimistic=draft(unit["id"],tenant,"unused");optimistic.pop("unitId");optimistic.pop("code");optimistic.update(tenancyId=first["id"],expectedVersion=expected_version(first),reasonCode="correction")
            updated=q.concurrent(m,parallel,"updateDraftTenancy",[optimistic,optimistic],"version-concurrent",1,"STALE_VERSION")
            current_first=next(r["result"] for r in updated if r["ok"])
            result=q.concurrent(m,parallel,"activateTenancy",[{"tenancyId":first["id"],"expectedVersion":expected_version(current_first),"reasonCode":"activation-reviewed"},{"tenancyId":second["id"],"expectedVersion":expected_version(second),"reasonCode":"activation-reviewed"}],"occupancy-concurrent",1,"OCCUPANCY_OVERLAP")
        active=next(r["result"] for r in result if r["ok"])
        ended,_=q.command(m,"manager1","endTenancy",{"tenancyId":active["id"],"expectedVersion":expected_version(active),"endDate":"2035-06-30","reasonCode":"move-out-confirmed"},"end-tenancy")
        rows=read_rows(root,"zp_tenancies",["id","leaseState","version","tenantUserId","endDate"],{"id":ended["id"]})
        assert len(rows)==1 and rows[0]["leaseState"]=="ended" and str(rows[0]["tenantUserId"])==str(tenant)
        before=q.audit();health=call(m,"auditHealth",{"propertyId":property_id});assert before==q.audit() and health.get("valid") is True;q.record({"label":"audit-health-readonly","status":"qualified","result":health})
    for role in ["zp_owner","zp_tenant","zp_vendor"]:
        with role_client(root,q,"property_deny_"+role,role,"1",18462) as c:
            q.command(c,role,"createProperty",{"name":"Must not exist "+q.run_id,"reasonCode":"initial-setup"},"deny-"+role,expected_error="DOMAIN_ACTION_DENIED")
    with role_client(root,q,"property_manager_foreign","zp_property_manager","2",18462) as foreign:
        q.command(foreign,"manager2","createBuilding",{"propertyId":property_id,"name":"Forbidden building","reasonCode":"initial-setup"},"deny-foreign-property",expected_error="PROPERTY_SCOPE")
        before=q.audit();observed=call(foreign,"reconcileCommand",{"action":"createProperty","requestId":pid});assert observed["status"]=="not_observed" and before==q.audit();q.record({"label":"cross-actor-reconciliation","status":"isolated-readonly"})

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--execute",action="store_true");p.add_argument("--run-id",default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"));p.add_argument("--receipt",type=pathlib.Path);args=p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9-]{1,60}",args.run_id):p.error("invalid run ID")
    root=Loom();schemas=schema_gate(root)
    if not args.execute:print(json.dumps({"status":"schema-qualified-no-writes","tools":{k:v["name"] for k,v in schemas.items()}}));return
    if not args.receipt or args.receipt.exists():p.error("new receipt path required")
    q=Qualification(root,args.run_id)
    try:run(root,q);status="passed"
    except Exception as exc:status="blocked";q.record({"label":"run-stopped","status":"blocked","errorType":type(exc).__name__});raise
    finally:
        args.receipt.parent.mkdir(parents=True,exist_ok=True);args.receipt.write_text(json.dumps({"runId":args.run_id,"status":locals().get("status","blocked"),"observedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"tools":{k:v["name"] for k,v in schemas.items()},"checks":q.events},indent=2)+"\n")
if __name__=="__main__":main()
