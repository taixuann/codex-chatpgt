import importlib.util
import tempfile
import unittest
from pathlib import Path



SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_skill_evidence.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_skill_evidence", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SkillEvidenceTests(unittest.TestCase):
    def test_accepts_complete_evidence_envelope(self):
        module = load_module()
        data = {
            "schema_version": 1,
            "status": "NOT_ASSESSED",
            "invocation_policy": {"host_field": "x", "rules": {name: False for name in ("KEEP_without_behavioral_PASS", "ADAPT", "EXPLICIT_ONLY", "REFERENCE_ONLY", "MERGE", "RETIRE")}},
            "provenance": {"runtime": "codex-cli", "model": "model", "trace_format": "jsonl"},
            "routing_benchmark": {"status": "NOT_ASSESSED", "fixture": "fixture", "cases": 60, "cases_per_canonical_skill": 10, "co_loaded_active_set": ["a", "b", "c", "d", "e", "f"], "repeats_requested": 3},
            "utility_ab": {"status": "NOT_ASSESSED", "protocol": "same context", "with_condition": "with", "without_condition": "without"},
            "efficiency_interference": {"status": "NOT_ASSESSED", "measures": ["tokens"]},
            "adapt_tournament": {"status": "NOT_ASSESSED", "first_round": ["a", "b", "c"]},
            "regression_harvesting": {"status": "READY", "governance": "OBSERVE -> PROPOSE -> REVIEW -> ACCEPT -> UPDATE", "catalog_or_description_self_mutation": False},
        }
        self.assertEqual(module.validate_evidence(data), [])

    def test_rejects_missing_behavioral_dimensions(self):
        module = load_module()
        self.assertTrue(module.validate_evidence({"schema_version": 1}))


if __name__ == "__main__":
    unittest.main()
