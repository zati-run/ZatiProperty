# First maintenance journey

Native Maintenance requests queue: request title, property, unit, tenancy, priority, status. Open a record to inspect context; linked work orders lead to a focused Assign vendor action. Work orders use native view/edit drawers with readable labels and vendor selection. Only the vendor/state fields are editable in assignment. Quote means awaiting estimate/approval, not approved spending. Deny destructive actions through ACL and remove irrelevant default buttons.

Empty queue: explain there are no requests; filters can be cleared. Failed save: retain values, show server rejection. Success: saved Quote/vendor state survives reload. Narrow screens prioritize request identity, priority/status and action; record drawers carry secondary context. No fake financial balances or cosmetic acceptance claims.

The linked work table prioritizes State and Vendor before Work order at narrow
widths. Use a focused Save assignment action; remove the default context Edit
action. Observed node refinements are recorded in
`../bindings/linked-work-refinement.json`. Eligibility filtering and contextual
read grants remain acceptance dependencies, not waived requirements.

`maintenance-final-overlay.json` is the canonical ordered final refinement contract.
Initial composition manifests and historical composition receipts are not the final
page state. The initial composer refuses occupied grids or any prior attempt; it
must never be used to regenerate the final experience without this overlay and
new rendered acceptance.
