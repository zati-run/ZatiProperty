# Native property context read verification

Observed: 2026-10-10T10:57:51.859687+00:00.
Verifier source: faa9848cd295d09ff02770a9ccf3f97771eb7044.
Target: isolated synthetic zp-dev, NocoBase CE2.2.21.
Coordinator-qualified installed context: property-tenancy0.1.2, association-guard0.1.3,
action-form0.1.0; current Loom catalog272tools,
0c86d70bbb19c25dc35f706b6e25c35871e7ed161d47be2b131c0d9571ab5b75.

On DGX, ZP_RUNTIME_DIR=<private-runtime> python3 scripts/verify_property_ui_reads.py
passed126/126 data GET cases. Eight additional roles:check GETs confirmed each
single selected application role and absence of constructor/configure authority.
Sign-in used the qualified Loom native authentication tool; tokens stayed private.
The runtime mutation lane was held during this read matrix. No app writes occurred.

Results:45 HTTP200 and81 HTTP403. Manager accounts ran54 cases; owner, tenant and
vendor accounts ran24 each. All72 portal new-resource/relation cases returned403.
Foreign manager records were excluded either by explicit403 or successful empty
scoped responses; empty results were not treated as successful record access.

Positive fixtures: manager1 property4, unit3, building1, owner contact1; unit3's
property4/building1 binding was separately confirmed through Loom before testing.
Manager2's existing property2/unit2 provided reciprocal foreign-scope checks.
Own direct GET, filtered LIST, property/building appends and association endpoints
returned the expected native IDs with whitelisted fields. Explicit private identity
field projections were denied. Manager2 could not retrieve manager1 context.

The new portfolio, ownership, interest, party, term and permitted-account resources
also received direct list checks, but empty collections do not establish populated
row-scope or revision acceptance. Those future synthetic positive/negative graphs,
protected command workflows, browser persistence, role navigation and full E3/E5
membership transition qualification remain open. Existing maintenance coverage is
separate; this receipt does not imply financial or full portal acceptance.

Sanitized detailed evidence: property-ui-role-read-results.json.
SHA256:278e3d903da4440afd6b4001c75dd6d7511e37c471f580ede3b06e2308c40688.
Only account aliases, case labels, status, native synthetic IDs and observed field
keys are retained; response values, tokens and private endpoints are excluded.
