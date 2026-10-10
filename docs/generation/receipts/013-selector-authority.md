# Selector companion native authority and concurrency checks

Date: 2026-10-10. Target: zp-dev, NocoBase CE 2.2.21.
All operations used Loom MCP. Synthetic application roles ran through ephemeral
role-bound Loom instances with explicit native effective-role/allowAll checks.
Only expected-denied writes were attempted; scope and hash were read through the
constructor Loom connection after every case.

**Six of six bounded cases passed:**

| Case | Native outcome | Scope/hash afterward |
| --- | --- | --- |
| Constructor stale expected-hash write | 409 | Unchanged |
| Manager scope read | 403 | Unchanged |
| Manager scope write | 403 | Unchanged |
| Owner scope read | 403 | Unchanged |
| Tenant scope read | 403 | Unchanged |
| Vendor scope read | 403 | Unchanged |

The tested selector UID was `bj2lik9byrf`; current legitimate predicates were used
for the manager denied-write case. No successful write or restoration was performed.
The first harness run did not recognize the adapter's new sanitized
`selector-scope-http-409` marker and stopped after confirming unchanged state.
A bounded diagnostic confirmed the marker and unchanged state; the classifier was
updated before the successful six-case suite. No uncertain mutation was replayed.

Harness: `scripts/verify_selector_authority.py --run`. Default invocation is
preparation only. [Sanitized results](selector-authority-results.json) preserve
status codes and hashes, without tokens or private runtime paths.

These results establish the tested constructor boundary and stale-hash denial,
not successful application of new selector settings or browser option filtering.
Those remain separately evidenced by the coordinator and native browser reviewer.
