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
                expected = "none" if case.get("expected") == "none" else case["expected"]
                if routing:
                    trace_events = [{"skill_loads": [] if expected == "none" else ["skill-creator"]}]
                    before_snapshot = {}
                    after_snapshot = {}
                else:
                    trace_events = [{"skill_loads": ["skill-creator"], "item": {"type": "command_execution", "command": " ".join(case.get("trace_markers", []))}}]
                    contract = module._artifact_contract(case)
                    if contract.get("operation") == "modified":
                        before_snapshot = {contract["path"]: "old"}
                        after_snapshot = {contract["path"]: "new"}
                    elif contract.get("operation") == "created":
                        before_snapshot = {}
                        after_snapshot = {contract["path"]: "new"}
                    else:
                        before_snapshot = {}
                        after_snapshot = {}
                if "G5_COEXISTENCE" in case.get("gates", [case["gate"]]):
                    for path in module.COEXISTENCE_PATHS[case["id"]]:
                        before_snapshot[path] = "fixture"
                        after_snapshot[path] = "fixture"
                final_report = {"selected_skill": expected} if routing else (
                    {"disposition": expected, "necessity": {"checks": sorted(module.NECESSITY_CHECKS), "disposition": module.EXPECTED_NECESSITY_DISPOSITIONS[case["id"]], "evidence": {check: {"disposition": "USE_EXISTING", "reason": "fixture alternative was compared against the requested reusable capability"} for check in module.NECESSITY_CHECKS}, "justification": "fixture alternatives compared"}}
                    if case["kind"] in {"CREATE", "UPDATE", "MAINTAIN"} else {"disposition": expected}
                )
                changed_paths = sorted(module._changed_paths(before_snapshot, after_snapshot))
                results.append({
                    "case_id": case["id"],
                    "kind": case["kind"],
                    "condition": "with_skill",
                    "expected": case["expected"],
                    "partition": case["partition"],
                    "gate": case["gate"],
                    "gates": case.get("gates", [case["gate"]]),
                    "status": "PASS",
                    "observed": expected,
                    "activation": "unloaded" if expected == "none" else "loaded",
                    "process_observed": not routing,
                    "trace_matches": True,
                    "artifact_ok": True,
                    "necessity_observed": True,
                    "coexistence_fixture": module.COEXISTENCE_PATHS.get(case["id"], set()).issubset(before_snapshot),
                    "changed_paths": changed_paths,
                    "cost_metrics": module._cost_metrics(trace_events, set(changed_paths)),
                    "trace_events": trace_events,
                    "before_snapshot": before_snapshot,
                    "after_snapshot": after_snapshot,
                    "final_report": final_report,
                })
            gates = {gate: "PASS" for gate in module.GATES}
            gates["G7_INDEPENDENT_REVIEW"] = "NOT_ASSESSED"
            baseline_results = []
            paired = []
            for case in cases:
                if case.get("paired") is not True:
                    continue
                contract = module._artifact_contract(case)
                if contract.get("operation") == "modified":
                    baseline_before = {contract["path"]: "old"}
                    baseline_after = {contract["path"]: "new"}
                elif contract.get("operation") == "created":
                    baseline_before = {}
                    baseline_after = {contract["path"]: "new"}
                else:
                    baseline_before = {}
                    baseline_after = {}
                if "G5_COEXISTENCE" in case.get("gates", [case["gate"]]):
                    for path in module.COEXISTENCE_PATHS[case["id"]]:
                        baseline_before[path] = "fixture"
                        baseline_after[path] = "fixture"
                baseline_changed_paths = sorted(module._changed_paths(baseline_before, baseline_after))
                baseline_events = [{"item": {"type": "command_execution", "command": " ".join(case.get("trace_markers", []))}}]
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
                    "activation": None,
                    "process_observed": True,
                    "trace_matches": True,
                    "artifact_ok": True,
                    "necessity_observed": case["kind"] == "EVALUATE",
                    "coexistence_fixture": module.COEXISTENCE_PATHS.get(case["id"], set()).issubset(baseline_before),
                    "changed_paths": baseline_changed_paths,
                    "cost_metrics": module._cost_metrics(baseline_events, set(baseline_changed_paths)),
                    "trace_events": baseline_events,
                    "before_snapshot": baseline_before,
                    "after_snapshot": baseline_after,
                    "final_report": {"disposition": "baseline"},
                }
                baseline_results.append(baseline)
                candidate = next(item for item in results if item["case_id"] == case["id"])
                paired.append({"case_id": case["id"], "with_status": "PASS", "without_status": "OBSERVED", **module._paired_evidence(candidate, baseline)})
            results.extend(baseline_results)
            payload = {
                "coverage": {"full_corpus": True},
                "gates": gates,
                "routing": {"status": "PASS", "TP": 5, "FN": 0, "FP": 0, "TN": 7, "precision": 1.0, "recall": 1.0, "false_positive_rate": 0.0, "assessed_cases": 12, "total_cases": 12},
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
        self.assertEqual(module._artifact_ok(case, before, {"target/SKILL.md": "new", "extra": "changed"})[0], False)

    def test_necessity_and_coexistence_evidence_are_structured(self):
        module = load_module()
        case = {"id": "create-local-upstream", "kind": "CREATE"}
        weak = {"necessity": {"checks": sorted(module.NECESSITY_CHECKS), "evidence": {check: {"disposition": "REJECT", "reason": "x"} for check in module.NECESSITY_CHECKS}, "justification": "x"}}
        self.assertFalse(module._necessity_ok(case, weak)[0])
        strong = {"necessity": {"checks": sorted(module.NECESSITY_CHECKS), "disposition": "CLONE_AND_ADAPT", "evidence": {check: {"disposition": "USE_EXISTING", "reason": "This alternative was compared against the requested reusable capability."} for check in module.NECESSITY_CHECKS}, "justification": "The maintained upstream baseline is the smallest justified owner."}}
        self.assertTrue(module._necessity_ok(case, strong)[0])
        coexistence = {path: "hash" for path in module.COEXISTENCE_PATHS["maintain-overlap"]}
        self.assertFalse(module._recomputed_record({"trace_events": [], "before_snapshot": {".fixture-coexistence": "hash"}, "after_snapshot": {}, "final_report": {}}, {"id": "maintain-overlap", "kind": "MAINTAIN"})["coexistence_fixture"])
        self.assertTrue(module._recomputed_record({"trace_events": [], "before_snapshot": coexistence, "after_snapshot": coexistence, "final_report": {}}, {"id": "maintain-overlap", "kind": "MAINTAIN"})["coexistence_fixture"])

    def test_case_owned_gates_include_declared_additional_gates(self):
        module = load_module()
        result = {"condition": "with_skill", "status": "FAIL", "gates": ["G4_BEHAVIOR", "G6_EFFICIENCY"]}
        self.assertEqual(module._case_gate_status([result], "G6_EFFICIENCY"), "FAIL")
        self.assertEqual(module._case_gate_status([result], "G1_STRUCTURE"), "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
