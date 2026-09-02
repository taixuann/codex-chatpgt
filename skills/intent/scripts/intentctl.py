#!/usr/bin/env python3
"""Small deterministic helper for the intent run-state contract.

This command observes and validates state; it does not interpret intent or
mutate Issues, plans, tasks, or repository source.  ``--write`` is required
for derived staleness/recovery updates.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
MATRIX_PATH = ROOT / "skills/intent/references/requirement-matrix.yaml"
STAGE_STATUSES = {"passed", "skipped_with_reason", "not_applicable", "blocked", "failed"}
REQUIREMENTS = {"required", "optional", "conditional", "not_applicable"}
CLAIM_STATES = {"CONFIRMED", "INFERRED", "UNKNOWN", "USER_DECISION", "PROPOSED"}
TRUST_VALUES = {
    "freshness": {"fresh", "stale_soft", "stale_review_required", "stale_hard"},
    "completeness": {"complete", "partial"},
    "integrity": {"valid", "invalid"},
    "scope_match": {"exact", "related", "mismatch"},
    "evidence_traceability": {"complete", "partial"},
}
PROCEDURE_TRACE = {
    "workspace_anchor": ["workspace-resolution.md"],
    "source_intake": ["source-contract.md"],
    "context_resolution": ["context-resolution.md"],
    "evidence_acquisition": ["evidence-classification.md"],
    "claim_audit": ["evidence-classification.md"],
    "relationship_audit": ["relationship-audit.md"],
    "staleness": ["adaptive-depth.md"],
    "authority_resolution": ["quality-gates.md"],
    "convergence_audit": ["convergence-audit.md"],
    "orientation": ["orientation-view.md"],
    "session_handoff": ["intent-handoff.md"],
    "fresh_context_eval": ["intent-handoff.md"],
}
ISSUE_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*$")
ISSUE_URL_RE = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/[1-9][0-9]*$"
)


class IntentError(ValueError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise IntentError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def workspace_report(cwd: Path | None = None) -> dict[str, Any]:
    active = (cwd or Path.cwd()).expanduser().resolve()
    report: dict[str, Any] = {
        "cwd": str(active),
        "repo_root": None,
        "head": "uncommitted",
        "branch": "none",
        "dirty": False,
        "instruction_chain": [],
    }
    try:
        root = Path(run_git(active, "rev-parse", "--show-toplevel")).resolve()
        report["repo_root"] = str(root)
        report["head"] = run_git(active, "rev-parse", "HEAD")
        try:
            report["branch"] = run_git(active, "symbolic-ref", "--quiet", "--short", "HEAD")
        except IntentError:
            report["branch"] = "(detached)"
        report["dirty"] = bool(run_git(active, "status", "--porcelain"))
        if active == root or root in active.parents:
            chain: list[str] = []
            current = root
            while True:
                candidate = current / "AGENTS.md"
                if candidate.is_file():
                    chain.append(candidate.relative_to(root).as_posix())
                if current == active:
                    break
                try:
                    current = current / active.relative_to(current).parts[0]
                except ValueError:
                    break
            report["instruction_chain"] = chain
    except IntentError:
        report["instruction_chain"] = ["(no Git project anchor)"]
    return report


def load_matrix() -> dict[str, Any]:
    try:
        data = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise IntentError(f"cannot load requirement matrix: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise IntentError("requirement matrix must declare schema_version: 1")
    profiles = data.get("profiles")
    stages = data.get("stages")
    if not isinstance(profiles, dict) or not isinstance(stages, list) or not stages:
        raise IntentError("requirement matrix profiles and stages are required")
    for profile, requirements in profiles.items():
        if not isinstance(requirements, dict) or set(requirements) != set(stages):
            raise IntentError(f"matrix profile {profile} must cover every stage")
        if any(value not in REQUIREMENTS for value in requirements.values()):
            raise IntentError(f"matrix profile {profile} contains an invalid requirement")
    return data


def profile_for(origin: str, depth: str) -> str:
    prefix = "issue" if origin == "github_issue" else "idea"
    return f"{prefix}_{depth}"


def _stage(status: str, reason: str | None = None) -> dict[str, Any]:
    value: dict[str, Any] = {"status": status, "evidence": []}
    if reason:
        value["reason"] = reason
    return value


def init_run(origin: str, locator: str, depth: str, cwd: Path) -> dict[str, Any]:
    matrix = load_matrix()
    profile = profile_for(origin, depth)
    requirements = matrix["profiles"].get(profile)
    if requirements is None:
        raise IntentError(f"no requirement profile for {origin}/{depth}")
    workspace = workspace_report(cwd)
    stages = {}
    for name, requirement in requirements.items():
        if requirement == "required":
            stages[name] = _stage("blocked", "pending execution")
        elif requirement == "not_applicable":
            stages[name] = _stage("not_applicable", "not applicable for this origin/depth")
        else:
            stages[name] = _stage("not_applicable", "not selected at initialization")
    return {
        "intent_run": {
            "schema_version": 1,
            "origin": {"type": origin, "locator": locator, "observed_at": now()},
            "workspace": workspace,
            "depth": depth,
            "profile": profile,
            "stages": stages,
            "evidence": [],
            "claims": [],
            "decisions": [],
            "relationships": [],
            "unknowns": [],
            "contradictions": [],
            "blockers": [],
            "procedure_trace": PROCEDURE_TRACE,
            "intent": {
                "objective": "",
                "why": "",
                "current_state": "",
                "target_state": "",
                "success_criteria": [],
                "scope": [],
                "out_of_scope": [],
            },
            "orientation": None,
            "handoff": {
                "packet": None,
                "recovery": None,
            },
            "trust": {
                "freshness": "fresh",
                "completeness": "partial",
                "integrity": "valid",
                "scope_match": "exact",
                "evidence_traceability": "partial",
            },
        }
    }


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise IntentError(f"{field} must be a mapping")
    return value


def validate_run(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict) or set(data) != {"intent_run"}:
        return ["document must contain only an intent_run mapping"]
    run = _require_mapping(data["intent_run"], "intent_run")
    if run.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    origin = _require_mapping(run.get("origin"), "origin") if isinstance(run.get("origin"), dict) else {}
    origin_type = origin.get("type")
    locator = origin.get("locator")
    if origin_type not in {"github_issue", "user_idea"}:
        errors.append("origin.type must be github_issue or user_idea")
    if not isinstance(locator, str) or not locator.strip():
        errors.append("origin.locator is required")
    elif origin_type == "github_issue" and not (ISSUE_RE.fullmatch(locator) or ISSUE_URL_RE.fullmatch(locator)):
        errors.append("github_issue locator must be owner/repo#number or canonical Issue URL")
    if not isinstance(origin.get("observed_at"), str) or not origin.get("observed_at"):
        errors.append("origin.observed_at is required")
    depth = run.get("depth")
    if depth not in {"light", "focused", "deep"}:
        errors.append("depth must be light, focused, or deep")
    matrix = load_matrix()
    profile = profile_for(origin_type, depth) if origin_type in {"github_issue", "user_idea"} and depth in {"light", "focused", "deep"} else None
    if profile and run.get("profile") != profile:
        errors.append(f"profile must be {profile}")

    workspace = run.get("workspace")
    if not isinstance(workspace, dict):
        errors.append("workspace must be a mapping")
    else:
        if not isinstance(workspace.get("cwd"), str) or not workspace.get("cwd"):
            errors.append("workspace.cwd is required")
        if workspace.get("repo_root") is not None and (not isinstance(workspace.get("repo_root"), str) or not workspace.get("repo_root")):
            errors.append("workspace.repo_root must be a path or null")
        for field in ("head", "branch"):
            if not isinstance(workspace.get(field), str) or not workspace.get(field):
                errors.append(f"workspace.{field} is required")
        if not isinstance(workspace.get("dirty"), bool):
            errors.append("workspace.dirty must be boolean")
        if not isinstance(workspace.get("instruction_chain"), list):
            errors.append("workspace.instruction_chain must be a list")

    requirements = matrix["profiles"].get(profile, {}) if profile else {}
    stages = run.get("stages")
    if not isinstance(stages, dict):
        errors.append("stages must be a mapping")
        stages = {}
    if set(stages) != set(requirements):
        errors.append("stages must exactly match the selected requirement profile")
    for name in requirements:
        stage = stages.get(name)
        if not isinstance(stage, dict):
            errors.append(f"stage {name} must be a mapping")
            continue
        status = stage.get("status")
        if status not in STAGE_STATUSES:
            errors.append(f"stage {name} has invalid status")
        if status in {"blocked", "failed", "skipped_with_reason", "not_applicable"} and not str(stage.get("reason", "")).strip():
            errors.append(f"stage {name} requires a reason for status {status}")
        if not isinstance(stage.get("evidence", []), list):
            errors.append(f"stage {name}.evidence must be a list")

    evidence = run.get("evidence", [])
    evidence_ids: set[str] = set()
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
        evidence = []
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{index}] must be a mapping")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in evidence_ids:
            errors.append(f"evidence[{index}].id must be unique and non-empty")
        else:
            evidence_ids.add(ident)
        for field in ("locator", "kind", "observed_at"):
            if not isinstance(item.get(field), str) or not item.get(field).strip():
                errors.append(f"evidence[{index}].{field} is required")
    if isinstance(stages, dict):
        for stage, record in stages.items():
            refs = record.get("evidence", []) if isinstance(record, dict) else []
            if isinstance(refs, list) and any(ref not in evidence_ids for ref in refs):
                errors.append(f"stage {stage}.evidence contains a dangling reference")

    claims = run.get("claims", [])
    if not isinstance(claims, list):
        errors.append("claims must be a list")
        claims = []
    claim_ids: set[str] = set()
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claims[{index}] must be a mapping")
            continue
        ident = claim.get("id")
        if not isinstance(ident, str) or not ident.strip() or ident in claim_ids:
            errors.append(f"claims[{index}].id must be unique and non-empty")
        else:
            claim_ids.add(ident)
        if not isinstance(claim.get("text"), str) or not claim.get("text").strip():
            errors.append(f"claims[{index}].text is required")
        state = claim.get("state")
        if state not in CLAIM_STATES:
            errors.append(f"claims[{index}].state is invalid")
        refs = claim.get("evidence", [])
        if not isinstance(refs, list) or any(ref not in evidence_ids for ref in refs):
            errors.append(f"claims[{index}].evidence contains a dangling reference")
        if state == "CONFIRMED" and not refs:
            errors.append(f"claims[{index}] confirmed claims require evidence")

    for field in ("relationships", "unknowns", "blockers", "contradictions"):
        if not isinstance(run.get(field, []), list):
            errors.append(f"{field} must be a list")
    trace = run.get("procedure_trace")
    if not isinstance(trace, dict):
        errors.append("procedure_trace must be a mapping")
    else:
        for stage, refs in trace.items():
            if stage not in PROCEDURE_TRACE:
                errors.append(f"procedure_trace contains unknown stage: {stage}")
                continue
            if not isinstance(refs, list) or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
                errors.append(f"procedure_trace.{stage} must be a list of references")
            for ref in refs if isinstance(refs, list) else []:
                if not (ROOT / "skills/intent/references" / ref).is_file():
                    errors.append(f"procedure_trace.{stage} reference does not resolve: {ref}")
    decisions = run.get("decisions", [])
    if not isinstance(decisions, list):
        errors.append("decisions must be a list")
    else:
        for index, decision in enumerate(decisions):
            if not isinstance(decision, dict) or not isinstance(decision.get("status"), str):
                errors.append(f"decisions[{index}] must declare a status")

    intent = run.get("intent")
    if not isinstance(intent, dict):
        errors.append("intent must be a mapping")
    else:
        for field in ("objective", "why", "current_state", "target_state"):
            if not isinstance(intent.get(field), str):
                errors.append(f"intent.{field} must be a string")
        for field in ("success_criteria", "scope", "out_of_scope"):
            value = intent.get(field)
            if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
                errors.append(f"intent.{field} must be a list of strings")

    handoff = run.get("handoff")
    if not isinstance(handoff, dict):
        errors.append("handoff must be a mapping")
    else:
        if handoff.get("packet") is not None and not isinstance(handoff.get("packet"), str):
            errors.append("handoff.packet must be a path or null")
        recovery = handoff.get("recovery")
        if recovery is not None and not isinstance(recovery, dict):
            errors.append("handoff.recovery must be a mapping or null")

    trust = run.get("trust")
    if not isinstance(trust, dict):
        errors.append("trust must be a mapping")
    else:
        for field, allowed in TRUST_VALUES.items():
            if trust.get(field) not in allowed:
                errors.append(f"trust.{field} is invalid")
    return errors


def load_run(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise IntentError(f"cannot read run state: {exc}") from exc
    if not isinstance(data, dict):
        raise IntentError("run state must be a YAML mapping")
    return data


def save_run(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def readiness(data: dict[str, Any]) -> list[str]:
    errors = validate_run(data)
    if errors:
        return errors
    run = data["intent_run"]
    requirements = load_matrix()["profiles"][run["profile"]]
    trace = run["procedure_trace"]
    for stage, requirement in requirements.items():
        if requirement == "required" and not trace.get(stage):
            errors.append(f"required procedure trace missing: {stage}")
    for name, requirement in requirements.items():
        status = run["stages"][name]["status"]
        if requirement == "required" and status != "passed":
            errors.append(f"missing required stage: {name}")
        if requirement in {"conditional", "optional"} and status in {"blocked", "failed"}:
            errors.append(f"stage {name} is {status}")
    for decision in run.get("decisions", []):
        if decision.get("status") in {"open", "blocked", "unresolved"}:
            errors.append("unresolved authority decision remains")
    if run.get("contradictions"):
        errors.append("unresolved contradictions remain")
    intent = run["intent"]
    for field in ("objective", "why"):
        if not intent[field].strip():
            errors.append(f"G5 boundary field missing: intent.{field}")
    for field in ("success_criteria", "scope", "out_of_scope"):
        if not intent[field]:
            errors.append(f"G5 boundary field missing: intent.{field}")
    handoff = run["handoff"]
    if requirements.get("session_handoff") == "required":
        packet = handoff.get("packet")
        packet_path = Path(packet).expanduser() if packet else None
        if packet_path is not None and not packet_path.is_absolute():
            packet_path = ROOT / packet_path
        if packet_path is None or not packet_path.exists():
            errors.append("required session handoff packet is missing")
        elif not _session_packet_valid(packet_path):
            errors.append("required session handoff packet failed shared validation")
    if requirements.get("fresh_context_eval") == "required":
        recovery = handoff.get("recovery") or {}
        try:
            derived_recovery = fresh_context(data)
        except IntentError as exc:
            errors.append(f"fresh-context evaluation is invalid: {exc}")
        else:
            if recovery.get("status") != "passed" or derived_recovery.get("status") != "passed":
                errors.append("fresh-context evaluation has not passed")
    trust = run["trust"]
    if trust["freshness"] in {"stale_review_required", "stale_hard"}:
        errors.append(f"freshness requires review: {trust['freshness']}")
    if trust["completeness"] != "complete":
        errors.append("trust completeness is not complete")
    if trust["integrity"] != "valid":
        errors.append("trust integrity is not valid")
    if trust["scope_match"] != "exact":
        errors.append("trust scope_match is not exact")
    if trust["evidence_traceability"] != "complete":
        errors.append("evidence traceability is incomplete")
    if run.get("blockers"):
        errors.extend(f"blocker: {item}" for item in run["blockers"])
    return errors


def _session_packet_valid(packet: Path) -> bool:
    """Reuse the shared packet validator without copying its contract."""
    validator = ROOT / "skills/control-plane/session-packet-management/scripts/validate_session_packet.py"
    if not validator.is_file():
        return False
    result = subprocess.run(
        [sys.executable, str(validator), str(packet)],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def staleness(data: dict[str, Any], cwd: Path) -> dict[str, Any]:
    errors = validate_run(data)
    if errors:
        raise IntentError("invalid run state: " + "; ".join(errors))
    run = data["intent_run"]
    observed = run["workspace"]
    current = workspace_report(cwd)
    if current.get("repo_root") != observed.get("repo_root"):
        freshness = "stale_hard"
    elif current.get("head") != observed.get("head"):
        freshness = "stale_review_required"
    elif current.get("branch") != observed.get("branch") or current.get("dirty") != observed.get("dirty"):
        freshness = "stale_soft"
    else:
        freshness = "fresh"
    return {"freshness": freshness, "observed": observed, "current": current}


RECOVERY_FIELDS = (
    "objective", "why", "scope", "out_of_scope", "success", "current_state",
    "surfaces", "relationships", "decisions", "unknowns", "evidence_traceability",
)


def fresh_context(data: dict[str, Any]) -> dict[str, Any]:
    errors = validate_run(data)
    if errors:
        raise IntentError("invalid run state: " + "; ".join(errors))
    run = data["intent_run"]
    intent = run["intent"]
    workspace = run["workspace"]
    fields = {
        "objective": bool(intent["objective"].strip()),
        "why": bool(intent["why"].strip()),
        "scope": bool(intent["scope"]),
        "out_of_scope": bool(intent["out_of_scope"]),
        "success": bool(intent["success_criteria"]),
        "current_state": bool(intent["current_state"].strip() and workspace.get("cwd") and workspace.get("head")),
        "surfaces": bool(run.get("evidence")),
        "relationships": isinstance(run.get("relationships"), list),
        "decisions": isinstance(run.get("decisions"), list),
        "unknowns": isinstance(run.get("unknowns"), list),
        "evidence_traceability": run["trust"]["evidence_traceability"] == "complete",
    }
    score = sum(1 for field in RECOVERY_FIELDS if fields.get(field) is True)
    missing = [field for field in RECOVERY_FIELDS if fields.get(field) is not True]
    recovery = (run.get("handoff") or {}).get("recovery") or {}
    burden = len(missing)
    unsupported = 0
    packet = (run.get("handoff") or {}).get("packet")
    profile = run.get("profile", "")
    packet_path = Path(packet).expanduser() if packet else None
    if packet_path is not None and not packet_path.is_absolute():
        packet_path = ROOT / packet_path
    if profile.endswith(("_focused", "_deep")) and (packet_path is None or not packet_path.exists()):
        missing.append("session_packet")
        burden += 1
    status = "passed" if score >= 10 and burden == 0 and unsupported == 0 else "blocked"
    return {
        "status": status,
        "context_recovery_score": {"passed": score, "total": len(RECOVERY_FIELDS)},
        "fields": fields,
        "rediscovery_burden": burden,
        "unsupported_reconstruction": unsupported,
        "missing": missing,
    }


def emit(value: Any, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(value, indent=2, sort_keys=False))
    else:
        print(yaml.safe_dump(value, sort_keys=False).rstrip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="intentctl")
    sub = parser.add_subparsers(dest="command", required=True)
    workspace = sub.add_parser("workspace")
    workspace.add_argument("--json", action="store_true", help="emit JSON")
    workspace.add_argument("--cwd", type=Path, default=Path.cwd())
    init = sub.add_parser("init")
    init.add_argument("--json", action="store_true", help="emit JSON")
    init.add_argument("--origin", choices=("github_issue", "user_idea"), required=True)
    init.add_argument("--locator", required=True)
    init.add_argument("--depth", choices=("light", "focused", "deep"), default="light")
    init.add_argument("--cwd", type=Path, default=Path.cwd())
    init.add_argument("--output", type=Path, required=True)
    for name in ("status", "validate", "staleness", "readiness", "fresh-context"):
        command = sub.add_parser(name)
        command.add_argument("--json", action="store_true", help="emit JSON")
        command.add_argument("run", type=Path)
        if name == "staleness":
            command.add_argument("--cwd", type=Path, default=Path.cwd())
            command.add_argument("--write", action="store_true")
        if name == "fresh-context":
            command.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "workspace":
            emit(workspace_report(args.cwd), args.json)
            return 0
        if args.command == "init":
            if args.origin == "github_issue" and not (ISSUE_RE.fullmatch(args.locator) or ISSUE_URL_RE.fullmatch(args.locator)):
                raise IntentError("github_issue locator must be canonical")
            data = init_run(args.origin, args.locator, args.depth, args.cwd)
            save_run(args.output, data)
            emit({"status": "initialized", "output": str(args.output), "profile": data["intent_run"]["profile"]}, args.json)
            return 0
        data = load_run(args.run)
        if args.command == "validate":
            errors = validate_run(data)
            if errors:
                for error in errors:
                    print(f"FAIL intent run: {error}")
                return 1
            print("OK intent run: schema, origin, matrix, stage, claim, and trust invariants valid")
            return 0
        if args.command == "status":
            run = data.get("intent_run", {})
            requirements = load_matrix().get("profiles", {}).get(run.get("profile"), {})
            emit({"profile": run.get("profile"), "depth": run.get("depth"), "stages": {
                name: {"requiredness": req, "status": run.get("stages", {}).get(name, {}).get("status")}
                for name, req in requirements.items()
            }, "blockers": run.get("blockers", [])}, args.json)
            return 0
        if args.command == "staleness":
            result = staleness(data, args.cwd)
            if args.write:
                data["intent_run"]["trust"]["freshness"] = result["freshness"]
                save_run(args.run, data)
            emit(result, args.json)
            return 0
        if args.command == "fresh-context":
            result = fresh_context(data)
            if args.write:
                handoff = data["intent_run"].setdefault("handoff", {})
                recovery = handoff.get("recovery")
                if not isinstance(recovery, dict):
                    recovery = {}
                    handoff["recovery"] = recovery
                recovery.update(result)
                data["intent_run"]["stages"]["fresh_context_eval"] = _stage(result["status"], "rubric evaluation")
                data["intent_run"]["trust"]["completeness"] = "complete" if result["status"] == "passed" else "partial"
                save_run(args.run, data)
            emit(result, args.json)
            return 0 if result["status"] == "passed" else 1
        if args.command == "readiness":
            errors = readiness(data)
            if errors:
                print("INTENT_BLOCKED")
                for error in errors:
                    print(f"- {error}")
                return 1
            print("INTENT_READY")
            print("PLAN_READY")
            return 0
    except (IntentError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL intentctl: {exc}")
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
