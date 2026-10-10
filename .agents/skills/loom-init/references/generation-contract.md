# Loom generation requirements

Application construction MUST use Loom MCP to create the app in NocoBase. NocoBase owns data models, relations, ACL, native UI rendering, and supported business workflows. A separate custom application or direct NocoBase API/CLI construction is not an implicit fallback. When a required operation is unavailable through the approved MCP tools, record the gap and seek an explicit architecture/scope decision.

Discover all pages of the real MCP catalog and validate each call against its schema. Tool presence proves neither permission nor acceptance. Separate tool discovery, successful invocation, native state verification, role/tenant checks, browser behavior, and business acceptance.

Endpoint contracts:
- `/mcp` provides bounded read-only collection access and cannot build an app.
- `/ui/mcp` is a limited typed UI subset, but its credential authorizes the whole bound application and does not inherit read collection, field or tenant restrictions. Limited operations are not resource isolation. Broader forms, actions and layouts require a qualified native capability.
- `/native/mcp` exposes broader native operations under separately scoped credentials and a pinned catalog. Both authoring endpoints are disabled by default. Native authority does not inherit read endpoint tenant/field restrictions.

An operator must provision and approve the trusted backend, endpoint, fixed role, packages, catalog and distinct credentials. Do not modify connection configuration or enable endpoints implicitly. Never store secrets in source, prompts, receipts, or coordination records. Review native table defaults, which can include view/edit/delete actions.

Before each bounded mutation batch, record desired state, discovered schema, scoped authority, dependencies, acceptance checks and recovery. Inspect existing native state and reuse stable IDs. After uncertain/unknown outcomes, inspect native state before any retry; never automatically replay mutations. Use synthetic records in an explicitly approved environment. Destructive operations, plugin changes, user/role administration, and provider operations require the applicable explicit scope.

Implement domain models and relationships, role/tenant ACL, UI and workflows through discovered approved tools, then validate records, permissions, workflows and rendered UI. Track missing tools/plugins, commercial entitlements, provider integrations and unqualified behaviors as gaps. Copied release evidence and local scaffolding tests do not establish current backend capability or finished-app acceptance.
