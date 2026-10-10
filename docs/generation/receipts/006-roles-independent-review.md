# Independent maintenance role preparation review

Reviewer: runtime_discovery. Scope: role application source and synthetic fixture specification; no role/data/schema mutations performed.

## Decision

No blocking source finding for applying this bounded role configuration to the isolated synthetic instance, conditional on the separately reviewed and installed domain guard. This is permission to verify the proposed configuration, not effective ACL acceptance.

## Exact reviewed files

- `scripts/maintenance_roles.py`: `ee104fe54d9f7206ebfd1b8713bef0b54a7bb3f88b10662912fada8a9c7543b7`
- `generation/roles/maintenance-native.json`: `2f245f2d729bc9aa03a283c2eb53506cacf72ac2d101ab47f19c71b2acf08d5e`
- `generation/fixtures/maintenance.json`: `c755cd1effa8857ad987f3553daabd67b15393554789a92e494a050f62958305`

## Findings and checks

- Four explicit role names; empty global strategies/snippets; explicit numeric generated route IDs only.
- Fixture accounts must finish with exactly one intended role. Root/admin accounts are rejected; default/member extras are removed and read back. No union fallback is introduced.
- Ownership scopes use server current-user expression. Nested vendor/property join scope must be proved on real native allow/deny reads; source presence does not qualify semantics.
- Manager work-order update allowlist is state, vendorId, vendor and priority. Other application roles have no update grants. Domain guard must independently reject nested vendor writes and protected financial/approval changes.
- Passwords are generated privately with secrets.token_urlsafe(32); private credential and journal files are mode 0600. Mutation arguments and backend exceptions are not logged.
- Uncertain mutation journal entries block replay until reconciliation.
- Offline command `python3 scripts/maintenance_roles.py` passed: four roles, eight accounts, zero mutations.
- Documentation follow-up: vendorId-only limitation conflicts with the explicit vendor association grant. protectedFieldsExcluded mixes hidden fields with viewable/write-protected foreign keys; clarify those separate boundaries.
- Apply is not idempotence acceptance: existing scopes/resources and relation-specific permission behavior still require native verification.

## Browser diagnosis (root account only)

Fresh synthetic initialization account signed in through native login, then read the generated maintenance page. No builder or business-record actions were used.

Screenshots: `screenshots/maintenance-root-diagnostic-1365.png` and `screenshots/maintenance-root-diagnostic-390.png`.

The native maintenance table renders an empty No data state. Narrow image was visually inspected: only Actions and Request columns are immediately visible; property/tenancy/status context requires internal horizontal scrolling. Document-level overflow was false. Toolbar uses icon-only native controls. This does not establish polished narrow-width acceptance or a completed manager journey. Initial post-resize transient blank screenshot was replaced with a fresh narrow session after page network-idle.

Role-specific journey, populated states, saved assignment/reload, real keyboard workflow and server-side denied writes remain pending. Root access is never portal or manager acceptance.
