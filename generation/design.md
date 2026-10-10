# ZatiProperty design contract

Status: proposed implementation baseline; no rendered app acceptance yet.
Authority: RFC-001 defines product scope, permissions and financial invariants.
This document defines design intent, not executable Loom schema or live capability.

## Direction

A calm, precise workspace for property operations. Clear record identity, readable
financial data and obvious next actions take priority. Use native NocoBase controls,
light neutral surfaces, dark text, one restrained accent and consistent spacing.
Preserve approved brand assets when supplied; do not invent a new Zati logo.

## Role tasks and navigation

| Audience | Priority journeys | Consequential mistake to prevent |
| --- | --- | --- |
| Property manager | Find property/unit; progress tenancy; triage maintenance | Acting on the wrong property or tenancy |
| Accounting staff | Inspect exception; reconcile; prepare statement | Misposting money or crossing trust boundaries |
| Owner | View own portfolio; inspect statement; follow maintenance | Exposing another owner's records |
| Tenant | View own tenancy; report issue; track status | Exposing another tenant's records |
| Vendor | View assigned job; inspect permitted details; update progress | Exposing unrelated work or personal data |

Map these audiences to the actual RFC roles; this table grants no permissions.
For staff, start with Portfolio, Leasing, Maintenance and Accounting as candidate
navigation groups. Show only qualified, permitted workflows. Portals use their own
small task-focused navigation. Do not mirror every collection in the main menu.

## Shared visual and content choices

- Use the native type scale; one clear page title and consistent section headings.
- Use a small spacing rhythm (e.g. 4/8/16/24 units) where native controls expose it;
  otherwise preserve consistent native spacing rather than injecting custom CSS.
- One primary action per task region. Secondary actions are quieter; destructive
  and protected financial actions remain visibly distinct and permission checked.
- Use semantic status text with color/icon support, never color alone.
- Use explicit currency, readable date conventions, aligned numeric columns and
  clear missing-value treatment. The RFC and company settings define formats.
- Prefer short domain labels: “Create lease”, “Assign vendor”, “View statement”.
  Explain outcomes and errors in plain language with a permitted next step.

## Native page patterns

- Work queue: search, meaningful filters, identity/status/date, next action.
- Record: identity and context first, grouped fields, related work and audit access.
- Form: minimal required fields, safe defaults, near-field errors, save feedback.
- Overview: actionable exceptions first; metrics only with units, period and purpose.
- Narrow viewport: identity/status/action first; supported detail/column alternatives.

## Implementation and review

Discover available layout/theme/action controls before mapping these choices.
Record unsupported choices and native alternatives in the relevant batch receipt.
First representative journey: manager opens a maintenance request, sees property
and tenancy context, assigns a permitted vendor, then confirms saved status.
Review desktop and narrow layouts, keyboard operation, empty/error/denied states
and persisted results using synthetic accounts. Financial journeys need separate
protected-service acceptance; this sample does not qualify accounting or portals.
Use `.agents/skills/loom-design/references/review.md` for the evidence procedure.
Evidence: pending connection to an authorized native app and browser surface.
