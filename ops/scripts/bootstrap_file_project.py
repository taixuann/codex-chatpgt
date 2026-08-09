#!/usr/bin/env python3
"""Safely materialize a small, adaptive file-first project from an artifact map."""
from __future__ import annotations

import argparse
import os
from pathlib import Path, PurePosixPath
import tempfile
from typing import Any

import yaml


FORBIDDEN_TOP_LEVEL = {".codex", ".git", "agents", "credentials", "memories", "sessions", "skills", "workflows"}
RAW_PREFIX = PurePosixPath("data/raw")
ALLOWED_INTENTS = {"create", "update", "preserve"}


class BootstrapError(ValueError):
    """Raised when an artifact map is unsafe or internally inconsistent."""


def _relative_path(value: Any) -> PurePosixPath:
    if not isinstance(value, str) or not value.strip():
        raise BootstrapError("artifact path must be a non-empty string")
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if not path.parts or path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise BootstrapError(f"artifact path must be relative and normalized: {value}")
    if path.parts[0] in FORBIDDEN_TOP_LEVEL:
        raise BootstrapError(f"artifact path is outside the project bootstrap boundary: {value}")
    return path


def validate_map(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict) or not isinstance(data.get("project"), dict):
        raise BootstrapError("artifact map requires a project mapping")
    project = data["project"]
    if not project.get("name") or not project.get("purpose"):
        raise BootstrapError("project.name and project.purpose are required")
    if project.get("mode") not in {"new", "existing"}:
        raise BootstrapError("project.mode must be new or existing")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise BootstrapError("artifact map requires a non-empty artifacts list")

    normalized: list[dict[str, Any]] = []
    declared_paths: set[str] = set()
    for item in artifacts:
        if not isinstance(item, dict):
            raise BootstrapError("each artifact must be a mapping")
        declared_paths.add(_relative_path(item.get("path")).as_posix())
    paths: set[str] = set()
    for raw in artifacts:
        rel = _relative_path(raw.get("path"))
        key = rel.as_posix()
        if key in paths:
            raise BootstrapError(f"duplicate artifact path: {key}")
        paths.add(key)
        intent = raw.get("intent", "create")
        if intent not in ALLOWED_INTENTS:
            raise BootstrapError(f"unsupported intent for {key}: {intent}")
        if rel == RAW_PREFIX or RAW_PREFIX in rel.parents:
            if intent != "preserve":
                raise BootstrapError("data/raw is immutable; only preserve intent is allowed")
        if intent in {"create", "update"} and not isinstance(raw.get("content"), str):
            raise BootstrapError(f"{key} requires string content for {intent} intent")
        links = raw.get("links", [])
        if not isinstance(links, list) or not all(isinstance(item, str) for item in links):
            raise BootstrapError(f"links must be a list of strings for {key}")
        for link in links:
            if not link.startswith("external://"):
                raise BootstrapError(f"non-external link must be resolved before bootstrap: {link}")
        depends_on = raw.get("depends_on", [])
        if not isinstance(depends_on, list) or not all(isinstance(item, str) for item in depends_on):
            raise BootstrapError(f"depends_on must be a list of strings for {key}")
        for dependency in depends_on:
            dependency_key = _relative_path(dependency).as_posix()
            if dependency_key not in declared_paths:
                raise BootstrapError(f"unknown dependency for {key}: {dependency}")
        normalized.append({**raw, "path": key, "intent": intent})
    return {**data, "artifacts": normalized}


def load_map(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise BootstrapError(f"cannot read artifact map {path}: {exc}") from exc
    return validate_map(data)


def _safe_target(root: Path, rel: str) -> Path:
    root = root.resolve()
    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise BootstrapError(f"artifact escapes output root: {rel}") from exc
    return target


def materialize(data: dict[str, Any], output_root: Path, apply: bool) -> list[str]:
    root = output_root.resolve()
    if apply:
        root.mkdir(parents=True, exist_ok=True)
    actions: list[str] = []
    targets: list[tuple[dict[str, Any], Path]] = []
    for artifact in data["artifacts"]:
        target = _safe_target(root, artifact["path"])
        if target.exists() and target.is_symlink():
            raise BootstrapError(f"refusing symlink target: {artifact['path']}")
        if target.exists() and target.is_dir():
            raise BootstrapError(f"artifact target must be a file: {artifact['path']}")
        intent = artifact["intent"]
        if intent == "create" and target.exists():
            raise BootstrapError(f"create target already exists: {artifact['path']}")
        if intent == "update" and not target.exists():
            raise BootstrapError(f"update target does not exist: {artifact['path']}")
        if intent == "preserve":
            if not target.exists():
                raise BootstrapError(f"preserve target does not exist: {artifact['path']}")
            actions.append(f"preserve {artifact['path']}")
            continue
        targets.append((artifact, target))
        actions.append(f"{intent} {artifact['path']}")

    if apply:
        for artifact, target in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(artifact["content"])
                os.replace(temporary, target)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_map", type=Path)
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--apply", action="store_true", help="materialize after validation; default is dry-run")
    args = parser.parse_args()
    try:
        data = load_map(args.artifact_map)
        actions = materialize(data, args.output_root, args.apply)
    except (BootstrapError, OSError) as exc:
        print(f"FAIL bootstrap: {exc}")
        return 1
    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"OK {mode}: {len(actions)} artifact(s)")
    for action in actions:
        print(f"  {action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
