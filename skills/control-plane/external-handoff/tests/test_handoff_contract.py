import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ExternalHandoffContractTests(unittest.TestCase):
    def test_handoff_requires_explicit_argv_and_rejects_shell_operators(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("executable plus separate argv tokens", text)
        self.assertIn("Shell operators,", text)
        self.assertIn("are rejected", text)

    def test_handoff_preserves_scope_and_approval_boundaries(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("approval gate before any external write", text)
        self.assertIn("does not execute the external action", text)
        self.assertIn("Never include credentials", text)


if __name__ == "__main__":
    unittest.main()
