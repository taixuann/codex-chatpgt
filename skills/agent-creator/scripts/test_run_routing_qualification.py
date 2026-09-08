import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("run_routing_qualification.py")
SPEC = importlib.util.spec_from_file_location("run_routing_qualification", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class RoutingQualificationTests(unittest.TestCase):
    @staticmethod
    def _capture(repo: Path) -> str:
        return __import__("subprocess").check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

    @classmethod
    def _rows(cls, lane: str, repo: Path) -> list[dict]:
        capture = cls._capture(repo)
        if lane == "routing":
            keys = [(case_id, variant) for case_id, variants in MODULE.ROUTING_VARIANTS.items() for variant in range(1, len(variants) + 1)]
        else:
            keys = [("MISSING-CAPABILITY", variant) for variant in range(1, len(MODULE.MISSING_VARIANTS) + 1)]
        return [
            {
                "lane": lane,
                "case_id": case_id,
                "variant": variant,
                "model": MODULE.MODEL,
                "reasoning": MODULE.REASONING,
                "exit_code": 124,
                "verdict": "NOT_ASSESSED",
                "qualification_status": "NOT_ASSESSED",
                "failure_class": "TIMEOUT_NO_EVENT",
                "expected_owner": "agent-creator" if lane == "routing" else "NEEDS_SKILL",
                "capture_revision": capture,
                "source_fingerprint": MODULE.source_fingerprint(repo),
            }
            for case_id, variant in keys
        ]

    def test_expected_matrix_has_three_prompt_variants(self):
        self.assertEqual(len(MODULE.ROUTING_VARIANTS), 7)
        self.assertTrue(all(len(variants) == 3 for variants in MODULE.ROUTING_VARIANTS.values()))
        self.assertEqual(len(MODULE.MISSING_VARIANTS), 4)

    def test_wrong_owner_is_rejected(self):
        repo = Path(__file__).parents[3]
        rows = self._rows("routing", repo)
        target = rows[0]
        target.update({"exit_code": 0, "verdict": "OBSERVED", "qualification_status": "PASS", "selected_owner": "skill-creator"})
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl") as handle:
            handle.write("\n".join(json.dumps(row) for row in rows) + "\n")
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_receipts(Path(handle.name), repo)

    def test_routing_requires_exact_keyset(self):
        repo = Path(__file__).parents[3]
        rows = self._rows("routing", repo)[:-1]
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl") as handle:
            handle.write("\n".join(json.dumps(row) for row in rows) + "\n")
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_receipts(Path(handle.name), repo)

    def test_missing_capability_requires_exact_keyset(self):
        repo = Path(__file__).parents[3]
        rows = self._rows("missing-capability", repo)[:-1]
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl") as handle:
            handle.write("\n".join(json.dumps(row) for row in rows) + "\n")
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_receipts(Path(handle.name), repo)

    def test_source_fingerprint_mismatch_is_rejected(self):
        repo = Path(__file__).parents[3]
        rows = self._rows("routing", repo)
        rows[0]["source_fingerprint"][MODULE.ROUTING_SOURCE_PATHS[0]] = "0" * 64
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl") as handle:
            handle.write("\n".join(json.dumps(row) for row in rows) + "\n")
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_receipts(Path(handle.name), repo)

    def test_invalid_timeout_shape_is_rejected(self):
        repo = Path(__file__).parents[3]
        rows = self._rows("routing", repo)
        rows[0]["failure_class"] = "TIMEOUT"
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl") as handle:
            handle.write("\n".join(json.dumps(row) for row in rows) + "\n")
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_receipts(Path(handle.name), repo)

    def test_mixed_capture_revisions_are_rejected(self):
        repo = Path(__file__).parents[3]
        rows = self._rows("routing", repo)
        rows[1]["capture_revision"] = "0" * 40
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl") as handle:
            handle.write("\n".join(json.dumps(row) for row in rows) + "\n")
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_receipts(Path(handle.name), repo)

    def test_timeout_classification_separates_event_presence(self):
        self.assertEqual(MODULE.classify_failure("", "", True, 124), "TIMEOUT_NO_EVENT")
        self.assertEqual(MODULE.classify_failure("event", "", True, 124), "TIMEOUT_AFTER_EVENT")


if __name__ == "__main__":
    unittest.main()
