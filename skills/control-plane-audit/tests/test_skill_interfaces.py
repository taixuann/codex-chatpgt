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
        self.assertEqual(len(names), 65)
        self.assertIn("external-handoff", names)
        self.assertIn("shared-session-closeout", names)
        self.assertIn("socratic", names)
        self.assertIn("skill-retrospective", names)
        self.assertIn("api-and-interface-design", names)
        self.assertNotIn("workflow-manager", names)
        optional_root = root.parent / "ops" / "on-demand-skills"
        optional = module.discover_packages(optional_root)
        self.assertEqual({package.name for package in optional}, {
            "anthropic-skill-creator",
            "franky-cron-installer",
            "franky-promotion",
            "franky-source-migration",
            "install-project-link",
        })


if __name__ == "__main__":
    unittest.main()
