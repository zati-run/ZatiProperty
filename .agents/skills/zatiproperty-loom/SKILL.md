---
name: zatiproperty-loom
description: Generate, extend, or verify ZatiProperty on NocoBase through Loom MCP. Use for every ZatiProperty collection, page, role, workflow, fixture, plugin integration, and application generation task.
---

# Generate ZatiProperty through Loom

## Mandatory path

Read `AGENTS.md`, `docs/rfc/rfc-001.md` and `docs/generation/README.md` from the
project root. Loom MCP MUST be the construction interface for this application.
NocoBase CE is the runtime and system of record. Do not replace the native app with
a custom frontend/backend, mock database, or direct REST/CLI/SQL/UI configuration.
The RFC's property, tenancy, leasing, maintenance, accounting and automation scope
remains authoritative; a CRUD demo is not completion of that scope.

This skill supplies instructions, not tools or permissions. Discover the actual MCP
connection and schemas in the current agent session. If no Loom MCP connection is
available, prepare local artifacts and report the missing endpoint/role/catalog;
never claim generation succeeded or fabricate tool calls. The installed `loom`
launcher alone is not proof of a running or configured service.

## 1. Qualify the target

- Confirm the authorized installation, environment and application boundary. Read
  endpoint credentials from the configured secret facility; never ask for secrets
  in chat or embed them in artifacts. Record only a safe target alias.
- Discover server identity, tools and their current input schemas. Verify the
  pinned NocoBase/Loom revisions, installed packages, CE entitlement and target role.
  Ask for missing non-secret connection information only when required.
- Prefer the narrowest endpoint with the required qualified capability:

  | Surface | Permitted use and limit |
  | --- | --- |
  | `/mcp` | Scoped collection reads; cannot generate an app |
  | `/ui/mcp` | Supported typed UI subset; credential authorizes the whole bound application and does not inherit read collection/field/tenant restrictions. Limited operations are not resource isolation; not universal form/layout authoring |
  | `/native/mcp` | Opt-in native catalog for supported configuration/data/workflow operations; can have app-wide authority outside the read bridge scopes |

- Do not infer tool names, parameter shapes, CE availability, or write authority from
  another installation. Capture catalog evidence and map required capabilities to
  actually discovered operations before constructing mutation requests.
- Missing capabilities stop the affected batch. Specify a bounded Loom extension or
  supported custom plugin integration path and seek its owning implementation;
  do not bypass the bridge. Plugin source can be authored in this repository for a
  documented gap, but installation/configuration through Loom must be qualified.

## 2. Describe the entire app before applying batches

Keep desired state in `generation/` using the artifact contract in
`docs/generation/README.md`. These files are reviewable project specifications,
not a promise that Loom directly executes a manifest format. Translate them into
calls only after discovering the live tool schemas.

Map every RFC requirement to one of: planned, generated, verified, blocked, or
explicitly deferred by the owner/RFC. Record the matching logical IDs, native IDs,
capability evidence, plugin need and acceptance evidence. Declare namespaces and
ownership; never adopt or overwrite pre-existing resources just because names match.

Arrange coherent, reviewable batches in this dependency order:

1. Installation/package and identity qualification; company settings, reference
   data, properties/units/contacts, role boundaries and initial synthetic fixtures.
2. Prospects, applications, leases, tenancies, documents and role-scoped native pages.
3. Maintenance requests, work orders, inspections, vendors and scoped vendor views.
4. Protected ledger/audit/security plugins and trust invariants before financial
   workflows; accounting, reconciliation, statements and approval interfaces.
5. Owner/tenant portals, notifications and external adapter contracts; sandbox
   qualification only within specifically approved environments.
6. Runtime AI tools/workflows with explicit permissions, migrations, backups,
   restore checks, accessibility, and complete end-to-end acceptance.

No batch order relaxes the RFC's licensing, access, financial or release gates.
Review proposed collections/relations, role scopes, pages, workflow side effects,
plugin changes and rollback/repair paths before applying. Current owner scope is
preparation only; live application generation must be a subsequent authorized task.

## 3. Apply through Loom and reconcile

- Read current native state, resolve logical/native bindings, and calculate an
  explicit diff. Verify ownership and target before each bounded mutation batch.
- Follow each discovered tool's validation, fingerprint, concurrency, pagination,
  and error contract. Do not invent transactions or idempotency guarantees.
- Apply only authorized changes using the qualified Loom MCP tool. Validate with
  immediate native readback and record observed identifiers/state.
- On timeout or ambiguous results, mark the operation `unknown`, stop dependent
  writes and reconcile by native readback. Retry only after establishing whether
  an effect occurred and selecting a safe correction. Never replay an entire batch
  blindly. Destructive changes require an explicit reviewed scope and recovery path.
- Operator UI customizations are drift to reconcile into desired state, not a
  second untracked authoring process. Protect ledger/audit/security configuration.

## 4. Verify real behavior

Use synthetic role-specific accounts/fixtures to verify allowed actions and denied
cross-owner/tenant/vendor access, including field visibility and generated actions.
Check persisted records across reload and native page navigation/edit/save. Verify
workflow trigger/execution and error handling, not just its saved definition.

Custom domain services require invariant and transaction tests. Financial batches
must demonstrate balanced immutable postings, idempotency and reversals, trust
segregation, and denied generic writes. Do not use generic native data operations
to post money or bypass protected services. Runtime AI cannot gain construction
credentials or financial/decision authority through this skill.

Store sanitized receipts, revision/catalog identity, scope, checks, failures and
recovery state under `docs/generation/receipts/`. Report app-native persistence,
UI/role/workflow acceptance and external provider verification separately. A tool
response, fixture suite or generated artifact is not production readiness.

## 5. Handoff

Update the requirement coverage and bindings after each accepted batch. State what
is generated, what is verified, what is blocked and the next dependency. Keep work
ownership in `ajent.social`, without secrets, private hosts or customer data.
Do not declare the entire property management system complete while RFC requirements
remain unmapped, unverified, or silently replaced with placeholders.
