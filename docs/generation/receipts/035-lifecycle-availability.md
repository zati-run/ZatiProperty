# 035 — State-appropriate tenancy actions and explicit refresh

Three existing native protected forms were updated once through Loom MCP with fresh package/schema/placement qualification and node CAS. Source: df85af18fcd270303d74563d25df4f4822cb7978, independently reviewed by the coordinator before applying. NocoBase Community Edition 2.2.21, synthetic development installation; action-form companion 0.2.0 and protected property-tenancy domain 0.1.4. Actual UTC verification time is in the sanitized JSON.

- Activate tenancy now displays editable controls only for draft records.
- End tenancy displays editable controls only for active records.
- Amend draft displays its complete editable proposal only for draft records.
- Unavailable actions show a short explanation and Refresh record. Pending command reconciliation remains separate and available.

Fresh native readback verified all three forms remain attached to their intended grids. Only availableWhen changed; action/schema/implementation pins, business bindings, context and permissions were unchanged. Permanent one-shot mutation journals and before/after observations are preserved privately. No business command was issued during this verification.

## Rendered and persistence evidence

Using the synthetic property manager, existing ended tenancy 6 displayed no activation, ending or amendment submit controls. Draft tenancy 4 displayed activation and amendment controls, while ending remained unavailable. Native resolve responses confirmed those states.

Refresh record reloaded the native page and reopened the ended record with the same correct action availability. On the amendment form, editing a date and choosing Keep editing in the refresh confirmation preserved the unsaved value; the original value was restored locally and never submitted. Desktop and fresh 390-pixel viewport checks passed with no page errors, unexpected notifications or document horizontal overflow. Narrow tests used the already-qualified direct Tenancies route; hamburger navigation is not claimed here.

[Sanitized native/browser evidence](035-lifecycle-availability.json). Visually inspected narrow captures: [draft activation](screenshots/035-draft-activate-narrow.png), [ended explanation](screenshots/035-ended-unavailable-narrow.png), [amendment and refresh](screenshots/035-amendment-refresh-narrow.png).

The initial resized-viewport capture was only a loading state and is excluded. Fresh narrow captures waited for the real controls and modal dismissal. Existing duplicate optional labels and minor-unit amendment editing remain separate UX work; this receipt does not close all tenancy, portal, leasing or accounting requirements.

## Verification boundary

Seventeen app form tests and two availability tests passed against the actual companion policy. Companion source review and its mounted native React/Ant Design adapter tests separately cover pending/in-flight commands, same-model multiple instances, unknown-result storage, dirty cancellation and a request starting after confirmation opens. Those tests used isolated transport; they are not business-command acceptance.

This configuration verification used existing draft and ended records and no new active fixture. It does not newly claim the active-state ending form journey, additional role grants, production deployment or financial acceptance. Prior protected-domain and role acceptance remains in its own receipts. Independent review of this configured evidence is required before integrating this receipt.
