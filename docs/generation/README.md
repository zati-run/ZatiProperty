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
MCP authoring. Seven maintenance-context collections, two native pages, four scoped
roles and eight synthetic accounts have been generated. See the receipts for exact
versions, identifiers and separate verification results.

The representative maintenance journey is still under verification. Association
read disclosure ZP-ACL-001 blocks portal acceptance; see receipt 005. Complete RFC
acceptance, accounting, external integrations and production are not established.
Historical preparation-only statements are not current runtime evidence.

## Design contract

Keep `generation/design.md` short and authoritative for role tasks, navigation, visual direction, native patterns and review evidence. Use the `loom-design` skill before generating UI. These design intentions are not executable Loom schemas; map them to qualified native capabilities. Review representative rendered journeys and report unsampled or unavailable browser acceptance.
