# Protected hook error status — source candidate

Native NocoBase CE 2.2.21 generic root single and filtered writes were denied with HTTP500 and DOMAIN_ACTION_REQUIRED because domain.deny produced an Error without an HTTP status. Complete protected and domain snapshots remained unchanged. The HTTP500 is a product error-status defect, not accepted behavior.

This candidate is based on terminal-command source a233699c81ae2707215c9bc8a713e8994846141e. It retains the uninstalled 0.1.3 candidate version. The hook-only denyHook helper recognizes exactly DOMAIN_ACTION_REQUIRED, CONTEXT_IMMUTABLE and CONTEXT_DELETE_PROTECTED, supplies a safe human explanation and stable code, and sets status/statusCode403 plus expose=true for native middleware. Unknown codes remain internal TypeError failures; no global exception masking or role broadening is introduced. Domain command rejection handling is unchanged.

All 54 Node source/adapter tests passed on DGX. Tests cover all three allowlisted errors, safe messages, HTTP status and unknown-code behavior. This is source qualification only. After independent review and Loom installation, repeat complete native guard probes and verify actual HTTP403, stable code, useful message, and unchanged full state. Nested guard qualification also depends on the separate native array-serialization fix.
