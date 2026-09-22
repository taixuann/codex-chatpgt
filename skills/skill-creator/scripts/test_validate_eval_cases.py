import importlib.util
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("validate_eval_cases.py")
INITIALIZER = Path(__file__).with_name("init_skill.py")


def load_module():
    spec = importlib.util.spec_from_file_location("validate_eval_cases", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_initializer():
    script_dir = str(INITIALIZER.parent)
    sys.path.insert(0, script_dir)
    try:
        spec = importlib.util.spec_from_file_location("init_skill", INITIALIZER)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(script_dir)


class EvalContractTests(unittest.TestCase):
    def test_runtime_fixture_uses_repo_skill_discovery_location(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        with module._fixture(skill_dir, True) as fixture:
            self.assertTrue((fixture / ".agents" / "skills" / "skill-creator" / "SKILL.md").is_file())

    def test_localize_coexistence_marker_is_in_project_fixture(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        case = {"id": "audit-localize", "kind": "AUDIT"}
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

    def test_trial_metadata_binds_identity_and_terminal_cleanup(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        case = {"id": "create-local-upstream", "kind": "CREATE", "paired": True}
        trial = module._trial_metadata(
            skill_dir,
            case,
            "with_skill",
            {"candidate_revision": "a" * 40, "base_identity": "b" * 40, "test_fingerprint": "c" * 64},
        )
        result = module._trial_result({"status": "PASS"}, trial)
        self.assertRegex(result["trial"]["trial_id"], r"^[0-9a-f-]{36}$")
        self.assertEqual(result["trial"]["candidate_fingerprint"]["revision"], "a" * 40)
        self.assertEqual(result["trial"]["base_identity"], "b" * 40)
        self.assertEqual(result["trial"]["test_fingerprint"], "c" * 64)
        self.assertEqual(result["trial"]["lifecycle"]["terminal_state"], "CLEANED")
        self.assertTrue(result["trial"]["lifecycle"]["evidence_frozen"])

    def test_unavailable_preflight_emits_per_case_not_assessed_records(self):
        module = load_module()
        cases_path = SCRIPT.parents[1] / "evals" / "cases.yaml"
        report = module.run(
            cases_path,
            SCRIPT.parents[1],
            "definitely-not-a-codex-runtime",
            "gpt-5.6-luna",
            "medium",
            1,
            None,
            "smoke",
            None,
            None,
        )
        self.assertEqual(report["runtime_preflight"]["status"], "NO_RUNTIME")
        self.assertEqual(len(report["results"]), 3)
        self.assertTrue(all(item["status"] == "NOT_ASSESSED" for item in report["results"]))
        self.assertTrue(all(item["trial"]["lifecycle"]["terminal_state"] == "CLEANED" for item in report["results"]))

    def test_fixture_is_a_nested_git_project_for_runtime_write_boundaries(self):
        module = load_module()
        with module._fixture(SCRIPT.parents[1], True) as fixture:
            self.assertTrue((fixture / ".git").is_dir())

    def test_repository_case_contract_has_all_gates_and_partitions(self):
        module = load_module()
        self.assertEqual(module.validate(SCRIPT.parents[1] / "evals" / "cases.yaml"), [])

    def test_action_contract_covers_four_actions_and_fail_closed_edges(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        cases = module.load_cases(skill_dir / "evals" / "cases.yaml")["action_cases"]
        self.assertEqual({case["action"] for case in cases[:4]}, {"create", "install", "update", "audit"})
        self.assertEqual(cases[4]["expected"], "fail-closed")
        self.assertEqual(cases[5]["expected"], "clarify-or-no-route")
        root = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(all(f"workflows/{action}.md" in root for action in ("create", "install", "update", "audit")))
        self.assertNotRegex(root, r"\bMAINTAIN\b")

    def test_shared_reference_contracts_preserve_operational_semantics(self):
        skill_dir = SCRIPT.parents[1]
        evaluation = (skill_dir / "references" / "evaluation.md").read_text(encoding="utf-8")
        authoring = (skill_dir / "references" / "authoring.md").read_text(encoding="utf-8")
        environment = (skill_dir / "references" / "test-environment.md").read_text(encoding="utf-8")
        architecture = (skill_dir / "references" / "architecture.md").read_text(encoding="utf-8")
        self.assertNotIn("G0_NECESSITY", evaluation)
        for marker in (
            "real-task selection", "portfolio", "outcome correctness", "workflow fidelity",
            "branch/checkpoint coverage", "held-out", "batch-before-repair", "stochastic",
            "persistent or creation-only", "failure classification",
        ):
            self.assertIn(marker, evaluation.lower())
        for marker in ("WHY", "WHEN", "WHAT", "HOW", "BRANCH", "OUTPUT", "RELATED RESOURCES"):
            self.assertIn(marker, authoring)
        for marker in ("RUN", "READ"):
            self.assertIn(marker, authoring)
        for marker in (
            "normal path before exceptions", "decision before enumeration",
            "resource routing by `when`", "consumer/load timing", "flat inventory",
        ):
            self.assertIn(marker, authoring.lower())
        for marker in (
            "ALLOCATE", "PREPARE", "BASELINE", "RUN", "FREEZE EVIDENCE", "REPORT",
            "ARCHIVE", "CLEAN", "CLEANED", "PRESERVED_FOR_REVIEW", "CLEANUP_BLOCKED",
            "temporary copy", "worktree", "sandbox", "candidate revision/tree fingerprint",
            "test/case fingerprint",
        ):
            self.assertIn(marker, environment)
        for marker in ("Phase Contract", "failure", "recovery", "forward trace", "reverse-trace"):
            self.assertIn(marker.lower(), architecture.lower())

    def test_create_install_boundary_and_multimode_case_are_current(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        create = (skill_dir / "workflows" / "create.md").read_text(encoding="utf-8").lower()
        cases = module.load_cases(skill_dir / "evals" / "cases.yaml")
        local_upstream = next(case for case in cases["cases"] if case["id"] == "create-local-upstream")
        self.assertEqual(local_upstream["expected"], "REFERENCE_AND_ADAPT")
        self.assertIn("donor/reference-only", local_upstream["prompt"].lower())
        self.assertIn("not independently installable", local_upstream["prompt"].lower())
        source_strategy = (skill_dir / "references" / "source-strategy.md").read_text(encoding="utf-8").lower()
        self.assertIn("installable owner", source_strategy)
        self.assertIn("donor/reference", source_strategy)
        multimode = next(case for case in cases["cases"] if case["id"] == "create-multimode-one-skill")
        self.assertIn("install", create)
        self.assertIn("donor", create)
        self.assertIn("create, install, update, and audit", multimode["prompt"].lower())
        self.assertIn("evaluate", multimode["prompt"].lower())
        self.assertNotIn("create, update, evaluate, and audit", multimode["prompt"].lower())

    def test_issue_fixture_has_no_unconsumed_duplicate(self):
        module = load_module()
        repo_root = SCRIPT.parents[3]
        tracked = module.subprocess.check_output(
            ["git", "ls-files", "fixtures/issue-121/skill-creator-v2"],
            cwd=repo_root,
            text=True,
        )
        self.assertEqual(tracked, "")

    def test_action_cases_have_a_runtime_workflow_observation_contract(self):
        module = load_module()
        case = {"id": "explicit-create", "kind": "ACTION", "prompt": "Create a reusable skill."}
        prompt = module._runtime_prompt(case, Path("/tmp/eval"))
        self.assertIn("selected_workflow", prompt)
        self.assertEqual(module._artifact_contract(case), {})

    def test_audit_workflow_is_read_only_and_returns_dispositions(self):
        audit = (SCRIPT.parents[1] / "workflows" / "audit.md").read_text(encoding="utf-8")
        self.assertIn("read-only", audit)
        self.assertIn("HEALTHY", audit)
        self.assertIn("BLOCKED", audit)
        self.assertNotIn("execute the selected disposition", audit)

    def test_initializer_omits_unsupported_metadata_by_default(self):
        module = load_initializer()
        with tempfile.TemporaryDirectory() as directory:
            result = module.init_skill("generated-skill", Path(directory), [], False, {})
            self.assertIsNotNone(result)
            self.assertTrue((result / "SKILL.md").is_file())
            self.assertFalse((result / "agents").exists())
        self.assertFalse((SCRIPT.parents[1] / "agents" / "openai.yaml").exists())

    def test_initializer_creates_metadata_only_for_explicit_interface_contract(self):
        module = load_initializer()
        with tempfile.TemporaryDirectory() as directory:
            result = module.init_skill(
                "generated-skill",
                Path(directory),
                [],
                False,
                ["short_description=Generate a reusable skill package"],
            )
            self.assertIsNotNone(result)
            self.assertTrue((result / "agents" / "openai.yaml").is_file())

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
            binding = {
                "version": 1,
                "repository_root": "/tmp/repository",
                "base_head": "0" * 40,
                "candidate_head": "1" * 40,
                "skill_tree_sha256": "a" * 64,
                "cases_sha256": "b" * 64,
            }

            def trial(condition):
                return {
                    "trial_id": str(uuid.UUID(int=next(trial.counter))),
                    "condition": condition,
                    "environment_kind": "temporary_copy",
                    "candidate_fingerprint": {"revision": binding["candidate_head"], "tree_sha256": binding["skill_tree_sha256"]},
                    "test_fingerprint": binding["cases_sha256"],
                    "base_identity": binding["base_head"],
                    "runtime_auth_status": "READY",
                    "lifecycle": {"sequence": module.TRIAL_SEQUENCE, "baseline": "paired_without_skill", "evidence_frozen": True, "terminal_state": "CLEANED"},
                }
            trial.counter = iter(range(1, 1000))
            results = []
            for case in cases:
                routing = case["kind"] == "routing"
                expected = "none" if case.get("expected") == "none" else case["expected"]
                contract = {}
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
                for effect in contract.get("side_effects", []):
                    if effect["operation"] == "deleted":
                        after_snapshot.pop(effect["path"], None)
                final_report = {"selected_skill": expected} if routing else (
                    {"disposition": expected, "necessity": {"disposition": module.EXPECTED_NECESSITY_DISPOSITIONS[case["id"]], "alternatives": {check: {"state": "CHECKED", "disposition": module.EXPECTED_NECESSITY_DISPOSITIONS[case["id"]] if case["kind"] == "CREATE" and check == "maintained_candidate" else "USE_EXISTING", "reason": "fixture alternative was compared against the requested reusable capability", **({"source_role": "DONOR_REFERENCE_ONLY"} if case["kind"] == "CREATE" and check == "maintained_candidate" else {})} for check in module.NECESSITY_CHECKS}, "justification": "fixture alternatives compared"}}
                    if case["kind"] in {"CREATE", "UPDATE", "AUDIT"} else {"disposition": expected}
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
                    "runtime_evidence": {"skill_discovery": "NOT_ASSESSED", "explicit_invocation": "NOT_REQUESTED", "implicit_activation": "unloaded" if expected == "none" else "loaded", "behavior": "OBSERVED"},
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
                    "trial": trial("with_skill"),
                })
            gates = {gate: "PASS" for gate in module.GATES}
            gates["G7_INDEPENDENT_REVIEW"] = "NOT_ASSESSED"
            baseline_results = []
            paired = []
            for case in cases:
                if case.get("paired") is not True:
                    continue
                contract = module._artifact_contract(case, False)
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
                    "runtime_evidence": {"skill_discovery": "NOT_ASSESSED", "explicit_invocation": "NOT_REQUESTED", "implicit_activation": "NOT_ASSESSED", "behavior": "OBSERVED"},
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
                    "trial": trial("without_skill"),
                }
                baseline_results.append(baseline)
                candidate = next(item for item in results if item["case_id"] == case["id"])
                paired.append({"case_id": case["id"], "with_status": "PASS", "without_status": "OBSERVED", **module._paired_evidence(candidate, baseline)})
            results.extend(baseline_results)
            action_cases = module.load_cases(cases_path)["action_cases"]
            action_results = [
                {
                    "case_id": case["id"],
                    "kind": "ACTION",
                    "condition": "with_skill",
                    "expected": case["expected"],
                    "status": "PASS",
                    "observed": case["expected"],
                    "activation": "loaded",
                    "runtime_observed": True,
                    "runtime_evidence": {"skill_discovery": "NOT_ASSESSED", "explicit_invocation": "NOT_REQUESTED", "implicit_activation": "loaded", "behavior": "OBSERVED"},
                    "process_observed": True,
                    "trace_matches": True,
                    "artifact_ok": True,
                    "changed_paths": [],
                    "cost_metrics": {"tool_calls": 1, "command_count": 1, "token_count": None, "tokens_observed": False, "artifact_count": 0},
                    "trace_events": [{"skill_loads": ["skill-creator"], "item": {"type": "command_execution", "command": "skill action probe"}}],
                    "before_snapshot": {},
                    "after_snapshot": {},
                    "final_report": {"selected_workflow": case["expected"]},
                    "trial": trial("with_skill"),
                }
                for case in action_cases
            ]
            payload = {
                "evidence_binding": binding,
                "coverage": {"full_corpus": True},
                "gates": gates,
                "routing": {"status": "PASS", "TP": 5, "FN": 0, "FP": 0, "TN": 7, "precision": 1.0, "recall": 1.0, "false_positive_rate": 0.0, "assessed_cases": 12, "total_cases": 12, "action_status": "PASS", "action_assessed_cases": 6, "action_total_cases": 6, "action_expected_cases": 6},
                "action_cases": action_results,
                "paired": paired,
                "results": results,
            }
            before.write_text(json.dumps(payload), encoding="utf-8")
            after.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "PASS")
            expected_binding = dict(payload["evidence_binding"])
            expected_binding["candidate_head"] = "2" * 40
            self.assertEqual(module._compare(before, after, cases_path, expected_binding)["status"], "REJECT")
            missing_binding = json.loads(json.dumps(payload))
            missing_binding.pop("evidence_binding")
            before.write_text(json.dumps(missing_binding), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            stale_binding = json.loads(json.dumps(payload))
            stale_binding["evidence_binding"]["candidate_head"] = "f" * 40
            before.write_text(json.dumps(stale_binding), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            incomplete = json.loads(json.dumps(payload))
            incomplete["results"][0].pop("activation")
            before.write_text(json.dumps(incomplete), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            missing_trial = json.loads(json.dumps(payload))
            missing_trial["results"][0].pop("trial")
            before.write_text(json.dumps(missing_trial), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            duplicate_trial = json.loads(json.dumps(payload))
            duplicate_trial["action_cases"][0]["trial"]["trial_id"] = duplicate_trial["results"][0]["trial"]["trial_id"]
            before.write_text(json.dumps(duplicate_trial), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            invalid_gate = json.loads(json.dumps(payload))
            invalid_gate["gates"]["G7_INDEPENDENT_REVIEW"] = "PASS"
            before.write_text(json.dumps(invalid_gate), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            missing_pair = json.loads(json.dumps(payload))
            missing_pair["paired"] = []
            before.write_text(json.dumps(missing_pair), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            missing_actions = json.loads(json.dumps(payload))
            missing_actions.pop("action_cases")
            before.write_text(json.dumps(missing_actions), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            missing_action_runtime = json.loads(json.dumps(payload))
            missing_action_runtime["action_cases"][0].pop("trace_events")
            before.write_text(json.dumps(missing_action_runtime), encoding="utf-8")
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
            next(item for item in gate_mismatch["results"] if item["case_id"] == "audit-overlap")["status"] = "FAIL"
            before.write_text(json.dumps(gate_mismatch), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")

    def test_independent_review_is_not_caller_supplied(self):
        self.assertNotIn("--review-status", SCRIPT.read_text(encoding="utf-8"))

    def test_evidence_binding_rejects_candidate_ref_not_at_current_head(self):
        module = load_module()
        root = Path(__file__).resolve().parents[3]
        with patch.object(module, "_git_revision", side_effect=["0" * 40, "1" * 40, "2" * 40]):
            binding = module._evidence_binding(root / "skills" / "skill-creator", root / "skills" / "skill-creator" / "evals" / "cases.yaml", "base", "candidate")
        self.assertIsNone(binding["candidate_head"])
        self.assertFalse(module._valid_evidence_binding(binding))

    def test_evidence_binding_rejects_dirty_candidate_package(self):
        module = load_module()
        root = Path(__file__).resolve().parents[3]
        with patch.object(module, "_git_revision", side_effect=["a" * 40, "a" * 40, "b" * 40]), patch.object(module, "_candidate_worktree_matches", return_value=False):
            binding = module._evidence_binding(root / "skills" / "skill-creator", root / "skills" / "skill-creator" / "evals" / "cases.yaml", "base", "candidate")
        self.assertIsNone(binding["candidate_head"])

    def test_negative_activation_requires_explicit_empty_load_signal(self):
        module = load_module()
        self.assertEqual(module._runtime_activation([{"skill_loads": []}]), "unloaded")
        self.assertIsNone(module._runtime_activation([{"item": {"type": "agent_message", "text": "none"}}]))

    def test_activation_matching_is_exact_and_targeted(self):
        module = load_module()
        self.assertEqual(module._runtime_activation([{"skill_loads": ["skill-creator"]}]), "loaded")
        self.assertEqual(module._runtime_activation([{"skill_loads": [{"name": "skill-creator"}]}]), "loaded")
        self.assertEqual(module._runtime_activation([{"skill_loads": ["not-skill-creator"]}]), "unloaded")
        self.assertEqual(module._runtime_activation([{"loaded_skill": "another-skill"}]), "unloaded")
        self.assertEqual(module._runtime_activation([{"skill_loads": []}, {"skill_loads": ["skill-creator"]}]), "loaded")
        self.assertIsNone(module._runtime_activation([{"skill_loads": ["skill-creator"]}, {"skill_loads": []}]))

    def test_run_requires_revision_binding(self):
        module = load_module()
        original = sys.argv
        try:
            sys.argv = [str(SCRIPT), str(SCRIPT.parent.parent / "evals" / "cases.yaml"), "--run"]
            output = io.StringIO()
            with contextlib.redirect_stdout(output), patch.object(module, "run") as run:
                self.assertEqual(module.main(), 1)
            run.assert_not_called()
            self.assertIn("--run requires both --base and --candidate", output.getvalue())
        finally:
            sys.argv = original

    def test_routing_pass_requires_expected_activation_state(self):
        module = load_module()
        positive = {"kind": "routing", "expected": "skill-creator"}
        negative = {"kind": "routing", "expected": "none"}
        self.assertEqual(module._routing_status(positive, "loaded", "skill-creator")[0], "PASS")
        self.assertEqual(module._routing_status(positive, "unloaded", "skill-creator")[0], "FAIL")
        self.assertEqual(module._routing_status(negative, "unloaded", "none")[0], "PASS")
        self.assertEqual(module._routing_status(negative, "loaded", "none")[0], "FAIL")

    def test_trace_markers_are_bound_to_process_payloads(self):
        module = load_module()
        case = {"trace_markers": ["clone"]}
        self.assertFalse(module._trace_matches(case, [{"item": {"type": "agent_message", "text": "clone"}}]))
        self.assertTrue(module._trace_matches(case, [{"item": {"type": "command_execution", "command": "git clone source"}}]))
        self.assertTrue(module._trace_matches(case, [{"item": {"type": "command_execution", "aggregated_output": "git clone source"}}]))

    def test_runtime_prompt_does_not_leak_case_expected_disposition(self):
        module = load_module()
        case = {
            "id": "create-local-upstream",
            "kind": "CREATE",
            "expected": "CLONE_AND_ADAPT",
            "prompt": "Create the requested reusable local skill.",
            "artifact": "created",
            "artifact_path": ".agents/skills/generated-skill/SKILL.md",
        }
        prompt = module._runtime_prompt(case, Path("/tmp/eval"))
        self.assertNotIn("must be exactly", prompt)
        self.assertNotIn("matching the expected", prompt)
        self.assertEqual(prompt.count(case["expected"]), 1)

    def test_action_dispositions_do_not_use_no_match_state(self):
        module = load_module()
        self.assertNotIn("NO_MATCH", module.ACTION_DISPOSITIONS)
        self.assertIn("NOT_AVAILABLE", module.NECESSITY_STATES)

    def test_json_object_allows_trailing_prose(self):
        module = load_module()
        self.assertEqual(module._json_object('{"disposition":"REJECT"}\nDone.'), {"disposition": "REJECT"})

    def test_snapshot_ignores_runtime_bytecode(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "kept.txt").write_text("kept", encoding="utf-8")
            cache = root / "__pycache__"
            cache.mkdir()
            (cache / "generated.cpython-313.pyc").write_bytes(b"cache")
            snapshot = module._snapshot(root)
            self.assertEqual(set(snapshot), {"kept.txt"})

    def test_snapshot_binds_directories_and_symlink_targets(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "target").mkdir()
            (root / "target" / "file.txt").write_text("one", encoding="utf-8")
            (root / "link").symlink_to("target", target_is_directory=True)
            first = module._snapshot(root)
            (root / "link").unlink()
            (root / "link").symlink_to("other", target_is_directory=True)
            second = module._snapshot(root)
            self.assertIn("@dir/target", first)
            self.assertNotEqual(first["link"], second["link"])

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

    def test_action_probe_failures_are_qualification_failures(self):
        module = load_module()
        cases = [{"id": "explicit-create"}, {"id": "unknown-action"}]
        report = module._routing_metrics(
            [{"case_id": "positive", "status": "PASS", "observed": "skill-creator"}],
            [{"id": "positive", "kind": "routing", "polarity": "positive"}],
            [{"case_id": "explicit-create", "status": "FAIL"}, {"case_id": "unknown-action", "status": "PASS"}],
            cases,
        )
        self.assertEqual(report["action_status"], "FAIL")
        self.assertEqual(report["status"], "FAIL")

    def test_create_source_strategy_branches_are_valid_alternatives(self):
        module = load_module()
        self.assertIn("INSTALL_EXISTING", module.ACTION_DISPOSITIONS)
        self.assertIn("REFERENCE_AND_ADAPT", module.ACTION_DISPOSITIONS)
        alternatives = {
            check: {
                "state": "CHECKED",
                "disposition": "REFERENCE_AND_ADAPT" if check == "maintained_candidate" else "USE_EXISTING",
                "reason": "The candidate was inspected against the requested reusable capability.",
                **({"source_role": "DONOR_REFERENCE_ONLY"} if check == "maintained_candidate" else {}),
            }
            for check in module.NECESSITY_CHECKS
        }
        ok, reason = module._necessity_ok(
            {"id": "create-local-upstream", "kind": "CREATE"},
            {"necessity": {"disposition": "REFERENCE_AND_ADAPT", "alternatives": alternatives, "justification": "The baseline was compared before adaptation."}},
        )
        self.assertTrue(ok, reason)

    def test_create_rejects_installable_maintained_candidate(self):
        module = load_module()
        alternatives = {
            check: {
                "state": "CHECKED",
                "disposition": "INSTALL_EXISTING" if check == "maintained_candidate" else "USE_EXISTING",
                "reason": "The candidate was inspected against the requested reusable capability.",
                **({"source_role": "INSTALLABLE_OWNER"} if check == "maintained_candidate" else {}),
            }
            for check in module.NECESSITY_CHECKS
        }
        ok, reason = module._necessity_ok(
            {"id": "create-local-upstream", "kind": "CREATE"},
            {"necessity": {"disposition": "REFERENCE_AND_ADAPT", "alternatives": alternatives, "justification": "The maintained owner satisfies the requested capability."}},
        )
        self.assertFalse(ok)
        self.assertIn("INSTALL", reason)

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
        weak = {"necessity": {"disposition": "CLONE_AND_ADAPT", "alternatives": {"native": {"state": "CHECKED", "disposition": "REJECT", "reason": "x"}}, "justification": "x"}}
        self.assertFalse(module._necessity_ok(case, weak)[0])
        malformed = {"necessity": {"disposition": {}, "alternatives": {"native": {"state": "NOT_AVAILABLE", "disposition": "REJECT"}}, "justification": "malformed model output"}}
        self.assertFalse(module._necessity_ok(case, malformed)[0])
        strong = {"necessity": {"disposition": "REFERENCE_AND_ADAPT", "alternatives": {"native": {"state": "CHECKED", "disposition": "REJECT", "reason": "Native behavior was inspected and cannot own this reusable workflow."}, "maintained_candidate": {"state": "CHECKED", "disposition": "REFERENCE_AND_ADAPT", "source_role": "DONOR_REFERENCE_ONLY", "reason": "The maintained donor was inspected and is not independently installable."}, "project_or_user_skill": {"state": "NOT_AVAILABLE"}}, "justification": "The donor baseline is the smallest justified reference adaptation."}}
        self.assertTrue(module._necessity_ok(case, strong)[0])
        coexistence = {path: "hash" for path in module.COEXISTENCE_PATHS["audit-overlap"]}
        self.assertFalse(module._recomputed_record({"trace_events": [], "before_snapshot": {".fixture-coexistence": "hash"}, "after_snapshot": {}, "final_report": {}}, {"id": "audit-overlap", "kind": "AUDIT"})["coexistence_fixture"])
        self.assertTrue(module._recomputed_record({"trace_events": [], "before_snapshot": coexistence, "after_snapshot": coexistence, "final_report": {}}, {"id": "audit-overlap", "kind": "AUDIT"})["coexistence_fixture"])

    def test_audit_upstream_drift_uses_update_needed_disposition(self):
        module = load_module()
        case = {"id": "audit-upstream-drift", "kind": "AUDIT"}
        alternatives = {
            name: {
                "state": "CHECKED",
                "disposition": "USE_EXISTING",
                "reason": "checked alternative capability and captured evidence",
            }
            for name in module.NECESSITY_CHECKS
        }
        self.assertTrue(module._necessity_ok(case, {
            "necessity": {
                "disposition": "UPDATE_NEEDED",
                "alternatives": alternatives,
                "justification": "upstream drift requires a later update",
            }
        })[0])

    def test_runtime_preflight_rejects_missing_runtime_without_launching_cases(self):
        module = load_module()
        self.assertEqual(module._runtime_preflight("definitely-not-a-codex-runtime", 1)["status"], "NO_RUNTIME")

    def test_run_rejects_candidate_ref_that_is_not_current_head(self):
        module = load_module()
        cases_path = SCRIPT.parents[1] / "evals" / "cases.yaml"
        report = module.run(
            cases_path,
            SCRIPT.parents[1],
            "definitely-not-a-codex-runtime",
            "gpt-5.6-luna",
            "medium",
            1,
            None,
            "smoke",
            "HEAD",
            "HEAD~1",
        )
        self.assertEqual(report["runtime_preflight"]["status"], "CANDIDATE_MISMATCH")
        self.assertTrue(all(item["status"] == "NOT_ASSESSED" for item in report["results"]))

    def test_trial_record_validation_rejects_missing_lifecycle_evidence(self):
        module = load_module()
        binding = {"candidate_head": "a" * 40, "skill_tree_sha256": "b" * 64, "cases_sha256": "c" * 64, "base_head": "d" * 40}
        item = {"condition": "with_skill"}
        self.assertFalse(module._trial_record_is_valid(item, binding))

    def test_subprocess_env_strips_inherited_git_routing_state(self):
        module = load_module()
        with patch.dict(module.os.environ, {
            "GIT_DIR": "/tmp/redirected-git",
            "GIT_WORK_TREE": "/tmp/redirected-worktree",
            "GIT_CONFIG_GLOBAL": "/tmp/redirected-config",
        }, clear=False):
            environment = module._subprocess_env()
        self.assertNotIn("GIT_DIR", environment)
        self.assertNotIn("GIT_WORK_TREE", environment)
        self.assertNotIn("GIT_CONFIG_GLOBAL", environment)

    def test_timeout_classes_preserve_auth_transport_turn_and_process_causes(self):
        module = load_module()
        self.assertEqual(module._timeout_class("401 unauthorized"), "AUTH_TIMEOUT")
        self.assertEqual(module._timeout_class("websocket stream disconnected"), "TRANSPORT_TIMEOUT")
        self.assertEqual(module._timeout_class("process did not exit"), "PROCESS_TIMEOUT")
        self.assertEqual(module._timeout_class("model turn still running"), "TURN_TIMEOUT")

    def test_case_owned_gates_include_declared_additional_gates(self):
        module = load_module()
        result = {"condition": "with_skill", "status": "FAIL", "gates": ["G4_BEHAVIOR", "G6_EFFICIENCY"]}
        self.assertEqual(module._case_gate_status([result], "G6_EFFICIENCY"), "FAIL")
        self.assertEqual(module._case_gate_status([result], "G1_STRUCTURE"), "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
