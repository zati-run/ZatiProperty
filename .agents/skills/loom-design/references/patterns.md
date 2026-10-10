# Native application patterns

Apply only supported controls and properties from the current Loom/NocoBase catalog.
These are design intentions, not API schemas. Read only the relevant section.

## Navigation and overview

Group by work: Portfolio, Leasing, Maintenance, Accounting for a property manager;
use each role's vocabulary and allowed tasks. Put the most frequent destinations
first. Keep a clear current location, human-readable record title and return path.
Start an overview with work requiring attention and its next action. Add metrics
only when each answers a real question; label units, period, freshness and empty
results. Charts need a task, accessible labels and an equivalent readable summary.

## Lists and queues

Show identifying context, status, next relevant date and actionable exception first.
Default sort should match the task (e.g. urgent open requests, then age). Keep search
and useful filters discoverable; show active filters and an obvious reset. Preserve
context when returning from a record where the native capability supports it.
Align numeric amounts, show currency/date conventions, and distinguish missing
values from zero. Limit initial columns; put long notes and rare fields in details.
Do not make every cell an action. Bulk actions require selection feedback, scope
and permission checks; avoid exposing destructive default actions accidentally.

## Detail and action

Lead with record identity, status, critical context and next action. Group the
remaining fields by meaning; use tabs only for distinct, substantial tasks. Related
records should show their relation and a clear route back. Keep audit/history
available without crowding routine work. Use action labels such as “Create lease”
and “Assign vendor”; reserve vague “Submit” for contexts where the result is clear.
Financial actions must use the protected domain service; layout never bypasses it.

## Forms

Ask only for the fields needed now. Group related fields, label every input, mark
requirements clearly and explain unfamiliar formats with short examples. Use safe
defaults and appropriate native input types. Validate near the field, preserve
entered values on failure and explain how to recover. Keep save/cancel discoverable;
show pending and success states. Warn about unsaved work if supported; record the
gap if not. Separate destructive actions and describe the affected record/scope.

## States, accessibility and narrow screens

Design loading, first-use empty, filtered-empty, error, success and permission-denied
states. Give each a truthful explanation and a permitted next step; never invent
records to make a dashboard look populated. First-use prompts should teach the task.
Provide visible focus, keyboard operation, text labels and understandable errors.
Use the [WCAG 2.2 reference](https://www.w3.org/WAI/WCAG22/quickref/) when checking criteria.
Aim for WCAG 2.2 AA: check contrast, focus visibility, name/role/value, reflow and
minimum target size under the applicable criteria. Do not assert compliance from
this checklist alone. On narrow screens, prioritize key identity/status/actions,
keep labels readable and use supported column/detail alternatives. Horizontal
scroll for genuinely two-dimensional data must be discoverable and contain all
columns; surrounding page content should still reflow without clipping.
