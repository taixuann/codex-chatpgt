#!/usr/bin/env python3
"""Deterministic packet/result normalization for the fresh Athena boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

INVALID_REVIEWER_IDS = {"", "NOT_ASSESSED", "UNKNOWN", "UNAVAILABLE", "NONE", "NULL"}
NATIVE_REVIEWER_ID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
ATHENA_PROVIDER_INVALID = {"", "NOT_ASSESSED", "UNKNOWN", "UNAVAILABLE", "NONE", "NULL"}
SUPPORTING_DOCUMENT_DISPOSITIONS = {"UPDATED", "VERIFIED_UNCHANGED", "NOT_APPLICABLE", "BLOCKED"}
FINDING_EVIDENCE_STATES = {"verified", "plausible_unverified", "refuted", "not_assessed"}
FINDING_EVIDENCE_PRIORITY = {"refuted": 0, "not_assessed": 1, "plausible_unverified": 2, "verified": 3}
FINDING_SEVERITY_PRIORITY = {"minor": 0, "material": 1, "major": 2, "blocker": 3, "critical": 4}
REVIEW_AXES = {"work", "goal", "joint"}


def observed_reviewer_id(value: Any) -> bool:
    return isinstance(value, str) and value.strip().upper() not in INVALID_REVIEWER_IDS and NATIVE_REVIEWER_ID.fullmatch(value.strip()) is not None


def review_attempt(packet: dict[str, Any], reviewer_session_id: str) -> dict[str, Any]:
    """Derive readable tracking identity without making it an authority."""
    spec = packet.get("review_attempt")
    if not isinstance(spec, dict) or spec.get("axis") not in REVIEW_AXES or isinstance(spec.get("round"), bool) or not isinstance(spec.get("round"), int) or spec["round"] < 1:
        raise ValueError("review_attempt requires axis work, goal, or joint and a positive round")
    candidate = str((packet.get("candidate") or {}).get("head", ""))
    if not re.fullmatch(r"[0-9a-f]{40}", candidate):
        raise ValueError("review_attempt requires an exact candidate head")
    authority = packet.get("authority") or {}
    repository = str(authority.get("repository", "")).strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("review_attempt requires owner/repository authority")
    target = f"pr-{authority['pr']}" if isinstance(authority.get("pr"), int) and authority["pr"] > 0 else f"issue-{authority.get('issue', '')}"
    if not re.fullmatch(r"(?:pr|issue)-[0-9]+", target):
        raise ValueError("review_attempt requires a positive PR or Issue target")
    repo_slug = repository.split("/", 1)[1]
    label = f"athena:{repo_slug}:{target}:{candidate[:7]}:{spec['axis']}:r{spec['round']}"
    criteria_fingerprint = fp(packet.get("criteria"))
    evidence_fingerprint = fp(packet.get("evidence"))
    review_id = "athena-" + fp({"label": label, "criteria": criteria_fingerprint, "evidence": evidence_fingerprint})[:16]
    if "display_label" in spec and spec["display_label"] != label:
        raise ValueError("review_attempt display_label is not deterministic")
    if "review_id" in spec and spec["review_id"] != review_id:
        raise ValueError("review_attempt review_id is not deterministic")
    if not observed_reviewer_id(reviewer_session_id):
        raise ValueError("review_attempt requires a native reviewer session ID")
    return {"review_id": review_id, "candidate_head": candidate, "axis": spec["axis"], "round": spec["round"], "reviewer_session_id": reviewer_session_id, "display_label": label}


def review_receipt_filename(attempt: dict[str, Any]) -> str:
    """Use readable dimensions in filenames; exact identity stays in the receipt."""
    if not isinstance(attempt, dict) or not re.fullmatch(r"[0-9a-f]{40}", str(attempt.get("candidate_head", ""))) or attempt.get("axis") not in REVIEW_AXES or isinstance(attempt.get("round"), bool) or not isinstance(attempt.get("round"), int) or attempt["round"] < 1:
        raise ValueError("review attempt is invalid")
    return f"athena-{attempt['candidate_head'][:7]}-{attempt['axis']}-r{attempt['round']}.yaml"


def review_receipt_path(directory: str | Path, attempt: dict[str, Any]) -> Path:
    target = Path(directory) / review_receipt_filename(attempt)
    if target.exists():
        raise ValueError(f"review receipt collision: {target.name}; increment round instead of overwriting")
    return target


def write_new(path: str | Path, value: dict[str, Any]) -> None:
    target = Path(path)
    if target.exists():
        raise ValueError("review receipt already exists; refusing overwrite")
    write(target, value, exclusive=True)


def valid_reviewer_attestation(value: Any, reviewer_session_id: str | None, review_route: str = "luna-max") -> bool:
    runtime = value.get("runtime") if isinstance(value, dict) else None
    expected = {"luna-max": ("luna-max", "gpt-5.6-luna", "max"), "astra-light": ("astra-light", "gpt-6-astra", "low")}.get(review_route)
    if expected is None:
        return False
    # Normal review output can only carry a host observation.  Trust is a
    # separate host-owned event attached after semantic review.
    return (
        isinstance(value, dict)
        and value.get("source") == "codex_app"
        and value.get("verification") == "host_observed_not_assessed"
        and not value.get("signature")
        and bool(value.get("host_id"))
        and value.get("thread_id") == reviewer_session_id
        and value.get("fresh_context") is True
        and value.get("read_only") is True
        and value.get("producer_transcript") is False
        and isinstance(runtime, dict)
        and runtime.get("profile") in {expected[0], "NOT_ASSESSED"}
        and runtime.get("model") == expected[1]
        and runtime.get("reasoning_effort") == expected[2]
        and isinstance(runtime.get("provider"), str)
        and (review_route == "luna-max" or (runtime.get("provider", "").strip() and runtime.get("provider", "").strip().upper() not in ATHENA_PROVIDER_INVALID))
    )


def validate_criteria_manifest(packet: dict[str, Any]) -> None:
    """Validate a caller-supplied locked manifest without owning its contents."""
    manifest = packet.get("criteria_manifest")
    if manifest is None:
        raise ValueError("review packet must supply criteria_manifest and criteria_revision")
    if not isinstance(manifest, list) or not manifest or any(
        not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip()
        for item in manifest
    ):
        raise ValueError("criteria_manifest must contain non-empty criterion records")
    manifest_ids = [item["id"] for item in manifest]
    packet_ids = [item.get("id") for item in packet.get("criteria", []) if isinstance(item, dict)]
    if len(set(manifest_ids)) != len(manifest_ids) or packet_ids != manifest_ids:
        raise ValueError("criteria must exactly match the supplied locked criteria_manifest")
    for locked, criterion in zip(manifest, packet.get("criteria", [])):
        if any(criterion.get(key) != value for key, value in locked.items() if key != "id") or any(key in criterion and key not in locked for key in ("requirement", "text", "current_requirement")):
            raise ValueError("criteria requirement text does not match the locked manifest")
    if not isinstance(packet.get("criteria_revision"), str) or not packet["criteria_revision"].strip():
        raise ValueError("criteria_manifest requires criteria_revision")
    if packet.get("criteria_manifest_fingerprint") != fp(manifest):
        raise ValueError("criteria_manifest_fingerprint does not match the supplied manifest")


def load(path: str) -> dict[str, Any]:
    import yaml
    return yaml.safe_load(Path(path).read_text()) or {}


def write(path: str, value: dict[str, Any], *, exclusive: bool = False) -> None:
    import yaml
    target = Path(path)
    if not target.is_absolute() or not target.parent.exists() or not target.parent.is_dir() or target.is_symlink() or (target.exists() and (not target.is_file() or target.stat().st_nlink > 1)):
        raise ValueError("review output path must be absolute, existing-parent, and non-symlink")
    current = target.parent
    while current != current.parent:
        if current.is_symlink() and not (sys.platform == "darwin" and current == Path("/var") and os.path.realpath(current) == "/private/var"):
            raise ValueError("review output path traverses a symlink")
        current = current.parent
    flags = os.O_WRONLY | os.O_CREAT | (os.O_EXCL if exclusive else os.O_TRUNC) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(os.path.realpath(target), flags, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(yaml.safe_dump(value, sort_keys=False))


def fp(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def convergence_status(attempts: list[dict[str, Any]]) -> str:
    """Stop a bounded review loop when the candidate and evidence stop moving."""
    if not isinstance(attempts, list) or any(not isinstance(item, dict) for item in attempts):
        raise ValueError("convergence history must be a list of mappings")
    if len(attempts) < 2:
        return "continue"
    previous, latest = attempts[-2:]
    same_head = previous.get("candidate_head") == latest.get("candidate_head")
    same_evidence = previous.get("evidence_fingerprint") == latest.get("evidence_fingerprint")
    same_root_cause = previous.get("root_cause") == latest.get("root_cause")
    if same_head and same_evidence and same_root_cause:
        return "oscillating"
    if same_head and same_evidence:
        return "no_progress"
    return "continue"


def finding_fp(item: dict[str, Any]) -> str:
    identity = [str(item.get(key, "")).strip().lower() for key in ("category", "file", "line", "criterion", "symbol", "location") if str(item.get(key, "")).strip()]
    text = "|".join(identity) if len(identity) >= 2 and any(str(item.get(key, "")).strip() for key in ("line", "symbol", "location")) else "|".join(identity + [re.sub(r"\s+", " ", str(item.get("summary", "")).strip().lower())])
    return hashlib.sha256(re.sub(r"\s+", " ", text).encode()).hexdigest()[:16]


def finding_priority(item: dict[str, Any]) -> tuple[int, int]:
    severity = str(item.get("severity", "minor")).lower()
    if severity not in FINDING_SEVERITY_PRIORITY:
        raise ValueError("finding severity is invalid")
    return (FINDING_EVIDENCE_PRIORITY[item["evidence_state"]], FINDING_SEVERITY_PRIORITY[severity])


def valid_supporting_documents(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, dict)
        and isinstance(item.get("path"), str)
        and isinstance(item.get("disposition"), str)
        and item["disposition"] in SUPPORTING_DOCUMENT_DISPOSITIONS
        and (item["disposition"] == "NOT_APPLICABLE" or bool(item["path"].strip()))
        and isinstance(item.get("reason"), str)
        and bool(item["reason"].strip())
        for item in value
    )


def supporting_documents_clear(value: Any) -> bool:
    return valid_supporting_documents(value) and all(item["disposition"] != "BLOCKED" for item in value)


def validate_result(result: dict[str, Any], packet: dict[str, Any], candidate: str) -> None:
    validate_criteria_manifest(packet)
    snapshot = result.get("snapshot") or {}
    if snapshot.get("criteria_revision") != packet.get("criteria_revision") or snapshot.get("criteria_manifest_fingerprint") != packet.get("criteria_manifest_fingerprint") or snapshot.get("review_route", "luna-max") != packet.get("review_route", "luna-max"):
        raise ValueError("review snapshot is not bound to the locked criteria manifest")
    expected_base = packet.get("base") or {}
    expected_candidate = packet.get("candidate") or {}
    expected_rubric = packet.get("rubric_ref", "athena-review:v1")
    expected_repo_binding = packet.get("repo_binding") or {}
    expected_attempt = review_attempt(packet, snapshot.get("reviewer_session_id"))
    packet_criteria = packet.get("criteria") or []
    expected_ids = [item.get("id") for item in packet_criteria if isinstance(item, dict)]
    axis = (result.get("review_attempt") or {}).get("axis")
    if axis not in REVIEW_AXES:
        raise ValueError("review result requires a valid review axis")
    findings = result.get("findings")
    if (
        result.get("version") != 1
        or result.get("stale") is not False
        or result.get("reviewability") != "reviewable"
        or not isinstance(packet.get("changed_files"), list)
        or not packet.get("changed_files")
        or not isinstance(packet.get("validation"), dict)
        or not packet.get("validation")
        or not isinstance(packet.get("evidence"), dict)
        or not packet.get("evidence")
        or not valid_supporting_documents(result.get("supporting_documents"))
        or result.get("supporting_documents") != packet.get("supporting_documents")
        or not re.fullmatch(r"[0-9a-f]{40}", str(candidate))
        or expected_candidate.get("head") != candidate
        or snapshot.get("candidate_head") != candidate
        or snapshot.get("base_ref") != expected_base.get("ref")
        or snapshot.get("base_head") != expected_base.get("head")
        or snapshot.get("criteria_fingerprint") != fp(packet.get("criteria"))
        or snapshot.get("rubric_ref") != expected_rubric
        or snapshot.get("authority_fingerprint") != fp(packet.get("authority"))
        or snapshot.get("workspace_fingerprint") != packet.get("workspace_fingerprint")
        or snapshot.get("evidence_fingerprint") != fp(packet.get("evidence"))
        or snapshot.get("validation_fingerprint") != fp(packet.get("validation"))
        or snapshot.get("supporting_documents_fingerprint") != fp(packet.get("supporting_documents"))
        or snapshot.get("repo_binding_fingerprint") != fp(expected_repo_binding)
        or snapshot.get("changed_files_fingerprint") != fp(sorted(packet.get("changed_files", [])))
        or result.get("review_attempt") != expected_attempt
        or snapshot.get("review_attempt") != expected_attempt
        or sorted(expected_candidate.get("changed_files", [])) != sorted(packet.get("changed_files", []))
        or not observed_reviewer_id(snapshot.get("reviewer_session_id"))
        or snapshot.get("reviewer_identity_source") != "host_observed_not_assessed"
        or not valid_reviewer_attestation(snapshot.get("reviewer_attestation"), snapshot.get("reviewer_session_id"), packet.get("review_route", "luna-max"))
        or snapshot.get("fresh_context") is not True
        or snapshot.get("read_only") is not True
        or any(not isinstance(item, dict) or not item.get("id") for item in packet_criteria)
        or len(expected_ids) != len(set(expected_ids))
    ):
        raise ValueError("stale or wrong candidate review")
    if result.get("recommendation") != "not_assessed":
        raise ValueError("review recommendation must remain not_assessed")
    if axis in {"work", "joint"}:
        if not isinstance(findings, list) or any(not isinstance(item, dict) or item.get("evidence_state") not in FINDING_EVIDENCE_STATES or str(item.get("severity", "minor")).lower() not in FINDING_SEVERITY_PRIORITY or item.get("fingerprint") != finding_fp(item) for item in findings):
            raise ValueError("work review findings are invalid")
        material = [item for item in findings if item.get("evidence_state") != "refuted" and str(item.get("severity", "minor")).lower() in {"critical", "blocker", "major", "material"}]
        verified = [item for item in material if item.get("evidence_state") == "verified"]
        expected_work = "fail" if verified else ("concerns" if material else "pass")
        if result.get("work_review", {}).get("status") not in {"pass", "concerns", "fail"} or result["work_review"]["status"] != expected_work or result.get("verified_material_findings") != [finding_fp(item) for item in verified]:
            raise ValueError("work review status is inconsistent with findings")
    if axis in {"goal", "joint"}:
        criteria = result.get("goal_review", {}).get("criteria") or []
        result_ids = [item.get("id") for item in criteria if isinstance(item, dict)]
        if not packet_criteria or result_ids != expected_ids or any(not isinstance(item, dict) or item.get("status") not in {"fulfilled", "partial", "unfulfilled", "not_assessed"} or not str(item.get("evidence", "")).strip() for item in criteria):
            raise ValueError("goal review criteria are incomplete")
        statuses = {item.get("status") for item in criteria}
        expected_goal = "insufficient_evidence" if "not_assessed" in statuses else ("complete" if statuses <= {"fulfilled"} else ("incomplete" if "unfulfilled" in statuses else "partial"))
        if result.get("goal_review", {}).get("status") not in {"complete", "partial", "incomplete", "insufficient_evidence"} or result["goal_review"]["status"] != expected_goal:
            raise ValueError("goal review status is inconsistent with criteria")


def normalize(packet: dict[str, Any], supplied: dict[str, Any], *, reviewer_session_id: str | None = None, reviewer_attestation: dict[str, Any] | None = None) -> dict[str, Any]:
    required = {"authority", "base", "candidate", "criteria", "criteria_manifest", "criteria_revision", "criteria_manifest_fingerprint", "changed_files", "validation", "evidence", "supporting_documents", "repo_binding", "workspace_fingerprint", "review_attempt"}
    missing = required - set(packet)
    if missing:
        raise ValueError(f"packet missing: {sorted(missing)}")
    validate_criteria_manifest(packet)
    exact_commit = re.compile(r"^[0-9a-f]{40}$")
    if not exact_commit.fullmatch(str(packet["candidate"].get("head", ""))) or not packet["base"].get("ref") or not exact_commit.fullmatch(str(packet["base"].get("head", ""))):
        raise ValueError("exact base and candidate are required")
    if not isinstance(packet["changed_files"], list) or not packet["changed_files"] or not isinstance(packet["validation"], dict) or not packet["validation"] or not isinstance(packet["evidence"], dict) or not packet["evidence"] or not isinstance(packet["repo_binding"], dict) or not packet["repo_binding"].get("root") or not packet["repo_binding"].get("worktree") or not isinstance(packet["workspace_fingerprint"], str) or not packet["workspace_fingerprint"] or not valid_supporting_documents(packet["supporting_documents"]):
        raise ValueError("review packet must include changed_files, validation, and evidence")
    if sorted(packet["candidate"].get("changed_files", [])) != sorted(packet["changed_files"]):
        raise ValueError("candidate changed_files do not match review packet")
    supplied_id = supplied.get("reviewer_session_id")
    if supplied_id and supplied_id != "NOT_ASSESSED":
        raise ValueError("reviewer result cannot author its own identity")
    review_route = packet.get("review_route", "luna-max")
    if review_route not in {"luna-max", "astra-light"}:
        raise ValueError("unsupported Athena review route")
    if supplied.get("fresh_context") is not True or supplied.get("read_only") is not True or supplied.get("producer_transcript") or not observed_reviewer_id(reviewer_session_id) or not valid_reviewer_attestation(reviewer_attestation, reviewer_session_id, review_route):
        raise ValueError("reviewer must provide host-observed, non-trusted evidence")
    attempt = review_attempt(packet, reviewer_session_id)
    findings_by_fp: dict[str, dict[str, Any]] = {}
    axis = packet["review_attempt"]["axis"]
    for item in supplied.get("findings", []) if axis in {"work", "joint"} else []:
        if not isinstance(item, dict) or item.get("evidence_state") not in FINDING_EVIDENCE_STATES:
            raise ValueError("finding evidence_state is invalid")
        item = dict(item); item["severity"] = str(item.get("severity", "minor")).lower(); finding_priority(item); item["fingerprint"] = finding_fp(item)
        current = findings_by_fp.get(item["fingerprint"])
        if current is None or finding_priority(item) > finding_priority(current):
            findings_by_fp[item["fingerprint"]] = item
    findings = list(findings_by_fp.values())
    material = [item for item in findings if item.get("evidence_state") != "refuted" and item.get("severity", "minor").lower() in {"critical", "blocker", "major", "material"}]
    verified = [item for item in material if item.get("evidence_state") == "verified"]
    work_status = "fail" if verified else ("concerns" if material else "pass")
    criteria = []
    goal_status = None
    if axis in {"goal", "joint"}:
        packet_criteria = packet["criteria"]
        adjudications = supplied.get("criteria_review")
        if not isinstance(packet_criteria, list) or not packet_criteria or any(not isinstance(item, dict) or not item.get("id") for item in packet_criteria) or len({item["id"] for item in packet_criteria}) != len(packet_criteria) or not isinstance(adjudications, list):
            raise ValueError("review must independently adjudicate every criterion")
        judgments = {item.get("id"): item for item in adjudications if isinstance(item, dict)}
        if set(judgments) != {item.get("id") for item in packet_criteria} or any(not item.get("status") or not str(item.get("evidence", "")).strip() for item in judgments.values()):
            raise ValueError("criterion adjudication is incomplete")
        criteria = [{**item, "status": judgments[item["id"]]["status"], "evidence": judgments[item["id"]]["evidence"]} for item in packet_criteria]
        statuses = {item.get("status") for item in criteria}
        if statuses - {"fulfilled", "partial", "unfulfilled", "not_assessed"}:
            raise ValueError("criterion adjudication contains an invalid status")
        if "not_assessed" in statuses:
            goal_status = "insufficient_evidence"
        elif statuses <= {"fulfilled"}:
            goal_status = "complete"
        elif "unfulfilled" in statuses:
            goal_status = "incomplete"
        elif "partial" in statuses:
            goal_status = "partial"
        else:
            goal_status = "incomplete"
    snapshot = {"candidate_head": packet["candidate"]["head"], "base_ref": packet["base"]["ref"], "base_head": packet["base"]["head"], "criteria_fingerprint": fp(packet["criteria"]), "rubric_ref": packet.get("rubric_ref", "athena-review:v1"), "authority_fingerprint": fp(packet["authority"]), "workspace_fingerprint": packet["workspace_fingerprint"], "evidence_fingerprint": fp(packet["evidence"]), "validation_fingerprint": fp(packet["validation"]), "supporting_documents_fingerprint": fp(packet["supporting_documents"]), "changed_files_fingerprint": fp(sorted(packet["changed_files"])), "repo_binding_fingerprint": fp(packet["repo_binding"]), "review_route": review_route, "review_attempt": attempt, "reviewer_session_id": reviewer_session_id, "reviewer_identity_source": "host_observed_not_assessed", "reviewer_attestation": reviewer_attestation, "fresh_context": True, "read_only": True}
    if "criteria_manifest" in packet:
        snapshot["criteria_revision"] = packet["criteria_revision"]
        snapshot["criteria_manifest_fingerprint"] = packet["criteria_manifest_fingerprint"]
    result = {"version": 1, "snapshot": snapshot, "review_attempt": attempt, "stale": False, "reviewability": "reviewable", "supporting_documents": packet["supporting_documents"], "limitations": [*supplied.get("limitations", []), "reviewer host trust is not assessed"] if snapshot["reviewer_identity_source"] == "host_observed_not_assessed" else supplied.get("limitations", []), "recommendation": "not_assessed"}
    if axis in {"work", "joint"}:
        result.update({"work_review": {"status": work_status, "coverage": supplied.get("work_coverage", "bounded")}, "findings": findings, "verified_material_findings": [item["fingerprint"] for item in verified]})
    if axis in {"goal", "joint"}:
        result["goal_review"] = {"status": goal_status, "criteria": criteria}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="command", required=True)
    norm = sub.add_parser("normalize"); norm.add_argument("--packet", required=True); norm.add_argument("--result", required=True); norm.add_argument("--reviewer-session-id", required=True); norm.add_argument("--reviewer-attestation", required=True)
    val = sub.add_parser("validate"); val.add_argument("--result", required=True); val.add_argument("--packet", required=True); val.add_argument("--candidate", required=True)
    args = parser.parse_args()
    try:
        if args.command == "normalize":
            write_new(args.result, normalize(load(args.packet), load(args.result), reviewer_session_id=args.reviewer_session_id, reviewer_attestation=load(args.reviewer_attestation))); print("PASS")
        else:
            result = load(args.result)
            validate_result(result, load(args.packet), args.candidate)
            print("PASS")
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
