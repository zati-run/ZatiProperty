# Domain draft proposal independent review

Reviewed candidate `e369d37` including `ccb11b5133ce6655cc67c9b6a23fbf0cc3febfac`, account correction `dd885bc`, and adapter correction `4bb58cd65e0c269201d79b821795d9cb0dbb5dd7`.

Independent isolated DGX review ran the domain package's npm test: 62 passed, zero failed. Source review approved with native acceptance outstanding.

The initial candidate omitted current tenant account mapping revalidation when returning party user IDs. The correction invokes the same actor-scoped account and user checks used by domain commands, normalizes safe canonical IDs, and adds revoked, absent, foreign, duplicate mapping and unsafe-ID regressions asserting no writes. A separate correction restores the typed missing-row denial import.

The proposal requires read/amend action authority and manager property scope, selects only the current draft revision, returns an explicit field whitelist and version/revision, and computes a canonical digest. Its transaction performs reads/locks only; no command, audit-head, event, or outbox writes are introduced. This source review does not establish native middleware behavior or browser acceptance.

## Separate live readback diagnosis

An already committed synthetic browser createProperty returned COMMITTED_READBACK_UNAVAILABLE. No command was retried. Read-only manager GET of the committed record succeeded with both comma-separated and array field projection. The installed callback injection library encoded the comma projection correctly in an isolated callback probe.

The domain controller assigns an explicit data envelope, and pinned NocoBase data-wrapping middleware adds another. The observed native response size matched the two-envelope result. Action-form 0.1.5 removed only one envelope, leaving the result ID unavailable before readback dispatch. No native property GET appeared during the failed submit. Reconciliation uses the same response boundary and also needs a narrowly qualified envelope correction. The persisted command remains authoritative; this diagnosis authorizes no command replay.
