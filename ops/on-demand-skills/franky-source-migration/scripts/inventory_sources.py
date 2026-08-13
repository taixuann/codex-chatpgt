#!/usr/bin/env python3
"""Inventory recognized source artifacts without reading or changing content."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PATTERNS = {
    "claude-code": ("CLAUDE.md", ".claude/commands", ".claude/skills", ".claude/agents", ".mcp.json", ".claude/settings.json", ".claude.json"),
    "opencode": ("AGENTS.md", ".opencode/skills", ".opencode/commands", "opencode.json", "opencode.jsonc"),
    "antigravity": (".agent/skills", ".gemini/skills", ".gemini/antigravity", "gemini.md", "GEMINI.md"),
}


def digest(path: Path) -> str:
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    return "directory"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--source", required=True, choices=sorted(PATTERNS))
    args = parser.parse_args()
    root = args.root.resolve()
    artifacts = []
    for relative in PATTERNS[args.source]:
        path = root / relative
        if not path.exists():
            continue
        artifact_type = "instruction" if path.name.lower() in {"claude.md", "agents.md", "gemini.md"} else "source-surface"
        artifacts.append({"source": args.source, "path": str(path), "type": artifact_type, "active": True, "sha256": digest(path)})
    print(json.dumps({"root": str(root), "artifacts": artifacts}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
