from pathlib import Path
import sys
import tempfile
import shutil
import subprocess
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))
from scripts.run_non_interactive_handoff import _argv, get_repo_root, run_non_interactive_handoff


class NonInteractiveRunnerTests(unittest.TestCase):
    def test_runner_uses_argv_tokens(self):
        self.assertEqual(_argv("echo safe"), ["echo", "safe"])

    def test_shell_operators_are_rejected(self):
        with self.assertRaises(ValueError):
            _argv(["echo", "safe", ";", "touch", "/tmp/unexpected"])

    def test_repository_root_is_verified(self):
        root = get_repo_root()
        self.assertTrue((root / "ops" / "schemas" / "franky-task.schema.yaml").is_file())
        self.assertTrue((root / "manifests" / "agent-repertoires.yaml").is_file())

    def test_consequential_runner_rejects_omitted_root(self):
        with self.assertRaisesRegex(ValueError, "explicit --repo-root"):
            run_non_interactive_handoff(["echo", "safe"])

    def test_consequential_runner_rejects_unverified_root(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "installed control-plane root|control-plane repository root"):
                run_non_interactive_handoff(["echo", "safe"], repo_root=Path(directory))

    def test_copied_marker_git_root_with_canonical_origin_is_rejected(self):
        source = get_repo_root()
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / "fake-root"
            for relative in ("AGENTS.md", "agents/AGENTS.md", "skills/AGENTS.md", "documentation/OPERATING-WORKFLOW.md", "ops/schemas/franky-task.schema.yaml", "ops/schemas/franky-result.schema.yaml", "manifests/agent-repertoires.yaml"):
                target = fake / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source / relative, target)
            subprocess.run(["git", "init", "-q", str(fake)], check=True)
            subprocess.run(["git", "-C", str(fake), "remote", "add", "origin", "git@github.com:taixuann/codex-chatpgt.git"], check=True)
            with self.assertRaisesRegex(RuntimeError, "installed control-plane root"):
                run_non_interactive_handoff(["echo", "safe"], repo_root=fake)


if __name__ == "__main__":
    unittest.main()
