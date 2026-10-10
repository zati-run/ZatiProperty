# Protected property and tenancy actions — source candidate

This package is a proposed NocoBase CE 2.2.21 domain service for the first property/
tenancy increment. It is **not installed or accepted**. Collection metadata is
owned by the generation contract and must be created through Loom. The package
does not create collections, post money, send messages, or operate a dispatcher.

## Construction and authority

The fixed resource is `zpPropertyTenancy`, with thirteen actions:
createDraftTenancy, updateDraftTenancy, activateTenancy, endTenancy,
createOwnershipSet, setOwnershipInterests, approveOwnershipSet, auditHealth,
createProperty, createBuilding, createUnit, createOwnerContact, authorizeTenantAccount.
Every action requires a native action grant, one effective role, an authenticated
actor, and that actor's assignment on the property's managerUserId. New property
creation binds managerUserId to the actor. authorizeTenantAccount is the explicit
exception: it requires the selected native role's stored allowAll=true flag and
checks the stated property's assigned manager before creating an immutable
manager/account permission with canonical unique mappingKey. Application roles
must not receive this constructor action. Root is not
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
Generic context creation is also denied: property/building/unit/owner-contact
creation uses narrow scoped actions with hierarchy checks. Ordinary context editing
is not yet offered by this increment. Every linked tenant party account requires
a constructor-owned zp_tenant_account_permissions row for its manager; mere users
collection membership is insufficient. New drafts leave tenantUserId null; only
activation publishes the primary binding atomically. Legacy adoption preserves
its existing binding. Secondary party account access and changed owner account
membership fail closed until new portal scopes are separately qualified.

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
required. New primary user references must resolve and have an explicit manager/account
permission; there is no invitation flow.
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
sequence, actor/action/entity/property IDs, safe previous/resulting snapshots,
server UTC timestamp, generated correlation ID, a fixed operational reasonCode
and its human-readable description, plus a supplementary request hash. Snapshots
retain tenancy dates/unit/primary binding/draftRevision or ownership dates and
interestsRevision, preserving recoverable links to immutable detailed revisions.
Raw names/contact values and free-text reasons are not accepted into the audit.
Restricted audit role grants and rendered audit explanations still need native
qualification.

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

## Command recovery contract (0.1.1)

Every mutating action requires a lowercase UUIDv4 requestId. The immutable receipt key binds actor, action and requestId; canonical input excluding requestId is hashed. Under the existing global audit-head transaction lock, identical repeats return the committed result; differing payload reuse fails with REQUEST_ID_COLLISION. Business rows, audit event, outbox entry and command receipt commit together. Initial audit-head initialization races may produce a conflict; read the command outcome before considering an explicit retry with the identical identifier and payload.

GET zpPropertyTenancy:reconcileCommand accepts commandAction and requestId. It requires both current reconciliation and original-action ACL, returns only the caller's receipt, and never initializes audit state. not_observed is not proof that an earlier in-flight command cannot still commit and does not authorize automatic replay. Preserve identifier and payload during uncertain outcomes. auditHealth also performs no initialization.

Manager and constructor ACL snippets are separate. Generic CRUD on command receipts stays denied even for constructor users; account authorization additionally requires the native allowAll constructor flag. Permitted account choices read scoped mapping userId/displayName only. Labels derive from the linked user's nickname or a bounded explicit constructor-approved fallback. Identity bindings remain immutable.

The reviewed additive migration uses generation/collections/property-tenancy-commands.json and apply_property_tenancy.py --commands. It keeps the original manifest and runtime ownership digest unchanged, verifies the pinned parent metadata/IDs, and uses separate command-schema intent/bindings. Never rewrite the original binding digest to bypass the migration chain. Source tests are not native transaction, formatter, browser or live acceptance; those remain required before enablement.
