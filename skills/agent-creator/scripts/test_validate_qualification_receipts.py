import copy
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_qualification_receipts.py")
SPEC = importlib.util.spec_from_file_location("validate_qualification_receipts", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

RECEIPTS = SCRIPT.parent.parent / "references" / "qualification-receipts.jsonl"
EXCLUSIONS = SCRIPT.parent.parent / "references" / "qualification-exclusions.jsonl"


class QualificationReceiptTests(unittest.TestCase):
    def test_current_receipts_derive_all_lanes(self):
        records = MODULE.load_records(RECEIPTS)
        self.assertEqual(MODULE.validate(records), {"HR-01": 10, "HR-02": 10, "HR-03": 10})

    def test_invalid_artifact_result_is_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-02")
        target["evidence"]["artifact_valid"] = False
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_invalid_process_result_is_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-03")
        target["marker"] = "present"
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_exclusion_ledger_is_validated(self):
        self.assertEqual(MODULE.validate_exclusions(EXCLUSIONS), 8)

    def test_unclassified_sandbox_violation_is_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["trace_events"]["sandbox_violation"])
        target["evidence"].pop("sandbox_disposition")
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_prompt_constraint_does_not_prove_hr03_behavior(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-03")
        target["evidence"]["probe_denied"] = False
        target["evidence"]["delegation_constraint_read"] = True
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_shared_artifact_path_is_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-02" and record["run"] == 2)
        target["artifact_path"] = "fixture-1/result.json"
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_model_prose_does_not_prove_hr01_no_mutation(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-01")
        target["evidence"]["state_after_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)


if __name__ == "__main__":
    unittest.main()
