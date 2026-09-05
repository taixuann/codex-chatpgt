import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("validate_eval_cases.py")


def load_module():
    spec = importlib.util.spec_from_file_location("validate_eval_cases", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EvalContractTests(unittest.TestCase):
    def test_runtime_fixture_uses_repo_skill_discovery_location(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        with module._fixture(skill_dir, True) as fixture:
            self.assertTrue((fixture / ".agents" / "skills" / "skill-creator" / "SKILL.md").is_file())

    def test_repository_case_contract_has_all_gates_and_partitions(self):
        module = load_module()
        self.assertEqual(module.validate(SCRIPT.parents[1] / "evals" / "cases.yaml"), [])

    def test_compare_rejects_missing_before_or_after_evidence(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before = root / "before.json"
            after = root / "after.json"
            before.write_text(json.dumps({"results": []}), encoding="utf-8")
            after.write_text(json.dumps({"results": [{"partition": "held_out", "status": "PASS"}]}), encoding="utf-8")
            self.assertEqual(module._compare(before, after)["status"], "REJECT")

    def test_compare_accepts_non_regressing_held_out_candidate(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before = root / "before.json"
            after = root / "after.json"
            results = [
                {"case_id": "must", "condition": "with_skill", "partition": "must_pass", "status": "PASS"},
                {"case_id": "held", "condition": "with_skill", "partition": "held_out", "status": "PASS"},
                {"case_id": "reg", "condition": "with_skill", "partition": "regression", "status": "PASS"},
            ]
            payload = {"coverage": {"full_corpus": True}, "results": results}
            before.write_text(json.dumps(payload), encoding="utf-8")
            after.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(module._compare(before, after)["status"], "PASS")

    def test_review_flag_without_exact_attestation_stays_unassessed(self):
        module = load_module()
        self.assertEqual(module._independent_review_status("PASS", None, SCRIPT.parents[1]), "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
