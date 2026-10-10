# Read-only schema preview baseline qualification

Date:2026-10-10. Target: zp_buildings.units hasMany zp_units through existing buildingId.
Baseline canonical SHA256: `36cf51dc26ae2df63e699e3ef0a82eb84db31c3c01db6d4ed6da1723cdc65976`.

Reviewer independently ran fresh native Acceptance.capture through Loom and obtained exact equality with the captured baseline. The source field is absent in native field inventory and companion inspect. zp_units.buildingId is an existing bigInt foreign key; zp_units.building is an existing belongsTo to zp_buildings through buildingId. All four captured role snapshots exactly match, including permissions, strategy and routes. No grant was changed.

Stored ACL digest: `4e8d71b6815286e449bc2645ca19d92ca1700d5d6b2df004634247b0044c7d8c`.
Actual discovered operation: `loom_native_loom_schema_authoring_preview_has_m_0166cd2ed89617d4`.
Input schema SHA256: `88e3d2976ab80a83a5d5fedece55801a0f1b2404df6a2be95286ea396c041fc5`.
The intended requestBody with the target and expectedAclDigest validates against that actual schema. The reviewer did not dispatch preview or any authoring mutation.

Subsequent coordinator outcome: the one-shot preview failed409 PREVIEW_RELATED_STATE_CHANGED. The coordinator reported full captured native baseline equality afterward. This is a blocked preview, not rollback acceptance or app authoring success: internal metadata discrepancy remains under investigation, and the original intent must not be replayed. The prior manager-negative run stopped at native403 No permissions; it establishes neither plugin-invariant execution nor a missing authority grant.
