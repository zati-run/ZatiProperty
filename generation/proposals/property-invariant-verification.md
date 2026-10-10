# Native invariant qualification plan

Target: installed property-tenancy 0.1.2, NocoBase CE 2.2.21. This script is prepared only; execution requires coordinator-exclusive mutation handoff. New terminal rejection semantics in 0.1.3 invalidate the unchanged-audit expectations and require separate review.

Use existing synthetic manager1 property4, unit3, contact1, draft tenancy4 and ended tenancy5. Verify bindings before writing; manager2 property2 is the known foreign scope. Create two ownership sets for 2040 within property4; no account or role changes.

Exactly 27 native mutation attempts: five successful domain commands, six expected domain denials, sixteen expected generic denials (eight each constructor/root and manager). Successes: create set A, set complete interests, approve A, create overlapping set B, set its interests. Denials: incomplete sum, second missing owner after first nested insertion, stale version, approved-set immutable, overlapping approval, foreign property. Generic probes: single update, filtered multi-record update, nested association update, association create, and each of four protected audit/outbox/command/head updates. Root denials must be domain hooks; manager denials must be native ACL. No grant is broadened to force a probe.

Each command has a private fsynced intent, audit/readback and reconciliation. Generic probes compare complete bounded snapshots of tenancy/party/term/ownership/interest records and audit state. Unexpected success or response stops without retry. Any failure requires explicit checkpoint reconciliation; no automatic batch resume exists.

Partial nested rollback is demonstrated by a valid first owner insert followed by a nonexistent second owner returning OWNER_SCOPE, with all rows/revisions/audit unchanged. This is a real database transaction rolling back a domain rejection. It is NOT an injected database constraint failure; that stronger requested gate remains unqualified because no safe qualified public input currently reaches a constraint after nested insertion. Do not add fault injection, raw SQL or broaden permissions to fabricate this test.

Independent review must inspect actual status/code contracts and source mutation count before execution. Browser and terminal rejected-command receipts are separate gates.

The first controlled run stopped at a locally invalid completeSet=false input. Native MCP schema permits only true; this is recorded as local schema rejection, not a native domain rejection. Reviewed explicit --resume-incomplete verifies audit head13 unchanged, no command receipt for that request, ownership set1 draft/version1 and its exact sole 10000-basis-point owner1 interest/revision1. It skips the already committed/rejected prefix, preserves the original journal and uses a separate role bridge directory. No prior writes are replayed.
