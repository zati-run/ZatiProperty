# Maintenance denied and filtered-empty feedback

Observed UTC 2026-10-10. Native synthetic manager account at desktop 1365x900; Chromium141.0.7390.37, NocoBase2.2.21. No valid assignment changes or financial approvals were made.

## Denied transition

A manager attempted Quote to Progress while approval was unavailable. Original feedback displayed only a stable domain error code. After reviewed maintenance plugin0.1.3 was deployed through Loom, the fresh native save returned422 with this visible explanation:

> Owner approval is required before work can progress. Approval is not available yet; keep this job in Quote. No changes were saved.

The form remained open with attempted Progress and Demo Vendor 1 preserved. Separate Loom readback before and after confirmed the stored state remained Quote with vendorId1. The failed form is not evidence that Progress was saved.

The rendered error screenshot was visually inspected. It provides the approval dependency, safe next step and explicit unchanged-state feedback. Native Save failed indicator also appears.

Evidence: screenshots/maintenance-denied-transition-1365.png, screenshots/maintenance-denied-transition.json, manager-final-native-readbacks.json stages helpful-denied-ui-before/after. Script: scripts/maintenance_negative_browser.mjs (ZP_DENY_ONLY=1).

## Filtered empty and recovery

Applied a nonmatching Request contains filter through native end-user controls. Native list returnedHTTP200 with zero records and the table rendered No data. Reopened Filter and used Reset/Submit; Leaking kitchen tap returned. This was a read/filter exercise, with no app-schema or business-record mutations.

The empty screenshot was visually inspected. It confirms native empty presentation and working filter recovery; there is currently no richer inline clear-filter guidance in that empty table.

Evidence: screenshots/maintenance-filtered-empty-1365.png and screenshots/maintenance-filtered-empty.json. Script: scripts/maintenance_negative_browser.mjs (ZP_FILTER_ONLY=1).

## Limits

These are desktop sampled error/empty-state checks. Narrow error messages, complete keyboard-only/mobile accessibility, other failure paths and portal financial approval operations remain unqualified. Existing source-only and historical checkpoints are not upgraded by this receipt.
