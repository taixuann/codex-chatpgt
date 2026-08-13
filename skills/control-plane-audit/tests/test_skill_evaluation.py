import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "run_skill_evaluation.py"


def load_module():
    spec = importlib.util.spec_from_file_location("run_skill_evaluation", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SkillEvaluationTests(unittest.TestCase):
    def test_evaluation_home_uses_isolated_project_local_skill_tree(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "demo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("demo", encoding="utf-8")
            (skill / "agents").mkdir()
            (skill / "agents" / "openai.yaml").write_text(
                "policy:\n  allow_implicit_invocation: false\n", encoding="utf-8"
            )
            auth_home = root / "auth-source"
            auth_home.mkdir()
            (auth_home / "auth.json").write_text("{}", encoding="utf-8")
            (root / ".tmp").mkdir()
            with patch.dict(os.environ, {"CODEX_HOME": str(auth_home)}):
                temporary = module.evaluation_home(root, "with", ["demo"])
            try:
                project_skill = Path(temporary.name) / ".agents" / "skills" / "demo"
                self.assertTrue((project_skill / "SKILL.md").exists())
                self.assertIn("allow_implicit_invocation: true", (project_skill / "agents" / "openai.yaml").read_text())
                self.assertTrue((Path(temporary.name) / "auth.json").is_symlink())
            finally:
                temporary.cleanup()

    def test_benchmark_prompt_requires_bounded_read_only_execution(self):
        module = load_module()
        prompt = module.benchmark_prompt(
            {"prompt": "Audit the control plane"}, ["control-plane-audit"], "WITH-SKILL"
        )
        self.assertIn("Perform the task in a read-only way", prompt)
        self.assertIn("modify files", prompt)

    def test_trace_parser_extracts_final_answer_usage_and_tool_events(self):
        module = load_module()
        lines = [
            '{"type":"thread.started","thread_id":"t1"}',
            '{"type":"item.completed","item":{"type":"agent_message","text":"{\\"selected_skill\\":\\"project-bootstrap\\"}"}}',
            '{"type":"item.completed","item":{"type":"command_execution","command":"pwd"}}',
            '{"type":"turn.completed","usage":{"input_tokens":12,"output_tokens":8,"total_tokens":20}}',
        ]
        trace = module.summarize_trace("".join(line + "\n" for line in lines), "")
        self.assertEqual(trace["final_answer"], '{"selected_skill":"project-bootstrap"}')
        self.assertEqual(trace["usage"]["total_tokens"], 20)
        self.assertEqual(trace["commands"], ["pwd"])

    def test_trace_parser_accepts_timeout_byte_buffers(self):
        module = load_module()
        trace = module.summarize_trace(b'{"type":"turn.started"}\n', b"network unavailable\n")
        self.assertEqual(trace["events"], 1)
        self.assertEqual(trace["stderr"], ["network unavailable"])

    def test_routing_metrics_distinguish_none_accuracy_and_false_positives(self):
        module = load_module()
        records = [
            {"expected": "project-bootstrap", "actual": "project-bootstrap", "kind": "positive"},
            {"expected": "none", "actual": "project-bootstrap", "kind": "none"},
            {"expected": "none", "actual": "none", "kind": "negative"},
            {"expected": "instruction-maintenance", "actual": "none", "kind": "oblique"},
        ]
        metrics = module.routing_metrics(records)
        self.assertEqual(metrics["true_positives"], 1)
        self.assertEqual(metrics["false_positives"], 1)
        self.assertEqual(metrics["none_accuracy"], 0.5)
        self.assertEqual(metrics["evaluated"], 4)

    def test_utility_metrics_keep_baseline_and_with_results_separate(self):
        module = load_module()
        result = module.utility_metrics(
            [
                {"with_status": "pass", "without_status": "fail", "with_tokens": 20, "without_tokens": 10},
                {"with_status": "pass", "without_status": "pass", "with_tokens": 30, "without_tokens": 25},
            ]
        )
        self.assertEqual(result["load_bearing_passes"], 1)
        self.assertEqual(result["redundancy_candidates"], 1)
        self.assertEqual(result["token_delta_total"], 15)

    def test_regression_record_is_observation_only(self):
        module = load_module()
        record = module.regression_record(
            {"id": "case-1", "prompt": "Do the thing", "expected": "one"},
            {"actual": "two", "selection_source": "final_response_self_report"},
        )
        self.assertEqual(record["expected"], "one")
        self.assertEqual(record["actual"], "two")
        self.assertEqual(record["governance"], "OBSERVE -> PROPOSE -> REVIEW -> ACCEPT -> UPDATE")
        self.assertNotIn("catalog", record)


if __name__ == "__main__":
    unittest.main()
