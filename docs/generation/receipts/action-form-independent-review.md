# Independent Loom protected-action form source review

Date: 2026-10-10 UTC.
Author: loom_discovery. Independent reviewer: coverage_plan.
Exact Loom candidate: 2e25700e258c0f8cbd035010e97d42c822b418d8.
Base: ec4b6408d4376e5a3cf881dd2ffb28342140e1e7.
Package: @loom/plugin-action-form 0.1.0.

Decision: approve bounded source integration. This is not native installation,
rendered acceptance, or approval to omit terminal-rejection recovery.

Copied the candidate package into a separate DGX reviewer worktree and ran
node --test --test-concurrency=1 packages/plugins/@loom/plugin-action-form/test/*.test.js.
All16 tests pass. The ten package files, sorted relative filename plus NUL plus
bytes plus NUL, hash to e10480d7573e57a772fe99e9f653877a5b8817d28723637b31a715c623f51031.
The exact committed package matches these reviewed bytes. Archive SHA256:
5b6afdda14f408814d332cf5e106eda09510f3ec2c8e61aeb78670dd0e40b312.

Reviewed typed constructor configuration, owned native node/CAS checks, fixed
action/context/reconciliation/readback tuple, installed implementation/schema
identity, actor and single-role authorization, and native callback dispatch
forwarding only the caller bearer and selected role. No constructor token proxy
or generic CRUD fallback exists. Scoped native reads supply context and choices.

Review findings were resolved before attestation: reconciliation pins action
identity; installed server content is hashed; canonical bigint choice strings
convert only to safe integer target fields; boolean decision fields cannot be
hidden in context/literal bindings; request/config/action/payload digests survive
payload expiry or role switches. Committed action followed by denied readback
retains uncertainty and reconciles without a second POST.

All dispatched failures retain intent. Correcting rejected input safely requires
the separately proposed terminal domain-rejection receipt contract. That remains
a required product dependency, not an approved deferral. Native package loading,
actual role ACL/callback behavior, current-record bindings and desktop/narrow
form submission/reload/error journeys still require live qualification through
the authorized Loom workflow. No runtime mutations occurred during this review.
