# Independent native ACL denial harness review

Reviewed source: 79897eab5cb467df92c2b30f6f2014ff9049c8ea.
Reviewer: coordinator, independently of coverage-plan author.
DGX command: PYTHONPATH=scripts python3 -m unittest scripts/test_schema_acl_preservation.py.
Result: 16 tests passed.

The new exception is opt-in only for constructor-negative probes and recognizes
the exact observed HTTP403 No permissions packet. It records native-acl
separately from a plugin denial. HTTP401/500, malformed transport, other messages,
extra response fields and stale-digest assertions cannot satisfy that exception.
No permission is modified. Source verification does not prove live rollback.
