# Synthetic tenancy lifecycle and stale-form rejection

Environment matches receipt022. Generated protected manager forms were used
through the native browser; no operator REST, CLI or database mutation occurred.

- Tenancy6 draft version0 activated once: request f07557ae-80c8-4801-98af-96c4105ad1fb.
  HTTP200 reported verified, active, version1.
- The end form already open on version0 was then submitted by the user.
  Preparation returned HTTP409 RECORD_CONTEXT_CHANGED before business submit.
  This is a stale native context check, not an idempotency replay.
- Fresh browser sign-in/reload read active version1.
- The reloaded end form saved the synthetic exclusive end date2043-01-01 once:
  request df9402dd-039f-4f7a-b8b5-66b4b390957d, HTTP200 verified, ended, version2.
- A separate fresh browser read confirmed ended version2. No page errors were
  observed in these journeys.

Private exclusive intent/response records preserve each request. The first
fresh end-test script failed on a local readback variable before any intent or
submission; the corrected script reloaded state before the sole end command.

Remaining acceptance: independent review, lifecycle-specific role denies and
audit/outbox readback. UI state is safe at the server boundary but needs clearer
stale-context feedback, automatic record refresh, and state-appropriate action
visibility. Both activate and end forms remain visible on ended records; this
is a presentation gap, not permission to weaken server transitions.
