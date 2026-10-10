# Separate transactional rollback qualification

The positive buildings.units generation is a separate once-only schema mutation.
Its success cannot prove rollback or native cache cleanup.

A reusable Loom companion may expose validateHasMany for read-only preflight;
that cannot exercise transactional cleanup. A separate previewHasMany operation
would be explicitly non-read-only, constructor-only, bounded to the same typed
existing-FK relationship and full ACL CAS. It would invoke the same native field
creation and hooks inside SERIALIZABLE transaction, throw an internal fixed
rollback sentinel after those hooks, and return success only after confirmed
rollback plus absent persisted/native field and unchanged full ACL digest.
No arbitrary fault callback, raw query, checkpoint parameter or plugin code is
accepted. Concurrent permission reads require separate verification.

This proposal is not implemented or authorized for live dispatch by this receipt.
Source/prototype cleanup tests do not establish actual native rollback acceptance.
