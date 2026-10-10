# Independent property/tenancy read preparation review

Reviewed candidate: 6ee6036a3d24b16d43df0bb13d8ca48b8ff8c713.
Base: 6f49583b7ccef7933e4819256cffab60112a744d.
Reviewer: coverage_plan; source author: runtime_discovery.
Date: 2026-10-10 UTC.

Decision: approve this read/navigation preparation candidate for integration.
No runtime writes were performed and this is not page, permission or E3 acceptance.

Inspected the two native page manifests, manager read overlay, captured baseline,
scope-preserving merge helper and durable mutation journal. The overlay retains
existing manager write actions rather than replacing whole resource grants,
rejects differing or unrestricted existing view scopes, and grants no portal,
generic users, audit or command access. Context-bound tables use property/tenancy
IDs plus current revision; nested targets have separate manager-scoped reads.
Historical revisions and unqualified portal draft access remain outside the grant.
No generic data create/edit/delete action is introduced by the page manifests.

On an isolated DGX reviewer checkout of the exact candidate,
python3 -m unittest discover -s tests -p test_property_ui_preparation.py -v
passed all seven tests. git diff --check from the stated base passed.
Recomputed baselineHash and manifestHash both match the captured preparation
receipt. These checks are offline source/helper evidence only.

Before apply, the coordinator must re-read native role flags, permissions, route
grants and field metadata; reject baseline drift; retain scoped native IDs; and
obtain durable native readback. The proposal explicitly leaves actual context
binding, allowed/denied relation access, generated page actions, persistence and
desktop/narrow rendered journeys to native qualification. Property draft,
membership migration and protected command forms retain their own gates.
