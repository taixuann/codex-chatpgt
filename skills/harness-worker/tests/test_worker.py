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
sys.path.insert(0, str(SCRIPTS))
import harness_worker  # noqa: E402


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


class HarnessWorkerTests(unittest.TestCase):
    def test_worker_has_no_parent_or_renderer_import(self) -> None:
        source = Path(harness_worker.__file__).read_text()
        self.assertNotRegex(source, r"(?m)^(?:from|import) (?:issue_execution|delegation_prompt)\b")

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
        request["expected_context"]["effective_context_fingerprint_expectation"] = harness_worker.effective_context(str(self.repo), str(self.repo), ["issue-execution"])["fingerprint"]
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


    def test_exact_session_resume_and_mismatch_fail_closed(self) -> None:
        first = self.run_request(self.request("defect"), "defect")
        self.assertEqual(first["runtime"]["session_state"], "fresh")
        second = self.run_request(self.request("fix", "resume"), "fix")
        self.assertEqual(second["runtime"]["session_state"], "resumed")
        self.assertEqual(second["runtime"]["native_session_id"], "native-1")
        bad = self.request("bad-cwd", "resume")
        bad["repo"]["cwd"] = str(self.repo.parent)
        with self.assertRaises(ValueError):
            harness_worker.run(bad, Path(self.tmp.name) / "sessions.json", 10)

    def test_required_skill_context_fails_closed_when_missing(self) -> None:
        with self.assertRaisesRegex(ValueError, "required skills unavailable"):
            harness_worker.effective_context(str(self.repo), str(self.repo), ["missing-skill"])

    def test_context_rejects_symlinked_instruction_and_skill_sources(self) -> None:
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (outside / "AGENTS.md").write_text("outside instructions\n")
        (self.repo / "AGENTS.md").symlink_to(outside / "AGENTS.md")
        with self.assertRaisesRegex(ValueError, "CONTEXT_CONTRACT_UNVERIFIED"):
            harness_worker.effective_context(str(self.repo), str(self.repo))
        (self.repo / "AGENTS.md").unlink()
        skill = self.repo / "skills" / "issue-execution" / "SKILL.md"
        skill.unlink()
        (outside / "SKILL.md").write_text("outside skill\n")
        skill.symlink_to(outside / "SKILL.md")
        with self.assertRaisesRegex(ValueError, "CONTEXT_CONTRACT_UNVERIFIED"):
            harness_worker.effective_context(str(self.repo), str(self.repo), ["issue-execution"])

    def test_receipt_context_is_bound_to_request(self) -> None:
        request = self.request("context-bound")
        receipt = self.run_request(request, "context-bound")
        receipt["context"]["instruction_fingerprint"] = "wrong"
        with self.assertRaisesRegex(ValueError, "instruction context does not match"):
            harness_worker.validate_harness_receipt(request, receipt)


    def test_timeout_is_reported_at_real_subprocess_boundary(self) -> None:
        request = self.request("timeout")
        script = self.repo / "timeout.py"
        script.write_text("import time\ntime.sleep(2)\n")
        request["command"] = [sys.executable, str(script)]
        env = {**os.environ, "HEADLESS_CLI_TEST_ONLY": "1", "HEADLESS_CLI_SANDBOX_EXECUTABLE": str(self.sandbox)}
        with patch.dict(os.environ, env, clear=True):
            receipt = harness_worker.run(request, Path(request["outputs"]["registry"]), 0.01)
        self.assertEqual(receipt["execution"]["status"], "TIMED_OUT")
        self.assertEqual(receipt["execution"]["error_code"], "TIMED_OUT")
        self.assertTrue(receipt["runtime"]["native_session_id"])
        request["session"]["policy"] = "resume"
        with self.assertRaisesRegex(ValueError, "rebind is required"):
            harness_worker.run(request, Path(request["outputs"]["registry"]), 0.01)


    def test_production_agy_fails_fast_without_sandbox_runtime_inputs(self) -> None:
        request = self.request("agy-preflight")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print"]
        request["_delegation_prompt"] = "Run the bounded AGY fixture."
        request["_delegation_contract"] = {"task_id": "fixture"}
        request["_delegation_binding"] = {"version": 1, "profile": "agy", "source_contract_sha256": harness_worker._digest(request["_delegation_contract"]), "rendered_prompt_sha256": harness_worker._digest(request["_delegation_prompt"])}
        clean_env = dict(os.environ)
        clean_env.pop("HEADLESS_CLI_ALLOW_NETWORK", None)
        clean_env.pop("HEADLESS_CLI_RUNTIME_WRITE_ROOTS", None)
        for launch_env in ({}, {"HEADLESS_CLI_ALLOW_NETWORK": "1"}):
            with self.subTest(launch_env=launch_env), patch.dict(os.environ, {**clean_env, **launch_env}, clear=True):
                receipt = harness_worker.run(request, Path(self.tmp.name) / "sessions.json", 10)
            self.assertEqual(receipt["execution"]["error_code"], "RUNTIME_UNAVAILABLE")
            self.assertEqual(receipt["fallback_required"], "prometheus")

    def test_q0_blocks_repository_egress_before_native_launch(self) -> None:
        request = self.request("q0-egress")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print"]
        request["_delegation_prompt"] = "Return one harmless smoke token."
        request["_delegation_contract"] = {"task_id": "q0"}
        request["_delegation_binding"] = {"version": 1, "profile": "agy", "source_contract_sha256": harness_worker._digest(request["_delegation_contract"]), "rendered_prompt_sha256": harness_worker._digest(request["_delegation_prompt"])}
        runtime = Path(self.tmp.name) / "q0-runtime"
        runtime.mkdir()
        with patch.dict(os.environ, {"HEADLESS_CLI_ALLOW_NETWORK": "1", "HEADLESS_CLI_RUNTIME_WRITE_ROOTS": str(runtime), "HEADLESS_CLI_RUNTIME_READ_ROOTS": str(runtime)}, clear=True), patch.object(harness_worker.shutil, "which", return_value=str(self.fake)):
            receipt = harness_worker.run(request, Path(self.tmp.name) / "q0-sessions.json", 10)
        self.assertEqual(receipt["execution"]["error_code"], "RUNTIME_UNAVAILABLE")
        self.assertEqual(receipt["live_qualification"]["status"], "NOT_ASSESSED")
        self.assertEqual(receipt["live_qualification"]["reason"], "HOST_REPOSITORY_EGRESS_BLOCKED")
        self.assertFalse(receipt["live_qualification"]["provider_launched"])
        self.assertTrue(receipt["live_qualification"]["capability_fingerprint"])

        request["qualification_stage"] = "fixture"
        with patch.dict(os.environ, {"HEADLESS_CLI_ALLOW_NETWORK": "1", "HEADLESS_CLI_RUNTIME_WRITE_ROOTS": str(runtime), "HEADLESS_CLI_RUNTIME_READ_ROOTS": str(runtime)}, clear=True), patch.object(harness_worker.shutil, "which", return_value=str(self.fake)), patch.object(harness_worker, "agy_sandbox_probe"):
            observation = harness_worker.agy_capability_preflight(request)
        self.assertEqual(observation["status"], "READY")

    def test_q0_reports_sandbox_incompatibility_before_provider_launch(self) -> None:
        request = self.request("q0-sandbox")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print"]
        request["_delegation_prompt"] = "Return one harmless smoke token."
        request["_delegation_contract"] = {"task_id": "q0-sandbox"}
        request["_delegation_binding"] = {"version": 1, "profile": "agy", "source_contract_sha256": harness_worker._digest(request["_delegation_contract"]), "rendered_prompt_sha256": harness_worker._digest(request["_delegation_prompt"])}
        runtime = Path(self.tmp.name) / "q0-sandbox-runtime"
        runtime.mkdir()
        with patch.dict(os.environ, {"HEADLESS_CLI_ALLOW_NETWORK": "1", "HEADLESS_CLI_RUNTIME_WRITE_ROOTS": str(runtime), "HEADLESS_CLI_RUNTIME_READ_ROOTS": str(runtime), "HEADLESS_CLI_REPOSITORY_EGRESS_ALLOWED": "1"}, clear=True), patch.object(harness_worker.shutil, "which", return_value=str(self.fake)), patch.object(harness_worker, "agy_sandbox_probe", side_effect=RuntimeError("RUNTIME_UNAVAILABLE: HOST_AGY_SANDBOX_INCOMPATIBLE")):
            receipt = harness_worker.run(request, Path(self.tmp.name) / "q0-sandbox-sessions.json", 10)
        self.assertEqual(receipt["live_qualification"]["reason"], "HOST_AGY_SANDBOX_INCOMPATIBLE")
        self.assertFalse(receipt["live_qualification"]["provider_launched"])

    def test_prelaunch_resume_does_not_forge_a_saved_session(self) -> None:
        request = self.request("agy-preflight-resume", "resume")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print"]
        request["_delegation_prompt"] = "Run the bounded AGY fixture."
        request["_delegation_contract"] = {"task_id": "fixture"}
        request["_delegation_binding"] = {"version": 1, "profile": "agy", "source_contract_sha256": harness_worker._digest(request["_delegation_contract"]), "rendered_prompt_sha256": harness_worker._digest(request["_delegation_prompt"])}
        with patch.dict(os.environ, {"HEADLESS_CLI_ALLOW_NETWORK": "1"}, clear=False):
            with self.assertRaisesRegex(ValueError, "exact saved session is absent"):
                harness_worker.run(request, Path(request["outputs"]["registry"]), 10)

    def test_delegation_prompt_fingerprint_is_verified(self) -> None:
        request = self.request("delegation-fingerprint")
        request["_delegation_prompt"] = "actual prompt"
        request["_delegation_binding"] = {"version": 1, "profile": "agy", "source_contract_sha256": "0" * 64, "rendered_prompt_sha256": "1" * 64}
        with self.assertRaisesRegex(ValueError, "fingerprints"):
            harness_worker.bind_delegation(request)

    def test_delegation_scope_mismatch_fails_closed(self) -> None:
        request = self.request("delegation-scope-mismatch")
        request["scope"]["allowed_paths"] = ["."]
        request["_delegation_prompt"] = "actual prompt"
        contract = {"task_id": "scope-mismatch", "allowed_scope": ["safe.txt"]}
        request["_delegation_contract"] = contract
        request["_delegation_binding"] = {
            "version": 1,
            "profile": "agy",
            "source_contract_sha256": harness_worker._digest(contract),
            "rendered_prompt_sha256": harness_worker._digest(request["_delegation_prompt"]),
        }
        with self.assertRaisesRegex(ValueError, "rendered scope"):
            harness_worker.bind_delegation(request)

    def test_request_rejects_portability_ambiguous_scope_paths(self) -> None:
        for path in ("./outside", "foo/./bar", "foo//bar", "C:/outside", "NUL", "foo\u200bbar"):
            request = self.request(f"scope-{path}")
            request["scope"]["allowed_paths"] = [path]
            with self.subTest(path=path), patch.object(harness_worker.sys, "platform", "darwin"), self.assertRaises(ValueError):
                harness_worker.sandbox_command(["echo", "ok"], request)

    def test_root_allowance_emits_git_deny_after_root_allow(self) -> None:
        request = self.request("root-order")
        request["scope"]["allowed_paths"] = ["."]
        with patch.object(harness_worker.sys, "platform", "darwin"):
            profile = harness_worker.sandbox_command(["echo", "ok"], request)[2]
        deny = f'(deny file-write* (subpath "{harness_worker.canonical(self.repo)}/.git"))'
        allow = f'(allow file-write* (subpath "{harness_worker.canonical(self.repo)}"))'
        self.assertGreater(profile.index(deny), profile.index(allow))

    def test_sandbox_requires_a_scope_path_list(self) -> None:
        request = self.request("scope-type")
        request["scope"]["allowed_paths"] = "."
        with patch.object(harness_worker.sys, "platform", "darwin"), self.assertRaisesRegex(ValueError, "must be a list"):
            harness_worker.sandbox_command(["echo", "ok"], request)



    def test_native_resume_binds_exact_provider_session(self) -> None:
        request = self.request("agy-resume")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print", "hello"]
        command = harness_worker.bind_native_command(request["command"], request, {"native_session_id": "agy-native"})
        self.assertIn(["--conversation", "agy-native"], [command[index:index + 2] for index in range(len(command) - 1)])

    def test_agy_print_flag_is_after_bound_options(self) -> None:
        request = self.request("agy-print-order")
        request["harness"] = "agy"
        command = harness_worker.bind_native_command(["agy", "--print"], request)
        self.assertEqual(command[-1], "--print")
        self.assertLess(command.index("--output-format"), command.index("--print"))
        self.assertIn("--sandbox", command)


    def test_agy_workspace_is_bound_to_request_cwd(self) -> None:
        request = self.request("agy-add-dir")
        request["harness"] = "agy"
        command = harness_worker.bind_native_command(["agy", "--print"], request)
        index = command.index("--add-dir")
        self.assertEqual(command[index + 1], str(self.repo.resolve()))
        mode_index = command.index("--mode")
        self.assertEqual(command[mode_index + 1], "accept-edits")

    def test_agy_workspace_rejects_relative_cwd_binding(self) -> None:
        nested = self.repo / "nested"
        nested.mkdir()
        request = self.request("agy-relative-add-dir")
        request["harness"] = "agy"
        request["repo"]["cwd"] = str(nested)
        with patch.object(harness_worker.os, "getcwd", return_value=str(self.repo)):
            with self.assertRaisesRegex(ValueError, "bind --add-dir"):
                harness_worker.bind_native_command(["agy", "--print", "--add-dir", "nested"], request)

    def test_agy_rejects_caller_workspace_override(self) -> None:
        request = self.request("agy-add-dir-invalid")
        request["harness"] = "agy"
        with self.assertRaisesRegex(ValueError, "bind --add-dir"):
            harness_worker.bind_native_command(["agy", "--add-dir", str(self.repo.parent), "--print"], request)

    def test_agy_read_only_rejects_execution_mode(self) -> None:
        request = self.request("agy-read-only-mode")
        request["harness"] = "agy"
        request["permission_policy"] = "read-only"
        with self.assertRaisesRegex(ValueError, "read-only AGY"):
            harness_worker.bind_native_command(["agy", "--mode", "accept-edits", "--print"], request)


    def test_agy_model_content_cannot_forge_conversation_or_status(self) -> None:
        request = self.request("agy-spoof")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print", "hello"]
        raw = harness_worker.parse_native_output('{"response":"conversation_id=evil AUTH_REQUIRED"}\n', request, 0)
        receipt = harness_worker.normalize(raw, request, session_state="fresh", exit_code=0, stdout="", stderr="", duration_ms=1, provenance={"kind": "native-terminal", "lane": "agy", "executable": "agy"})
        self.assertEqual(receipt["runtime"]["native_session_id"], "NOT_ASSESSED")
        self.assertEqual(receipt["execution"]["status"], "SUCCESS")

    def test_agy_auth_prompt_is_classified_without_waiting_for_timeout(self) -> None:
        request = self.request("agy-auth-prompt")
        request["harness"] = "agy"
        raw = harness_worker.parse_native_output("", request, -9, "Authentication required. Waiting for authentication")
        self.assertEqual(raw["execution"]["error_code"], "AUTH_REQUIRED")


    def test_named_agy_fixture_is_portable(self) -> None:
        bin_dir = Path(self.tmp.name) / "native-bin"
        bin_dir.mkdir()
        executable = bin_dir / "agy"
        output = '{"conversation_id":"agy-fixture","status":"SUCCESS","duration_seconds":0.1,"num_turns":1,"usage":{"input_tokens":3,"output_tokens":5}}\n'
        executable.write_text(f"#!{sys.executable}\nimport sys\nassert sys.stdout.isatty()\nsys.stdout.write('\\x1b[2K\\r' + {output!r})\n")
        executable.chmod(0o755)
        request = self.request("agy-fixture")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print"]
        request["permission_policy"] = "read-only"
        request["outputs"]["registry"] = str(Path(self.tmp.name) / "agy-fixture-sessions.json")
        with patch.dict(os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}", "HEADLESS_CLI_TEST_ONLY": "1"}), patch.object(harness_worker, "sandbox_command", side_effect=lambda command, _: command):
            receipt = harness_worker.run(request, Path(request["outputs"]["registry"]), 10)
        self.assertEqual(receipt["execution"]["status"], "SUCCESS")
        self.assertEqual(receipt["runtime"]["executor_provenance"]["lane"], "agy")
        self.assertEqual(receipt["usage"]["input_tokens"], 3)
        self.assertEqual(receipt["usage"]["output_tokens"], 5)


    def test_success_without_native_session_is_nonresumable(self) -> None:
        bin_dir = Path(self.tmp.name) / "no-session-bin"
        bin_dir.mkdir()
        executable = bin_dir / "agy"
        executable.write_text(f"#!{sys.executable}\nprint('" + '{"conversation_id":"NOT_ASSESSED","status":"SUCCESS","duration_seconds":0.1,"num_turns":1,"usage":{}}' + "')\n")
        executable.chmod(0o755)
        request = self.request("agy-no-session")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print"]
        registry = Path(self.tmp.name) / "agy-no-session.json"
        request["outputs"]["registry"] = str(registry)
        with patch.dict(os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}", "HEADLESS_CLI_TEST_ONLY": "1"}), patch.object(harness_worker, "sandbox_command", side_effect=lambda command, _: command):
            receipt = harness_worker.run(request, registry, 10)
        self.assertEqual(receipt["execution"]["status"], "SUCCESS")
        saved = json.loads(registry.read_text())[request["session_alias"]]
        self.assertEqual(saved["status"], "failed")
        self.assertFalse(saved["resumable"])


    def test_auth_failure_invalidates_native_session_even_with_zero_exit(self) -> None:
        bin_dir = Path(self.tmp.name) / "auth-failure-bin"
        bin_dir.mkdir()
        executable = bin_dir / "agy"
        executable.write_text(f"#!{sys.executable}\nprint('" + '{"conversation_id":"agy-auth","status":"AUTH_REQUIRED","duration_seconds":0.1,"num_turns":0,"usage":{}}' + "')\n")
        executable.chmod(0o755)
        request = self.request("agy-auth-failure")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print"]
        registry = Path(self.tmp.name) / "agy-auth-failure.json"
        request["outputs"]["registry"] = str(registry)
        with patch.dict(os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}", "HEADLESS_CLI_TEST_ONLY": "1"}), patch.object(harness_worker, "sandbox_command", side_effect=lambda command, _: command):
            receipt = harness_worker.run(request, registry, 10)
        self.assertEqual(receipt["execution"]["error_code"], "AUTH_REQUIRED")
        saved = json.loads(registry.read_text())[request["session_alias"]]
        self.assertEqual(saved["status"], "failed")
        self.assertFalse(saved["resumable"])
        request["session"]["policy"] = "resume"
        with patch.dict(os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}", "HEADLESS_CLI_TEST_ONLY": "1"}), patch.object(harness_worker, "sandbox_command", side_effect=lambda command, _: command):
            with self.assertRaisesRegex(ValueError, "rebind is required"):
                harness_worker.run(request, registry, 10)


    def test_native_bounded_write_reconciles_allowed_and_unrelated_paths(self) -> None:
        bin_dir = Path(self.tmp.name) / "bounded-native-bin"
        bin_dir.mkdir()
        executable = bin_dir / "agy"
        executable.write_text(f"#!{sys.executable}\nfrom pathlib import Path\nPath('allowed.txt').write_text('ok\\n')\nprint('{{\"conversation_id\":\"agy-write\",\"status\":\"SUCCESS\",\"duration_seconds\":0.1,\"num_turns\":1,\"usage\":{{}}}}')\n")
        executable.chmod(0o755)
        request = self.request("agy-bounded")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print"]
        request["scope"]["allowed_paths"] = ["allowed.txt"]
        request["_delegation_prompt"] = "Run the bounded write fixture."
        request["_delegation_binding"] = {"version": 1, "profile": "agy", "source_contract_sha256": "0" * 64, "rendered_prompt_sha256": harness_worker._digest(request["_delegation_prompt"])}
        request["outputs"]["registry"] = str(Path(self.tmp.name) / "agy-bounded-sessions.json")
        request["permission_policy"] = "bounded-write"
        with patch.dict(os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}", "HEADLESS_CLI_TEST_ONLY": "1"}), patch.object(harness_worker, "sandbox_command", side_effect=lambda command, _: command):
            receipt = harness_worker.run(request, Path(request["outputs"]["registry"]), 10)
        self.assertEqual(receipt["execution"]["status"], "SUCCESS")
        self.assertTrue((self.repo / "allowed.txt").is_file())
        executable.write_text(f"#!{sys.executable}\nfrom pathlib import Path\nPath('unrelated.txt').write_text('bad\\n')\nprint('{{\"conversation_id\":\"agy-write-2\",\"status\":\"SUCCESS\",\"duration_seconds\":0.1,\"num_turns\":1,\"usage\":{{}}}}')\n")
        request["request_id"] = "issue-107:T1:agy-bounded-unrelated"
        request["session_alias"] = "fixture:107:T1-unrelated"
        request["outputs"]["registry"] = str(Path(self.tmp.name) / "agy-bounded-unrelated-sessions.json")
        with patch.dict(os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}", "HEADLESS_CLI_TEST_ONLY": "1"}), patch.object(harness_worker, "sandbox_command", side_effect=lambda command, _: command):
            with self.assertRaisesRegex(ValueError, "MUTATION_SCOPE_VIOLATION"):
                harness_worker.run(request, Path(self.tmp.name) / "agy-bounded-unrelated-sessions.json", 10)


    def test_bounded_write_rejects_git_metadata_only_mutation(self) -> None:
        script = self.repo / "git-metadata-mutator.py"
        script.write_text(
            "from pathlib import Path\n"
            "Path('.git/description').write_text('mutated by runtime\\n')\n"
            "print('{\"protocolVersion\":1,\"type\":\"result\",\"command\":\"invoke\",\"exitCode\":0,\"data\":{\"runtime\":{\"harness\":\"fake\",\"native_session_id\":\"native-git-only\"},\"execution\":{\"status\":\"SUCCESS\"}}}')\n"
        )
        request = self.request("git-only")
        request["scope"]["allowed_paths"] = ["."]
        request["command"] = [sys.executable, str(script)]
        with patch.dict(os.environ, {"HEADLESS_CLI_TEST_ONLY": "1", "HEADLESS_CLI_SANDBOX_EXECUTABLE": str(self.sandbox)}, clear=False):
            with self.assertRaisesRegex(ValueError, "Git metadata changed"):
                harness_worker.run(request, Path(request["outputs"]["registry"]), 10)


    def test_child_environment_is_allowlisted(self) -> None:
        request = self.request("env")
        with patch.dict(os.environ, {"MODE": "fix", "UNRELATED_SECRET": "must-not-pass"}, clear=True):
            env = harness_worker.runtime_environment(request, None)
        self.assertEqual(env["MODE"], "fix")
        self.assertNotIn("UNRELATED_SECRET", env)


    def test_read_only_and_preexisting_file_mutations_fail_closed(self) -> None:
        request = self.request("defect")
        request["permission_policy"] = "read-only"
        with self.assertRaises(ValueError):
            harness_worker.run(request, Path(self.tmp.name) / "readonly-sessions.json", 10)
        request = self.request("defect")
        (self.repo / "README.md").write_text("dirty\n")
        request["scope"]["allowed_paths"] = ["result.txt"]
        mutator = self.repo / "mutator.py"
        mutator.write_text("from pathlib import Path\nPath('README.md').write_text('changed by runtime\\n')\nprint('{\"runtime\": {\"harness\": \"fake\", \"native_session_id\": \"native-2\"}, \"execution\": {\"status\": \"SUCCESS\"}}')\n")
        request["command"] = [sys.executable, str(mutator)]
        with self.assertRaises(ValueError):
            harness_worker.run(request, Path(self.tmp.name) / "dirty-sessions.json", 10)


    def test_git_metadata_mutations_fail_closed(self) -> None:
        script = Path(self.tmp.name) / "mutate-git.py"
        script.write_text(
            "from pathlib import Path\n"
            "Path('.git/description').write_text('mutated by runtime\\n')\n"
            "print('{\"protocolVersion\":1,\"type\":\"result\",\"command\":\"invoke\",\"exitCode\":0,\"data\":{\"runtime\":{\"harness\":\"fake\",\"native_session_id\":\"native-git\"},\"execution\":{\"status\":\"SUCCESS\"}}}')\n"
        )
        request = self.request("git-metadata-mutation")
        request["permission_policy"] = "read-only"
        request["command"] = [sys.executable, str(script)]
        with patch.dict(os.environ, {"HEADLESS_CLI_TEST_ONLY": "1", "HEADLESS_CLI_SANDBOX_EXECUTABLE": str(self.sandbox)}, clear=False):
            with self.assertRaisesRegex(ValueError, "MUTATION_SCOPE_VIOLATION"):
                harness_worker.run(request, Path(request["outputs"]["registry"]), 10)


    def test_output_targets_reject_special_files(self) -> None:
        fifo = Path(self.tmp.name) / "receipt.fifo"
        os.mkfifo(fifo)
        request = self.request("fifo")
        request["outputs"]["registry"] = str(fifo)
        with self.assertRaises(ValueError):
            harness_worker.validate_output_targets(request, str(fifo))


    def test_malformed_local_session_registry_fails_closed(self) -> None:
        registry = Path(self.tmp.name) / "malformed-sessions.json"
        registry.write_text("[]")
        with self.assertRaisesRegex(ValueError, "local session registry"):
            harness_worker.run(self.request("malformed"), registry, 10)
        registry.write_text('{"fixture:107:T1": []}')
        with self.assertRaisesRegex(ValueError, "registry entry"):
            harness_worker.run(self.request("malformed-entry"), registry, 10)
        registry.write_text('{"fixture:107:T1": {}}')
        with self.assertRaisesRegex(ValueError, "registry entry"):
            harness_worker.run(self.request("malformed-empty"), registry, 10)

    def test_stale_local_session_status_fails_closed(self) -> None:
        registry = Path(self.tmp.name) / "stale-sessions.json"
        registry.write_text(json.dumps({"fixture": {"native_session_id": "native-1", "resumable": True, "status": "stale"}}))
        with self.assertRaisesRegex(ValueError, "status is invalid"):
            harness_worker.read_registry(registry)


    def test_executor_output_is_bounded_before_parsing(self) -> None:
        request = self.request("oversized")
        request["command"] = [sys.executable, "-c", "import sys; sys.stdout.write('x' * (1024 * 1024 + 1))"]
        with patch.dict(os.environ, {"HEADLESS_CLI_TEST_ONLY": "1", "HEADLESS_CLI_SANDBOX_EXECUTABLE": str(self.sandbox)}, clear=False):
            with self.assertRaisesRegex(ValueError, "bounded receipt limit"):
                harness_worker.run(request, Path(self.tmp.name) / "sessions.json", 10)


    def test_rebind_clears_a_nonresumable_failed_binding(self) -> None:
        request = self.request("rebind")
        registry = Path(request["outputs"]["registry"])
        registry.write_text(json.dumps({request["session_alias"]: {"native_session_id": "NOT_ASSESSED", "resumable": False}}))
        request["session"]["policy"] = "resume"
        with self.assertRaisesRegex(ValueError, "rebind is required"):
            harness_worker.run(request, registry, 10)
        request["session"]["policy"] = "rebind"
        with patch.dict(os.environ, {"HEADLESS_CLI_TEST_ONLY": "1", "HEADLESS_CLI_SANDBOX_EXECUTABLE": str(self.sandbox)}, clear=False):
            receipt = harness_worker.run(request, registry, 10)
        self.assertEqual(receipt["runtime"]["session_state"], "rebound")
        self.assertEqual(receipt["runtime"]["native_session_id"], "native-1")
        self.assertTrue(json.loads(registry.read_text())[request["session_alias"]]["resumable"])


    def test_shell_is_not_an_execution_boundary(self) -> None:
        request = self.request("defect")
        request["command"] = ["sh", "-c", "echo injected"]
        with self.assertRaises(ValueError):
            harness_worker.run(request, Path(self.tmp.name) / "sessions.json", 10)
        request = self.request("defect")
        request["command"] = ["sh", "-v"]
        with self.assertRaises(ValueError):
            harness_worker.run(request, Path(self.tmp.name) / "sessions.json", 10)
        request = self.request("defect")
        request["harness"] = "agy"
        request["command"] = ["agy", "--dangerously-bypass-approvals-and-sandbox"]
        with self.assertRaises(ValueError):
            harness_worker.run(request, Path(self.tmp.name) / "sessions.json", 10)


    def test_bounded_write_profile_is_path_scoped(self) -> None:
        request = self.request("defect")
        with patch.object(harness_worker.sys, "platform", "darwin"):
            command = harness_worker.sandbox_command(["echo", "ok"], request)
        profile = command[2]
        allowed = Path(harness_worker.canonical(self.repo / "result.txt"))
        self.assertIn(f'(allow file-write* (literal "{allowed}"))', profile)
        self.assertNotIn(f'(allow file-write* (subpath "{self.repo}"))', profile)


    def test_agy_runtime_roots_are_explicit_and_outside_worktree(self) -> None:
        request = self.request("runtime-roots")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print"]
        runtime = Path(self.tmp.name) / "runtime"
        runtime.mkdir()
        with patch.dict(os.environ, {"HEADLESS_CLI_RUNTIME_WRITE_ROOTS": str(runtime), "HEADLESS_CLI_ALLOW_NETWORK": "1"}):
            with patch.object(harness_worker.sys, "platform", "darwin"):
                command = harness_worker.sandbox_command(["echo", "ok"], request)
        profile = command[2]
        self.assertIn(f'(allow file-write* (subpath "{harness_worker.canonical(runtime)}"))', profile)
        self.assertIn("(allow network-outbound)", profile)
        with patch.dict(os.environ, {"HEADLESS_CLI_RUNTIME_WRITE_ROOTS": str(self.repo)}):
            with patch.object(harness_worker.sys, "platform", "darwin"):
                with self.assertRaises(ValueError):
                    harness_worker.sandbox_command(["echo", "ok"], request)
        with patch.dict(os.environ, {"HEADLESS_CLI_RUNTIME_WRITE_ROOTS": os.environ["HOME"]}):
            with self.assertRaisesRegex(ValueError, "HOME"):
                harness_worker.runtime_write_roots(request)


    def test_native_read_profile_is_explicit_and_does_not_grant_home(self) -> None:
        request = self.request("read-roots")
        request["harness"] = "agy"
        request["command"] = ["agy", "--print"]
        runtime = Path(self.tmp.name) / "runtime-read"
        unrelated = Path(self.tmp.name) / "unrelated"
        runtime.mkdir()
        unrelated.mkdir()
        with patch.dict(
            os.environ,
            {
                "HEADLESS_CLI_RUNTIME_WRITE_ROOTS": str(runtime),
                "HEADLESS_CLI_RUNTIME_READ_ROOTS": str(runtime),
                "HEADLESS_CLI_ALLOW_NETWORK": "1",
            },
        ), patch.object(harness_worker.sys, "platform", "darwin"):
            command = harness_worker.sandbox_command(["echo", "ok"], request)
        profile = command[2]
        self.assertIn('(deny file-read* (subpath "/Users"))', profile)
        self.assertIn('(deny file-read* (subpath "/private/tmp"))', profile)
        self.assertIn(f'(allow file-read* (subpath "{harness_worker.canonical(self.repo)}"))', profile)
        self.assertIn(f'(allow file-read* (subpath "{harness_worker.canonical(runtime)}"))', profile)
        self.assertNotIn(str(unrelated), profile)
        self.assertIn(f'(deny file-write* (subpath "{harness_worker.canonical(self.repo)}/.git"))', profile)
        with patch.dict(os.environ, {"HEADLESS_CLI_RUNTIME_READ_ROOTS": os.environ["HOME"]}), patch.object(harness_worker.sys, "platform", "darwin"):
            with self.assertRaisesRegex(ValueError, "HOME"):
                harness_worker.sandbox_command(["echo", "ok"], request)


    def test_detached_head_git_state_is_observable(self) -> None:
        subprocess.run(["git", "-C", str(self.repo), "switch", "--detach", "-q", self.base], check=True)
        self.assertIsInstance(harness_worker.git_state(str(self.repo)), str)

    def test_git_observation_env_disables_optional_locks(self) -> None:
        dangerous = {
            "PATH": "/test-path",
            "GIT_OPTIONAL_LOCKS": "1",
            "GIT_DIR": "/tmp/other-repo",
            "GIT_EXTERNAL_DIFF": "/tmp/other-diff",
            "GIT_CONFIG_GLOBAL": "/tmp/other-config",
            "GIT_TRACE": "/tmp/git-trace.log",
            "GIT_TRACE2": "/tmp/git-trace2.log",
            "GIT_TRACE2_EVENT": "/tmp/git-trace2-event.json",
            "GIT_REDIRECT_STDERR": "/tmp/git-stderr.log",
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "core.fsmonitor",
            "GIT_CONFIG_VALUE_0": "true",
        }
        with patch.dict(os.environ, dangerous, clear=False):
            env = harness_worker.git_observation_env()
        self.assertEqual(env["GIT_OPTIONAL_LOCKS"], "0")
        self.assertEqual(env["PATH"], "/test-path")
        for key in ("GIT_DIR", "GIT_EXTERNAL_DIFF", "GIT_CONFIG_GLOBAL", "GIT_TRACE", "GIT_TRACE2", "GIT_TRACE2_EVENT", "GIT_REDIRECT_STDERR"):
            self.assertNotIn(key, env)
        self.assertEqual(env["GIT_CONFIG_COUNT"], "2")
        self.assertEqual(env["GIT_CONFIG_KEY_0"], "core.fsmonitor")
        self.assertEqual(env["GIT_CONFIG_VALUE_0"], "false")
        self.assertEqual(env["GIT_CONFIG_KEY_1"], "core.pager")

        original_run = harness_worker.subprocess.run
        calls = []

        def observe_run(*args, **kwargs):
            command = args[0] if args else kwargs.get("args", [])
            if command and command[0] == "git":
                calls.append(kwargs.get("env"))
            return original_run(*args, **kwargs)

        call_environment = {**dangerous, "PATH": os.environ["PATH"]}
        with patch.dict(os.environ, call_environment, clear=False), patch.object(harness_worker.subprocess, "run", side_effect=observe_run):
            harness_worker.git_state(str(self.repo))
        self.assertTrue(calls)
        for observed_env in calls:
            self.assertEqual(observed_env["GIT_OPTIONAL_LOCKS"], "0")
            self.assertNotIn("GIT_DIR", observed_env)

    def test_git_observation_env_ignores_replace_object_override(self) -> None:
        original = self.base
        subprocess.run(["git", "-C", str(self.repo), "switch", "-c", "replacement-fixture", "-q"], check=True)
        (self.repo / "README.md").write_text("replacement\n")
        subprocess.run(["git", "-C", str(self.repo), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "commit", "-qm", "replacement"], check=True)
        replacement = git(self.repo, "rev-parse", "HEAD")
        subprocess.run(["git", "-C", str(self.repo), "switch", "main", "-q"], check=True)
        subprocess.run(["git", "-C", str(self.repo), "replace", original, replacement], check=True)
        try:
            with patch.dict(os.environ, {"GIT_NO_REPLACE_OBJECTS": "1"}, clear=False):
                result = subprocess.run(
                    ["git", "-C", str(self.repo), "show", "HEAD:README.md"],
                    capture_output=True,
                    text=True,
                    check=True,
                    env=harness_worker.git_observation_env(),
                )
            self.assertEqual(result.stdout, "replacement\n")
        finally:
            subprocess.run(["git", "-C", str(self.repo), "replace", "-d", original], check=True)


    def test_runtime_requires_structured_test_result_envelope(self) -> None:
        request = self.request("defect")
        with self.assertRaises(ValueError):
            harness_worker.parse_structured_output('{"runtime": {"native_session_id": "forged"}}', request, 0)


    def test_mismatched_trailing_error_does_not_override_valid_result(self) -> None:
        request = self.request("trailing-error")
        data = {"runtime": {"harness": "fake", "native_session_id": "native-1", "actual_model": "fake", "actual_effort": "low", "requested_route": "balanced", "actual_route": "balanced", "resolved_profile": "fake", "provider": "fake"}, "execution": {"status": "SUCCESS"}}
        stdout = "\n".join([json.dumps({"protocolVersion": 1, "type": "result", "command": "invoke", "exitCode": 0, "data": data}), json.dumps({"protocolVersion": 1, "type": "error", "command": "invoke", "exitCode": 1, "error": {"code": "AUTH_REQUIRED", "message": "late error"}})])
        self.assertEqual(harness_worker.parse_structured_output(stdout, request, 0), data)


    def test_resumed_runtime_id_change_fails_closed(self) -> None:
        self.run_request(self.request("defect"), "defect")
        request = self.request("fix", "resume")
        path = Path(self.tmp.name) / "request-id.yaml"; receipt_path = Path(self.tmp.name) / "receipt-id.yaml"
        path.write_text(yaml.safe_dump(request))
        result = subprocess.run([sys.executable, str(SCRIPTS / "harness_worker.py"), "run", "--request", str(path), "--registry", str(Path(self.tmp.name) / "sessions.json"), "--receipt", str(receipt_path)], text=True, capture_output=True, env={**os.environ, "HEADLESS_CLI_TEST_ONLY": "1", "NATIVE_ID": "changed"})
        self.assertNotEqual(result.returncode, 0)


    def test_failed_native_session_resume_is_exact_and_explicit(self) -> None:
        envelope = json.dumps({"protocolVersion": 1, "type": "result", "command": "invoke", "exitCode": 1, "data": {"runtime": {"harness": "fake", "native_session_id": "native-failed", "actual_model": "fake-model", "actual_effort": "low", "requested_route": "balanced", "actual_route": "balanced", "provider": "fake"}, "execution": {"status": "FAILED", "error_code": "EXECUTION_FAILED"}}})
        _, request, _ = self.run_fault("failed-resume", envelope, exit_code=1)
        request["session"]["policy"] = "resume"
        with patch.dict(os.environ, {"HEADLESS_CLI_TEST_ONLY": "1", "HEADLESS_CLI_SANDBOX_EXECUTABLE": str(self.sandbox)}, clear=False):
            receipt = harness_worker.run(request, Path(self.tmp.name) / "sessions.json", 10)
        self.assertEqual(receipt["runtime"]["session_state"], "resumed")
        self.assertEqual(receipt["runtime"]["native_session_id"], "native-failed")


    def test_active_native_lane_is_agy_only(self) -> None:
        self.assertEqual(harness_worker.NATIVE_TERMINAL_LANES, {"agy"})


if __name__ == "__main__":
    unittest.main()
