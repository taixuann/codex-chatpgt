import unittest

from ops.scripts.validate_franky_documentation_impact import required_surfaces


class DocumentationImpactTests(unittest.TestCase):
    def test_control_plane_paths_require_canonical_review_surfaces(self):
        surfaces = required_surfaces(["agents/franky.toml", "ops/scripts/example.py"])
        self.assertEqual(
            surfaces,
            {"agent-guidance", "current-state", "operating-workflow", "validation-contracts"},
        )

    def test_absolute_and_traversal_paths_are_rejected(self):
        for path in ("/Users/tai/.codex/agents/franky.toml", "../agents/franky.toml"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    required_surfaces([path])


if __name__ == "__main__":
    unittest.main()
