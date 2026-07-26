import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "factory.py"


class FactoryTests(unittest.TestCase):
    def run_factory(self, payload):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            request = root / "request.yaml"
            output = root / "output"
            request.write_text(payload, encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCRIPT), str(request), "--output-root", str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            manifest = next(output.glob("*/manifest.yaml"))
            return result, manifest.read_text(encoding="utf-8")

    def test_existing_skill_generates_proposed_package(self):
        result, manifest = self.run_factory(
            """request_id: valid-request
purpose: Audit the control plane
roles: [franky]
mode: workflow_only
capabilities:
  - id: audit
    description: Audit the Franky control plane
    skill: franky-maintenance
    operation: audit_maintenance_scope
    inputs: [scope]
    outputs: [audit report]
    validation: [scope is explicit]
"""
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("status: proposed", manifest)
        self.assertNotIn("severity: critical", manifest)

    def test_missing_capabilities_is_blocked(self):
        result, manifest = self.run_factory(
            "request_id: incomplete-request\npurpose: Design a workflow\nroles: [franky]\n"
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("code: missing_capabilities", manifest)

    def test_unknown_role_is_blocked(self):
        result, manifest = self.run_factory(
            "request_id: bad-role\npurpose: Do work\nroles: [unknown]\ncapabilities: [{id: work, description: do work}]\n"
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("code: unknown_role", manifest)


if __name__ == "__main__":
    unittest.main()
