#!/usr/bin/env python3
"""Read-only hierarchy role matrix. Synthetic identities authenticate through Loom."""
import argparse,json,os,sys,urllib.request,urllib.parse,urllib.error,datetime,pathlib
from loom_mcp import Loom
from verify_property_commands import tool,unwrap
ROOT=pathlib.Path(__file__).resolve().parents[1]
def cases(manager,graph):
    ownproperty,ownunit,units,tenancies=(4,3,[3,4],[4,5]) if graph=="1" else (2,2,[2],[2])
    return [
      ("property-units",f"zp_properties/{ownproperty}/units:list",{"pageSize":50},units if manager else None,"list"),
      ("unit-tenancies",f"zp_units/{ownunit}/tenancies:list",{"pageSize":50},tenancies if manager else None,"list"),
      ("append-units","zp_properties:get",{"filterByTk":ownproperty,"appends[]":["units"]},units if manager else None,"units"),
      ("append-tenancies","zp_units:get",{"filterByTk":ownunit,"appends[]":["tenancies"]},tenancies if manager else None,"tenancies"),
      ("nested-hierarchy","zp_properties:get",{"filterByTk":ownproperty,"appends[]":["units.tenancies"]},None,"nested"),
      ("foreign-property-units",f"zp_properties/{2 if graph=='1' else 4}/units:list",{"pageSize":50},None,"list"),
      ("foreign-unit-tenancies",f"zp_units/{2 if graph=='1' else 3}/tenancies:list",{"pageSize":50},None,"list"),
      ("foreign-append","zp_properties:get",{"filterByTk":2 if graph=="1" else 4,"appends[]":["units.tenancies"]},None,"scoped-get"),
      ("sensitive-tenancy-field","zp_tenancies:get",{"filterByTk":4,"fields[]":["id","tenantUserId"]},None,"get"),
      ("users-denied","users:list",{"pageSize":1},None,"list"),
      ("protected-audit-denied","zp_domain_events:list",{"pageSize":1},None,"list")]
def validate(status,body,expected,kind):
    if expected is None:return status==403 or (kind=="scoped-get" and status==200 and body.get("data","missing") is None)
    if status!=200:return False
    data=body.get("data")
    rows=data if kind=="list" else data.get("units" if kind=="nested" else kind) if isinstance(data,dict) else None
    if not isinstance(rows,list) or sorted(int(r["id"]) for r in rows)!=sorted(expected):return False
    if kind=="nested":
        for row in rows:
            if not isinstance(row.get("tenancies"),list):return False
            expected_children={2:[2],3:[4,5],4:[]}.get(int(row["id"]))
            if expected_children is None or sorted(int(t["id"]) for t in row["tenancies"])!=expected_children:return False
            if any(str(t.get("unitId",row["id"]))!=str(row["id"]) for t in row["tenancies"]):return False
    return True
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--receipt",type=pathlib.Path,default=ROOT/"docs/generation/receipts/hierarchy-role-native-matrix.json");args=parser.parse_args()
    if args.receipt.exists():raise RuntimeError("Preserve previous receipt")
    runtime=pathlib.Path(os.environ["ZP_RUNTIME_DIR"]);client=Loom()
    base=json.loads((runtime/"loom.json").read_text())["backendURL"].rstrip("/")
    accounts=json.loads((runtime/"maintenance-test-accounts.json").read_text());results=[]
    for key,account in sorted(accounts.items()):
        role,graph=key.rsplit(".",1)
        if role not in ["zp_property_manager","zp_owner","zp_tenant","zp_vendor"]:continue
        auth=client.call(tool(client,"loom_native_auth_sign_in_"),{"requestBody":{"account":account["email"],"password":account["password"]},"X-Authenticator":"basic"})
        token=unwrap(auth).get("token")
        if not token:raise RuntimeError("Authentication failed")
        def get(path,params):
            request=urllib.request.Request(base+"/"+path+"?"+urllib.parse.urlencode(params,doseq=True),headers={"Authorization":"Bearer "+token,"X-Role":role,"Accept":"application/json"},method="GET")
            try:
                with urllib.request.urlopen(request,timeout=30) as r:return r.status,json.load(r)
            except urllib.error.HTTPError as e:return e.code,{}
        status,context=get("roles:check",{})
        if status!=200 or context.get("data",{}).get("role")!=role or context["data"].get("allowAll") is True:raise RuntimeError("Effective role mismatch")
        for label,path,params,expected,kind in cases(role=="zp_property_manager",graph):
            status,body=get(path,params);ok=validate(status,body,expected,kind)
            results.append({"actor":key,"case":label,"status":status,"passed":ok,"expectedIds":expected})
    output={"observedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"checks":results,"passed":sum(x["passed"] for x in results),"total":len(results),"allPassed":all(x["passed"] for x in results)}
    destination=args.receipt
    if destination.exists():raise RuntimeError("Preserve previous receipt; use separate worktree for rerun")
    destination.write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps({"passed":output["passed"],"total":output["total"],"failed":[x for x in results if not x["passed"]]}))
    if not output["allPassed"]:sys.exit(1)
if __name__=="__main__":main()
