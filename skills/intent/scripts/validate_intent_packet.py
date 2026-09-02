#!/usr/bin/env python3
"""Validate an intent family packet without changing repository state."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Any

import yaml


SCENARIOS = {"interview-me", "idea-refine", "define-goal"}
SOURCE_KINDS = {"user", "github_issue"}
USER_LOCATOR_RE = re.compile(
    r"^(?:conversation|user[-_]request[:#/_-][A-Za-z0-9._/-]+|pasted-text:[^\s]+)$"
)
GITHUB_ISSUE_RE = re.compile(
    r"^(?:[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*|"
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/[1-9][0-9]*)$"
)


def _nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, field: str, *, required: bool = True) -> list[str]:
    if value is None and not required:
        return []
    if not isinstance(value, list) or (required and not value):
        raise ValueError(f"{field} must be a non-empty list of strings")
    result = []
    for index, item in enumerate(value):
        result.append(_nonempty_string(item, f"{field}[{index}]"))
    return result


def validate(data: Any, *, ready_for_plan: bool = False) -> None:
    if not isinstance(data, dict):
        raise ValueError("packet must be a mapping")
    if data.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if data.get("kind") != "intent_packet":
        raise ValueError("kind must be intent_packet")

    source = data.get("source")
    if not isinstance(source, dict):
        raise ValueError("source must be a mapping")
    source_kind = _nonempty_string(source.get("kind"), "source.kind")
    if source_kind not in SOURCE_KINDS:
        raise ValueError("source.kind must be user or github_issue")
    locator = _nonempty_string(source.get("locator"), "source.locator")
    if source_kind == "user" and not USER_LOCATOR_RE.fullmatch(locator):
        raise ValueError(
            "user source.locator must be conversation, user-request:<ref>, or pasted-text:<ref>"
        )
    if source_kind == "github_issue" and not GITHUB_ISSUE_RE.fullmatch(locator):
        raise ValueError(
            "github_issue source.locator must be owner/repo#<number> or a canonical GitHub issue URL"
        )

    scenario = _nonempty_string(data.get("scenario"), "scenario")
    subskill = _nonempty_string(data.get("subskill"), "subskill")
    if scenario not in SCENARIOS or subskill not in SCENARIOS:
        raise ValueError("scenario and subskill must be known intent leaves")
    if scenario != subskill:
        raise ValueError("scenario and subskill must match")

    _nonempty_string(data.get("objective"), "objective")
    _string_list(data.get("success_criteria"), "success_criteria")
    _string_list(data.get("scope"), "scope")
    _string_list(data.get("out_of_scope"), "out_of_scope")
    _string_list(data.get("assumptions", []), "assumptions", required=False)
    open_questions = _string_list(data.get("open_questions", []), "open_questions", required=False)

    confirmed = data.get("confirmed")
    if not isinstance(confirmed, bool):
        raise ValueError("confirmed must be boolean")
    confidence = data.get("confidence")
    if confidence is not None and (not isinstance(confidence, int) or isinstance(confidence, bool) or not 0 <= confidence <= 100):
        raise ValueError("confidence must be an integer from 0 to 100")
    side_effects = data.get("side_effects", "none")
    if side_effects != "none":
        raise ValueError("intent packets must declare side_effects: none")

    if ready_for_plan and (not confirmed or open_questions):
        raise ValueError("ready-for-plan requires confirmed: true and no open_questions")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--ready-for-plan", action="store_true")
    args = parser.parse_args()
    try:
        data = yaml.safe_load(args.packet.read_text(encoding="utf-8"))
        validate(data, ready_for_plan=args.ready_for_plan)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL intent packet: {exc}")
        return 1
    print("OK intent packet: source, scenario, objective, scope, and confirmation contract valid")
    if args.ready_for_plan:
        print("READY intent packet: eligible as a plan input")
    else:
        print("STATUS intent packet: confirmation gate not asserted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
