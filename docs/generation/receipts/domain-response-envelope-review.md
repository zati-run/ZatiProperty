# Independent domain response-envelope review

Date: 2026-10-10. Candidate: `52b6f57f82b639975b01d29b692e3ea1b43e963e`.
Reviewed delta: `e369d37..52b6f57`; reviewer did not author this delta.
Disposition: accepted for source integration and bounded native qualification.

The controller now gives its result directly to native middleware. The pinned
NocoBase middleware creates exactly one data wrapper. This preserves errors and
leaves native response processing authoritative. Reconciliation Swagger now adds
that one wrapper; its inner schema is byte-equivalent as parsed JSON. Every other
Swagger operation, including the proposal prefill contract, is unchanged.

Independent DGX command in the plugin directory:
`ZP_NATIVE_DATA_WRAPPING=<qualified middleware file> ZP_ACTION_FORM_SERVER=<qualified companion server file> npm test`.
Result: **65 passed, zero failed, zero skipped**. The actual pinned native middleware
and actual companion nativeDispatch participate in the adapter tests; the business
service is isolated for these response-shape tests. Covered results include create,
committed/rejected/not-observed reconciliation, proposal, and audit-health.
`git diff --check` passed.

Source hashes:
- Native dataWrapping: `1387f3c0884b40d154544824e3cf3d6d255f98e75f0641a7d31103a8effa4cd7`.
- Companion server: `5486c3e218d5338081ffe7522c46bfabc7ebfea0010ef0939a960c830d6b7737`.

No app mutation, live response acceptance, package acceptance, or rendered journey
is claimed by this review. Native installation/readback and existing uncertain
command reconciliation remain coordinator-owned gates; no prior write may be
replayed based only on these source checks.
