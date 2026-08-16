import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ops/scripts"))
import validate_feynman_v1 as validator


class FeynmanV1Tests(unittest.TestCase):
    def test_checked_in_behavior_fixture(self):
        validator.validate(ROOT / "ops/scripts/fixtures/feynman-v1.yaml")

    def test_high_fit_does_not_identify_mechanism(self):
        result = validator.evaluate_case({"fit_r2": 0.999, "candidate_mechanisms": ["a", "b"]})
        self.assertEqual(result, {"status": "REQUIRES_ADDITIONAL_MEASUREMENT", "route": "HUMAN"})

    def test_context_gap_routes_to_argus(self):
        self.assertEqual(validator.evaluate_case({"failure": "context_gap"})["route"], "ARGUS")

    def test_packet_qualification_preserves_alternatives_and_abstains(self):
        packet = {
            "context": {"project_manifest": ".agents/manifest.yaml"},
            "evidence": [{"provenance": "result.yaml", "supports": ["mechanism"]}],
            "claim": {"id": "mechanism", "type": "mechanistic", "fit_r2": 0.999},
            "alternatives": ["candidate-a", "candidate-b"],
        }
        self.assertEqual(validator.qualify_packet(packet), {
            "status": "REQUIRES_ADDITIONAL_MEASUREMENT",
            "alternatives_preserved": True,
            "abstained": True,
            "route": "HUMAN",
        })

    def test_packet_qualification_routes_context_gap(self):
        packet = {"context": {}, "evidence": [], "claim": {"id": "c1", "type": "descriptive"}}
        self.assertEqual(validator.qualify_packet(packet)["route"], "ARGUS")


if __name__ == "__main__":
    unittest.main()
