# Next slice: property context to an active tenancy

Status: proposed implementation sequence, not generated state or acceptance. The
maintenance browser gate remains open; this proposal neither completes E3 nor
changes the authoritative task graph in `docs/plan.md`.

Contract: RFC 5.1, 5.3–5.4, 5.6–5.9, 6.1–6.3, 6.6–6.7, 11 and 13. Design uses
`generation/design.md` and Loom design references `patterns.md` and `review.md`.
Implementation remains native NocoBase CE through Loom MCP on the qualified DGX
installation. Only synthetic data and non-consequential development actions apply.

## First outcome

A manager selects a property and vacant unit, inspects its existing occupancy and
ownership context, creates a draft tenancy with its parties and terms, reviews
validation, activates it, and sees the same current tenancy on the unit after
reload. A second manager cannot see or change that property. A tenant sees only
its own permitted tenancy summary. Ending and replacing that tenancy preserves
history and does not rewrite the existing maintenance request's historical context.

This is the next usable outcome. Financial balances, deposit custody, rent posting,
lease signing, screening decisions and legal notices are separate protected gates.
A typed rent amount is a contractual term; it must not create a ledger balance.

## Sequence and resources

| Increment | Desired native resources | Meaningful exit |
| --- | --- | --- |
| 1. Portfolio and occupancy context | Extend existing properties/units/tenancies; add portfolios and optional buildings; owner contacts and dated property interests; property/tenancy parties | Manager can explain which unit, current tenancy, owner interests and historical maintenance context a record belongs to |
| 2. Draft-to-active tenancy | Tenancy terms and parties, move-in/out checklists, lifecycle action service and immutable change events | Draft activation and end/replace workflow survive reload, concurrency and cross-role negatives |
| 3. Operational follow-up | Prospect pipeline/contact history, insurance policy/renewal evidence, subsidy arrangements/inspections, rent-review proposals, private document links | Manager sees actionable upcoming work tied to the correct tenancy, without external sending or financial posting |

Keep one reviewable batch per completed outcome. Qualify each batch through source
checks, native readback, persistence, role cases, rendered journeys and independent
exact-head review before local integration and landed verification. The first two
increments should land before broadening operational follow-up.

### Schema decisions to qualify

- Preserve all existing native IDs, stable logical IDs and maintenance links. Add
  fields/relations through discovered Loom schemas; read before applying. The current
  minimal tenancy `open` status is historical implementation state, not a complete
  lifecycle. Record an explicit, fixture-tested migration to the accepted lifecycle;
  do not silently relabel data or add a competing second source of status truth.
- Property: stable identity, address, jurisdiction references and portfolio/building
  hierarchy. Unit: stable name/code, property/building relationship, bedrooms and
  lettable status. Derive occupied/vacant display from accepted tenancy dates rather
  than a freely editable occupancy flag.
- Owner contacts and property interests: owner identity, share, effective dates,
  management agreement reference and non-posting reserve instructions. Use exact
  fractional representation; the proposed whole-property share validation is 100%
  for a complete interest set. Confirm representation for incomplete onboarding
  rather than inventing ownership or silently rounding shares.
- Tenancy: unit, dates, currency, rent in integer minor units, frequency, due day,
  prorating/deposit terms and lifecycle. Add primary tenant, co-tenant, guarantor
  and occupant party relations with explicit roles. Deposit terms are not receipt
  or held-funds records. Preserve past parties and terms through versioned changes.
- Prospect: stages matching RFC inquiry/showing/application/screening/lease/lost,
  assigned staff, source, notes and permitted follow-up dates. Move-to-tenancy links
  preserve prospect history; no automated application approval.
- Insurance: coverage dates, status, policy evidence and reminder proposal. Subsidy:
  agency/program, dated tenant/subsidizer responsibility and inspection schedule;
  responsibility terms do not post receivables. Rent review: proposal, criteria
  reference, effective date and required human decision; no sent notice.
- Documents: entity link, category, retention classification and storage identity.
  Use authenticated retrieval. Do not expose a public attachment URL as a substitute
  for private document access; this blocks document acceptance until qualified.

## Server invariants and protected actions

Use a small domain plugin only for verified invariants/gaps. Its installation,
updates and typed construction integration must remain available through Loom.
Native form validation helps users, but cannot replace server checks.

1. Unit/building/property references must agree. Effective ownership, party and
   tenancy dates must be valid. Co-tenants share a tenancy rather than creating
   accidental overlapping occupancies. Qualify the proposed non-overlap rule for
   active tenancies on the same unit, including simultaneous activation requests.
2. Activation requires permitted unit, valid dates and required parties/terms.
   End/replace creates a traceable history transition; it cannot cascade-delete
   maintenance links or rewrite earlier recorded tenancy context.
3. A manager cannot change manager/user ownership bindings, linked parties or
   property interests merely by nesting objects inside an otherwise allowed form
   update. Validate direct, FK and association payloads and rollback failed changes.
4. Immutable lifecycle/change-event records identify actor, previous/new state and
   reason. Do not call a mutable event collection a qualified audit trail. If the
   RFC append-only audit requirement is unavailable, implement the protected audit
   dependency before claiming lifecycle acceptance.
5. Monetary terms use integer minor units and explicit currency/frequency. No
   generic writes to balances, journals, paid status, distributions or trust data.
   Proposed rent/deposit/subsidy terms cannot trigger ledger or provider calls.
6. Notifications are synthetic in-app work items only. Move-out/renewal/rent-review
   proposals do not send notices. Screening, e-signing, adverse decisions, payment
   execution and real external communication retain separate authority gates.

## Roles and native pages

Staff navigation starts with **Portfolio** and **Tenancies**, retaining Maintenance.
Use native tables with meaningful filters, focused record drawers/pages and short
forms; avoid one menu item for every collection.

- **Portfolio queue:** property and unit identity, occupancy period/status, next
  operational task. Property detail groups units, owner interests and recent work.
- **Unit detail:** current and future tenancy, previous occupancy history and linked
  maintenance. The primary action reflects the real state: Create tenancy for a
  vacant unit, View tenancy for an occupied one.
- **Tenancy draft:** context first; parties and dates, then terms/checklist. Show a
  review summary and explicit Activate action; display date/overlap errors at the
  affected fields without losing entered data.
- **Active tenancy:** current terms, parties, documents and task history. End tenancy
  is distinct from ordinary editing and asks for a reason/date without suggesting
  that deposit settlement or legal notice is already complete.
- **Follow-up queue:** expiring insurance, scheduled inspections and rent-review
  proposals grouped by due date with a permitted next action, not unqualified
  balances or decorative metrics.

Retain manager property scopes based on qualified assignments; owner scopes derive
from effective interests, tenant scopes from active or historically permitted party
links. Adding co-tenants must not expose unrelated occupants' private fields.
Vendors gain no new tenancy/owner-document permissions. Owner/tenant screens need
only the relevant summary/actions; no builder, selector-construction, audit-edit or
financial authority. Finance roles are not introduced as a shortcut to this slice.

Every new relation grant needs target row/field checks through the association guard.
Its current supported surface is bounded; union roles, deeper traversal, reports,
exports and custom actions must not inherit presumed qualification. Native menu and
route access are additional checks, never substitutes for record authorization.

## Synthetic fixtures and acceptance

Use at least two manager portfolios with different owners, tenants and property
assignments. Include a vacant unit, an active tenancy with co-tenant/guarantor, an
ended tenancy with maintenance history, a future tenancy, conflicting dates,
expired/valid insurance, split subsidy terms and a pending rent-review proposal.
Include an owner interest change and denied attempts to retain another owner's
records. Reuse the existing maintenance fixture identities where compatible; add
new graphs rather than overwrite their accepted state.

Required evidence per increment:

- Exact revisions, schemas, native IDs and before/after readback; reload from a new
  session proves persistence. Native bindings must match the desired migration.
- Two simultaneous activation attempts cannot create conflicting active occupancy;
  failed transitions and nested ownership edits leave no partial changes.
- Manager/owner/tenant allow-and-deny matrix covers direct GET/LIST, nested appends,
  relation endpoints, projections and typed lifecycle writes. Fixture-specific
  shared ownership is explicitly tested, not treated as a blanket foreign denial.
- Property → unit → tenancy → maintenance context remains consistent after ending
  and replacing a tenancy. Historical maintenance retains the original tenancy.
- Desktop and narrow rendered journeys show context, readable dates/currency/status,
  usable forms and saved outcomes. Test keyboard operation, empty history, denied
  access, validation failures and unavailable-document feedback. Request/response
  success and DOM text alone do not prove visibility or usable layout.
- Protected document retrieval denies guessed identifiers and expired/other-role
  links. Audit immutability and lifecycle recovery receive independent domain review.
- Financial/provider/external-message calls remain absent from the synthetic path;
  this is an authority boundary, not proof that future accounting works.

## Loom and platform qualification before dispatch

| Capability to verify | If missing or incompatible |
| --- | --- |
| Additive field/relation changes and migration readback preserving existing native IDs | Implement a reusable Loom desired-state reconciliation operation; never mutate NocoBase directly |
| Typed lifecycle-action invocation and plugin install/update/load identity | Extend Loom's MCP schemas/adapter; do not fall back to arbitrary REST requests or client-only status edits |
| Scoped native collection and relation reads for new ownership/party paths | Expand the reusable association guard with exact native-shape tests; unsupported paths remain blocked |
| Native form actions, date controls, relationship filters and post-save navigation | Add narrow reusable Loom flow operations and verify actual native pages; no standalone frontend |
| Authenticated private attachments and approved document rendering | Qualify CE storage/actions or build a documented domain plugin through Loom; keep private-document acceptance blocked |
| Immutable lifecycle/audit service and native action permission enforcement | Implement protected server invariants with tests and qualified Loom integration before sensitive lifecycle acceptance |

Discover actual live tool schemas again for each new capability. The existing
248/250-style catalog counts and installed binaries do not establish the next
operation's availability. Record exact missing operations and bounded Loom changes;
do not defer required RFC behavior merely because generic CRUD is easier.

## Increment 1 schema preparation qualification

User identity bindings use native bigInt metadata; the domain service accepts canonical positive numeric/string IDs through JavaScript MAX_SAFE_INTEGER and rejects larger values. Contract rent/deposit remain explicitly bounded signed32-bit minor amounts (0–2147483647), enforced by both field validation and the protected domain action before database writes. Currency has no default and must be supplied as three uppercase letters. This is contractual data only; no ledger posting.

Additive migration defaults to read-only inspection. Eight offline fault tests cover lost responses, pre-write disconnects, retained uncertain intents, read-only reconciliation, conflicting fields, metadata drift, idempotent completed bindings, and missing capabilities/dependencies. These checks prove source recovery behavior only. Role grants are a separate gated operation; schema success explicitly reports appAcceptance false and never creates or changes grants. No app mutation or complete property/tenancy acceptance is claimed.
