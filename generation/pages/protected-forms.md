# Protected property and tenancy forms

The desired templates in `property-protected-forms.json` are transient native action forms. They bind protected domain actions and never grant generic create/update access to protected collections.

Manager placements await explicit native grid handoff:

| Placement key | Form | Native context |
| --- | --- | --- |
| manager-property-create-grid | Add a property | Focused manager page; name and visible reason |
| manager-unit-detail-grid | Draft a tenancy | Unit detail record supplies unitId |
| manager-tenancy-detail-grid | Activate / end tenancy | Tenancy detail supplies identity and current version |

Show unit/property context above the draft form and tenancy dates/state above lifecycle actions. Dates, parties, reason and end-date confirmation remain visible. Rent and deposit display decimal money but submit bounded integer minor units; this initial form is explicitly USD-only, with server-validated fixed currency and visible USD labels. Other currency forms remain planned. Portal identities use scoped permitted-account display names, never an unrestricted users picker. No boolean approval is silently preselected.

Use `scripts/apply_protected_forms.py qualify --key <key> --bindings <private JSON> --qualification <new private file>` after the required versions are installed. For contextual forms, qualification reads the actual grid-to-popup-to-table ancestor chain and native popup.record capability; the popup and owning table must both match the expected collection. This proof is refreshed before dispatch. Bindings map the placement keys above to objects containing an observed gridUid. Qualification is read-only and refuses stale versions or missing terminal command contracts. Review the resulting config and native placement, then use `apply` with the same arguments and a new private `--journal` path. The independent review receipt referenced by the template must exist before CLI apply.

Each application call handles one form. Requalify the grid before the next form, especially when activate/end share a grid. `verify` performs read-only config and placement readback. A present journal fences further dispatch, including a previous successful run; do not delete it or retry blindly. Unknown outcomes require independent reconciliation of observed native state and original intent.

Required rendered acceptance includes narrow widths, labeled nested fields, readable money/date controls, allowed account choices, denied foreign accounts, explicit state changes, persistent native readback and terminal-error correction using a new request only after the original identity is durably rejected. These templates are not rendered acceptance.

One-level associated popup forms require companion 0.1.4. The helper now pins
both actual native popup ancestor chains, the native hasMany relation metadata,
and its generated foreign-key metadata before construction. It compares the
fresh proof again before each write. The server independently verifies scoped
parent-child membership using the selected native popup source identity. Nested
associated-table forms remain blocked; they require additional context custody
qualification. No page bindings or native form acceptance are implied by these
source changes.
