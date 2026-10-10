# Final representative maintenance journey

Live synthetic manager journey passed independently of the application-authoring lane at desktop 1365x900 and narrow 390x844. This qualifies the sampled maintenance assignment slice only.

## Environment and source

Observed UTC: 2026-10-10, desktop completed09:51:31 and narrow completed09:54:28; final narrow native readback09:54:42. Task directory suffixes are identifiers, not evidence timestamps.

NocoBase version 2.2.21 on the isolated DGX development instance; Chromium 141.0.7390.37. Effective browser identity was the single-role synthetic zp_property_manager.1 account, never root. Loom's root constructor connection was used only for authorized fixture baseline reset and native readback, not for browser business actions.

Exact source heads, working-file hashes, catalog digest, tool counts, screenshot/report hashes are recorded in manager-final-source-evidence.json. Heads alone do not represent the uncommitted generation/verification changes; the file hashes identify those exact artifacts.

## Completed sequence for each viewport

1. Read work-order1 through Loom and confirmed Quote/vendor1.
2. Reset only that owned synthetic work order through Loom to New job with no assigned vendor; read back the baseline.
3. Fresh native manager sign-in. Opened Leaking kitchen tap and confirmed Demo Property 1, Unit 1 and DEMO-T1 context.
4. Opened Assign vendor. Actual native vendor-list HTTP200 response contained exactly Demo Vendor 1. Expired, foreign-manager and same-manager/other-property fixtures were excluded.
5. Selected Demo Vendor 1 and Quote, then saved using the native Save assignment action.
6. Reloaded, reopened the request, and confirmed Quote and Demo Vendor 1.
7. Performed separate root Loom native readback, confirming state=quote and vendorId=1. Request/property/unit/tenancy references stayed1.

Both final screenshots were visually inspected by the independent runtime lane. At narrow width the contextual fields stack legibly, and Actions, Status/Quote and Vendor/Demo Vendor 1 are visible together in the related-work table. No horizontal scroll is needed to confirm the sampled saved status and vendor.

## Evidence

- manager-final-native-readbacks.json: ordered native before/reset/after evidence.
- screenshots/maintenance-manager-1365.json and maintenance-manager-390.json: context, actual eligibility response, native save and reload assertions.
- screenshots/maintenance-manager-saved-reload-1365.png and maintenance-manager-saved-reload-390.png: final rendered state.
- screenshots/maintenance-manager-picker-1365.png and maintenance-manager-picker-390.png: eligible picker surfaces.
- scripts/maintenance_manager_live.mjs and reset_maintenance_browser_fixture.py: reproducible bounded browser/reset paths with private runtime credentials.

## Interaction and limits

View, Assign vendor and Save assignment native buttons were activated with Enter. Desktop selectors opened with ArrowDown; option selection used pointer. Narrow selectors use their native mobile touch targets. This proves sampled keyboard activation, not complete keyboard-only or accessibility certification.

Two narrow harness attempts targeted an inner desktop control with pointer-events:none rather than its native mobile wrapper. Neither reached Save. Loom readback confirmed New job/no vendor before retry. Correcting the observed touch target resolved the test; no forced click, DOM mutation or application change was used.

All app construction and fixture resets crossed Loom MCP. Native browser writes were authorized synthetic end-user acceptance only. No customer data, external communications, production actions or financial postings occurred. Portal, full automation, empty/error/loading coverage, trust accounting and the remainder of the RFC retain their independent qualification gates.

The final integration reviewer should inspect these artifacts before merging. Earlier diagnostic receipts remain historical and are superseded for the resolved representative-journey findings by this receipt.
