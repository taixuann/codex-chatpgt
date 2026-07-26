#!/usr/bin/env python3
"""Create a deterministic promotion manifest for Codex-first artifacts."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    if path.is_file():
        hasher.update(path.read_bytes())
        return hasher.hexdigest()
    if not path.is_dir():
        raise ValueError(f"artifact does not exist: {path}")
    for child in sorted(p for p in path.rglob("*") if p.is_file()):
        hasher.update(str(child.relative_to(path)).encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(child.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--goal-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--artifact", action="append", default=[], metavar="SOURCE=DESTINATION")
    args = parser.parse_args()
    rows: list[tuple[Path, str, str]] = []
    try:
        for raw in args.artifact:
            source_text, destination = raw.split("=", 1)
            source = Path(source_text).resolve()
            if not str(source).startswith("/Users/tai/.codex/"):
                raise ValueError(f"source must be under /Users/tai/.codex: {source}")
            rows.append((source, destination, digest(source)))
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1
    lines = [
        f"goal_id: {args.goal_id}",
        "status: proposed",
        "source_root: /Users/tai/.codex",
        "artifacts:",
    ]
    for source, destination, sha256 in rows:
        lines.extend([
            f"  - source: {source}",
            f"    destination: {destination}",
            f"    sha256: {sha256}",
            "    version: 1",
        ])
    lines.extend(["dependencies: []", "validation: []", "rollback: []", ""])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE {args.output} ({len(rows)} artifacts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
