import importlib.util
import unittest
from pathlib import Path


VALIDATOR_PATH = (
    Path(__file__).resolve().parents[3]
    / "skills/control-plane/control-plane-audit/scripts/validate_git_allowlist.py"
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

    def test_retired_persona_skill_paths_are_rejected(self):
        for path in ("skills/franky-old/SKILL.md", "skills/franky-maintenance/SKILL.md"):
            with self.subTest(path=path):
                self.assertFalse(validate_git_allowlist.is_allowed_path(path))

    def test_session_packets_allow_only_declared_artifacts(self):
        root = "documentation/sessions/20260826_example-work_001/"
        for name in ("session.yaml", "context.md", "plan.md", "task.md", "references.yaml", ".rag/manifest.yaml"):
            with self.subTest(name=name):
                self.assertTrue(validate_git_allowlist.is_allowed_path(root + name))

    def test_session_packets_reject_sensitive_or_unknown_files(self):
        root = "documentation/sessions/20260826_example-work_001/"
        for name in ("credentials.yaml", "token.txt", "config.toml", "notes.txt", ".rag/index.sqlite"):
            with self.subTest(name=name):
                self.assertFalse(validate_git_allowlist.is_allowed_path(root + name))

    def test_session_plan_records_allow_only_canonical_plan_surface(self):
        self.assertTrue(
            validate_git_allowlist.is_allowed_path(
                "documentation/sessions/records/plans/PLAN-ARW-FRANKY-AGENT-FIRST-20260813-001.md"
            )
        )
        rejected = (
            "documentation/sessions/records/plans/README.md",
            "documentation/sessions/records/plans/PLAN-example.yaml",
            "documentation/sessions/records/plans/nested/PLAN-example.md",
            "documentation/sessions/records/reviews/README.md",
            "documentation/sessions/records/reviews/ISSUE-96-REVIEW.json",
            "documentation/sessions/records/reviews/nested/ISSUE-96-REVIEW.yaml",
        )
        for path in rejected:
            with self.subTest(path=path):
                self.assertFalse(validate_git_allowlist.is_allowed_path(path))
        self.assertTrue(
            validate_git_allowlist.is_allowed_path(
                "documentation/sessions/records/reviews/ISSUE-57-ATHENA-REVIEW.yaml"
            )
        )

    def test_session_records_still_reject_sensitive_names(self):
        rejected = (
            "documentation/sessions/records/plans/PLAN-credentials.md",
            "documentation/sessions/records/plans/PLAN-token.md",
            "documentation/sessions/records/reviews/ISSUE-token.yaml",
        )
        for path in rejected:
            with self.subTest(path=path):
                self.assertTrue(validate_git_allowlist.is_sensitive_path(path))
                self.assertFalse(validate_git_allowlist.is_allowed_path(path))


if __name__ == "__main__":
    unittest.main()
