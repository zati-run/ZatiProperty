# Bounded sign-in feedback browser evidence

Date: 2026-10-10. Receipt source baseline: ZatiProperty aa8cc2f.
Feature source: Loom preauth-feedback 0.1.1, reviewed393246e.
Runtime: NocoBase Community Edition2.2.21 synthetic development app.

The coordinator captured these browser results; this reviewer independently read
the complete JSON and visually inspected both screenshots. This is a review of
recorded browser evidence, not an independent rerun or runtime package attestation.

Normal synthetic sign-in reached the maintenance request page without a stale
pre-authentication notification. Both before/after notification lists are empty.
The actual server still returned401 for auth:check, aiEmployees:listByUser and
aiConversations:unreadCounts during preauthentication; the companion did not turn
these failures into successes or suppress their rejected requests.

The second run injected one browser-only authenticated401 response for
aiEmployees:listByUser. Its explicit Unauthenticated notification remained visible
and the browser returned to sign-in. This is a synthetic client response fault,
not evidence that the server rejected a valid authenticated account. Additional
requests during that fault are recorded separately in the JSON. The test confirms
authenticated error feedback is not hidden by the preauthentication policy.

Reviewed images:
- [Normal completed sign-in](screenshots/preauth011-normal.png)
- [Synthetic authenticated error visible](screenshots/preauth011-postauth-fault.png)

Acceptance is limited to sign-in notification behavior. It establishes no other
app workflow, permission, persistence, accessibility or production acceptance.
No app metadata, domain records or external communication were changed by this
review. Package installation/source identity remains in the coordinator's separate
Loom generation records.

Evidence SHA256:
- preauth011-normal.json: 8477475c18e510edcca7356420112dbde8652c6dc5cfb8839d1b90eccc6e29f7
- screenshots/preauth011-normal.png: 55f29319dd6028c91ca3b4a7637fe36b9ac3f9e994b263002f9757a44be6ed79
- preauth011-postauth-fault.json: 43e84afca592a7b54ce5a6dee318825fd805e9e92c0fb3b3de39106a81bed689
- screenshots/preauth011-postauth-fault.png: 2ae2394669e1f757ab34a961d8893a28d0152c4cf053590d485fd3f51f622846
