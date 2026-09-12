#!/usr/bin/env python3
import copy
import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location("delegation_prompt", "skills/issue-execution/scripts/delegation_prompt.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


CONTRACT = {
    "task_id": "DP-test",
    "objective": "Render one bounded executor request.",
    "authority": {"issue": 107, "owner": "parent"},
    "context": {"repo": "taixuann/codex-chatpgt", "cwd": "/repo"},
    "starting_state": "Candidate commit exists.",
    "target_state": "One deterministic rendered request.",
    "allowed_scope": ["skills/issue-execution/scripts/delegation_prompt.py", "skills/issue-execution/tests/"],
    "forbidden_scope": ["agents/", "skills/harness-worker/"],
    "constraints": ["stdlib only", "do not select the executor"],
    "acceptance": [{"id": "DP-01", "requirement": "Contract is the only semantic authority."}, {"id": "DP-02", "requirement": "Parent supplies the executor."}],
    "validation": ["python -m unittest skills/issue-execution/tests/test_delegation_prompt.py"],
    "return_contract": {"fields": ["status", "changed_files", "validation", "blockers"]},
    "stop_conditions": ["stop on scope conflict", "stop when evidence is unavailable"],
}


class DelegationPromptTests(unittest.TestCase):
    def test_deterministic_and_semantically_complete(self):
        first = MODULE.render(CONTRACT, "agy")
        second = MODULE.render(copy.deepcopy(CONTRACT), "agy")
        self.assertEqual(first, second)
        self.assertEqual([item["id"] for item in first["semantic_manifest"]["acceptance"]["expected"]], ["DP-01", "DP-02"])
        for value in ("delegation_prompt.py", "harness-worker/", "status", "stop on scope conflict"):
            self.assertIn(value, first["prompt"])
        self.assertNotIn("memory", first["prompt"].lower())

    def test_profiles_differ_only_at_executor_presentation(self):
        agy = MODULE.render(CONTRACT, "agy")
        prometheus = MODULE.render(CONTRACT, "prometheus")
        self.assertNotEqual(agy["prompt"], prometheus["prompt"])
        self.assertEqual(agy["semantic_manifest"], prometheus["semantic_manifest"])
        self.assertEqual(agy["renderer"]["source_contract_sha256"], prometheus["renderer"]["source_contract_sha256"])

    def test_identity_is_explicit_baseline(self):
        result = MODULE.render(CONTRACT, "identity")
        self.assertEqual(result["renderer"]["profile"], "identity")

    def test_acceptance_fixture_declares_all_dp_criteria(self):
        import yaml
        criteria = yaml.safe_load(Path("skills/issue-execution/references/delegation-prompt-cases.yaml").read_text())["criteria"]
        self.assertEqual([item["id"] for item in criteria], [f"DP-{index:02d}" for index in range(1, 11)])

    def test_fail_closed_inputs(self):
        with self.assertRaises(ValueError):
            MODULE.render(CONTRACT, "unknown")
        malformed = copy.deepcopy(CONTRACT)
        malformed["memory"] = "do not load"
        with self.assertRaises(ValueError):
            MODULE.render(malformed, "agy")
        malformed = copy.deepcopy(CONTRACT)
        malformed["allowed_scope"] = []
        with self.assertRaises(ValueError):
            MODULE.render(malformed, "agy")
        malformed = copy.deepcopy(CONTRACT)
        malformed.pop("validation")
        with self.assertRaises(ValueError):
            MODULE.render(malformed, "agy")
        malformed = copy.deepcopy(CONTRACT)
        malformed["acceptance"] = [{"id": "DP-01", "requirement": "x"}, {"id": "DP-01", "requirement": "y"}]
        with self.assertRaises(ValueError):
            MODULE.render(malformed, "agy")

    def test_optional_content_is_not_invented(self):
        contract = copy.deepcopy(CONTRACT)
        contract.pop("starting_state")
        contract.pop("forbidden_scope")
        contract.pop("target_state")
        contract.pop("prior_failed_approach", None)
        result = MODULE.render(contract, "prometheus")
        self.assertNotIn("## Target state", result["prompt"])
        self.assertNotIn("## Prior failed approach", result["prompt"])


if __name__ == "__main__":
    unittest.main()
