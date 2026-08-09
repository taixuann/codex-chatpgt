import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml


SCRIPT = Path(__file__).parents[1] / "bootstrap_file_project.py"


def load_module():
    spec = importlib.util.spec_from_file_location("bootstrap_file_project", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BootstrapFileProjectTests(unittest.TestCase):
    def test_adaptive_materialization_creates_only_declared_files(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = {
                "project": {"name": "iv-notes", "purpose": "metadata orientation", "mode": "new"},
                "artifacts": [
                    {"path": "README.md", "purpose": "orientation", "format": "markdown", "content": "# IV notes\n"},
                    {"path": "project.yaml", "purpose": "profile", "format": "yaml", "links": ["external://literature-wiki"], "content": "name: iv-notes\n"},
                    {"path": "experiments/iv/metadata/README.md", "purpose": "metadata", "format": "markdown", "depends_on": ["project.yaml"], "content": "# Metadata\n"},
                ],
            }
            actions = module.materialize(module.validate_map(data), root, True)
            self.assertEqual(len(actions), 3)
            self.assertEqual(sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()), [
                "README.md", "experiments/iv/metadata/README.md", "project.yaml"
            ])
            self.assertFalse((root / "samples").exists())
            self.assertFalse((root / "workflows").exists())

    def test_dry_run_does_not_write(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = {"project": {"name": "x", "purpose": "y", "mode": "new"}, "artifacts": [{"path": "README.md", "content": "# x\n"}]}
            module.materialize(module.validate_map(data), root, False)
            self.assertFalse((root / "README.md").exists())

    def test_rejects_raw_data_and_control_plane_paths(self):
        module = load_module()
        raw_map = {"project": {"name": "x", "purpose": "y", "mode": "new"}, "artifacts": [{"path": "data/raw/input.csv", "content": "bad"}]}
        with self.assertRaises(module.BootstrapError):
            module.validate_map(raw_map)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw_path = root / "data/raw/input.csv"
            raw_path.parent.mkdir(parents=True)
            raw_path.write_text("immutable\n", encoding="utf-8")
            raw_map["artifacts"][0]["intent"] = "preserve"
            actions = module.materialize(module.validate_map(raw_map), root, True)
            self.assertEqual(actions, ["preserve data/raw/input.csv"])
        with self.assertRaises(module.BootstrapError):
            module.validate_map({"project": {"name": "x", "purpose": "y", "mode": "new"}, "artifacts": [{"path": "agents/demo.toml", "content": "bad"}]})

    def test_rejects_malformed_artifact_entries_with_bootstrap_error(self):
        module = load_module()
        with self.assertRaises(module.BootstrapError):
            module.validate_map({
                "project": {"name": "x", "purpose": "y", "mode": "new"},
                "artifacts": ["not-a-mapping"],
            })

    def test_cli_dry_run_then_apply_is_file_first(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            artifact_map = root / "artifact-map.yaml"
            output = root / "project"
            artifact_map.write_text(yaml.safe_dump({
                "project": {"name": "iv-notes", "purpose": "measurement orientation", "mode": "new"},
                "artifacts": [
                    {"path": "README.md", "purpose": "orientation", "content": "# IV notes\n"},
                    {"path": "project.yaml", "purpose": "external references", "links": ["external://literature-wiki", "external://openscience"], "content": "name: iv-notes\n"},
                    {"path": "experiments/electrical-iv/metadata/README.md", "purpose": "measurement metadata", "depends_on": ["project.yaml"], "content": "# Metadata\n"},
                ],
            }, sort_keys=False), encoding="utf-8")
            command = ["python3", str(SCRIPT), str(artifact_map), str(output)]
            dry = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(dry.returncode, 0, dry.stdout + dry.stderr)
            self.assertFalse(output.exists())
            applied = subprocess.run(command + ["--apply"], capture_output=True, text=True, check=False)
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            self.assertEqual(len([path for path in output.rglob("*") if path.is_file()]), 3)
            self.assertFalse((output / "samples").exists())

    def test_existing_project_updates_declared_file_only(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = root / "project.yaml"
            unrelated = root / "notes.md"
            profile.write_text("name: old\n", encoding="utf-8")
            unrelated.write_text("keep\n", encoding="utf-8")
            data = {
                "project": {"name": "iv-notes", "purpose": "update profile", "mode": "existing"},
                "artifacts": [{"path": "project.yaml", "intent": "update", "content": "name: new\n"}],
            }
            module.materialize(module.validate_map(data), root, True)
            self.assertEqual(profile.read_text(encoding="utf-8"), "name: new\n")
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep\n")


if __name__ == "__main__":
    unittest.main()
