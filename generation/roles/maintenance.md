# Maintenance roles

Desired state; not runtime acceptance. All application roles deny schema/role/plugin authoring.

| Role | Allowed scope | Write boundary |
| --- | --- | --- |
| PropertyManager | Properties whose managerUserId equals current user; linked units, tenancies, requests and work orders; active vendor directory | Request triage and work-order assignment within own properties; no generic approval flag writes, deletions or ledger access |
| Owner | Own properties via ownerUserId; associated requests/work orders | Read only in first slice; protected approval service pending |
| Tenant | Own tenancy via tenantUserId; requests/work orders linked to that tenancy | Read only in first slice; protected intake follow-up required |
| Vendor | Own vendor profile via userId and assigned work orders | Read only in first slice; scoped completion workflow pending |

Native ACL filters must use current-user expressions from qualified metadata. Test two distinct principals per portal audience. Hidden buttons alone do not establish denial. Construction root is a separate authority and never a portal role.
