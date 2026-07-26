#!/usr/bin/env python3
"""Validate promotion manifest paths, hashes, dependencies, and rollback."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to validate promotion manifests") from exc


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    if path.is_file():
        hasher.update(path.read_bytes())
    elif path.is_dir():
        for child in sorted(p for p in path.rglob("*") if p.is_file()):
            hasher.update(str(child.relative_to(path)).encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(child.read_bytes())
            hasher.update(b"\0")
    else:
        raise ValueError(f"artifact does not exist: {path}")
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("source_root") != "/Users/tai/.codex":
            raise ValueError("manifest must use /Users/tai/.codex as source_root")
        if data.get("status") not in {"proposed", "approved", "promoted", "rejected"}:
            raise ValueError("manifest has unsupported status")
        artifacts = data.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise ValueError("manifest requires artifacts")
        for item in artifacts:
            for key in ("source", "destination", "sha256", "version"):
                if key not in item:
                    raise ValueError(f"artifact missing {key}")
            source = Path(item["source"]).resolve()
            if not str(source).startswith("/Users/tai/.codex/"):
                raise ValueError(f"artifact source outside Codex root: {source}")
            if digest(source) != item["sha256"]:
                raise ValueError(f"hash mismatch: {source}")
        for dependency in data.get("dependencies", []):
            if not Path(dependency).exists():
                raise ValueError(f"missing dependency: {dependency}")
        if not data.get("rollback"):
            raise ValueError("manifest requires rollback entries")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.manifest}: {exc}")
        return 1
    print(f"OK {args.manifest}: {len(data['artifacts'])} artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
