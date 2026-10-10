# Maintenance intake independent source review

Exact reviewed source: `bc352ed111da3b7def8fe121577f9c6bef126ea9`. Isolated DGX suite: `node --test packages/plugins/@zati/plugin-maintenance/test/*.test.js`, 31 passed, no skips. No runtime mutation or installation.

One blocking server-boundary finding: `intake-native.js` protects request/work-order creation with beforeCreate only. Native bulkCreate can omit individual hooks; add the same transaction-owned guard to beforeBulkCreate on both collections, with registration and denial/owned-transaction regressions. The command receipt table already includes this guard. Thus source is not yet accepted for installation.

The revised native load wiring registers the command resource and Swagger. Reviewed command flow checks effective role, property/tenancy scope, preserves request linkage and attachment identities, stores immutable request snapshot, and uses actor/action/request digest receipts under serialized actor transactions. These checks do not substitute for missing bulk-hook coverage or native persistence/ACL qualification.

Remaining runtime gates include installed loader/schema discovery, ordinary repository and bulk/nested negative writes, rollback/idempotency, role permissions and rendered request-to-job acceptance. No live acceptance is asserted.

## Corrected candidate

Exact follow-up source `05f1913b1262cdbb6bc82befad2c6b89b16f1ab8` adds both missing bulk-create guards and denial regressions. Independently inspected the focused diff and reran all 31 tests successfully in the reviewer checkout. The finding above is resolved; the corrected candidate is accepted for source integration. Native installation and application acceptance gates listed above remain open.
