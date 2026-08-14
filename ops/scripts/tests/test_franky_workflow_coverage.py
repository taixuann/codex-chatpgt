from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "franky-validate.yml"


class FrankyWorkflowCoverageTests(unittest.TestCase):
    def setUp(self):
        self.workflow = WORKFLOW.read_text()

    def event_paths(self, event):
        match = re.search(
            rf"^  {event}:\n(?P<body>(?:^    .*\n|^$)*)",
            self.workflow,
            flags=re.MULTILINE,
        )
        self.assertIsNotNone(match, f"missing {event} trigger")
        return set(re.findall(r"^      - '([^']+)'$", match["body"], re.MULTILINE))

    def test_manual_validation_remains_available(self):
        self.assertIn("  workflow_dispatch:\n", self.workflow)

    def test_push_and_pull_request_cover_all_validated_surfaces(self):
        required = {
            "AGENTS.md",
            "agents/**",
            "skills/**",
            "documentation/**",
            "manifests/**",
            "ops/**",
            ".github/workflows/franky-validate.yml",
        }
        for event in ("push", "pull_request"):
            with self.subTest(event=event):
                self.assertEqual(required, self.event_paths(event))


if __name__ == "__main__":
    unittest.main()
