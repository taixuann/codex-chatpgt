import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]


class IntentLeafEvalTests(unittest.TestCase):
    expected = {
        "interview-me": {"ask-one-question-with-guess", "preserve-issue-locator-and-clarify", "no-match"},
        "idea-refine": {"alternatives-and-assumptions", "preserve-locator-and-refine", "no-match"},
        "define-goal": {"measurable-objective", "preserve-locator-and-define", "no-match"},
    }

    def test_each_leaf_has_source_contrast_and_negative_case(self):
        for name, expected in self.expected.items():
            data = yaml.safe_load((ROOT / name / "evals/cases.yaml").read_text(encoding="utf-8"))
            self.assertEqual(data["skill"], name)
            cases = data["cases"]
            self.assertGreaterEqual(len(cases), 3)
            self.assertEqual({case["expect"] for case in cases}, expected)
            self.assertEqual({case["source"] for case in cases}, {"user", "github_issue"})
            self.assertTrue(any(case["expect"] == "no-match" for case in cases))


if __name__ == "__main__":
    unittest.main()
