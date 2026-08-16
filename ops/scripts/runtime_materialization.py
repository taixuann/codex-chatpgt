#!/usr/bin/env python3
"""Deterministic repository-level runtime materialization proof.

This module is deliberately not a host dispatcher or model router.  It resolves
checked-in contracts, executes one deterministic operation, and validates the
resulting artifact and repository-level authority boundary.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import tomllib
from typing import Any

import yaml


REQUIRED_ARTIFACT_FIELDS = {
    "request_id",
    "agent",
    "skill",
    "provenance",
    "lifecycle_state",
    "validation_result",
}
ALLOWED_TRANSITIONS = {"DRAFT": {"VALIDATED"}, "VALIDATED": set()}


class MaterializationError(ValueError):
    """Raised when a repository-level materialization contract is invalid."""


def _load_agent(path: Path, expected: str) -> dict[str, Any]:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise MaterializationError(f"agent contract unreadable: {path}") from exc
    if data.get("name") != expected:
        raise MaterializationError(f"agent contract name mismatch: {expected}")
    return data


def _load_catalog(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise MaterializationError(f"skill catalog unreadable: {path}") from exc
    if not isinstance(data, dict):
        raise MaterializationError("skill catalog must be a mapping")
    return data


def resolve_context(
    *,
    agent: str,
    skill: str,
    authority: str,
    permissions: dict[str, bool],
    agents_root: Path,
    catalog_path: Path,
) -> dict[str, Any]:
    """Resolve one compatible agent/skill pair into an execution context."""
    if not authority or not isinstance(permissions, dict):
        raise MaterializationError("authority and permissions are required")
    agent_data = _load_agent(agents_root / f"{agent}.toml", agent)
    catalog = _load_catalog(catalog_path)
    active = set(catalog.get("canonical_active") or [])
    if skill not in active:
        raise MaterializationError(f"skill is not canonical_active: {skill}")
    capability_map = {
        "franky": {
            "control-plane-audit",
            "instruction-maintenance",
            "runtime-adapter-management",
            "external-handoff",
            "shared-session-closeout",
        },
    }
    if skill not in capability_map.get(agent, set()):
        raise MaterializationError(f"skill is incompatible with agent: {agent}/{skill}")
    return {
        "agent": agent_data["name"],
        "skill": skill,
        "authority": authority,
        "permissions": dict(permissions),
        "validation_state": "RESOLVED",
    }


def validate_artifact(artifact: dict[str, Any]) -> None:
    missing = REQUIRED_ARTIFACT_FIELDS - set(artifact)
    if missing:
        raise MaterializationError(f"artifact missing fields: {sorted(missing)}")
    if not artifact["request_id"] or not artifact["agent"] or not artifact["skill"]:
        raise MaterializationError("artifact identity fields must be non-empty")
    if not isinstance(artifact["provenance"], dict) or not artifact["provenance"].get("source"):
        raise MaterializationError("artifact provenance.source is required")
    if artifact["lifecycle_state"] not in (set(ALLOWED_TRANSITIONS) | {"VALIDATED"}):
        raise MaterializationError("unknown artifact lifecycle state")
    if artifact["validation_result"] not in {"PASS", "REJECT"}:
        raise MaterializationError("artifact validation_result must be PASS or REJECT")


def transition_artifact(artifact: dict[str, Any], target: str) -> dict[str, Any]:
    current = artifact.get("lifecycle_state")
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise MaterializationError(f"invalid artifact transition: {current} -> {target}")
    updated = dict(artifact)
    updated["lifecycle_state"] = target
    validate_artifact(updated)
    return updated


def execute(
    context: dict[str, Any],
    input_artifact: dict[str, Any],
    *,
    request_id: str,
    action: str = "audit",
    mutation_requested: bool = False,
) -> dict[str, Any]:
    """Execute a deterministic audit boundary and emit a validated artifact."""
    validate_artifact(input_artifact)
    if input_artifact["lifecycle_state"] != "DRAFT":
        raise MaterializationError("input artifact must be DRAFT")
    if mutation_requested and not context["permissions"].get("mutate", False):
        return {
            "request_id": request_id,
            "agent": context["agent"],
            "skill": context["skill"],
            "provenance": {"source": "runtime_materialization", "input_request": request_id},
            "lifecycle_state": "DRAFT",
            "validation_result": "REJECT",
            "execution": {"action": action, "status": "REJECT", "reason": "mutation_not_authorized"},
        }
    digest = hashlib.sha256(repr(sorted(input_artifact.items())).encode("utf-8")).hexdigest()
    output = {
        "request_id": request_id,
        "agent": context["agent"],
        "skill": context["skill"],
        "provenance": {
            "source": "runtime_materialization",
            "input_digest": digest,
            "authority": context["authority"],
        },
        "lifecycle_state": "DRAFT",
        "validation_result": "PASS",
        "execution": {"action": action, "status": "PASS", "mutation": False},
    }
    return transition_artifact(output, "VALIDATED")
