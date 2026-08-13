#!/usr/bin/env python3
"""Validate Franky v1 contracts and the canonical approved repertoire."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[2]
TASK_SCHEMA = ROOT / "ops/schemas/franky-task.schema.yaml"
RESULT_SCHEMA = ROOT / "ops/schemas/franky-result.schema.yaml"
DEFAULT_TASK = ROOT / "ops/schemas/examples/franky-task.yaml"
DEFAULT_RESULT = ROOT / "ops/schemas/examples/franky-result.yaml"
DEFAULT_REPERTOIRE = ROOT / "manifests/agent-capability-repertoires.yaml"
EXPECTED_AGENTS = {"franky", "feynman", "prometheus", "athena", "argus"}
REQUIRED_AUTHORITY = {
    "inspect_control_plane",
    "propose_changes",
    "modify_allowed_control_plane_files",
    "run_validators",
    "produce_acceptance_ready_evidence",
}
FORBIDDEN_AUTHORITY = {
    "final_accept_own_change",
    "modify_global_policy_without_review",
    "change_agent_roles_without_decision",
    "alter_validation_requirements",
    "approve_runtime_security_changes",
}


def _validate(value: object, spec: dict, path: str) -> None:
    expected = spec.get("type")
    if expected == "object" and not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    if expected == "array" and not isinstance(value, list):
        raise ValueError(f"{path}: expected array")
    if expected == "string" and (not isinstance(value, str) or len(value) < spec.get("minLength", 0)):
        raise ValueError(f"{path}: expected non-empty string")
    if expected == "boolean" and not isinstance(value, bool):
        raise ValueError(f"{path}: expected boolean")
    if expected == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
        raise ValueError(f"{path}: expected integer")
    if "const" in spec and value != spec["const"]:
        raise ValueError(f"{path}: expected {spec['const']!r}")
    if "enum" in spec and value not in spec["enum"]:
        raise ValueError(f"{path}: expected one of {spec['enum']}")
    if expected == "object":
        required = spec.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            raise ValueError(f"{path}: missing required field(s): {', '.join(missing)}")
        properties = spec.get("properties", {})
        if spec.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            if unknown:
                raise ValueError(f"{path}: undeclared field(s): {', '.join(unknown)}")
        for key, child in value.items():
            if key in properties:
                _validate(child, properties[key], f"{path}.{key}")
    if expected == "array":
        if len(value) < spec.get("minItems", 0):
            raise ValueError(f"{path}: requires at least {spec['minItems']} item(s)")
        for index, child in enumerate(value):
            _validate(child, spec.get("items", {}), f"{path}[{index}]")


def _load(path: Path) -> object:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _validate_schema(document: object, schema_path: Path, document_path: Path) -> None:
    _validate(document, _load(schema_path), str(document_path))


def _validate_repertoire(path: Path) -> dict:
    document = _load(path)
    if document.get("schema_version") != 1:
        raise ValueError("repertoire: schema_version must be 1")
    agents = document.get("agents")
    if not isinstance(agents, dict) or set(agents) != EXPECTED_AGENTS:
        raise ValueError(f"repertoire: expected exactly {sorted(EXPECTED_AGENTS)}")
    franky = agents["franky"]
    if "shared-session-closeout" not in franky.get("lifecycle_capabilities", []):
        raise ValueError("repertoire.franky: shared-session-closeout is mandatory for consequential closure")
    if "skill-creator" in franky.get("primary_capabilities", []):
        raise ValueError("repertoire.franky: local skill-creator ownership is governed by Issue #38")
    for name, entry in agents.items():
        for field in ("primary_capabilities", "lifecycle_capabilities", "conditional_capabilities"):
            if not isinstance(entry.get(field), list):
                raise ValueError(f"repertoire.{name}.{field}: expected list")
    return document


def validate(task_path: Path, result_path: Path, repertoire_path: Path) -> None:
    task = _load(task_path)
    result = _load(result_path)
    _validate_schema(task, TASK_SCHEMA, task_path)
    _validate_schema(result, RESULT_SCHEMA, result_path)
    repertoire = _validate_repertoire(repertoire_path)
    if task["contract_version"]["major"] != 1:
        raise ValueError("task.contract_version.major: unsupported major version")
    if "franky.result.v1" not in task["accepted_result_versions"]:
        raise ValueError("task.accepted_result_versions: franky.result.v1 is required")
    if result["contract_version"]["major"] != task["contract_version"]["major"]:
        raise ValueError("task/result contract major versions must match")
    authority_matrix = task["authority_matrix"]
    if not REQUIRED_AUTHORITY.issubset(set(authority_matrix["franky_can"])):
        raise ValueError("authority_matrix.franky_can is missing a required authority")
    if not FORBIDDEN_AUTHORITY.issubset(set(authority_matrix["franky_cannot"])):
        raise ValueError("authority_matrix.franky_cannot is missing a required boundary")
    if task["authority"]["architecture_change"] == "allowed" and task.get("review", {}).get("required") is not True:
        raise ValueError("architecture-change request requires an explicit review flag")
    franky = repertoire["agents"]["franky"]
    approved = set(franky["primary_capabilities"])
    approved.update(franky["lifecycle_capabilities"])
    approved.update(franky["conditional_capabilities"])
    approved.update(item["capability"] for item in franky["external_or_runtime_dependencies"])
    unknown_required = sorted(set(task["required_capabilities"]) - approved)
    if unknown_required:
        raise ValueError(f"task.required_capabilities: not in Franky repertoire: {', '.join(unknown_required)}")
    routed = {result["routing"]["primary_capability"], *result["routing"]["supporting_capabilities"]}
    unknown_routed = sorted(routed - approved)
    if unknown_routed:
        raise ValueError(f"result.routing: not in Franky repertoire: {', '.join(unknown_routed)}")
    if task["request_id"] != result["request_id"]:
        raise ValueError("task/result request_id values must match")
    expected_commit = result["evidence_freshness"]["source_commit"]
    for index, item in enumerate(result["lifecycle"]["evidence"]):
        provenance = item["provenance"]
        if provenance["result"] != item["status"]:
            raise ValueError(f"lifecycle evidence[{index}] provenance.result must match status")
        if provenance["commit"] != expected_commit:
            raise ValueError("lifecycle evidence provenance must share evidence_freshness.source_commit")
    for name, evidence in result["runtime_evidence"].items():
        if evidence.get("status") not in {"PASS", "BLOCKED", "NOT_ASSESSED"}:
            raise ValueError(f"runtime_evidence.{name}: invalid status")
        if not isinstance(evidence.get("evidence"), str) or not evidence["evidence"].strip():
            raise ValueError(f"runtime_evidence.{name}: evidence is required")
    lifecycle = result["lifecycle"]
    expected_states = ["REQUEST", "CONTRACT", "ADMISSION", "ROUTING", "IMPACT", "EXECUTION", "VALIDATION", "CLOSURE", "ACCEPTANCE_READY"]
    evidence_states = [item["state"] for item in lifecycle["evidence"]]
    if lifecycle["state"] not in expected_states:
        raise ValueError("lifecycle state is not canonical")
    target_index = expected_states.index(lifecycle["state"])
    if evidence_states != expected_states[: target_index + 1]:
        raise ValueError("lifecycle evidence must be ordered evidence prefix ending at declared state")
    if any(item["status"] != "PASS" for item in lifecycle["evidence"][:-1]):
        raise ValueError("completed lifecycle prefix cannot contain non-PASS evidence")
    if lifecycle["state"] == "ACCEPTANCE_READY" and lifecycle["evidence"][-1]["status"] != "PASS":
        raise ValueError("acceptance_ready lifecycle cannot contain non-PASS evidence")
    if result["status"] == "acceptance_ready" and lifecycle["state"] != "ACCEPTANCE_READY":
        raise ValueError("acceptance_ready result must have ACCEPTANCE_READY lifecycle state")
    if result["status"] != "acceptance_ready" and lifecycle["state"] == "ACCEPTANCE_READY":
        raise ValueError("non-acceptance-ready result cannot claim ACCEPTANCE_READY lifecycle state")
    if task["intent"]["mode"] == "mutate" and task["authority"]["mutation"] != "allowed":
        raise ValueError("mutating task requires explicit mutation authority: allowed")
    lifecycle_capability = result["routing"].get("lifecycle_capability")
    consequential = task["intent"]["mode"] == "mutate" or task["intent"]["completion"] == "end_to_end"
    if consequential and lifecycle_capability != "shared-session-closeout":
        raise ValueError("consequential result must route closure through shared-session-closeout")
    if lifecycle_capability is not None and lifecycle_capability not in franky["lifecycle_capabilities"]:
        raise ValueError(f"result.routing.lifecycle_capability: not in Franky repertoire: {lifecycle_capability}")
    if lifecycle_capability is not None and not result["routing"].get("lifecycle_reason"):
        raise ValueError("lifecycle routing requires an explanation")
    if consequential and result["routing"].get("impact_required") is not True:
        raise ValueError("consequential result must declare impact_required: true")
    impact_evidence = result["routing"].get("impact_evidence")
    if consequential and not isinstance(impact_evidence, dict):
        raise ValueError("consequential result must provide structured impact_evidence")
    if consequential and not result["routing"]["supporting_capabilities"]:
        raise ValueError("consequential result must include impact-triggered supporting capability")
    supporting_reasons = result["routing"]["supporting_reasons"]
    if {item["capability"] for item in supporting_reasons} != set(result["routing"]["supporting_capabilities"]):
        raise ValueError("routing supporting reasons must explain exactly the supporting capabilities")
    if consequential and set(result["routing"]["supporting_capabilities"]) != set(impact_evidence["supporting_capabilities"]):
        raise ValueError("impact evidence must name exactly the routed supporting capabilities")
    if consequential and not impact_evidence["source_state"]:
        raise ValueError("impact evidence must be source-state-bound")
    validation_sources = {item["source_state"] for item in result["validation"]}
    if consequential and impact_evidence["source_state"] not in validation_sources:
        raise ValueError("impact evidence source_state must match validation source_state")
    allowed_surfaces = {"implementation/config", "canonical-state", "references/documentation", "validation/proof"}
    if consequential and not set(impact_evidence["surfaces"]).issubset(allowed_surfaces):
        raise ValueError("impact evidence contains an unknown closure surface")
    required = set(task["required_capabilities"])
    if result["routing"]["primary_capability"] not in required:
        raise ValueError("result primary capability must be declared by the task")
    if not set(result["routing"]["supporting_capabilities"]).issubset(required):
        raise ValueError("result supporting capabilities must be declared by the task")
    mutating_actions = {"created", "modified", "deleted"}
    if any(change["action"] in mutating_actions for change in result["changes"]):
        if task["authority"]["mutation"] != "allowed":
            raise ValueError("result with mutating changes requires explicit mutation authority: allowed")
    if result["status"] == "acceptance_ready":
        if result["unresolved"]["blockers"]:
            raise ValueError("acceptance_ready result cannot contain blockers")
        if any(item["status"] in {"FAIL", "BLOCKED"} for item in result["validation"]):
            raise ValueError("acceptance_ready result cannot contain failed or blocked validation")
        task_review_required = task.get("review", {}).get("required", False)
        if task_review_required and result["review"].get("required") is not True:
            raise ValueError("result cannot downgrade task-required independent review")
        if (task_review_required or result["review"]["required"]) and result["review"]["status"] != "PASS":
            raise ValueError("acceptance_ready result requires a completed independent review PASS")
        reviewer_id = result["review"]["reviewer_id"].lower()
        reviewer_role = result["review"]["reviewer_role"]
        if reviewer_id == "athena" and reviewer_role != "independent_reviewer":
            raise ValueError("Athena reviewer must be bound as independent_reviewer")
        if reviewer_id == "parent-control-plane" and reviewer_role != "parent_acceptance":
            raise ValueError("parent reviewer must be bound as parent_acceptance")
        if reviewer_id not in {"athena", "parent-control-plane"}:
            raise ValueError("acceptance_ready result requires a bound non-self reviewer identity")
        not_assessed = [
            name for name, value in result["closure"].items() if value == "NOT_ASSESSED"
        ]
        if not_assessed and not result["unresolved"]["limitations"]:
            raise ValueError("NOT_ASSESSED closure surfaces require explicit limitations")
        if any(item["status"] == "NOT_ASSESSED" for item in result["validation"]):
            if not result["unresolved"]["limitations"]:
                raise ValueError("NOT_ASSESSED validation requires explicit limitations")
        freshness = result["evidence_freshness"]
        if not freshness["mutation_free_since_validation"] or freshness["invalidated_by_mutation"]:
            raise ValueError("acceptance_ready evidence is stale after mutation")
        for name, evidence in result["runtime_evidence"].items():
            if evidence["status"] != "PASS" and not result["unresolved"]["limitations"]:
                raise ValueError(f"runtime_evidence.{name} requires an explicit limitation")
        if result["review"]["status"] == "PASS" and not result["review"]["scope"]:
            raise ValueError("independent review PASS requires a declared scope")
    if result["status"] == "acceptance_ready" and any(
        value == "BLOCKED" for value in result["closure"].values()
    ):
        raise ValueError("acceptance_ready result cannot have a blocked closure surface")


def _enforce_current_head(result_path: Path) -> None:
    result = _load(result_path)
    if result.get("status") != "acceptance_ready" or result.get("evidence_freshness", {}).get("source_commit") != "HEAD":
        return
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"cannot verify current Git state for HEAD-bound evidence: {exc}") from exc
    if not head:
        raise ValueError("cannot resolve current Git HEAD for evidence")
    if dirty:
        raise ValueError("acceptance_ready HEAD-bound evidence requires a clean working tree")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", type=Path, default=DEFAULT_TASK)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--repertoire", type=Path, default=DEFAULT_REPERTOIRE)
    args = parser.parse_args()
    try:
        validate(args.task, args.result, args.repertoire)
        _enforce_current_head(args.result)
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL franky-contracts: {exc}")
        return 1
    print("OK franky-contracts: task, result, and approved repertoire")
    return 0


if __name__ == "__main__":
    sys.exit(main())
