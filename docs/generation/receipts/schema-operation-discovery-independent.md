# Independent schema operation discovery review

Source a288508310d59e10c3a45bfbed4c677ba7d6fac7 independently reviewed
by coordinator. DGX PYTHONPATH=scripts python3 -m unittest
scripts/test_schema_acl_preservation.py: 19 tests passed.
Resolution requires a unique observed native alias, exact qualified operation
description and bounded request schema. Ambiguous, wrong-operation and wrong
schema cases reject. It never invents or dispatches a missing operation.

Earlier negative harness execution stopped before create dispatch because its
untruncated name did not match the actual catalog. Subsequent explicit-discovered
native calls verified manager inspect/create denial at HTTP403 and constructor
stale-ACL denial at HTTP409 ACL_BASELINE_CHANGED. Full baseline stayed unchanged.
These negatives do not satisfy the blocked rollback metadata invariant.
