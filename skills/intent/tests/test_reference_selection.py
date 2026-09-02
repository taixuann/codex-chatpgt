from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReferenceSelectionTests(unittest.TestCase):
    def test_policy_covers_profiles_and_references(self):
        module = load_module("validate_reference_selection", ROOT / "scripts/validate_reference_selection.py")
        policy_path = ROOT / "references/reference-selection.yaml"
        policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
        self.assertEqual(module.validate(policy, policy_path.parent), [])

    def test_expected_trace_is_derived_from_policy(self):
        intentctl = load_module("intentctl_policy", ROOT / "scripts/intentctl.py")
        run = {"profile": "issue_focused", "relationships": [], "stages": {}}
        expected = intentctl.expected_references(run)
        self.assertIn("relationship_audit", expected)
        self.assertIn("issue-audit.md", expected["claim_audit"])

    def test_conformance_harness_reviews_observable_subset_and_marks_native_unassessed(self):
        harness = load_module("run_conformance", ROOT / "evals/run_conformance.py")
        cases = yaml.safe_load((ROOT / "evals/cases.yaml").read_text(encoding="utf-8"))
        observations = yaml.safe_load((ROOT / "evals/conformance.yaml").read_text(encoding="utf-8"))
        policy = yaml.safe_load((ROOT / "references/reference-selection.yaml").read_text(encoding="utf-8"))
        report = harness.run(cases, observations, policy)
        self.assertGreaterEqual(len(report["results"]), 15)
        self.assertTrue(any(item["level"] == "L2_DETERMINISTIC_CONFORMANCE" for item in report["results"]))
        self.assertTrue(any(item.get("result") == "NOT_ASSESSED" for item in report["results"]))
        self.assertTrue(all(item.get("overall", item.get("result")) in {"pass", "NOT_ASSESSED"} for item in report["results"]))

    def test_conformance_catches_missing_observable(self):
        harness = load_module("run_conformance_negative", ROOT / "evals/run_conformance.py")
        case = {"id": "issue_focused_normal", "origin": "github_issue", "depth": "focused", "capability": "issue-intake", "prompt": "check"}
        policy = yaml.safe_load((ROOT / "references/reference-selection.yaml").read_text(encoding="utf-8"))
        result = harness.review(case, {"observed_capability": "issue-intake", "observed_references": list(policy["profiles"]["issue_focused"]), "required_observables": ["handoff"], "observables": []}, policy)
        self.assertEqual(result["overall"], "fail")

    def test_conformance_penalizes_unnecessary_action(self):
        harness = load_module("run_conformance_overaction", ROOT / "evals/run_conformance.py")
        policy = yaml.safe_load((ROOT / "references/reference-selection.yaml").read_text(encoding="utf-8"))
        result = harness.review(
            {"id": "idea_no_external_research", "origin": "user_idea", "depth": "light", "capability": "idea-intake", "prompt": "small"},
            {"observed_capability": "idea-intake", "observed_references": policy["profiles"]["idea_light"], "required_observables": [], "observables": [], "unnecessary_actions": ["external_research"]},
            policy,
        )
        self.assertEqual(result["overall"], "fail")


if __name__ == "__main__":
    unittest.main()
