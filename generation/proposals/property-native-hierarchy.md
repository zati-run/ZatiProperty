# Native associated-record hierarchy

Prepared only; no schema, role or page mutations performed by this lane. Add two reverse hasMany relations using existing foreign keys: properties.units → units.propertyId; units.tenancies → tenancies.unitId. Existing tenancy terms/parties relations are reused. No new generic write permission or portal change.

Native Loom field reads confirmed properties currently has buildings/ownershipSets but no units; units has belongsTo property/building but no tenancies. Native flow catalog on existing maintenance request popup grid xavei31sxda advertises associatedRecords requiring associationField and includes the existing workOrders relation. The established maintenance table uses resource {binding:associatedRecords,associationField:workOrders}; this candidate applies that qualified native pattern to the hierarchy.

Property popup Units uses units; unit popup Tenancies uses tenancies; tenancy popup terms and parties use their respective existing relations. All manual hierarchy dataScope expressions are removed. Native binding owns source record ID propagation and avoids undocumented implicit-field filters.

Manager read-only overlay adds source relation fields units and tenancies; existing target collection record/field scopes remain mandatory. Native association guard must verify source access, source relation permission and scoped target access at each hop. Portals retain their previous grants. Before applying the role overlay, reconcile live grants and preserve all non-view actions exactly.

Generation gates: review these manifests; reconcile failed compose attempts and empty target grid; apply two additive fields through Loom with native readback; independently review exact field foreignKey/source/target metadata and unchanged fixture bindings; freshly query property/unit popup catalogs for the newly named associatedRecords options; apply manager relation-read union preserving scope/writes/portals; compose pages through Loom, remove generated mutation actions before routes; test own/foreign association resource endpoints plus nested paths and all portal denials; verify property4 exposes units3/4, unit3 exposes tenancies4/5 and each tenancy displays only its own terms/parties, with reload and desktop/narrow browser evidence.

This candidate does not claim schema application, contextual binding runtime acceptance or rendered UI acceptance. Scope integrity and actual child records remain native verification gates.
