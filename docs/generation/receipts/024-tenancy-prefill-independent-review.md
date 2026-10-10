# Independent tenancy draft readback and role review

Reviewer worktree base aa8cc2f. This review observes generated runtime state;
it does not modify or approve unrelated uncommitted desired-page source.

Fresh synthetic manager browser sign-ins independently reopened the generated
Tenancies amendment popup for tenancy4 at desktop1365 and narrow390 widths.
The form loaded revision3, record version2, rent160000 NZD minor units, deposit300000,
the revised tenant display name and the permitted tenant account label.
Read-only native proposal confirmed account6, one complete primary party with dates,
and all contractual terms. Narrow top/bottom screenshots demonstrate readable
stacked controls; no submit or keyboard-only acceptance is claimed.
No page errors were captured in these fresh amendment browser sessions.

Sixteen read-only Loom checks across eight synthetic accounts passed. Manager1
can resolve and read the proposal. Manager2 resolve returns HTTP200 with
contextAvailable false, empty prefill and null digest/version; direct proposal is
403. Both accounts for owner, tenant and vendor receive403 for both operations.
The initial observer stopped when it incorrectly expected every denial to be HTTP
non-success; that private observation was retained, and the exact scoped-empty
contract was then separately verified. No business operation was retried.

A separate fresh manager browser reload also found new draft tenancy6, revision1
and version0. Native proposal independently confirmed USD150000 rent and300000
deposit minor units, account6, primary party and dates2042-01-01 through2043-01-01.
This verifies persisted amounts after the coordinator's once-only creation,
not a second creation or an independent submit replay.

All application reads used Loom role bridges or the generated browser journey.
No direct operator REST, business command, schema edit or permission write was
performed. Role bridges were stopped after use. Full E3, tenancy activation/end,
financial posting, full keyboard interaction and all narrow creation paths remain
outside this bounded receipt.
