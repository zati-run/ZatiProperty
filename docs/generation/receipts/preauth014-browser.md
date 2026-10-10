# Pre-authentication feedback and session custody — native browser acceptance

Actual UTC verification is recorded in the accompanying JSON. Synthetic NocoBase Community Edition 2.2.21; companion 0.1.4 source 98a9546; independently reviewed in c8783fb. Coordinator installed through Loom and verified all five deployed package files against archive SHA256 c670c120cf801edc1557ca03e1dc8f41c938118d6dac6cc9821fc6f9caa1d692.

Two fresh-browser passes navigated from the root route and signed in immediately as a synthetic property manager. A real anonymous AI employee-list POST response (401) was held until after successful sign-in, then released. The new session remained present and the rendered native maintenance page showed no stale authentication notification. Full browser reload retained the session and no unexpected notification. No page errors occurred.

A separate browser-only synthetic authenticated 401/EMPTY_TOKEN response then produced the normal unauthenticated notification and cleared the session. This verifies that the compatibility wrapper does not suppress genuine authenticated failure handling. Only normal sign-in and read requests occurred; no domain command, schema authoring, fixture or permission mutation was issued.

Evidence: [sanitized result](preauth014-browser.json), [visually inspected native page](screenshots/preauth014-fast-root-clean.png). The screenshot was captured after the delayed anonymous response and before the authenticated fault. It demonstrates rendered feedback, not broader application acceptance.

The earlier 0.1.2 and 0.1.3 failed browser proofs remain preserved privately. Version 0.1.3 missed the native AI request-config clone; 0.1.4 binds custody to a private owned function identity with exact dispatch metadata and final credential absence. This acceptance is bounded to the pinned native client, the qualified anonymous root/sign-in requests, and the tested selected-role flow. It does not assert production deployment, all browsers, or general authentication changes.
