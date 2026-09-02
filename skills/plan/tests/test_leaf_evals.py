import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


class PlanLeafEvalTests(unittest.TestCase):
    expected = {
        "spec-driven-development": {"reviewable-spec", "surface-contradictions", "no-match"},
        "socratic": {"architecture-preflight", "resolve-material-decisions", "no-match"},
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


if __name__ == "__main__":
    unittest.main()
