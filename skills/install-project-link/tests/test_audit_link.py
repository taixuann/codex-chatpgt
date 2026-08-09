import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/audit_link.py"
CREATE_SCRIPT = Path(__file__).resolve().parents[1] / "scripts/create_project_link.py"


def load_module():
    spec = importlib.util.spec_from_file_location("audit_link", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_create_module():
    spec = importlib.util.spec_from_file_location("create_project_link", CREATE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class AuditLinkTests(unittest.TestCase):
    def test_proposed_link_is_read_only(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            target = root / "workspace" / "link"
            target.parent.mkdir()
            self.assertEqual(
                module.audit(source, target, root, True), 0
            )

    def test_system_skill_is_rejected(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / ".system"
            source.mkdir()
            target = root / "link"
            self.assertNotEqual(module.audit(source, target, root, True), 0)

    def test_apply_creates_only_an_approved_link(self):
        module = load_create_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source.mkdir()
            target = root / "workspace" / "link"
            target.parent.mkdir()
            source, target = module.validate(source, target, root)
            target.symlink_to(source)
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), source)


if __name__ == "__main__":
    unittest.main()
