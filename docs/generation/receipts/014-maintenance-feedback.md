# Maintenance approval feedback repair

Date: 2026-10-10. Target: `zp-dev`, NocoBase CE 2.2.21. Loom source:
`ec4b6408d4376e5a3cf881dd2ffb28342140e1e7`.

The native manager form rejected Progress safely but displayed only an internal
error identifier. Maintenance plugin 0.1.3 now explains that owner approval is
required, that approval is not available yet, and that the job should remain in
Quote. The server rule and HTTP 422 response are unchanged; a stable error code
is attached independently of the human message.

Independent source reviewer `loom_discovery` accepted the bounded change before
installation. DGX command `node --test --test-concurrency=1 test/*.test.js` passed
all 18 tests. Archive SHA256:
`21d80cc1d3c4eee6c61cc4e01a91c4752720c1536fa6c41e3381747352ed2021`.

Installation used Loom `nbf_plugin_update_upload`, with a private durable intent
recorded before the request. The queued response was `ok`; no retry occurred.
[Five installed file hashes](maintenance-013-installed-files.json) match the
reviewed source. The older 0.1.2 identity receipt is explicitly historical.

A fresh browser denial returned HTTP 422 with the full human explanation,
preserved the attempted form values, and left native persisted state at Quote
and vendor 1. The coordinator independently inspected the rendered error
screenshot. This proves the bounded denied transition; it does not implement
owner approval, payment proof, or accounting.
