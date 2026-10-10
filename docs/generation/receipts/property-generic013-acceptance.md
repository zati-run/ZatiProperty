# Native protected-write qualification — 2026-10-10

Passed 16/16 generic-write denial probes against the synthetic NocoBase Community Edition 2.2.21 development app. App source base 0761c44; independently reviewed harness970a4f86a3ee551a1faee5fba9694ed0fd833987; six DGX safety/source-validator tests passed. All mutations were attempted through discovered Loom MCP tools with actual schema validation and fresh private durable intents.

Native package readback confirmed enabled, installed and compatible: @zati/plugin-property-tenancy0.1.3; @loom/plugin-native-array-compat0.1.1; @loom/plugin-package-lifecycle0.1.0. This lane verified live package metadata and behavior; exact archive/file attestation remains in the coordinator's separate installation evidence.

Eight root probes reached the protected domain hooks and returned exact HTTP403, stable DOMAIN_ACTION_REQUIRED and the approved human explanation. Eight manager probes returned exact native ACL HTTP403 No permissions. Probes covered single update, filtered multi-record update, nested association update using the array query argument, associated term creation, and updates to domain event, outbox, command receipt and audit-head protected contents.

Complete unprojected rows from ten business collections and four protected stores were compared before/after each probe and the whole batch. All remained identical: SHA25696b5d7315f96bc310abc4d75665b77fdc2f164b438517a033a139cf28740d40f. Private snapshots and exact error responses remain in the owned runtime; public JSON includes only labels, boundary/status and digests.

The previous fresh run stopped after three verified hook denials because the association-create fixture lacked required term fields and returned native400 validation. Its receipt remains property-generic013-native-20261010.json. After independent review, a schema-complete term fixture was used in a new guard-only run/journal; no domain or ownership commands were replayed. Final evidence: property-generic013-complete-native-20261010.json.

A separate read-only owner check confirmed current permissions equal the original baseline after the reviewed restore, owner digest102a1779647d76b03b5da724dcb6e41ed63b457c9906b79b01cc27aec0381d50.

Limits: these are synthetic native API/guard results. They do not establish browser acceptance, physical NOT NULL/FK constraints, all generic delete/bulk-create variants, production readiness or ledger posting. The protected service and hooks are the verified application boundary; physical constraints remain a separately recorded gap.

