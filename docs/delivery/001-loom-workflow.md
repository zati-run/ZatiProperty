# Loom generation workflow preparation

Date: 2026-10-10

## Owner decision and scope

ZatiProperty must be generated on NocoBase through Loom MCP. This delivery prepares
the RFC, project instructions, generation skill and reusable initialization skill.
The owner explicitly selected preparation first; no live application generation is
part of this delivery.

The initial RFC and auto-generated AGENTS were untracked source material. Original
copies were preserved in a Git-private backup before the isolated execution copy
was edited. LICENSE is unchanged.

## Decisions

- RFC revision 3 makes Loom the mandatory construction interface and reconciles
  stale standalone/multi-company architecture with one NocoBase CE installation
  per management company. Detailed functional scope is retained.
- Build-time Loom authority and runtime application AI are separate. Both authoring
  endpoints can act outside read-bridge data restrictions; typed UI limits do not
  imply resource isolation.
- `zatiproperty-loom` owns this project's generation workflow and evidence contract.
- `loom-init` is a portable Agent Skill with a local Python helper, not a new CLI
  subcommand. The existing Loom command launches the server; no CLI source or
  installation was altered. The helper can safely scaffold instructions and a
  marked RFC construction contract, but the agent must semantically reconcile the
  full RFC. This avoids pretending a text template can rewrite arbitrary designs.

## Evidence

Execution occurred in an isolated Linux worktree. The installed Loom README and
UI/native delivery guides were inspected for endpoint semantics. No current Loom
MCP connection is exposed in the coordinating session; no backend discovery or
mutation was claimed.

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .agents/skills/loom-init/tests -v`
passed all 14 helper tests, including dry run, idempotence, backup preservation,
collisions, reserved paths, traversal and link safety. Relative documentation links
were checked. Independent source review identified an incomplete description of
UI authoring authority; that description was corrected in the RFC, AGENTS, project
skill and reusable template, and the helper suite passed again.

These checks qualify workflow preparation only. Live app generation still requires
an authorized target, connected Loom endpoint, current schema/catalog discovery,
CE/package qualification, and the RFC's generation and acceptance gates.
