"""Offline fault tests; no runtime endpoint, credentials or app mutations."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/apply_property_tenancy.py'
sys.path.insert(0, str(SCRIPT.parent))
loader = importlib.util.spec_from_file_location('migration', SCRIPT)
migration = importlib.util.module_from_spec(loader)
loader.loader.exec_module(migration)

class Native:
    def __init__(self):
        self.rows = {'existing': {'name':'existing','key':'existing-key','fields':[{'name':'old','key':'old-key','type':'string'}]}}
        self.calls = []
        self.fail_after_write = False
        self.fail_before_write = False
        self.tools = [{'name':x} for x in ['loom_native_collections_get_x','loom_native_collections_list_bx','loom_native_collections_create_x','loom_native_collections_fields_create_x']]
    def call(self,name,args):
        self.calls.append((name,args))
        if 'list_b' in name: return {'data':list(self.rows.values())}
        if 'collections_get_' in name: return {'data':self.rows[args['filterByTk']]}
        if self.fail_before_write: raise OSError('synthetic transport disconnect')
        if 'fields_create_' in name:
            field=dict(args['requestBody'],key='new-key')
            self.rows[args['collectionName']]['fields'].append(field)
        else:
            row=dict(args['requestBody'],key='created-key')
            row['fields']=[dict(f,key='created-'+f['name']) for f in row['fields']]
            self.rows[row['name']]=row
        if self.fail_after_write: raise OSError('synthetic response lost')
        return {'data':{}}

class MigrationFaults(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/'generation/collections').mkdir(parents=True)
        (self.root/'generation/bindings').mkdir()
        self.runtime=self.root/'private'; self.runtime.mkdir()
        self.spec={'collections':[],'addFields':[{'collection':'existing','field':{'name':'new','type':'string'}}]}
        (self.root/'generation/bindings/collections.json').write_text(json.dumps({'existing':{'name':'existing','key':'existing-key'}}))
        self.native=Native()
        self.save()
    def tearDown(self): self.tmp.cleanup()
    def save(self): (self.root/'generation/collections/property-tenancy.json').write_text(json.dumps(self.spec))
    def run_migration(self,*flags):
        output=io.StringIO()
        with patch.object(migration,'ROOT',self.root), patch.object(migration,'Loom',return_value=self.native), patch.dict(os.environ,{'ZP_RUNTIME_DIR':str(self.runtime)}), patch.object(sys,'argv',['migration',*flags]), contextlib.redirect_stdout(output):
            migration.main()
        return output.getvalue()
    def writes(self): return [c for c in self.native.calls if 'create_' in c[0]]
    def test_default_inspection_has_no_writes_or_permission_claims(self):
        self.run_migration()
        self.assertEqual(self.writes(),[])
        self.assertEqual(list(self.runtime.iterdir()),[])
    def test_lost_response_blocks_replay_and_reports_present_without_adoption(self):
        self.native.fail_after_write=True
        with self.assertRaises(OSError): self.run_migration('--apply')
        self.assertEqual(len(self.writes()),1)
        with self.assertRaisesRegex(RuntimeError,'Unresolved intent'): self.run_migration('--apply')
        self.assertEqual(len(self.writes()),1)
        report=self.run_migration('--reconcile')
        self.assertIn('present-matching-unadopted',report)
        self.assertTrue((self.runtime/'property-schema-intent.json').exists())
        self.assertFalse((self.runtime/'property-schema-bindings.json').exists())
        self.assertEqual(len(self.writes()),1)
    def test_prewrite_disconnect_reports_absent_but_does_not_retry(self):
        self.native.fail_before_write=True
        with self.assertRaises(OSError): self.run_migration('--apply')
        self.assertIn('"reconciliation": "absent"',self.run_migration('--reconcile'))
        self.assertEqual(len(self.writes()),1)
        with self.assertRaises(RuntimeError): self.run_migration('--apply')
    def test_conflicting_or_identical_unowned_field_refuses_adoption(self):
        for field_type in ['integer','string']:
            self.native.rows['existing']['fields'].append({'name':'new','type':field_type,'key':'foreign-key'})
            with self.assertRaisesRegex(RuntimeError,'Unowned field collision'): self.run_migration('--apply')
            self.native.rows['existing']['fields'].pop()
        self.assertEqual(self.writes(),[])
    def test_postwrite_metadata_drift_retains_intent(self):
        self.native.fail_after_write=True
        with self.assertRaises(OSError): self.run_migration('--apply')
        self.native.rows['existing']['fields'][-1]['type']='integer'
        with self.assertRaisesRegex(RuntimeError,'Metadata drift'): self.run_migration('--reconcile')
        self.assertTrue((self.runtime/'property-schema-intent.json').exists())
    def test_completed_addition_records_identity_and_is_idempotent(self):
        report=self.run_migration('--apply')
        self.assertIn('"appAcceptance": false',report)
        self.assertFalse((self.runtime/'property-schema-intent.json').exists())
        state=json.loads((self.runtime/'property-schema-bindings.json').read_text())
        self.assertEqual(state['fields']['existing.new'],'new-key')
        self.run_migration('--apply')
        self.assertEqual(len(self.writes()),1)
        self.assertTrue(all('roles' not in name for name,_ in self.native.calls))
    def test_missing_capability_fails_before_any_mutation(self):
        self.native.tools=[t for t in self.native.tools if 'fields_create' not in t['name']]
        with self.assertRaisesRegex(RuntimeError,'capability'): self.run_migration('--apply')
        self.assertEqual(self.writes(),[])
    def test_partial_batch_does_not_skip_missing_field_or_grant_roles(self):
        self.spec['addFields'].append({'collection':'missing','field':{'name':'x','type':'string'}}); self.save()
        with self.assertRaisesRegex(RuntimeError,'Missing base collection'): self.run_migration('--apply')
        self.assertEqual(self.writes(),[])
        self.assertTrue(all('roles' not in name for name,_ in self.native.calls))

if __name__=='__main__': unittest.main()

