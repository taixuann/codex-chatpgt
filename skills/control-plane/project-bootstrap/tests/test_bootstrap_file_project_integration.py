import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml


SCRIPT = Path(__file__).parents[1] / "scripts" / "bootstrap_file_project.py"


class ScientificFileFirstLifecycleTests(unittest.TestCase):
    def test_scientific_lifecycle_is_file_first_and_repairable(self):
        """Exercise the bounded scientific project path through the public CLI."""
        with tempfile.TemporaryDirectory() as temp:
            workspace = Path(temp)
            project = workspace / "iv-project"
            project.mkdir()

            raw = project / "data" / "raw" / "run-001.csv"
            raw.parent.mkdir(parents=True)
            raw.write_text("voltage,current\n0,0\n1,2\n", encoding="utf-8")
            raw_digest = hashlib.sha256(raw.read_bytes()).hexdigest()
            preexisting = project / "operator-notes.md"
            preexisting.write_text("retain this unrelated file\n", encoding="utf-8")

            artifact_map = workspace / "artifact-map.yaml"
            artifacts = [
                {
                    "path": "data/raw/run-001.csv",
                    "intent": "preserve",
                    "purpose": "immutable instrument evidence",
                },
                {
                    "path": "project.yaml",
                    "purpose": "project profile and knowledge pointers",
                    "links": ["external://literature-wiki", "external://openscience"],
                    "content": (
                        "name: iv-project\n"
                        "knowledge:\n"
                        "  wiki: external://literature-wiki\n"
                        "  openscience: external://openscience\n"
                    ),
                },
                {
                    "path": "experiments/iv/metadata.yaml",
                    "purpose": "measurement context",
                    "content": "run: run-001\ntechnique: electrical-iv\n",
                },
                {
                    "path": "data/processed/run-001.csv",
                    "purpose": "derived data without changing raw evidence",
                    "depends_on": ["data/raw/run-001.csv"],
                    "content": "voltage,current\n0,0\n1,2\n",
                },
                {
                    "path": "analysis/run-001.md",
                    "purpose": "analysis interpretation",
                    "depends_on": ["data/processed/run-001.csv"],
                    "content": "# Run 001\nProcessed data are ready for review.\n",
                },
                {
                    "path": "results/run-001.csv",
                    "purpose": "reviewable result output",
                    "depends_on": ["analysis/run-001.md"],
                    "content": "metric,value\nslope,2\n",
                },
            ]
            request = {
                "project": {
                    "name": "iv-project",
                    "purpose": "file-first electrical measurement record",
                    "mode": "existing",
                },
                "artifacts": artifacts,
            }

            def write_request(raw_intent: str) -> None:
                artifacts[0]["intent"] = raw_intent
                artifact_map.write_text(
                    yaml.safe_dump(request, sort_keys=False), encoding="utf-8"
                )

            command = [sys.executable, str(SCRIPT), str(artifact_map), str(project)]

            # A dry-run validates the complete map but leaves even new parent
            # directories untouched.
            write_request("preserve")
            dry_run = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(dry_run.returncode, 0, dry_run.stdout + dry_run.stderr)
            self.assertIn("OK DRY-RUN", dry_run.stdout)
            self.assertFalse((project / "project.yaml").exists())
            self.assertFalse((project / "data" / "processed").exists())
            self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(), raw_digest)

            # An unsafe raw create request fails before any declared output is
            # written. Repairing only that intent restores the bounded path.
            write_request("create")
            failed = subprocess.run(command + ["--apply"], capture_output=True, text=True, check=False)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("FAIL bootstrap", failed.stdout)
            self.assertFalse((project / "project.yaml").exists())
            self.assertFalse((project / "data" / "processed").exists())
            self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(), raw_digest)

            write_request("preserve")
            applied = subprocess.run(command + ["--apply"], capture_output=True, text=True, check=False)
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            self.assertIn("OK APPLIED", applied.stdout)

            expected_files = {
                "operator-notes.md",
                "data/raw/run-001.csv",
                "project.yaml",
                "experiments/iv/metadata.yaml",
                "data/processed/run-001.csv",
                "analysis/run-001.md",
                "results/run-001.csv",
            }
            actual_files = {
                path.relative_to(project).as_posix()
                for path in project.rglob("*")
                if path.is_file()
            }
            self.assertEqual(actual_files, expected_files)
            self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(), raw_digest)
            self.assertIn("external://literature-wiki", (project / "project.yaml").read_text(encoding="utf-8"))
            self.assertIn("external://openscience", (project / "project.yaml").read_text(encoding="utf-8"))

            # Optional surfaces are selected by project need, not emitted as a
            # static scaffold for this experiment-only fixture.
            for optional in (
                "research",
                "samples",
                "figures",
                "manuscript",
                "tools",
                "workflows",
                "skills",
                "agents",
            ):
                self.assertFalse((project / optional).exists(), optional)


if __name__ == "__main__":
    unittest.main()
