import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


class PlanLeafEvalTests(unittest.TestCase):
    expected = {
        "architecture-preflight": {"architecture-preflight", "return-to-intent", "no-match"},
        "planning-and-task-breakdown": {"ordered-task-breakdown", "checkpoints-and-dependencies", "no-match"},
    }

    def test_each_leaf_has_positive_and_negative_contract_cases(self):
        for name, expected in self.expected.items():
            data = yaml.safe_load((ROOT / name / "evals/cases.yaml").read_text(encoding="utf-8"))
            self.assertEqual(data["skill"], name)
            cases = data["cases"]
            self.assertGreaterEqual(len(cases), 3)
            self.assertEqual({case["expect"] for case in cases}, expected)
            self.assertTrue(any(case["expect"] == "no-match" for case in cases))

    def test_root_covers_complete_capability_scenarios(self):
        data = yaml.safe_load((ROOT / "evals/cases.yaml").read_text(encoding="utf-8"))
        self.assertEqual({case["id"] for case in data["cases"]}, {
            "simple-accepted-intent", "accepted-intent-needs-decomposition",
            "material-architecture-uncertainty", "architecture-plus-decomposition",
            "goal-scope-ambiguity", "canonical-pattern", "light-readiness", "deep-readiness",
        })
        self.assertEqual(data["cases"][3]["expected"], ["architecture-preflight", "planning-and-task-breakdown"])
        modes = {case["id"]: case.get("expected_review_class") for case in data["cases"] if "mode" in case}
        self.assertEqual(modes, {"light-readiness": None, "deep-readiness": "plan_contract"})

    def test_architecture_retrieval_policy_has_selective_triggers(self):
        policy = (ROOT / "architecture-preflight/references/retrieval-policy.md").read_text()
        for signal in ("shared interfaces", "durable state", "trust boundary"):
            self.assertIn(signal, policy)
        self.assertIn("canonical pattern", policy)

    def test_architecture_selector_is_bounded_and_evidence_aware(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("selector", ROOT / "architecture-preflight/scripts/select_references.py")
        module = importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module)
        self.assertEqual(module.select_references([]), [])
        self.assertEqual(module.select_references(["state", "trust", "agent"]), ["data-systems/operations", "threat-modeling"])
        self.assertEqual(module.select_references(["state"], canonical_pattern=True), [])


if __name__ == "__main__":
    unittest.main()
