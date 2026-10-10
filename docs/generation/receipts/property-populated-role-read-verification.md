# Populated property/tenancy native read verification

Observed 2026-10-10T11:15:36.555564+00:00; source matrix committed before execution.
Expanded matrix: **222/222 data GET cases passed**, plus eight explicit selected-role
checks. HTTP status counts: {'200': 60, '403': 162}. Actual role credentials were used privately;
authentication went through Loom and every tested data request was read-only.

The constructor first read the synthetic fixture graph through qualified native
Loom list tools. Tenancy 4 is draft revision 2 with no published tenant account;
tenancy 5 is ended revision 1. Both belong to unit 3/property 4. Party and term
IDs 1 and 3 retain tenancy 4 revisions 1 and 2; IDs 2 belong to tenancy 5 revision 1.
Permission row 1 links manager user 2 to synthetic tenant user 6.

Manager 1 reads all permitted scalar fields, both history/current revisions,
native associations and nested tenancy/unit/property context. Manager 2 cannot
read these foreign rows. Owners, tenants and vendors cannot read new party, term
or permission resources and associated expansions. All tested private identity
fields and generic users enumeration were denied. Historical manager revision
visibility is intentional; explicit revision-filter queries return current rows.

No app mutation, workflow or rendered journey acceptance is claimed. Ownership
fixtures do not exist, so populated ownership/dated-interest scope remains
unverified. This receipt supplements, rather than replaces, the earlier 126-case
empty-resource matrix. The initial 174-case populated pass is preserved separately;
the expanded pass added deeper relation traversal and complete requested-field
checks. One intervening rerun completed requests but its output publication was
correctly blocked by the existing-receipt fence; it is not counted as evidence.

Detailed expanded receipt SHA256: `52788c92a72e82225355d53d38fd02718d2eaf1d32d8ed1d72b5888d502d368d`.
