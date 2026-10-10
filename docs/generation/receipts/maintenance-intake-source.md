# Maintenance intake and conversion source candidate

Scope: RFC 8.1 manager intake → request context → one linked New job → existing permitted vendor assignment. No progress, spending, approval, invoice or payment authority.

The existing rendered maintenance queue has Filter/Refresh/View and request context with vendor assignment. It has no intake/conversion controls. A fresh manager session confirmed this; this receipt does not claim the proposed controls are generated.

The candidate reuses Loom's protected action-form interface and idempotent-terminal-v1 contract. It adds two maintenance actions and actor-bound read-only reconciliation. A native transaction locks the submitting user and request, validates manager/property/unit/tenancy scope, creates at most one linked job through this service, preserves the request and its snapshot, and links original native attachment IDs. Successful and terminal rejected command receipts are immutable through generic CRUD. Financial lifecycle guards are unchanged.

Native file-manager 2.2.21 source defines attachment fields as belongsToMany targeting attachments with Upload.Attachment. The proposed request edit uses that native widget; job conversion copies the original associations. Source tests prove link-copy intent and rollback behavior, not actual upload, storage privacy or rendered file access. Those remain required native gates.

Validation: DGX Node test runner, maintenance plugin suite: 30 passed, zero skipped. Tests include registered action/Swagger agreement, unauthenticated and union-role denial, original-action reconciliation authorization, generic receipt/intake creation guards, file creator association checks, command replay/collision, concurrent conversion in a serialized transactional fixture, scope denial and link-failure rollback. Fixture concurrency is not native database concurrency acceptance.

Required before acceptance: independent exact-head review; Loom-only package/schema/role/page generation with durable intent journals; package/schema readback; real manager intake and native file upload; conversion and vendor assignment; saved reload at desktop/narrow widths; own/foreign and all portal role deny checks; actual native concurrency and rollback qualification; direct and nested file access tests. Existing role grants must be preserved by overlay/readback, never replaced from historical manifests.

Native generation has not begun in this lane. Protected form pins must be discovered after installation; candidate qualification flags remain false until independent review and live schema binding.
