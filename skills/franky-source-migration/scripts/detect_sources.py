#!/usr/bin/env python3
"""Detect supported source-tool signatures without modifying the filesystem."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SIGNATURES = {
    "claude-code": ("CLAUDE.md", ".claude"),
    # AGENTS.md is shared by multiple tools and is not an OpenCode signature.
    "opencode": (".opencode", "opencode.json", "opencode.jsonc"),
    "antigravity": (".agent", ".gemini"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="+", type=Path)
    args = parser.parse_args()
    detections = []
    for root in args.roots:
        root = root.resolve()
        present = [name for name, markers in SIGNATURES.items() if any((root / marker).exists() for marker in markers)]
        detections.append({"root": str(root), "sources": present})
    print(json.dumps({"detections": detections}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
