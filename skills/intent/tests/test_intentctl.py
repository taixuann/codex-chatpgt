from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

import yaml


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("intentctl", ROOT / "scripts/intentctl.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class IntentCtlTests(unittest.TestCase):
    def _run(self, origin="user_idea", depth="light"):
        return MODULE.init_run(origin, "conversation" if origin == "user_idea" else "taixuann/codex-chatpgt#96", depth, Path.cwd())

    def test_workspace_reuses_current_repository_and_instruction_chain(self):
        report = MODULE.workspace_report(Path.cwd())
        self.assertEqual(report["repo_root"], str(Path.cwd()))
        self.assertIn("AGENTS.md", report["instruction_chain"])
        self.assertNotIn("workspace", " ".join(report["instruction_chain"]))

    def test_workspace_loads_root_to_cwd_instruction_chain(self):
        report = MODULE.workspace_report(Path.cwd() / "skills" / "intent")
        self.assertEqual(report["instruction_chain"], ["AGENTS.md", "skills/AGENTS.md"])

    def test_idea_outside_git_uses_unbound_workspace_without_global_hunt(self):
        with tempfile.TemporaryDirectory() as directory:
            report = MODULE.workspace_report(Path(directory))
            self.assertIsNone(report["repo_root"])
            self.assertEqual(report["head"], "uncommitted")
            data = MODULE.init_run("user_idea", "conversation", "light", Path(directory))
            self.assertEqual(MODULE.validate_run(data), [])

    def test_user_origin_locator_uses_canonical_grammar(self):
        data = self._run()["intent_run"]
        data["origin"]["locator"] = "https://example.com/request"
        self.assertTrue(any("user locator" in error for error in MODULE.validate_run({"intent_run": data})))

    def test_relative_handoff_resolves_against_anchored_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "second-repo"
            repo.mkdir()
            MODULE.run_git(repo, "init", "-q")
            data = self._run("user_idea", "focused")
            run = data["intent_run"]
            run["workspace"]["repo_root"] = str(repo)
            run["handoff"]["packet"] = ".agents/sessions/example"
            self.assertEqual(MODULE._resolve_packet_path(run, run["handoff"]["packet"]), (repo / ".agents/sessions/example").resolve())
            self.assertTrue(MODULE._packet_is_anchored(run, repo / ".agents/sessions/example"))

    def test_absolute_or_cross_repository_packet_binding_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo_a, repo_b = root / "repo-a", root / "repo-b"
            repo_a.mkdir(); repo_b.mkdir()
            MODULE.run_git(repo_a, "init", "-q")
            MODULE.run_git(repo_b, "init", "-q")
            data = self._run("user_idea", "focused")
            run = data["intent_run"]
            run["workspace"]["repo_root"] = str(repo_a)
            self.assertTrue(MODULE._packet_is_anchored(run, repo_a / ".agents/sessions/example"))
            self.assertTrue(MODULE._packet_is_anchored(run, (repo_a / ".agents/sessions/example").resolve()))
            self.assertFalse(MODULE._packet_is_anchored(run, repo_b / ".agents/sessions/example"))

    def test_materialize_rejects_valid_packet_from_other_repository(self):
        session_spec = importlib.util.spec_from_file_location(
            "sessionctl_for_cross_repo", Path.cwd() / "skills/control-plane/session-packet-management/scripts/sessionctl.py"
        )
        assert session_spec and session_spec.loader
        sessionctl = importlib.util.module_from_spec(session_spec)
        session_spec.loader.exec_module(sessionctl)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo_a, repo_b = root / "repo-a", root / "repo-b"
            repo_a.mkdir(); repo_b.mkdir()
            for repo in (repo_a, repo_b):
                MODULE.run_git(repo, "init", "-q")
                MODULE.run_git(repo, "-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-qm", "init")
            packet_b = sessionctl.init_packet(repo_b, "20260902_cross-repo_001", "intent", "conversation")
            data = self._run("user_idea", "focused")
            run = data["intent_run"]
            run["workspace"] = MODULE.workspace_report(repo_a)
            run["handoff"]["packet"] = str(packet_b)
            run["intent"].update(objective="bounded", why="evidence", current_state="anchored", target_state="ready", success_criteria=["pass"], scope=["intent"], out_of_scope=["plan"])
            with self.assertRaises(MODULE.IntentError):
                MODULE.materialize_intent_artifact(data)

    def test_materialize_rejects_packet_with_mismatched_declared_repository(self):
        session_spec = importlib.util.spec_from_file_location(
            "sessionctl_for_declared_repo", Path.cwd() / "skills/control-plane/session-packet-management/scripts/sessionctl.py"
        )
        assert session_spec and session_spec.loader
        sessionctl = importlib.util.module_from_spec(session_spec)
        session_spec.loader.exec_module(sessionctl)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo_a, repo_b = root / "repo-a", root / "repo-b"
            repo_a.mkdir(); repo_b.mkdir()
            for repo in (repo_a, repo_b):
                MODULE.run_git(repo, "init", "-q")
                MODULE.run_git(repo, "-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-qm", "init")
            packet = sessionctl.init_packet(repo_a, "20260902_declared-repo_001", "intent", "conversation")
            session = yaml.safe_load((packet / "session.yaml").read_text())
            session["repository_root"] = str(repo_b)
            (packet / "session.yaml").write_text(yaml.safe_dump(session, sort_keys=False))
            data = self._run("user_idea", "focused")
            run = data["intent_run"]
            run["workspace"] = MODULE.workspace_report(repo_a)
            run["handoff"]["packet"] = str(packet.relative_to(repo_a))
            run["intent"].update(objective="bounded", why="evidence", current_state="anchored", target_state="ready", success_criteria=["pass"], scope=["intent"], out_of_scope=["plan"])
            self.assertFalse(MODULE._packet_declared_repo_matches(run, packet))
            self.assertIn("session_packet_anchor", MODULE.fresh_context(data)["missing"])
            with self.assertRaises(MODULE.IntentError):
                MODULE.materialize_intent_artifact(data)

    def test_dirty_fingerprint_detects_relevant_dirty_state_change(self):
        data = self._run()["intent_run"]
        data["workspace"]["dirty_fingerprint"] = "different"
        result = MODULE.staleness({"intent_run": data}, Path.cwd())
        self.assertEqual(result["freshness"], "stale_soft")

    def test_init_uses_matrix_for_issue_and_idea_profiles(self):
        for origin in ("github_issue", "user_idea"):
            for depth in ("light", "focused", "deep"):
                run = self._run(origin, depth)["intent_run"]
                self.assertEqual(run["profile"], f"{'issue' if origin == 'github_issue' else 'idea'}_{depth}")
                self.assertEqual(set(run["stages"]), set(MODULE.load_matrix()["stages"]))

    def test_confirmed_claim_requires_evidence(self):
        data = self._run()["intent_run"]
        data["claims"] = [{"id": "C1", "text": "known", "state": "CONFIRMED", "evidence": []}]
        self.assertTrue(any("confirmed claims require evidence" in e for e in MODULE.validate_run({"intent_run": data})))

    def test_readiness_passes_only_after_required_gates(self):
        data = self._run()["intent_run"]
        for stage in data["stages"].values():
            if stage["status"] == "blocked":
                stage["status"] = "passed"
                stage.pop("reason", None)
        data["evidence"] = []
        for stage in data["stages"]:
            observables = sorted({item for ref in data["procedure_trace"]["expected"].get(stage, []) for item in MODULE.load_reference_policy()["references"][ref].get("required_observables", [])})
            data["evidence"].append({"id": f"E_{stage}", "locator": f"evidence/{stage}", "kind": "procedure-output", "procedure": stage, "observables": observables, "observed_at": "2026-09-02T00:00:00Z"})
            data["stages"][stage]["evidence"] = [f"E_{stage}"]
        data["claims"] = [{"id": "C1", "text": "known", "state": "CONFIRMED", "evidence": ["E_workspace_anchor"]}]
        data["intent"].update(
            objective="A bounded objective",
            why="Current evidence requires a bounded handoff",
            current_state="The current repository state is anchored",
            target_state="A planner can continue from the handoff",
            success_criteria=["A deterministic check passes"],
            scope=["intent family"],
            out_of_scope=["implementation planning"],
        )
        data["trust"].update(completeness="complete", evidence_traceability="complete")
        data["procedure_trace"]["observed"] = data["procedure_trace"]["expected"]
        self.assertEqual(MODULE.readiness({"intent_run": data}), [])

    def test_readiness_rejects_self_attested_unobserved_references(self):
        data = self._run()["intent_run"]
        for stage in data["stages"].values():
            if stage["status"] == "blocked":
                stage["status"] = "passed"
                stage.pop("reason", None)
        data["trust"].update(completeness="complete", evidence_traceability="complete")
        errors = MODULE.readiness({"intent_run": data})
        self.assertTrue(any("not observed" in error for error in errors))

    def test_readiness_rejects_trace_copy_without_stage_evidence(self):
        data = self._run()["intent_run"]
        for stage in data["stages"].values():
            if stage["status"] == "blocked":
                stage["status"] = "passed"
                stage.pop("reason", None)
        data["procedure_trace"]["observed"] = data["procedure_trace"]["expected"]
        data["trust"].update(completeness="complete", evidence_traceability="complete")
        errors = MODULE.readiness({"intent_run": data})
        self.assertTrue(any("lacks observable evidence" in error for error in errors))

    def test_staleness_detects_changed_head_without_invalidation(self):
        data = self._run()["intent_run"]
        data["workspace"]["head"] = "0" * 40
        result = MODULE.staleness({"intent_run": data}, Path.cwd())
        self.assertEqual(result["freshness"], "stale_review_required")

    def test_readiness_blocks_without_boundary_content(self):
        data = self._run()["intent_run"]
        for stage in data["stages"].values():
            if stage["status"] == "blocked":
                stage["status"] = "passed"
                stage.pop("reason", None)
        data["trust"].update(completeness="complete", evidence_traceability="complete")
        errors = MODULE.readiness({"intent_run": data})
        self.assertTrue(any("G5 boundary field missing" in error for error in errors))

    def test_fresh_context_recovery_is_derived_from_canonical_intent(self):
        data = self._run("user_idea", "light")
        run = data["intent_run"]
        run["intent"].update(
            objective="A bounded objective",
            why="A current-state reason",
            current_state="The current repository is known",
            target_state="The planner receives sufficient context",
            success_criteria=["A check passes"],
            scope=["the relevant package"],
            out_of_scope=["implementation"],
        )
        run["evidence"] = [{"id": "E1", "locator": "AGENTS.md", "kind": "repository", "observed_at": "2026-09-02T00:00:00Z"}]
        run["trust"]["evidence_traceability"] = "complete"
        run["handoff"]["recovery"] = {"fields": {field: False for field in MODULE.RECOVERY_FIELDS}}
        result = MODULE.fresh_context(data)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["rediscovery_burden"], 0)
        self.assertEqual(result["unsupported_reconstruction"], 0)
        self.assertTrue(all(result["fields"].values()))

    def test_fresh_context_write_initializes_empty_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "intent-run.yaml"
            self.assertEqual(
                MODULE.main(
                    [
                        "init",
                        "--origin",
                        "user_idea",
                        "--locator",
                        "conversation",
                        "--output",
                        str(output),
                    ]
                ),
                0,
            )
            self.assertEqual(
                MODULE.main(["fresh-context", str(output), "--write"]),
                1,
            )
            written = yaml.safe_load(output.read_text())
            self.assertIsInstance(written["intent_run"]["handoff"]["recovery"], dict)
            self.assertIn("status", written["intent_run"]["handoff"]["recovery"])

    def test_focused_handoff_binds_materialized_intent_artifact(self):
        session_spec = importlib.util.spec_from_file_location(
            "sessionctl_for_intent", Path.cwd() / "skills/control-plane/session-packet-management/scripts/sessionctl.py"
        )
        assert session_spec and session_spec.loader
        sessionctl = importlib.util.module_from_spec(session_spec)
        session_spec.loader.exec_module(sessionctl)
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            MODULE.run_git(repo, "init", "-q")
            MODULE.run_git(repo, "-c", "user.email=test@example.com", "-c", "user.name=test", "commit", "--allow-empty", "-qm", "init")
            packet = sessionctl.init_packet(repo, "20260902_intent_001", "intent", "conversation")
            data = self._run("user_idea", "focused")
            run = data["intent_run"]
            run["workspace"] = MODULE.workspace_report(repo)
            run["handoff"]["packet"] = str(packet.relative_to(repo))
            run["intent"].update(objective="bounded", why="evidence", current_state="anchored", target_state="ready", success_criteria=["pass"], scope=["intent"], out_of_scope=["plan"])
            for stage in run["stages"]:
                run["stages"][stage]["status"] = "passed"
                run["stages"][stage].pop("reason", None)
            run["procedure_trace"]["expected"] = MODULE.expected_references(run)
            for stage in run["stages"]:
                observables = sorted({item for ref in run["procedure_trace"]["expected"].get(stage, []) for item in MODULE.load_reference_policy()["references"][ref].get("required_observables", [])})
                evidence_id = f"E_{stage}"
                run["evidence"].append({"id": evidence_id, "locator": f"evidence/{stage}", "kind": "procedure-output", "procedure": stage, "observables": observables, "observed_at": "2026-09-02T00:00:00Z"})
                run["stages"][stage]["evidence"] = [evidence_id]
            run["procedure_trace"]["observed"] = run["procedure_trace"]["expected"]
            run["trust"]["evidence_traceability"] = "complete"
            output = repo / "intent-run.yaml"
            self.assertEqual(MODULE.materialize_intent_artifact(data).resolve(), (packet / "intent.md").resolve())
            self.assertEqual(MODULE._packet_canonical_intent(run), MODULE._canonical_packet_intent(run))
            MODULE.save_run(output, data)
            self.assertEqual(MODULE.main(["fresh-context", str(output), "--write"]), 0)
            self.assertEqual(MODULE.main(["readiness", str(output)]), 0)
            text = (packet / "intent.md").read_text()
            (packet / "intent.md").write_text(text.replace("objective: bounded", "objective: tampered", 1), encoding="utf-8")
            self.assertEqual(MODULE.main(["readiness", str(output)]), 1)

    def test_behavioral_fixture_covers_required_cases(self):
        fixture = yaml.safe_load((ROOT / "tests/fixtures/behavioral-cases.yaml").read_text(encoding="utf-8"))
        self.assertEqual(len(fixture["cases"]), 15)
        self.assertTrue({"positive", "negative", "incomplete", "edge"} <= {case["class"] for case in fixture["cases"]})


if __name__ == "__main__":
    unittest.main()
