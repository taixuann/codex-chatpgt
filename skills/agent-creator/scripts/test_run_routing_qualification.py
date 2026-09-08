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
    def test_expected_matrix_has_three_prompt_variants(self):
        self.assertEqual(len(MODULE.ROUTING_VARIANTS), 7)
        self.assertTrue(all(len(variants) == 3 for variants in MODULE.ROUTING_VARIANTS.values()))
        self.assertEqual(len(MODULE.MISSING_VARIANTS), 4)

    def test_wrong_owner_is_rejected(self):
        rows = []
        for index in range(3):
            rows.append(
                {
                    "lane": "routing",
                    "case_id": "ROUTE-01",
                    "variant": index + 1,
                    "model": MODULE.MODEL,
                    "reasoning": MODULE.REASONING,
                    "exit_code": 0,
                    "verdict": "OBSERVED",
                    "selected_owner": "skill-creator",
                    "expected_owner": "agent-creator",
                    "capture_revision": "0" * 40,
                }
            )
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl") as handle:
            handle.write("\n".join(json.dumps(row) for row in rows) + "\n")
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_receipts(Path(handle.name), Path(__file__).parents[3])


if __name__ == "__main__":
    unittest.main()
