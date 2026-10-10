# Maintenance role read verification

Date: 2026-10-10. Target alias: zp-dev. Evidence class: live role-authenticated native GET.
Source base: `7084a5d0039227992179247463212a33ac8affd7`. Tested uncommitted artifact digests:

| Artifact | SHA-256 |
| --- | --- |
| scripts/maintenance_roles.py | b35ce10f5d1f3339f4c30f7ab21670c5f9f9ffb3cd48f45f496071d6c71f9b4e |
| generation/roles/maintenance-native.json | 2f245f2d729bc9aa03a283c2eb53506cacf72ac2d101ab47f19c71b2acf08d5e |
| generation/fixtures/maintenance.json | c755cd1effa8857ad987f3553daabd67b15393554789a92e494a050f62958305 |

## Scope and result

Eight synthetic accounts, two each for property manager, owner, tenant and vendor, were authenticated through the discovered Loom native sign-in operation. Tokens remained private and were used only for direct native GET verification. No data or permission mutations were performed by this verification lane.

**Passed: 30 resource cases, comprising 90 record-access requests and 30 protected-field assertions.** Each case checks own-record GET returns the expected native ID, foreign-record GET discloses no record, and foreign-ID filtered LIST returns no record. Eight additional constructor-owned vendor-property join LIST requests were denied. Eight authenticated role-context checks succeeded. These are 106 authenticated GET requests total; sign-in operations are counted separately.

| Role | Accounts | Resource cases | Resources |
| --- | --- | --- | --- |
| Property manager | 2 | 12 | Properties, units, tenancies, vendors, maintenance requests, work orders |
| Owner | 2 | 8 | Properties, units, maintenance requests, work orders |
| Tenant | 2 | 6 | Tenancies, maintenance requests, work orders |
| Vendor | 2 | 4 | Vendors, work orders |

Observed HTTP outcomes:

```json
{
  "recordRequests": {
    "ownGetHttp": {
      "200": 30
    },
    "foreignGetHttp": {
      "200": 30
    },
    "foreignListHttp": {
      "200": 30
    }
  },
  "constructorJoinRequests": {
    "403": 8
  }
}
```

A denied read can be HTTP 200 with an empty payload. The assertions check absence of data, not a presumed status code. Protected scalar identity and approval fields were absent from successful records.

## Reconciled initial failures

Initial runs stopped on the vendor own-work-order assertion while fixture work orders lacked vendor assignment. That was an unmet fixture precondition, not evidence of an ACL leak. After the coordinator assigned the first work order, 29 of 30 cases passed and the second unassigned work order remained inaccessible. After coordinator assignment of the second fixture work order, the full suite passed. No permission grants were broadened to repair the test. A manager-authenticated read confirmed work order 1 had state `quote` and vendor ID 1 during reconciliation.

## Command and limitations

```sh
ZP_RUNTIME_DIR=<private-runtime> python3 scripts/maintenance_roles.py --verify-reads --bindings <private-runtime>/maintenance-fixture-ids.json
```

The command exited 0 and reported `roleReadChecks: 30`, `status: passed`, `writesVerified: false`. The sanitized per-account results are recorded below. Credentials, endpoint addresses and private runtime paths are excluded.

This bounded suite does not verify write permissions, relation appends, report/export paths, rendered pages, keyboard interaction, reload persistence, ledger behavior or production readiness. Role-specific write checks owned by the coordinator require their separate receipt. Portal capabilities beyond this first maintenance slice remain planned.

## Per-account evidence

```json
{
  "evidence": "role-authenticated-native-GET",
  "results": [
    {
      "account": "zp_property_manager.1",
      "resource": "zp_properties",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_property_manager.1",
      "resource": "zp_units",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_property_manager.1",
      "resource": "zp_tenancies",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_property_manager.1",
      "resource": "zp_vendors",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_property_manager.1",
      "resource": "zp_maintenance_requests",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_property_manager.1",
      "resource": "zp_work_orders",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_property_manager.2",
      "resource": "zp_properties",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_property_manager.2",
      "resource": "zp_units",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_property_manager.2",
      "resource": "zp_tenancies",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_property_manager.2",
      "resource": "zp_vendors",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_property_manager.2",
      "resource": "zp_maintenance_requests",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_property_manager.2",
      "resource": "zp_work_orders",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_owner.1",
      "resource": "zp_properties",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_owner.1",
      "resource": "zp_units",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_owner.1",
      "resource": "zp_maintenance_requests",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_owner.1",
      "resource": "zp_work_orders",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_owner.2",
      "resource": "zp_properties",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_owner.2",
      "resource": "zp_units",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_owner.2",
      "resource": "zp_maintenance_requests",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_owner.2",
      "resource": "zp_work_orders",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_tenant.1",
      "resource": "zp_tenancies",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_tenant.1",
      "resource": "zp_maintenance_requests",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_tenant.1",
      "resource": "zp_work_orders",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_tenant.2",
      "resource": "zp_tenancies",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_tenant.2",
      "resource": "zp_maintenance_requests",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_tenant.2",
      "resource": "zp_work_orders",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_vendor.1",
      "resource": "zp_vendors",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_vendor.1",
      "resource": "zp_work_orders",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_vendor.2",
      "resource": "zp_vendors",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    },
    {
      "account": "zp_vendor.2",
      "resource": "zp_work_orders",
      "ownGet": "pass",
      "foreignGet": "denied",
      "foreignList": "denied",
      "protectedFields": "absent",
      "ownGetHttp": 200,
      "foreignGetHttp": 200,
      "foreignListHttp": 200
    }
  ],
  "constructorJoinDenials": [
    {
      "account": "zp_property_manager.1",
      "resource": "zp_vendor_properties",
      "httpStatus": 403
    },
    {
      "account": "zp_property_manager.2",
      "resource": "zp_vendor_properties",
      "httpStatus": 403
    },
    {
      "account": "zp_owner.1",
      "resource": "zp_vendor_properties",
      "httpStatus": 403
    },
    {
      "account": "zp_owner.2",
      "resource": "zp_vendor_properties",
      "httpStatus": 403
    },
    {
      "account": "zp_tenant.1",
      "resource": "zp_vendor_properties",
      "httpStatus": 403
    },
    {
      "account": "zp_tenant.2",
      "resource": "zp_vendor_properties",
      "httpStatus": 403
    },
    {
      "account": "zp_vendor.1",
      "resource": "zp_vendor_properties",
      "httpStatus": 403
    },
    {
      "account": "zp_vendor.2",
      "resource": "zp_vendor_properties",
      "httpStatus": 403
    }
  ],
  "writes": "not tested; use role-bound Loom instance or native end-user UI",
  "appendsAndReports": "not tested by this bounded GET suite"
}
```
