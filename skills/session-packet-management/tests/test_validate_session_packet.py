from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1]))
from scripts.validate_session_packet import PacketError, validate


TEMPLATE_ROOT = Path(__file__).parents[1] / "templates"


class SessionPacketValidationTests(unittest.TestCase):
    def _packet(self) -> Path:
        root = Path(tempfile.mkdtemp()) / "20260826_example-work_001"
        root.mkdir()
        for name in ("session.yaml", "context.md", "spec.md", "plan.md", "task.md", "references.yaml"):
            content = (TEMPLATE_ROOT / name).read_text(encoding="utf-8").replace("20260826_example-work_001", root.name)
            (root / name).write_text(content, encoding="utf-8")
        return root

    def test_template_packet_passes(self) -> None:
        validate(self._packet())

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


if __name__ == "__main__":
    unittest.main()
