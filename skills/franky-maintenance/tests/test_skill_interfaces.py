import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_skill_interfaces.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_skill_interfaces", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SkillInterfaceDiscoveryTests(unittest.TestCase):
    def test_discovery_covers_all_tracked_packages_not_personal_overlays(self):
        module = load_module()
        root = Path(__file__).parents[3] / "skills"
        packages = module.discover_packages(root)
        names = {package.name for package in packages}
        self.assertEqual(len(names), 10)
        self.assertIn("external-handoff", names)
        self.assertIn("shared-session-closeout", names)
        self.assertNotIn("workflow-manager", names)


if __name__ == "__main__":
    unittest.main()
