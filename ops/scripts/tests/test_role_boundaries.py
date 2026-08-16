import unittest
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ops/scripts"))
import validate_role_boundaries as validator


class RoleBoundaryTests(unittest.TestCase):
    def test_checked_in_authority_and_contracts_pass(self):
        validator.validate()

    def test_canonical_role_set_is_not_expanded(self):
        self.assertEqual(validator.CANONICAL, {"feynman", "prometheus", "franky"})
        self.assertEqual(validator.SUPPORT, {"argus", "athena"})

    def test_canonical_adapters_expose_human_escalation(self):
        for name in validator.CANONICAL:
            with self.subTest(name=name):
                self.assertIn("HUMAN ESCALATION", validator._read_adapter(name))

    def test_feynman_contract_exposes_scientific_v1_sections(self):
        instructions = validator._read_adapter("feynman")
        for section in validator.FEYNMAN_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(section, instructions)

    def test_support_adapter_cannot_be_write_capable(self):
        path = ROOT / "agents/argus.toml"
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        data["sandbox_mode"] = "workspace-write"
        with self.assertRaisesRegex(ValueError, "sandbox_mode=read-only"):
            validator._validate_adapter("argus", data, data["developer_instructions"])

    def test_support_adapter_requires_edit_prohibitions(self):
        path = ROOT / "agents/athena.toml"
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "read-only prohibition"):
            validator._validate_adapter("athena", data, "Independent review only.")


if __name__ == "__main__":
    unittest.main()
