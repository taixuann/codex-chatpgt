import unittest
from pathlib import Path
import sys

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


if __name__ == "__main__":
    unittest.main()
