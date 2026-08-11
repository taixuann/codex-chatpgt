#!/usr/bin/env python3
"""Validate tracked control-plane skill frontmatter and UI metadata."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required to validate skill interfaces") from exc


def discover_packages(root: Path) -> list[Path]:
    """Return Git-tracked skill packages, excluding ignored overlays."""
    root = root.resolve()
    repo_root = root.parent
    tracked = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "--", f"{root.name}/*/SKILL.md"],
        check=False,
        capture_output=True,
        text=True,
    )
    if tracked.returncode == 0 and tracked.stdout.strip():
        return sorted(
            (repo_root / path.rsplit("/", 1)[0]).resolve()
            for path in tracked.stdout.splitlines()
            if path.startswith(f"{root.name}/")
        )
    return sorted(
        package for package in root.glob("franky-*/") if (package / "SKILL.md").is_file()
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        packages = discover_packages(args.root)
        if not packages:
            raise ValueError("no tracked skill packages found")
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
    print(f"OK {args.root}: {len(packages)} tracked skill interfaces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
