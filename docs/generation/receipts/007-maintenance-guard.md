# Maintenance guard qualification checkpoint

Target: zp-dev, NocoBase 2.2.21, construction root. Package @zati/plugin-maintenance 0.1.1 artifact SHA256 b8fd43aa4863cdffc8b1e94b30fcf548bbcfbbefc916604cbbf4e01aceb4ead6.

Independent coordinator reviewed source and ran the domain tests (15 passing after compatibility metadata fix). Package upload and enable occurred only through Loom. Native pm:get confirms enabled/installed; its package version and compatibility display remain cached at 0.1.0/false after in-process restart. Independent fresh process inspection of installed package and pinned compatibility function confirmed 0.1.1 and compatible server2.2.21; this is runtime filesystem evidence, not corrected native metadata.

Live Loom resource-create with missing property rejected HTTP422 ZP_MAINTENANCE_PROPERTY_REQUIRED. No invalid work order was reported created. This permits bounded synthetic fixture/role qualification; it does not pass domain acceptance. Remaining checks include contextual consistency, property-specific vendor mappings, expired vendors, persisted assignment, association payloads, rollback, cross-role denial and native UI.

Recovery: initial update failed at native filter guard; Loom fixed the selector. Subsequent update was queued but failed because the plugin was not registered. Pending-package install-upload replaced files with0.1.1. Native in-process restart preserved stale metadata caches. Awaited native enable uses fresh manifest loader and succeeded without force flags.
