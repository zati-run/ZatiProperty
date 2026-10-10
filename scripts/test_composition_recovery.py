import pathlib, tempfile, unittest
from compose_maintenance_pages import compose_once

class Fake:
    def __init__(self, fail=False, occupied=False):
        self.writes=0; self.fail=fail; self.occupied=occupied
    def call(self, name, args):
        if 'compose_' in name:
            self.writes += 1
            if self.fail: raise TimeoutError('ambiguous after native dispatch')
            return {'data': {'created': True}}
        return {'data': {'tree': {'subModels': {'items': [{}] if self.occupied else []}}}}

class Recovery(unittest.TestCase):
    def test_ambiguous_write_is_fenced(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d); c=Fake(fail=True); a={'requestBody': {'target': {'uid': 'owned'}}}
            with self.assertRaises(TimeoutError): compose_once(c,a,p/'receipt',p/'journal')
            with self.assertRaises(RuntimeError): compose_once(c,a,p/'receipt',p/'journal')
            self.assertEqual(c.writes,1)
    def test_occupied_target_never_writes(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d); c=Fake(occupied=True)
            with self.assertRaises(RuntimeError): compose_once(c,{'requestBody': {'target': {'uid': 'owned'}}},p/'receipt',p/'journal')
            self.assertEqual(c.writes,0)
    def test_lost_receipt_still_fenced(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d); c=Fake(); a={'requestBody': {'target': {'uid': 'owned'}}}
            compose_once(c,a,p/'receipt',p/'journal');(p/'receipt').unlink()
            with self.assertRaises(RuntimeError): compose_once(c,a,p/'receipt',p/'journal')
            self.assertEqual(c.writes,1)
if __name__ == '__main__': unittest.main()
