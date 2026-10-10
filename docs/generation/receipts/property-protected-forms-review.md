# Protected property forms independent source review

Accepted source candidate: 8e24c22745dc8ce606b9351dbfc509b382140c2b, incorporating
c6f737d preparation. Reviewer coverage_plan, 2026-10-10. This is source approval
for bounded native generation, not native or rendered app acceptance.

Eight source tests passed independently in an isolated DGX review worktree using
`PYTHONPATH=scripts python3 -m unittest tests/test_protected_forms.py -v`.
Diff check passed. No app mutation was performed by this review.

Both findings from the prior blocked c6f737d review are resolved for this tranche:
the helper proves native popup ancestry, main collection, selected-row filter
and popup.record capability during qualification and immediately before dispatch.
The companion independently enforces this server-side. Draft terms fix currency
to USD through immutable server-validated nested input; terms, rent and deposit
labels state USD explicitly. General multi-currency form support remains planned.

The required companion is independently reviewed 0.1.3 source
bd5fe84458a50d781aa2588bbbf77a160128cbac. Action/package/schema/content/command-contract
pins, caller role execution, readback, native CAS and durable no-replay journals
remain intact. Generic CRUD and constructor authority are not granted to managers.

Before application acceptance, qualify actual installed package bytes and native
placement; generate through Loom, read back, test scoped roles, then verify the
rendered journey, explicit decision controls, terminal correction and reload.
This receipt does not approve changes outside the reviewed source or waive those
runtime gates. Domain and accounting acceptance remain separate.
