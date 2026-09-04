import importlib.util
from pathlib import Path
import unittest
import tempfile
import hashlib


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_plan_packet.py"
SPEC = importlib.util.spec_from_file_location("validate_plan_packet", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)
PROJ_SPEC = importlib.util.spec_from_file_location("project_tasks", ROOT / "scripts/project_tasks.py")
PROJ = importlib.util.module_from_spec(PROJ_SPEC); assert PROJ_SPEC and PROJ_SPEC.loader; PROJ_SPEC.loader.exec_module(PROJ)


class PlanPacketTests(unittest.TestCase):
    def test_task_projection_is_idempotent(self):
        import yaml
        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        self.assertEqual(PROJ.project(data), PROJ.project(data))
        self.assertEqual(PROJ.project(data)["kind"], "plan_task_projection")
    def test_root_only_none_composition_is_valid(self):
        import yaml
        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["scenario"] = "none"; data["capabilities"] = []
        MODULE.validate(data)

    def test_deep_readiness_requires_independent_revision_bound_receipt(self):
        import yaml
        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data.update({"revision": "a" * 40, "artifact_ref": "plan", "depth": "DEEP", "approved": True, "critique": {"receipt": "plan-critique.yaml"}})
        with tempfile.TemporaryDirectory() as directory:
            packet = Path(directory) / ".agents/sessions/test" / "plan.yaml"; packet.parent.mkdir(parents=True)
            packet.write_text(yaml.safe_dump(data))
            with self.assertRaisesRegex(ValueError, "existing critique"):
                MODULE.validate(data, ready_for_build=True, deep=True, packet_path=packet)

    def test_deep_readiness_rejects_wrong_review_class(self):
        import yaml
        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data.update({"revision": "a" * 40, "artifact_ref": "plan", "depth": "DEEP", "approved": True, "critique": {"receipt": "plan-critique.yaml"}})
        receipt = {"kind": "athena.review-result.v1", "review_class": "architecture_contract", "target_ref": "plan", "target_revision": "a" * 40, "reviewer": {"independent": True, "provenance": "athena:test"}, "coverage": {"reviewed": ["plan"], "not_reviewed": [], "complete": True}, "criteria": [{"id": "C1", "status": "fulfilled", "evidence": ["local:test"], "rationale": "checked"}], "findings": [], "recommendation": {"status": "clear_for_parent_decision"}, "limitations": [], "human_review": {"required": False}}
        manifest = {"artifacts": {"plan": "plan.yaml", "plan_critique": "plan-critique.yaml"}}
        with tempfile.TemporaryDirectory() as directory:
            packet = Path(directory) / ".agents/sessions/test" / "plan.yaml"; packet.parent.mkdir(parents=True)
            packet.write_text(yaml.safe_dump(data))
            (packet.parent / "plan-critique.yaml").write_text(yaml.safe_dump(receipt))
            plan_md = packet.parent / "plan.md"; plan_md.write_text("plan")
            digest = hashlib.sha256(plan_md.read_bytes()).hexdigest()
            data["plan_digest"] = digest; manifest["artifacts"]["plan_digest"] = digest
            packet.write_text(yaml.safe_dump(data)); (packet.parent / "session.yaml").write_text(yaml.safe_dump(manifest))
            with self.assertRaisesRegex(ValueError, "review_class"):
                MODULE.validate(data, ready_for_build=True, deep=True, packet_path=packet)
    def test_valid_packet_can_be_ready_for_build(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        MODULE.validate(data)

    def test_github_issue_source_can_be_ready_for_build(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["source"] = {
            "kind": "github_issue",
            "locator": "taixuann/codex-chatpgt#123",
        }
        MODULE.validate(data)

    def test_cycle_is_rejected(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/invalid-cycle.yaml").read_text())
        with self.assertRaises(ValueError):
            MODULE.validate(data)

    def test_intent_source_requires_confirmation_and_provenance(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["source"]["confirmed"] = False
        with self.assertRaises(ValueError):
            MODULE.validate(data)

    def test_intent_source_must_bind_canonical_packet_contract(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["source"]["intent_source"].pop("packet_schema_version")
        with self.assertRaises(ValueError):
            MODULE.validate(data)

    def test_intent_packet_locator_must_be_bounded(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["source"]["locator"] = "does-not-exist.yaml"
        with self.assertRaises(ValueError):
            MODULE.validate(data)

    def test_github_issue_locator_must_be_canonical(self):
        import yaml

        data = yaml.safe_load((ROOT / "scripts/fixtures/valid.yaml").read_text())
        data["source"] = {"kind": "github_issue", "locator": "not-an-issue"}
        with self.assertRaises(ValueError):
            MODULE.validate(data)


if __name__ == "__main__":
    unittest.main()
