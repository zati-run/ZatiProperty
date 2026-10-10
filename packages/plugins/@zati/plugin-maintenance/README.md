# Protected maintenance slice

Server invariant plugin for NocoBase **2.2.21**, with a no-op native client entry. Install and enable the packed artifact
through Loom MCP. Collection metadata is generated separately through Loom;
this plugin never creates collections, migrations or financial records.

The first slice supports valid maintenance contexts, active vendors whose
insurance and license expire no earlier than the current UTC date, an explicit
`zp_vendor_properties` row matching vendorId and propertyId, and New to
Quote assignment. Context links are immutable after creation. Work orders require
an existing request and matching property, optional unit and optional tenancy.
A supplied tenancy must belong to the supplied unit; the unit must belong to the
property. Existing unit/property and tenancy/unit links cannot be reassigned.

`approvalRequired` defaults to true and `approvalGranted` to false. Generic writes
cannot change these values. Progress and Complete are blocked pending a protected
owner approval service. Complete to Closed is blocked pending verified payment
proof. New/Quote to Closed represents cancellation; Closed records are immutable.
The canonical lifecycle also permits Quote to New, Progress to Quote and Complete
to Progress; capability guards independently block entry to Progress/Complete.
No ledger, invoice, payment or approval decision action is provided.
Estimated minor amounts accept safe nonnegative integer numbers or canonical
PostgreSQL bigint strings up to Number.MAX_SAFE_INTEGER; there is no numeric
coercion, decimal rounding or support for larger amounts in this slice.

Hooks require a transaction, lock referenced rows, reject stale state updates,
and revalidate after native association writes. Bulk model mutations and deletion
of protected or contextual records are denied. These conservative restrictions
also prevent ordinary archival/hierarchy migration; a dedicated protected service
is needed before those operations can be supported. Setting hooks:false inside
trusted server code or direct database writes remains outside the protected native
application action boundary; do not expose such capabilities to application roles.

## Qualification

`node --test --test-concurrency=1 test/*.test.js` exercises pure rules and a thin
hook fixture. These tests do not establish native persistence or association API
acceptance. Qualification must use Loom-installed plugin activation and Loom MCP
writes/readback against the pinned installation, including raw foreign keys,
association-object writes, denied approval changes, cross-property links,
concurrent updates, rollback, role allow/deny, and reload persistence.

Adapter semantics were inspected in the pinned runtime:

- `@nocobase/database/lib/model-hook.js`: named Sequelize hooks emit through db.
- `@nocobase/database/lib/repository.js`: create/update use transactions; guarded
  per-record writes and afterSaveWithAssociations execute inside that transaction.
- `@nocobase/database/lib/update-associations.js`: association updates follow
  model persistence and may invoke association setters with the same transaction.
- `@nocobase/plugin-workflow/dist/server/Plugin.js`: server plugin extends Plugin.

**Unimplemented:** immutable audit history, approval decisions/thresholds,
vendor-document exception policy,
vendor quote/invoice/proof-of-work artifacts, SLA automation and payment binding.
The property permission mapping is checked and locked in the write transaction;
its actual native enforcement remains unverified until live negative tests pass.
Mapping mutations must remain restricted to authorized construction/admin roles.
Role ACL must separately scope available vendors and records. No claim
of complete RFC 8 or 11 compliance is made.

The dist-only package includes `dist/externalVersion.js` with its inspected
external runtime dependency, `@nocobase/server` 2.2.21. The pinned plugin manager
requires this file for compatibility checks; peerDependencies alone do not qualify
a dist-only archive. Version 0.1.1 corrects the missing metadata in the initial
0.1.0 upload, which remained disabled. Native compatible readback is still required
before activation.

Version 0.1.2 supplies the required `dist/client/index.js` UMD entry. The pinned
frontend loads enabled plugins at that URL even when they only enforce server
rules; absence prevented fresh browser startup. The entry exports a native Plugin
subclass with an empty load method, no custom interface and no registration side
effects. Its external client dependency is pinned to 2.2.21, matching the qualified
native bundle. VM tests exercise AMD, CommonJS and browser-global loader formats;
actual browser reload acceptance remains a separate required check.
