"""Check repository ownership and non-destructive behavior of link cleanup."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class LinkSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name).resolve()
        self.root = base / "repository"
        self.root.mkdir()
        self.script = self.root / "link-skills.py"
        shutil.copyfile(Path(__file__).resolve().parents[1] / "link-skills.py", self.script)
        self.target = base / "installed"
        self.target.mkdir()
        self.skill = self.root / "current"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text("current skill\n")

    def run_script(self, *arguments):
        return subprocess.run(
            [sys.executable, str(self.script), "--target", str(self.target), *arguments],
            capture_output=True, text=True, cwd=self.target.parent,
        )

    def test_default_preserves_stale_links_and_is_idempotent(self):
        stale = self.target / "removed"
        stale.symlink_to(self.root / "removed")
        self.assertEqual(self.run_script().returncode, 0)
        self.assertTrue(stale.is_symlink())
        self.assertEqual((self.target / "current").resolve(), self.skill)
        self.assertEqual(self.run_script().returncode, 0)

    def test_prune_removes_only_owned_first_level_same_name_links(self):
        vanished = self.target / "vanished"
        vanished.symlink_to(self.root / "vanished")
        no_entry = self.root / "no-entry"
        no_entry.mkdir()
        stale = self.target / "no-entry"
        stale.symlink_to(no_entry)
        preserved = {
            "foreign": self.root.parent / "elsewhere" / "foreign",
            "nested": self.root / "nested" / "nested",
            "alias": self.root / "old-name",
        }
        for name, source in preserved.items():
            (self.target / name).symlink_to(source)
        (self.target / "loop").symlink_to(self.target / "loop")
        regular = self.target / "regular"
        regular.write_text("keep me")
        (self.target / "directory").mkdir()
        result = self.run_script("--prune")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(vanished.is_symlink())
        self.assertFalse(stale.is_symlink())
        self.assertTrue(no_entry.is_dir())
        for name in [*preserved, "loop"]:
            self.assertTrue((self.target / name).is_symlink(), name)
        self.assertEqual(regular.read_text(), "keep me")
        self.assertTrue((self.target / "directory").is_dir())
        self.assertEqual((self.target / "current").resolve(), self.skill)
        self.assertEqual(self.run_script("--prune").returncode, 0)

    def test_prune_dry_run_neither_deletes_nor_creates_links(self):
        stale = self.target / "removed"
        stale.symlink_to(self.root / "removed")
        self.assertEqual(self.run_script("--prune", "--dry-run").returncode, 0)
        self.assertTrue(stale.is_symlink())
        self.assertFalse((self.target / "current").exists())
        stale.unlink()
        self.target.rmdir()
        self.assertEqual(self.run_script("--prune", "--dry-run").returncode, 0)
        self.assertFalse(self.target.exists())

    def test_conflicting_foreign_skill_link_is_preserved(self):
        conflicting = self.target / "current"
        foreign = self.root.parent / "elsewhere" / "current"
        conflicting.symlink_to(foreign)
        self.assertEqual(self.run_script("--prune").returncode, 1)
        self.assertEqual(conflicting.readlink(), foreign)


if __name__ == "__main__":
    unittest.main()
