from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("sessionctl", ROOT / "scripts/sessionctl.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class SessionCtlTests(unittest.TestCase):
    def _repo(self) -> Path:
        root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "test"], check=True)
        (root / "README.md").write_text("test\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "init"], check=True)
        return root

    def test_intent_init_uses_unified_location_and_validates(self):
        repo = self._repo()
        packet = MODULE.init_packet(repo, "20260902_idea-example_001", "intent", "conversation")
        self.assertEqual(packet, repo / ".agents/sessions/20260902_idea-example_001")
        self.assertTrue((packet / "intent.md").is_file())
        self.assertFalse((packet / "plan.md").exists())
        validator = ROOT / "scripts/validate_session_packet.py"
        result = subprocess.run(["python3", str(validator), str(packet)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_plan_init_extends_same_packet_with_plan(self):
        repo = self._repo()
        packet = MODULE.init_packet(repo, "20260902_issue-example_001", "plan", "org/repo#1")
        self.assertEqual(packet.parent, repo / ".agents/sessions")
        self.assertTrue((packet / "intent.md").is_file())
        self.assertTrue((packet / "plan.md").is_file())

    def test_advance_extends_existing_intent_packet(self):
        repo = self._repo()
        packet = MODULE.init_packet(repo, "20260902_idea-advance_001", "intent", "conversation")
        MODULE.advance_packet(packet, "plan")
        self.assertTrue((packet / "plan.md").is_file())
        session = (packet / "session.yaml").read_text(encoding="utf-8")
        self.assertIn("stage: plan", session)
        validator = ROOT / "scripts/validate_session_packet.py"
        result = subprocess.run(["python3", str(validator), str(packet)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
