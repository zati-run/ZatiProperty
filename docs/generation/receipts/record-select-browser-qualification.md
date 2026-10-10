# Record selector browser qualification

Fresh manager account session after Loom selector companion installation.

Request detail now renders property Demo Property 1, Unit 1 and tenancy DEMO-T1.
The native linked work-order table initially failed because request.workOrders was
not an explicit readable relation. Coordinator added that relation grant through
Loom; the table then rendered Quote and Demo Vendor 1 correctly.

The vendor selector opened with native combobox focus and ArrowDown. Its live
vendor-list request returned 403. The compiled eligibility filter contained
propertyPermissions.propertyId = null: native ctx.record.propertyId was unresolved.
The selector still displayed cached selected Demo Vendor 1. That visible option
is not evidence of successful eligibility filtering. No assignment save was made.

Harness scripts/maintenance_manager_live.mjs now requires a successful live
vendor-list response and exactly the eligible synthetic record name before it can
record a successful picker check, preventing stale selection from masquerading as
filtered results. Source/date/association guard qualification remains in progress.

Current screenshots and manager JSON are diagnostic, not complete acceptance.

## Current-record binding follow-up

After coordinator granted manager read-only work-order propertyId/unitId/tenancyId
through Loom, a fresh native picker request compiled propertyPermissions.propertyId
with value 1 (no longer null). Live list still returned403 due to pending nested
relation-filter guard compatibility. Harness correctly rejected cached selection.
No assignment was submitted during this check.

## Guard 0.1.3 browser qualification passed

After the independently reviewed guard 0.1.3 was installed through Loom, fresh
manager sessions at 1365x900 and 390x844 passed live vendor-list response checks:
HTTP200, parsed records exactly Demo Vendor 1. Expired synthetic vendor, foreign
manager vendor and the same manager's other-property vendor were absent. This
qualification used the actual native list response, not cached selected labels.

Both screenshots were visually inspected: desktop dropdown and narrow native
bottom sheet show Demo Vendor 1 and readable property/unit/tenancy context.
Narrow screenshots wait for the native option to scroll into view before capture,
avoiding a transient bottom-sheet opening frame. The narrow selector was opened
through its native wrapper pointer action; desktop selector used ArrowDown.

Evidence: screenshots/maintenance-manager-picker-1365.png,
screenshots/maintenance-manager-picker-390.png and maintenance-manager-390.json.
The desktop command passed the same HTTP/data assertions before its report format
was extended to include their values explicitly. Native View Enter worked.

No assignment save was made in these read-only qualification runs. A final clean
baseline-to-save-and-reload journey and complete keyboard-only interaction remain
separate gates; portal and financial acceptance are not implied.
