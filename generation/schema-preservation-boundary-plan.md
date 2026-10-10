# Remaining schema preservation gates

## Scoped-constructor fixture

Owner: runtime_discovery; stage: source qualification.
Acceptance: [A synthetic singular role reaches the companion and is rejected
because constructor permission contains nonempty parameters; unrelated roles
and business records remain unchanged.]

Use one unique synthetic role and account through discovered Loom operations.
No global strategy actions, snippets, wildcard, allowAll or portal membership.
Candidate explicit resources: loomSchemaAuthoring inspect/createHasMany/
previewHasMany; flowSurfaces updateSettings; collections.fields create.
At least flowSurfaces must carry a bounded nonempty fields parameter.

Pinned native applyDataPermissions accepts resource names and action keys
name/fields/filter/scope/own; RoleResourceModel installs the named resource into
the effective ACL role. This qualifies a candidate path, not its live behavior.
Read back persisted grants and prove effective native permission shapes before
the denial probe. If roles_check cannot expose them, use a separately reviewed
fixed-action diagnostic rather than infer effective grants from stored rows.
Require CONSTRUCTOR_REQUIRED from the companion; native No permissions is
insufficient evidence of scoped-constructor rejection.

Privately generate account credentials; use an isolated role bridge. Review exact
fixture script and discovered schemas before mutations. Journal once-only writes.
Capture a new whole ACL baseline after fixture creation. Never reuse the old
digest or change existing manager/portal permissions.

## Mutation-window rollback preview

Owner: runtime_discovery; stage: source qualification.
Acceptance: [One reviewed preview rolls back with unchanged complete schema,
ACL and native metadata; requests observed during the actual mutation interval
retain expected allow/deny boundaries.]

Parallel client reads alone do not prove mutation-window overlap. Qualify a native
checkpoint/timestamp contract or implement a bounded preview-only observation
capability at the owned field-created checkpoint. It must evaluate only reviewed
fixed role/resource/action cases, return booleans/digests, preserve constructor
authorization and reject arbitrary callbacks, SQL and introspection. This needs
independent source review before installation or execution.

Supplement with simultaneous native manager/portal reads, clearly separated from
in-window evidence. Persist intent before one preview using the fresh post-fixture
ACL digest. Reconcile field absence, all ACL rows, target FK/associations and owned
cache state. Uncertain outcome or unproven overlap leaves this gate open. Positive
building.units creation awaits both gates and coordinator handoff.

## Reviewed implementation candidates

Loom candidate 06fecec adds a separate fixed five-second observed preview.
Its passive middleware records only qualified requests entering and completing in
the same process interval, with actor/role/argument digests. All schema mutations
hold the lifecycle fence. Source-only tests and isolated installed-native middleware
tests do not establish concurrent application acceptance.

scripts/verify_schema_preview_overlap.py prepares eight role bridges before one
durably journaled preview, then performs six bounded GETs per account (48 total).
It requires actual own-record, foreign-null and portal-denied native responses,
matching actor/role/resource/argument digests and timestamps within the returned
window, and identical before/after schema/ACL state. Existing synthetic building 1
is the read target; the reverse-field preview target remains building.units.
Explicit reserved ports are required; no other native write/upgrade lane may run.
The tool schema and summary must match the reviewed operation before dispatch.

This harness has not run against the application. Do not interpret source readiness
as concurrent or positive schema acceptance. The coordinator must independently
review both candidates, qualify installed package bytes/catalog, finish the scoped
fixture and capture a fresh baseline before executing the one-shot preview.
