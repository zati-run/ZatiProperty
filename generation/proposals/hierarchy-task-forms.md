# Next bounded E3 hierarchy task slice

Source preparation only. RFC 6.1 requires Property → optional Building → Unit. The existing protected domain service already exposes createBuilding and createUnit with manager property scope, contextual building/property checks, idempotent commands and audit/outbox transactions. Read-only live Loom discovery exposed create_building and create_unit typed tools; this is exposure evidence, not execution acceptance. The existing manager read projection already includes buildings.propertyId and units.buildingId, avoiding hidden numeric identity inputs.

Prepare two focused native protected forms: “Add a building to this property” in the property details context; “Add a unit to this building” in a building details context. Each has one named primary save, name/reference and explicit reason. Context IDs are server-bound and hidden; no generic create permission is added. Saved result uses scoped native record readback. The latter placement requires a native Buildings table under property context, with View detail popup and one-level associated ancestry. Exact grid bindings must be read and independently qualified after native generation; none are invented here. Source normalizers pass both configs against actual domain schemas and all three companion authoring schemas.

Coordinator apply sequence: finish current tenancy draft/amend/activate/end native acceptance; qualify existing properties.buildings and candidate buildings.units relation without replaying owned metadata; preserve all role baselines during schema authoring; add only manager relation read grants; generate read-only Buildings/Units context blocks; qualify exact popup ancestry and selected record custody; attach one reviewed form at a time through Loom. For each command capture one prepared UUID, click once, verify native result and command receipt, reload, and test cross-manager/portal denial. Never count source templates as generated functionality.

Property-level units without a building remain an explicit follow-up: current createUnit command accepts omitted buildingId, but rendering its entire schema would expose an unscoped numeric building input in a property-context form. A bounded optional-input presentation contract or scoped property-filtered building selector must be qualified before that journey. Do not silently force every property to have a building.

## Remaining RFC coverage and dependency order

- 5.1: current versioned draft parties/terms and guarded lifecycle are partial. Sequence-generated reference, lease expiry/review/inspection fields, legacy open/closed transition service, recurring charges, deposit ledger and private attachments remain outstanding. Financial elements depend on protected ledger work, not generic CRUD.
- 5.3 and 6.6: private document ingestion/access/scan gates must precede communication attachments; threads, templates, consent/quiet hours and delivery status remain planned. No external send is authorized.
- 5.4: insurance policy metadata, reviewed document verification and expiry task generation are a bounded later slice; force-placed charges remain behind jurisdiction and ledger gates.
- 5.6: prospect source/pipeline/follow-up tasks can follow E3 domain landing. Conversion must preserve identity; showing sync and external publication remain synthetic adapters until qualified.
- 5.7: subsidy contract dates, agency/tenant split and recertification task proposals are planned. Payment reconciliation and receivables require ledger invariants.
- 5.8: current protected commands create immutable audit/outbox rows; all named RFC events and delivery automation are not complete. No dispatcher is enabled.
- 5.9: immutable rent-review proposals and postpone/maintain/change decisions require notice-rule checks and approved document generation; no sending or ledger side effects implied.
- 6.1: ownership complete-set service exists but its manager rendered workflow and access transitions need acceptance. Unit capacity/per-room leasing remains unimplemented.
- 6.3: native hierarchy navigation is not a portfolio financial dashboard. Occupancy/expiration can be qualified from lifecycle data; delinquency, collections, NOI and maintenance spend await ledger-backed reproducible views. No fabricated totals.

Authoritative plan E3/T3.1 spans these remaining requirements and stays open. E4 leasing and E5 portal expansion retain their T3.5 dependency; this source preparation does not close it.
