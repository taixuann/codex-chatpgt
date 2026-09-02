#!/usr/bin/env python3
"""Validate a plan family packet without executing its tasks."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re
import sys
from typing import Any

import yaml


SCENARIOS = {"socratic", "spec-driven-development", "planning-and-task-breakdown"}
SOURCE_KINDS = {"intent_packet", "github_issue"}
INTENT_PACKET_LOCATOR_RE = re.compile(
    r"^(?:conversation|intent-packet:[A-Za-z0-9._/-]+)$"
)

_SOURCE_PATH = Path(__file__).resolve().parents[2] / "intent/scripts/source_contract.py"
_SOURCE_SPEC = importlib.util.spec_from_file_location("intent_source_contract", _SOURCE_PATH)
if _SOURCE_SPEC is None or _SOURCE_SPEC.loader is None:  # pragma: no cover
    raise ImportError("cannot load canonical intent source contract")
_SOURCE = importlib.util.module_from_spec(_SOURCE_SPEC)
_SOURCE_SPEC.loader.exec_module(_SOURCE)


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _strings(value: Any, field: str, *, required: bool = True) -> list[str]:
    if value is None and not required:
        return []
    if not isinstance(value, list) or (required and not value):
        raise ValueError(f"{field} must be a non-empty list of strings")
    result = []
    for index, item in enumerate(value):
        result.append(_string(item, f"{field}[{index}]"))
    return result


def _check_acyclic(tasks: list[dict[str, Any]]) -> None:
    ids = {task["id"] for task in tasks}
    edges = {task["id"]: task.get("depends_on", []) for task in tasks}
    for task_id, deps in edges.items():
        if not isinstance(deps, list) or any(dep not in ids for dep in deps):
            raise ValueError(f"tasks[{task_id}].depends_on must reference known task IDs")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ValueError("task dependency graph contains a cycle")
        if node in visited:
            return
        visiting.add(node)
        for dep in edges[node]:
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for node in ids:
        visit(node)


def _validate_intent_origin(origin: Any, field: str = "source.intent_source") -> None:
    if not isinstance(origin, dict):
        raise ValueError(f"{field} must be a mapping")
    kind = _string(origin.get("kind"), f"{field}.kind")
    if kind not in {"user", "github_issue"}:
        raise ValueError(f"{field}.kind must be user or github_issue")
    locator = _string(origin.get("locator"), f"{field}.locator")
    if origin.get("packet_schema_version") != 1:
        raise ValueError(f"{field}.packet_schema_version must be 1")
    if kind == "user" and not _SOURCE.valid_locator("user", locator):
        raise ValueError(
            f"{field}.locator must be conversation, user-request:<ref>, or pasted-text:<ref>"
        )
    if kind == "github_issue" and not _SOURCE.valid_locator("github_issue", locator):
        raise ValueError(
            f"{field}.locator must be owner/repo#<number> or a canonical GitHub issue URL"
        )


def validate(data: Any, *, ready_for_build: bool = False) -> None:
    if not isinstance(data, dict):
        raise ValueError("packet must be a mapping")
    if data.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if data.get("kind") != "plan_packet":
        raise ValueError("kind must be plan_packet")

    source = data.get("source")
    if not isinstance(source, dict):
        raise ValueError("source must be a mapping")
    source_kind = _string(source.get("kind"), "source.kind")
    if source_kind not in SOURCE_KINDS:
        raise ValueError("source.kind must be intent_packet or github_issue")
    locator = _string(source.get("locator"), "source.locator")
    if source_kind == "github_issue":
        if not _SOURCE.valid_locator("github_issue", locator):
            raise ValueError(
                "github_issue source.locator must be owner/repo#<number> or a canonical GitHub issue URL"
            )
    else:
        if not INTENT_PACKET_LOCATOR_RE.fullmatch(locator):
            raise ValueError(
                "intent_packet source.locator must be conversation or intent-packet:<ref>"
            )
        if source.get("confirmed") is not True:
            raise ValueError("intent_packet source.confirmed must be true")
        _validate_intent_origin(source.get("intent_source"))

    scenario = _string(data.get("scenario"), "scenario")
    subskill = _string(data.get("subskill"), "subskill")
    if scenario not in SCENARIOS or subskill not in SCENARIOS:
        raise ValueError("scenario and subskill must be known plan leaves")
    if scenario != subskill:
        raise ValueError("scenario and subskill must match")

    _string(data.get("objective"), "objective")
    _strings(data.get("assumptions", []), "assumptions", required=False)
    _strings(data.get("dependencies", []), "dependencies", required=False)
    _strings(data.get("checkpoints"), "checkpoints")
    _strings(data.get("out_of_scope"), "out_of_scope")
    open_questions = _strings(data.get("open_questions", []), "open_questions", required=False)

    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must be a non-empty list")
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            raise ValueError(f"tasks[{index}] must be a mapping")
        task_id = _string(task.get("id"), f"tasks[{index}].id")
        if task_id in seen:
            raise ValueError(f"duplicate task id: {task_id}")
        seen.add(task_id)
        _string(task.get("title"), f"tasks[{index}].title")
        _strings(task.get("acceptance"), f"tasks[{index}].acceptance")
        _strings(task.get("verification"), f"tasks[{index}].verification")
        depends_on = task.get("depends_on", [])
        if not isinstance(depends_on, list) or any(not isinstance(dep, str) or not dep.strip() for dep in depends_on):
            raise ValueError(f"tasks[{index}].depends_on must be a list of task IDs")
        normalized.append(task)
    _check_acyclic(normalized)

    approved = data.get("approved")
    if not isinstance(approved, bool):
        raise ValueError("approved must be boolean")
    if data.get("side_effects", "none") != "none":
        raise ValueError("plan packets must declare side_effects: none")
    if ready_for_build and (not approved or open_questions):
        raise ValueError("ready-for-build requires approved: true and no open_questions")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--ready-for-build", action="store_true")
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.packet.read_text(encoding="utf-8"))
        validate(data, ready_for_build=args.ready_for_build)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL plan packet: {exc}")
        return 1
    print("OK plan packet: source, scenario, tasks, dependencies, and verification contract valid")
    if args.ready_for_build:
        print("READY plan packet: approved and eligible as a build input")
    else:
        print("STATUS plan packet: build approval gate not asserted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
