# Maintenance access and selector live regression

Date: 2026-10-10. Target alias: zp-dev; NocoBase CE 2.2.21.
Generic association guard: 0.1.2, reviewed archive SHA-256
`ce6f865e64f9ccccd559c05f59affc1871b0d063e2d0750bde94e08f54e34384`.
Evidence: authenticated live GET requests with synthetic accounts and fixtures.
No permissions, domain records or application configuration were mutated by this verifier.

## Results

- **95/95 security GET requests passed:** scalar and dotted projections, nested
  appends, own/foreign association endpoints, positive own records, and both required
  manager context responses. Protected target fields are absent; manager context
  remains available instead of blanket relation denial.
- **32/32 scalar resource cases passed** across eight accounts: 32 own GETs,
  31 foreign GET denials, 31 foreign filtered-LIST denials, and one explicitly shared
  vendor GET/LIST pair allowed with protected fields absent. These are 96 record
  requests plus eight role-context GETs and eight mapping-list GETs: **112 GETs**.
  Both managers can read only scoped mapping rows; all six portal mapping-list
  requests return HTTP 403. An additional constructor Loom read qualified the
  declared shared mapping; it is not counted as a role-authenticated GET above.
- **8/8 native vendor-selector filter GET requests passed:** caller property
  equality and target mapping-row scope are enforced together. Dynamic today
  insurance/license conditions exclude the expired fixture. Same-manager vendors
  attached to a different property are excluded from the current property chooser.

These three suites total **215 role-authenticated GET requests**. Authentication
operations and constructor fixture readback are separate from this count.

## Mixed-row fixture and observed outcomes

Constructor-owned fixture mappings include vendor1 to property1 and property2,
vendor2 to property2, and vendor4 to property3 (property1 and property3 share manager1).
The mixed-row precondition was verified through Loom before testing. This tests that
manager1's property1 mapping cannot authorize vendor1 when caller filter asks for
property2. All selector requests returned HTTP 200 with these counts:

| Actor and property scope | Without date predicates | With active/dynamic-today predicates |
| --- | ---: | ---: |
| Manager1, property1 | 2 | 1 |
| Manager1, foreign property2 | 0 | 0 |
| Manager2, property2 | 2 | 2 |
| Manager2, foreign property1 | 0 | 0 |

The first scalar rerun correctly encountered newly authorized sharing: manager2 can
now see vendor1 because of its explicit property2 mapping. The verifier was updated
to accept that one pair only after reading and checking the exact constructor mapping.
It still checks protected fields and denies all 31 other foreign resource pairs.
No grants were broadened to make tests pass.

## Commands and evidence

With private `ZP_RUNTIME_DIR`:

```sh
python3 scripts/verify_vendor_selector_reads.py
python3 scripts/maintenance_read_security.py
python3 scripts/maintenance_roles.py --verify-reads --bindings <private-runtime>/maintenance-fixture-ids.json
```

Each final command exited 0. Sanitized per-case evidence:
[security](maintenance-read-security-results.json),
[scalar roles](maintenance-role-read-results.json),
[selector filters](vendor-selector-read-results.json).

## Disposition and limits

ZP-ACL-001 and native-key regression AG-001 are closed for this tested maintenance
read surface. This receipt qualifies native filter query behavior, not the browser
selector's installed filter configuration, empty/error feedback or persistence.
Those remain separate UI gates. It does not qualify writes, unused reports/exports,
union roles, complete portals, ledger/accounting, provider actions or production.
Historical scalar and failure receipts remain evidence for their original snapshots.

## Linked-work positive coverage

The final 95-request security suite adds own-request `workOrders:list` and `appends=workOrders` positive checks plus both foreign-request variants. All four pass after the explicit manager request.workOrders view grant; projected child fields remain protected. The original 91 cases also continue to pass.

## Exact native picker regression — guard 0.1.3

The browser exposed a query-shape gap after the earlier 0.1.2 synthetic dotted-key tests: native RecordSelect sends nested `propertyPermissions: {propertyId: {$eq: value}}` inside two `$and` groups. Guard 0.1.3 adds only that bounded normalization. Independent live reruns now pass **24/24 selector GETs** and **95/95 security GETs**, without changing expected isolation. The selector cases cover both dotted and exact native nested forms, page size 40, active/dynamic-today dates, allowed and foreign properties, mixed mapping rows and unresolved null. Eight null cases return 403 with no records; sixteen resolved cases return 200 with the expected scoped counts.

Archive SHA-256 independently reviewed: `c69fa642fc29a51af778d3b6eaf6051f324de18c1bef4c04ca5f9a6583ba97f0`. Sanitized latest evidence: [native picker cases](vendor-selector-read-results-0.1.3.json) and [security cases](maintenance-read-security-results-0.1.3.json). Response shapes preserve field names, scalar types and counts; credentials and raw scalar data are omitted. No verifier permission or domain writes occurred. These 119 requests are a separate rerun, not an addition to the earlier 215-request baseline count. Native rendered picker behavior remains a separate browser gate.
