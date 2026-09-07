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


if __name__ == "__main__":
    unittest.main()
