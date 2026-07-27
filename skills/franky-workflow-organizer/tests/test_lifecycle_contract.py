import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path("/Users/tai/.codex/workflows/franky")
SCRIPT = Path("/Users/tai/.codex/skills/franky-workflow-organizer/scripts/validate_lifecycle_contract.py")


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_lifecycle_contract", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LifecycleContractTests(unittest.TestCase):
    def copy_root(self, root):
        for path in ROOT.glob("*.yaml"):
            (root / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    def test_current_entrypoint_matches_canonical_contract(self):
        load_validator().validate(ROOT)

    def test_missing_handoff_field_is_rejected(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.copy_root(root)
            lifecycle = yaml.safe_load((root / "lifecycle-contract.yaml").read_text(encoding="utf-8"))
            lifecycle["handoff"]["required_fields"].remove("change_id")
            (root / "lifecycle-contract.yaml").write_text(yaml.safe_dump(lifecycle, sort_keys=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.validate(root)

    def test_canonical_apply_must_emit_lifecycle_handoff(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.copy_root(root)
            canonical_path = root / "franky.yaml"
            canonical = yaml.safe_load(canonical_path.read_text(encoding="utf-8"))
            apply_step = next(step for step in canonical["steps"] if step["id"] == "apply")
            apply_step["outputs"].remove("lifecycle handoff envelope")
            canonical_path.write_text(yaml.safe_dump(canonical, sort_keys=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.validate(root)

    def test_wrong_version_is_rejected(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.copy_root(root)
            lifecycle_path = root / "lifecycle-contract.yaml"
            lifecycle = yaml.safe_load(lifecycle_path.read_text(encoding="utf-8"))
            lifecycle["version"] = 99
            lifecycle_path.write_text(yaml.safe_dump(lifecycle, sort_keys=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.validate(root)

    def test_purpose_and_branch_mismatch_is_rejected(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.copy_root(root)
            canonical_path = root / "franky.yaml"
            canonical = yaml.safe_load(canonical_path.read_text(encoding="utf-8"))
            canonical["retired_entrypoint_ids"].remove("WF-FRANKY-MAINTENANCE")
            canonical_path.write_text(yaml.safe_dump(canonical, sort_keys=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.validate(root)

    def test_cross_scope_target_is_rejected(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.copy_root(root)
            canonical_path = root / "franky.yaml"
            canonical = yaml.safe_load(canonical_path.read_text(encoding="utf-8"))
            canonical["lifecycle_ref"]["workflow_id"] = "WF-M1-001"
            canonical_path.write_text(yaml.safe_dump(canonical, sort_keys=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.validate(root)


if __name__ == "__main__":
    unittest.main()
