# Independent bounded unit journey verification

Read-only verification on2026-10-10 from source268fd84, synthetic CE2.2.21, protected domain0.1.4/action-form0.1.9. No business writes. This verifies persisted unit5/property6/building2 after the coordinator's single requestbf3fe0b9-c45c-40aa-9856-12b9e723284f; that request was not repeated.

[48 role checks](unit-independent-role-reads.json) passed across eight separately authenticated selected-role accounts: unit get/filtered-list, property6 associated units, property append, unit/property context and protected create-unit form resolve with building2/sourceproperty6. Manager1 reads its unit and resolves available context; manager2 is excluded or gets unavailable context. Owner/tenant/vendor accounts cannot see this unrelated unit or use the form. Native denied/empty outcomes are recorded individually; no generic users grant or authority change occurred.

[Fresh browser checks](unit-independent-rendered.json) passed at1365/390 widths, showing the saved unit under its property with building context after reload/navigation. Existing Units/buildings/form content remained; generic Edit/Delete absent, pageerrors empty. Desktop screenshot visually inspected: property heading, Buildings and Units tables, selected building link and protected form remain visible. Long names truncate in native tables; full keyboard/polish acceptance is not claimed.

Initial read-only browser attempt stopped on an ambiguous exact building-name locator because both Buildings and Units correctly display the name. The corrected bounded observer selected the first building-name match and checked the unit separately. No failed observer was treated as acceptance, and no business command was submitted.

Whole E3, all hierarchy workflows and post-upgrade action-form0.2.0 behavior remain separate gates.
