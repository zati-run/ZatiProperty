# Independent protected command review

Exact source `e4b83e1a4db3bbd8d8e468223cc52756041c8aa9`, isolated detached DGX reviewer checkout,2026-10-10 UTC. Decision: source approved for controlled Loom migration/plugin qualification. No blocking finding in the reviewed delta. No app mutation, installation or command execution performed by reviewer.

## Findings

- Mutations require UUIDv4 request identity. Command key binds normalized actor, action and request ID; request hash binds canonical business input. Same key/same payload returns the committed result; changed payload fails collision. Command receipt, domain rows, audit, outbox and head update share one transaction. Audit-head lock serializes mutations; unique receipt key adds database enforcement. Unknown outcome requires reconcile, not a new identity/retry loop.
- Reconciliation is truly read-only in this implementation: lookupCommand performs a bounded SELECT outside the mutation transaction, never creates an audit head, command receipt or audit event. No receipt returns not_observed with retryAuthorized false; this correctly avoids equating absence during a concurrent/uncommitted request with proven failure. Actor and original action are bound into lookup key. Adapter requires both reconcile permission and original command permission; no cross-actor query input is accepted.
- Existing single effective-role and native action ACL gates remain. Constructor-only account authorization still requires native allowAll plus action permission before service mutation. Manager and constructor snippets are separated. Account choice displayName is copied by the protected constructor action from native nickname or bounded supplied label, rather than granting users access.
- auditHealth no longer creates a head for an empty system. It may open/lock a read transaction; this is not a data mutation. Existing audit-head initialization race still may roll back an attempted first mutation; reconcile/no automatic retry is the correct boundary until native concurrency acceptance.
- Command migration uses its own journal/binding namespace, rejects unresolved parent intent and parent digest mismatch, checks parent collection ownership plus authored metadata and extension field identity before adding command receipt collection/displayName. It preserves the parent specification/bindings. A non-null displayName addition to any populated legacy mapping table must be qualified natively; if native migration rejects existing rows, stop for a separately reviewed bounded migration, do not overwrite or invent names.
- Error responses retain bounded codes and human guidance, avoiding SQL/payload/credential echo. Unclassified failures explicitly say outcome could not be confirmed, fitting request reconciliation rather than promising no save. Stored receipt JSON parse failure fails closed. Protected hooks include the new command collection, preventing generic mutation of receipts.

## Verification

`node --test --test-concurrency=1 packages/plugins/@zati/plugin-property-tenancy/test/*.test.js`:39 passed,0 failed.

`python3 -m unittest discover -s tests -p test_property_tenancy_migration.py`:12 passed.

These are source/in-memory adapter and migration mocks. They establish tested branches, not native DB isolation or deployment acceptance. Required next gates: Loom-only owned additive migration with native metadata readback; actual protected hook direct/nested/bulk denial; concurrent identical command requests yielding one audit/outbox/receipt; collision unchanged state; cross-role/action/actor reconciliation denial; timeout/commit readback recovery; fresh empty auditHealth leaving no rows; role-specific rendered action form; persistence across reload. Generic CRUD permissions must remain denied. Financial posting remains absent/out of scope.
