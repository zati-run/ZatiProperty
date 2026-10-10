# Maintenance client entry repair

Target: `zp-dev`, synthetic development only, NocoBase CE 2.2.21.
Loom source includes commits `bd32fea` (authoring-only bootstrap) and `f0cc2a1`
(plugin update selector binding), based on `5ed932583ef550edb4446f0b4d9ad7c5f3a470ae`.

A fresh browser failed to load because enabled maintenance plugin 0.1.1 had no
native client entry. Earlier root screenshots predate that failure and are not
acceptance for the current plugin-enabled application.

Plugin 0.1.2 adds the native UMD client entry, a no-op Plugin subclass; its server
invariants are unchanged. Coordinator independently reviewed the loader source and
ran `node --test packages/plugins/@zati/plugin-maintenance/test/*.test.js`:
18 passed. AMD, CommonJS and browser-global export checks passed. These are local
source checks, not native interaction acceptance.

The archive SHA-256 is
`410b557ee22b5216f5daadcd5c24a7e3c7c7c8d6f7cd75ea45ff6cdb774ea639`.
The coordinator checked this digest before invoking discovered
`nbf_plugin_update_upload` with package selector `@zati/plugin-maintenance`.
Loom returned `data: ok`; this native operation is asynchronous, so that response
alone did not prove installation. The expected native static client asset then
returned HTTP 200, and the independent browser worker confirmed fresh manager
sign-in and rendered request/linked-work tables.

Full journey acceptance remains pending: manager context relations need qualified
read grants, and ZP-ACL-001 association disclosure blocks portal acceptance.
Native plugin manager package metadata may remain stale after in-process reload;
reported cached version is not used as proof of loaded archive identity. No live
payments, accounting, external communication or production deployment occurred.
