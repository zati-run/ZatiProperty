# Hierarchy permission restoration and next overlay

Reviewed app source: 0761c44f95d35c8432800b92e162c25e7d9e8481. The owner-restoration journal preserves its original intent, records successful readback verification, and records ownerDigest 102a1779647d76b03b5da724dcb6e41ed63b457c9906b79b01cc27aec0381d50 and restoredResources zp_properties/zp_units. Fresh native read-only capture independently confirms canonical owner permission resources equal the original hierarchy baseline. Vendor state is unchanged. Tenant differs only by duplicate unitId in the existing tenancy view field list; no additional distinct permission. Preserve this observed state rather than silently normalizing it.

Fresh checkpoint: hierarchy-restored-20261010. Baseline digest: 228e3fd57fa41b17de92b391504e5f2f9b810e15e70c06d4769f2d44703ddfb7. Four roles and eleven manager permission resources captured. The prior hierarchy baseline and drift evidence remain untouched. Manager native metadata already contains properties.units and units.tenancies; its unit view has duplicate propertyId. Native state presence is not authorization acceptance.

After coordinator review and exclusive mutation-lane handoff, the existing permission overlay entry point is:

```sh
python3 scripts/apply_property_ui.py --phase permissions --checkpoint hierarchy-restored-20261010 --baseline 228e3fd57fa41b17de92b391504e5f2f9b810e15e70c06d4769f2d44703ddfb7 --journal-suffix hierarchy-reviewed-1
```

Use the privately configured ZP_RUNTIME_DIR; this command writes through Loom. It was NOT executed by the review lane. Recheck that its journal suffix has no existing intents, validate desired generation/roles/property-tenancy.json against the exact reviewed source, and stop if any role baseline drifts. Do not substitute a fresh checkpoint merely to evade an uncertain journal. The overlay has eight scoped-resource operations and eleven manager permission resource writes; it preserves existing write actions, portal state, flags, snippets and routes. Any already-existing scope must match exactly. No generic domain writes or constructor account-authorization grants are permitted.

Post-overlay verification must include manager1 property4→units3/4 and unit3→tenancies4/5 allowed with native projections; manager2 direct get/list and association endpoints exclude that graph. Test properties.units and units.tenancies through both appends and association endpoints, own/foreign source IDs, explicit fields and nested appends. Owner/tenant/vendor must retain prior scopes and deny the new hierarchy relation grants. Protected event/outbox/command-receipt/account identity fields and generic users enumeration stay denied. Run existing property UI and populated-role read suites plus hierarchy-specific cases with role-specific selected-role credentials. Reads alone do not qualify writes: generic create/update/delete remain denied and protected action ACL still excludes constructor authorization. Native rendered hierarchy navigation, reload and allowed/denied form interactions remain separate gates.

No app mutation was performed by this review lane. The fresh capture used only native reads through Loom. A rejected invocation with an unsupported CLI option exited in argument parsing before any runtime call.
