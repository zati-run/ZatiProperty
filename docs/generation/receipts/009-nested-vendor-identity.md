# Nested vendor identity negative check

Date: 2026-10-10. Target: zp-dev, synthetic maintenance fixtures only.
Evidence: one live role-specific Loom MCP write attempt plus separate constructor
Loom readback. Actor was `zp_property_manager.1`, verified by the existing ephemeral
role bridge as the selected manager role with `allowAll: false`.

The attempted work-order update used the already assigned vendor association:
`vendor: {id: ownVendorId, userId: otherSyntheticVendorUserId}`. This tested whether
an allowed native association field could mutate a protected target user binding.

Result: the native call returned successfully with no error, but no work-order,
vendor or other-vendor field changed. Vendor user ID remained 8; attempted ID 9
was not applied. Both values identify synthetic fixture accounts. Independent
before/after snapshots of all three records were captured privately. No restoration
was needed or attempted, and no mutation was retried.

This is a **passing bounded negative**, not evidence that all nested association
writes are safe. Property-permission mapping mutation was not attempted. The
separately confirmed read disclosure ZP-ACL-001 remains open pending its guard.

Harness: `scripts/verify_nested_vendor_identity.py --run`, with private runtime
and Loom source environment bindings. Default invocation is preparation only.
All writes are through the ephemeral manager Loom MCP instance; no direct native
REST, CLI or database mutation was used. Tokens and private bridge files are not
included in this receipt.

## Bounded nested mapping negative

After generic association guard 0.1.1 restored native key readback, the coordinator authorized one additional manager-role Loom update of the existing own vendor's nested `propertyPermissions` association, attempting to change the own mapping's property from synthetic ID 1 to foreign property ID 2. Before and after snapshots covered the work order, vendor, both known mapping records and the complete mapping list. The native call returned successfully, but all snapshots remained unchanged; property ID remained 1. No restoration or replay was needed. Harness: `scripts/verify_nested_vendor_mapping.py --run`; default invocation performs no mutation.

An earlier attempt under guard 0.1.0 stopped at before-state readback because the guard omitted native IDs; no write occurred on that attempt. This passing bounded negative does not generalize to arbitrary nested creates, deletes or every association payload.
