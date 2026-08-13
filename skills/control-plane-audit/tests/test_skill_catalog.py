import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_skill_catalog.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_skill_catalog", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SkillCatalogTests(unittest.TestCase):
    def _write_skill(self, root: Path, name: str, policy: str = "") -> None:
        skill_dir = root / "skills" / name
        (skill_dir / "agents").mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: A sufficiently specific skill description.\n---\n"
            "# Contract\n\nTrigger\nInputs\nOutput\nBoundary\nStop\nValidation\n",
            encoding="utf-8",
        )
        (skill_dir / "agents" / "openai.yaml").write_text(
            "interface:\n  display_name: Test\n"
            + (f"policy:\n  allow_implicit_invocation: {policy}\n" if policy else ""),
            encoding="utf-8",
        )

    def test_non_keep_requires_implicit_invocation_disabled(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_skill(root, "one", "true")
            catalog = {
                "schema_version": 1,
                "dispositions": {"EXPLICIT_ONLY": ["one"]},
                "canonical_active": [],
            }
            errors = module.validate_catalog(root, catalog, {"one"})
            self.assertTrue(any("allow_implicit_invocation must be false" in error for error in errors))

    def test_keep_candidate_without_behavioral_pass_must_be_disabled(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_skill(root, "one", "true")
            catalog = {
                "schema_version": 1,
                "dispositions": {"KEEP": ["one"]},
                "canonical_active": ["one"],
                "capability_keys": {"one": "one"},
                "evidence": {
                    "one": {
                        "utility": "PASS",
                        "structural": "PASS",
                        "behavioral": "NOT_ASSESSED",
                        "basis": "bounded evidence",
                    }
                },
            }
            errors = module.validate_catalog(root, catalog, {"one"})
            self.assertTrue(any("KEEP candidate must disable" in error for error in errors))

    def test_keep_with_behavioral_pass_may_enable_implicit_invocation(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_skill(root, "one", "true")
            catalog = {
                "schema_version": 1,
                "dispositions": {"KEEP": ["one"]},
                "canonical_active": ["one"],
                "capability_keys": {"one": "one"},
                "evidence": {
                    "one": {
                        "utility": "PASS",
                        "structural": "PASS",
                        "behavioral": "PASS",
                        "basis": "bounded evidence",
                    }
                },
            }
            errors = module.validate_catalog(root, catalog, {"one"})
            self.assertFalse(any("allow_implicit_invocation" in error for error in errors))

    def test_rejects_duplicate_or_missing_dispositions(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "skills" / "one").mkdir(parents=True)
            (root / "skills" / "two").mkdir(parents=True)
            for name in ("one", "two"):
                (root / "skills" / name / "SKILL.md").write_text(
                    f"---\nname: {name}\ndescription: A sufficiently specific skill description.\n---\n",
                    encoding="utf-8",
                )
            catalog = {"schema_version": 1, "dispositions": {"KEEP": ["one", "one"]}}
            errors = module.validate_catalog(root, catalog, {"one", "two"})
            self.assertTrue(any("exactly one disposition" in error for error in errors))

    def test_canonical_active_requires_utility_evidence(self):
        module = load_module()
        catalog = {
            "schema_version": 1,
            "canonical_active": ["one"],
            "dispositions": {"KEEP": ["one"]},
            "evidence": {"one": {"utility": "NOT_ASSESSED"}},
        }
        errors = module.validate_catalog(Path("."), catalog, {"one"})
        self.assertTrue(any("utility evidence" in error for error in errors))

    def test_rejects_duplicate_canonical_capability_keys(self):
        module = load_module()
        catalog = {
            "schema_version": 1,
            "canonical_active": ["one", "two"],
            "dispositions": {"KEEP": ["one", "two"]},
            "capability_keys": {"one": "same", "two": "same"},
            "evidence": {
                name: {
                    "utility": "PASS",
                    "structural": "PASS",
                    "behavioral": "NOT_ASSESSED",
                    "basis": "bounded evidence",
                }
                for name in ("one", "two")
            },
        }
        errors = module.validate_catalog(Path("."), catalog, {"one", "two"})
        self.assertTrue(any("duplicate capability keys" in error for error in errors))

    def test_repository_catalog_is_complete(self):
        module = load_module()
        root = Path(__file__).parents[3]
        catalog = yaml.safe_load((root / "manifests" / "skill-catalog.yaml").read_text())
        tracked = set(module.tracked_skill_names(root))
        self.assertEqual(module.validate_catalog(root, catalog, tracked), [])


if __name__ == "__main__":
    unittest.main()
