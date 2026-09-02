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
        data["evidence"] = [{"id": "E1", "locator": "AGENTS.md", "kind": "repository", "observed_at": "2026-09-02T00:00:00Z"}]
        data["claims"] = [{"id": "C1", "text": "known", "state": "CONFIRMED", "evidence": ["E1"]}]
        data["intent"].update(
            objective="A bounded objective",
            why="Current evidence requires a bounded handoff",
            success_criteria=["A deterministic check passes"],
            scope=["intent family"],
            out_of_scope=["implementation planning"],
        )
        data["trust"].update(completeness="complete", evidence_traceability="complete")
        self.assertEqual(MODULE.readiness({"intent_run": data}), [])

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

    def test_behavioral_fixture_covers_required_cases(self):
        fixture = yaml.safe_load((ROOT / "tests/fixtures/behavioral-cases.yaml").read_text(encoding="utf-8"))
        self.assertEqual(len(fixture["cases"]), 15)
        self.assertTrue({"positive", "negative", "incomplete", "edge"} <= {case["class"] for case in fixture["cases"]})


if __name__ == "__main__":
    unittest.main()
