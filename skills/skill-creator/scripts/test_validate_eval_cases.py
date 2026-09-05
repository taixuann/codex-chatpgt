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

    def test_localize_coexistence_marker_is_in_project_fixture(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        case = {"id": "maintain-localize", "kind": "MAINTAIN"}
        with module._fixture(skill_dir, True, case) as fixture:
            self.assertFalse((fixture / ".fixture-coexistence").is_file())
            self.assertTrue((fixture / "project" / ".fixture-coexistence").is_file())

    def test_snapshot_excludes_runtime_home(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex-home").mkdir()
            (root / ".codex-home" / "cache").write_text("runtime", encoding="utf-8")
            (root / "artifact.txt").write_text("artifact", encoding="utf-8")
            self.assertEqual(set(module._snapshot(root)), {"artifact.txt"})

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
            cases_path = SCRIPT.parents[1] / "evals" / "cases.yaml"
            cases = module.load_cases(cases_path)["cases"]
            results = []
            for case in cases:
                routing = case["kind"] == "routing"
                results.append({
                    "case_id": case["id"],
                    "kind": case["kind"],
                    "condition": "with_skill",
                    "expected": case["expected"],
                    "partition": case["partition"],
                    "gate": case["gate"],
                    "gates": case.get("gates", [case["gate"]]),
                    "status": "PASS",
                    "observed": "none" if case.get("expected") == "none" else case["expected"],
                    "activation": "unloaded" if case.get("expected") == "none" else "loaded",
                    "process_observed": not routing,
                    "trace_matches": not routing,
                    "artifact_ok": not routing,
                    "changed_paths": [] if routing else [f".evaluation/{case['id']}.json"],
                    "cost_metrics": {"tool_calls": 1, "command_count": 1, "artifact_count": 1},
                })
            gates = {gate: "PASS" for gate in module.GATES}
            gates["G7_INDEPENDENT_REVIEW"] = "NOT_ASSESSED"
            baseline_results = []
            paired = []
            for case in cases:
                if case.get("paired") is not True:
                    continue
                baseline = {
                    "case_id": case["id"],
                    "kind": case["kind"],
                    "condition": "without_skill",
                    "expected": case["expected"],
                    "partition": case["partition"],
                    "gate": case["gate"],
                    "gates": case.get("gates", [case["gate"]]),
                    "status": "OBSERVED",
                    "observed": "baseline",
                    "process_observed": True,
                    "trace_matches": True,
                    "artifact_ok": True,
                    "changed_paths": [f".baseline/{case['id']}.json"],
                    "cost_metrics": {"tool_calls": 1, "command_count": 1, "artifact_count": 1},
                }
                baseline_results.append(baseline)
                candidate = next(item for item in results if item["case_id"] == case["id"])
                paired.append({"case_id": case["id"], "with_status": "PASS", "without_status": "OBSERVED", **module._paired_evidence(candidate, baseline)})
            results.extend(baseline_results)
            payload = {
                "coverage": {"full_corpus": True},
                "gates": gates,
                "routing": {"status": "PASS", "precision": 1.0, "recall": 1.0},
                "paired": paired,
                "results": results,
            }
            before.write_text(json.dumps(payload), encoding="utf-8")
            after.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "PASS")
            incomplete = json.loads(json.dumps(payload))
            incomplete["results"][0].pop("activation")
            before.write_text(json.dumps(incomplete), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            invalid_gate = json.loads(json.dumps(payload))
            invalid_gate["gates"]["G7_INDEPENDENT_REVIEW"] = "PASS"
            before.write_text(json.dumps(invalid_gate), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            missing_pair = json.loads(json.dumps(payload))
            missing_pair["paired"] = []
            before.write_text(json.dumps(missing_pair), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            missing_baseline = json.loads(json.dumps(payload))
            missing_baseline["results"] = [item for item in missing_baseline["results"] if item["condition"] == "with_skill"]
            before.write_text(json.dumps(missing_baseline), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            relabeled = json.loads(json.dumps(payload))
            relabeled["results"][0]["kind"] = "CREATE"
            before.write_text(json.dumps(relabeled), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            gate_mismatch = json.loads(json.dumps(payload))
            next(item for item in gate_mismatch["results"] if item["case_id"] == "maintain-overlap")["status"] = "FAIL"
            before.write_text(json.dumps(gate_mismatch), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")

    def test_independent_review_is_not_caller_supplied(self):
        self.assertNotIn("--review-status", SCRIPT.read_text(encoding="utf-8"))

    def test_negative_activation_requires_explicit_empty_load_signal(self):
        module = load_module()
        self.assertEqual(module._runtime_activation([{"skill_loads": []}]), "unloaded")
        self.assertIsNone(module._runtime_activation([{"item": {"type": "agent_message", "text": "none"}}]))

    def test_trace_markers_are_bound_to_process_payloads(self):
        module = load_module()
        case = {"trace_markers": ["clone"]}
        self.assertFalse(module._trace_matches(case, [{"item": {"type": "agent_message", "text": "clone"}}]))
        self.assertTrue(module._trace_matches(case, [{"item": {"type": "command_execution", "command": "git clone source"}}]))

    def test_routing_metrics_counts_observed_failures(self):
        module = load_module()
        cases = [
            {"id": "positive", "kind": "routing", "polarity": "positive"},
            {"id": "negative", "kind": "routing", "polarity": "negative"},
        ]
        results = [
            {"case_id": "positive", "status": "FAIL", "observed": "none"},
            {"case_id": "negative", "status": "PASS", "observed": "skill-creator"},
        ]
        report = module._routing_metrics(results, cases)
        self.assertEqual(report["FN"], 1)
        self.assertEqual(report["FP"], 1)
        self.assertEqual(report["status"], "FAIL")

    def test_artifact_contract_requires_real_change(self):
        module = load_module()
        case = {"id": "update-bounded", "kind": "UPDATE", "artifact": "modified", "artifact_path": "target/SKILL.md"}
        before = {"target/SKILL.md": "old"}
        self.assertEqual(module._artifact_ok(case, before, before)[0], False)
        self.assertEqual(module._artifact_ok(case, before, {"target/SKILL.md": "new"})[0], True)

    def test_case_owned_gates_include_declared_additional_gates(self):
        module = load_module()
        result = {"condition": "with_skill", "status": "FAIL", "gates": ["G4_BEHAVIOR", "G6_EFFICIENCY"]}
        self.assertEqual(module._case_gate_status([result], "G6_EFFICIENCY"), "FAIL")
        self.assertEqual(module._case_gate_status([result], "G1_STRUCTURE"), "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
