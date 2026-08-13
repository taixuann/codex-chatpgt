#!/usr/bin/env python3
"""Validate the explicit skill admission catalog.

The catalog is the routing boundary: a package can exist on disk without being
canonical or implicitly discoverable. Structural quality remains necessary,
but canonical admission additionally requires capability/utility evidence.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
import re


DISPOSITIONS = {
    "KEEP",
    "ADAPT",
    "EXPLICIT_ONLY",
    "REFERENCE_ONLY",
    "MERGE",
    "RETIRE",
}


def tracked_skill_names(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "skills/*/SKILL.md"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return sorted(Path(path).parent.name for path in result.stdout.splitlines() if path)


def validate_catalog(root: Path, catalog: dict[str, Any], tracked: set[str]) -> list[str]:
    errors: list[str] = []
    if catalog.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    dispositions = catalog.get("dispositions")
    if not isinstance(dispositions, dict):
        return ["dispositions must be a mapping"]
    unknown = set(dispositions) - DISPOSITIONS
    if unknown:
        errors.append(f"unknown dispositions: {', '.join(sorted(unknown))}")

    owners: dict[str, str] = {}
    for disposition, names in dispositions.items():
        if not isinstance(names, list):
            errors.append(f"{disposition} must be a list")
            continue
        for name in names:
            if not isinstance(name, str) or not name:
                errors.append(f"{disposition} contains an invalid package name")
                continue
            if name in owners:
                errors.append(f"{name} must have exactly one disposition")
            owners[name] = disposition

    missing = tracked - set(owners)
    extra = set(owners) - tracked
    if missing:
        errors.append(f"tracked packages missing a disposition: {', '.join(sorted(missing))}")
    if extra:
        errors.append(f"catalog names are not tracked packages: {', '.join(sorted(extra))}")

    overlays = catalog.get("noncanonical_overlays", [])
    if not isinstance(overlays, list):
        errors.append("noncanonical_overlays must be a list")
        overlays = []
    overlay_names: set[str] = set()
    for overlay in overlays:
        if not isinstance(overlay, dict) or not overlay.get("name") or not overlay.get("path"):
            errors.append("each noncanonical overlay requires name and path")
            continue
        if overlay.get("disposition") not in DISPOSITIONS - {"KEEP"}:
            errors.append(f"overlay {overlay['name']} must be noncanonical")
        if overlay["name"] in overlay_names:
            errors.append(f"duplicate noncanonical overlay: {overlay['name']}")
        overlay_names.add(overlay["name"])
        if overlay["name"] in owners:
            errors.append(f"overlay cannot also be a tracked package: {overlay['name']}")
        if not (root / overlay["path"]).exists():
            errors.append(f"overlay path does not exist: {overlay['path']}")

    canonical = catalog.get("canonical_active")
    if not isinstance(canonical, list) or not canonical:
        errors.append("canonical_active must be a non-empty list")
        canonical = []
    if len(canonical) != len(set(canonical)):
        errors.append("canonical_active contains duplicates")
    for name in canonical:
        if name not in owners:
            errors.append(f"canonical_active package is not catalogued: {name}")
        elif owners[name] != "KEEP":
            errors.append(f"canonical_active package must have KEEP disposition: {name}")

    evidence = catalog.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("evidence must be a mapping")
        evidence = {}
    for name in canonical:
        item = evidence.get(name)
        if not isinstance(item, dict) or item.get("utility") != "PASS":
            errors.append(f"{name} lacks PASS capability/utility evidence")
        elif not str(item.get("basis", "")).strip():
            errors.append(f"{name} utility evidence requires a basis")
        for key in ("structural", "behavioral"):
            if item and key not in item:
                errors.append(f"{name} utility evidence must declare {key} status")

        skill_path = root / "skills" / name / "SKILL.md"
        try:
            text = skill_path.read_text(encoding="utf-8")
            body = text.split("---\n", 2)[-1]
            metadata = yaml.safe_load(text.split("---\n", 2)[1]) or {}
            description = str(metadata.get("description", ""))
            if not 8 <= len(description.split()) <= 60:
                errors.append(f"{name} description is too broad or too short")
            if not re.search(r"\b(do not|don't|never|only|not)\b", description, re.IGNORECASE):
                errors.append(f"{name} description lacks a negative routing boundary")
            required_sections = ("Trigger", "Inputs", "Output", "Boundary", "Stop", "Validation")
            for section in required_sections:
                if not re.search(rf"(?:^#+\s+.*{section}|\*\*{section}:?)", body, re.IGNORECASE | re.MULTILINE):
                    errors.append(f"{name} is missing a {section.lower()} contract field")
        except (OSError, IndexError, yaml.YAMLError) as exc:
            errors.append(f"{name} cannot be inspected for its contract: {exc}")

    capability_keys = catalog.get("capability_keys", {})
    if not isinstance(capability_keys, dict):
        errors.append("capability_keys must be a mapping")
    else:
        keys = [capability_keys.get(name) for name in canonical]
        if any(not isinstance(key, str) or not key.strip() for key in keys):
            errors.append("every canonical package requires a capability key")
        if len(keys) != len(set(keys)):
            errors.append("canonical packages have duplicate capability keys")

    for name, item in evidence.items():
        if name not in owners:
            errors.append(f"evidence names an uncatalogued package: {name}")
        if not isinstance(item, dict):
            errors.append(f"evidence for {name} must be a mapping")
            continue
        for path in item.get("evidence_paths", []):
            if not (root / path).exists():
                errors.append(f"{name} evidence path does not exist: {path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()
    try:
        catalog = yaml.safe_load(args.catalog.read_text(encoding="utf-8")) or {}
        tracked = set(tracked_skill_names(args.root.resolve()))
        errors = validate_catalog(args.root.resolve(), catalog, tracked)
    except (OSError, yaml.YAMLError) as exc:
        print(f"FAIL skill catalog: {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"FAIL skill catalog: {error}")
        return 1
    canonical = catalog["canonical_active"]
    print(f"OK skill catalog: {len(tracked)} tracked packages, {len(canonical)} canonical active")
    print("LIMITATION capability evidence is repository-grounded; model-mediated runtime selection remains NOT_ASSESSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
