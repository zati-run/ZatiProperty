---
name: loom-design
description: Design and refine intuitive NocoBase applications generated through Loom MCP. Use before generating navigation, pages, forms, actions or themes, and when reviewing their rendered usability.
---

# Design a Loom application

Use the project RFC, generation skill and live Loom catalog as constraints. This
skill adds design decisions; it supplies no tools, credentials or mutation authority.
Read this core once per design batch. Load only the reference needed below.

## 1. Start with people and tasks

Identify each role's three most frequent tasks and its most consequential mistake.
Describe the shortest complete journey: entry, context, action, saved result, recovery.
Organize navigation by user goals and familiar domain nouns, not database tables.
Choose one primary action per screen or task region; keep secondary and destructive
actions visually subordinate. Hide unauthorized actions through real ACL as well
as UI visibility. A simpler screen must never weaken permissions or business rules.

## 2. Make one small, persistent design contract

Create or update `generation/design.md` before page generation. Keep it under 120
lines: roles/tasks; navigation; 2–3 sentences of visual direction; semantic color,
type, spacing and density choices; reusable page patterns; responsive priorities;
copy conventions; and accessibility/review evidence pointers. Preserve approved
brand decisions. A missing brand defaults to a calm, light operations interface:
neutral surfaces, dark readable text, one restrained accent, generous grouping,
compact but comfortable data rows. Adapt to actual user needs, not fashion.

Use the installed native theme and controls as the baseline. Favor a consistent
spacing rhythm, aligned labels, clear heading levels and fewer competing surfaces.
Use color for meaning; pair status with words/icons. Avoid decorative gradients,
oversized dashboard numbers, excessive cards and charts without an actionable use.

## 3. Design with capabilities you actually have

Map each design choice to a discovered native property, component or operation.
Record unsupported choices with a native alternative or explicit blocked status.
Never invent Loom tools, theme tokens, CSS injection, responsive controls or plugins.
Keep app construction through authorized Loom MCP. Configuration readback can
prove a setting exists; it cannot prove the screen looks good or works well.

Read [screen patterns](references/patterns.md) only for the page family being built.
Finish one representative task journey before multiplying its pattern across the app.
Prefer native table/detail/form/action compositions; approve a custom component
only for a recorded need and a separately qualified integration path.

## 4. Review the rendered result

Read [review](references/review.md) for the representative journey and before release.
Use real browser screenshots and interaction evidence from synthetic role accounts
when an authorized UI surface is available. Review desktop and a narrow viewport.
Fix task blockers before visual refinement. If browser access is unavailable, report
visual and interaction acceptance as unverified; save the concrete review steps.
Never describe generated schemas, tool success or an attractive mockup as UI acceptance.

## Token discipline and handoff

- Reuse the design contract; do not load the entire design library or repeat its text.
- Load only the current reference and relevant catalog schemas. Cache capability
  summaries with target/version/role identity; refresh when that identity changes.
- Read exact affected resources and paginated evidence; preserve IDs and errors,
  not giant tool dumps. Make small diffs and reconcile unknown writes before retrying.
- Return changed patterns, verified evidence, unresolved gaps and next task in a
  short handoff. Do not reload settled choices unless evidence requires a change.
