# Native protected command qualification

Preparation owned by runtime_discovery; no business writes until coordinator explicitly hands over the single write lane. Exact initial source base bd549b1. Run on DGX only. Current source script defaults to live schema discovery, not execution.

## Prerequisites

- Reviewed command migration and plugin0.1.1 installed through Loom, native catalog recaptured; all12 mutation tools require requestId, reconcileCommand exposes GET commandAction/requestId. Script fails before dispatch on stale schema.
- Manager1/2 receive reviewed custom-action snippet, without generic create/update/destroy. Owner/tenant/vendor remain denied. Existing eight private synthetic test accounts retained.
- Stop other domain writes during global audit-count assertions. Reserve two owned loopback role bridges18462/18463 (check free); main bridge stays coordinator-owned. Existing helper starts at most two Node bridges, then terminates its own processes in finally. Each bridge has maxConcurrent1; two bridges give real independent requests for the same actor.
- Set private ZP_RUNTIME_DIR and ZP_LOOM_DIR plus a fresh run ID/receipt. No credentials in command arguments or sanitized receipts. Same run directory cannot be replayed.

## Executable coverage

The script performs a pre-mutation auditHealth read and checks no audit/head/command/outbox state changed, retaining initial counts. A truly empty initial store proves the formerly unsafe empty-head case; a populated store only qualifies read-only behavior on that state.

Manager creates a synthetic property/building/unit/contact, then replays the identical property request and rejects same-key/different-input collision. Root authorizes the existing synthetic tenant only when no mapping exists; pre-existing matching mapping is retained, never overwritten. Manager constructor action and foreign tenant association are denied. Two draft tenancies target one new unit. Unknown reconciliation is read-only/not_observed/retryAuthorized=false.

Two independent manager bridges issue identical-key commands concurrently (one receipt/result), then two same-version draft updates (one success/one stale) and overlapping activations (one success/one overlap denial). Successful active tenancy ends through its protected action, followed by root native state readback. Final auditHealth validates the chain without writes. Each mutation checks one new event/outbox/receipt with matching event IDs and head sequence; replay/denial checks unchanged state. Portal roles cannot create; manager2 cannot mutate manager1 property and cannot reconcile manager1 request identity.

Every command has a durable fsynced private intent and unique UUID before dispatch. Expected denial must match its domain code and leave protected state unchanged. Network or unclassified failure stops; best-effort GET reconciliation is recorded, never followed by mutation retry. Concurrent failure leaves both durable request IDs for explicit native reconciliation. Sanitized receipts carry synthetic IDs/status/code only. This suite does not create tenant accounts, edit roles or plugins, send messages, post financial entries or start payments.

## Remaining independent gates

Native direct/nested/bulk generic-CRUD denials for every protected table, readonly reconciliation permission negatives for each original action, ownership approval full lifecycle and schema restore/migration tests remain separate coverage unless added explicitly. This script does not fake browser or accessibility acceptance. Property UI/ActionForm worker must independently verify rendered role-specific journey, saved reload, useful errors and uncertain-command recovery. No mocks are reported as native execution.

## Review hardening

All expected versions now come from returned native draft/update/active results, including version0; no lifecycle version is inferred. Audit reads paginate in pages of50 with stable ID order, duplicate detection and a1000row safety cap. Denial acceptance parses the structured native HTTP status and exact domain code; permission denies may also use the native Forbidden/ACL_DENIED form. Transport text containing a code is never a passed denial. Every dispatch validates arguments against the actual live discovered JSON schema. Local safety tests exercise version0, missing version rejection, pagination and structured error boundaries, and run the actual domain validator against the proposed proration/rent-frequency fixture. Generic/bulk hook coverage remains separate.

Explicit continuation after the constructor authority fix uses --resume-authorize with the original run ID and a new receipt path. It reopens existing journals, requires all four context results, verifies audit state against the interrupted intent, GET-reconciles the original account request as not_observed, and reads every context ownership binding. Only coordinator approval after reviewed plugin0.1.2 permits this step; the command uses the original request ID and preserves all earlier intents/results. It does not replay createProperty/building/unit/contact or prior tests. Any changed audit/outcome/binding stops for review. Unexpected exact responses are now captured only in private runtime files.
