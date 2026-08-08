import importlib.util
import tempfile
import unittest
from datetime import date
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_skill_quality.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_skill_quality", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SkillQualityTests(unittest.TestCase):
    def make_skill(self, body="description: A test skill\n"):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name) / "example-skill"
        root.mkdir()
        (root / "SKILL.md").write_text(f"---\nname: example-skill\n{body}---\n# Example\n", encoding="utf-8")
        return temp, root

    def test_compatible_skill_passes_with_advisories(self):
        module = load_module()
        temp, root = self.make_skill()
        self.addCleanup(temp.cleanup)
        report = module.assess(root, date(2026, 7, 27))
        self.assertEqual(report["status"], "warning")
        self.assertEqual({item["gate"] for item in report["results"]}, {"structure", "security", "eval", "staleness"})

    def test_embedded_credential_blocks(self):
        module = load_module()
        temp, root = self.make_skill("description: A test skill\nmetadata:\n  access_token: abcdefghijklmnop\n")
        self.addCleanup(temp.cleanup)
        (root / "config.yaml").write_text("access_token: abcdefghijklmnop\n", encoding="utf-8")
        report = module.assess(root, date(2026, 7, 27))
        self.assertEqual(report["status"], "blocked")
        self.assertTrue(any(item["gate"] == "security" and item["status"] == "fail" for item in report["results"]))

    def test_current_review_and_tests_pass(self):
        module = load_module()
        temp, root = self.make_skill("description: A test skill\nmetadata:\n  last_reviewed: 2026-07-20\n  review_interval_days: 30\n")
        self.addCleanup(temp.cleanup)
        (root / "tests").mkdir()
        (root / "tests" / "test_example.py").write_text("# evidence\n", encoding="utf-8")
        report = module.assess(root, date(2026, 7, 27))
        self.assertEqual(report["status"], "pass")


if __name__ == "__main__":
    unittest.main()
