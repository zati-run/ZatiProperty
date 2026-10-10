# Protected-form construction: read-only qualification

2026-10-10T11:21:39.106387+00:00 . App source base `0583c014b62aa1ec95145b5be3d410ab23d7af01`. No form or business writes by this lane.

Actual Loom native catalog exposes companion operations:

- `loom_native_loom_action_forms_describe_b2a66d95c8a05430`: plain actionPackage/resource/action/reconcileAction parameters.
- `loom_native_loom_action_forms_get_cefd755e47768fb3`: plain uid.
- `loom_native_loom_action_forms_create_c1120ae7942c664a`: requestBody containing uid, gridUid, expectedGridHash and config.
- `loom_native_loom_action_forms_set_9982d85f19737eab`: requestBody containing uid, expectedNodeHash and config.
- `loom_native_flow_surfaces_get_5ce19daccb56cc79`: plain root-level uid; normalized tree supports placement readback.

The native MCP catalog supplies broad generic mutation annotations even for these GET operations. Read-only classification here is established by the reviewed installed handler contract and actual GET schemas, not by those annotations.

Companion get on the coordinator-provided Portfolio grid `e3pqxowwqlx` returned type BlockGridModel and nodeHash `c62d814557aebede62eed4e07734e74edb82aa38330163d2d5450aeba3a56b3b`. This is the digest from the same native repository representation checked by create. A normalized Flow tree must not be substituted when computing expectedGridHash. No missing inspect-target capability was found.

Native get for the owned proposed UID `zp_property_create_form_v1` returned exactly status404/MODEL_NOT_FOUND. The helper recognizes only that precise observed error envelope as absence; permission/transport errors never authorize creation.

Four actual describe calls returned domain package version0.1.2 and implementationDigest `825a60605252bc08c008856cab96fd56173504f2344ac522bc97f157834f0873`:

| Action | Request schema SHA256 |
| --- | --- |
| createProperty | 3448f93ab0115aa96b41d6bdea79f433662439e89c9854a41cf51eeb240cef7f |
| createDraftTenancy | 43e782641379aad6ab4bfd99bfced9a4c341529754ab970ae848e60a4306c83e |
| activateTenancy | 704635d228d4da722eeb3866b11c5ee59ace70e47114d27279cc6fd0c7e93a6e |
| endTenancy | a6590ae16d53fa1c064023bc936e0621d3efb9ab813fc836ab32e687a339080c |

These are historical qualification observations, not usable generation pins for the terminal-recovery forms. The desired contract requires domain0.1.3, companion0.1.3 and idempotent-terminal-v1. Fresh describe, enabled/compatible package readback and exact reviewed grid bindings must pass before each form is generated. Final placement is unassigned; the observed Portfolio grid is not implicitly the property-create placement.

The source helper operates one form at a time, exclusively through discovered Loom tools. A durable private intent is fsynced before mutation, retained on all unknown outcomes, and never automatically replayed. Readback checks exact config and native grid attachment. Existing intent requires read-only verification and independent reconciliation; this helper does not erase a fence. It supports native CAS for initial creation and cosmetic configuration updates only; action binding changes require a separately reviewed migration.

Pending: independent desired-form/source review, final page/detail-grid handoff, new-version qualification, native installation/rendering, role allow/deny, persistence and terminal-rejection correction in the browser. No app acceptance is established by this receipt.

## Context and currency follow-up

Read-only native context on existing maintenance popup grid `xavei31sxda` returned `vars:{}` for path `record`, and `popup.record` as an object for that explicit path. Native get yielded the actual chain: BlockGridModel → ChildPageTabModel → ChildPageModel → ViewActionModel → TableActionsColumnModel → TableBlockModel. The view popup and owning table both identified main-source `zp_maintenance_requests`; popup filterByTk was `{{ctx.record.id}}`. This existing journey proves the native shape only; new unit/tenancy grids must independently match their respective collection.

The app constructor now requires the same bounded ancestor proof and native popup.record capability at qualification and refreshes that proof before dispatch. The reusable companion0.1.3 also validates the ancestor chain server-side, locks involved rows during constructor/submit transactions, and pins the explicit record path in its immutable configuration tuple. Wrong collection, unknown ancestry, cycles and association-specific context fail closed.

The initial draft-tenancy form is explicitly USD-only: `fixedInputs:/term/currency=USD`, with visible USD labels for terms, rent and deposit. Companion0.1.3 validates the fixed value against the actual action schema, rejects conflicting browser input at prepare and submit, and omits the editable currency control. This does not restrict the general protected domain service to US currency. Other currency-specific forms remain ungenerated.

Eight isolated source tests pass after these corrections. Independent review and native generated-form acceptance remain required.
