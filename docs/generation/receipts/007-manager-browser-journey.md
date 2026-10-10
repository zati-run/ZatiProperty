# Synthetic manager browser journey

Reviewer/operator: runtime_discovery. Browser: Chromium 141.0.7390.37 on DGX. Native app: NocoBase 2.2.21. Account: isolated synthetic zp_property_manager.1, signed in with its private generated credentials (never root). Domain plugin client packaging repair 0.1.2 restored app bootstrap after the former client asset 404.

## Verified behavior

- Manager sees one own request, Leaking kitchen tap, Open, Medium.
- Native View button opens request details with description and related Work to arrange table.
- Coordinator reset graph1 to New job and no vendor through Loom before this run.
- Native Assign vendor editor offered Demo Vendor 1 and Expired synthetic vendor; foreign Demo Vendor 2 was absent.
- Selected Demo Vendor 1 and Quote, then activated Submit with Enter. Save completed.
- Reload displayed Quote and Demo Vendor 1. First final assertion encountered duplicate matching text because NocoBase restored nested drawer navigation; no write was retried.
- New independent manager browser sessions at 1365x900 and 390x844 read Quote and Demo Vendor 1 from the related table. Coordinator separately confirmed state=quote and vendorId=1 through Loom readback.
- Native View button activated with Enter at both widths. Native state selector opened with ArrowDown. An earlier attempt focused its inner non-focusable span and failed; this was corrected to the native button locator and is not a product keyboard defect.

## Evidence

Harness: scripts/maintenance_manager_live.mjs. Fresh-session reports: screenshots/maintenance-manager-1365.json and maintenance-manager-390.json. Images: maintenance-manager-queue-{1365,390}.png, maintenance-manager-context-{1365,390}.png, maintenance-manager-saved-reload-{1365,390}.png. Before-save desktop image: maintenance-manager-before-save-1365.png.

Harness requires private runtime/module environment variables. ZP_RUN_JOURNEY=1 enables end-user save; default mode performs observation only. ZP_VERIFY_SAVED=1 checks existing saved outcome without writing.

## Unresolved acceptance findings

1. Property, unit and tenancy context (Demo Property 1, Unit 1, DEMO-T1) is absent for manager in both viewport reports. This blocks the representative journey requirement to establish context before assignment.
2. Expired synthetic vendor remains selectable in the chooser. Server-side rejection is separately qualified; chooser filtering and useful error feedback remain unaccepted.
3. Narrow screenshot visually inspected: readable request card and Work to arrange table, but only Actions and Work order columns fit. Quote and Vendor exist in rendered DOM yet are outside the immediate horizontal view. Do not equate the selector match with a visually clear saved result.
4. Portal acceptance and backend relation/field permissions are separately blocked by ZP-ACL-001; this browser run does not qualify them.
5. Full keyboard-only journey, loading/error/empty states, and independent final visual review remain pending.

This is a partial live maintenance workflow receipt, not full app or representative journey acceptance.

## Follow-up native layout verification

After coordinator applied Loom column ordering/width changes, a fresh manager session at 390x844 independently verified the updated screenshot. Actions/Assign vendor, state/Quote and Vendor/Demo Vendor 1 are now visible together without horizontal scrolling. Finding 3 above is resolved for the sampled synthetic values. The latest maintenance-manager-saved-reload-390.png and maintenance-manager-390.json supersede the earlier layout image/report at those paths. Missing property/unit/tenancy context remains. Harness now uses the renamed Save assignment button; no second save was performed for this read-only layout check.
