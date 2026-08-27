#!/usr/bin/env python3
"""Validate the reversible documentation archive index."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import yaml


def validate(index_path: Path) -> None:
    index = yaml.safe_load(index_path.read_text(encoding="utf-8"))
    if not isinstance(index, dict) or index.get("kind") != "codex.documentation-archive.v1":
        raise ValueError("archive index kind is invalid")
    if not isinstance(index.get("archive_id"), (str, int)) or not index["archive_id"]:
        raise ValueError("archive_id is required")
    if not isinstance(index.get("entries"), list):
        raise ValueError("entries must be a list")
    resolved_index = index_path.resolve()
    if len(resolved_index.parents) < 4:
        raise ValueError("archive index must be nested under a repository documentation directory")
    root = resolved_index.parents[3]
    archive_root = index_path.parent.resolve()
    originals: set[str] = set()
    archived: set[str] = set()
    for entry in index["entries"]:
        if not isinstance(entry, dict):
            raise ValueError("each archive entry must be a mapping")
        for field in ("original_path", "archived_path", "status", "reason"):
            if not isinstance(entry.get(field), str) or not entry[field]:
                raise ValueError(f"archive entry {field} is required")
        original = Path(entry["original_path"])
        target = Path(entry["archived_path"])
        if original.is_absolute() or target.is_absolute() or ".." in original.parts or ".." in target.parts:
            raise ValueError("archive paths must be relative and traversal-free")
        if not entry["original_path"].startswith("documentation/plans/"):
            raise ValueError("original_path must point to documentation/plans")
        target_abs = (root / target).resolve()
        if archive_root not in target_abs.parents:
            raise ValueError("archived_path must remain under the archive directory")
        if (root / original).exists():
            raise ValueError(f"archived original still exists: {original}")
        if not target_abs.is_file():
            raise ValueError(f"archived target is missing: {target}")
        if entry["original_path"] in originals or entry["archived_path"] in archived:
            raise ValueError("archive paths must be unique")
        originals.add(entry["original_path"])
        archived.add(entry["archived_path"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("index", type=Path)
    args = parser.parse_args()
    try:
        validate(args.index)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL archive-index: {exc}")
        return 1
    print(f"OK archive-index: {args.index}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
