from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "skills" / "harness-worker" / "scripts"
ISSUE_SCRIPTS = ROOT / "skills" / "issue-execution" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import harness_worker as harness_worker  # noqa: E402
sys.path.insert(0, str(ROOT / "skills" / "issue-execution" / "scripts"))
import issue_execution  # noqa: E402
sys.path.insert(0, str(ROOT / "skills" / "athena-review" / "scripts"))
import review  # noqa: E402
from delegation_prompt import render  # noqa: E402

REVIEWER_ID = "22222222-2222-2222-2222-222222222222"


def reviewer_attestation(reviewer_id: str = REVIEWER_ID) -> dict:
    return {"source": "codex_app", "verification": "host_observed_not_assessed", "host_id": "local", "thread_id": reviewer_id, "fresh_context": True, "read_only": True, "producer_transcript": False, "runtime": {"profile": "luna-max", "model": "gpt-5.6-luna", "reasoning_effort": "max", "provider": "openai"}}


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


class KernelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "fixture"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "config", "user.name", "fixture"], check=True)
        (self.repo / "README.md").write_text("fixture\n")
        skill = self.repo / "skills" / "issue-execution"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("fixture skill\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "README.md", "skills"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "base"], check=True)
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.state_dir = self.repo / ".agents" / "sessions" / "issue-107"
        self.fake = self.repo / "fake_runtime.py"
        self.fake.write_text(
            "import json, os, pathlib\n"
            "mode=os.environ.get('MODE','defect')\n"
            "pathlib.Path('result.txt').write_text('fixed\\n' if mode == 'fix' else 'wrong\\n')\n"
            "print(json.dumps({'protocolVersion': 1, 'type': 'result', 'command': 'invoke', 'exitCode': 0, 'data': {'runtime': {'harness':'fake','native_session_id': os.environ.get('NATIVE_ID') or os.environ.get('HEADLESS_SESSION_ID') or 'native-1','actual_model':'fake-model','actual_effort':'low','requested_route':'bounded','actual_route':'balanced','requested_profile':'semantic-balanced','resolved_profile': 'astra-light' if mode == 'athena' else 'fake-balanced','provider':'fake'}, 'execution': {'status':'SUCCESS'}, 'context': {'instruction_fingerprint':'fixture','skill_observation':'BEHAVIOR_OBSERVED'}}}))\n"
        )
        self.sandbox = Path(self.tmp.name) / "sandbox-exec"
        self.sandbox.write_text("#!/bin/sh\n[ \"$1\" = -p ] && shift 2\nexec \"$@\"\n")
        self.sandbox.chmod(0o755)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_commit_history_classifies_checkpoint_policy(self) -> None:
        (self.repo / "result.txt").write_text("one\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "result.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "Implement bounded kernel"], check=True)
        semantic_head = git(self.repo, "rev-parse", "HEAD")
        semantic = issue_execution.classify_commit_history(str(self.repo), self.base, semantic_head)
        self.assertEqual(semantic["status"], "pass")
        self.assertEqual(semantic["commits"][0]["category"], "semantic checkpoint")

        (self.repo / "result.txt").write_text("two\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "result.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "repair verified finding"], check=True)
        repair_head = git(self.repo, "rev-parse", "HEAD")
        repair = issue_execution.classify_commit_history(str(self.repo), self.base, repair_head)
        self.assertEqual(repair["status"], "pass")
        self.assertEqual(repair["commits"][-1]["category"], "repair_checkpoint")

        (self.repo / "result.txt").write_text("three\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "result.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "fix typo"], check=True)
        (self.repo / "result.txt").write_text("four\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "result.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "test parser"], check=True)
        noisy_head = git(self.repo, "rev-parse", "HEAD")
        noisy = issue_execution.classify_commit_history(str(self.repo), self.base, noisy_head)
        self.assertEqual(noisy["status"], "fail")
        self.assertEqual(noisy["violations"][0]["type"], "repeated_history_noise")

    def request(self, mode: str, policy: str = "resume_or_start") -> dict:
        request = {
            "version": 1,
            "request_id": f"issue-107:T1:{mode}",
            "authority": {"repository": "fixture/repo", "issue": 107, "task": "T1"},
            "lane": "execute",
            "repo": {"root": str(self.repo), "cwd": str(self.repo), "worktree": str(self.repo)},
            "scope": {"allowed_paths": ["result.txt"], "mutation_boundary": "fixture"},
            "session": {"policy": policy},
            "permission_policy": "bounded-write",
            "route_requirements": {"semantic_complexity": "bounded", "mutation_risk": "bounded", "context_burden": "low", "validation_strength": "strong", "latency_preference": "normal", "independence_required": True},
            "expected_context": {"required_skills": ["issue-execution"], "instruction_fingerprint_expectation": "fixture"},
            "return_contract": "normalized-runtime-receipt-v1",
            "harness": "fake",
            "session_alias": "fixture:107:T1",
            "command": [sys.executable, str(self.fake)],
            "outputs": {"registry": str(Path(self.tmp.name) / "sessions.json"), "receipt": str(Path(self.tmp.name) / f"receipt-{mode}.yaml")},
            "mode": mode,
        }
        request["expected_context"]["effective_context_fingerprint_expectation"] = issue_execution.effective_context(str(self.repo), str(self.repo), ["issue-execution"])["fingerprint"]
        return request

    def run_request(self, request: dict, mode: str) -> dict:
        path = Path(self.tmp.name) / f"request-{mode}.yaml"
        receipt_path = Path(self.tmp.name) / f"receipt-{mode}.yaml"
        path.write_text(yaml.safe_dump(request))
        env = {**os.environ, "MODE": mode, "HEADLESS_CLI_TEST_ONLY": "1", "HEADLESS_CLI_SANDBOX_EXECUTABLE": str(self.sandbox)}
        result = subprocess.run([sys.executable, str(SCRIPTS / "harness_worker.py"), "run", "--request", str(path), "--registry", str(Path(self.tmp.name) / "sessions.json"), "--receipt", str(receipt_path)], text=True, capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return yaml.safe_load(receipt_path.read_text())

    def run_fault(self, name: str, envelope: str, *, exit_code: int = 1, prelude: str = "") -> tuple[subprocess.CompletedProcess[str], dict, Path]:
        script = self.repo / f"fault-{name}.py"
        script.write_text(prelude + "print(" + repr(envelope) + ")\nimport sys\nsys.exit(" + str(exit_code) + ")\n")
        request = self.request(name)
        request["command"] = [sys.executable, str(script)]
        request_path = Path(self.tmp.name) / f"request-{name}.yaml"
        receipt_path = Path(self.tmp.name) / f"receipt-{name}.yaml"
        request_path.write_text(yaml.safe_dump(request))
        env = {**os.environ, "HEADLESS_CLI_TEST_ONLY": "1", "HEADLESS_CLI_SANDBOX_EXECUTABLE": str(self.sandbox)}
        result = subprocess.run([sys.executable, str(SCRIPTS / "harness_worker.py"), "run", "--request", str(request_path), "--registry", str(Path(self.tmp.name) / "sessions.json"), "--receipt", str(receipt_path)], text=True, capture_output=True, env=env)
        return result, request, receipt_path

    def test_semantic_route_is_normalized_and_explicit_routes_are_supported(self) -> None:
        request = self.request("route")
        self.assertEqual(issue_execution.requested_semantic_route(request), "balanced")
        request["route_requirements"]["semantic_route"] = "strongest"
        issue_execution.validate_request(request)
        self.assertEqual(issue_execution.requested_semantic_route(request), "strongest")
        request["expected_context"]["required_skills"].append("athena-review")
        with self.assertRaisesRegex(ValueError, "native parent sidecar"):
            issue_execution.validate_request(request)

    def test_worker_fallback_is_availability_only(self) -> None:
        for code in ("QUOTA_EXHAUSTED", "RATE_LIMITED", "RUNTIME_UNAVAILABLE", "PROVIDER_UNAVAILABLE"):
            self.assertEqual(issue_execution.select_worker(code), {"requested_worker": "agy", "actual_worker": "agy", "fallback_triggered": True, "fallback_reason": code})
        for code in (None, "TEST_FAILED", "EXECUTION_FAILED", "REVIEW_FINDING"):
            self.assertEqual(issue_execution.select_worker(code), {"requested_worker": "agy", "actual_worker": "agy", "fallback_triggered": False, "fallback_reason": None})
        with self.assertRaisesRegex(ValueError, "worker_route is invalid"):
            issue_execution.validate_worker_route({"requested_worker": "agy", "actual_worker": "agy", "fallback_triggered": False})

    def test_delegation_compiler_prompt_is_consumed_by_worker(self) -> None:
        probe = self.repo / "prompt-probe.py"
        probe.write_text(
            "import json, sys\n"
            "from pathlib import Path\n"
            "Path('rendered.txt').write_text(sys.argv[-1])\n"
            "print(json.dumps({'protocolVersion': 1, 'type': 'result', 'command': 'invoke', 'exitCode': 0, 'data': {'runtime': {'harness': 'fake', 'native_session_id': 'compiled-native', 'actual_model': 'fake-model', 'actual_effort': 'low', 'requested_route': 'balanced', 'actual_route': 'balanced', 'resolved_profile': 'fake-balanced', 'provider': 'fake'}, 'execution': {'status': 'SUCCESS'}}}))\n"
        )
        request = self.request("compiled")
        request["command"] = [sys.executable, str(probe)]
        request["scope"]["allowed_paths"] = ["rendered.txt"]
        request["delegation"] = {
            "executor_profile": "agy",
            "task_contract": {
                "task_id": "compiled-test",
                "objective": "Render this exact objective for the worker.",
                "allowed_scope": ["rendered.txt"],
                "forbidden_scope": [".git/"],
                "constraints": ["write one file only"],
                "acceptance": [{"id": "DP-DISPATCH", "requirement": "worker consumes the rendered prompt"}],
                "validation": ["inspect rendered.txt"],
                "return_contract": {"fields": ["status", "changed_files"]},
                "stop_conditions": ["stop after the edit"],
            },
        }
        rendered = render(request["delegation"]["task_contract"], "agy")
        request["_delegation_prompt"] = rendered["prompt"]
        request["_delegation_binding"] = rendered["renderer"]
        request.pop("delegation")
        receipt = self.run_request(request, "compiled")
        self.assertIn("Render this exact objective for the worker.", (self.repo / "rendered.txt").read_text())
        self.assertEqual(receipt["delegation"]["profile"], "agy")

    def test_production_agy_dispatch_requires_contract(self) -> None:
        request = self.request("missing-delegation")
        request["harness"] = "agy"
        with patch.dict(os.environ, {"HEADLESS_CLI_TEST_ONLY": ""}):
            with self.assertRaisesRegex(ValueError, "DELEGATION_REQUIRED"):
                harness_worker.bind_delegation(request)


    def test_worker_fallback_decision_is_parent_owned(self) -> None:
        request = self.request("fallback")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print", "hello"]
        primary = {"execution": {"error_code": "RUNTIME_UNAVAILABLE"}}
        with patch.object(harness_worker, "_run_once", return_value=primary) as run_once, patch.object(issue_execution, "validate_receipt"):
            result = harness_worker.run(request, Path(self.tmp.name) / "sessions.json", 10)
        self.assertEqual(run_once.call_count, 1)
        self.assertEqual(result["fallback_required"], "prometheus")
        self.assertEqual(result["worker_route"]["actual_worker"], "agy")
        with patch.object(harness_worker, "_run_once", side_effect=ValueError("RUNTIME_UNAVAILABLE before launch")) as run_once:
            result = harness_worker.run(request, Path(self.tmp.name) / "sessions.json", 10)
        self.assertEqual(run_once.call_count, 1)
        self.assertEqual(result["fallback_required"], "prometheus")
        with patch.object(harness_worker, "_run_once", side_effect=ValueError("EXECUTION_PROTOCOL_VIOLATION: malformed")) as run_once:
            with self.assertRaisesRegex(ValueError, "malformed"):
                harness_worker.run(request, Path(self.tmp.name) / "sessions.json", 10)
        self.assertEqual(run_once.call_count, 1)

    def test_native_prometheus_return_contract_has_positive_and_negative_fixtures(self) -> None:
        request = self.request("fallback-role")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print", "hello"]
        issue_execution.validate_request(request)
        raw = {
            "runtime": {"harness": "native-terminal", "requested_route": "balanced", "actual_route": "balanced", "native_session_id": "prometheus-session"},
            "execution": {"status": "SUCCESS", "error_code": None},
            "usage": {},
            "context": {"instruction_fingerprint": None, "skill_observation": "NOT_ASSESSED"},
            "capacity": {"state": "UNKNOWN", "source": "none"},
        }
        receipt = harness_worker.normalize(raw, request, session_state="fresh", exit_code=0, stdout="", stderr="", duration_ms=1, provenance={"kind": "native-terminal", "lane": "prometheus", "executable": "codex"})
        receipt["worker_route"] = {"requested_worker": "agy", "actual_worker": "prometheus", "fallback_triggered": True, "fallback_reason": "RUNTIME_UNAVAILABLE"}
        receipt["native_prometheus_result"] = {"parent_request_id": request["request_id"], "attempt": 1, "fallback_reason": "RUNTIME_UNAVAILABLE", "result_status": "SUCCESS", "changed_paths": [], "validation": {"status": "PASS"}, "authority": request["authority"], "repo": request["repo"], "agy_failure": {"request_id": request["request_id"], "actual_worker": "agy", "error_code": "RUNTIME_UNAVAILABLE", "status": "FAILED"}}
        issue_execution.validate_receipt(request, receipt)
        bad = {**receipt, "native_prometheus_result": {key: value for key, value in receipt["native_prometheus_result"].items() if key != "agy_failure"}}
        with self.assertRaisesRegex(ValueError, "fallback result is incomplete"):
            issue_execution.validate_receipt(request, bad)
        bad = {**receipt, "native_prometheus_result": {**receipt["native_prometheus_result"], "validation": {}}}
        with self.assertRaisesRegex(ValueError, "observed validation"):
            issue_execution.validate_receipt(request, bad)
        bad = {**receipt, "native_prometheus_result": {**receipt["native_prometheus_result"], "repo": {}}}
        with self.assertRaisesRegex(ValueError, "repository binding"):
            issue_execution.validate_receipt(request, bad)
        bad = {**receipt, "native_prometheus_result": {**receipt["native_prometheus_result"], "changed_paths": ["outside.txt"]}}
        with self.assertRaisesRegex(ValueError, "exceed the parent allowed scope"):
            issue_execution.validate_receipt(request, bad)

    def test_native_one_shot_receipt_preserves_unobserved_session(self) -> None:
        request = self.request("agy-receipt")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print", "hello"]
        raw = harness_worker.parse_native_output("plain native output\n", request, 0)
        receipt = harness_worker.normalize(raw, request, session_state="fresh", exit_code=0, stdout="plain native output\n", stderr="", duration_ms=1, provenance={"kind": "native-terminal", "lane": "agy", "executable": "agy"})
        self.assertEqual(receipt["runtime"]["native_session_id"], "NOT_ASSESSED")
        self.assertEqual(receipt["runtime"]["actual_model"], "NOT_ASSESSED")
        issue_execution.validate_receipt(request, receipt)



    def test_agy_empty_failed_conversation_is_a_non_resumable_receipt(self) -> None:
        request = self.request("agy-empty-session")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print", "hello"]
        stream = '{"conversation_id":"","status":"AUTH_REQUIRED","duration_seconds":0.1,"num_turns":0,"usage":{}}\n'
        raw = harness_worker.parse_native_output(stream, request, 0)
        receipt = harness_worker.normalize(raw, request, session_state="fresh", exit_code=0, stdout=stream, stderr="", duration_ms=1, provenance={"kind": "native-terminal", "lane": "agy", "executable": "agy"})
        self.assertEqual(receipt["runtime"]["native_session_id"], "NOT_ASSESSED")
        self.assertEqual(receipt["execution"]["status"], "FAILED")
        self.assertEqual(receipt["execution"]["error_code"], "AUTH_REQUIRED")
        issue_execution.validate_receipt(request, receipt)






    def test_resume_rebinds_when_effective_cwd_instruction_chain_drifts(self) -> None:
        nested = self.repo / "nested"
        nested.mkdir()
        (self.repo / "AGENTS.md").write_text("root instructions\n")
        (nested / "AGENTS.md").write_text("nested instructions\n")
        skill = self.repo / "skills" / "issue-execution"
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text("fixture skill\n")
        root_context = issue_execution.effective_context(str(self.repo), str(self.repo), ["issue-execution"])
        nested_context = issue_execution.effective_context(str(self.repo), str(nested), ["issue-execution"])
        self.assertNotEqual(root_context["fingerprint"], nested_context["fingerprint"])
        with self.assertRaisesRegex(ValueError, "required skills unavailable"):
            issue_execution.effective_context(str(self.repo), str(self.repo), ["missing-skill"])
        request = self.request("context-root")
        registry = Path(self.tmp.name) / "context-sessions.json"
        request["outputs"]["registry"] = str(registry)
        with patch.dict(os.environ, {"HEADLESS_CLI_SANDBOX_EXECUTABLE": str(self.sandbox), "HEADLESS_CLI_TEST_ONLY": "1", "MODE": "context-root"}):
            harness_worker.run(request, registry, 10)
            drifted = self.request("context-nested", "resume")
            drifted["repo"]["cwd"] = str(nested)
            drifted["scope"]["allowed_paths"] = ["nested/result.txt"]
            drifted["outputs"]["registry"] = str(registry)
            with self.assertRaisesRegex(ValueError, "SESSION_CONTEXT_MISMATCH: cwd"):
                harness_worker.run(drifted, registry, 10)



    def test_golden_repair_changes_head_and_requires_fresh_review(self) -> None:
        first = self.run_request(self.request("defect"), "defect")
        issue_execution.validate_receipt(self.request("defect"), first)
        subprocess.run(["git", "-C", str(self.repo), "add", "result.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "candidate A"], check=True)
        candidate_a = git(self.repo, "rev-parse", "HEAD")
        manifest = [{"id": "AC-1"}]
        packet_a = {"authority": {"repository": "fixture/repo", "issue": 107}, "base": {"ref": "main", "head": self.base}, "candidate": {"head": candidate_a, "changed_files": ["result.txt"]}, "criteria": [{"id": "AC-1", "status": "partial", "evidence": "wrong output"}], "criteria_manifest": manifest, "criteria_revision": "fixture-r1", "criteria_manifest_fingerprint": review.fp(manifest), "changed_files": ["result.txt"], "validation": {"tests": "pass"}, "evidence": {"receipt": first}, "supporting_documents": [{"path": "", "disposition": "NOT_APPLICABLE", "reason": "fixture has no supporting-document impact"}], "repo_binding": issue_execution.repository_binding(str(self.repo)), "workspace_fingerprint": issue_execution.workspace_fingerprint(str(self.repo))}
        packet_a["review_attempt"] = {"axis": "joint", "round": 1}
        result_a = review.normalize(packet_a, {"fresh_context": True, "read_only": True, "reviewer_session_id": "NOT_ASSESSED", "criteria_review": [{"id": "AC-1", "status": "partial", "evidence": "reviewed wrong output"}], "findings": [{"category": "correctness", "file": "result.txt", "line": 1, "summary": "wrong output", "severity": "major", "evidence_state": "verified"}]}, reviewer_session_id=REVIEWER_ID, reviewer_attestation=reviewer_attestation())
        self.assertEqual(result_a["work_review"]["status"], "fail")
        self.assertEqual(result_a["goal_review"]["status"], "partial")
        self.assertEqual(first["runtime"]["native_session_id"], "native-1")
        self.assertEqual(packet_a["candidate"]["head"], candidate_a)
        second = self.run_request(self.request("fix", "resume"), "fix")
        subprocess.run(["git", "-C", str(self.repo), "add", "result.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "candidate B"], check=True)
        candidate_b = git(self.repo, "rev-parse", "HEAD")
        self.assertNotEqual(candidate_a, candidate_b)
        self.assertFalse(issue_execution.review_current(result_a, candidate=candidate_b, base_ref="main", base_head=self.base, criteria_fp=result_a["snapshot"]["criteria_fingerprint"], rubric_ref=result_a["snapshot"]["rubric_ref"], authority_fp=result_a["snapshot"]["authority_fingerprint"], workspace_fp=result_a["snapshot"]["workspace_fingerprint"], evidence_fp=result_a["snapshot"]["evidence_fingerprint"], validation_fp=result_a["snapshot"]["validation_fingerprint"], supporting_documents_fp=result_a["snapshot"]["supporting_documents_fingerprint"], changed_files_fp=result_a["snapshot"]["changed_files_fingerprint"]))
        packet_b = {**packet_a, "candidate": {"head": candidate_b, "changed_files": ["result.txt"]}, "criteria": [{"id": "AC-1", "status": "fulfilled", "evidence": "fixed output"}], "evidence": {"receipt": second}}
        result_b = review.normalize(packet_b, {"fresh_context": True, "read_only": True, "reviewer_session_id": "NOT_ASSESSED", "criteria_review": [{"id": "AC-1", "status": "fulfilled", "evidence": "reviewed fixed output"}], "findings": []}, reviewer_session_id=REVIEWER_ID, reviewer_attestation=reviewer_attestation())
        self.assertEqual(result_b["work_review"]["status"], "pass")
        self.assertEqual(result_b["goal_review"]["status"], "complete")
        self.assertEqual(result_b["recommendation"], "not_assessed")
        issue_execution.validate_receipt(self.request("fix", "resume"), second)

    def test_receipt_and_ledger_fail_closed(self) -> None:
        receipt = self.run_request(self.request("defect"), "defect")
        bad = dict(receipt); bad["accepted_head"] = "fake"
        with self.assertRaises(ValueError):
            issue_execution.validate_receipt(self.request("defect"), bad)
        bad_worktree = dict(receipt); bad_worktree["execution"] = {**receipt["execution"], "worktree": str(self.repo.parent)}
        with self.assertRaises(ValueError):
            issue_execution.validate_receipt(self.request("defect"), bad_worktree)
        bad_exit = dict(receipt); bad_exit["execution"] = {key: value for key, value in receipt["execution"].items() if key != "exit_code"}
        with self.assertRaises(ValueError):
            issue_execution.validate_receipt(self.request("defect"), bad_exit)
        missing_runtime = dict(receipt); missing_runtime["runtime"] = {**receipt["runtime"], "provider": None}
        with self.assertRaisesRegex(ValueError, "cannot be null"):
            issue_execution.validate_receipt(self.request("defect"), missing_runtime)
        bad_status_exit = dict(receipt); bad_status_exit["execution"] = {**receipt["execution"], "exit_code": 1}
        with self.assertRaisesRegex(ValueError, "exit_code 0"):
            issue_execution.validate_receipt(self.request("defect"), bad_status_exit)
        sparse = {"version": 1, "request_id": self.request("defect")["request_id"], "runtime": {"harness": "fake", "native_session_id": "native-1"}, "execution": {"repo_root": str(self.repo), "cwd": str(self.repo), "worktree": str(self.repo), "status": "SUCCESS", "exit_code": 0}}
        with self.assertRaises(ValueError):
            issue_execution.validate_receipt(self.request("defect"), sparse)
        malformed_section = dict(receipt); malformed_section["runtime"] = []
        with self.assertRaisesRegex(ValueError, "sections must be mappings"):
            issue_execution.validate_receipt(self.request("defect"), malformed_section)
        (self.repo / "result.txt").write_text("changed\n")
        ledger = {"allowed_paths": ["result.txt"], "files": []}
        with self.assertRaises(ValueError):
            issue_execution.reconcile(str(self.repo), self.base, ledger)

    def test_successful_receipt_rejects_non_resumable_native_id(self) -> None:
        request = self.request("sentinel-success")
        receipt = self.run_request(request, "sentinel-success")
        receipt["runtime"]["native_session_id"] = "NOT_ASSESSED"
        with self.assertRaises(ValueError):
            issue_execution.validate_receipt(request, receipt)

    def test_baseline_fingerprint_is_required_and_bound(self) -> None:
        baseline = issue_execution.baseline(str(self.repo))
        issue_execution.validate_baseline_record(baseline)
        baseline["status"] = [" M changed.txt"]
        with self.assertRaises(ValueError):
            issue_execution.validate_baseline_record(baseline)

    def test_output_writers_reject_hardlinks(self) -> None:
        source = Path(self.tmp.name) / "source.yaml"
        target = Path(self.tmp.name) / "target.yaml"
        source.write_text("source\n")
        os.link(source, target)
        with self.assertRaises(ValueError):
            issue_execution.dump_document(target, {"status": "unsafe"})


    def test_ledger_is_bound_to_the_trusted_issue_authority(self) -> None:
        ledger = {"repository": "fixture/repo", "issue": 999, "criteria": [{"id": "AC-1"}], "tasks": [{"id": "T1", "objective": "bounded", "status": "done", "dependencies": [], "criteria": ["AC-1"]}], "files": [], "supporting_documents": [{"disposition": "NOT_APPLICABLE", "reason": "none"}]}
        with self.assertRaisesRegex(ValueError, "Issue does not match"):
            issue_execution.validate_ledger(ledger, expected_repository="fixture/repo", expected_issue=107)

    def test_ignored_lifecycle_state_is_not_issue_changed_file(self) -> None:
        ignore = self.repo / ".gitignore"
        ignore.write_text(".agents/sessions/\n")
        subprocess.run(["git", "-C", str(self.repo), "add", ".gitignore"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "ignore lifecycle state"], check=True)
        base = git(self.repo, "rev-parse", "HEAD")
        lifecycle = self.repo / ".agents" / "sessions" / "issue-107"
        lifecycle.mkdir(parents=True)
        (lifecycle / "session.yaml").write_text("status: ready\n")
        self.assertNotIn(".agents/sessions/issue-107/session.yaml", issue_execution.changed_files(str(self.repo), base))
        self.assertNotIn(".git/config", issue_execution.workspace_manifest(str(self.repo)))

    def test_hygiene_oracle_checks_git_and_named_scratch_surfaces(self) -> None:
        subprocess.run(["git", "-C", str(self.repo), "add", "fake_runtime.py"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "fixture runtime"], check=True)
        git_probe = self.repo / "git-leak.txt"
        git_probe.write_text("leak\n")
        scratch = Path(self.tmp.name) / "runtime-scratch"
        scratch.mkdir()
        probe = scratch / "leak.txt"
        probe.write_text("leak\n")
        dirty = issue_execution.hygiene_snapshot(str(self.repo), [str(probe)])
        self.assertFalse(dirty["git_clean"])
        self.assertFalse(dirty["scratch_clean"])
        self.assertFalse(dirty["clean"])
        probe.unlink()
        git_probe.unlink()
        clean = issue_execution.hygiene_snapshot(str(self.repo), [str(probe)])
        self.assertTrue(clean["git_clean"])
        self.assertTrue(clean["scratch_clean"])
        self.assertTrue(clean["clean"])


    def test_capacity_taxonomy_rejects_unknown_states(self) -> None:
        request = self.request("capacity")
        receipt = self.run_request(request, "capacity")
        invalid = {**receipt, "capacity": {**receipt["capacity"], "state": "MODEL_UNAVAILABLE"}}
        with self.assertRaises(ValueError):
            issue_execution.validate_receipt(request, invalid)
        invalid = {**receipt, "capacity": {"state": "AVAILABLE", "source": "none"}}
        with self.assertRaises(ValueError):
            issue_execution.validate_receipt(request, invalid)
        invalid = {**receipt, "execution": {**receipt["execution"], "status": "FAILED", "error_code": "NOT_A_REAL_ERROR"}}
        with self.assertRaises(ValueError):
            issue_execution.validate_receipt(request, invalid)

    def test_fault_taxonomy_uses_real_subprocess_boundary(self) -> None:
        base_runtime = {"harness": "fake", "native_session_id": "native-fault", "actual_model": "fake-model", "actual_effort": "low", "requested_route": "balanced", "actual_route": "balanced", "provider": "fake"}
        for name, status, error_code in (("auth", "AUTH_REQUIRED", "AUTH_REQUIRED"), ("quota", "FAILED", "QUOTA_EXHAUSTED"), ("rate", "FAILED", "RATE_LIMITED"), ("permission", "FAILED", "PERMISSION_DENIED")):
            envelope = json.dumps({"protocolVersion": 1, "type": "result", "command": "invoke", "exitCode": 1, "data": {"runtime": base_runtime, "execution": {"status": status, "error_code": error_code}, "context": {"instruction_fingerprint": "fixture", "skill_observation": "NOT_ASSESSED"}}})
            result, request, receipt_path = self.run_fault(name, envelope)
            self.assertEqual(result.returncode, 0, result.stderr)
            issue_execution.validate_receipt(request, yaml.safe_load(receipt_path.read_text()))

        malformed, _, _ = self.run_fault("malformed", "not-json")
        self.assertNotEqual(malformed.returncode, 0)
        self.assertIn("EXECUTION_PROTOCOL_VIOLATION", malformed.stderr)

        oversized, _, _ = self.run_fault("oversized", "x" * (harness_worker.MAX_OUTPUT_BYTES + 1), exit_code=0)
        self.assertNotEqual(oversized.returncode, 0)
        self.assertIn("output exceeded", oversized.stderr)

        missing_model_runtime = {key: value for key, value in base_runtime.items() if key != "actual_model"}
        missing_model = json.dumps({"protocolVersion": 1, "type": "result", "command": "invoke", "exitCode": 0, "data": {"runtime": missing_model_runtime, "execution": {"status": "SUCCESS"}, "context": {"instruction_fingerprint": "fixture", "skill_observation": "NOT_ASSESSED"}}})
        no_model, _, _ = self.run_fault("missing-model", missing_model, exit_code=0)
        self.assertEqual(no_model.returncode, 0, no_model.stderr)
        self.assertEqual(yaml.safe_load((Path(self.tmp.name) / "receipt-missing-model.yaml").read_text())["runtime"]["actual_model"], "NOT_ASSESSED")

        crashed, request, receipt_path = self.run_fault("mutation-crash", json.dumps({"protocolVersion": 1, "type": "result", "command": "invoke", "exitCode": 1, "data": {"runtime": base_runtime, "execution": {"status": "FAILED", "error_code": "EXECUTION_FAILED"}, "context": {"instruction_fingerprint": "fixture", "skill_observation": "NOT_ASSESSED"}}}), prelude="from pathlib import Path\nPath('result.txt').write_text('partial\\n')\n")
        self.assertEqual(crashed.returncode, 0, crashed.stderr)
        issue_execution.validate_receipt(request, yaml.safe_load(receipt_path.read_text()))
        self.assertEqual((self.repo / "result.txt").read_text(), "partial\n")








    def test_file_allowances_do_not_match_descendants(self) -> None:
        self.assertTrue(issue_execution.path_matches_allowance("result.txt", ["result.txt"], str(self.repo)))
        self.assertFalse(issue_execution.path_matches_allowance("result.txt/child", ["result.txt"], str(self.repo)))
        self.assertTrue(issue_execution.path_matches_allowance("nested/child", ["nested/"], str(self.repo)))

    def test_ledger_rejects_cycles_and_unmapped_criteria(self) -> None:
        ledger = {"criteria": [{"id": "AC-1"}, {"id": "AC-2"}], "tasks": [{"id": "T1", "objective": "one", "status": "done", "dependencies": ["T2"], "criteria": ["AC-1"]}, {"id": "T2", "objective": "two", "status": "done", "dependencies": ["T1"], "criteria": ["AC-2"]}], "files": [], "supporting_documents": [{"disposition": "NOT_APPLICABLE", "reason": "none"}]}
        with self.assertRaises(ValueError):
            issue_execution.validate_ledger(ledger)
        ledger["tasks"][0]["dependencies"] = []
        ledger["tasks"][1]["criteria"] = ["AC-1"]
        with self.assertRaises(ValueError):
            issue_execution.validate_ledger(ledger)

    def test_task_execution_pointer_is_compact_and_route_bound(self) -> None:
        ledger = {"repository": "fixture/repo", "issue": 107, "criteria": [{"id": "AC-1"}], "tasks": [{"id": "T1", "objective": "one", "status": "done", "dependencies": [], "criteria": ["AC-1"]}], "files": [], "supporting_documents": [{"disposition": "NOT_APPLICABLE", "reason": "none"}]}
        execution = {"actor": "agy", "primitive": "harness", "display_label": "AGY | I107:T1 | execute | a1", "attempt": 1, "receipt": "/tmp/agy-receipt.yaml", "result": "success", "validation": "pass"}
        recorded = issue_execution.record_task_execution(ledger, "T1", execution)
        issue_execution.validate_ledger(recorded, expected_repository="fixture/repo", expected_issue=107)
        self.assertEqual(recorded["tasks"][0]["executions"], [execution])
        fallback = {"actor": "prometheus", "primitive": "subagent", "display_label": "Prometheus | I107:T1 | fallback | a1", "attempt": 1, "receipt": "/tmp/prometheus-receipt.yaml", "result": "success", "validation": "pass"}
        recorded = issue_execution.record_task_execution(recorded, "T1", fallback)
        self.assertEqual(recorded["tasks"][0]["executions"], [execution, fallback])
        with self.assertRaisesRegex(ValueError, "invalid"):
            issue_execution.record_task_execution(ledger, "T1", {**execution, "primitive": "subagent"})
        with self.assertRaises(ValueError):
            issue_execution.validate_ledger({**recorded, "tasks": [{**recorded["tasks"][0], "executions": [{**execution, "prompt": "secret"}]}]})

    def test_bounded_write_rejects_profile_syntax_in_allowed_path(self) -> None:
        request = self.request("defect")
        request["scope"]["allowed_paths"] = ['bad"path.txt']
        with self.assertRaises(ValueError):
            issue_execution.validate_request(request)

    def test_bounded_write_rejects_repository_root_allowance(self) -> None:
        request = self.request("defect")
        for root_allowance in (".", "./", ".//"):
            request["scope"]["allowed_paths"] = [root_allowance]
            with self.assertRaises(ValueError):
                issue_execution.validate_request(request)
            with patch.object(harness_worker.sys, "platform", "darwin"):
                with self.assertRaises(ValueError):
                    harness_worker.sandbox_command(["echo", "ok"], request)
            self.assertFalse(issue_execution.path_matches_allowance("any/file", [root_allowance], str(self.repo)))

    def test_bounded_write_rejects_git_metadata_allowance(self) -> None:
        for path in (".git/HEAD", "nested/.git/config"):
            request = self.request("git-metadata")
            request["scope"]["allowed_paths"] = [path]
            with self.assertRaisesRegex(ValueError, "cannot include .git metadata"):
                issue_execution.validate_request(request)
            with patch.object(harness_worker.sys, "platform", "darwin"):
                with self.assertRaisesRegex(ValueError, "cannot target .git metadata"):
                    harness_worker.sandbox_command(["echo", "ok"], request)

    def test_bounded_write_rejects_profile_syntax_in_repo_paths(self) -> None:
        for key in ("root", "cwd", "worktree"):
            request = self.request("defect")
            request["repo"][key] = f'{self.repo}"bad'
            with self.assertRaises(ValueError):
                issue_execution.validate_request(request)

    def test_bounded_write_rejects_symlinked_allowed_target(self) -> None:
        target = self.repo / "target"
        target.mkdir()
        (self.repo / "link").symlink_to(target, target_is_directory=True)
        request = self.request("defect")
        request["scope"]["allowed_paths"] = ["link/out.txt"]
        with patch.object(harness_worker.sys, "platform", "darwin"):
            with self.assertRaises(ValueError):
                harness_worker.sandbox_command(["echo", "ok"], request)

    def test_runtime_write_root_rejects_symlinked_parent(self) -> None:
        parent = Path(self.tmp.name) / "runtime-parent"
        target = Path(self.tmp.name) / "runtime-target"
        target.mkdir()
        parent.symlink_to(target, target_is_directory=True)
        request = self.request("runtime-root")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print"]
        with patch.dict(os.environ, {"HEADLESS_CLI_RUNTIME_WRITE_ROOTS": str(parent)}):
            with self.assertRaises(ValueError):
                harness_worker.runtime_write_roots(request)


    def test_linked_worktree_evidence_excludes_git_file(self) -> None:
        linked = Path(self.tmp.name) / "linked-worktree"
        subprocess.run(["git", "-C", str(self.repo), "worktree", "add", "--detach", "-q", str(linked), self.base], check=True)
        try:
            self.assertNotIn(".git", issue_execution.workspace_manifest(str(linked)))
        finally:
            subprocess.run(["git", "-C", str(self.repo), "worktree", "remove", "--force", str(linked)], check=True)

    def test_malformed_repo_request_fails_as_value_error(self) -> None:
        request = self.request("malformed-repo")
        request["repo"] = []
        with self.assertRaisesRegex(ValueError, "repo must be a mapping"):
            issue_execution.validate_request(request)

    def test_baseline_untracked_directory_path_is_normalized(self) -> None:
        current = {"repo_root": issue_execution.canonical(str(self.repo)), "head": self.base, "branch": "main", "status": ["?? dir/"], "status_records": [{"xy": "??", "path": "dir/"}], "workspace_manifest": {"dir": "baseline"}, "workspace_files": [], "tracked_files": [], "excluded_paths": [], "workspace_fingerprint": "fixture"}
        current["fingerprint"] = issue_execution.digest(current)
        with patch.object(issue_execution, "changed_files", return_value=["dir"]), patch.object(issue_execution, "workspace_manifest", return_value={"dir": "baseline"}), patch.object(issue_execution, "git", side_effect=[self.base, ""]):
            issue_execution.reconcile(str(self.repo), "main", {"repository": "fixture/repo", "issue": 107, "criteria": [{"id": "AC-1"}], "tasks": [{"id": "T1", "objective": "x", "status": "done", "dependencies": [], "criteria": ["AC-1"]}], "files": [], "supporting_documents": [{"disposition": "NOT_APPLICABLE", "reason": "none"}]}, current, expected_repository="fixture/repo", expected_issue=107)

    def test_preflight_blocks_dirty_baseline_and_can_record_it_explicitly(self) -> None:
        criteria = Path(self.tmp.name) / "criteria.yaml"
        criteria.write_text("- id: AC-1\n  status: pending\n")
        state = self.state_dir
        command = [sys.executable, str(ISSUE_SCRIPTS / "issue_execution.py"), "preflight", "--repo-root", str(self.repo), "--repository", "fixture/repo", "--issue", "107", "--base-branch", "main", "--base-sha", self.base, "--state-dir", str(state), "--criteria", str(criteria)]
        blocked = subprocess.run(command, text=True, capture_output=True)
        self.assertNotEqual(blocked.returncode, 0)
        fingerprint = issue_execution.baseline(str(self.repo), [str(state)])["fingerprint"]
        allowed = subprocess.run(command + ["--allowed-paths", "README.md", "fake_runtime.py", "--allow-known-dirty", "--dirty-baseline-fingerprint", fingerprint], text=True, capture_output=True)
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        session = yaml.safe_load((state / "session.yaml").read_text())
        self.assertEqual(session["baseline"]["head"], self.base)
        self.assertTrue(session["baseline"]["status"])
        self.assertEqual(session["review_cycle"]["work"]["status"], "not_run")
        self.assertEqual(session["review_cycle"]["goal"]["status"], "not_run")

    def test_preflight_accepts_only_repository_local_state_directory(self) -> None:
        criteria = Path(self.tmp.name) / "criteria-inside.yaml"
        criteria.write_text("- id: AC-1\n  status: pending\n")
        state = Path(self.tmp.name) / "external-state"
        command = [sys.executable, str(ISSUE_SCRIPTS / "issue_execution.py"), "preflight", "--repo-root", str(self.repo), "--repository", "fixture/repo", "--issue", "107", "--base-branch", "main", "--base-sha", self.base, "--state-dir", str(state), "--criteria", str(criteria)]
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("under <worktree>/.agents/sessions", result.stderr)
        self.assertFalse((state / "session.yaml").exists())

    def test_preflight_rejects_symlinked_state_directory(self) -> None:
        criteria = Path(self.tmp.name) / "criteria-symlink.yaml"
        criteria.write_text("- id: AC-1\n  status: pending\n")
        target = Path(self.tmp.name) / "external-state"
        target.mkdir()
        state = self.repo / "state-link"
        state.symlink_to(target, target_is_directory=True)
        command = [sys.executable, str(ISSUE_SCRIPTS / "issue_execution.py"), "preflight", "--repo-root", str(self.repo), "--repository", "fixture/repo", "--issue", "107", "--base-branch", "main", "--base-sha", self.base, "--state-dir", str(state), "--criteria", str(criteria)]
        result = subprocess.run(command, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("traverses a symlink", result.stderr)

    def test_acceptance_requires_current_two_axis_review_and_stales_on_repair(self) -> None:
        base_head = self.base; candidate_head = self.base
        review_result = {"version": 1, "stale": False, "reviewability": "reviewable", "snapshot": {"base_ref": "main", "base_head": base_head, "candidate_head": candidate_head, "criteria_fingerprint": "c", "rubric_ref": "r", "authority_fingerprint": "", "workspace_fingerprint": "", "evidence_fingerprint": "e", "validation_fingerprint": "", "supporting_documents_fingerprint": "", "changed_files_fingerprint": "", "repo_binding_fingerprint": "", "fresh_context": True, "read_only": True, "reviewer_session_id": REVIEWER_ID, "reviewer_identity_source": "host_observed_not_assessed", "reviewer_attestation": reviewer_attestation()}, "work_review": {"status": "pass"}, "goal_review": {"status": "complete", "criteria": [{"id": "AC-1", "status": "fulfilled", "evidence": "verified"}]}, "findings": [], "verified_material_findings": [], "supporting_documents": [{"path": "", "disposition": "NOT_APPLICABLE", "reason": "fixture has no supporting-document impact"}], "recommendation": "not_assessed"}
        session = {"status": "reviewing", "repository": "fixture/repo", "issue": 107, "task": None, "repo_binding": issue_execution.repository_binding(str(self.repo)), "state_dir": str(self.state_dir), "base": {"branch": "main", "sha": base_head}, "baseline": issue_execution.baseline(str(self.repo), [str(self.state_dir)])}
        manifest = [{"id": "AC-1"}]
        packet = {"authority": {"repository": "fixture/repo", "issue": 107}, "base": {"ref": "main", "head": base_head}, "candidate": {"head": candidate_head, "changed_files": []}, "criteria": [{"id": "AC-1", "status": "fulfilled", "evidence": "owner"}], "criteria_manifest": manifest, "criteria_revision": "fixture-r1", "criteria_manifest_fingerprint": review.fp(manifest), "changed_files": [], "validation": {"tests": "pass"}, "evidence": {"receipt": "r"}, "supporting_documents": [{"path": "", "disposition": "NOT_APPLICABLE", "reason": "fixture has no supporting-document impact"}], "repo_binding": issue_execution.repository_binding(str(self.repo)), "workspace_fingerprint": issue_execution.workspace_fingerprint(str(self.repo), [str(self.tmp.name)]), "rubric_ref": "r"}
        review_result["snapshot"]["criteria_fingerprint"] = issue_execution.digest(packet["criteria"])
        review_result["snapshot"]["authority_fingerprint"] = issue_execution.digest(packet["authority"])
        review_result["snapshot"]["workspace_fingerprint"] = packet["workspace_fingerprint"]
        review_result["snapshot"]["evidence_fingerprint"] = issue_execution.digest(packet["evidence"])
        review_result["snapshot"]["validation_fingerprint"] = issue_execution.digest(packet["validation"])
        review_result["snapshot"]["supporting_documents_fingerprint"] = issue_execution.digest(packet["supporting_documents"])
        review_result["snapshot"]["changed_files_fingerprint"] = issue_execution.digest(sorted(packet.get("changed_files", [])))
        review_result["snapshot"]["repo_binding_fingerprint"] = issue_execution.digest(packet["repo_binding"])
        forged_approval = {"authority": "parent", "approval_id": "test-approval", "decision": "accept", "candidate_head": candidate_head}
        with self.assertRaises(ValueError):
            issue_execution.accept_candidate(session, review_result, packet, repo_root=str(self.repo), base_ref="main", candidate=candidate_head, base_head=base_head, criteria_fp=issue_execution.digest(packet["criteria"]), rubric_ref="r", evidence_fp=issue_execution.digest(packet["evidence"]))
        session["forged_approval"] = forged_approval
        session["review_cycle"] = {"round": 1, "candidate_head": candidate_head, "work": {"stale": False}, "goal": {"stale": False}}
        stale = issue_execution.mark_stale(session, "c" * 40)
        self.assertTrue(stale["review_cycle"]["work"]["stale"])
        self.assertTrue(stale["review_cycle"]["goal"]["stale"])
        self.assertEqual(stale["review_cycle"]["round"], 2)
        no_acceptance = {"status": "reviewing", "review_cycle": {"round": 1, "candidate_head": "a", "work": {"stale": False}, "goal": {"stale": False}}}
        self.assertTrue(issue_execution.mark_stale(no_acceptance, "b")["review_cycle"]["goal"]["stale"])
        with self.assertRaises(ValueError):
            issue_execution.accept_candidate(session, review_result, packet, repo_root=str(self.repo), base_ref="main", candidate="c" * 40, base_head=base_head, criteria_fp=issue_execution.digest(packet["criteria"]), rubric_ref="r", evidence_fp=issue_execution.digest(packet["evidence"]))

    def test_acceptance_requires_reviewing_pre_state(self) -> None:
        with self.assertRaisesRegex(ValueError, "reviewing session"):
            issue_execution.accept_candidate({"status": "ready"}, {}, {}, repo_root=str(self.repo), base_ref="main", candidate=self.base, base_head=self.base, criteria_fp="", rubric_ref="", evidence_fp="")

    def test_reconcile_rejects_deleted_preexisting_untracked_file(self) -> None:
        dirty = self.repo / "preexisting.txt"
        dirty.write_text("owned before\n")
        trusted = issue_execution.baseline(str(self.repo))
        dirty.unlink()
        with self.assertRaisesRegex(ValueError, "missing_preexisting"):
            issue_execution.reconcile(str(self.repo), "main", {"repository": "fixture/repo", "issue": 107, "criteria": [{"id": "AC-1"}], "tasks": [{"id": "T1", "objective": "x", "status": "done", "dependencies": [], "criteria": ["AC-1"]}], "files": [], "supporting_documents": [{"disposition": "NOT_APPLICABLE", "reason": "none"}]}, trusted, expected_repository="fixture/repo", expected_issue=107)

    def test_reconcile_rejects_deleted_preexisting_ignored_file(self) -> None:
        ignore = self.repo / ".gitignore"
        ignore.write_text("ignored.txt\n")
        subprocess.run(["git", "-C", str(self.repo), "add", ".gitignore"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "ignore file"], check=True)
        ignored = self.repo / "ignored.txt"
        ignored.write_text("owned before\n")
        trusted = issue_execution.baseline(str(self.repo))
        ignored.unlink()
        with self.assertRaisesRegex(ValueError, "missing_preexisting"):
            issue_execution.reconcile(str(self.repo), "main", {"repository": "fixture/repo", "issue": 107, "criteria": [{"id": "AC-1"}], "tasks": [{"id": "T1", "objective": "x", "status": "done", "dependencies": [], "criteria": ["AC-1"]}], "files": [], "supporting_documents": [{"disposition": "NOT_APPLICABLE", "reason": "none"}]}, trusted, expected_repository="fixture/repo", expected_issue=107)

    def test_reconcile_allows_deleted_clean_tracked_file_when_ledgered(self) -> None:
        trusted = issue_execution.baseline(str(self.repo))
        (self.repo / "README.md").unlink()
        ledger = {"repository": "fixture/repo", "issue": 107, "allowed_paths": ["README.md"], "criteria": [{"id": "AC-1"}], "tasks": [{"id": "T1", "objective": "remove obsolete file", "status": "done", "dependencies": [], "criteria": ["AC-1"]}], "files": [{"path": "README.md", "task": "T1", "disposition": "DELETED", "evidence": "obsolete", "criteria": ["AC-1"]}], "supporting_documents": [{"disposition": "NOT_APPLICABLE", "reason": "none"}]}
        issue_execution.reconcile(str(self.repo), "main", ledger, trusted, expected_repository="fixture/repo", expected_issue=107)

    def test_reconcile_preserves_preexisting_rename_baseline(self) -> None:
        subprocess.run(["git", "-C", str(self.repo), "mv", "README.md", "README-renamed.md"], check=True)
        trusted = issue_execution.baseline(str(self.repo))
        ledger = {"repository": "fixture/repo", "issue": 107, "allowed_paths": ["README-renamed.md"], "criteria": [{"id": "AC-1"}], "tasks": [{"id": "T1", "objective": "preserve rename", "status": "done", "dependencies": [], "criteria": ["AC-1"]}], "files": [], "supporting_documents": [{"disposition": "NOT_APPLICABLE", "reason": "none"}]}
        issue_execution.reconcile(str(self.repo), "main", ledger, trusted, expected_repository="fixture/repo", expected_issue=107)

    def test_composed_review_stops_before_external_parent(self) -> None:
        baseline = issue_execution.baseline(str(self.repo), [str(self.state_dir)])
        subprocess.run(["git", "-C", str(self.repo), "switch", "-q", "-c", "codex/test"], check=True)
        (self.repo / "result.txt").write_text("fixed\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "result.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "candidate"], check=True)
        candidate = git(self.repo, "rev-parse", "HEAD")
        manifest = [{"id": "AC-1"}]
        packet = {"authority": {"repository": "fixture/repo", "issue": 107}, "base": {"ref": "main", "head": self.base}, "candidate": {"head": candidate, "changed_files": ["result.txt"]}, "criteria": [{"id": "AC-1", "status": "fulfilled", "evidence": "owner"}], "criteria_manifest": manifest, "criteria_revision": "fixture-r1", "criteria_manifest_fingerprint": review.fp(manifest), "changed_files": ["result.txt"], "validation": {"tests": "pass"}, "evidence": {"receipt": "r"}, "supporting_documents": [{"path": "", "disposition": "NOT_APPLICABLE", "reason": "fixture"}], "repo_binding": issue_execution.repository_binding(str(self.repo)), "workspace_fingerprint": issue_execution.workspace_fingerprint(str(self.repo), [str(self.state_dir)]), "rubric_ref": "r"}
        packet["review_attempt"] = {"axis": "joint", "round": 1}
        observed = review.normalize(packet, {"fresh_context": True, "read_only": True, "reviewer_session_id": "NOT_ASSESSED", "criteria_review": [{"id": "AC-1", "status": "fulfilled", "evidence": "independent"}], "findings": []}, reviewer_session_id=REVIEWER_ID, reviewer_attestation=reviewer_attestation())
        session = {"status": "reviewing", "repository": "fixture/repo", "issue": 107, "task": None, "repo_binding": issue_execution.repository_binding(str(self.repo)), "state_dir": str(self.state_dir), "base": {"branch": "main", "sha": self.base}, "canonical_branch": "codex/test", "baseline": baseline}
        with self.assertRaisesRegex(ValueError, "separate WORK and GOAL"):
            issue_execution.accept_candidate(session, observed, packet, repo_root=str(self.repo), base_ref="main", candidate=candidate, base_head=self.base, criteria_fp=issue_execution.digest(packet["criteria"]), rubric_ref="r", evidence_fp=issue_execution.digest(packet["evidence"]))

    def test_separate_work_and_goal_reviews_reach_parent_decision_boundary(self) -> None:
        baseline = issue_execution.baseline(str(self.repo), [str(self.state_dir)])
        subprocess.run(["git", "-C", str(self.repo), "switch", "-q", "-c", "codex/test-separate-review"], check=True)
        (self.repo / "result.txt").write_text("fixed\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "result.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "candidate"], check=True)
        candidate = git(self.repo, "rev-parse", "HEAD")
        manifest = [{"id": "AC-1"}]
        packet = {"authority": {"repository": "fixture/repo", "issue": 107}, "base": {"ref": "main", "head": self.base}, "candidate": {"head": candidate, "changed_files": ["result.txt"]}, "criteria": [{"id": "AC-1", "status": "fulfilled", "evidence": "owner"}], "criteria_manifest": manifest, "criteria_revision": "fixture-r1", "criteria_manifest_fingerprint": review.fp(manifest), "changed_files": ["result.txt"], "validation": {"tests": "pass"}, "evidence": {"receipt": "r"}, "supporting_documents": [{"path": "", "disposition": "NOT_APPLICABLE", "reason": "fixture"}], "repo_binding": issue_execution.repository_binding(str(self.repo)), "workspace_fingerprint": issue_execution.workspace_fingerprint(str(self.repo), [str(self.state_dir)]), "rubric_ref": "r"}
        work_packet = {**packet, "review_attempt": {"axis": "work", "round": 1}}
        goal_packet = {**packet, "review_attempt": {"axis": "goal", "round": 1}}
        work_id = "33333333-3333-3333-3333-333333333333"
        goal_id = "44444444-4444-4444-4444-444444444444"
        work = review.normalize(work_packet, {"fresh_context": True, "read_only": True, "reviewer_session_id": "NOT_ASSESSED", "findings": []}, reviewer_session_id=work_id, reviewer_attestation=reviewer_attestation(work_id))
        goal = review.normalize(goal_packet, {"fresh_context": True, "read_only": True, "reviewer_session_id": "NOT_ASSESSED", "criteria_review": [{"id": "AC-1", "status": "fulfilled", "evidence": "independent"}]}, reviewer_session_id=goal_id, reviewer_attestation=reviewer_attestation(goal_id))
        session = {"status": "reviewing", "repository": "fixture/repo", "issue": 107, "task": None, "repo_binding": issue_execution.repository_binding(str(self.repo)), "state_dir": str(self.state_dir), "base": {"branch": "main", "sha": self.base}, "canonical_branch": "codex/test-separate-review", "baseline": baseline}
        eligible = issue_execution.accept_candidate(session, work, packet, repo_root=str(self.repo), base_ref="main", candidate=candidate, base_head=self.base, criteria_fp=issue_execution.digest(packet["criteria"]), rubric_ref="r", evidence_fp=issue_execution.digest(packet["evidence"]), goal_review=goal)
        self.assertEqual(eligible["status"], "awaiting_parent_decision")
        self.assertEqual(eligible["review_cycle"]["work"]["status"], "pass")
        self.assertEqual(eligible["review_cycle"]["goal"]["status"], "complete")
        self.assertEqual(eligible["review_cycle"]["work"]["receipt"], f"review/athena-{candidate[:7]}-work-r1.yaml")
        self.assertIn("athena:repo:issue-107:", eligible["review_cycle"]["goal"]["display_label"])
        self.assertEqual(eligible["candidate"], {"head": candidate, "checkpoint_reason": "integrated_candidate"})
        self.assertNotIn("latest_review", eligible)

    def test_composed_review_rejects_blocked_supporting_document(self) -> None:
        baseline = issue_execution.baseline(str(self.repo), [str(self.state_dir)])
        subprocess.run(["git", "-C", str(self.repo), "switch", "-q", "-c", "codex/test-blocked-support"], check=True)
        (self.repo / "result.txt").write_text("fixed\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "result.txt"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "candidate"], check=True)
        candidate = git(self.repo, "rev-parse", "HEAD")
        manifest = [{"id": "AC-1"}]
        packet = {"authority": {"repository": "fixture/repo", "issue": 107}, "base": {"ref": "main", "head": self.base}, "candidate": {"head": candidate, "changed_files": ["result.txt"]}, "criteria": [{"id": "AC-1", "status": "fulfilled", "evidence": "owner"}], "criteria_manifest": manifest, "criteria_revision": "fixture-r1", "criteria_manifest_fingerprint": review.fp(manifest), "changed_files": ["result.txt"], "validation": {"tests": "pass"}, "evidence": {"receipt": "r"}, "supporting_documents": [{"path": "README.md", "disposition": "BLOCKED", "reason": "owner decision required"}], "repo_binding": issue_execution.repository_binding(str(self.repo)), "workspace_fingerprint": issue_execution.workspace_fingerprint(str(self.repo), [str(self.state_dir)]), "rubric_ref": "r"}
        work_packet = {**packet, "review_attempt": {"axis": "work", "round": 1}}
        goal_packet = {**packet, "review_attempt": {"axis": "goal", "round": 1}}
        work_id = "33333333-3333-3333-3333-333333333333"
        goal_id = "44444444-4444-4444-4444-444444444444"
        observed = review.normalize(work_packet, {"fresh_context": True, "read_only": True, "findings": []}, reviewer_session_id=work_id, reviewer_attestation=reviewer_attestation(work_id))
        goal = review.normalize(goal_packet, {"fresh_context": True, "read_only": True, "criteria_review": [{"id": "AC-1", "status": "fulfilled", "evidence": "independent"}]}, reviewer_session_id=goal_id, reviewer_attestation=reviewer_attestation(goal_id))
        session = {"status": "reviewing", "repository": "fixture/repo", "issue": 107, "task": None, "repo_binding": issue_execution.repository_binding(str(self.repo)), "state_dir": str(self.state_dir), "base": {"branch": "main", "sha": self.base}, "canonical_branch": "codex/test-blocked-support", "baseline": baseline}
        with self.assertRaisesRegex(ValueError, "supporting-document"):
            issue_execution.accept_candidate(session, observed, packet, repo_root=str(self.repo), base_ref="main", candidate=candidate, base_head=self.base, criteria_fp=issue_execution.digest(packet["criteria"]), rubric_ref="r", evidence_fp=issue_execution.digest(packet["evidence"]), goal_review=goal)














if __name__ == "__main__":
    unittest.main()
