# ZatiProperty agent instructions

## Required construction path

ZatiProperty MUST be generated and evolved on NocoBase Community Edition through
**Loom's MCP interface**. This is an architectural requirement, not an optional
integration. Read [RFC-ZP-0001](docs/rfc/rfc-001.md) and load
[the ZatiProperty Loom skill](.agents/skills/zatiproperty-loom/SKILL.md) before any
application generation or change.

Do not scaffold a standalone application, substitute another database or UI, or
bypass Loom with direct NocoBase REST/CLI/database mutations or manual UI authoring.
NocoBase owns the application runtime, durable data, native pages, roles and
workflows. Loom is the construction bridge, not a replacement application runtime.
Custom NocoBase plugins are allowed only for documented platform gaps or domain
invariants and must be incorporated into the generated application through the
qualified Loom workflow. A missing bridge operation is a blocker to resolve in
Loom, not permission to bypass it.

## Start every task

1. Read this file, the RFC, the project skill, and `ajent.social`. Preserve existing
   source, untracked files and concurrent work. Record ownership and handoffs there;
   keep this coordination file ignored in the public repository and free of secrets.
2. Inspect repository status and the current generation artifacts and receipts.
   This repository currently contains specification and workflow preparation;
   no generated application or live NocoBase acceptance is established.
3. Confirm the task's scope: preparing local artifacts does not authorize connecting
   or mutating a live instance. The current assignment is workflow preparation only.
4. For authorized generation, discover the available Loom endpoint and tool schemas,
   verify the target installation, authenticated role, pinned versions and enabled
   CE packages. Never infer live capabilities from fixture or source evidence.
5. Follow [the generation record contract](docs/generation/README.md). Keep intended
   state in Git, observed state in sanitized receipts, and unsupported work explicit.

## Authority and correctness

- `/mcp` is read-only. `/ui/mcp` has a limited typed operation set, but its
  credential authorizes the whole bound application; read-endpoint collection,
  field and tenant restrictions do not carry over. `/native/mcp` is opt-in and
  also can have broad application-wide authority. Use the smallest qualified
  surface; never enable broader authority or reuse endpoint credentials silently.
- Use synthetic fixtures until real data/environment scope is explicitly approved.
  Never commit credentials, private keys, tokens, private endpoints or customer data.
- Reconcile uncertain mutation outcomes before retrying. Capture before/after state
  and native identifiers; do not blindly replay batches.
- One installation serves one management company. Portal access still requires
  strict owner/tenant/vendor record and field scopes. Housing tenants are domain
  entities, not software tenancy boundaries.
- Ledger, audit and trust controls are protected domain services. Generic data tools
  and AI must not bypass immutable posting rules or required human approvals.
- Live payments, notices, screening decisions and tax filings require their own
  approved operational authority; app-generation permission does not authorize them.

## Execution and verification

Perform active coding and verification on qualified DGX resources under the global
execution rules. Do not start Mac builds or containers for this Linux application.
Use isolated task worktrees and bounded resources; preserve the original checkout.

There is no generated app, package manifest or app test suite yet. Do not claim that
`npm test`, a NocoBase install, or an MCP server is available just because the RFC
mentions it. Document actual commands when tooling exists. Relevant preparation
checks include `git diff --check`, Markdown/link checks and the initializer's own
unit tests; they prove preparation only.

Generated batches require native state readback, real persistence across reload,
role allow/deny checks, native UI checks, and applicable domain/migration tests.
Record exact revisions and distinguish local, fixture, live, deployment and
production evidence. Obtain independent review before integrating changes; financial
and security implementations retain the RFC's stronger review requirements.

## Reusable initialization

For another project, use [loom-init](.agents/skills/loom-init/SKILL.md). It prepares
local instructions and an RFC construction contract; it does not generate the app,
configure credentials or implement a `loom init` CLI command. Reconcile the full RFC
semantically after scaffolding. The existing `loom` launcher starts a server from an
operator-provided configuration; it is not an initializer.

## Application design

For UI generation, use `.agents/skills/loom-design/SKILL.md` and its on-demand references. Maintain `generation/design.md` as the compact shared design contract. Require role-oriented navigation, usable native page patterns, accessible states and evidence from rendered representative journeys. Do not equate a saved schema with visual or interaction acceptance.
