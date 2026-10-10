import importlib.util
import os
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("init_project", Path(__file__).resolve().parents[1] / "scripts/init_project.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_init(self, **kwargs):
        return MODULE.initialize(self.root, "ZatiProperty", "docs/rfc/rfc-001.md", **kwargs)

    def test_dry_run(self):
        self.run_init()
        self.assertEqual(list(self.root.iterdir()), [])

    def test_write_idempotent(self):
        self.run_init(write=True)
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(self.run_init(write=True), 0)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_preserves_agents_and_authored_rfc(self):
        original = b"Existing rules\r\n"
        (self.root / "AGENTS.md").write_bytes(original)
        rfc = self.root / "docs/rfc/rfc-001.md"
        rfc.parent.mkdir(parents=True)
        body = b"# Original\r\nKeep this material.\r\n"
        rfc.write_bytes(body)
        self.run_init(write=True, replace_agents=True)
        self.assertEqual((self.root / "AGENTS.md.loom-init.bak").read_bytes(), original)
        self.assertTrue(rfc.read_bytes().endswith(body))

    def test_collision_has_no_partial_writes(self):
        p = self.root / ".agents/skills/zatiproperty-loom/SKILL.md"
        p.parent.mkdir(parents=True)
        p.write_text("Existing skill")
        with self.assertRaises(ValueError):
            self.run_init(write=True)
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.assertEqual(p.read_text(), "Existing skill")

    def test_existing_agents_needs_opt_in(self):
        (self.root / "AGENTS.md").write_text("Existing")
        with self.assertRaises(ValueError):
            self.run_init(write=True)
        self.assertEqual((self.root / "AGENTS.md").read_text(), "Existing")

    def test_backup_collision(self):
        (self.root / "AGENTS.md").write_text("Existing")
        (self.root / "AGENTS.md.loom-init.bak").write_text("Older")
        with self.assertRaises(ValueError):
            self.run_init(write=True, replace_agents=True)
        self.assertEqual((self.root / "AGENTS.md").read_text(), "Existing")

    def test_traversal_absolute_and_overlap(self):
        for rfc in ("../escape.md", "/tmp/escape.md", "AGENTS.md", "AGENTS.md/child", ".agents/skills/zatiproperty-loom/SKILL.md"):
            with self.subTest(rfc=rfc), self.assertRaises(ValueError):
                MODULE.initialize(self.root, "ZatiProperty", rfc, write=True)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "docs").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                self.run_init(write=True)
            self.assertEqual(list(Path(outside).iterdir()), [])
            self.assertFalse((self.root / "AGENTS.md").exists())

    def test_malformed_markers(self):
        p = self.root / "docs/rfc/rfc-001.md"
        p.parent.mkdir(parents=True)
        p.write_text(MODULE.START + "\nbody")
        with self.assertRaises(ValueError):
            self.run_init(write=True)
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_hardlink_destination(self):
        other = self.root / "foreign.md"
        other.write_text("Foreign material")
        os.link(other, self.root / "AGENTS.md")
        with self.assertRaises(ValueError):
            self.run_init(write=True, replace_agents=True)
        self.assertEqual(other.read_text(), "Foreign material")

    def test_project_name_yaml_punctuation(self):
        name = 'Example: "Quoted" # Company'
        MODULE.initialize(self.root, name, "docs/rfc.md", write=True)
        p = self.root / ".agents/skills/example-quoted-company-loom/SKILL.md"
        description = p.read_text().splitlines()[2].removeprefix("description: ")
        self.assertIn(name, json.loads(description))

    def test_control_character_path(self):
        with self.assertRaises(ValueError):
            MODULE.initialize(self.root, "Example", "docs/evil\n.md", write=True)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_reserved_rfc_paths(self):
        for rfc in (".git/config", ".git/config.md", ".agents/policy.md", "docs/.control/rfc.md", "docs/rfc.json"):
            with self.subTest(rfc=rfc), self.assertRaises(ValueError):
                MODULE.initialize(self.root, "Example", rfc, write=True)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_unicode_name(self):
        MODULE.initialize(self.root, "物業管理", "docs/rfc.md", write=True)
        self.assertIn("物業管理", (self.root / "AGENTS.md").read_text())
        self.assertTrue((self.root / ".agents/skills/project-loom/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
