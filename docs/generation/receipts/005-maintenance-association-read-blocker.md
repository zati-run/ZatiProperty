# Blocking maintenance association disclosure

Date: 2026-10-10. Target alias: zp-dev. Native baseline: NocoBase 2.2.21.
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

## Guard 0.1.1 live domain regression

After Loom installation of the independently reviewed 0.1.1 guard and explicit manager context view grants, the expanded suite passed **91 of 91 authenticated GET requests**. Both positive manager-context requests return the required related objects, sanitized by target permissions. Scalar own reads remain available; foreign rows, ungranted appends, nested relations and protected field projections disclose no unauthorized data. Native keys are restored, addressing AG-001 for these observed domain reads.

The first run reported eight harness failures because deliberate forbidden-field projections were required to return HTTP 200. The agreed guard design rejects these with HTTP 403. The harness was corrected to accept fail-closed denial for these adversarial projections while keeping separate own-record and manager-context tests strictly positive. The second run passed every case. No application state or grants were changed by the verifier.

HTTP outcome counts: `{"200": 18, "403": 73}`. Sanitized response keys/types and per-case outcomes are in [maintenance-read-security.json](maintenance-read-security.json). Script SHA-256: `31c9fe7c94fa356717d822b70d96caf4fb50489e2c042355fe3f81813333468b`.

**Bounded disposition:** ZP-ACL-001 is remediated for this tested native maintenance GET/LIST/association surface. Portal acceptance remains blocked pending complete native metadata/menu compatibility, rendered role journeys and other required gates. A separately observed guard rejection of system role-route metadata is outside these 91 domain requests and remains open. This result does not qualify all runtime actions, exports, reports, union roles or production. Historical failing evidence above is retained.

## Final bounded 0.1.2 disposition

See [012-maintenance-access-and-selector-regression](012-maintenance-access-and-selector-regression.md): the latest guard and reviewed manager scopes pass 91 security GETs, 32 scalar resource cases and eight mixed-mapping/dynamic-date selector GETs. This closes ZP-ACL-001 and AG-001 for the tested maintenance read surface. Complete portal/UI/product acceptance remains separately gated. Historical failures above are retained.
