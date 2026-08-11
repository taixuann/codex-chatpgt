import unittest
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "skills" / "control-plane-audit" / "scripts" / "fixtures" / "skill-routing.yaml"
MODULE_PATH = ROOT / "skills" / "control-plane-audit" / "scripts" / "validate_skill_routing.py"
SPEC = importlib.util.spec_from_file_location("validate_skill_routing", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class SkillRoutingFixtureTests(unittest.TestCase):
    def test_static_fixture_covers_required_classes(self):
        skill_count, case_count = MODULE.validate(ROOT, FIXTURE)
        self.assertGreaterEqual(skill_count, 6)
        self.assertGreaterEqual(case_count, 5)


if __name__ == "__main__":
    unittest.main()
