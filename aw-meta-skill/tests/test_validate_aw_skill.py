import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_aw_skill.py"
spec = importlib.util.spec_from_file_location("validate_aw_skill", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10" role="img"><title>Workflow</title><desc>Steps</desc><text>Start</text></svg>'''
FRONT = '''---\nname: sample-skill\ndescription: Sample workflow skill.\nmetadata:\n  version: "1.0.0"\n  author: "tester"\n  creation_context: "Test fixture."\n---\n'''


class WorkflowLocationTests(unittest.TestCase):
    def make_skill(self, root: Path, *, workflow_path: str) -> Path:
        skill = root / "sample-skill"
        (skill / "docs").mkdir(parents=True)
        (skill / "references").mkdir()
        (skill / "SKILL.md").write_text(
            FRONT + f"[Execution workflow]({workflow_path})\n\n"
            "![Workflow](docs/workflow.svg)\n",
            encoding="utf-8",
        )
        (skill / "docs" / "workflow.svg").write_text(SVG, encoding="utf-8")
        target = skill / workflow_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# Workflow\n\n## Steps\n\n"
            "The workflow.svg is the visual projection.\n",
            encoding="utf-8",
        )
        return skill

    def test_references_workflow_is_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp), workflow_path="references/workflow.md")
            self.assertEqual([], validator.validate(skill))


    def test_legacy_workflow_copy_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp), workflow_path="references/workflow.md")
            (skill / "docs" / "workflow.md").write_text("# Old copy\n", encoding="utf-8")
            errors = validator.validate(skill)
            self.assertTrue(any("docs/workflow.md is obsolete" in error for error in errors))

    def test_docs_workflow_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp), workflow_path="docs/workflow.md")
            errors = validator.validate(skill)
            self.assertTrue(any("references/workflow.md" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
