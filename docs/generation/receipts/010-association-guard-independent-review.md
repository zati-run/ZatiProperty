# Independent association guard source review

Reviewer: coverage_plan; implementation author: loom_discovery. Date: 2026-10-10.
Scope: reusable `@loom/plugin-association-guard` 0.1.0 candidate in the Loom repository.
This review excludes this reviewer's own plan, role manifests and verification scripts.

Reviewed archive SHA-256:
`89275b02f1c68adac0b3c07a1ec2104deccb4f0c9579587edc113de8e6e12104`.
The package was uncommitted at review; exact source digests:

| Package-relative file | SHA-256 |
| --- | --- |
| dist/server/guard.js | 1da36d423d533f7efd3cdb70b95b244cd0ab0ed81fc274e3281f02600fe9ef5a |
| dist/server/index.js | 1cf1fef223f803cef3b807f0b4595a1a1fe2a15d003110938b5d873307ca9e44 |
| dist/client/index.js | 3322effcd2d81010048c876d4001fc5394b49da159db2fafe420729e8dfcb7f7 |
| package.json | 410f5938546751544c7de5edbc1092d182dda5741b355d72dcb6c0ca9a78f985 |

## Findings and disposition

No blocking source defect found within the documented bounded native GET/LIST
scope. The reviewer challenged association source/target row authorization,
role-row-field coupling, missing record identity, hidden-field query inference,
nested/through-object projection and bounded execution. The implementation
addresses these conservatively: one effective selected role, native ACL permissions
per collection, source/target scoped record checks, declared permitted-field response
projection, query path authorization, and fail-closed unsupported shapes.

The loader uses a captured database binding for parsed native scope templates.
The author fixed a loader binding issue identified by its native-adapter tests;
reviewer inspected the final closure and independently reran the complete suite.

Independent DGX command:
`node --test packages/plugins/@loom/plugin-association-guard/test/*.test.js`

Result: **27 tests passed**. Archive digest independently matched. These are local
source/loader contract tests, not live middleware or app acceptance.

## Required live gates and limitations

Before closing ZP-ACL-001, qualify actual native `currentRoles`, collection-manager
markers, association source identity, response shapes and middleware order. Run the
independent 91-request maintenance security regression after the guard is installed
through Loom and the explicit manager context relation grants are applied. Manager
context must remain usable; rejecting every relation is not sufficient acceptance.

Intentional limits: main database and collection-manager-created collections;
GET/LIST; one effective role; one-hop association resource endpoints; depth 4;
128 returned nodes; 16 collection groups; page size at most 20. Unsupported scope,
query or response structures fail closed. These constraints may require native page
size and operator error feedback adjustments; they are not full NocoBase compatibility.
Writes, exports, reports, custom actions and production deployment are not qualified
by this review. Native system metadata paths are outside the guard's stated scope.

## Live qualification finding AG-001

After installation of 0.1.0, independent root Loom readback returned declared work-order scalars but omitted the native primary key and generated foreign-key fields. The guard's projection treats `collection.getField` as the only source of declared attributes, but the live native collection does not expose auto-generated keys there. A planned nested mapping negative stopped during its before-state snapshot, before any write. This is a blocking native compatibility finding; the source review and 27 mocked/adapter tests do not close live acceptance. The implementation author was notified to recognize native declared model primary/generated FK attributes while retaining native field permissions, with a regression test for an auto-generated key absent from `getField`.

## Independent remediation review — 0.1.1

Reviewer inspected native-field fallback to own properties of `collection.model.rawAttributes` after `getField` lookup. Native ACL permission remains mandatory; unknown attributes remain excluded. The same helper is used by projection and path/filter validation. Page-size cap is now 50 to accommodate the native chooser's default 40; other bounded limits remain. Independently reran all tests: **30 passed**. Verified archive SHA-256 `8658707871016a9bb42ebbc8dff086649b76423aa6adfb7d7e3403bb6c859c98`. No blocking source finding in this repair; actual runtime replacement, restored identity readback and complete security regression remain mandatory before closing AG-001 or ZP-ACL-001.

## Independent 0.1.2 source review

Reviewer inspected the explicit system-metadata boundary and target-ID relation predicate binding. System-to-authored paths enter full authorization; pure metadata responses are scanned for implicit authored relation objects. One-hop positive literal relation equality resolves matched target primary keys using caller equality and target native row scope in one query, rejecting overflow instead of truncating. Empty matched IDs remain a false membership predicate. OR, negation and multi-hop relation predicates are rejected. Exact native dynamic-today date predicate is supported. No blocking source finding within these limits.

Independent tests: **41 passed**. Archive SHA-256 independently confirmed: `ce6f865e64f9ccccd559c05f59affc1871b0d063e2d0750bde94e08f54e34384`. Native system metadata, mixed permitted/foreign mapping rows, same-manager other-property exclusion, dynamic dates and full prior regression remain live gates after installation.

## Independent 0.1.3 source review

The native browser picker uses a nested one-leaf relationship filter rather than the previously tested dotted key. The 0.1.3 diff normalizes only that exact bounded shape to the existing target-ID authorization path. Null, multi-leaf, multi-hop and negated/disjunctive relationship inputs remain denied. Independently ran all guard tests: **45 passed**. Archive SHA-256 confirmed `c69fa642fc29a51af778d3b6eaf6051f324de18c1bef4c04ca5f9a6583ba97f0`. Source accepted within this bounded extension; exact native-shaped query and browser qualification remain mandatory.

## Exact-head attestation — 0.1.3

Loom head `ec4b6408d4376e5a3cf881dd2ffb28342140e1e7` was independently reconciled against reviewed source and archive. Its four-file delta atop `b0df5b15b57ee94e836e412633b80509154d4dc0` is exactly the reviewed nested-filter normalization, tests, package version and documentation. Source was clean except the coordination file. Archive SHA-256 still matches `c69fa642fc29a51af778d3b6eaf6051f324de18c1bef4c04ca5f9a6583ba97f0`. The independent 45 passing source tests and subsequent 24-selector/95-security live checks apply to these exact reviewed bytes. No unchanged core suite was unnecessarily rerun. No blocking finding remains within this bounded reviewed change; complete browser and product acceptance remain separate.
