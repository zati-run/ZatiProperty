# Native property command qualification — 2026-10-10

Qualified against NocoBase Community Edition 2.2.21 and installed property-tenancy plugin 0.1.2 (reviewed source 7b9cda16a991d5b29c180e8d66ff5d45070ac9eb). Harness source b5ae95c; 13 local safety tests passed. Actual MCP schemas were discovered and validated before use.

The original run committed four context commands, then stopped at constructor authority. After the reviewed plugin correction, an explicit coordinator-authorized resume reconciled the original request and all context/audit state before continuing. The first resume stopped before mutation because an existing private bridge directory was preserved. The reviewed bounded directory fix allocated fresh private attempt directories. No batch was replayed. Both historical failures remain in the final JSON checks.

Final native result: passed. Context creation and each successful command produced exactly one matching immutable audit event, outbox entry and command receipt. Same-key replay produced no additional effects; changed payload collided. Concurrent identical commands returned the same unit with one effect. Concurrent draft updates yielded one success and one stale-version denial. Overlapping activations yielded one success and one overlap denial. The winning tenancy ended successfully; native readback verified final state and binding. Audit health was valid at sequence 11.

Manager account authorization and an unmapped party were denied. Owner, tenant and vendor command calls were denied by native ACL; manager access to the foreign property was denied by the domain scope. Reconciliation for unknown and foreign-actor commands remained read-only. Expected rejections in version 0.1.2 leave audit/outbox/command state unchanged; terminal rejection receipts remain separate future work.

Synthetic bindings: property 4, building 1, units 3 and 4, owner contact 1, account permission 1; tenancy 4 remains draft at version 1, tenancy 5 is ended at version 2. Both tenancies belong to property 4/unit 3.

Evidence: property-command-native-20261010.json (initial stop), property-command-native-resumed-20261010.json (directory stop), property-command-native-resumed2-20261010.json (final passed run). Private fsynced intents, results and bridge logs remain in the owned runtime; no credentials are committed.

Limits: this is live synthetic native command acceptance, not browser acceptance, production deployment, hosted CI, generic/nested/bulk CRUD guard acceptance, ownership lifecycle qualification, or financial posting. Role resource-read matrix evidence is maintained independently.
