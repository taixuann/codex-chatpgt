import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[3]


def load_roles():
    return {
        path.stem: tomllib.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "agents").glob("*.toml"))
    }


class RoleContractTests(unittest.TestCase):
    def test_standalone_shape_and_sandbox(self):
        roles = load_roles()
        self.assertEqual(set(roles), {"athena", "franky", "prometheus"})
        self.assertEqual(roles["franky"]["sandbox_mode"], "workspace-write")
        self.assertEqual(roles["prometheus"]["sandbox_mode"], "workspace-write")
        self.assertEqual(roles["athena"]["sandbox_mode"], "read-only")
        self.assertEqual(roles["athena"]["model"], "gpt-5.6-luna")
        self.assertEqual(roles["athena"]["model_reasoning_effort"], "max")
        self.assertIn("Luna Max", roles["athena"]["developer_instructions"])
        for name, role in roles.items():
            self.assertEqual(role["name"], name)
            self.assertTrue(role["description"].strip())
            self.assertTrue(role["developer_instructions"].strip())

    def test_description_and_developer_instructions_are_separate(self):
        roles = load_roles()
        self.assertIn("substrate", roles["franky"]["description"])
        self.assertIn("workspace-write", roles["prometheus"]["description"])
        self.assertIn("independent", roles["athena"]["description"])
        self.assertNotIn("athena.review.v1", roles["athena"]["developer_instructions"])
        self.assertNotIn("athena.review-result.v1", roles["athena"]["developer_instructions"])
        self.assertNotIn("Evaluate one explicit review class", roles["athena"]["developer_instructions"])

    def test_role_boundaries_do_not_reintroduce_audited_residue(self):
        roles = load_roles()
        self.assertNotIn("workspace-write\n  runtime instance", roles["franky"]["developer_instructions"])
        self.assertIn("explicit mutation authority", roles["franky"]["developer_instructions"])
        self.assertNotIn("audit documentation and artifact lifecycle completeness", roles["prometheus"]["developer_instructions"])
        self.assertNotIn("deterministic validation commands", roles["prometheus"]["developer_instructions"])
        self.assertIn("major compatibility/security implications", roles["prometheus"]["developer_instructions"])


if __name__ == "__main__":
    unittest.main()
