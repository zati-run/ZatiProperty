# Effective constructor authority fix candidate

2026-10-10 UTC. Source base9bdd19409ce8427c1db68479798f89bc35d3fae2. No live plugin change or mutation replay by this lane. Package candidate0.1.2.

Native command qualification stopped on constructor account authorization after four synthetic context mutations, each with matched event/outbox/command receipt. The authorization request was reconciled twice: not_observed, retryAuthorized false. The batch was not replayed.

Read-only evidence: persisted roles:get(root) allowAll is null; roles:check reports allowAll true. Installed NocoBase2.2.21 ACL source does not expose a stored/effective role allowAll flag to rely on uniformly: role-check synthesizes its presentation flag from native root membership. Hardcoding that role name in this plugin would be wrong. Native ACL.can applies effective rules, including unrestricted constructor authority.

The fix reuses the already qualified Loom RecordSelect companion semantics: current actor, exactly one effective role, explicit native zpPropertyTenancy:authorizeTenantAccount permission, plus native unrestricted flowSurfaces:updateSettings permission. A permission with nonempty params is restricted and cannot authorize accounts. The plugin no longer reads persisted roles.allowAll and does not compare a role name to root. The existing single-role/action ACL gate runs before this check; the domain service still requires constructor authority.

Pinned installed source hashes:
- @nocobase/acl/lib/acl.js:0f2d23c7539309abf3a15284bac678f6425f320f96c581ab05954682b04cd398
- @nocobase/plugin-acl/dist/server/actions/role-check.js:000b07e62899e189e0d39d6ac4d2d5d384f342d7f6a6b08e70c74ec502e32fe3

44 Node tests pass,0 fail. Added adapter tests: stored metadata absent/null with effective unrestricted capability allows; named root without capability denies; all domain actions without authoring denies; restricted authoring denies; constructor authoring without explicit action ACL denies. Tests remain mocks, not live fix acceptance.

Independent exact-head review precedes Loom package update. Then reconcile the existing request ID and resume only the saved authorization step under coordinator mutation-lane handoff. Preserve all existing contexts and immutable receipts. Never grant manager constructor permission to work around this issue.
