#!/usr/bin/env python3
"""Deterministically render a task contract for an admitted executor profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from issue_execution import digest, dump_document, load_document

RENDERER_VERSION = 1
PROFILES = {"agy", "prometheus", "identity"}
REQUIRED = {
    "task_id", "objective", "allowed_scope",
    "constraints", "acceptance", "validation", "return_contract", "stop_conditions",
}
OPTIONAL = {"authority", "context", "starting_state", "target_state", "forbidden_scope", "action_boundaries", "prior_failed_approach", "examples"}
BLOCKED_KEYS = {
    "memory", "history", "conversation", "transcript", "prior_messages", "chat_history",
    "prompt_history", "clarification_questions", "tool_selection", "executor_selection",
    "model_catalog", "hidden_reasoning", "chain_of_thought",
}


def _nonempty(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def _check_blocked_keys(value: Any) -> None:
    if isinstance(value, dict):
        blocked = {str(key).lower() for key in value} & BLOCKED_KEYS
        if blocked:
            raise ValueError(f"forbidden renderer input field: {sorted(blocked)[0]}")
        for item in value.values():
            _check_blocked_keys(item)
    elif isinstance(value, list):
        for item in value:
            _check_blocked_keys(item)


def _items(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list) or not value or any(not _nonempty(item) for item in value):
        raise ValueError(f"{field} must be a non-empty list")
    return value


def _acceptance(value: Any) -> list[dict[str, Any]]:
    items = _items(value, "acceptance")
    seen: set[str] = set()
    result = []
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip() or not _nonempty(item.get("requirement")):
            raise ValueError("acceptance entries require id and requirement")
        if item["id"] in seen:
            raise ValueError(f"duplicate acceptance id: {item['id']}")
        seen.add(item["id"])
        result.append(item)
    return result


def _return_fields(value: Any) -> list[str]:
    fields = value.get("fields") if isinstance(value, dict) else value
    if not isinstance(fields, list) or not fields or any(not isinstance(item, str) or not item.strip() for item in fields):
        raise ValueError("return_contract must provide a non-empty fields list")
    if len(set(fields)) != len(fields):
        raise ValueError("return_contract fields must be unique")
    return fields


def _validate_contract(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        raise ValueError("task_contract must be an object")
    _check_blocked_keys(contract)
    unknown = set(contract) - REQUIRED - OPTIONAL
    missing = REQUIRED - set(contract)
    if missing:
        raise ValueError(f"missing task contract fields: {sorted(missing)}")
    if unknown:
        raise ValueError(f"unknown task contract fields: {sorted(unknown)}")
    for field in ("task_id", "objective"):
        if not isinstance(contract[field], str) or not contract[field].strip():
            raise ValueError(f"{field} must be a non-empty string")
    for field in ("constraints", "validation", "stop_conditions"):
        if not _nonempty(contract[field]):
            raise ValueError(f"{field} must not be empty")
    _items(contract["allowed_scope"], "allowed_scope")
    if "forbidden_scope" in contract:
        _items(contract["forbidden_scope"], "forbidden_scope")
    _acceptance(contract["acceptance"])
    _return_fields(contract["return_contract"])
    return contract


def _value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _section(label: str, value: Any, *, bullets: bool = False) -> list[str]:
    lines = [f"## {label}"]
    if bullets and isinstance(value, list):
        lines.extend(f"- {_value(item)}" for item in value)
    else:
        lines.append(_value(value))
    return lines


def _boundary(profile: str) -> str:
    return {
        "agy": "Execute only within the supplied contract. Do not select another executor, widen authority, or perform destructive or external actions unless explicitly granted.",
        "prometheus": "Act within the supplied parent contract. Do not select another executor, widen authority, or perform destructive or external actions outside explicit authorization.",
        "identity": "Use the supplied contract exactly; this identity profile adds no executor-specific instruction.",
    }[profile]


def _prompt(contract: dict[str, Any], profile: str) -> str:
    sections: list[str] = []
    sections += _section("Objective", contract["objective"])
    for field, label in (("authority", "Authority"), ("context", "Context"), ("starting_state", "Starting state"), ("target_state", "Target state")):
        if field in contract:
            sections += _section(label, contract[field])
    sections += _section("Allowed scope", contract["allowed_scope"], bullets=True)
    if "forbidden_scope" in contract:
        sections += _section("Forbidden scope", contract["forbidden_scope"], bullets=True)
    sections += _section("Constraints", contract["constraints"], bullets=isinstance(contract["constraints"], list))
    sections.append("## Relevant acceptance criteria")
    sections.extend(f"- {item['id']}: {_value(item['requirement'])}" for item in contract["acceptance"])
    sections += _section("Required validation", contract["validation"], bullets=isinstance(contract["validation"], list))
    for field, label in (("action_boundaries", "Action boundaries"), ("prior_failed_approach", "Prior failed approach"), ("examples", "Examples")):
        if field in contract:
            sections += _section(label, contract[field], bullets=isinstance(contract[field], list))
    sections += _section("Execution boundary", _boundary(profile))
    sections += _section("Return contract", contract["return_contract"])
    sections += _section("Stop conditions", contract["stop_conditions"], bullets=isinstance(contract["stop_conditions"], list))
    return "\n\n".join(sections) + "\n"


def render(task_contract: dict[str, Any], executor_profile: str) -> dict[str, Any]:
    if executor_profile not in PROFILES:
        raise ValueError(f"unknown executor profile: {executor_profile}")
    contract = _validate_contract(task_contract)
    prompt = _prompt(contract, executor_profile)
    acceptance = _acceptance(contract["acceptance"])
    manifest = {
        "renderer": {
            "profile": executor_profile,
            "version": RENDERER_VERSION,
            "source_contract_sha256": digest(contract),
            "rendered_prompt_sha256": digest(prompt),
        },
        "prompt": prompt,
        "semantic_manifest": {
            "objective": contract["objective"],
            "allowed_scope": contract["allowed_scope"],
            "constraints": contract["constraints"],
            "acceptance": {"expected": acceptance, "represented": acceptance},
            "validation": contract["validation"],
            "return_contract": contract["return_contract"],
            "stop_conditions": contract["stop_conditions"],
        },
    }
    for field in ("authority", "context", "starting_state", "target_state", "forbidden_scope", "action_boundaries"):
        if field in contract:
            manifest["semantic_manifest"][field] = contract[field]
    passthrough = {field: contract[field] for field in ("prior_failed_approach", "examples") if field in contract}
    if passthrough:
        manifest["semantic_manifest"]["pass_through_context"] = passthrough
    manifest["semantic_manifest"]["acceptance"]["verification"] = "deterministic construction record; not independent semantic verification"
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("render", choices=["render"])
    parser.add_argument("--contract", required=True)
    parser.add_argument("--executor-profile", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = render(load_document(args.contract), args.executor_profile)
        if args.output:
            dump_document(args.output, result)
        else:
            print(json.dumps(result, sort_keys=False, indent=2))
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
