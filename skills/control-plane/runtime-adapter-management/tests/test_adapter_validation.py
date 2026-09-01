from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).parents[1]
VALIDATOR = ROOT / "scripts/validate_agent_toml.py"
REPO_ROOT = ROOT.parents[2]


class AdapterValidationTests(unittest.TestCase):
    def test_canonical_franky_adapter_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(REPO_ROOT / "agents/franky.toml")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_template_passes_structural_validation(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(ROOT / "templates/agent.toml")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
