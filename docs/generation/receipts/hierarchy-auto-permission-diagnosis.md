# Native field creation expands existing ACL fields

Read-only source and native state diagnosis on NocoBase CE2.2.21. plugin-acl/dist/server/server.js fields.afterCreate iterates every main data-source role resource action for the collection and appends the new field name to its existing fields array. It does not restrict the update to constructors/managers and does not deduplicate. This explains both portal auto-grants and duplicate scalar foreign-key names after context-aware relation registration.

The captured baseline and current observed state show owner zp_properties gained units and owner zp_units gained tenancies (and duplicate propertyId). Manager additions are intended for the reviewed hierarchy; owner additions are not. This is a native schema-authoring side effect, not proof of an intended portal grant.

Prepared restore_hierarchy_owner.py defaults to read-only. It compares all four role snapshots to the coordinator's exact observed state before any operation, permits only the narrowly identified field-array additions, preserves scopes/actions/resources/global flags/routes, and produces a two-resource owner restore. The apply path uses one discovered schema-validated Loom roles.applyDataPermissions call through a fresh durable journal, then compares owner permissions to the original baseline and all other roles to the observed pre-restore state. Any drift or uncertain write stops; never retry without reconciliation.

Read-only preflight passed: owner before digest2ee8f0f9c4ebaf3d1bd8b80a42654521db66793ec524a5ba5c1a3923dbed9d9b, observed digest739ae84051b0761f909703044b3938a77442808b0d9da130a465466115586d8e. Four safety tests pass. No restore executed by this lane.

After independent review/apply/readback, capture a fresh manager overlay baseline with a new checkpoint, preserving the original baseline and owner restore journal. Every future Loom schema batch needs before/after role snapshots and explicit restore of unplanned native auto-grants before acceptance. A reusable bridge workflow should make this native side effect visible and fail closed; do not disable or patch native ACL hooks directly.
