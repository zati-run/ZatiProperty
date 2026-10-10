# Draft proposal read contract source verification

Base df76fc7ffa63076af61dcd51e450121339a54826. Candidate domain version0.1.4 adds one read-only action and no mutation action. GET draftTenancyProposal requires read plus original amendment ACL, selected manager property scope and existing draft state. Current terms/parties are validated and projected into a canonical versioned proposal envelope. Unknown state/ambiguous terms fail closed. No audit head, receipt, event, outbox or business write occurs on this read path.

DGX: node --test packages/plugins/@zati/plugin-property-tenancy/test/*.test.js — 59 passed. New checks cover stable current-revision digest, changed version/value digest, old revision/private-column exclusion, foreign manager/legacy/active denial, zero-write invariants, original mutation ACL requirement, scoped permission rejection and native GET empty-values handling. git diff --check passed.

No archive built, plugin uploaded, native mutation or runtime qualification performed. Independent exact-head review is required. Typed prefill, native role readback, rendered amendment and full RFC E3 acceptance remain outstanding.
