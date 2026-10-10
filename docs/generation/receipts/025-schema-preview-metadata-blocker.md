# Schema rollback preview: blocked native metadata invariant

Loom schema ACL preservation 0.1.3 is installed, enabled and compatible on
NocoBase CE 2.2.21. The independently checked baseline SHA-256 is
36cf51dc26ae2df63e699e3ef0a82eb84db31c3c01db6d4ed6da1723cdc65976.
Target zp_buildings.units is absent. Its intended existing target foreign key
is zp_units.buildingId, with the existing building belongsTo relationship.
All four application-role policy snapshots were included.

The discovered preview operation was called once with the exact ACL digest
4e8d71b6815286e449bc2645ca19d92ca1700d5d6b2df004634247b0044c7d8c.
It returned HTTP 409 PREVIEW_RELATED_STATE_CHANGED. The original exclusive
intent and failure receipt remain preserved; the preview was not retried.

Fresh native readback after that error exactly matched the whole baseline:
target field absent, ACL digest unchanged, foreign-key/belongsTo definitions
unchanged, and all four role snapshots unchanged. That does not establish
internal native metadata preservation: the stronger preview check failed.
Investigation is assigned to a reusable Loom-side fix, preserving the strict
related-state invariant. No positive hasMany authoring has been attempted.

Manager inspect was denied by native authorization before the Loom domain
handler: HTTP 403, errors message No permissions, without a plugin error code.
The verifier must identify that exact native denial separately from the
constructor-only plugin gate; no manager grant is being broadened.
