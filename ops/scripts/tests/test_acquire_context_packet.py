import os
import tempfile
import unittest
from pathlib import Path

from ops.scripts.acquire_context_packet import ContextPacketError, build_packet


class ContextPacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "AGENTS.md").write_text("scope: control-plane\n", encoding="utf-8")
        (self.root / "documentation").mkdir()
        (self.root / "documentation" / "CURRENT.md").write_text("status: active\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_packet_is_compact_sorted_and_deterministic(self):
        kwargs = {
            "canonical": ["documentation/CURRENT.md", "AGENTS.md"],
            "repository_evidence": [],
            "conflicts": ["state mismatch", "state mismatch"],
            "uncertainties": ["runtime trace unavailable"],
        }
        first = build_packet(self.root, **kwargs)
        second = build_packet(self.root, **kwargs)
        self.assertEqual(first, second)
        self.assertEqual([item["path"] for item in first["canonical"]], ["AGENTS.md", "documentation/CURRENT.md"])
        self.assertEqual(first["conflicts"], ["state mismatch"])
        self.assertEqual(set(first), {"canonical", "repository_evidence", "conflicts", "uncertainties"})

    def test_rejects_traversal_absolute_windows_and_sensitive_paths(self):
        candidates = [
            "../outside.txt",
            str(self.root / "AGENTS.md"),
            r"C:\\secret.txt",
            ".git/config",
            ".env",
        ]
        for candidate in candidates:
            with self.subTest(candidate=candidate), self.assertRaises(ContextPacketError):
                build_packet(self.root, canonical=[candidate])

    def test_rejects_symlink_and_does_not_write(self):
        target = self.root / "outside.txt"
        target.write_text("outside\n", encoding="utf-8")
        link = self.root / "linked.md"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        before = sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*"))
        with self.assertRaises(ContextPacketError):
            build_packet(self.root, canonical=["linked.md"])
        after = sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*"))
        self.assertEqual(before, after)
        self.assertEqual(os.readlink(link), str(target))

    def test_rejects_missing_directory_binary_and_overlap(self):
        (self.root / "folder").mkdir()
        (self.root / "binary.bin").write_bytes(b"\xff\x00")
        cases = [
            (dict(canonical=["missing.md"]), "does not exist"),
            (dict(canonical=["folder"]), "regular file"),
            (dict(canonical=["binary.bin"]), "UTF-8"),
            (dict(canonical=["AGENTS.md"], repository_evidence=["AGENTS.md"]), "both packet"),
        ]
        for kwargs, expected in cases:
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ContextPacketError, expected):
                build_packet(self.root, **kwargs)


if __name__ == "__main__":
    unittest.main()
