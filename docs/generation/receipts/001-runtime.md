# Isolated synthetic development runtime

Observed UTC: 2026-10-10T08:28:56.893160+00:00

## Authority and scope

Owner authorized an isolated NocoBase Community Edition development deployment on DGX. This receipt covers runtime provisioning and initial account authentication only. No collection, schema, business record, workflow, role or UI mutation occurred. No production deployment or external communication was performed.

## Source and command

Loom source revision: `5ed932583ef550edb4446f0b4d9ad7c5f3a470ae`. Provisioner: `scripts/nocobase-fixture.py` in the session-owned Loom checkout. Runtime state is outside Git. The following command uses a placeholder for its private runtime directory:

```sh
python3 scripts/nocobase-fixture.py start --runtime-dir "$ZP_RUNTIME_DIR" --port 18360 --name zp-dev-20261011
```

Resource names, runtime directory and listening port were checked unused before launch. The `seed` action was not run because it bypasses Loom MCP. Fresh generated initialization credentials and a bootstrap token are stored only in private runtime files; token file mode is 0600. No credentials were copied from other fixtures.

## Observed resources

Docker server 29.2.1, accessed using `sudo -n docker`. Images were already cached for ARM64. HTTP is bound to loopback port 18360 only; PostgreSQL has no host published port. Resources carry provisioner ownership labels. Restart policy is `no`; persistent synthetic storage is retained.

| Container | Pinned image | CPU cap | Memory cap | State |
|---|---|---:|---:|---|
| zp-dev-20261011-nb | nocobase/nocobase@sha256:fb57b1b686e808d88624db4726b782316272481eec60a20a380d3c5645a37620 | 2 | 3 GiB | running |
| zp-dev-20261011-db | postgres@sha256:721873c34ceb9f8d8fc265984940dc982404c105f19ad51be9fdc5970a6080ea | 2 | 3 GiB | running |

## Verification and limits

- Provisioner completed successfully: `Synthetic fixture ready; NocoBase 2.2.21` from read-only `app:getInfo`.
- Fresh initialization account sign-in succeeded; token was persisted privately without printing it.
- Docker inspection confirmed both resource caps and running state.
- Total configured limits: 4 CPUs and 6 GiB memory.
- Installed/enabled package inventory, authenticated role permissions, CE feature coverage, Loom MCP catalog, and all application acceptance remain for subsequent qualification. Image/version presence is not capability acceptance.
- No application slice has been generated or accepted by this receipt.

## Ownership handoff

The session coordinator owns these development containers and their lifecycle. Preserve foreign containers and check exact ownership labels before any stop/removal. The fixture provisioner's `stop` action stops its two owned containers while retaining stored data.
