# Initialize another Loom project

Use the portable **loom-init Agent Skill** at [.agents/skills/loom-init](../.agents/skills/loom-init/SKILL.md). There is no new `loom init` executable or subcommand. This choice keeps initialization available without changing or reinstalling the existing Loom bridge CLI.

The helper prepares three local artifacts: AGENTS.md, a project generation skill, and a managed Loom construction contract in the chosen RFC. An agent must then reconcile the whole RFC and incorporate still-applicable old agent instructions. Running the helper does not generate an application or qualify a live NocoBase backend.

## Copy and invoke

The examples below run from the target repository root.

Copy the entire `.agents/skills/loom-init/` directory into an existing target repository. From that repository, inspect a dry run:

```sh
python3 .agents/skills/loom-init/scripts/init_project.py \
  --target . \
  --project-name ExampleProperty \
  --rfc docs/rfc/rfc-001.md
```

If the target is new and these paths are available, write the scaffold:

```sh
python3 .agents/skills/loom-init/scripts/init_project.py \
  --target . \
  --project-name ExampleProperty \
  --rfc docs/rfc/rfc-001.md \
  --write
```

When AGENTS.md exists with different content, review its instructions first. Add `--replace-agents` to the dry run and then to the write command only when replacement is intended. The original is preserved byte-for-byte as `AGENTS.md.loom-init.bak`. An existing backup blocks another replacement. Preserve it and reconcile manually; do not delete it just to rerun the helper.

If the skill is installed globally at ~/.agents/skills/loom-init, invoke it from the target repository root without copying first:

```sh
python3 ~/.agents/skills/loom-init/scripts/init_project.py --target . --project-name ExampleProperty --rfc docs/rfc/rfc-001.md
```

Add --write only after reviewing the dry run.

For agent-directed use:

> Use the loom-init skill to initialize this repository for ExampleProperty with docs/rfc/rfc-001.md as the authoritative RFC. Prepare the generation workflow only. Reconcile the entire RFC with the mandatory Loom MCP construction contract, retain its business requirements, and incorporate applicable existing agent instructions. Do not mutate a live backend.

## Behavior and limits

- Python 3.9+ and its standard library are sufficient; no packages, network calls, credentials or MCP configuration changes are needed.
- Dry run is the default. Target repository creation is left to the owner.
- Unmodified generated files rerun without changes. A different project skill is a collision and stops the whole preflight. Tailored files require manual reconciliation.
- Existing RFC content outside the unique managed markers is preserved, including line endings. Missing RFCs receive a placeholder requiring actual product requirements.
- RFC paths must name a .md or .markdown document outside hidden/control directories such as .git and .agents. Relative RFC paths cannot escape the repository; symbolic links, hard-linked destinations, nonregular files, malformed markers and overlapping destinations are refused.
- All expected collisions are checked before the first write. Writes are not a multi-file transaction: disk failures or concurrent changes can leave partial work. Claim exclusive ownership, inspect any failure and rerun only after reconciling state.
- Unicode project names are accepted. Directory names use the lowercase ASCII portion, falling back to `project-loom` for names without ASCII letters or digits; inspect collision output when reusing such names.

The helper does not understand the surrounding RFC's meaning. Before calling initialization complete, review every section for conflicting custom application architecture, direct NocoBase API/CLI authoring, authority assumptions and acceptance claims. Tailor the project skill to the required data, roles, workflows, native UI and recovery behavior.

For generation, discover the actual MCP catalog and schemas. The read endpoint cannot build an app; authoring endpoints require operator-provisioned credentials and explicitly scoped authority. See the [generation contract](../.agents/skills/loom-init/references/generation-contract.md).

## Scaffold verification

```sh
python3 -m unittest discover -s .agents/skills/loom-init/tests -v
```

These temporary-directory tests cover dry run, repeatability, preservation, explicit replacement, collisions, traversal, links, overlapping paths, malformed markers and Unicode names. They do not contact Loom or NocoBase and do not establish finished-app acceptance.
