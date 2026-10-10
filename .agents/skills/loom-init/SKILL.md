---
name: loom-init
description: Prepare a project to generate its application in NocoBase through Loom MCP. Use when initializing Loom project instructions, a project generation skill, and an RFC construction contract; this skill does not generate the application.
---

# Initialize a Loom generation project

Use this portable skill instead of assuming a `loom init` CLI exists. Requires Python 3.9+ for the local helper. Copy this entire directory when reusing it.

1. Read the target repository instructions, existing RFC, and coordination record. Establish the app name, intended scope, authoritative RFC, and existing authored requirements. Resolve conflicts with the owner when there is no safe default.
2. Run the helper in dry-run mode first:
   `python3 scripts/init_project.py --target /path/to/project --project-name Example --rfc docs/rfc/rfc-001.md`
   The target must already exist; the RFC must be a .md or .markdown document outside hidden/control directories such as .git or .agents. Output reports exact destinations and collisions.
3. Inspect the proposed templates in [references](references/generation-contract.md). If approved by the task scope, add `--write`. Existing AGENTS.md requires explicit `--replace-agents`; its original bytes are preserved in AGENTS.md.loom-init.bak. Never delete a backup to bypass a collision. Existing project skills must match the generated file or initialization stops before writing.
4. Reconcile the ENTIRE RFC semantically. The helper only manages a clearly delimited construction contract and preserves the surrounding document. Remove or rewrite contradictory frontend/backend, direct API, CLI, and hand-build directions while preserving product requirements, decisions, and authored evidence. Document resolved decisions. **Scaffold success is not completed initialization until this reconciliation is done.**
5. Tailor the generated project skill to the application's domains, stage gates, recovery, and exact acceptance evidence. Incorporate still-applicable prior AGENTS instructions from the backup. Read the final instructions and RFC together and report remaining conflicts or unknowns.
6. Report files changed and scaffolding checks separately from live backend or application acceptance. Do not start live generation unless the user has authorized it.

Read [generation-contract.md](references/generation-contract.md) before tailoring. Discover actual Loom MCP tools and their schemas at generation time; never infer live capability from a fixed tool count or copied documentation. MCP availability, trusted endpoint and operator credential provisioning are prerequisites for live generation, not prerequisites for preparing local instructions.

The helper uses only the Python standard library, makes no network requests, and edits no credentials or MCP configuration. It refuses symbolic links in the target or managed paths, path escapes, nonregular destination files, and overlapping outputs. It preflights every destination before writing. Run with exclusive ownership of target paths: filesystem changes by another process between preflight and writing are outside its transaction guarantees.

Run helper checks with `python3 -m unittest discover -s tests -v`. These fixtures qualify scaffolding behavior only.
