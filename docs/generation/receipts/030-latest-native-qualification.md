# Latest bounded native qualification

Synthetic NocoBase Community Edition 2.2.21. This receipt refreshes evidence; it does not establish whole E3 acceptance.

Schema-preservation companion 0.1.5 completed one qualified rollback preview. [Observed result](schema015-preview-result.json) records rolledBack=true, fieldAbsent=true, complete exposed baseline unchanged and related metadata unchanged. Baseline digest36cf51dc26ae2df63e699e3ef0a82eb84db31c3c01db6d4ed6da1723cdc65976 and ACL digest4e8d71b6815286e449bc2645ca19d92ca1700d5d6b2df004634247b0044c7d8c are preserved. Both effectiveAclAcceptance and nativeAcceptance remain false. This closes the specific failed-preview metadata-preservation gate from025/029; positive persistent association creation, reload and effective role access remain unqualified. No field was retained by the preview.

Pre-authentication companion0.1.4 has [bounded browser evidence](preauth014-browser.md): delayed real anonymous401 after fast sign-in did not clear the new session; reload retained it; a browser-injected authenticated401 still displayed native feedback and cleared the session. Its [sanitized result](preauth014-browser.json) and screenshot are copied unchanged from the independently recorded Loom evidence. Earlier failed0.1.2/0.1.3 proofs remain historical; this is not universal authentication acceptance.

## Actual bridge and source integration

Read-only process inspection found the active bridge started at2026-10-10T15:24:01.360000Z. Its checkout reflog places HEAD at44cb939432a16ea1c3d4f7afe54db5f9ba32440d at that start, before later documentation-only integration commits. The process configuration points to the reviewed schema015/preauth014 catalog: digest67eca0dff67322253a302e606ffab1e8b08342b8812cb38c52a4fd08d3216a21,256 native tools and25 supplemental tools. The running source is therefore recorded separately from later integrated Git HEAD. No credentials or private endpoints are copied.

Read-only integrated-worktree ref inspection confirms local integration of app957b2c6a9d8fb6aad0825a74cf8a54efd79ce681 and Loom9863d05207a4f2cc65a95da447a3dedacdb73db8. Independent bounded source reviews are app e8d4dc7 and Loom219bcd7. This records local integration, not publication or whole-product acceptance. The document author inspected source/process/catalog records read-only and did not repeat the native preview or browser tests.

Full property/tenancy lifecycle, portal-membership migration, persistent hierarchy authoring and broad RFC delivery remain open. No accounting or consequential financial action is established.
