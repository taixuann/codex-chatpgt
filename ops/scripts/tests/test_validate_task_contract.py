import tempfile
import unittest
from pathlib import Path

import yaml

from ops.scripts.validate_task_contract import validate


VALID = Path(__file__).resolve().parents[2] / "schemas/examples/task-contract.yaml"


class TaskContractValidatorTests(unittest.TestCase):
    def test_checked_in_contract_is_valid(self):
        validate(VALID)

    def test_unknown_field_is_rejected(self):
        contract = yaml.safe_load(VALID.read_text(encoding="utf-8"))
        contract["unexpected"] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.yaml"
            path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate(path)


if __name__ == "__main__":
    unittest.main()
