# Property/tenancy independent source review

Current source disposition: final candidate `4947b7a840da94fa6344f79a5751f9ba89422275` is approved for controlled native qualification, as recorded in the final follow-up below. The initial findings are retained as review history; this receipt does not establish live app acceptance.

Reviewed candidate `5859045c2d1efe5befa877d06ea1fae2ca6502d7` against proposal/schema `2ea72a1fafeea73dd51e015d9002260dc38956f4` on DGX, 2026-10-10 UTC. Isolated detached reviewer checkout; no runtime mutations or installation. Decision: changes required before installation.

Paths below are under `packages/plugins/@zati/plugin-property-tenancy/`.

1. **High: context create boundary missing.** `dist/server/index.js:44`–51 adds update and destroy hooks only. Generic creation/bulk creation of units/buildings/owner contacts does not enforce actor scope and consistent property/building references. Later `service.js:124`–127 validates when tenancy operations use a unit, but leaves inconsistent or foreign-linked context records possible. Protect context creation with server-owned actor checks and association consistency, including nested/bulk routes; qualify actual native paths.
2. **High: arbitrary party-account linkage.** `dist/server/service.js:130`–133 only checks that a user exists. `service.js:28` makes the supplied primary user the tenancy portal identity. A manager can supply unrelated, staff/vendor or another manager’s tenant account ID. Require a server-owned permitted tenant-account association boundary for every linked party, with cross-role/cross-manager negatives. User existence is not authority.
3. **High: audit contract incomplete.** `dist/server/service.js:110` keeps only hashes of reason/request and resulting state/version. It cannot explain the human reason or previous state as required by proposal invariant 4. Store a bounded recoverable reason/code and prior/resulting lifecycle summaries within restricted immutable audit, avoiding unnecessary personal data. Hash-only limitation is honestly documented but remains a contract gap.

## Evidence and limits

Command: `node --test --test-concurrency=1 packages/plugins/@zati/plugin-property-tenancy/test/*.test.js`: 20 passed, zero failed. These are in-memory service/adapter mocks, not native persistence, concurrency or bypass acceptance. Reviewer checkout was clean before this receipt.

Read-only inspection of installed NocoBase 2.2.21 database `model-hook.js` confirms recognized Sequelize hooks are forwarded as collection-specific events with original arguments. This supports adapter hook signature plausibility only; native nested/bulk rollback and hook coverage still require Loom-mediated verification after fixes.

Positive source findings: single effective-role and native action ACL check; property manager identity checks; closed action/input allowlists; generated immutable audit chain and pending outbox within the same transaction; protected collection create/update/delete and bulk guards keyed by private transaction WeakSet; row locks and shared audit-head lock serialize service operations. Initial audit-head creation race may roll back and requires reconciliation. No financial posting, payment provider call or outbox sender found.

Still unqualified: actual ACL grant semantics, native lock/overlap concurrency, initial-head race, bulk/nested association bypass negatives, actual transaction rollback, role-restricted audit reads, installation compatibility, persistence and rendered lifecycle journeys. Passing source tests does not establish these gates.

## Independent re-review of fixes

Exact candidate `a9aa8a53a9e8d802e251c93a11181a60fa330922`, additive schema contract `c78a1a1330dbac8154e1a4c745d13f21606932e4`, 2026-10-10 UTC. Decision: previous three source blockers resolved; eligible for controlled Loom installation and native qualification, not app acceptance.

- Context collections now share protected create/update/delete and bulk hooks. Four typed creation actions enforce manager ownership and building/property agreement. Generic context edits are deliberately denied rather than partially guarded.
- Immutable manager/account permission mappings use a canonical unique mapping key; constructor authorization requires native effective role allowAll true plus the action permission. Every supplied party user must have the manager mapping. New drafts keep tenantUserId null until activation. Legacy primary identity remains immutable. Secondary portal membership activation and owner identity changes fail closed pending their scoped migrations; those RFC workflows remain incomplete.
- Audit now retains bounded reasonCode/readable label and previous/resulting snapshots of state, dates, version and identity/revision references. It excludes contact names and raw financial terms while making lifecycle transitions explainable.

Reran the same bounded Node command: 24 tests pass, zero fail. These remain mocks. No runtime mutation was performed. Native initial-head concurrency, collection hooks for nested/bulk writes, rollback, protected ACL permissions, approved-account chooser and read scope, audit read restrictions, persistence and browser action form remain mandatory before acceptance. No additional source blocker was found in this bounded independent review.

Final exact-head follow-up: `4947b7a840da94fa6344f79a5751f9ba89422275` independently reviewed against a9aa8a53 delta. Activation rechecks permitted account/user existence; ownership approval rechecks owner user existence; currency requires a string. Same Node command:25 tests pass. These changes resolve account deletion drift and input coercion without broadening authority. Source approval for controlled native qualification remains; no live acceptance implied.
