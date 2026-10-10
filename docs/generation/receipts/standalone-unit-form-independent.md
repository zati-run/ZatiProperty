# Independent source review — create a unit without a building

Reviewed exact desired source 26c40199d35238f8f59dc3039d18127947933a17 (superseding the initial placement in 74b3bcd). The focused form uses a proposed Add unit Portfolio row-action drawer, binds propertyId from the selected property, and omits the optional buildingId through the reviewed typed companion contract. It creates no invented native UIDs, numeric identity input, new role grants or generic CRUD fallback.

Independently validated the desired configuration against the actual protected domain createUnit schema, companion policy at 2cdb865e404ac9eb91248f3ce18874b3956b7c71, and all three constructor schemas (create, set and migrateContract). Validation passed. Companion independent review ran 61 tests successfully.

Accepted for bounded source integration and subsequent fresh native qualification. No form was generated and no business record was written during this review. Native creation, scoped access, buildingId null persistence, rendered controls and save/readback remain coordinator-owned acceptance gates.

The focused popup payload independently validates against the actual discovered native add_record_action MCP schema. It uses the existing Portfolio table UID and a native currentRecord details block containing property name and address. The new protected form grid is deliberately unresolved: actual popup creation, readback and fresh exact property-context ancestry qualification are mandatory before attaching the form. This review does not invent or approve an unobserved grid UID.
