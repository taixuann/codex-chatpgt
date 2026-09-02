import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_intent_packet.py"
SPEC = importlib.util.spec_from_file_location("validate_intent_packet", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class IntentPacketTests(unittest.TestCase):
    def test_valid_packet_can_be_ready_for_plan(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        MODULE.validate(data, ready_for_plan=True)

    def test_github_issue_source_can_be_ready_for_plan(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/github-issue.yaml").read_text())
        MODULE.validate(data, ready_for_plan=True)

    def test_non_allowed_source_is_rejected(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/invalid-source.yaml").read_text())
        with self.assertRaises(ValueError):
            MODULE.validate(data)

    def test_user_locator_must_be_a_known_reference(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["source"]["locator"] = "arbitrary-text"
        with self.assertRaises(ValueError):
            MODULE.validate(data)

        data["source"]["locator"] = "user-request"
        with self.assertRaises(ValueError):
            MODULE.validate(data)

    def test_github_issue_locator_must_be_canonical(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["source"] = {"kind": "github_issue", "locator": "https://example.com/foo#bar"}
        with self.assertRaises(ValueError):
            MODULE.validate(data)

    def test_obsolete_scenario_and_confidence_fields_are_rejected(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["scenario"] = "define-goal"
        with self.assertRaises(ValueError):
            MODULE.validate(data)
        data.pop("scenario")
        data["confidence"] = 95
        with self.assertRaises(ValueError):
            MODULE.validate(data)


if __name__ == "__main__":
    unittest.main()
