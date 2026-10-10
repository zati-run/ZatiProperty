# Independent source review — create a unit without a building

Reviewed exact desired source 74b3bcd918ba3a10205c4a742abbcb6fd4ffb219. The focused form uses the existing property detail placement, binds propertyId from the selected property, and omits the optional buildingId through the reviewed typed companion contract. It creates no invented native UIDs, numeric identity input, new role grants or generic CRUD fallback.

Independently validated the desired configuration against the actual protected domain createUnit schema, companion policy at 2cdb865e404ac9eb91248f3ce18874b3956b7c71, and all three constructor schemas (create, set and migrateContract). Validation passed. Companion independent review ran 61 tests successfully.

Accepted for bounded source integration and subsequent fresh native qualification. No form was generated and no business record was written during this review. Native creation, scoped access, buildingId null persistence, rendered controls and save/readback remain coordinator-owned acceptance gates.
