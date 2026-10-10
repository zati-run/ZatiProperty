# Independent bounded building journey verification

App source b1493d6, synthetic CE2.2.21, protected domain0.1.4/action-form0.1.9. Independent fresh read-only verification on2026-10-10; no business writes.

48 checks passed across eight individually authenticated synthetic accounts: direct building2 get/filtered-list, property6 associated buildings, property append, building/property context and protected form resolve. Manager1 observes its building/property; manager2 receives exclusion or inaccessible context; both accounts of each portal role are denied. Selected role checked before reads, no allowAll. [Per-case evidence](building-independent-role-reads.json).

Fresh browser captures at1365 and390 widths show the persisted building under property6 after navigation/reload. Units and the protected building form remain in the DOM; no generic Edit/Delete controls, no page errors. Narrow screenshot was visually inspected: property heading, Buildings list and Units remain legible; long building name truncates in native table. This does not establish full keyboard/polish acceptance. [Rendered checks](building-independent-rendered.json) and screenshots are separate from root creation request011551fa-95f8-4362-8287-1ad506aede25; this reviewer did not repeat that command.

Initial observer attempts used incorrect button labels and timed out without business writes. Reusing an existing private observer also replaced two private pre-save screenshot/DOM files with new read captures; original committed031 evidence and request journals were preserved, coordinator notified. Final outputs use an independent prefix. No failure was treated as a passed check.

Separately reviewed source binding e1aaa71dfb725e8ec5a602e4965cb51c005f2b5c: create-unit grid d3vkb0wzty8 has exact one-level associated building popup and parent property chain; propertyId FK/source identity and selected building key agree. Desired propertyId/buildingId come from scoped context, not a selector. Accepted for bounded generation with fresh qualification/CAS/readback; unit save/role/reload acceptance remains open. Building.units reverse field is not required for this bounded create path.

This closes only the observed building read/reload/role subset, not whole E3 or all hierarchy workflows.
