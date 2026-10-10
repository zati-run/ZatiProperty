# Draft tenancy amendment

Scope: T3.0/T3.1/T3.2, draft-only protected command. Desired template:
`tenancy-draft-amendment-form.json`. Required domain 0.1.4 and companion 0.1.9.
No native popup binding is invented: qualification requires the separately reviewed
`manager-tenancy-amendment-grid` binding and exact tenancy popup ancestry. The observed binding is now tracked in generation/bindings/property-protected-form-targets.json and receipt amendment-placement-native-readback.json.

A manager opens their tenancy, reads its status and current revision, then reviews
a complete prefilled proposal. Dates use an exclusive end date. Currency remains
the existing contractual currency; integer minor units are explicitly labeled and
never silently converted to USD. The permitted account chooser exposes no generic
users enumeration. Saving appends a draft revision and preserves prior terms and
parties; activation remains a separate protected decision.

The companion displays the captured proposal revision and record version. Changed
source/version/account authority prevents save; user edits and uncertain intent
remain available for reconciliation. The current domain rejects adopted legacy
drafts, changed account membership, and non-draft records through this form.

Required qualification: native contract read and role allow/deny, complete current
term/party prefill, unchanged defaults, edit/save/reload with new revision and intact
history, stale concurrent save, revoked account, foreign record, unknown-result
recovery, narrow viewport and keyboard/error feedback. The bounded edit/save journey is recorded in receipt 022; independent desktop/narrow prefill reload and role checks are in 024. Full stale-proposal, revoked-account, unknown-outcome and keyboard acceptance remain open.

Active contractual amendments, rent-review approval/versioning, renewals, dated
multi-owner/co-tenant portal membership, operational status transitions, Sequence
identifiers, and missing tenancy date fields remain required RFC work. This draft
form does not satisfy or defer those requirements.
