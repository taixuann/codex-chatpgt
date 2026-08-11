import importlib.util
import unittest
from pathlib import Path


VALIDATOR_PATH = (
    Path(__file__).resolve().parents[3]
    / "skills/franky-maintenance/scripts/validate_git_allowlist.py"
)
SPEC = importlib.util.spec_from_file_location("validate_git_allowlist", VALIDATOR_PATH)
assert SPEC and SPEC.loader
validate_git_allowlist = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_git_allowlist)


class GitAllowlistTests(unittest.TestCase):
    def test_canonical_plan_surface_is_narrowly_allowed(self):
        allowed = (
            "plans/PLAN-test.md",
            "plans/PLAN-FRONTEND-SKILL-001-browser-driven-frontend-workbench-20260811.md",
        )
        for path in allowed:
            with self.subTest(path=path):
                self.assertTrue(validate_git_allowlist.is_allowed_path(path))

    def test_noncanonical_plan_paths_are_rejected(self):
        rejected = (
            "plans/foo.md",
            "plans/PLAN-test.json",
            "plans/sub/PLAN-test.md",
            "plans/PLAN-test.exe",
        )
        for path in rejected:
            with self.subTest(path=path):
                self.assertFalse(validate_git_allowlist.is_allowed_path(path))


if __name__ == "__main__":
    unittest.main()
