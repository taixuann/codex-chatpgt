from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).parents[1]))
from scripts.validate_session_packet import PacketError, validate


TEMPLATE_ROOT = Path(__file__).parents[1] / "templates"


class SessionPacketValidationTests(unittest.TestCase):
    def _packet(self) -> Path:
        repository = Path(tempfile.mkdtemp())
        root = repository / ".agents" / "sessions" / "20260826_example-work_001"
        root.mkdir(parents=True)
        session = yaml.safe_load((TEMPLATE_ROOT / "session.yaml").read_text(encoding="utf-8"))
        session.update(
            stage="plan",
            repository_root=str(repository),
            packet_root=f".agents/sessions/{root.name}",
            artifacts={"context": "context.md", "intent": "intent.md", "plan": "plan.md", "tasks": "task.md", "references": "references.yaml"},
        )
        (root / "session.yaml").write_text(yaml.safe_dump(session, sort_keys=False), encoding="utf-8")
        for name in ("context.md", "intent.md", "plan.md", "task.md", "references.yaml"):
            content = (TEMPLATE_ROOT / name).read_text(encoding="utf-8").replace("20260826_example-work_001", root.name)
            if name == "context.md":
                content = content.replace("  - intent.md\n", "  - intent.md\n  - plan.md\n")
            if name == "intent.md":
                content = content.replace("downstream: []", "downstream:\n  - plan.md")
            if name == "plan.md":
                content = content.replace("  - spec.md\n", "  - intent.md\n")
            (root / name).write_text(content, encoding="utf-8")
        return root

    def test_template_packet_passes(self) -> None:
        validate(self._packet())

    def test_intent_stage_packet_is_valid_without_plan_or_task(self) -> None:
        root = self._packet()
        (root / "plan.md").unlink()
        (root / "task.md").unlink()
        session = yaml.safe_load((root / "session.yaml").read_text(encoding="utf-8"))
        session["stage"] = "intent"
        session["artifacts"] = {"context": "context.md", "intent": "intent.md", "references": "references.yaml"}
        (root / "session.yaml").write_text(yaml.safe_dump(session, sort_keys=False), encoding="utf-8")
        context = (root / "context.md").read_text(encoding="utf-8").replace("  - plan.md\n", "")
        (root / "context.md").write_text(context, encoding="utf-8")
        intent = (root / "intent.md").read_text(encoding="utf-8").replace("downstream:\n  - plan.md", "downstream: []")
        (root / "intent.md").write_text(intent, encoding="utf-8")
        validate(root)

    def test_plan_stage_requires_intent_artifact(self) -> None:
        root = self._packet()
        (root / "intent.md").unlink()
        session = yaml.safe_load((root / "session.yaml").read_text(encoding="utf-8"))
        session["artifacts"].pop("intent")
        (root / "session.yaml").write_text(yaml.safe_dump(session, sort_keys=False), encoding="utf-8")
        with self.assertRaisesRegex(PacketError, "artifact-map|artifacts"):
            validate(root)

    def test_task_artifact_requires_plan(self) -> None:
        root = self._packet()
        (root / "plan.md").unlink()
        with self.assertRaisesRegex(PacketError, "plan.md"):
            validate(root)

    def test_directory_id_must_match_metadata(self) -> None:
        root = self._packet()
        (root / "session.yaml").write_text(
            (root / "session.yaml").read_text(encoding="utf-8").replace(root.name, "20260826_other-work_001"),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(PacketError, "directory name"):
            validate(root)

    def test_rag_requires_manifest(self) -> None:
        root = self._packet()
        (root / ".rag").mkdir()
        with self.assertRaisesRegex(PacketError, "manifest"):
            validate(root)

    def test_artifact_metadata_requires_provenance(self) -> None:
        root = self._packet()
        text = (root / "plan.md").read_text(encoding="utf-8").replace("provenance:\n", "provenance:\n", 1)
        # Remove the required recorder field while preserving valid YAML.
        text = text.replace("  recorded_by: franky\n", "", 1)
        (root / "plan.md").write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(PacketError, "provenance"):
            validate(root)

    def test_downstream_links_require_reciprocal_upstream(self) -> None:
        root = self._packet()
        text = (root / "task.md").read_text(encoding="utf-8").replace("  - plan.md\n", "", 1)
        (root / "task.md").write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(PacketError, "reciprocal"):
            validate(root)

    def test_franky_records_must_be_declared_in_artifact_map(self) -> None:
        root = self._packet()
        (root / "franky.ticket.yaml").write_text("kind: franky.task.v1\n", encoding="utf-8")
        (root / "franky.results.yaml").write_text("kind: franky.result.v1\n", encoding="utf-8")
        session = (root / "session.yaml").read_text(encoding="utf-8")
        session = session.replace("  ticket: franky.ticket.yaml\n", "").replace("  results: franky.results.yaml\n", "")
        (root / "session.yaml").write_text(session, encoding="utf-8")
        with self.assertRaisesRegex(PacketError, "artifact map"):
            validate(root)

    def test_references_require_bound_entries(self) -> None:
        root = self._packet()
        (root / "references.yaml").write_text(
            "kind: codex.session-references.v1\nsession_id: %s\nreferences: []\n" % root.name,
            encoding="utf-8",
        )
        with self.assertRaisesRegex(PacketError, "non-empty list"):
            validate(root)

    def test_packet_root_must_bind_to_validated_directory(self) -> None:
        root = self._packet()
        text = (root / "session.yaml").read_text(encoding="utf-8").replace(
            f"packet_root: .agents/sessions/{root.name}", "packet_root: elsewhere"
        )
        (root / "session.yaml").write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(PacketError, "packet_root"):
            validate(root)


if __name__ == "__main__":
    unittest.main()
