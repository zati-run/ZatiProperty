# Property/tenancy initial native qualification

Status: generated foundation; acceptance pending. Target: `zp-dev`, synthetic development only.
Observed 2026-10-10 UTC. Application source `6f49583b7ccef7933e4819256cffab60112a744d`;
reviewed plugin source `4947b7a840da94fa6344f79a5751f9ba89422275`.
Loom source `ec4b6408d4376e5a3cf881dd2ffb28342140e1e7`; NocoBase CE2.2.21.

## Generated and read back

Through Loom native MCP under the qualified construction role, the owned schema
batch applied23operations: eleven collections and twelve additive fields.
The immutable specification digest is
`e767b528bfc0269688d91d22785a96e9436f28484376b8ad1af21c310267c0a7`.
Returned identifiers and ownership are in
[generation bindings](../../../generation/bindings/property-tenancy-schema.json).
The original schema intent and bindings remain distinct from later additive migrations.

The installed `@zati/plugin-property-tenancy`0.1.0 archive SHA256 is
`3bcffb7ea1acdaa069da959707b3ecbbc0e12c6e85f449982f365619db867e9f`.
Loom plugin readback reports installed, enabled and compatible. Seven installed
files byte-match the reviewed source; see
[installed file evidence](property-tenancy-010-installed-files.json).
The refreshed native catalog exposes13domain actions: twelve mutations and
`auditHealth`. Catalog has238native operations plus25supplemental operations;
SHA256 `d300687de13a3370130cda5e4404ab935e1f0ad3889af6439c5dc900adc33939`.

## Bounded native verification

A construction-role generic create against the audit event collection was denied
with `DOMAIN_ACTION_REQUIRED`; before/after bounded lists were empty.
[Native guard evidence](property-domain-first-native-guard.json).
An initial unbounded list was rejected by the association guard before any write;
the verified read used explicit bounded pagination. No uncertain mutation was replayed.

The native action-form probe showed a CreateForm with generic create permission
denied hides both input and custom action. The temporary probe route was removed
through Loom and its exact previous role route set restored. See
[probe and cleanup](protected-action-ui-qualification.md).
This confirms a reusable Loom authoring gap, not permission to grant generic CRUD.

## Remaining gates

Plugin0.1.1 command receipts/reconciliation and a separate additive schema migration
are source candidates awaiting independent review and native qualification.
Loom action-form work is in progress. Manager read overlays and navigation remain
unapplied candidates. No new property/tenancy business fixtures or role grants are
claimed here. Live concurrency, rollback, audit chain, account membership, scoped
portals, command replay, native persistence and rendered journeys remain unverified.
The source tests and installed files do not establish these acceptance gates.

There is no ledger implementation or financial acceptance. Consequential actions
and external communications remain disabled/outside this session authority.

## Command upgrade observation

The independently reviewed command candidate
`e4b83e1a4db3bbd8d8e468223cc52756041c8aa9` was incorporated on feature source
`bd549b1` and installed through Loom as0.1.1. Archive SHA256
`681eefc018765298d96c83e04121ca9d6b092822d435979c420e4af267aba294`.
Native plugin readback reports version0.1.1, installed and enabled; compatibility
was not present in that response and is not inferred. All eight installed package
files match the reviewed candidate, see
[property-tenancy-011-installed-files.json](property-tenancy-011-installed-files.json).

The separately bound additive command schema applied two operations. Its digest is
`8b6adc702a2bedbeb2773a678162510e8649e8943330cb8ed87c1ec393442b06`;
[parent-linked bindings](../../../generation/bindings/property-tenancy-command-schema.json).
The current catalog has239native plus25supplemental tools, including14domain tools;
all twelve mutations require requestId. Catalog SHA256
`f71713d09cfdb596df83ab2980fcd50c465c72065851ac287c0dcd7ba79e4850`.

A constructor-role GET reconciliation of a fresh unknown command returned
not_observed with retryAuthorized=false. Before/after audit head, events, outbox
and command receipt collections remained empty;
[empty reconciliation evidence](property-command-empty-reconcile.json).
This verifies only the bounded read-only path, not mutation idempotency or concurrency.
A bridge restart initially failed for missing prefixed TLS environment variable
names; the owned process was restarted with the required keys and actual MCP
discovery/readback then succeeded. No application write was replayed.
