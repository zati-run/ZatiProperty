# Terminal command rejection and safe form correction

Status: proposed required recovery capability; not implemented or accepted.

The Loom protected action form preserves request identity after every dispatched
failure. An HTTP4xx alone cannot prove no effect: a command may commit before
scoped readback is denied. Reconciliation of an absent receipt does not prove an
older in-flight request cannot commit. This prevents safe correction after a
fully rejected domain validation unless the server establishes a terminal fence.

## Proposed bounded domain contract

Retain the existing actor/action/requestId key, canonical payload hash and global
native audit-head transaction lock. Persist either committed or rejected terminal
outcomes in protected command receipts. Repeated identical input returns the same
terminal outcome; changed input fails collision without altering the receipt.

For an expected domain rejection, first complete rollback of all business effects.
Then acquire the same database lock in a new transaction and recheck the key. If a
concurrent attempt already committed, return its committed outcome. If none exists,
append an immutable audit event describing the safe rejection code and no business
change, a non-dispatching outbox entry and the terminal rejected command receipt
atomically. Future attempts see the receipt before domain effects. Unexpected
exceptions, transport uncertainty, unauthorized actions before the service handler,
or inability to persist this fence remain unknown and must retain the intent.

This is a candidate design, not permission to suppress failed transactions. A
rejection receipt must have a safe stable code, approved human recovery text and
no raw payload or sensitive values. Permission changes still prevent unauthorized
reconciliation. A constructor cannot manufacture a successful business outcome.

Loom may offer correction with a new requestId only after an authorized read-only
reconciliation returns a terminal rejected outcome matching the exact actor,
action, requestId and payload digest. Preserve the old receipt reference. The
submitted data stays visible and editable only after that terminal proof.

## Required proof before enabling correction

- Native domain rollback leaves no partial business rows.
- Concurrent failing and succeeding attempts with the same key converge to one
  terminal receipt; no business commit can occur after terminal rejection.
- Duplicate same-input rejection emits no extra audit/outbox events.
- Changed-input replay cannot replace the terminal outcome.
- Domain commit followed by denied readback remains committed/unknown, never rejected.
- Lost responses preserve identity across reload; late requests cannot bypass fence.
- Expected native ACL denial before dispatch does not become forged service proof.
- Rendered correction has readable error, retained input and explicit safe recovery.

The independent reviewers must assess the contract and implementation before the
plugin upgrade is generated through Loom. Until then, correction is blocked rather
than silently replayed or labeled accepted.

## Independent design refinements

Review requires payload-digest equality before borrowing any existing outcome;
different payload is always collision. Only an explicit allowlist of expected
domain codes can produce terminal rejection, never arbitrary error.code, database,
audit or serialization failures. Audit records for rejected creation carry no
untrusted entity ID, only static safe action/code/digest and authenticated actor.
Reconciliation must return server payloadDigest and terminal outcome. Existing
0.1.1 committed receipts need explicit read compatibility or a separately reviewed
migration; immutable history must not be rewritten through generic operations.
Fence or audit insertion failure leaves the request unknown, with intent retained.
