# Independent migration helper readback review

Date: 2026-10-10. Candidate: `20c20187ca94be68154f5428b7799d711e5524a6`.
Reviewed delta from previously reviewed 0c204e3. Accepted source-only.

Independent DGX command: `python3 -m unittest discover -s scripts -p test_contract_migration.py`: eight passed. Diff check passed.

The helper consumes the qualified Forms.get fields and separately reads the native surface tree for migration history; it no longer assumes an undocumented node field. Exact UID/type, tree identity, owner and config equality are required. Historical old/new pins, review digest, prior config digest and reason must match the reviewed migration. The initial candidate omitted form UID/type checks; review found this and 20c2018 adds them with regression coverage.

Readonly verify uses only observation and writes a new exclusive receipt. It neither opens/rewrites the original uncertain journal nor dispatches a migration. The original apply path retains the single-dispatch journal and CAS gates. This source review does not claim native readback, app acceptance or authority to replay the already committed migration.
