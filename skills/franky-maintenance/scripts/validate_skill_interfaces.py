#!/usr/bin/env python3
"""Validate Franky skill frontmatter and generated UI interface metadata."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to validate skill interfaces") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        packages = sorted(args.root.glob("franky-*/"))
        if not packages:
            raise ValueError("no Franky skill packages found")
        for package in packages:
            skill_text = (package / "SKILL.md").read_text(encoding="utf-8")
            if not skill_text.startswith("---\n"):
                raise ValueError(f"{package.name}: missing frontmatter")
            frontmatter = yaml.safe_load(skill_text.split("---\n", 2)[1])
            interface = yaml.safe_load((package / "agents/openai.yaml").read_text(encoding="utf-8"))
            if frontmatter.get("name") != package.name:
                raise ValueError(f"{package.name}: SKILL name mismatch")
            ui = interface.get("interface", {})
            if not ui.get("display_name") or not ui.get("short_description"):
                raise ValueError(f"{package.name}: incomplete interface metadata")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.root}: {exc}")
        return 1
    print(f"OK {args.root}: {len(packages)} Franky skill interfaces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
