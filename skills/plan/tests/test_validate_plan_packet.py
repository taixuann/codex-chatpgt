import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_plan_packet.py"
SPEC = importlib.util.spec_from_file_location("validate_plan_packet", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class PlanPacketTests(unittest.TestCase):
    def test_valid_packet_can_be_ready_for_build(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        MODULE.validate(data, ready_for_build=True)

    def test_github_issue_source_can_be_ready_for_build(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["source"] = {
            "kind": "github_issue",
            "locator": "taixuann/codex-chatpgt#123",
        }
        MODULE.validate(data, ready_for_build=True)

    def test_cycle_is_rejected(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/invalid-cycle.yaml").read_text())
        with self.assertRaises(ValueError):
            MODULE.validate(data)

    def test_intent_source_requires_confirmation_and_provenance(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["source"]["confirmed"] = False
        with self.assertRaises(ValueError):
            MODULE.validate(data)

    def test_intent_packet_locator_must_be_bounded(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["source"]["locator"] = "does-not-exist.yaml"
        with self.assertRaises(ValueError):
            MODULE.validate(data)

    def test_github_issue_locator_must_be_canonical(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["source"] = {"kind": "github_issue", "locator": "not-an-issue"}
        with self.assertRaises(ValueError):
            MODULE.validate(data)


if __name__ == "__main__":
    unittest.main()
