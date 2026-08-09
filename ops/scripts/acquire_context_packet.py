#!/usr/bin/env python3
"""Build a compact, read-only context packet from an explicit file allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Iterable


SENSITIVE_PARTS = {
    ".codex",
    ".git",
    "caches",
    "credentials",
    "logs",
    "sessions",
}


class ContextPacketError(ValueError):
    """Raised when an acquisition request exceeds the explicit safe scope."""


def _relative_path(raw: str) -> Path:
    if not isinstance(raw, str) or not raw or "\x00" in raw:
        raise ContextPacketError("include path must be a non-empty string without NUL")
    candidate = Path(raw)
    windows = PureWindowsPath(raw)
    if candidate.is_absolute() or windows.is_absolute() or windows.drive:
        raise ContextPacketError(f"absolute include path is not allowed: {raw}")
    if ".." in candidate.parts:
        raise ContextPacketError(f"parent traversal is not allowed: {raw}")
    if any(part == "" for part in candidate.parts):
        raise ContextPacketError(f"empty include path component is not allowed: {raw}")
    return candidate


def _check_sensitive(relative: Path) -> None:
    parts = {part.casefold() for part in relative.parts}
    if parts & SENSITIVE_PARTS or any(part.startswith(".env") for part in parts):
        raise ContextPacketError(f"sensitive/runtime path is not allowed: {relative}")


def _entry(root: Path, raw: str) -> dict[str, object]:
    relative = _relative_path(raw)
    _check_sensitive(relative)
    target = root.joinpath(relative)

    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ContextPacketError(f"symlink path is not allowed: {relative}")
    if not target.exists():
        raise ContextPacketError(f"include path does not exist: {relative}")
    if not target.is_file():
        raise ContextPacketError(f"include path is not a regular file: {relative}")

    try:
        payload = target.read_bytes()
        payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContextPacketError(f"include path is not UTF-8 text: {relative}") from exc

    return {
        "path": relative.as_posix(),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "lines": payload.count(b"\n") + (1 if payload and not payload.endswith(b"\n") else 0),
    }


def _entries(root: Path, paths: Iterable[str]) -> list[dict[str, object]]:
    unique = list(dict.fromkeys(paths))
    return sorted((_entry(root, raw) for raw in unique), key=lambda item: str(item["path"]))


def build_packet(
    root: Path,
    *,
    canonical: Iterable[str] = (),
    repository_evidence: Iterable[str] = (),
    conflicts: Iterable[str] = (),
    uncertainties: Iterable[str] = (),
) -> dict[str, object]:
    """Build a deterministic packet without writing to ``root``."""
    if root.is_symlink() or not root.exists() or not root.is_dir():
        raise ContextPacketError(f"root must be an existing regular directory: {root}")
    root = root.resolve()
    canonical_entries = _entries(root, canonical)
    evidence_entries = _entries(root, repository_evidence)
    overlap = {item["path"] for item in canonical_entries} & {
        item["path"] for item in evidence_entries
    }
    if overlap:
        raise ContextPacketError(f"path appears in both packet sections: {sorted(overlap)}")
    return {
        "canonical": canonical_entries,
        "repository_evidence": evidence_entries,
        "conflicts": sorted(dict.fromkeys(str(item) for item in conflicts)),
        "uncertainties": sorted(dict.fromkeys(str(item) for item in uncertainties)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--canonical", action="append", default=[])
    parser.add_argument("--evidence", dest="repository_evidence", action="append", default=[])
    parser.add_argument("--conflict", action="append", default=[])
    parser.add_argument("--uncertainty", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        packet = build_packet(
            args.root,
            canonical=args.canonical,
            repository_evidence=args.repository_evidence,
            conflicts=args.conflict,
            uncertainties=args.uncertainty,
        )
    except (ContextPacketError, OSError) as exc:
        print(f"FAIL context-packet: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
