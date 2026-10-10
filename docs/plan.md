# ZatiProperty implementation delivery plan

Status: implementation plan; pinned Wazi conformance required on these exact bytes before dispatch. No task below claims live acceptance.
Plan ID: zatiproperty:implementation
Authority ID: zatiproperty:repository
Authored revision: implementation-r1

## Scope and authority

The owner authorized app implementation through Loom MCP and a synthetic DGX development installation, including reusable Loom repairs and enabled app authoring. Historical workflow-only RFC text is superseded for this session's authority, not silently treated as app evidence. Production, customer data, external communication, live payments and consequential financial actions remain outside authority. One company per installation, CE-only native NocoBase, and protected ledger/audit invariants remain mandatory.

The authoritative task graph is this file. [Coverage](../generation/coverage.md) indexes the RFC without introducing another task graph. [Design](../generation/design.md) defines the initial native UI direction. [Generation records](generation/README.md) define evidence. Actual installation and catalog qualification remain T1.0 obligations.

## Acceptance and delivery

Every slice requires exact source and target revisions, native IDs and before/after readback, persistence after reload, allowed and denied role cases, workflow behavior and rendered desktop/narrow journeys. UI verification includes browser golden-path and error/denied cases, keyboard and accessibility checks; API changes require actual request/status/body tests. Financial/security code needs domain review in addition to independent code review. Local, fixture, live app, provider and production evidence remain separate.

Each epic is one coherent reviewable outcome batch; reusable Loom changes may use their owning repository PR with explicit cross-repository SHA dependencies. No batch merges without independently reviewed exact head and applicable checks. Existing protections remain intact. Blocked billing is recorded as unavailable hosted CI, never a passing status. No task is complete until its stated gate has evidence.

## Checkable work breakdown

### E1 -- Foundation and Loom qualification
fidelity: executable
Acceptance: RFC sections 1, 2, 3, 4; the pinned target, licenses, packages, role, complete MCP catalog and bounded authoring operations are recorded and uncertain writes reconcile by readback.

- [ ] T1.0 Qualify authorized DGX capacity, isolated installation scope and bounded Loom bootstrap repair  Owner: coordinator  Est: bounded by qualification  kind: agent stage: preflight  verifies: [E1]  acc: [development provisioning scope, isolated storage, resource capacity, ownership, bootstrap boundary and initial missing Loom capability are recorded]
- [ ] T1.1 Qualify the authorized development installation, CE package licenses, actor role, exact tool schemas and app-authoring authority; repair missing Loom capabilities as reusable MCP product work  Owner: implementation  Est: bounded by qualification  kind: agent stage: implement  verifies: [E1]  blocked-by: [T1.0]  acc: [the pinned target, licenses, packages, role, complete MCP catalog and bounded authoring operations are recorded and uncertain writes reconcile by readback]
- [ ] T1.2 Verify E1 changed behavior  Owner: verification  Est: bounded by qualification  kind: agent stage: verify  verifies: [E1]  blocked-by: [T1.1]  acc: [E1 scoped source checks and applicable live readback, persistence, role allow/deny, workflow and rendered browser acceptance pass with sanitized receipts]
- [ ] T1.3 Independently review E1 exact candidate  Owner: independent-reviewer  Est: bounded by qualification  kind: agent stage: review  verifies: [E1]  blocked-by: [T1.2]  acc: [independent reviewer identity, base/head revisions and domain review where required are recorded with no unresolved accepted blockers]
- [ ] T1.4 Rebase merge E1 reviewed candidate  Owner: coordinator  Est: bounded by qualification  kind: agent stage: merge  verifies: [E1]  blocked-by: [T1.3]  acc: [exact approved candidate passes required checks and protected GitHub rebase merge records landed revision]
- [ ] T1.5 Verify E1 landed source and app state  Owner: verification  Est: bounded by qualification  kind: agent stage: verify-landed  verifies: [E1]  blocked-by: [T1.4]  acc: [landed revision and generated-state bindings match reviewed scope and affected acceptance passes with explicit unverified gates]

### E2 -- Maintenance representative journey
fidelity: executable
Acceptance: RFC sections 8.1, 8.2, 8.4, 11, 13; a manager opens a synthetic request, sees correct property and tenancy context, assigns only a permitted vendor and observes persisted status after reload.

- [ ] T2.0 Qualify E2 prerequisites and capability mapping  Owner: coordinator  Est: bounded by qualification  kind: agent stage: preflight  verifies: [E2]  blocked-by: [T1.5]  acc: [RFC coverage, native capability mapping, ownership and safe synthetic batch scope are recorded]
- [ ] T2.1 Generate minimal property, unit, tenancy and vendor context with manager maintenance queue and assignment flow  Owner: implementation  Est: bounded by qualification  kind: agent stage: implement  verifies: [E2]  blocked-by: [T2.0]  acc: [a manager opens a synthetic request, sees correct property and tenancy context, assigns only a permitted vendor and observes persisted status after reload]
- [ ] T2.2 Verify E2 changed behavior  Owner: verification  Est: bounded by qualification  kind: agent stage: verify  verifies: [E2]  blocked-by: [T2.1]  acc: [E2 scoped source checks and applicable live readback, persistence, role allow/deny, workflow and rendered browser acceptance pass with sanitized receipts]
- [ ] T2.3 Independently review E2 exact candidate  Owner: independent-reviewer  Est: bounded by qualification  kind: agent stage: review  verifies: [E2]  blocked-by: [T2.2]  acc: [independent reviewer identity, base/head revisions and domain review where required are recorded with no unresolved accepted blockers]
- [ ] T2.4 Rebase merge E2 reviewed candidate  Owner: coordinator  Est: bounded by qualification  kind: agent stage: merge  verifies: [E2]  blocked-by: [T2.3]  acc: [exact approved candidate passes required checks and protected GitHub rebase merge records landed revision]
- [ ] T2.5 Verify E2 landed source and app state  Owner: verification  Est: bounded by qualification  kind: agent stage: verify-landed  verifies: [E2]  blocked-by: [T2.4]  acc: [landed revision and generated-state bindings match reviewed scope and affected acceptance passes with explicit unverified gates]

### E3 -- Property and tenancy operations
fidelity: executable
Acceptance: RFC sections 5.1, 5.3, 5.4, 5.6, 5.7, 5.8, 5.9, 6.1, 6.3, 6.6; native scoped journeys persist property and tenancy lifecycle changes, privacy-controlled files and synthetic insurance/subsidy/rent-review proposals with required approvals.

- [ ] T3.0 Qualify E3 prerequisites and capability mapping  Owner: coordinator  Est: bounded by qualification  kind: agent stage: preflight  verifies: [E3]  blocked-by: [T2.5]  acc: [RFC coverage, native capability mapping, ownership and safe synthetic batch scope are recorded]
- [ ] T3.1 Complete hierarchy, ownership, tenancy lifecycle, prospect CRM, insurance, subsidies, rent-review proposals, private files and domain events  Owner: implementation  Est: bounded by qualification  kind: agent stage: implement  verifies: [E3]  blocked-by: [T3.0]  acc: [native scoped journeys persist property and tenancy lifecycle changes, privacy-controlled files and synthetic insurance/subsidy/rent-review proposals with required approvals]
- [ ] T3.2 Verify E3 changed behavior  Owner: verification  Est: bounded by qualification  kind: agent stage: verify  verifies: [E3]  blocked-by: [T3.1]  acc: [E3 scoped source checks and applicable live readback, persistence, role allow/deny, workflow and rendered browser acceptance pass with sanitized receipts]
- [ ] T3.3 Independently review E3 exact candidate  Owner: independent-reviewer  Est: bounded by qualification  kind: agent stage: review  verifies: [E3]  blocked-by: [T3.2]  acc: [independent reviewer identity, base/head revisions and domain review where required are recorded with no unresolved accepted blockers]
- [ ] T3.4 Rebase merge E3 reviewed candidate  Owner: coordinator  Est: bounded by qualification  kind: agent stage: merge  verifies: [E3]  blocked-by: [T3.3]  acc: [exact approved candidate passes required checks and protected GitHub rebase merge records landed revision]
- [ ] T3.5 Verify E3 landed source and app state  Owner: verification  Est: bounded by qualification  kind: agent stage: verify-landed  verifies: [E3]  blocked-by: [T3.4]  acc: [landed revision and generated-state bindings match reviewed scope and affected acceptance passes with explicit unverified gates]

### E4 -- Leasing
fidelity: executable
Acceptance: RFC sections 5.5, 7; inquiry-to-lease and renewal fixtures pass with human screening approval, private applicant fields and no external publication or sending.

- [ ] T4.0 Qualify E4 prerequisites and capability mapping  Owner: coordinator  Est: bounded by qualification  kind: agent stage: preflight  verifies: [E4]  blocked-by: [T3.5]  acc: [RFC coverage, native capability mapping, ownership and safe synthetic batch scope are recorded]
- [ ] T4.1 Implement native listing/CMS previews, syndication fakes, applications, screening proposals, lease authoring, e-sign fakes and renewals  Owner: implementation  Est: bounded by qualification  kind: agent stage: implement  verifies: [E4]  blocked-by: [T4.0]  acc: [inquiry-to-lease and renewal fixtures pass with human screening approval, private applicant fields and no external publication or sending]
- [ ] T4.2 Verify E4 changed behavior  Owner: verification  Est: bounded by qualification  kind: agent stage: verify  verifies: [E4]  blocked-by: [T4.1]  acc: [E4 scoped source checks and applicable live readback, persistence, role allow/deny, workflow and rendered browser acceptance pass with sanitized receipts]
- [ ] T4.3 Independently review E4 exact candidate  Owner: independent-reviewer  Est: bounded by qualification  kind: agent stage: review  verifies: [E4]  blocked-by: [T4.2]  acc: [independent reviewer identity, base/head revisions and domain review where required are recorded with no unresolved accepted blockers]
- [ ] T4.4 Rebase merge E4 reviewed candidate  Owner: coordinator  Est: bounded by qualification  kind: agent stage: merge  verifies: [E4]  blocked-by: [T4.3]  acc: [exact approved candidate passes required checks and protected GitHub rebase merge records landed revision]
- [ ] T4.5 Verify E4 landed source and app state  Owner: verification  Est: bounded by qualification  kind: agent stage: verify-landed  verifies: [E4]  blocked-by: [T4.4]  acc: [landed revision and generated-state bindings match reviewed scope and affected acceptance passes with explicit unverified gates]

### E5 -- Portals and full maintenance
fidelity: executable
Acceptance: RFC sections 6.2, 6.5, 8; each portal sees only allowed records and fields; quote approval and recurring-work recovery pass; payment binding remains gated on protected accounting.

- [ ] T5.0 Qualify E5 prerequisites and capability mapping  Owner: coordinator  Est: bounded by qualification  kind: agent stage: preflight  verifies: [E5]  blocked-by: [T3.5]  acc: [RFC coverage, native capability mapping, ownership and safe synthetic batch scope are recorded]
- [ ] T5.1 Complete owner, tenant and vendor task pages, quotes and approval thresholds, inspections, work order lifecycle and recurring maintenance  Owner: implementation  Est: bounded by qualification  kind: agent stage: implement  verifies: [E5]  blocked-by: [T5.0]  acc: [each portal sees only allowed records and fields; quote approval and recurring-work recovery pass; payment binding remains gated on protected accounting]
- [ ] T5.2 Verify E5 changed behavior  Owner: verification  Est: bounded by qualification  kind: agent stage: verify  verifies: [E5]  blocked-by: [T5.1]  acc: [E5 scoped source checks and applicable live readback, persistence, role allow/deny, workflow and rendered browser acceptance pass with sanitized receipts]
- [ ] T5.3 Independently review E5 exact candidate  Owner: independent-reviewer  Est: bounded by qualification  kind: agent stage: review  verifies: [E5]  blocked-by: [T5.2]  acc: [independent reviewer identity, base/head revisions and domain review where required are recorded with no unresolved accepted blockers]
- [ ] T5.4 Rebase merge E5 reviewed candidate  Owner: coordinator  Est: bounded by qualification  kind: agent stage: merge  verifies: [E5]  blocked-by: [T5.3]  acc: [exact approved candidate passes required checks and protected GitHub rebase merge records landed revision]
- [ ] T5.5 Verify E5 landed source and app state  Owner: verification  Est: bounded by qualification  kind: agent stage: verify-landed  verifies: [E5]  blocked-by: [T5.4]  acc: [landed revision and generated-state bindings match reviewed scope and affected acceptance passes with explicit unverified gates]

### E6 -- Security and protected ledger
fidelity: executable
Acceptance: RFC sections 9.1, 9.2, 9.9, 11, 13; balanced posting, integer money, idempotency, reversals, closed periods, owner solvency, trust segregation and immutable audit hold server-side under concurrency; generic CRUD cannot write protected records.

- [ ] T6.0 Qualify E6 prerequisites and capability mapping  Owner: coordinator  Est: bounded by qualification  kind: agent stage: preflight  verifies: [E6]  blocked-by: [T1.5]  acc: [RFC coverage, native capability mapping, ownership and safe synthetic batch scope are recorded]
- [ ] T6.1 Implement qualified domain plugins for immutable double-entry posting, trust controls, hash-chained audit, MFA, sensitive fields and lifecycle retention  Owner: implementation  Est: bounded by qualification  kind: agent stage: implement  verifies: [E6]  blocked-by: [T6.0]  acc: [balanced posting, integer money, idempotency, reversals, closed periods, owner solvency, trust segregation and immutable audit hold server-side under concurrency; generic CRUD cannot write protected records]
- [ ] T6.2 Verify E6 changed behavior  Owner: verification  Est: bounded by qualification  kind: agent stage: verify  verifies: [E6]  blocked-by: [T6.1]  acc: [E6 scoped source checks and applicable live readback, persistence, role allow/deny, workflow and rendered browser acceptance pass with sanitized receipts]
- [ ] T6.3 Independently review E6 exact candidate  Owner: independent-reviewer  Est: bounded by qualification  kind: agent stage: review  verifies: [E6]  blocked-by: [T6.2]  acc: [independent reviewer identity, base/head revisions and domain review where required are recorded with no unresolved accepted blockers]
- [ ] T6.4 Rebase merge E6 reviewed candidate  Owner: coordinator  Est: bounded by qualification  kind: agent stage: merge  verifies: [E6]  blocked-by: [T6.3]  acc: [exact approved candidate passes required checks and protected GitHub rebase merge records landed revision]
- [ ] T6.5 Verify E6 landed source and app state  Owner: verification  Est: bounded by qualification  kind: agent stage: verify-landed  verifies: [E6]  blocked-by: [T6.4]  acc: [landed revision and generated-state bindings match reviewed scope and affected acceptance passes with explicit unverified gates]

### E7 -- Accounting and reporting
fidelity: executable
Acceptance: RFC sections 5.2, 6.4, 8.5, 9; synthetic rent-to-distribution and request-to-paid-work-order flows reconcile with protected ledger; financial reports derive from entries; dual control and tax filing approvals deny unapproved execution.

- [ ] T7.0 Qualify E7 prerequisites and capability mapping  Owner: coordinator  Est: bounded by qualification  kind: agent stage: preflight  verifies: [E7]  blocked-by: [T5.5, T6.5]  acc: [RFC coverage, native capability mapping, ownership and safe synthetic batch scope are recorded]
- [ ] T7.1 Implement synthetic charges/payments, fee calculations, distribution approval, bank reconciliation, statements, tax preparation, general ledger and financial reports  Owner: implementation  Est: bounded by qualification  kind: agent stage: implement  verifies: [E7]  blocked-by: [T7.0]  acc: [synthetic rent-to-distribution and request-to-paid-work-order flows reconcile with protected ledger; financial reports derive from entries; dual control and tax filing approvals deny unapproved execution]
- [ ] T7.2 Verify E7 changed behavior  Owner: verification  Est: bounded by qualification  kind: agent stage: verify  verifies: [E7]  blocked-by: [T7.1]  acc: [E7 scoped source checks and applicable live readback, persistence, role allow/deny, workflow and rendered browser acceptance pass with sanitized receipts]
- [ ] T7.3 Independently review E7 exact candidate  Owner: independent-reviewer  Est: bounded by qualification  kind: agent stage: review  verifies: [E7]  blocked-by: [T7.2]  acc: [independent reviewer identity, base/head revisions and domain review where required are recorded with no unresolved accepted blockers]
- [ ] T7.4 Rebase merge E7 reviewed candidate  Owner: coordinator  Est: bounded by qualification  kind: agent stage: merge  verifies: [E7]  blocked-by: [T7.3]  acc: [exact approved candidate passes required checks and protected GitHub rebase merge records landed revision]
- [ ] T7.5 Verify E7 landed source and app state  Owner: verification  Est: bounded by qualification  kind: agent stage: verify-landed  verifies: [E7]  blocked-by: [T7.4]  acc: [landed revision and generated-state bindings match reviewed scope and affected acceptance passes with explicit unverified gates]

### E8 -- Integration and automation
fidelity: executable
Acceptance: RFC sections 10, 12; retry and duplicate fixtures are idempotent; scoped tools deny ledger posting and adverse decisions; fair-housing safety and approval gates pass without provider sends.

- [ ] T8.0 Qualify E8 prerequisites and capability mapping  Owner: coordinator  Est: bounded by qualification  kind: agent stage: preflight  verifies: [E8]  blocked-by: [T4.5, T7.5]  acc: [RFC coverage, native capability mapping, ownership and safe synthetic batch scope are recorded]
- [ ] T8.1 Implement signed inbox/outbox recovery, adapter fake contracts, dry-run import/export, schedules, proposal inbox and scoped AI/MCP tools  Owner: implementation  Est: bounded by qualification  kind: agent stage: implement  verifies: [E8]  blocked-by: [T8.0]  acc: [retry and duplicate fixtures are idempotent; scoped tools deny ledger posting and adverse decisions; fair-housing safety and approval gates pass without provider sends]
- [ ] T8.2 Verify E8 changed behavior  Owner: verification  Est: bounded by qualification  kind: agent stage: verify  verifies: [E8]  blocked-by: [T8.1]  acc: [E8 scoped source checks and applicable live readback, persistence, role allow/deny, workflow and rendered browser acceptance pass with sanitized receipts]
- [ ] T8.3 Independently review E8 exact candidate  Owner: independent-reviewer  Est: bounded by qualification  kind: agent stage: review  verifies: [E8]  blocked-by: [T8.2]  acc: [independent reviewer identity, base/head revisions and domain review where required are recorded with no unresolved accepted blockers]
- [ ] T8.4 Rebase merge E8 reviewed candidate  Owner: coordinator  Est: bounded by qualification  kind: agent stage: merge  verifies: [E8]  blocked-by: [T8.3]  acc: [exact approved candidate passes required checks and protected GitHub rebase merge records landed revision]
- [ ] T8.5 Verify E8 landed source and app state  Owner: verification  Est: bounded by qualification  kind: agent stage: verify-landed  verifies: [E8]  blocked-by: [T8.4]  acc: [landed revision and generated-state bindings match reviewed scope and affected acceptance passes with explicit unverified gates]

### E9 -- Operational readiness and complete acceptance
fidelity: executable
Acceptance: RFC sections 14, 15, 16; all in-scope requirement rows have readback, persistence, role, workflow and rendered evidence or exact blockers; restore and migration checks preserve ledger/audit history; production remains unauthorized.

- [ ] T9.0 Qualify E9 prerequisites and capability mapping  Owner: coordinator  Est: bounded by qualification  kind: agent stage: preflight  verifies: [E9]  blocked-by: [T8.5]  acc: [RFC coverage, native capability mapping, ownership and safe synthetic batch scope are recorded]
- [ ] T9.1 Verify synthetic full-product journeys, accessibility, performance targets, backup/restore and upgrades; write operator and contributor guidance  Owner: implementation  Est: bounded by qualification  kind: agent stage: implement  verifies: [E9]  blocked-by: [T9.0]  acc: [all in-scope requirement rows have readback, persistence, role, workflow and rendered evidence or exact blockers; restore and migration checks preserve ledger/audit history; production remains unauthorized]
- [ ] T9.2 Verify E9 changed behavior  Owner: verification  Est: bounded by qualification  kind: agent stage: verify  verifies: [E9]  blocked-by: [T9.1]  acc: [E9 scoped source checks and applicable live readback, persistence, role allow/deny, workflow and rendered browser acceptance pass with sanitized receipts]
- [ ] T9.3 Independently review E9 exact candidate  Owner: independent-reviewer  Est: bounded by qualification  kind: agent stage: review  verifies: [E9]  blocked-by: [T9.2]  acc: [independent reviewer identity, base/head revisions and domain review where required are recorded with no unresolved accepted blockers]
- [ ] T9.4 Rebase merge E9 reviewed candidate  Owner: coordinator  Est: bounded by qualification  kind: agent stage: merge  verifies: [E9]  blocked-by: [T9.3]  acc: [exact approved candidate passes required checks and protected GitHub rebase merge records landed revision]
- [ ] T9.5 Verify E9 landed source and app state  Owner: verification  Est: bounded by qualification  kind: agent stage: verify-landed  verifies: [E9]  blocked-by: [T9.4]  acc: [landed revision and generated-state bindings match reviewed scope and affected acceptance passes with explicit unverified gates]

## Dependencies, risks and operating notes

E6 can progress independently of operational modules after E1; its services must be landed before E7. E4 and E5 can progress independently after E3. The maintenance-first E2 uses no ledger writes and does not qualify financial behavior. Shared target mutation is serialized by the coordinator; isolated source work may proceed under resource and ownership constraints.

Unknown CE entitlement, unsupported MCP authoring, absent domain invariants, ambiguous mutation outcomes and failed role isolation block the affected slice. Fix reusable construction gaps in Loom, qualify its MCP interfaces, then retry through Loom after state reconciliation. Do not substitute direct NocoBase mutation. Jurisdiction packs need cited fixtures and qualified review; unspecified legal coverage cannot be represented as compliance. External providers use fakes until separately authorized.

## Plan qualification

Preexisting DGX Wazi reader and semantic verifier were located by read-only discovery. The full gate initially passed all 54 tasks with pinned contract 0.0.1, semantic validity and reader compatibility. Final source digest and command output belong in the coordinator receipt after the last edit; revalidation is mandatory. This establishes syntax/semantic portability only, not authenticated execution authority or app acceptance.

## Evidence and handoff

Receipts belong under docs/generation/receipts/. Each completed coverage row names logical/native IDs and exact tool/catalog and package/role evidence. Report failed or omitted checks explicitly. After any authored plan change rerun pinned normalization, semantic validation and Markdown-reader compatibility before dispatch. Review findings get new stable fix/verification/review rows rather than erasing prior gate evidence.

## Progress log

- 2026-10-11: Established nine coherent outcome batches and 54 explicit stage tasks; all app outcomes remain planned pending primary coordinator qualification. This is embedded implementation planning, not a separate plan-only merge.
