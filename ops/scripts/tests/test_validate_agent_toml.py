import tempfile
import unittest
import importlib.util
from pathlib import Path

import tomllib

VALIDATOR_PATH = (
    Path(__file__).resolve().parents[3]
    / "skills/runtime-adapter-management/scripts/validate_agent_toml.py"
)
SPEC = importlib.util.spec_from_file_location("validate_agent_toml", VALIDATOR_PATH)
assert SPEC and SPEC.loader
validate_agent_toml = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_agent_toml)


VALID = """
name = "example"
description = "Bounded test adapter."
model = "gpt-5.6-luna"
model_reasoning_effort = "low"
sandbox_mode = "read-only"
developer_instructions = "Return bounded evidence."
"""


class AgentTomlValidationTests(unittest.TestCase):
    def test_checked_in_adapters_have_only_runtime_fields(self):
        root = Path(__file__).resolve().parents[3] / "agents"
        for path in sorted(root.glob("*.toml")):
            with self.subTest(path=path):
                data = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(set(data), validate_agent_toml.ALLOWED)

    def test_unknown_runtime_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "example.toml"
            path.write_text(VALID + "preferred_skills = ['unused']\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                data = tomllib.loads(path.read_text(encoding="utf-8"))
                unknown = set(data) - validate_agent_toml.ALLOWED
                if unknown:
                    raise ValueError(f"unknown fields: {', '.join(sorted(unknown))}")


if __name__ == "__main__":
    unittest.main()
