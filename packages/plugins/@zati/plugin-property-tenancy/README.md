# Protected property and tenancy actions — source candidate

This package is a proposed NocoBase CE 2.2.21 domain service for the first property/
tenancy increment. It is **not installed or accepted**. Collection metadata is
owned by the generation contract and must be created through Loom. The package
does not create collections, post money, send messages, or operate a dispatcher.

## Construction and authority

The fixed resource is `zpPropertyTenancy`, with eight actions:
createDraftTenancy, updateDraftTenancy, activateTenancy, endTenancy,
createOwnershipSet, setOwnershipInterests, approveOwnershipSet, auditHealth.
Every action requires a native action grant, one effective role, an authenticated
actor, and that actor's assignment on the property's managerUserId. Root is not
an implicit business manager. Owner contacts linked to interests must belong to
the same manager. No user identity, ownership approval flag or audit payload is
accepted from a generic collection mutation.

The native MCP source in the pinned package
`@nocobase/plugin-mcp-server/dist/server/mcp-tools.js` scans enabled package
Swagger files at lib/dist/src swagger.json or swagger/index.json. This package
supplies `dist/swagger/index.json`. Its package must be explicitly included in
the configured native MCP package patterns and its actual tools/schemas refreshed
and qualified after Loom installation. Source discovery is not live capability
qualification. Do not call an invented MCP alias or use direct REST as a fallback.

## Domain boundaries

Tenancy `status` retains open/closed/closed_allow_transactions. Additive nullable
leaseState tracks draft/active/ended. Existing null state is not inferred to mean
active or vacant: explicit adoption requires a complete dated draft, null expected
version, adoptLegacy true, and the existing primary user identity. Activation
fails closed if another tenancy on the unit has an unqualified legacy state.

Occupancy intervals are half-open [startDate,endDate), with null end unbounded.
Active and ended historical occupancy both participate in overlap checks.
Per-room leasing is unsupported and denied where flagged. End can shorten, never
extend, the contracted end; it does not change transaction acceptance status or
perform deposit settlement. There is no active-term amendment or renewal action.

Terms/parties are append-only proposal revisions linked by tenancy.draftRevision.
Generic writes, nested saves, bulk writes and deletes of protected collections
are denied unless their exact transaction is privately owned by this service.
Approved ownership sets cannot change. Draft complete interest sets append
revisions and must sum to exactly 10000 basis points; approval requires explicit
completeSet confirmation and expectedVersion. Overlapping approved periods are
denied. Replacing an open-ended approved set needs a future audited supersession
action; it is not silently enabled here.

Money is nonnegative integer minor units bounded to 2147483647 for this increment.
IDs accept canonical positive integer numbers/strings up to MAX_SAFE_INTEGER.
One draft has at most 20 parties/interests; occupancy/history scans max1000.
Unique code, audit sequence, head ID, and outbox eventId metadata constraints are
required. New primary user references must resolve; there is no invitation flow.
Portal current-revision row/field grants still need separate implementation and
tests; preservation of history does not authorize its disclosure.

## Transactions and audit

All mutations lock a single protected audit-head row before domain records.
This deliberately serializes bounded development work, including concurrent
activation and approval, at the cost of throughput. Initial head creation races
may produce a rolled-back conflict; callers reconcile state instead of blindly
retrying. No process mutex substitutes for the native database row lock.

Mutation, immutable change event, pending outbox row and head update use one
transaction. Canonical JSON sorts object keys recursively and preserves arrays;
eventHash is SHA256(previousHash + newline + canonicalPayload). Payload includes
sequence, actor/action/entity/property IDs, version/state, server UTC timestamp,
generated correlation ID, and hashes of the supplied reason/request. Raw party,
contact and monetary terms are excluded. The supplied free-text reason is hashed,
not retained as a human-readable audit explanation; a future reason-code and
private narrative policy is still required for broader operational audit UX.

auditHealth independently recomputes the complete chain and head up to10000
events. This is source-level verification behavior, not a production tamper-
evidence claim: external anchoring, privileged-database threats, retention,
recovery, throughput and independent security/domain review remain open.
The outbox has no sender/dispatcher and its payload/identity cannot be edited.

## Verification gates

Run on qualified Linux resources:

`node --test --test-concurrency=1 test/*.test.js`

The in-memory transactional tests prove service branching, serialization requests,
rollback logic and hash verification only. Adapter mocks prove installed hooks
and fixed handler registration contracts, not actual ORM hooks or native ACL.
Before acceptance, qualify through Loom: installation/compatibility, discovered
action schemas and role grants, actual transaction locks/rollback, simultaneous
native activations, bulk/nested bypass negatives, complete ownership approval,
audit/outbox readback and tamper rejection, persistence/reload, co-tenant privacy,
and rendered manager/tenant journeys. Keep maintenance context and its historical
IDs unchanged. No runtime changes were made by this source package work.
