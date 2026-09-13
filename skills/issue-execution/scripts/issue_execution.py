#!/usr/bin/env python3
"""Small, fail-closed Issue lifecycle and evidence helpers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

FORBIDDEN_RECEIPT_KEYS = {"ac_satisfied", "issue_complete", "review_passed", "accepted_head", "final_success"}
SEMANTIC_ROUTES = {"economy", "balanced", "strong", "strongest"}
LEGACY_ROUTE_MAP = {"low": "economy", "bounded": "balanced", "medium": "balanced", "high": "strong", "critical": "strongest"}
ROUTE_EFFORT_MAP = {"economy": "low", "balanced": "medium", "strong": "high", "strongest": "xhigh"}
REASONING_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
WORKER_AVAILABILITY_FAILURES = {"QUOTA_EXHAUSTED", "RATE_LIMITED", "RUNTIME_UNAVAILABLE", "PROVIDER_UNAVAILABLE"}
CAPACITY_STATES = {"AVAILABLE", "LOW", "EXHAUSTED", "RATE_LIMITED", "UNKNOWN"}
ERROR_CODES = {
    "ISSUE_AUTHORITY_INVALID", "STALE_BASE", "DIRTY_BASELINE_CONFLICT",
    "RUNTIME_UNAVAILABLE", "MODEL_ROUTE_UNAVAILABLE", "AUTH_REQUIRED",
    "CAPACITY_UNKNOWN", "CAPACITY_LOW", "QUOTA_EXHAUSTED", "RATE_LIMITED",
    "SESSION_INVALID", "SESSION_CONTEXT_MISMATCH", "CONTEXT_CONTRACT_UNVERIFIED",
    "REQUIRED_SKILL_UNAVAILABLE", "PERMISSION_NOT_ASSESSED", "PERMISSION_DENIED",
    "STRUCTURED_RESULT_INVALID", "EXECUTION_PROTOCOL_VIOLATION", "TIMED_OUT", "EXECUTION_FAILED",
    "MUTATION_SCOPE_VIOLATION", "GIT_RECONCILIATION_FAILED", "VALIDATION_FAILED",
    "PROVIDER_UNAVAILABLE",
    "REVIEW_NOT_REVIEWABLE", "REVIEW_INSUFFICIENT_EVIDENCE", "REVIEW_STALE",
    "PARENT_ACCEPTANCE_REQUIRED", "OSCILLATING", "BUDGET_EXHAUSTED",
}
INVALID_REVIEWER_IDS = {"", "NOT_ASSESSED", "UNKNOWN", "UNAVAILABLE", "NONE", "NULL"}
NATIVE_REVIEWER_ID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
MAX_TASK_EXECUTIONS = 8
HISTORY_NOISE_RE = re.compile(r"^(?:fix|test|wip|retry|debug|tmp|tweak|try)(?:\b|[:( -])", re.IGNORECASE)
HISTORY_BOUNDARY_RE = re.compile(r"\b(?:review|repair|semantic|integrat(?:e|ion)|candidate|authority|policy|contract|reconcile|qualification|checkpoint)\b", re.IGNORECASE)


def load_document(path: str | Path) -> Any:
    import yaml
    value = yaml.safe_load(Path(path).read_text())
    if value is None:
        raise ValueError(f"empty document: {path}")
    return value


def _allowed_platform_alias(path: Path) -> bool:
    return sys.platform == "darwin" and path == Path("/var") and canonical(path) == canonical("/private/var")


def safe_write_path(path: str | Path) -> Path:
    target = Path(path)
    if not target.is_absolute():
        raise ValueError("write path must be absolute")
    current = target.parent
    while current != current.parent:
        if current.is_symlink() and not _allowed_platform_alias(current):
            raise ValueError("write path traverses a symlink")
        current = current.parent
    if target.is_symlink() or (target.exists() and (not target.is_file() or target.stat().st_nlink > 1)) or not target.parent.exists() or not target.parent.is_dir():
        raise ValueError("write path is not a safe existing target")
    return Path(canonical(target))


def ensure_safe_directory(path: str | Path) -> Path:
    target = Path(path)
    if not target.is_absolute():
        raise ValueError("state directory must be absolute")
    missing: list[Path] = []
    current = target
    while not current.exists():
        missing.append(current)
        current = current.parent
    if not current.is_dir() or (current.is_symlink() and not _allowed_platform_alias(current)):
        raise ValueError("state directory traverses an unsafe path")
    for item in reversed(missing):
        item.mkdir()
    return Path(canonical(target))


def validate_state_dir(path: str | Path, repo_root: str, worktree_root: str | None = None) -> Path:
    target = Path(path)
    if not target.is_absolute():
        raise ValueError("state directory must be absolute")
    current = target
    while True:
        if current.is_symlink() and not _allowed_platform_alias(current):
            raise ValueError("state directory traverses a symlink")
        if current == current.parent:
            break
        current = current.parent
    resolved = Path(canonical(target))
    worktree = Path(canonical(worktree_root or repo_root))
    expected_root = worktree / ".agents" / "sessions"
    if resolved != expected_root and expected_root not in resolved.parents:
        raise ValueError("state directory must be under <worktree>/.agents/sessions")
    return resolved


def dump_document(path: str | Path, value: Any) -> None:
    import yaml
    target = safe_write_path(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(target, flags, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(yaml.safe_dump(value, sort_keys=False))


def canonical(path: str | Path) -> str:
    return os.path.realpath(os.path.abspath(os.fspath(path)))


def is_git_metadata_path(path: str | Path) -> bool:
    return ".git" in Path(path).parts


def git_worktree_identity(repo: str) -> dict[str, str]:
    root = canonical(repo)
    if not Path(root).is_dir():
        raise ValueError("repository root is not a directory")
    values: dict[str, str] = {}
    for key, args in {
        "top_level": ("--show-toplevel",),
        "git_dir": ("--git-dir",),
        "git_common_dir": ("--git-common-dir",),
        "inside_worktree": ("--is-inside-work-tree",),
    }.items():
        result = subprocess.run(["git", "-C", root, "rev-parse", *args], text=True, capture_output=True)
        if result.returncode:
            raise ValueError("repository root is not a Git worktree")
        value = result.stdout.strip()
        if key == "inside_worktree":
            values[key] = value
        else:
            path = Path(value)
            values[key] = canonical(path if path.is_absolute() else Path(root) / path)
    if values["inside_worktree"] != "true" or values["top_level"] != root:
        raise ValueError("request repository root is not the actual Git worktree root")
    return {key: values[key] for key in ("top_level", "git_dir", "git_common_dir")}


def repository_binding(repo_root: str, worktree: str | None = None) -> dict[str, Any]:
    worktree = worktree or repo_root
    repository_identity = git_worktree_identity(repo_root)
    worktree_identity = git_worktree_identity(worktree)
    if repository_identity["git_common_dir"] != worktree_identity["git_common_dir"]:
        raise ValueError("repository and worktree belong to different Git repositories")
    return {
        "root": canonical(repo_root),
        "worktree": canonical(worktree),
        "repository_identity": repository_identity,
        "worktree_identity": worktree_identity,
    }


def effective_context(repo_root: str, cwd: str, required_skills: list[str] | None = None) -> dict[str, Any]:
    """Bind the applicable instruction chain and local skill roots to CWD."""
    root = Path(canonical(repo_root))
    current = Path(canonical(cwd))
    if current != root and root not in current.parents:
        raise ValueError("context cwd escapes repository root")
    relative_parts = current.relative_to(root).parts
    ancestors = [root.joinpath(*relative_parts[:index]) for index in range(len(relative_parts) + 1)]
    instruction_paths: list[Path] = []
    for directory in ancestors:
        override = directory / "AGENTS.override.md"
        standard = directory / "AGENTS.md"
        if override.is_file():
            instruction_paths.append(override)
        elif standard.is_file():
            instruction_paths.append(standard)
    skills = list(required_skills or [])
    skill_paths: list[Path] = []
    missing_skills: list[str] = []
    for name in skills:
        if not isinstance(name, str) or not name.strip():
            continue
        if Path(name).is_absolute() or ".." in Path(name).parts:
            raise ValueError("CONTEXT_CONTRACT_UNVERIFIED: required skill path is unsafe")
        found = False
        for base in (root / "skills", root / ".agents" / "skills"):
            candidate = base / name / "SKILL.md"
            if candidate.is_file():
                skill_paths.append(candidate)
                found = True
        if not found:
            missing_skills.append(name)
    if missing_skills:
        raise ValueError(f"CONTEXT_CONTRACT_UNVERIFIED: required skills unavailable: {sorted(set(missing_skills))}")
    records: list[dict[str, str]] = []
    for path in [*instruction_paths, *skill_paths]:
        records.append({"path": str(path.relative_to(root)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    binding = {"cwd": str(current), "instruction_paths": [item["path"] for item in records[:len(instruction_paths)]], "skill_paths": [item["path"] for item in records[len(instruction_paths):]], "records": records}
    binding["fingerprint"] = digest(binding)
    return binding


def observed_reviewer_id(value: Any) -> bool:
    return isinstance(value, str) and value.strip().upper() not in INVALID_REVIEWER_IDS and NATIVE_REVIEWER_ID.fullmatch(value.strip()) is not None


def valid_reviewer_attestation(value: Any, reviewer_session_id: str | None, review_route: str = "luna-max") -> bool:
    runtime = value.get("runtime") if isinstance(value, dict) else None
    expected = {"luna-max": ("luna-max", "gpt-5.6-luna", "max"), "astra-light": ("astra-light", "gpt-6-astra", "low")}.get(review_route)
    if expected is None:
        return False
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
        and (review_route == "luna-max" or (runtime.get("provider", "").strip() and runtime.get("provider", "").strip().upper() not in INVALID_REVIEWER_IDS))
    )


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


NON_RESUMABLE_NATIVE_SESSION_IDS = {"NOT_ASSESSED", "UNKNOWN", "NONE", "NULL", "UNAVAILABLE"}


def valid_observed_native_session_id(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip().upper() not in NON_RESUMABLE_NATIVE_SESSION_IDS


def valid_observed_provider(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip().upper() not in INVALID_REVIEWER_IDS


def validate_baseline_record(value: dict[str, Any]) -> None:
    required = {"repo_root", "head", "branch", "status", "status_records", "workspace_manifest", "workspace_files", "tracked_files", "excluded_paths", "workspace_fingerprint", "fingerprint"}
    if not isinstance(value, dict) or not required <= value.keys() or not isinstance(value.get("fingerprint"), str):
        raise ValueError("trusted baseline is missing its fingerprint")
    if not all(isinstance(value.get(key), str) for key in ("repo_root", "head", "branch", "workspace_fingerprint")) or not isinstance(value["status"], list) or not isinstance(value["status_records"], list) or not isinstance(value["workspace_manifest"], dict) or not isinstance(value["workspace_files"], list) or not isinstance(value["tracked_files"], list) or not isinstance(value["excluded_paths"], list) or any(not isinstance(item, dict) for item in value["status_records"]) or any(not isinstance(item, str) for item in value["workspace_files"] + value["tracked_files"] + value["excluded_paths"]):
        raise ValueError("trusted baseline schema is invalid")
    unsigned = {key: item for key, item in value.items() if key != "fingerprint"}
    if value["fingerprint"] != digest(unsigned):
        raise ValueError("trusted baseline fingerprint does not match its contents")


def path_matches_allowance(path: str, allowed: list[str], repo_root: str | None = None) -> bool:
    for item in allowed:
        if Path(item) == Path("."):
            continue
        normalized = Path(item).as_posix().rstrip("/")
        if path == normalized:
            return True
        explicit_directory = item.endswith("/") or (repo_root is not None and (Path(repo_root) / normalized).is_dir())
        if explicit_directory and normalized in {"", "."}:
            return True
        if explicit_directory and path.startswith(normalized + "/"):
            return True
    return False


def filesystem_payload(target: Path) -> bytes:
    """Hash regular content, link targets, or special-file identity safely."""
    mode = target.lstat().st_mode
    if stat.S_ISLNK(mode):
        return b"symlink\0" + os.readlink(target).encode()
    if stat.S_ISREG(mode):
        return target.read_bytes()
    return b"special\0" + str(stat.S_IFMT(mode)).encode()


def workspace_fingerprint(repo: str, excluded: list[str] | None = None) -> str:
    root = Path(canonical(repo))
    excluded_roots = [Path(canonical(item)) for item in (excluded or [])]
    files: dict[str, str] = {"@root": hashlib.sha256(str(root.stat().st_mode).encode()).hexdigest()}
    for directory, names, entries in os.walk(root):
        names[:] = [name for name in names if name != ".git"]
        directory_path = Path(directory)
        if any(directory_path == item or item in directory_path.parents for item in excluded_roots):
            names[:] = []
            continue
        for name in names:
            target = directory_path / name
            if any(target == item or item in target.parents for item in excluded_roots):
                continue
            relative = target.relative_to(root).as_posix()
            if target.is_symlink():
                files[f"@entry/{relative}"] = hashlib.sha256(str(target.lstat().st_mode).encode() + b"\0" + os.readlink(target).encode()).hexdigest()
            else:
                files[f"@dir/{relative}"] = hashlib.sha256(str(target.stat().st_mode).encode()).hexdigest()
        for name in entries:
            if name == ".git":
                continue
            target = Path(directory) / name
            if any(target == item or item in target.parents for item in excluded_roots):
                continue
            relative = target.relative_to(root).as_posix()
            mode = target.lstat().st_mode
            files[relative] = hashlib.sha256(str(mode).encode() + b"\0" + filesystem_payload(target)).hexdigest()
    return digest(files)


def workspace_manifest(repo: str, excluded: list[str] | None = None) -> dict[str, str]:
    root = Path(canonical(repo))
    excluded_roots = [Path(canonical(item)) for item in (excluded or [])]
    manifest: dict[str, str] = {}
    for directory, names, entries in os.walk(root):
        names[:] = [name for name in names if name != ".git"]
        directory_path = Path(directory)
        if any(directory_path == item or item in directory_path.parents for item in excluded_roots):
            names[:] = []
            continue
        kept = []
        for name in names:
            target = directory_path / name
            if any(target == item or item in target.parents for item in excluded_roots):
                continue
            relative = target.relative_to(root).as_posix()
            if target.is_symlink():
                manifest[relative] = hashlib.sha256(b"symlink\0" + str(target.lstat().st_mode).encode() + b"\0" + os.readlink(target).encode()).hexdigest()
            else:
                manifest[relative] = hashlib.sha256(b"dir\0" + str(target.stat().st_mode).encode()).hexdigest()
                kept.append(name)
        names[:] = kept
        for name in entries:
            if name == ".git":
                continue
            target = directory_path / name
            if any(target == item or item in target.parents for item in excluded_roots):
                continue
            relative = target.relative_to(root).as_posix()
            mode = target.lstat().st_mode
            content = filesystem_payload(target)
            manifest[relative] = hashlib.sha256(str(mode).encode() + b"\0" + content).hexdigest()
    return manifest


def git(repo: str, *args: str) -> str:
    result = subprocess.run(["git", "-C", repo, *args], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git failed: {args}")
    return result.stdout.strip()


def git_status_records(repo: str) -> list[dict[str, str]]:
    result = subprocess.run(["git", "-C", repo, "status", "--porcelain=v1", "-z"], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "cannot inspect Git status")
    parts = [part for part in result.stdout.split("\0") if part]
    records: list[dict[str, str]] = []
    index = 0
    while index < len(parts):
        entry = parts[index]
        index += 1
        if len(entry) < 4 or entry[2] != " ":
            raise ValueError("Git status record is malformed")
        record = {"xy": entry[:2], "path": entry[3:]}
        if entry[:2][0] in "RC" or entry[:2][1] in "RC":
            if index >= len(parts):
                raise ValueError("Git rename status record is incomplete")
            record["original_path"] = parts[index]
            index += 1
        records.append(record)
    return records


def hygiene_snapshot(repo: str, scratch_paths: list[str] | None = None) -> dict[str, Any]:
    """Check Git status and explicitly named external scratch surfaces."""
    status_records = git_status_records(repo)
    existing = []
    for value in scratch_paths or []:
        target = Path(value)
        if target.exists() or target.is_symlink():
            existing.append(canonical(target))
    return {"git_clean": not status_records, "git_status_records": status_records, "scratch_clean": not existing, "existing_scratch_paths": sorted(existing), "clean": not status_records and not existing}


def status_paths(records: list[dict[str, str]]) -> list[str]:
    return [path for record in records for path in (record.get("path", ""), record.get("original_path", "")) if path]


def render_status_records(records: list[dict[str, str]]) -> list[str]:
    return [f"{record['xy']} {record.get('original_path', '')} -> {record['path']}" if record.get("original_path") else f"{record['xy']} {record['path']}" for record in records]


def baseline(repo: str, excluded: list[str] | None = None) -> dict[str, Any]:
    records = git_status_records(repo)
    manifest = workspace_manifest(repo, excluded)
    root = Path(canonical(repo))
    workspace_files = [path for path in manifest if (root / path).is_file() or (root / path).is_symlink()]
    value = {"repo_root": canonical(repo), "head": git(repo, "rev-parse", "HEAD"), "branch": git(repo, "branch", "--show-current"), "status": render_status_records(records), "status_records": records, "workspace_manifest": manifest, "workspace_files": sorted(workspace_files), "tracked_files": git(repo, "ls-files").splitlines(), "excluded_paths": sorted(canonical(item) for item in (excluded or [])), "workspace_fingerprint": workspace_fingerprint(repo, excluded)}
    value["fingerprint"] = digest(value)
    return value


def _walk_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return {str(key) for key in value} | set().union(*(_walk_keys(child) for child in value.values()))
    if isinstance(value, list):
        return set().union(*(_walk_keys(child) for child in value)) if value else set()
    return set()


def requested_semantic_route(request: dict[str, Any]) -> str:
    route = request.get("route_requirements") or {}
    value = route.get("semantic_route") or LEGACY_ROUTE_MAP.get(route.get("semantic_complexity"), route.get("semantic_complexity"))
    if value not in SEMANTIC_ROUTES:
        raise ValueError("MODEL_ROUTE_UNAVAILABLE: semantic route must be economy, balanced, strong, or strongest")
    return value


def requested_reasoning_effort(request: dict[str, Any]) -> str:
    explicit = (request.get("route_requirements") or {}).get("requested_effort")
    if explicit is not None:
        if explicit not in REASONING_EFFORTS:
            raise ValueError("MODEL_ROUTE_UNAVAILABLE: unsupported reasoning effort")
        return explicit
    return ROUTE_EFFORT_MAP[requested_semantic_route(request)]


def select_worker(error_code: str | None = None) -> dict[str, Any]:
    """Return the stage-1 AGY route; the parent owns any stage-2 switch."""
    reason = str(error_code or "").strip().upper()
    if reason in WORKER_AVAILABILITY_FAILURES:
        return {"requested_worker": "agy", "actual_worker": "agy", "fallback_triggered": True, "fallback_reason": reason}
    return {"requested_worker": "agy", "actual_worker": "agy", "fallback_triggered": False, "fallback_reason": None}


def validate_worker_route(value: Any) -> None:
    required = {"requested_worker", "actual_worker", "fallback_triggered", "fallback_reason"}
    if not isinstance(value, dict) or not required <= value.keys() or value.get("requested_worker") != "agy" or value.get("actual_worker") not in {"agy", "prometheus"} or not isinstance(value.get("fallback_triggered"), bool):
        raise ValueError("worker_route is invalid")
    reason = value.get("fallback_reason")
    if value["fallback_triggered"]:
        if value["actual_worker"] not in {"agy", "prometheus"} or reason not in WORKER_AVAILABILITY_FAILURES:
            raise ValueError("worker_route fallback must be availability-driven")
    elif value["actual_worker"] != "agy" or reason is not None:
        raise ValueError("worker_route without fallback must remain on AGY")


def validate_native_prometheus_result(request: dict[str, Any], receipt: dict[str, Any]) -> None:
    """Validate the parent-returned stage-2 native Prometheus contract."""
    result = receipt.get("native_prometheus_result")
    route = receipt.get("worker_route")
    if not isinstance(result, dict) or not isinstance(route, dict) or route.get("actual_worker") != "prometheus":
        raise ValueError("native Prometheus fallback result is missing")
    required = {"parent_request_id", "attempt", "fallback_reason", "result_status", "changed_paths", "validation", "authority", "repo", "agy_failure"}
    if not required <= result.keys():
        raise ValueError("native Prometheus fallback result is incomplete")
    if result["parent_request_id"] != request["request_id"] or not isinstance(result["attempt"], int) or result["attempt"] < 1:
        raise ValueError("native Prometheus fallback result is not bound to the parent request")
    if result["fallback_reason"] != route.get("fallback_reason") or result["fallback_reason"] not in WORKER_AVAILABILITY_FAILURES:
        raise ValueError("native Prometheus fallback reason is not bound to the AGY failure")
    agy_failure = result["agy_failure"]
    if not isinstance(agy_failure, dict) or agy_failure.get("request_id") != request["request_id"] or agy_failure.get("actual_worker") != "agy" or agy_failure.get("error_code") != result["fallback_reason"] or agy_failure.get("status") not in {"FAILED", "TIMED_OUT"}:
        raise ValueError("native Prometheus fallback lacks the observed AGY availability failure")
    if result["result_status"] != (receipt.get("execution") or {}).get("status") or result["result_status"] not in {"SUCCESS", "FAILED", "TIMED_OUT"}:
        raise ValueError("native Prometheus fallback result status is not bound to the receipt")
    authority = result["authority"]
    expected_authority = request.get("authority") or {}
    if not isinstance(authority, dict) or authority.get("repository") != expected_authority.get("repository") or authority.get("issue") != expected_authority.get("issue") or authority.get("task") != expected_authority.get("task"):
        raise ValueError("native Prometheus fallback authority mismatch")
    repo = result["repo"]
    expected_repo = request.get("repo") or {}
    if not isinstance(repo, dict) or any(not isinstance(repo.get(key), str) or not repo[key].strip() for key in ("root", "cwd", "worktree")) or any(canonical(repo[key]) != canonical(expected_repo.get(key, "")) for key in ("root", "cwd", "worktree")):
        raise ValueError("native Prometheus fallback repository binding mismatch")
    changed_paths = result["changed_paths"]
    if not isinstance(changed_paths, list) or any(not isinstance(path, str) or os.path.isabs(path) or ".." in Path(path).parts or is_git_metadata_path(path) for path in changed_paths):
        raise ValueError("native Prometheus changed_paths are invalid")
    allowed = (request.get("scope") or {}).get("allowed_paths") or []
    worktree = (request.get("repo") or {}).get("worktree")
    if any(not path_matches_allowance(path, allowed, worktree) for path in changed_paths):
        raise ValueError("native Prometheus changed_paths exceed the parent allowed scope")
    if not isinstance(result["validation"], dict) or not result["validation"]:
        raise ValueError("native Prometheus fallback must return observed validation")


def validate_capacity(capacity: Any) -> None:
    if not isinstance(capacity, dict) or capacity.get("state") not in CAPACITY_STATES or not isinstance(capacity.get("source"), str) or not capacity["source"].strip():
        raise ValueError("receipt capacity observation is invalid")
    if capacity["state"] != "UNKNOWN" and capacity["source"].strip().lower() in {"none", "not_assessed", "unknown"}:
        raise ValueError("non-UNKNOWN capacity requires an observed source")


def validate_request(request: dict[str, Any]) -> None:
    required = {"version", "request_id", "authority", "lane", "repo", "scope", "session", "permission_policy", "return_contract", "route_requirements", "expected_context", "harness", "command", "outputs"}
    missing = required - set(request)
    if missing:
        raise ValueError(f"request missing fields: {sorted(missing)}")
    if request["version"] != 1 or not request["request_id"]:
        raise ValueError("unsupported request version or empty request_id")
    if request["lane"] not in {"execute", "repair"} or request["return_contract"] != "normalized-runtime-receipt-v1":
        raise ValueError("unsupported lane or return_contract")
    route = request["route_requirements"]
    if not isinstance(route, dict) or not {"semantic_complexity", "mutation_risk", "context_burden", "validation_strength", "latency_preference", "independence_required"} <= route.keys():
        raise ValueError("route_requirements are incomplete")
    requested_semantic_route(request)
    requested_profile = route.get("requested_profile") or route.get("profile")
    if requested_profile is not None and (not isinstance(requested_profile, str) or not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_-]{0,255}", requested_profile)):
        raise ValueError("MODEL_ROUTE_UNAVAILABLE: profile must be a valid AGY profile name")
    expected_context = request["expected_context"]
    if not isinstance(expected_context, dict) or not isinstance(expected_context.get("required_skills"), list) or not expected_context.get("instruction_fingerprint_expectation") or not re.fullmatch(r"[0-9a-f]{64}", str(expected_context.get("effective_context_fingerprint_expectation", ""))):
        raise ValueError("expected_context is incomplete")
    if "athena-review" in expected_context["required_skills"]:
        raise ValueError("MODEL_ROUTE_UNAVAILABLE: Athena review runs as a native parent sidecar, not through harness-worker")
    authority = request["authority"]
    if not isinstance(authority, dict) or not authority.get("repository") or not isinstance(authority.get("issue"), int) or authority["issue"] <= 0:
        raise ValueError("request authority must identify a real positive Issue")
    repo = request["repo"]
    if not isinstance(repo, dict):
        raise ValueError("request repo must be a mapping")
    for key in ("root", "cwd", "worktree"):
        if not isinstance(repo.get(key), str) or not repo[key]:
            raise ValueError(f"request repo missing {key}")
        if any(char in repo[key] for char in ('"', "\\", "\n", "\r", "\x00")):
            raise ValueError(f"request repo {key} contains unsafe sandbox syntax")
    root, cwd = canonical(repo["root"]), canonical(repo["cwd"])
    worktree = canonical(repo["worktree"])
    if not (cwd == worktree or cwd.startswith(worktree + os.sep)):
        raise ValueError("request cwd escapes worktree")
    if not Path(cwd).is_dir() or not Path(worktree).is_dir():
        raise ValueError("request cwd/worktree must identify directories")
    repository_identity = git_worktree_identity(root)
    worktree_identity = git_worktree_identity(worktree)
    if worktree_identity["git_common_dir"] != repository_identity["git_common_dir"]:
        raise ValueError("request worktree belongs to a different repository")
    if request["permission_policy"] not in {"read-only", "bounded-write"}:
        raise ValueError("unsupported permission policy")
    if request["harness"] not in {"agy", "fake"}:
        raise ValueError("unsupported harness")
    command = request["command"]
    if not isinstance(command, list) or not command or any(not isinstance(item, str) for item in command):
        raise ValueError("request command must be a non-empty argv list")
    if request["harness"] == "agy" and (not command or Path(command[0]).name != request["harness"]):
        raise ValueError("RUNTIME_UNAVAILABLE: native terminal command does not match the requested lane")
    outputs = request["outputs"]
    if not isinstance(outputs, dict) or not isinstance(outputs.get("registry"), str) or not isinstance(outputs.get("receipt"), str):
        raise ValueError("request outputs must declare registry and receipt paths")
    scope = request["scope"]
    if not isinstance(scope, dict) or not scope.get("mutation_boundary"):
        raise ValueError("request scope must declare mutation_boundary")
    allowed = scope.get("allowed_paths") or []
    if request["permission_policy"] == "bounded-write" and not allowed:
        raise ValueError("bounded-write request must declare allowed_paths")
    if not isinstance(request.get("session"), dict) or request["session"].get("policy") not in {"fresh", "resume", "resume_or_start", "rebind"}:
        raise ValueError("unsupported session policy")
    for path in allowed:
        if not isinstance(path, str) or os.path.isabs(path) or Path(path) == Path(".") or ".." in Path(path).parts:
            raise ValueError("scope allowed_paths must stay relative to repo root")
        if is_git_metadata_path(path):
            raise ValueError("scope allowed_paths cannot include .git metadata")
        if any(char in path for char in ('"', "\\", "\n", "\r", "\x00")):
            raise ValueError("scope allowed_paths contain unsafe sandbox syntax")


def validate_receipt(request: dict[str, Any], receipt: dict[str, Any]) -> None:
    validate_request(request)
    if not isinstance(receipt, dict):
        raise ValueError("receipt must be a mapping")
    if _walk_keys(receipt) & FORBIDDEN_RECEIPT_KEYS:
        raise ValueError("runtime receipt contains workflow/acceptance claims")
    if receipt.get("version") != 1 or receipt.get("request_id") != request["request_id"]:
        raise ValueError("receipt version or request_id mismatch")
    runtime, execution = receipt.get("runtime", {}), receipt.get("execution", {})
    context, usage, capacity = receipt.get("context", {}), receipt.get("usage", {}), receipt.get("capacity", {})
    if any(not isinstance(section, dict) for section in (runtime, execution, context, usage, capacity)):
        raise ValueError("receipt sections must be mappings")
    required_runtime = {"harness", "executor_provenance", "requested_route", "actual_route", "requested_profile", "resolved_profile", "provider", "actual_model", "actual_effort", "native_session_id", "session_state"}
    required_execution = {"repo_root", "cwd", "worktree", "permission_observation", "status", "exit_code", "duration_ms"}
    required_context = {"instruction_fingerprint", "skill_observation", "effective_context"}
    required_usage = {"input_tokens", "cache_read_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens", "latency_ms"}
    if not required_runtime <= runtime.keys() or not required_execution <= execution.keys() or not required_context <= context.keys() or not required_usage <= usage.keys() or not isinstance(receipt.get("limitations"), list):
        raise ValueError("receipt is missing required runtime observations")
    if not isinstance(context.get("effective_context"), dict) or not context["effective_context"].get("fingerprint"):
        raise ValueError("receipt must bind the effective instruction and skill context")
    expected_context = request["expected_context"]
    if context["instruction_fingerprint"] not in {None, "NOT_ASSESSED"} and context["instruction_fingerprint"] != expected_context["instruction_fingerprint_expectation"]:
        raise ValueError("receipt instruction context does not match the request")
    if context["effective_context"]["fingerprint"] != expected_context["effective_context_fingerprint_expectation"]:
        raise ValueError("receipt effective context does not match the request")
    if any(runtime.get(key) is None or (isinstance(runtime.get(key), str) and not runtime[key].strip()) for key in required_runtime):
        raise ValueError("receipt runtime observations cannot be null or empty")
    session_states = {"fresh": {"fresh"}, "resume": {"resumed"}, "resume_or_start": {"fresh", "resumed"}, "rebind": {"fresh", "resumed", "rebound"}}
    if runtime.get("session_state") not in session_states[request["session"]["policy"]]:
        raise ValueError("receipt session_state contradicts the requested session policy")
    permission_observation = execution.get("permission_observation")
    if permission_observation not in {"not_assessed", "read-only", "bounded-write"}:
        raise ValueError("receipt permission_observation is invalid")
    if permission_observation != "not_assessed" and permission_observation != request["permission_policy"]:
        raise ValueError("receipt permission_observation contradicts the requested permission policy")
    validate_capacity(capacity)
    if not runtime.get("harness") or not runtime.get("native_session_id") or runtime.get("requested_route") != requested_semantic_route(request):
        raise ValueError("receipt must expose route/model/effort observations and exact native_session_id")
    if execution.get("status") == "SUCCESS" and request["harness"] == "fake" and not valid_observed_native_session_id(runtime.get("native_session_id")):
        raise ValueError("successful receipt must expose a resumable native_session_id")
    worker_route = receipt.get("worker_route")
    if request["harness"] == "agy" and not isinstance(worker_route, dict):
        raise ValueError("AGY receipt must record worker_route")
    if worker_route is not None:
        validate_worker_route(worker_route)
        if request["harness"] == "agy" and runtime.get("harness") == "agy" and worker_route != select_worker(execution.get("error_code")):
            raise ValueError("AGY worker_route is not bound to the observed execution error")
    fallback_required = receipt.get("fallback_required")
    if worker_route is not None and worker_route["actual_worker"] == "prometheus":
        if fallback_required is not None:
            raise ValueError("stage-2 Prometheus result cannot retain fallback_required")
        validate_native_prometheus_result(request, receipt)
    elif worker_route is not None and worker_route["fallback_triggered"]:
        if fallback_required != "prometheus":
            raise ValueError("stage-1 AGY availability failure must require Prometheus")
        if receipt.get("native_prometheus_result") is not None:
            raise ValueError("stage-1 AGY receipt cannot claim a Prometheus result")
    elif fallback_required is not None:
        raise ValueError("fallback_required contradicts worker_route")
    provenance = runtime.get("executor_provenance")
    fallback_valid = request["harness"] == "agy" and isinstance(worker_route, dict) and worker_route.get("actual_worker") == "prometheus" and runtime.get("harness") == "native-terminal"
    actual_harness = runtime.get("harness")
    expected_kind = "test-harness" if actual_harness == "fake" else "native-terminal"
    if (runtime.get("harness") != request["harness"] and not fallback_valid) or not isinstance(provenance, dict) or provenance.get("kind") != expected_kind or not provenance.get("executable"):
        raise ValueError("receipt must expose executor provenance")
    if fallback_valid and (provenance.get("lane") != "prometheus" or provenance.get("kind") != "native-terminal"):
        raise ValueError("native Prometheus fallback provenance is invalid")
    if canonical(execution.get("repo_root", "")) != canonical(request["repo"]["root"]):
        raise ValueError("receipt repo_root mismatch")
    if canonical(execution.get("cwd", "")) != canonical(request["repo"]["cwd"]):
        raise ValueError("receipt cwd mismatch")
    if canonical(execution.get("worktree", "")) != canonical(request["repo"]["worktree"]):
        raise ValueError("receipt worktree mismatch")
    if not isinstance(execution.get("exit_code"), int):
        raise ValueError("receipt must expose integer exit_code")
    if execution.get("status") == "SUCCESS" and execution.get("exit_code") != 0:
        raise ValueError("successful receipts require exit_code 0")
    if execution.get("status") != "SUCCESS" and execution.get("exit_code") == 0 and execution.get("error_code") not in {"AUTH_REQUIRED", "QUOTA_EXHAUSTED", "RATE_LIMITED", "RUNTIME_UNAVAILABLE", "PROVIDER_UNAVAILABLE", "PERMISSION_DENIED", "SESSION_INVALID", "MODEL_ROUTE_UNAVAILABLE", "EXECUTION_PROTOCOL_VIOLATION", "EXECUTION_FAILED"}:
        raise ValueError("provider-level failures with exit_code 0 require a recognized error_code")
    if execution.get("status") not in {"SUCCESS", "FAILED", "TIMED_OUT"}:
        raise ValueError("invalid normalized execution status")
    error_code = execution.get("error_code")
    if execution.get("status") == "SUCCESS":
        if error_code is not None:
            raise ValueError("successful receipt cannot carry an error_code")
    elif error_code not in ERROR_CODES:
        raise ValueError("failed receipt must carry one recognized error_code")
    status_error = {"TIMED_OUT": "TIMED_OUT"}
    if execution.get("status") in status_error and error_code != status_error[execution["status"]]:
        raise ValueError("normalized status and error_code disagree")


def changed_files(repo: str, base: str) -> list[str]:
    names = git(repo, "diff", "--name-only", f"{base}..HEAD").splitlines()
    names.extend(git(repo, "diff", "--name-only").splitlines())
    names.extend(git(repo, "diff", "--cached", "--name-only").splitlines())
    names.extend(git(repo, "ls-files", "--others", "--exclude-standard").splitlines())
    return sorted(set(names))


def committed_changed_files(repo: str, base: str, candidate: str) -> list[str]:
    return sorted(set(git(repo, "diff", "--name-only", f"{base}..{candidate}").splitlines()))


def is_ancestor(repo: str, base: str, candidate: str) -> bool:
    return subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", base, candidate], capture_output=True).returncode == 0


def classify_commit_history(repo: str, base: str, candidate: str) -> dict[str, Any]:
    """Classify checkpoint history without treating Git as workflow state."""
    raw = git(repo, "log", "--reverse", "--format=%H\t%s", "--name-only", "--no-renames", f"{base}..{candidate}")
    commits: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in raw.splitlines():
        match = re.fullmatch(r"([0-9a-f]{40})\t(.*)", line)
        if match:
            current = {"sha": match.group(1), "subject": match.group(2), "paths": []}
            commits.append(current)
        elif current is not None and line.strip():
            current["paths"].append(line)
    previous: dict[str, Any] | None = None
    violations: list[dict[str, str]] = []
    for commit in commits:
        subject = commit["subject"]
        if re.search(r"\brepair\b", subject, re.IGNORECASE):
            category = "repair_checkpoint"
        elif HISTORY_NOISE_RE.match(subject):
            category = "history_noise"
        elif HISTORY_BOUNDARY_RE.search(subject):
            category = "authority/config reconciliation"
        else:
            category = "semantic checkpoint"
        commit["category"] = category
        if previous and previous["category"] == category == "history_noise":
            overlap = sorted(set(previous["paths"]) & set(commit["paths"]))
            if overlap:
                violations.append({"type": "repeated_history_noise", "previous": previous["sha"], "current": commit["sha"], "paths": ",".join(overlap)})
        previous = commit
    return {"status": "fail" if violations else "pass", "commits": commits, "violations": violations}


def validate_ledger(ledger: dict[str, Any], *, expected_repository: str | None = None, expected_issue: int | None = None) -> None:
    if not isinstance(ledger, dict) or not isinstance(ledger.get("repository"), str) or not ledger["repository"] or not isinstance(ledger.get("issue"), int) or ledger["issue"] <= 0 or not isinstance(ledger.get("criteria"), list) or not ledger["criteria"] or not isinstance(ledger.get("tasks"), list) or not ledger["tasks"]:
        raise ValueError("ledger must contain criteria and a non-empty task DAG")
    if expected_repository is not None and ledger["repository"] != expected_repository:
        raise ValueError("ledger repository does not match the trusted Issue authority")
    if expected_issue is not None and ledger["issue"] != expected_issue:
        raise ValueError("ledger Issue does not match the trusted Issue authority")
    criteria_ids = [item.get("id") for item in ledger["criteria"] if isinstance(item, dict)]
    if len(criteria_ids) != len(ledger["criteria"]) or not criteria_ids or len(set(criteria_ids)) != len(criteria_ids):
        raise ValueError("ledger criteria must have unique ids")
    task_ids = []
    task_criteria: set[str] = set()
    for task in ledger["tasks"]:
        if not isinstance(task, dict) or not task.get("id") or not task.get("objective") or task.get("status") not in {"pending", "ready", "running", "done", "blocked"} or not isinstance(task.get("dependencies", []), list) or not isinstance(task.get("criteria", []), list) or not task["criteria"]:
            raise ValueError("ledger task is incomplete")
        task_ids.append(task["id"])
        task_criteria.update(task["criteria"])
        if any(item not in criteria_ids for item in task["criteria"]):
            raise ValueError("ledger task references an unknown criterion")
        if "execution" in task:
            raise ValueError("task execution history must use executions")
        if "executions" in task:
            executions = task["executions"]
            if not isinstance(executions, list) or not executions or len(executions) > MAX_TASK_EXECUTIONS:
                raise ValueError("task executions must be a bounded non-empty list")
            for execution in executions:
                validate_task_execution(execution)
    if len(set(task_ids)) != len(task_ids) or any(dep not in task_ids or dep == task["id"] for task in ledger["tasks"] for dep in task.get("dependencies", [])):
        raise ValueError("ledger task dependencies are invalid")
    if task_criteria != set(criteria_ids):
        raise ValueError("ledger task DAG does not cover every criterion")
    graph = {task["id"]: task.get("dependencies", []) for task in ledger["tasks"]}
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise ValueError("ledger task dependencies contain a cycle")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in graph[task_id]:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)
    for task_id in task_ids:
        visit(task_id)
    task_id_set = set(task_ids)
    task_by_id = {task["id"]: task for task in ledger["tasks"]}
    for item in ledger.get("files", []):
        if not isinstance(item, dict) or not item.get("path") or item.get("task") not in task_id_set or not item.get("disposition") or not item.get("evidence") or not isinstance(item.get("criteria"), list) or not item["criteria"] or any(ac not in criteria_ids for ac in item["criteria"]):
            raise ValueError("ledger file coverage is incomplete")
        if any(ac not in task_by_id[item["task"]]["criteria"] for ac in item["criteria"]):
            raise ValueError("ledger file criteria do not belong to the owning task")
    if ledger.get("baseline_files"):
        raise ValueError("baseline files must come from the trusted session, not the ledger")
    if not isinstance(ledger.get("supporting_documents"), list) or not ledger["supporting_documents"] or any(not isinstance(item, dict) or item.get("disposition") not in {"UPDATED", "VERIFIED_UNCHANGED", "NOT_APPLICABLE", "BLOCKED"} or (item.get("disposition") != "NOT_APPLICABLE" and not item.get("path")) or not str(item.get("reason", "")).strip() for item in ledger["supporting_documents"]):
        raise ValueError("ledger supporting-document closure is incomplete")


def validate_task_execution(value: Any) -> None:
    required = {"actor", "primitive", "display_label", "attempt", "receipt", "result", "validation"}
    if not isinstance(value, dict) or set(value) != required or value.get("actor") not in {"agy", "prometheus"} or value.get("primitive") not in {"harness", "subagent"} or (value.get("actor"), value.get("primitive")) not in {("agy", "harness"), ("prometheus", "subagent")} or not isinstance(value.get("display_label"), str) or not value["display_label"].strip() or any(char in value["display_label"] for char in "\n\r\x00") or isinstance(value.get("attempt"), bool) or not isinstance(value.get("attempt"), int) or value["attempt"] < 1 or not isinstance(value.get("receipt"), str) or not value["receipt"].strip() or any(char in value["receipt"] for char in "\n\r\x00") or value.get("result") not in {"success", "failed", "unavailable", "timed_out", "not_assessed"} or value.get("validation") not in {"pass", "fail", "not_assessed"}:
        raise ValueError("task execution record is incomplete or invalid")


def record_task_execution(ledger: dict[str, Any], task_id: str, execution: dict[str, Any]) -> dict[str, Any]:
    """Append one compact bounded execution pointer; never store prompts or transcripts."""
    validate_task_execution(execution)
    if not isinstance(ledger, dict) or not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("task execution requires a task id")
    tasks = ledger.get("tasks")
    if not isinstance(tasks, list) or not any(isinstance(task, dict) and task.get("id") == task_id for task in tasks):
        raise ValueError("task execution references an unknown task")
    updated = dict(ledger)
    updated["tasks"] = []
    for task in tasks:
        if task.get("id") != task_id:
            updated["tasks"].append(task)
            continue
        existing = task.get("executions", [])
        if "execution" in task or not isinstance(existing, list) or len(existing) >= MAX_TASK_EXECUTIONS:
            raise ValueError("task execution history is missing or at its bounded limit")
        updated["tasks"].append({**task, "executions": [*existing, dict(execution)]})
    return updated


def reconcile(repo: str, base: str, ledger: dict[str, Any], baseline: dict[str, Any] | None = None, *, expected_repository: str | None = None, expected_issue: int | None = None) -> None:
    validate_ledger(ledger, expected_repository=expected_repository, expected_issue=expected_issue)
    if baseline is None:
        raise ValueError("reconciliation requires a trusted fingerprinted baseline")
    validate_baseline_record(baseline)
    baseline_files = set()
    baseline_renames = []
    baseline_dirs = set()
    baseline_status_records = (baseline or {}).get("status_records")
    if baseline_status_records is None:
        baseline_status_records = []
        for entry in (baseline or {}).get("status", []):
            if len(entry) < 4:
                continue
            baseline_status_records.append({"xy": entry[:2], "path": entry[3:]})
    for record in baseline_status_records:
        path = record.get("path", "")
        if path.endswith("/"):
            baseline_dirs.add(path.rstrip("/"))
        baseline_files.update(path.rstrip("/") for path in status_paths([record]))
        if record.get("original_path"):
            baseline_renames.append((record["original_path"].rstrip("/"), path.rstrip("/")))
    if baseline and (baseline.get("repo_root") != canonical(repo) or baseline.get("head") != git(repo, "rev-parse", base)):
        raise ValueError("trusted baseline does not match the reconciliation repository/base")
    actual_all = set(changed_files(repo, base))
    baseline_manifest = (baseline or {}).get("workspace_manifest") or {}
    current_manifest = workspace_manifest(repo, (baseline or {}).get("excluded_paths") or None)
    committed = set(git(repo, "diff", "--name-only", f"{base}..HEAD").splitlines())
    if baseline is not None:
        actual_all.update({path for path in baseline_manifest.keys() | current_manifest.keys() if baseline_manifest.get(path) != current_manifest.get(path)})
    tracked = set((baseline or {}).get("tracked_files", []))
    protected_files = baseline_files | (set((baseline or {}).get("workspace_files", [])) - tracked)
    renamed_old = {old for old, _ in baseline_renames}
    missing_baseline = {path for path in protected_files if path not in renamed_old and path not in {"", "."} and path not in current_manifest}
    if missing_baseline:
        raise ValueError(json.dumps({"missing_preexisting": sorted(missing_baseline)}, sort_keys=True))
    unchanged_baseline = {path for path in baseline_files if current_manifest.get(path) == baseline_manifest.get(path)}
    for old, new in baseline_renames:
        if current_manifest.get(new) == baseline_manifest.get(new) and old not in current_manifest:
            unchanged_baseline.update({old, new})
    for directory in baseline_dirs:
        descendants = [path for path in actual_all if path == directory or path.startswith(directory + "/")]
        if descendants and all(current_manifest.get(path) == baseline_manifest.get(path) for path in descendants):
            unchanged_baseline.update(descendants)
    actual = actual_all - (unchanged_baseline - committed)
    entries = {entry["path"]: entry for entry in ledger.get("files", [])}
    missing = sorted(actual - entries.keys())
    stale = sorted(set(entries) - actual)
    allowed = ledger.get("allowed_paths", [])
    foreign = sorted(path for path in actual if not allowed or not path_matches_allowance(path, allowed, repo))
    if missing or foreign or stale:
        raise ValueError(json.dumps({"unaccounted": missing, "foreign": foreign, "stale": stale}, sort_keys=True))
    for path, entry in entries.items():
        if not entry.get("task") or not entry.get("disposition") or not entry.get("evidence"):
            raise ValueError(f"incomplete file ledger entry: {path}")


def review_current(review: dict[str, Any], *, candidate: str, base_ref: str, base_head: str, criteria_fp: str, rubric_ref: str, authority_fp: str, workspace_fp: str, evidence_fp: str, validation_fp: str, supporting_documents_fp: str, changed_files_fp: str, axis: str | None = None) -> bool:
    snapshot = review.get("snapshot") or {}
    attestation = snapshot.get("reviewer_attestation")
    identity_ok = snapshot.get("reviewer_identity_source") == "host_observed_not_assessed" and valid_reviewer_attestation(attestation, snapshot.get("reviewer_session_id"), snapshot.get("review_route", "luna-max"))
    return review.get("reviewability") == "reviewable" and (axis is None or (review.get("review_attempt", {}).get("axis") == axis and snapshot.get("review_attempt", {}).get("axis") == axis)) and re.fullmatch(r"[0-9a-f]{40}", str(candidate)) is not None and re.fullmatch(r"[0-9a-f]{40}", str(base_head)) is not None and snapshot.get("fresh_context") is True and snapshot.get("read_only") is True and observed_reviewer_id(snapshot.get("reviewer_session_id")) and identity_ok and snapshot.get("base_ref") == base_ref and snapshot.get("base_head") == base_head and snapshot.get("candidate_head") == candidate and snapshot.get("criteria_fingerprint") == criteria_fp and snapshot.get("rubric_ref") == rubric_ref and snapshot.get("authority_fingerprint") == authority_fp and snapshot.get("workspace_fingerprint") == workspace_fp and snapshot.get("evidence_fingerprint") == evidence_fp and snapshot.get("validation_fingerprint") == validation_fp and snapshot.get("supporting_documents_fingerprint") == supporting_documents_fp and snapshot.get("changed_files_fingerprint") == changed_files_fp and review.get("stale") is False


def accept_candidate(session: dict[str, Any], work_review: dict[str, Any], packet: dict[str, Any], *, repo_root: str, worktree_root: str | None = None, base_ref: str, candidate: str, base_head: str, criteria_fp: str, rubric_ref: str, evidence_fp: str, goal_review: dict[str, Any] | None = None) -> dict[str, Any]:
    lifecycle_root = validate_state_dir(session["state_dir"], repo_root, worktree_root) if session.get("state_dir") else None
    if session.get("status") not in {"reviewing"}:
        raise ValueError("candidate acceptance requires a reviewing session")
    if not isinstance(goal_review, dict) or work_review.get("review_attempt", {}).get("axis") != "work" or goal_review.get("review_attempt", {}).get("axis") != "goal":
        raise ValueError("candidate acceptance requires separate WORK and GOAL reviews")
    if work_review.get("snapshot", {}).get("reviewer_session_id") == goal_review.get("snapshot", {}).get("reviewer_session_id"):
        raise ValueError("WORK and GOAL reviews require distinct reviewer sessions")
    expected_criteria_fp = digest(packet.get("criteria"))
    expected_evidence_fp = digest(packet.get("evidence"))
    if criteria_fp != expected_criteria_fp or evidence_fp != expected_evidence_fp:
        raise ValueError("caller fingerprints do not match review packet")
    locked_base = session.get("base") or {}
    if locked_base.get("branch") != base_ref or locked_base.get("sha") != base_head:
        raise ValueError("candidate base does not match the session preflight base")
    authority = packet.get("authority") or {}
    if authority.get("repository") != session.get("repository") or authority.get("issue") != session.get("issue") or authority.get("task") != session.get("task"):
        raise ValueError("review packet authority does not match the session Issue authority")
    expected_binding = repository_binding(repo_root, worktree_root)
    worktree_repo = expected_binding["worktree"]
    if session.get("repo_binding") != expected_binding:
        raise ValueError("worktree does not match the session preflight repository binding")
    if packet.get("repo_binding") != expected_binding:
        raise ValueError("review packet repository binding does not match the current worktree")
    if any(review.get("snapshot", {}).get("repo_binding_fingerprint") != digest(expected_binding) for review in (work_review, goal_review)):
        raise ValueError("candidate review repository binding is stale")
    try:
        bound = git(worktree_repo, "rev-parse", "--verify", f"{candidate}^{{commit}}") == candidate and git(worktree_repo, "rev-parse", "HEAD") == candidate and git(worktree_repo, "rev-parse", base_ref) == base_head and is_ancestor(worktree_repo, base_head, candidate)
    except RuntimeError:
        bound = False
    if not bound:
        raise ValueError("candidate or base is not bound to the current repository state")
    current_status_records = git_status_records(worktree_repo)
    baseline_record = session.get("baseline")
    if baseline_record is not None:
        validate_baseline_record(baseline_record)
    baseline_status = (baseline_record or {}).get("status")
    if baseline_status is None:
        if current_status_records:
            raise ValueError("acceptance requires a clean worktree when no preflight baseline is recorded")
    elif current_status_records != baseline_record.get("status_records", []):
        raise ValueError("worktree changed after the preflight baseline")
    baseline_manifest = (session.get("baseline") or {}).get("workspace_manifest")
    if baseline_status and isinstance(baseline_manifest, dict):
        current_manifest = workspace_manifest(worktree_repo, baseline_record.get("excluded_paths") or ([str(lifecycle_root)] if lifecycle_root else None))
        baseline_paths = {path.rstrip("/") for path in status_paths(baseline_record.get("status_records", []))}
        protected_paths = {path for path in baseline_manifest if path in baseline_paths or any(path.startswith(root + "/") for root in baseline_paths)}
        if any(current_manifest.get(path) != baseline_manifest.get(path) for path in protected_paths):
            raise ValueError("pre-existing worktree content changed after preflight")
    reviewed_fingerprint = packet.get("workspace_fingerprint")
    if not reviewed_fingerprint or workspace_fingerprint(worktree_repo, [str(lifecycle_root)] if lifecycle_root else None) != reviewed_fingerprint:
        raise ValueError("worktree content changed after the reviewed candidate snapshot")
    actual_changed_files = committed_changed_files(worktree_repo, base_head, candidate)
    if sorted(packet.get("changed_files", [])) != actual_changed_files or sorted((packet.get("candidate") or {}).get("changed_files", [])) != actual_changed_files:
        raise ValueError("review packet changed_files do not match the bound Git diff")
    try:
        review_scripts = Path(__file__).resolve().parents[2] / "athena-review" / "scripts"
        if str(review_scripts) not in sys.path:
            sys.path.insert(0, str(review_scripts))
        from review import supporting_documents_clear, validate_result
        validate_result(work_review, {**packet, "review_attempt": work_review["review_attempt"]}, candidate)
        validate_result(goal_review, {**packet, "review_attempt": goal_review["review_attempt"]}, candidate)
    except (ImportError, ValueError, KeyError) as exc:
        raise ValueError(f"candidate review failed full validation: {exc}") from exc
    if not supporting_documents_clear(work_review.get("supporting_documents")) or not supporting_documents_clear(goal_review.get("supporting_documents")):
        raise ValueError("supporting-document closure is incomplete")
    changed_files_fp = digest(actual_changed_files)
    review_args = dict(candidate=candidate, base_ref=base_ref, base_head=base_head, criteria_fp=criteria_fp, rubric_ref=rubric_ref, authority_fp=digest(packet.get("authority")), workspace_fp=reviewed_fingerprint, evidence_fp=evidence_fp, validation_fp=digest(packet.get("validation")), supporting_documents_fp=digest(packet.get("supporting_documents")), changed_files_fp=changed_files_fp)
    if not review_current(work_review, axis="work", **review_args) or not review_current(goal_review, axis="goal", **review_args):
        raise ValueError("candidate review is stale or bound to different evidence")
    work_snapshot = work_review.get("snapshot", {})
    goal_snapshot = goal_review.get("snapshot", {})
    shared_snapshot_fields = ("candidate_head", "base_ref", "base_head", "criteria_fingerprint", "rubric_ref", "authority_fingerprint", "workspace_fingerprint", "evidence_fingerprint", "validation_fingerprint", "supporting_documents_fingerprint", "changed_files_fingerprint", "repo_binding_fingerprint", "criteria_revision", "criteria_manifest_fingerprint", "review_route")
    if any(work_snapshot.get(field) != goal_snapshot.get(field) for field in shared_snapshot_fields):
        raise ValueError("WORK and GOAL reviews are bound to different snapshots")
    criteria = goal_review.get("goal_review", {}).get("criteria") or []
    findings = work_review.get("findings")
    material_verified = [item for item in (findings if isinstance(findings, list) else []) if str(item.get("severity", "minor")).lower() in {"critical", "blocker", "major", "material"} and item.get("evidence_state") == "verified"]
    if any(review.get("snapshot", {}).get("reviewer_identity_source") != "host_observed_not_assessed" for review in (work_review, goal_review)):
        raise ValueError("local kernel cannot authenticate external reviewer trust")
    history_policy = classify_commit_history(worktree_repo, base_head, candidate)
    if history_policy["status"] != "pass":
        raise ValueError(f"history_policy_violation: {json.dumps(history_policy['violations'], sort_keys=True)}")
    if work_review.get("version") != 1 or goal_review.get("version") != 1 or work_review.get("recommendation") != "not_assessed" or goal_review.get("recommendation") != "not_assessed" or work_review.get("work_review", {}).get("status") != "pass" or goal_review.get("goal_review", {}).get("status") != "complete" or not criteria or any(item.get("status") != "fulfilled" or not item.get("id") or not str(item.get("evidence", "")).strip() for item in criteria) or not isinstance(findings, list) or material_verified or work_review.get("verified_material_findings") != []:
        raise ValueError("candidate is not technically eligible for parent decision")
    session = dict(session)
    session["candidate_head"] = candidate
    session["candidate"] = {"head": candidate, "checkpoint_reason": "integrated_candidate"}
    session["reviewed_workspace_fingerprint"] = reviewed_fingerprint
    # This helper proves technical eligibility only. Parent acceptance and
    # Draft PR publication are outside this repository process.
    session["status"] = "awaiting_parent_decision"
    session["review_cycle"] = {"round": work_review["review_attempt"]["round"], "candidate_head": candidate, "work": {"receipt": f"review/athena-{candidate[:7]}-work-r{work_review['review_attempt']['round']}.yaml", "display_label": work_review["review_attempt"]["display_label"], "review_id": work_review["review_attempt"]["review_id"], "reviewer_session_id": work_snapshot["reviewer_session_id"], "status": work_review["work_review"]["status"], "stale": False}, "goal": {"receipt": f"review/athena-{candidate[:7]}-goal-r{goal_review['review_attempt']['round']}.yaml", "display_label": goal_review["review_attempt"]["display_label"], "review_id": goal_review["review_attempt"]["review_id"], "reviewer_session_id": goal_snapshot["reviewer_session_id"], "status": goal_review["goal_review"]["status"], "stale": False}}
    return session


def mark_stale(session: dict[str, Any], new_head: str) -> dict[str, Any]:
    session = dict(session)
    cycle = session.get("review_cycle")
    if isinstance(cycle, dict) and cycle.get("candidate_head") and cycle.get("candidate_head") != new_head:
        cycle = {**cycle, "round": int(cycle.get("round", 0)) + 1, "candidate_head": new_head}
        for axis in ("work", "goal"):
            if isinstance(cycle.get(axis), dict):
                cycle[axis] = {**cycle[axis], "stale": True, "superseded_by": new_head}
        session["review_cycle"] = cycle
        if session.get("status") in {"awaiting_parent_decision"}:
            session["status"] = "reviewing"
    session["current_head"] = new_head
    session["candidate_head"] = new_head
    return session


def command_preflight(args: argparse.Namespace) -> None:
    repo = canonical(args.repo_root)
    worktree = canonical(args.worktree_root or args.repo_root)
    state = validate_state_dir(args.state_dir, repo, worktree)
    current = baseline(worktree, [str(state)])
    if current["status"] and not args.allow_known_dirty:
        raise SystemExit("BLOCKED: preflight found pre-existing dirty state")
    if current["status"] and args.dirty_baseline_fingerprint != current["fingerprint"]:
        raise SystemExit("BLOCKED: dirty baseline fingerprint is missing or does not match current state")
    if current["status"]:
        allowed = args.allowed_paths
        if not allowed or any(not any(path == item or path.startswith(item.rstrip("/") + "/") for item in allowed) for path in status_paths(current.get("status_records", []))):
            raise SystemExit("BLOCKED: dirty baseline overlaps undeclared paths")
    if (state / "session.yaml").exists() or (state / "tasks.yaml").exists():
        raise SystemExit("BLOCKED: existing session state requires explicit reconciliation")
    try:
        resolved_base = git(worktree, "rev-parse", "--verify", f"{args.base_branch}^{{commit}}")
        if resolved_base != args.base_sha or current["head"] != args.base_sha:
            raise SystemExit("BLOCKED: checkout HEAD, base branch, and supplied base SHA are not exactly aligned")
    except RuntimeError as exc:
        raise SystemExit(f"BLOCKED: supplied base SHA is unavailable: {exc}") from exc
    binding = repository_binding(repo, worktree)
    session = {"version": 1, "repository": args.repository, "issue": args.issue, "task": args.task, "repo_binding": binding, "state_dir": canonical(state), "base": {"branch": args.base_branch, "sha": args.base_sha}, "canonical_branch": current["branch"], "baseline": current, "current_head": current["head"], "candidate_head": None, "candidate": {"head": None, "checkpoint_reason": None}, "status": "ready", "current_task": None, "review_cycle": {"round": 1, "candidate_head": None, "work": {"status": "not_run", "stale": False}, "goal": {"status": "not_run", "stale": False}}, "blocked_reason": None}
    criteria = load_document(args.criteria)
    tasks = {"version": 1, "repository": args.repository, "issue": args.issue, "allowed_paths": args.allowed_paths, "tasks": [], "criteria": criteria, "files": [], "supporting_documents": []}
    ensure_safe_directory(state)
    dump_document(state / "session.yaml", session)
    dump_document(state / "tasks.yaml", tasks)
    print(json.dumps({"status": "READY", "baseline": current, "state_dir": str(state)}))


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    pre = sub.add_parser("preflight")
    pre.add_argument("--repo-root", required=True); pre.add_argument("--worktree-root"); pre.add_argument("--repository", required=True); pre.add_argument("--issue", required=True, type=int); pre.add_argument("--task"); pre.add_argument("--base-branch", required=True); pre.add_argument("--base-sha", required=True); pre.add_argument("--state-dir", required=True); pre.add_argument("--criteria", required=True); pre.add_argument("--allowed-paths", nargs="*", default=[]); pre.add_argument("--allow-known-dirty", action="store_true"); pre.add_argument("--dirty-baseline-fingerprint"); pre.set_defaults(handler=command_preflight)
    receipt = sub.add_parser("validate-receipt"); receipt.add_argument("--request", required=True); receipt.add_argument("--receipt", required=True); receipt.set_defaults(handler=lambda a: (validate_receipt(load_document(a.request), load_document(a.receipt)), print("PASS")))
    recon = sub.add_parser("reconcile"); recon.add_argument("--repo-root", required=True); recon.add_argument("--base", required=True); recon.add_argument("--ledger", required=True); recon.add_argument("--baseline-session", required=True)
    def do_reconcile(a: argparse.Namespace) -> None:
        session = load_document(a.baseline_session)
        reconcile(a.repo_root, a.base, load_document(a.ledger), session.get("baseline"), expected_repository=session.get("repository"), expected_issue=session.get("issue")); print("PASS")
    recon.set_defaults(handler=do_reconcile)
    args = parser.parse_args()
    try:
        args.handler(args)
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr); return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
