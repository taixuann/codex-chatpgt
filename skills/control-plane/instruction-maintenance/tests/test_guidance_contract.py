from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).parents[1]


class GuidanceContractTests(unittest.TestCase):
    def test_audit_template_declares_scope_and_findings(self) -> None:
        data = yaml.safe_load((ROOT / "templates/guidance-audit.yaml").read_text(encoding="utf-8"))
        self.assertEqual(data["component_type"], "guidance")
        self.assertEqual(data["operation"], "audit_guidance")
        self.assertIn("scope", data["checks"])
        self.assertIsInstance(data["findings"], list)

    def test_skill_requires_precedence_and_approval_boundaries(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("active instruction chain", text)
        self.assertIn("Require explicit approval", text)
        self.assertIn("protected scope", text)


if __name__ == "__main__":
    unittest.main()
