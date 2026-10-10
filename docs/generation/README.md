# ZatiProperty generation records

The construction authority is [RFC-ZP-0001](../rfc/rfc-001.md). The execution
procedure is [zatiproperty-loom](../../.agents/skills/zatiproperty-loom/SKILL.md).
This contract separates intended state, observed generation and acceptance evidence.

## Desired state

When generation begins, create the following reviewed artifacts in `generation/`:

| Artifact | Contents |
| --- | --- |
| `app.yaml` | App identity, stable logical `zp.*` identifiers, installation alias, declared native namespace/ownership, pinned versions, requirement coverage and approved batch scope |
| `collections/` | Domain entities, fields, relations, constraints and native capability mappings |
| `roles/` | Role-by-collection/action/field allow/deny matrix and record scopes |
| `pages/` | Native routes, menus, blocks, fields and actions with role visibility |
| `workflows/` | Triggers, transitions, approvals, side effects and recovery behavior |
| `plugins/` | Gap justification, plugin revision/package, install dependency and protected interfaces |
| `fixtures/` | Synthetic records and role-specific acceptance scenarios |
| `bindings/` | Stable logical IDs mapped to observed native IDs and owned-resource fingerprints |

These are project-owned desired-state artifacts. They are not a native Loom input
schema or an executable generator until a translator is actually implemented and
qualified. The agent maps them to the live MCP schemas. Do not commit a configuration
that embeds endpoint secrets or claims unverified bindings.

## Capability and coverage record

For each requirement or coherent requirement group record:

- RFC section and stable requirement ID.
- Desired native resources and ownership boundary.
- Status: `planned`, `generated`, `verified`, `blocked`, or `deferred`.
- Discovered endpoint, exact operation/schema/catalog identity, package and role.
- Custom plugin gap and dependency if needed.
- Native IDs, applicable checks and evidence references.
- Missing capability, unknown operation outcome or approved deferral, if any.

A `deferred` requirement needs an explicit owner/RFC basis. A missing API is
`blocked`, not implemented by a different platform. Empty native IDs are planning
information, not generated resources.

## Execution receipts

Write sanitized Markdown/JSON receipts under `docs/generation/receipts/`. Each
receipt records source revision, safe target alias, actor role, catalog evidence,
authorized batch, before/after state, returned native IDs, verification commands or
observations, failures, uncertain effects and recovery decisions. Raw credentials,
customer data and private infrastructure identifiers do not belong in receipts.

Keep backend readback, role denial/allowance, browser acceptance, plugin tests,
provider sandbox checks, deployment and production acceptance as separate claims.
Cross-role checks are required even though one install serves one company.

## Current state

The owner authorized synthetic development implementation and an isolated DGX
installation. The `zp-dev` target runs NocoBase CE 2.2.21 and qualified Loom native
MCP authoring. The bounded maintenance journey has independently reviewed local
integration and native role, persistence and rendered evidence; see receipt015,
the final manager journey and feedback receipts. Association-read guard0.1.3
resolved the previously recorded maintenance disclosure within the tested scope.

Property/tenancy generation is in progress. Domain plugin0.1.4 and Loom
action-form0.1.9 support protected commands without generic CRUD grants.
Property creation has independent browser/reload/role evidence (020–021).
Draft creation and amendment have saved journeys and independent persistence,
prefill and eight-account checks (022–024). Activation/end, stale context denial,
and independent lifecycle/audit checks are recorded separately (026–027).
Receipt028 is controlled error-rendering evidence, not backend acceptance.

The reverse hierarchy relationship remains absent: Loom's transactional preview
identified a native foreign-key allowNull metadata mismatch (025,029); persistent
fields and permissions remained unchanged. The delayed anonymous authentication
failure still needs successful session-retention browser evidence. Broader E3
work, complete role/workflow/concurrency coverage and UI polish remain open.

Complete RFC acceptance, accounting, external integrations and production are not
established. Historical preparation-only statements are not current runtime evidence.

## Design contract

Keep `generation/design.md` short and authoritative for role tasks, navigation, visual direction, native patterns and review evidence. Use the `loom-design` skill before generating UI. These design intentions are not executable Loom schemas; map them to qualified native capabilities. Review representative rendered journeys and report unsampled or unavailable browser acceptance.
