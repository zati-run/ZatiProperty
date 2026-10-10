# Draft amendment source independent review

Exact 7473b8549b5bd7b13d7074058a646209ad7ef412 independently reviewed. Ten existing form-helper tests and four amendment tests passed on DGX, including actual combined companion policy/prefill normalization with the domain Swagger. The unsupported readback.idPath was corrected to resultIdField and a regression rejects the old shape.

Accepted source-only. The form pins read proposal schema and implementation; uses current revision/version bindings; preserves complete editable party and term proposals; exposes scoped permitted-account choices; and preserves existing currency with explicit integer minor-unit inputs rather than silently converting to USD. Unknown native placement bindings are absent by design: qualification and independent review must precede authoring. Money/date usability, rendered amendment, atomic persisted history and role-denied reads remain live gates.
