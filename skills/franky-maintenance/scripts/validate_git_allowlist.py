#!/usr/bin/env python3
"""Validate the Codex Git allowlist and reject sensitive tracked paths."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


ALLOWED_PREFIXES = ("agents/", "skills/franky-", "skills/shared-session-closeout/", "workflows/franky/", "workflows/shared/", ".github/", "manifests/", "ops/schemas/", "ops/scripts/", "ops/schedulers/", "ops/changes/")
ALLOWED_FILES = {".gitignore", "AGENTS.md"}
FORBIDDEN_MARKERS = (".system/", "sessions/", "memories/", "cache/", "logs", ".sqlite", "config.toml", "credentials")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        result = subprocess.run(["git", "-C", str(args.root), "ls-files"], check=True, capture_output=True, text=True)
        paths = [line for line in result.stdout.splitlines() if line]
        for path in paths:
            if path not in ALLOWED_FILES and not path.startswith(ALLOWED_PREFIXES):
                raise ValueError(f"tracked path outside allowlist: {path}")
            if any(marker in path for marker in FORBIDDEN_MARKERS):
                raise ValueError(f"sensitive path is tracked: {path}")
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"FAIL {args.root}: {exc}")
        return 1
    print(f"OK {args.root}: {len(paths)} tracked paths within allowlist")
    return 0


if __name__ == "__main__":
    sys.exit(main())
