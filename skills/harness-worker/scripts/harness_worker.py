#!/usr/bin/env python3
"""Thin list-form subprocess adapter with exact native-session binding."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import errno
import hashlib
import json
import os
import re
import selectors
import signal
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

MAX_OUTPUT_BYTES = 1024 * 1024
INVALID_NATIVE_SESSION_IDS = {"NOT_ASSESSED", "UNKNOWN", "NONE", "NULL", "UNAVAILABLE"}
FORBIDDEN_RECEIPT_KEYS = {"ac_satisfied", "issue_complete", "review_passed", "accepted_head", "final_success"}
WORKER_AVAILABILITY_FAILURES = {"QUOTA_EXHAUSTED", "RATE_LIMITED", "RUNTIME_UNAVAILABLE", "PROVIDER_UNAVAILABLE"}
SEMANTIC_ROUTES = {"economy", "balanced", "strong", "strongest"}
ROUTE_EFFORT_MAP = {"economy": "low", "balanced": "medium", "strong": "high", "strongest": "xhigh"}
LEGACY_ROUTE_MAP = {"low": "economy", "bounded": "balanced", "medium": "balanced", "high": "strong", "critical": "strongest"}
REASONING_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
CAPACITY_STATES = {"AVAILABLE", "LOW", "EXHAUSTED", "RATE_LIMITED", "UNKNOWN"}
ERROR_CODES = {
    "AUTH_REQUIRED", "QUOTA_EXHAUSTED", "RATE_LIMITED", "PERMISSION_DENIED",
    "SESSION_INVALID", "RUNTIME_UNAVAILABLE", "PROVIDER_UNAVAILABLE",
    "MODEL_ROUTE_UNAVAILABLE", "EXECUTION_PROTOCOL_VIOLATION", "TIMED_OUT",
    "EXECUTION_FAILED", "MUTATION_SCOPE_VIOLATION",
}
NATIVE_TERMINAL_LANES = {"agy"}
AGY_DELEGATION_FLAGS = {"--print", "-p"}
AGY_DELEGATION_OPTIONS = {"--output-format", "--model", "--effort", "--conversation", "--print-timeout"}
USAGE_FIELDS = ("input_tokens", "cache_read_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens", "latency_ms")
ANSI_ESCAPE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")


def load_document(path: str | Path) -> Any:
    import yaml
    value = yaml.safe_load(Path(path).read_text())
    if value is None:
        raise ValueError(f"empty document: {path}")
    return value


def canonical(path: str | Path) -> str:
    return os.path.realpath(os.path.abspath(os.fspath(path)))


def is_git_metadata_path(path: str | Path) -> bool:
    return ".git" in Path(path).parts


def filesystem_payload(target: Path) -> bytes:
    mode = target.lstat().st_mode
    if stat.S_ISLNK(mode):
        return b"symlink\0" + os.readlink(target).encode()
    if stat.S_ISREG(mode):
        return target.read_bytes()
    return b"special\0" + str(stat.S_IFMT(mode)).encode()


def git_worktree_identity(repo: str) -> dict[str, str]:
    root = canonical(repo)
    if not Path(root).is_dir():
        raise ValueError("repository root is not a directory")
    values: dict[str, str] = {}
    for key, args in {"top_level": ("--show-toplevel",), "git_dir": ("--git-dir",), "git_common_dir": ("--git-common-dir",), "inside_worktree": ("--is-inside-work-tree",)}.items():
        result = subprocess.run(["git", "-C", root, "rev-parse", *args], text=True, capture_output=True)
        if result.returncode:
            raise ValueError("repository root is not a Git worktree")
        value = result.stdout.strip()
        values[key] = value if key == "inside_worktree" else canonical(Path(value) if Path(value).is_absolute() else Path(root) / value)
    if values["inside_worktree"] != "true" or values["top_level"] != root:
        raise ValueError("request repository root is not the actual Git worktree root")
    return {key: values[key] for key in ("top_level", "git_dir", "git_common_dir")}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _walk_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return {str(key) for key in value} | set().union(*(_walk_keys(child) for child in value.values()))
    if isinstance(value, list):
        return set().union(*(_walk_keys(child) for child in value)) if value else set()
    return set()


def effective_context(repo_root: str, cwd: str, required_skills: list[str] | None = None) -> dict[str, Any]:
    root = Path(canonical(repo_root)); current = Path(canonical(cwd))
    if current != root and root not in current.parents:
        raise ValueError("context cwd escapes repository root")
    relative = current.relative_to(root).parts
    ancestors = [root.joinpath(*relative[:index]) for index in range(len(relative) + 1)]
    instruction_paths = []
    for directory in ancestors:
        override, standard = directory / "AGENTS.override.md", directory / "AGENTS.md"
        if override.is_file(): instruction_paths.append(override)
        elif standard.is_file(): instruction_paths.append(standard)
    skill_paths = []
    missing_skills = []
    for name in required_skills or []:
        if not isinstance(name, str) or not name.strip(): continue
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
    records = [{"path": str(path.relative_to(root)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in [*instruction_paths, *skill_paths]]
    binding = {"cwd": str(current), "instruction_paths": [item["path"] for item in records[:len(instruction_paths)]], "skill_paths": [item["path"] for item in records[len(instruction_paths):]], "records": records}
    binding["fingerprint"] = _digest(binding)
    return binding


def path_matches_allowance(path: str, allowed: list[str], repo_root: str | None = None) -> bool:
    for item in allowed:
        if Path(item) == Path("."): continue
        normalized = Path(item).as_posix().rstrip("/")
        if path == normalized: return True
        explicit_directory = item.endswith("/") or (repo_root is not None and (Path(repo_root) / normalized).is_dir())
        if explicit_directory and path.startswith(normalized + "/"): return True
    return False


def requested_semantic_route(request: dict[str, Any]) -> str:
    route = request.get("route_requirements") or {}
    value = route.get("semantic_route") or LEGACY_ROUTE_MAP.get(route.get("semantic_complexity"), route.get("semantic_complexity"))
    if value not in SEMANTIC_ROUTES:
        raise ValueError("MODEL_ROUTE_UNAVAILABLE: semantic route must be economy, balanced, strong, or strongest")
    return value


def requested_reasoning_effort(request: dict[str, Any]) -> str:
    explicit = (request.get("route_requirements") or {}).get("requested_effort")
    if explicit is not None and explicit not in REASONING_EFFORTS:
        raise ValueError("MODEL_ROUTE_UNAVAILABLE: unsupported reasoning effort")
    return explicit or ROUTE_EFFORT_MAP[requested_semantic_route(request)]


def select_worker(error_code: str | None = None) -> dict[str, Any]:
    reason = str(error_code or "").strip().upper()
    return {"requested_worker": "agy", "actual_worker": "agy", "fallback_triggered": reason in WORKER_AVAILABILITY_FAILURES, "fallback_reason": reason if reason in WORKER_AVAILABILITY_FAILURES else None}


def validate_worker_route(value: Any) -> None:
    required = {"requested_worker", "actual_worker", "fallback_triggered", "fallback_reason"}
    if not isinstance(value, dict) or not required <= value.keys() or value.get("requested_worker") != "agy" or value.get("actual_worker") not in {"agy", "prometheus"} or not isinstance(value.get("fallback_triggered"), bool):
        raise ValueError("worker_route is invalid")
    if value["fallback_triggered"] and value.get("fallback_reason") not in WORKER_AVAILABILITY_FAILURES:
        raise ValueError("worker_route fallback must be availability-driven")
    if not value["fallback_triggered"] and (value.get("actual_worker") != "agy" or value.get("fallback_reason") is not None):
        raise ValueError("worker_route without fallback must remain on AGY")


def validate_harness_request(request: dict[str, Any]) -> None:
    required = {"version", "request_id", "authority", "lane", "repo", "scope", "session", "permission_policy", "return_contract", "route_requirements", "expected_context", "harness", "command", "outputs"}
    missing = required - set(request)
    if missing: raise ValueError(f"request missing fields: {sorted(missing)}")
    if request["version"] != 1 or not request["request_id"] or request["lane"] not in {"execute", "repair"} or request["return_contract"] != "normalized-runtime-receipt-v1":
        raise ValueError("unsupported request version, lane, or return_contract")
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
    if request["harness"] not in {"agy", "fake"}:
        raise ValueError("unsupported harness")
    if not isinstance(request["command"], list) or not request["command"] or any(not isinstance(item, str) for item in request["command"]):
        raise ValueError("request command must be a non-empty argv list")
    authority = request["authority"]
    if not isinstance(authority, dict) or not authority.get("repository") or not isinstance(authority.get("issue"), int) or authority["issue"] <= 0:
        raise ValueError("request authority must identify a real positive Issue")
    repo = request["repo"]
    if not isinstance(repo, dict): raise ValueError("request repo must be a mapping")
    for key in ("root", "cwd", "worktree"):
        if not isinstance(repo.get(key), str) or not repo[key]: raise ValueError(f"request repo missing {key}")
        if any(char in repo[key] for char in ('"', "\\", "\n", "\r", "\x00")): raise ValueError(f"request repo {key} contains unsafe sandbox syntax")
    root, cwd, worktree = canonical(repo["root"]), canonical(repo["cwd"]), canonical(repo["worktree"])
    if not (cwd == worktree or cwd.startswith(worktree + os.sep)) or not Path(cwd).is_dir() or not Path(worktree).is_dir():
        raise ValueError("request cwd/worktree must identify directories")
    if git_worktree_identity(root)["git_common_dir"] != git_worktree_identity(worktree)["git_common_dir"]:
        raise ValueError("request worktree belongs to a different repository")
    if request["permission_policy"] not in {"read-only", "bounded-write"}: raise ValueError("unsupported permission policy")
    scope = request["scope"]
    if not isinstance(scope, dict) or not scope.get("mutation_boundary"): raise ValueError("request scope must declare mutation_boundary")
    allowed = scope.get("allowed_paths") or []
    if not isinstance(allowed, list): raise ValueError("scope allowed_paths must be a list")
    if request["permission_policy"] == "bounded-write" and not allowed: raise ValueError("bounded-write request must declare allowed_paths")
    for path in allowed:
        if not isinstance(path, str) or os.path.isabs(path) or Path(path) == Path(".") or ".." in Path(path).parts or is_git_metadata_path(path) or any(char in path for char in ('"', "\\", "\n", "\r", "\x00")):
            raise ValueError("scope allowed_paths must stay relative to repo root")
    outputs = request["outputs"]
    if not isinstance(outputs, dict) or not isinstance(outputs.get("registry"), str) or not isinstance(outputs.get("receipt"), str): raise ValueError("request outputs must declare registry and receipt paths")
    if not isinstance(request.get("session"), dict) or request["session"].get("policy") not in {"fresh", "resume", "resume_or_start", "rebind"}:
        raise ValueError("unsupported session policy")
    if request["harness"] == "agy" and Path(request["command"][0]).name != "agy": raise ValueError("RUNTIME_UNAVAILABLE: native terminal command does not match the requested lane")


def validate_capacity(capacity: Any) -> None:
    if not isinstance(capacity, dict) or capacity.get("state") not in CAPACITY_STATES or not isinstance(capacity.get("source"), str) or not capacity["source"].strip():
        raise ValueError("receipt capacity observation is invalid")
    if capacity["state"] != "UNKNOWN" and capacity["source"].strip().lower() in {"none", "not_assessed", "unknown"}:
        raise ValueError("non-UNKNOWN capacity requires an observed source")


def valid_observed_native_session_id(value: Any) -> bool:
    return valid_native_session_id(value)


def valid_observed_provider(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip().upper() not in INVALID_NATIVE_SESSION_IDS


def validate_harness_receipt(request: dict[str, Any], receipt: dict[str, Any]) -> None:
    validate_harness_request(request)
    if not isinstance(receipt, dict) or FORBIDDEN_RECEIPT_KEYS.intersection(_walk_keys(receipt)):
        raise ValueError("runtime receipt is invalid or contains workflow claims")
    if receipt.get("version") != 1 or receipt.get("request_id") != request["request_id"]:
        raise ValueError("receipt version or request_id mismatch")
    runtime, execution, context, usage, capacity = (receipt.get(key, {}) for key in ("runtime", "execution", "context", "usage", "capacity"))
    if any(not isinstance(value, dict) for value in (runtime, execution, context, usage, capacity)):
        raise ValueError("receipt sections must be mappings")
    required_runtime = {"harness", "executor_provenance", "requested_route", "actual_route", "requested_profile", "resolved_profile", "provider", "actual_model", "actual_effort", "native_session_id", "session_state"}
    required_execution = {"repo_root", "cwd", "worktree", "permission_observation", "status", "exit_code", "duration_ms"}
    required_context = {"instruction_fingerprint", "skill_observation", "effective_context"}
    if not required_runtime <= runtime.keys() or not required_execution <= execution.keys() or not required_context <= context.keys() or not set(USAGE_FIELDS) <= usage.keys() or not isinstance(receipt.get("limitations"), list):
        raise ValueError("receipt is missing required runtime observations")
    if not isinstance(context["effective_context"], dict) or not context["effective_context"].get("fingerprint"):
        raise ValueError("receipt must bind effective context")
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
    if permission_observation not in {"not_assessed", "read-only", "bounded-write"} or (permission_observation != "not_assessed" and permission_observation != request["permission_policy"]):
        raise ValueError("receipt permission_observation contradicts the request")
    validate_capacity(capacity)
    if runtime.get("requested_route") != requested_semantic_route(request) or execution.get("status") not in {"SUCCESS", "FAILED", "TIMED_OUT"}:
        raise ValueError("receipt runtime observations contradict the request")
    if execution.get("status") == "SUCCESS" and request["harness"] == "fake" and not valid_observed_native_session_id(runtime.get("native_session_id")):
        raise ValueError("successful receipt must expose a resumable native_session_id")
    if not isinstance(runtime.get("executor_provenance"), dict) or not runtime["executor_provenance"].get("executable"):
        raise ValueError("receipt must expose executor provenance")
    actual_harness = runtime.get("harness")
    expected_kind = "test-harness" if actual_harness == "fake" else "native-terminal"
    if actual_harness != request["harness"] or runtime["executor_provenance"].get("kind") != expected_kind:
        raise ValueError("receipt executor provenance does not match the request")
    if canonical(execution.get("repo_root", "")) != canonical(request["repo"]["root"]) or canonical(execution.get("cwd", "")) != canonical(request["repo"]["cwd"]) or canonical(execution.get("worktree", "")) != canonical(request["repo"]["worktree"]):
        raise ValueError("receipt repository binding does not match the request")
    if not isinstance(execution.get("exit_code"), int): raise ValueError("receipt must expose integer exit_code")
    if execution.get("status") == "SUCCESS" and execution.get("exit_code") != 0: raise ValueError("successful receipts require exit_code 0")
    error_code = execution.get("error_code")
    if execution.get("status") == "SUCCESS" and error_code is not None: raise ValueError("successful receipt cannot carry an error_code")
    if execution.get("status") != "SUCCESS" and error_code not in ERROR_CODES: raise ValueError("failed receipt must carry one recognized error_code")
    if execution.get("status") == "TIMED_OUT" and error_code != "TIMED_OUT": raise ValueError("normalized status and error_code disagree")
    worker_route = receipt.get("worker_route")
    if request["harness"] == "agy":
        if not isinstance(worker_route, dict) or worker_route != select_worker(error_code):
            raise ValueError("AGY receipt worker_route is not bound to the observed execution error")
    if worker_route is not None: validate_worker_route(worker_route)


def dump_document(path: str | Path, value: Any) -> None:
    import yaml
    target = Path(path)
    if target.is_symlink() or (target.exists() and target.stat().st_nlink > 1) or not target.parent.exists() or not target.parent.is_dir():
        raise ValueError("write path is unsafe")
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(canonical(target), flags, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(yaml.safe_dump(value, sort_keys=False))


@contextmanager
def disposable_runtime_root(parent: str | Path | None = None):
    """Create and remove one private runtime root owned by this harness."""
    root = Path(tempfile.mkdtemp(prefix="harness-worker-", dir=str(parent) if parent else None))
    try:
        yield root
    finally:
        if root.is_symlink():
            raise RuntimeError("runtime cleanup refused a symlink")
        shutil.rmtree(root, ignore_errors=False)


def valid_native_session_id(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip().upper() not in INVALID_NATIVE_SESSION_IDS


def read_registry(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        registry = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("SESSION_INVALID: local session registry is unreadable") from exc
    if not isinstance(registry, dict):
        raise ValueError("SESSION_INVALID: local session registry must be an object")
    for alias, binding in registry.items():
        if not isinstance(alias, str) or not alias.strip() or not isinstance(binding, dict) or not isinstance(binding.get("native_session_id"), str) or not binding["native_session_id"].strip():
            raise ValueError("SESSION_INVALID: local session registry entry is malformed")
        if binding.get("resumable") is not False and not valid_native_session_id(binding["native_session_id"]):
            raise ValueError("SESSION_INVALID: local session registry marks a sentinel session as resumable")
    return registry


def write_registry(path: Path, registry: dict) -> None:
    if path.exists() and path.stat().st_nlink > 1:
        raise ValueError("SESSION_INVALID: local session registry is a hardlink")
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(canonical(path), flags, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(json.dumps(registry, indent=2, sort_keys=True) + "\n")


def validate_output_path(path: str, request: dict) -> str:
    target = Path(path)
    if not target.is_absolute() or any(char in path for char in ('"', "\\", "\n", "\r", "\x00")):
        raise ValueError("output path must be absolute and free of unsafe syntax")
    roots = {Path(canonical(request["repo"]["root"])), Path(canonical(request["repo"]["worktree"]))}
    current = target.parent
    while current != current.parent:
        if current.is_symlink():
            # macOS exposes /var as a stable alias for /private/var; rejecting
            # that OS path would make ordinary tempfile output unusable.
            if not (sys.platform == "darwin" and current == Path("/var") and canonical(current) == canonical("/private/var")):
                raise ValueError("output path traverses a symlink")
        current = current.parent
    resolved = Path(canonical(target))
    if target.is_symlink() or (target.exists() and (not target.is_file() or target.stat().st_nlink > 1)) or any(resolved == root or root in resolved.parents for root in roots):
        raise ValueError("output path must not be a symlink or repository path")
    if not target.parent.exists() or not target.parent.is_dir():
        raise ValueError("output parent must already exist")
    return str(resolved)


def validate_output_targets(request: dict, registry: str, receipt: str | None = None) -> None:
    expected_registry = validate_output_path(request["outputs"]["registry"], request)
    if canonical(registry) != expected_registry:
        raise ValueError("registry path is outside the request output boundary")
    if receipt is not None:
        expected_receipt = validate_output_path(request["outputs"]["receipt"], request)
        if canonical(receipt) != expected_receipt:
            raise ValueError("receipt path is outside the request output boundary")
        if expected_registry == expected_receipt:
            raise ValueError("registry and receipt paths must differ")


def _status_paths(raw: bytes) -> set[str]:
    parts = [part for part in raw.split(b"\0") if part]
    paths: set[str] = set()
    index = 0
    while index < len(parts):
        entry = parts[index]
        index += 1
        if len(entry) < 4:
            continue
        paths.add(entry[3:].decode(errors="surrogateescape"))
        if entry[:2] in {b"R ", b" R", b"C ", b" C"} and index < len(parts):
            paths.add(parts[index].decode(errors="surrogateescape"))
            index += 1
    return paths


def execution_snapshot(repo: str) -> dict[str, str]:
    """Capture cheap Git/runtime state without hashing the whole worktree."""
    root = Path(canonical(repo))

    def git_bytes(*args: str) -> bytes:
        result = subprocess.run(["git", "-C", repo, *args], capture_output=True, check=False)
        if result.returncode:
            raise RuntimeError(result.stderr.decode(errors="replace").strip() or "cannot inspect Git state")
        return result.stdout

    status = git_bytes("status", "--porcelain=v1", "-z", "--untracked-files=all")
    ignored = git_bytes("status", "--porcelain=v1", "-z", "--ignored", "--untracked-files=all")
    snapshot = {
        "@git-status": hashlib.sha256(status).hexdigest(),
        "@git-ignored": hashlib.sha256(ignored).hexdigest(),
        "@git-diff": hashlib.sha256(git_bytes("diff", "--binary")).hexdigest(),
        "@git-index": hashlib.sha256(git_bytes("diff", "--cached", "--binary")).hexdigest(),
    }
    for relative in _status_paths(status) | _status_paths(ignored):
        target = root / relative
        if target.exists() or target.is_symlink():
            stat_result = target.lstat()
            payload = f"{stat_result.st_mode}:{stat_result.st_size}:{stat_result.st_mtime_ns}".encode()
            if target.is_symlink():
                payload += b"\0" + os.readlink(target).encode()
        else:
            payload = b"MISSING"
        diff = git_bytes("diff", "--binary", "--", relative) + git_bytes("diff", "--cached", "--binary", "--", relative)
        snapshot[f"@git-path:{relative}"] = hashlib.sha256(payload + b"\0" + diff).hexdigest()
    return snapshot


def repository_head(repo: str) -> str:
    return subprocess.check_output(["git", "-C", repo, "rev-parse", "HEAD"], text=True).strip()


def git_state(repo: str) -> str:
    head_ref = subprocess.run(["git", "-C", repo, "symbolic-ref", "-q", "HEAD"], capture_output=True, text=True, check=False).stdout.strip() or "DETACHED_HEAD"
    root = Path(canonical(repo))
    git_pointer = root / ".git"
    git_dir = Path(subprocess.check_output(["git", "-C", repo, "rev-parse", "--git-dir"], text=True).strip())
    common_dir = Path(subprocess.check_output(["git", "-C", repo, "rev-parse", "--git-common-dir"], text=True).strip())
    if not git_dir.is_absolute():
        git_dir = root / git_dir
    if not common_dir.is_absolute():
        common_dir = root / common_dir
    metadata = []
    for label, path in (("git-pointer", git_pointer), ("git-head", git_dir / "HEAD"), ("git-index", git_dir / "index"), ("git-commondir", git_dir / "commondir"), ("git-config", common_dir / "config"), ("git-common-head", common_dir / "HEAD")):
        metadata.append(label.encode() + b"\0" + (filesystem_payload(path) if path.exists() or path.is_symlink() else b"MISSING"))
    outputs = [
        subprocess.check_output(["git", "-C", repo, "diff", "--cached", "--binary"]),
        head_ref.encode(),
        repository_head(repo).encode(),
        *metadata,
    ]
    return hashlib.sha256(b"\0".join(outputs)).hexdigest()


def contains_symlink(path: Path, root: Path) -> bool:
    current = path
    while True:
        if current.is_symlink():
            if not (sys.platform == "darwin" and current == Path("/var") and canonical(current) == canonical("/private/var")):
                return True
        if current == root or current.parent == current or root not in current.parents:
            return False
        current = current.parent


def runtime_write_roots(request: dict) -> list[Path]:
    if request["harness"] not in NATIVE_TERMINAL_LANES:
        return []
    raw = os.environ.get("HEADLESS_CLI_RUNTIME_WRITE_ROOTS", "")
    if not raw:
        return []
    repo_roots = {Path(canonical(request["repo"][key])) for key in ("root", "worktree")}
    roots: list[Path] = []
    for value in raw.split(os.pathsep):
        target = Path(value)
        if not target.is_absolute() or contains_symlink(target, Path("/")) or not target.is_dir() or any(char in value for char in ('"', "\\", "\n", "\r", "\x00")):
            raise ValueError("runtime write roots must be absolute, existing, non-symlink directories")
        resolved = Path(canonical(target))
        if any(resolved == root or root in resolved.parents or resolved in root.parents for root in repo_roots):
            raise ValueError("runtime write roots must not overlap the repository worktree")
        roots.append(resolved)
    return roots


def validate_agy_launch_environment(request: dict) -> None:
    """Fail closed before AGY can hang inside an incomplete sandbox."""
    if request.get("harness") != "agy" or os.environ.get("HEADLESS_CLI_TEST_ONLY") == "1":
        return
    if os.environ.get("HEADLESS_CLI_ALLOW_NETWORK") != "1":
        raise RuntimeError("RUNTIME_UNAVAILABLE: AGY launch requires HEADLESS_CLI_ALLOW_NETWORK=1")
    if not runtime_write_roots(request):
        raise RuntimeError("RUNTIME_UNAVAILABLE: AGY launch requires HEADLESS_CLI_RUNTIME_WRITE_ROOTS")


def native_lane(request: dict) -> str | None:
    lane = request.get("harness")
    return lane if lane in NATIVE_TERMINAL_LANES else None


def is_native_command(command: list[str], lane: str) -> bool:
    return bool(command) and Path(command[0]).name == lane


def bind_delegation(request: dict) -> dict:
    """Consume the parent-rendered delegation binding before AGY invocation."""
    prompt = request.get("_delegation_prompt")
    binding = request.get("_delegation_binding")
    if request.get("harness") == "agy" and (not isinstance(prompt, str) or not prompt.strip() or not isinstance(binding, dict)):
        if os.environ.get("HEADLESS_CLI_TEST_ONLY") == "1":
            return request
        raise ValueError("DELEGATION_REQUIRED: AGY implementation dispatch requires a parent-rendered contract")
    if prompt is None and binding is None:
        return request
    if request.get("harness") not in {"agy", "fake"} or not isinstance(prompt, str) or not isinstance(binding, dict) or binding.get("profile") != "agy":
        raise ValueError("DELEGATION_INVALID: worker dispatch must consume the AGY renderer binding")
    if binding.get("version") != 1 or not re.fullmatch(r"[0-9a-f]{64}", str(binding.get("source_contract_sha256", ""))) or binding.get("rendered_prompt_sha256") != _digest(prompt):
        raise ValueError("DELEGATION_INVALID: renderer fingerprints do not bind the supplied prompt")
    contract = request.get("_delegation_contract")
    if request.get("harness") == "agy" and os.environ.get("HEADLESS_CLI_TEST_ONLY") != "1":
        if not isinstance(contract, dict) or _digest(contract) != binding.get("source_contract_sha256"):
            raise ValueError("DELEGATION_INVALID: renderer source contract is not bound")
    if request.get("harness") == "agy":
        index = 1
        command = request.get("command") or []
        while index < len(command):
            option = command[index]
            if option in AGY_DELEGATION_FLAGS:
                index += 1
            elif option in AGY_DELEGATION_OPTIONS:
                if index + 1 >= len(command) or command[index + 1].startswith("-"):
                    raise ValueError("DELEGATION_INVALID: AGY command has an incomplete bound option")
                index += 2
            else:
                raise ValueError("DELEGATION_INVALID: ad-hoc AGY prompt bypasses the rendered prompt")
    bound = dict(request)
    return bound


def append_delegated_prompt(command: list[str], request: dict) -> list[str]:
    prompt = request.get("_delegation_prompt")
    return [*command, prompt] if prompt is not None else command


def bind_native_command(command: list[str], request: dict, old: dict | None = None) -> list[str]:
    lane = native_lane(request)
    if lane is None or not is_native_command(command, lane):
        raise ValueError("RUNTIME_UNAVAILABLE: native terminal command does not match the requested lane")
    route = request["route_requirements"]
    if lane == "agy":
        if "--print" not in command and "-p" not in command:
            command = [*command, "--print"]
        command = _bind_option(command, "--output-format", "json")
        if route.get("requested_model"):
            command = _bind_option(command, "--model", str(route["requested_model"]))
        elif any(item == "--model" or item.startswith("--model=") for item in command):
            raise ValueError("native AGY model must be bound to the request")
        if route.get("requested_effort"):
            command = _bind_option(command, "--effort", str(route["requested_effort"]))
        elif any(item == "--effort" or item.startswith("--effort=") for item in command):
            raise ValueError("native AGY effort must be bound to the request")
    else:
        raise ValueError("RUNTIME_UNAVAILABLE: only AGY is an active native lane")
    resume_flags = {"--conversation", "--continue", "-c", "--resume", "-r", "--session", "--fork"}
    if any(item in resume_flags or item.startswith(("--conversation=", "--resume=", "--session=", "--fork=")) for item in command):
        raise ValueError("production native command must not prebind a session")
    if old:
        native_id = old.get("native_session_id")
        if not valid_native_session_id(native_id):
            raise ValueError("SESSION_INVALID: native lane has no exact resumable session")
        command = _bind_option(command, "--conversation" if lane == "agy" else "--resume", native_id)
    return command


def _bind_option(command: list[str], option: str, value: str) -> list[str]:
    if any(item.startswith(option + "=") for item in command):
        raise ValueError(f"production command must use a separate argv value for {option}")
    positions = [index for index, item in enumerate(command) if item == option]
    if len(positions) > 1:
        raise ValueError(f"production command repeats {option}")
    if not positions:
        return [*command, option, value]
    index = positions[0]
    if index + 1 >= len(command) or command[index + 1] != value:
        raise ValueError(f"production command must bind {option} to the request")
    return command


def executor_provenance(request: dict) -> dict[str, str]:
    command = request["command"]
    if request["harness"] == "fake":
        if os.environ.get("HEADLESS_CLI_TEST_ONLY") != "1":
            raise ValueError("fake harness requires explicit test-only guard")
        return {"kind": "test-harness", "executable": Path(command[0]).name}
    lane = native_lane(request)
    if lane is not None:
        if not is_native_command(command, lane):
            raise ValueError("RUNTIME_UNAVAILABLE: native terminal executable does not match the requested lane")
        resolved = shutil.which(command[0])
        if not resolved or not Path(resolved).is_file():
            raise ValueError(f"RUNTIME_UNAVAILABLE: {lane} executable is not resolvable")
        resolved_path = canonical(resolved)
        return {"kind": "native-terminal", "lane": lane, "executable": command[0], "resolved_executable": resolved_path, "executable_sha256": hashlib.sha256(Path(resolved_path).read_bytes()).hexdigest()}
    raise ValueError("RUNTIME_UNAVAILABLE: unsupported worker lane")


def run_bounded(command: list[str], *, cwd: str, timeout: int, env: dict[str, str], use_pty: bool = False) -> tuple[int, str, str]:
    master_fd = slave_fd = None
    if use_pty:
        if os.name == "nt":
            raise RuntimeError("RUNTIME_UNAVAILABLE: AGY PTY capture requires a POSIX host")
        import pty
        master_fd, slave_fd = pty.openpty()
        try:
            process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL, stdout=slave_fd, stderr=subprocess.PIPE, env=env, start_new_session=True)
        except BaseException:
            os.close(master_fd)
            os.close(slave_fd)
            raise
        os.close(slave_fd)
        slave_fd = None
        streams = [(master_fd, "stdout"), (process.stderr, "stderr")]
    else:
        process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, start_new_session=True)
        streams = [(process.stdout, "stdout"), (process.stderr, "stderr")]
    assert process.stderr is not None and all(stream is not None for stream, _ in streams)
    selector = selectors.DefaultSelector()
    for stream, label in streams:
        selector.register(stream, selectors.EVENT_READ, label)
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    deadline = time.monotonic() + timeout

    def terminate_group() -> None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (OSError, ProcessLookupError):
            try:
                process.kill()
            except OSError:
                pass

    def reap_after_kill() -> None:
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            try:
                process.kill()
            except OSError:
                pass
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass

    try:
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                terminate_group()
                reap_after_kill()
                raise TimeoutError("TIMED_OUT: native executor exceeded timeout")
            for key, _ in selector.select(min(remaining, 0.25)):
                try:
                    chunk = os.read(key.fileobj if isinstance(key.fileobj, int) else key.fileobj.fileno(), 65536)
                except OSError as exc:
                    if exc.errno != errno.EIO:
                        raise
                    chunk = b""
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                buffers[key.data].extend(chunk)
                if len(buffers["stdout"]) + len(buffers["stderr"]) > MAX_OUTPUT_BYTES:
                    terminate_group()
                    reap_after_kill()
                    raise ValueError("STRUCTURED_RESULT_INVALID: executor output exceeded the bounded receipt limit")
        try:
            exit_code = process.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired as exc:
            terminate_group()
            reap_after_kill()
            raise TimeoutError("TIMED_OUT: native executor exceeded timeout") from exc
        terminate_group()
        return exit_code, buffers["stdout"].decode(errors="replace"), buffers["stderr"].decode(errors="replace")
    finally:
        selector.close()
        process.stderr.close()
        if process.stdout is not None:
            process.stdout.close()
        if master_fd is not None:
            os.close(master_fd)
        if slave_fd is not None:
            os.close(slave_fd)


def request_session_alias(request: dict) -> str:
    explicit = request.get("session_alias")
    if explicit:
        return str(explicit)
    raw = f"{request['authority']['repository']}-{request['authority']['issue']}-{request['authority'].get('task', request['lane'])}"
    alias = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip("-._")
    if not alias:
        raise ValueError("SESSION_INVALID: request has no usable default session alias")
    return alias


def structured_command(request: dict) -> list[str]:
    return list(request["command"])


def parse_structured_output(stdout: str, request: dict, exit_code: int) -> dict:
    envelope = None
    for line in reversed(stdout.splitlines()):
        try:
            candidate = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, dict) and candidate.get("protocolVersion") == 1 and candidate.get("type") in {"result", "error"} and candidate.get("command") == "invoke" and candidate.get("exitCode") == exit_code:
            envelope = candidate
            break
    if isinstance(envelope, dict) and envelope.get("type") == "error":
        raise ValueError("EXECUTION_PROTOCOL_VIOLATION: structured test result envelope is missing or malformed")
    if not isinstance(envelope, dict) or envelope.get("command") != "invoke" or envelope.get("exitCode") != exit_code or not isinstance(envelope.get("data"), dict):
        raise ValueError("EXECUTION_PROTOCOL_VIOLATION: structured test result envelope is missing or malformed")
    data = envelope["data"]
    if request["harness"] != "fake" or not isinstance(data.get("runtime"), dict) or not isinstance(data.get("execution"), dict):
        raise ValueError("test harness result does not match the structured receipt schema")
    return data


def _native_receipt(request: dict, *, runtime: dict, error_code: str | None, limitations: list[str], usage: dict | None = None) -> dict:
    observed_usage = usage if isinstance(usage, dict) else {}
    return {
        "runtime": {
            "harness": native_lane(request) or request["harness"],
            "requested_route": requested_semantic_route(request),
            "actual_route": runtime.get("actual_route", "NOT_ASSESSED"),
            "requested_profile": request["route_requirements"].get("requested_profile") or request["route_requirements"].get("profile") or "NOT_ASSESSED",
            "resolved_profile": runtime.get("resolved_profile", "NOT_ASSESSED"),
            "provider": runtime.get("provider", "NOT_ASSESSED"),
            "actual_model": runtime.get("actual_model", "NOT_ASSESSED"),
            "actual_effort": runtime.get("actual_effort", "NOT_ASSESSED"),
            "native_session_id": runtime.get("native_session_id", "NOT_ASSESSED"),
        },
        "execution": {"status": "FAILED" if error_code else "SUCCESS", "error_code": error_code},
        "context": {"instruction_fingerprint": None, "skill_observation": "NOT_ASSESSED"},
        "usage": {field: observed_usage.get(field) for field in USAGE_FIELDS},
        "limitations": limitations,
    }


def _runtime_error_code(*, status: object = None, message: object = None, http_status: object = None) -> str | None:
    """Classify only a documented native error envelope, never model text."""
    code = str(status or "").strip().upper()
    if code in {"AUTH_REQUIRED", "QUOTA_EXHAUSTED", "RATE_LIMITED", "PERMISSION_DENIED", "SESSION_INVALID", "TIMED_OUT", "RUNTIME_UNAVAILABLE", "PROVIDER_UNAVAILABLE", "EXECUTION_FAILED"}:
        return code
    try:
        numeric = int(http_status)
    except (TypeError, ValueError):
        numeric = None
    text = str(message or "").lower()
    if numeric == 429:
        return "RATE_LIMITED"
    if numeric in {401, 403}:
        return "QUOTA_EXHAUSTED" if "insufficient balance" in text else "AUTH_REQUIRED"
    if any(token in text for token in ("unauthorized", "authentication", "missing bearer", "api key")):
        return "AUTH_REQUIRED"
    if "quota" in text or "exhausted" in text or "insufficient balance" in text:
        return "QUOTA_EXHAUSTED"
    if "rate limit" in text or "too many requests" in text:
        return "RATE_LIMITED"
    if "permission" in text or "denied" in text:
        return "PERMISSION_DENIED"
    if "session" in text:
        return "SESSION_INVALID"
    return None


def clean_terminal_output(value: str) -> str:
    """Remove PTY repaint/control bytes before parsing machine output."""
    return ANSI_ESCAPE.sub("", value).replace("\r", "\n")


def parse_agy_output(stdout: str, request: dict, exit_code: int, stderr: str = "") -> dict:
    """Parse only agy's documented top-level JSON envelope; response is opaque."""
    envelope = None
    for line in reversed(clean_terminal_output(stdout).splitlines()):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict):
            continue
        required = {"conversation_id", "status", "duration_seconds", "num_turns", "usage"}
        if required <= value.keys() and isinstance(value.get("conversation_id"), str) and isinstance(value.get("status"), str) and isinstance(value.get("usage"), dict):
            envelope = value
            break
    error_code = None
    if envelope is not None and envelope.get("status", "").upper() != "SUCCESS":
        error_code = _runtime_error_code(status=envelope.get("status")) or "EXECUTION_FAILED"
    elif exit_code != 0:
        error_code = _runtime_error_code(message=stderr) or "EXECUTION_FAILED"
    native_id = envelope.get("conversation_id") if envelope else None
    runtime = {"native_session_id": native_id if valid_native_session_id(native_id) else "NOT_ASSESSED"}
    return _native_receipt(request, runtime=runtime, error_code=error_code, usage=envelope.get("usage") if envelope else None, limitations=["agy exposes a conversation ID, not a provider/model qualification receipt"])


def parse_native_output(stdout: str, request: dict, exit_code: int, stderr: str = "") -> dict:
    """Dispatch to the lane parser; never recursively inspect native output."""
    if request["harness"] == "agy":
        return parse_agy_output(stdout, request, exit_code, stderr)
    raise ValueError("unsupported native parser lane")


def sandbox_command(command: list[str], request: dict) -> list[str]:
    test_executable = os.environ.get("HEADLESS_CLI_SANDBOX_EXECUTABLE") if request["harness"] == "fake" else None
    if test_executable:
        return [test_executable, "-p", "(test)", *command]
    if sys.platform != "darwin":
        raise RuntimeError("EXECUTION_BOUNDARY_UNAVAILABLE: bounded execution requires a native OS sandbox")
    sandbox = ["(version 1)", "(deny default)", "(allow process-exec)", "(allow process-fork)", "(allow signal (target self))", "(allow sysctl-read)", "(allow mach-lookup)", "(allow file-read*)"]
    if request["permission_policy"] == "bounded-write":
        raw_root = Path(request["repo"]["worktree"]).absolute()
        root = canonical(raw_root)
        if any(char in root for char in ('"', "\\", "\n", "\r", "\x00")):
            raise ValueError("repo root contains unsafe sandbox syntax")
        for relative in request["scope"]["allowed_paths"]:
            relative_path = Path(relative)
            if not relative or relative_path == Path(".") or relative_path.is_absolute() or ".." in relative_path.parts or any(char in relative for char in ('"', "\\", "\n", "\r", "\x00")):
                raise ValueError(f"invalid bounded-write path: {relative!r}")
            if is_git_metadata_path(relative_path):
                raise ValueError(f"bounded-write path cannot target .git metadata: {relative!r}")
            raw_target = raw_root / relative_path
            if contains_symlink(raw_target, raw_root):
                raise ValueError(f"bounded-write path traverses a symlink: {relative!r}")
            target = canonical(raw_target)
            if any(char in target for char in ('"', "\\", "\n", "\r", "\x00")):
                raise ValueError(f"bounded-write target contains unsafe sandbox syntax: {relative!r}")
            if target != root and not target.startswith(root + os.sep):
                raise ValueError(f"bounded-write path escapes repo root: {relative!r}")
            rule = "subpath" if relative.endswith("/") or Path(target).is_dir() else "literal"
            sandbox.append(f'(allow file-write* ({rule} "{target}"))')
    if request["harness"] in NATIVE_TERMINAL_LANES:
        for root in runtime_write_roots(request):
            sandbox.append(f'(allow file-write* (subpath "{root}"))')
        if request["harness"] == "agy":
            # agy starts a localhost language-server sidecar even for print mode.
            sandbox.append("(allow network-inbound)")
        if os.environ.get("HEADLESS_CLI_ALLOW_NETWORK") == "1":
            sandbox.append("(allow network-outbound)")
    return ["sandbox-exec", "-p", " ".join(sandbox), *command]


def runtime_environment(request: dict, old: dict | None) -> dict[str, str]:
    """Pass only runtime inputs, never the caller's complete environment."""
    names = {"PATH", "HOME", "TMPDIR", "TMP", "TEMP", "LANG", "LC_ALL", "TERM"}
    if request["harness"] == "agy":
        names |= {"XDG_CONFIG_HOME", "XDG_CACHE_HOME", "AGY_HOME", "HEADLESS_CLI_RUNTIME_WRITE_ROOTS", "HEADLESS_CLI_ALLOW_NETWORK"}
    elif request["harness"] == "fake":
        names |= {"MODE", "NATIVE_ID", "HEADLESS_CLI_TEST_ONLY"}
    environment = {name: os.environ[name] for name in names if name in os.environ}
    environment["HEADLESS_SESSION_ID"] = old["native_session_id"] if old else ""
    return environment


def normalize(raw: dict, request: dict, *, session_state: str, exit_code: int, stdout: str, stderr: str, duration_ms: int, provenance: dict | None = None) -> dict:
    runtime = raw.get("runtime") or {}
    execution = raw.get("execution") or {}
    expected_route = requested_semantic_route(request)
    observed_route = runtime.get("requested_route") if isinstance(runtime, dict) else None
    legacy_route = request["route_requirements"].get("semantic_route") is None and observed_route == request["route_requirements"].get("semantic_complexity")
    if not isinstance(runtime, dict) or (observed_route != expected_route and not legacy_route):
        raise ValueError("runtime did not expose the requested semantic route")
    native_id = runtime.get("native_session_id") or raw.get("native_session_id")
    if not isinstance(native_id, str) or not native_id.strip():
        raise ValueError("runtime did not expose exact native_session_id")
    runtime = {**runtime, "actual_model": runtime.get("actual_model") or "NOT_ASSESSED", "actual_effort": runtime.get("actual_effort") or "NOT_ASSESSED"}
    status = execution.get("status") or ("SUCCESS" if exit_code == 0 else "FAILED")
    if exit_code != 0 and status == "SUCCESS":
        status = "FAILED"
    if status != "SUCCESS":
        status = "TIMED_OUT" if status == "TIMED_OUT" else "FAILED"
    if status == "SUCCESS" and request["harness"] == "fake" and not valid_native_session_id(native_id):
        raise ValueError("successful runtime must expose a resumable native_session_id")
    error_code = execution.get("error_code")
    if exit_code == 0 and status == "SUCCESS":
        error_code = None
    elif not error_code:
        error_code = "TIMED_OUT" if status == "TIMED_OUT" else "EXECUTION_FAILED"
    context = dict(raw.get("context") or {"instruction_fingerprint": None, "skill_observation": "NOT_ASSESSED"})
    context["effective_context"] = effective_context(request["repo"]["root"], request["repo"]["cwd"], request["expected_context"].get("required_skills", []))
    worker_route = raw.get("worker_route") or request.get("worker_route")
    if request["harness"] == "agy":
        expected_worker_route = select_worker(error_code)
        if worker_route is not None and worker_route != expected_worker_route:
            raise ValueError("runtime worker_route is not bound to the observed execution error")
        worker_route = expected_worker_route
    if worker_route is not None:
        validate_worker_route(worker_route)
    fallback_required = "prometheus" if worker_route and worker_route["fallback_triggered"] and worker_route["actual_worker"] == "agy" else None
    observed_usage = raw.get("usage") if isinstance(raw.get("usage"), dict) else {}
    usage = {field: observed_usage.get(field) for field in USAGE_FIELDS}
    if usage["latency_ms"] is None:
        usage["latency_ms"] = duration_ms
    return {
        "version": 1,
        "request_id": request["request_id"],
        **({"fallback_required": fallback_required} if fallback_required else {}),
        **({"worker_route": worker_route} if worker_route is not None else {}),
        "runtime": {"harness": runtime.get("harness", request["harness"]), "executor_provenance": provenance or executor_provenance(request), "requested_route": expected_route, "actual_route": runtime.get("actual_route", expected_route if request["harness"] == "fake" else "NOT_ASSESSED"), "requested_profile": runtime.get("requested_profile", request["route_requirements"].get("requested_profile") or request["route_requirements"].get("profile") or "NOT_ASSESSED"), "resolved_profile": runtime.get("resolved_profile", "NOT_ASSESSED"), "provider": runtime.get("provider", "fake" if request["harness"] == "fake" else "NOT_ASSESSED"), "actual_model": runtime.get("actual_model"), "actual_effort": runtime.get("actual_effort"), "native_session_id": str(native_id), "session_state": session_state},
        "execution": {"repo_root": canonical(request["repo"]["root"]), "cwd": canonical(request["repo"]["cwd"]), "worktree": canonical(request["repo"]["worktree"]), "permission_observation": runtime.get("permission_observation", "not_assessed"), "status": status, "error_code": error_code, "exit_code": exit_code, "duration_ms": duration_ms},
        "context": context,
        "usage": usage,
        "capacity": raw.get("capacity", {"state": "UNKNOWN", "source": "none"}),
        "limitations": list(raw.get("limitations", [])) + (["stderr was emitted"] if stderr else []),
        **({"delegation": request["_delegation_binding"]} if request.get("_delegation_binding") else {}),
    }


def _run_once(request: dict, registry_path: Path, timeout: int) -> dict:
    request = bind_delegation(request)
    validate_harness_request(request)
    validate_agy_launch_environment(request)
    alias = request_session_alias(request)
    registry = read_registry(registry_path)
    old = registry.get(alias)
    repo = request["repo"]
    validate_output_targets(request, str(registry_path))
    command = request.get("command")
    binding = {"alias": alias, "repository": request["authority"]["repository"], "issue": request["authority"]["issue"], "task": request["authority"].get("task"), "lane": request["lane"], "repo_path": canonical(repo["root"]), "worktree": canonical(repo["worktree"]), "cwd": canonical(repo["cwd"]), "git_identity": {"repository": git_worktree_identity(repo["root"]), "worktree": git_worktree_identity(repo["worktree"])}, "context_binding": effective_context(repo["root"], repo["cwd"], request["expected_context"].get("required_skills", [])), "harness": request["harness"], "permission_policy": request["permission_policy"], "scope": request["scope"], "route_requirements": request["route_requirements"], "expected_context": request["expected_context"], **({"delegation": request["_delegation_binding"]} if request.get("_delegation_binding") else {})}
    policy = request["session"]["policy"]
    if old:
        if old.get("resumable") is False:
            if policy != "rebind":
                raise ValueError("SESSION_INVALID: failed session has no exact native session; rebind is required")
            old = None
        if old:
            for key in ("repository", "issue", "task", "lane", "repo_path", "worktree", "cwd", "git_identity", "context_binding", "harness", "permission_policy", "scope", "route_requirements", "expected_context", "delegation"):
                if old.get(key) != binding.get(key):
                    if policy != "rebind":
                        raise ValueError(f"SESSION_CONTEXT_MISMATCH: {key}")
                    old = None
                    break
        if old and policy == "fresh":
            raise ValueError("SESSION_INVALID: fresh request collides with saved session")
    elif policy == "resume":
        raise ValueError("SESSION_INVALID: exact saved session is absent")
    session_state = "resumed" if old else ("rebound" if policy == "rebind" else "fresh")
    provenance = executor_provenance(request)
    if Path(command[0]).name in {"sh", "bash", "zsh", "fish", "cmd", "powershell", "pwsh"}:
        raise ValueError("shell command execution is not an accepted boundary")
    unsafe_flags = {"yolo", "--yolo", "--trust", "--force", "--bypass"}
    if any("dangerously" in item or item in unsafe_flags or any(item.startswith(flag + "=") for flag in unsafe_flags if flag.startswith("--")) for item in command):
        raise ValueError("unsafe approval/bypass flag is not an accepted boundary")
    command = structured_command(request)
    if request["harness"] in NATIVE_TERMINAL_LANES:
        command = bind_native_command(command, request, old)
        command[0] = provenance["resolved_executable"]
    command = append_delegated_prompt(command, request)
    command = sandbox_command(command, request)
    before_snapshot = execution_snapshot(repo["worktree"])
    before_snapshot["@git-state"] = git_state(repo["worktree"])
    before_head = repository_head(repo["worktree"])
    start = time.monotonic()
    proc = None
    timeout_error = None
    try:
        process_exit_code, process_stdout, process_stderr = run_bounded(command, cwd=canonical(repo["cwd"]), timeout=timeout, env=runtime_environment(request, old), use_pty=request["harness"] == "agy")
    except (TimeoutError, subprocess.TimeoutExpired) as exc:
        timeout_error = RuntimeError("TIMED_OUT: native executor exceeded timeout")
    duration_ms = int((time.monotonic() - start) * 1000)
    after_snapshot = execution_snapshot(repo["worktree"])
    after_snapshot["@git-state"] = git_state(repo["worktree"])
    if repository_head(repo["worktree"]) != before_head:
        raise ValueError("EXECUTION_BOUNDARY_VIOLATION: executor changed repository HEAD")
    changed = {path for path in before_snapshot.keys() | after_snapshot.keys() if before_snapshot.get(path) != after_snapshot.get(path)}
    if request["permission_policy"] == "read-only" and changed:
        raise ValueError(f"MUTATION_SCOPE_VIOLATION: read-only execution changed {sorted(changed)}")
    if request["permission_policy"] == "bounded-write":
        allowed = request["scope"]["allowed_paths"]
        changed_paths = {path.removeprefix("@git-path:") for path in changed if path.startswith("@git-path:")}
        if any(not path_matches_allowance(path, allowed, repo["worktree"]) for path in changed_paths):
            raise ValueError(f"MUTATION_SCOPE_VIOLATION: {sorted(changed)}")
    process_exit_code = 124 if timeout_error else process_exit_code
    process_stdout = "" if timeout_error else process_stdout
    process_stderr = "" if timeout_error else process_stderr
    if timeout_error:
        raw = {
            "runtime": {"harness": request["harness"], "requested_route": requested_semantic_route(request), "actual_route": "NOT_ASSESSED", "requested_profile": request["route_requirements"].get("requested_profile") or request["route_requirements"].get("profile") or "NOT_ASSESSED", "resolved_profile": "NOT_ASSESSED", "provider": "NOT_ASSESSED", "actual_model": "NOT_ASSESSED", "actual_effort": "NOT_ASSESSED", "native_session_id": old.get("native_session_id") if old else "NOT_ASSESSED"},
            "execution": {"status": "TIMED_OUT", "error_code": "TIMED_OUT"},
            "context": {"instruction_fingerprint": None, "skill_observation": "NOT_ASSESSED"},
            "limitations": [str(timeout_error)],
        }
    else:
        raw = parse_structured_output(process_stdout, request, process_exit_code) if request["harness"] == "fake" else parse_native_output(process_stdout, request, process_exit_code, process_stderr)
    receipt = normalize(raw, request, session_state=session_state, exit_code=process_exit_code, stdout=process_stdout, stderr=process_stderr, duration_ms=duration_ms)
    validate_harness_receipt(request, receipt)
    if old and receipt["runtime"]["native_session_id"] != old["native_session_id"]:
        raise ValueError("SESSION_INVALID: resumed runtime returned a different native_session_id")
    binding["native_session_id"] = receipt["runtime"]["native_session_id"]
    binding["status"] = "resumable" if process_exit_code == 0 else "failed"
    binding["resumable"] = valid_native_session_id(receipt["runtime"]["native_session_id"])
    binding["last_used_at"] = time.time()
    registry[alias] = binding
    write_registry(registry_path, registry)
    return receipt


def _availability_error_code(error: BaseException) -> str | None:
    message = str(error).strip().upper()
    for code in sorted(WORKER_AVAILABILITY_FAILURES, key=len, reverse=True):
        if message == code or message.startswith(f"{code} ") or message.startswith(f"{code}:"):
            return code
    return None


def _prelaunch_availability_receipt(request: dict, *, reason: str, error: BaseException) -> dict:
    policy = request["session"]["policy"]
    session_state = {"fresh": "fresh", "resume_or_start": "fresh", "resume": "resumed", "rebind": "rebound"}[policy]
    raw = {
        "runtime": {"harness": "agy", "requested_route": requested_semantic_route(request), "actual_route": "NOT_ASSESSED", "requested_profile": request["route_requirements"].get("requested_profile") or request["route_requirements"].get("profile") or "NOT_ASSESSED", "resolved_profile": "NOT_ASSESSED", "provider": "NOT_ASSESSED", "actual_model": "NOT_ASSESSED", "actual_effort": "NOT_ASSESSED", "native_session_id": "NOT_ASSESSED"},
        "execution": {"status": "FAILED", "error_code": reason},
        "context": {"instruction_fingerprint": None, "skill_observation": "NOT_ASSESSED"},
        "limitations": [f"AGY pre-launch availability failure: {str(error)[:1000]}"],
    }
    receipt = normalize(raw, request, session_state=session_state, exit_code=1, stdout="", stderr="", duration_ms=0, provenance={"kind": "native-terminal", "lane": "agy", "executable": Path(request["command"][0]).name, "resolved_executable": "NOT_ASSESSED", "executable_sha256": "NOT_ASSESSED"})
    validate_harness_receipt(request, receipt)
    return receipt


def run(request: dict, registry_path: Path, timeout: int) -> dict:
    """Run AGY; return a parent-owned Prometheus fallback decision on availability only."""
    try:
        receipt = _run_once(request, registry_path, timeout)
    except (ValueError, RuntimeError) as error:
        reason = _availability_error_code(error)
        if request.get("harness") != "agy" or reason is None:
            raise
        return _prelaunch_availability_receipt(request, reason=reason, error=error)
    reason = (receipt.get("execution") or {}).get("error_code")
    if request.get("harness") == "agy" and reason in WORKER_AVAILABILITY_FAILURES:
        receipt["worker_route"] = select_worker(reason)
        receipt["fallback_required"] = "prometheus"
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run"); run_parser.add_argument("--request", required=True); run_parser.add_argument("--registry", required=True); run_parser.add_argument("--receipt", required=True); run_parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    try:
        request = load_document(args.request)
        validate_output_targets(request, str(args.registry), args.receipt)
        receipt = run(request, Path(args.registry), args.timeout)
        dump_document(args.receipt, receipt); print(json.dumps(receipt, sort_keys=True)); return 0
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
