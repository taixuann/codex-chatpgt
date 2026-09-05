#!/usr/bin/env python3
"""Validate a small static contrastive skill-routing fixture.

This checks discoverability metadata and neighbor coverage only. It does not
claim to observe or prove model/runtime skill selection.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

import yaml


REQUIRED_KINDS = {"positive", "negative", "neighbor", "none", "ambiguous"}


def tracked_skills(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "skills/**/SKILL.md"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return set()
    return {
        Path(path).parent.name
        for path in result.stdout.splitlines()
        if path and ".system" not in Path(path).parts
    }


def skill_dir(root: Path, name: str) -> Path:
    matches = [
        p.parent for p in (root / "skills").rglob("SKILL.md")
        if p.parent.name == name and ".system" not in p.parts
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one package named {name}, found {len(matches)}")
    return matches[0]


def descriptions(root: Path, names: set[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in names:
        package = skill_dir(root, name)
        text = (package / "SKILL.md").read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\ndescription:" not in text.split("---\n", 2)[1]:
            raise ValueError(f"{name}: missing frontmatter description")
        frontmatter = yaml.safe_load(text.split("---\n", 2)[1]) or {}
        description = frontmatter.get("description")
        if not isinstance(description, str) or len(description.split()) < 8:
            raise ValueError(f"{name}: description is too vague for routing")
        interface_path = package / "agents" / "openai.yaml"
        if interface_path.exists():
            interface = yaml.safe_load(interface_path.read_text(encoding="utf-8")) or {}
            ui = interface.get("interface", {})
            if ui and (not isinstance(ui, dict) or len(str(ui.get("short_description", "")).split()) < 3):
                raise ValueError(f"{name}: interface short_description is too vague for routing")
        result[name] = description
    return result


def validate(root: Path, fixture: Path) -> tuple[int, int]:
    skills = tracked_skills(root)
    data = yaml.safe_load(fixture.read_text(encoding="utf-8")) or {}
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("fixture requires a non-empty cases list")
    seen: set[str] = set()
    kinds: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("each case must be a mapping")
        case_id = case.get("id")
        kind = case.get("kind")
        expected = case.get("expected")
        neighbors = case.get("neighbors", [])
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError(f"invalid or duplicate case id: {case_id!r}")
        if kind not in REQUIRED_KINDS:
            raise ValueError(f"{case_id}: invalid kind {kind!r}")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise ValueError(f"{case_id}: prompt is required")
        if expected != "none" and expected not in skills:
            raise ValueError(f"{case_id}: expected skill is not tracked: {expected}")
        if not isinstance(neighbors, list) or any(item not in skills for item in neighbors):
            raise ValueError(f"{case_id}: neighbors must be tracked skill names")
        if expected != "none" and expected in neighbors:
            raise ValueError(f"{case_id}: expected skill must not be its own neighbor")
        seen.add(case_id)
        kinds.add(kind)
    missing = REQUIRED_KINDS - kinds
    if missing:
        raise ValueError(f"fixture is missing case kinds: {', '.join(sorted(missing))}")
    descriptions(root, skills)
    return len(skills), len(cases)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    try:
        skill_count, case_count = validate(args.root.resolve(), args.fixture.resolve())
    except (OSError, ValueError, subprocess.CalledProcessError, yaml.YAMLError) as exc:
        print(f"FAIL static skill-routing eval: {exc}")
        return 1
    print(f"OK static skill-routing eval: {skill_count} tracked skills, {case_count} contrastive cases")
    print("LIMITATION behavioral runtime selection is not observed by this fixture")
    return 0


if __name__ == "__main__":
    sys.exit(main())
