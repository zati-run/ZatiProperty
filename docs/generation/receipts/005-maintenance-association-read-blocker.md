# Blocking maintenance association disclosure

Date: 2026-10-11. Target alias: zp-dev. Native baseline: NocoBase 2.2.21.
Source base: `7084a5d0039227992179247463212a33ac8affd7`; current uncommitted generation state.
Evidence: live authenticated native GET, synthetic accounts and fixture records only.
Status: **blocked — association append permissions do not protect related fields.**

## Finding ZP-ACL-001

Vendor, owner and tenant account 1 can each request their allowed work order with
`appends=property,unit,tenancy,request,vendor`. All three requests return HTTP 200
and include all five related objects, although these associations are absent from
the roles' work-order view field allowlists. Returned keys include:

- `property.managerUserId`, `property.ownerUserId` and address.
- `tenancy.tenantUserId` and unit identity.
- `vendor.userId` and compliance dates.
- `request.description`, `request.permissionToEnter` and tenancy identity.

The vendor role has no independent property, unit, tenancy or request resource grant.
Its allowed work-order read therefore exposes related resources it cannot directly
read. Owner and tenant related field restrictions are bypassed similarly.

This is a blocker to portal acceptance and to claiming complete first-slice role
isolation. The prior scalar GET receipt remains valid only for its explicitly bounded
non-appended requests. No real customer data was used or exposed in this qualification.

## Twelve-request test matrix

| Request class | Count | Observed result |
| --- | --- | --- |
| Own work order with five appends | 3 | HTTP 200; forbidden related objects and protected keys returned — FAIL |
| Own work order with explicit protected/context field projection | 3 | HTTP 200; only `id` and `state` returned — PASS |
| Foreign work order with appends | 3 | HTTP 200; `data: null` — PASS |
| Foreign work order with explicit field projection | 3 | HTTP 200; `data: null` — PASS |

Roles tested: `zp_vendor.1`, `zp_owner.1`, `zp_tenant.1`. Each was signed in via
Loom's discovered native authentication tool, then used its own token and role header
for GET requests. No permission grants, domain writes or app-authoring mutations were
performed. Tokens and raw field values were not included in this receipt.

## Reproduction contract

Use each synthetic role's authenticated context to GET `zp_work_orders:get` with
its own native fixture ID and query `appends=property,unit,tenancy,request,vendor`.
Repeat with the other graph's work-order ID. Separately request these `fields`:
`id,state,approvalRequired,approvalGranted,propertyId,unitId,tenancyId,requestId,vendorId,property.managerUserId,property.ownerUserId,tenancy.tenantUserId,vendor.userId`.

Required fix: enforce association and nested-field authorization server-side for
native reads, including direct caller-selected appends. Make the fix reusable and
incorporate it through Loom's qualified plugin workflow; do not merely hide relation
controls or broaden grants. Preserve required safe context through explicit reviewed
projections. Recheck nested appends, relation resource endpoints and role-allowed
context after remediation. This receipt does not qualify unused reports or exports.

## Sanitized observed response shapes

Scalar values below are represented only by their type. Object key names, response
status and collection counts are evidence; credentials and domain values are omitted.

```json
[
  {
    "account": "zp_vendor.1",
    "foreign": false,
    "mode": "appends",
    "httpStatus": 200,
    "shape": {
      "data": {
        "id": "int",
        "priority": "str",
        "state": "str",
        "title": "str",
        "createdById": "int",
        "vendor": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "name": "str",
          "trade": "str",
          "active": "bool",
          "insuranceExpiresAt": "str",
          "licenseExpiresAt": "str",
          "userId": "int"
        },
        "property": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "name": "str",
          "address": "str",
          "managerUserId": "int",
          "ownerUserId": "int"
        },
        "unit": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "name": "str",
          "propertyId": "int"
        },
        "tenancy": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "code": "str",
          "status": "str",
          "tenantUserId": "int",
          "unitId": "int"
        },
        "request": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "title": "str",
          "description": "str",
          "priority": "str",
          "status": "str",
          "permissionToEnter": "bool",
          "propertyId": "int",
          "unitId": "int",
          "tenancyId": "int"
        }
      }
    }
  },
  {
    "account": "zp_vendor.1",
    "foreign": false,
    "mode": "fields",
    "httpStatus": 200,
    "shape": {
      "data": {
        "id": "int",
        "state": "str"
      }
    }
  },
  {
    "account": "zp_vendor.1",
    "foreign": true,
    "mode": "appends",
    "httpStatus": 200,
    "shape": {
      "data": "NoneType"
    }
  },
  {
    "account": "zp_vendor.1",
    "foreign": true,
    "mode": "fields",
    "httpStatus": 200,
    "shape": {
      "data": "NoneType"
    }
  },
  {
    "account": "zp_owner.1",
    "foreign": false,
    "mode": "appends",
    "httpStatus": 200,
    "shape": {
      "data": {
        "id": "int",
        "priority": "str",
        "state": "str",
        "title": "str",
        "createdById": "int",
        "request": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "title": "str",
          "description": "str",
          "priority": "str",
          "status": "str",
          "permissionToEnter": "bool",
          "propertyId": "int",
          "unitId": "int",
          "tenancyId": "int"
        },
        "property": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "name": "str",
          "address": "str",
          "managerUserId": "int",
          "ownerUserId": "int"
        },
        "unit": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "name": "str",
          "propertyId": "int"
        },
        "tenancy": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "code": "str",
          "status": "str",
          "tenantUserId": "int",
          "unitId": "int"
        },
        "vendor": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "name": "str",
          "trade": "str",
          "active": "bool",
          "insuranceExpiresAt": "str",
          "licenseExpiresAt": "str",
          "userId": "int"
        }
      }
    }
  },
  {
    "account": "zp_owner.1",
    "foreign": false,
    "mode": "fields",
    "httpStatus": 200,
    "shape": {
      "data": {
        "id": "int",
        "state": "str"
      }
    }
  },
  {
    "account": "zp_owner.1",
    "foreign": true,
    "mode": "appends",
    "httpStatus": 200,
    "shape": {
      "data": "NoneType"
    }
  },
  {
    "account": "zp_owner.1",
    "foreign": true,
    "mode": "fields",
    "httpStatus": 200,
    "shape": {
      "data": "NoneType"
    }
  },
  {
    "account": "zp_tenant.1",
    "foreign": false,
    "mode": "appends",
    "httpStatus": 200,
    "shape": {
      "data": {
        "id": "int",
        "priority": "str",
        "state": "str",
        "title": "str",
        "createdById": "int",
        "request": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "title": "str",
          "description": "str",
          "priority": "str",
          "status": "str",
          "permissionToEnter": "bool",
          "propertyId": "int",
          "unitId": "int",
          "tenancyId": "int"
        },
        "property": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "name": "str",
          "address": "str",
          "managerUserId": "int",
          "ownerUserId": "int"
        },
        "unit": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "name": "str",
          "propertyId": "int"
        },
        "tenancy": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "code": "str",
          "status": "str",
          "tenantUserId": "int",
          "unitId": "int"
        },
        "vendor": {
          "id": "int",
          "createdById": "int",
          "updatedById": "int",
          "name": "str",
          "trade": "str",
          "active": "bool",
          "insuranceExpiresAt": "str",
          "licenseExpiresAt": "str",
          "userId": "int"
        }
      }
    }
  },
  {
    "account": "zp_tenant.1",
    "foreign": false,
    "mode": "fields",
    "httpStatus": 200,
    "shape": {
      "data": {
        "id": "int",
        "state": "str"
      }
    }
  },
  {
    "account": "zp_tenant.1",
    "foreign": true,
    "mode": "appends",
    "httpStatus": 200,
    "shape": {
      "data": "NoneType"
    }
  },
  {
    "account": "zp_tenant.1",
    "foreign": true,
    "mode": "fields",
    "httpStatus": 200,
    "shape": {
      "data": "NoneType"
    }
  }
]
```

## Expanded regression baseline

The reusable read-only regression script `scripts/maintenance_read_security.py` exercised 89 authenticated GET requests: flat and nested appends, scalar and dotted field projections, own/foreign relation resource endpoints, baseline own reads, and five manager context-resource reads. Baseline result: 68 passed, 21 failed; portal acceptance remains blocked. Existing scalar read acceptance is preserved only in its bounded form. The expanded suite also detects nested identity exposure through the manager's permitted vendor association and its property-permission relation. A passing guard regression must protect the target collection's field and row boundaries even for an allowed parent association.

Proposed desired-state manager view grants add property/unit/tenancy to maintenance requests and property/unit/tenancy/request to work orders. These support the required context display but must not be applied until the reusable association guard passes independent review and qualification. Write fields remain unchanged.
