#!/usr/bin/env python3
"""Validate and run the bounded skill-creator evaluation contract."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import time
from typing import Iterator
import uuid

import yaml


GATES = {
    "G0_NECESSITY",
    "G1_STRUCTURE",
    "G2_PROVENANCE",
    "G3_ROUTING",
    "G4_BEHAVIOR",
    "G5_COEXISTENCE",
    "G6_EFFICIENCY",
    "G7_INDEPENDENT_REVIEW",
}
PARTITIONS = {"must_pass", "regression", "held_out"}
KINDS = {"routing", "CREATE", "INSTALL", "UPDATE", "AUDIT", "EVALUATE"}
ACTIONS = {"create", "install", "update", "audit"}
PROCESS_ITEM_TYPES = {"command_execution", "custom_tool_call", "function_call", "mcp_tool_call", "tool_call"}
ACTION_DISPOSITIONS = {
    "USE_EXISTING", "INSTALL_EXISTING", "REFERENCE_AND_ADAPT", "CLONE_AND_ADAPT", "UPDATE_EXISTING", "LOCALIZE", "MERGE",
    "DISABLE_IMPLICIT", "RETIRE", "REJECT", "CREATE_FROM_SCRATCH_WITH_JUSTIFICATION", "BLOCKED",
    "HEALTHY", "UPDATE_NEEDED",
}
EVALUATION_DISPOSITIONS = {"PASS", "REJECT", "SIMPLIFY"}
NECESSITY_STATES = {"CHECKED", "NOT_AVAILABLE", "NOT_RELEVANT"}
ORIGIN_TYPES = {"observed_failure", "user_requirement", "upstream_change", "model_change", "architecture_contract"}
EXPECTED_CASE_COUNT = 31
EXPECTED_ROUTING_CASE_COUNT = 12
EXPECTED_LIFECYCLE_CASE_COUNT = 19
BINDING_VERSION = 1
SNAPSHOT_DIR_PREFIX = "\0dir/"
SNAPSHOT_CONTENT_PREFIX = "\0content/"
TRIAL_SEQUENCE = ["ALLOCATE", "PREPARE", "BASELINE", "RUN", "FREEZE", "REPORT", "ARCHIVE", "CLEAN"]
TRIAL_TERMINAL_STATES = {"CLEANED", "PRESERVED_FOR_REVIEW", "CLEANUP_BLOCKED"}
EXPECTED_PARTITIONS = {
    "must_pass": frozenset({
        "route-explicit-positive", "route-implicit-positive", "route-contextual-positive",
        "route-explicit-negative", "route-adjacent-negative", "route-sibling-negative",
        "create-local-upstream", "create-multimode-one-skill", "update-bounded", "evaluate-good",
        "install-healthy-copy", "install-owned-lifecycle",
    }),
    "regression": frozenset({
        "create-no-skill", "update-substantive", "audit-upstream-drift", "audit-retire",
        "evaluate-broad-description", "evaluate-decorative-resources",
        "install-collision-refused", "install-redesign-routed",
    }),
    "held_out": frozenset({
        "route-ambiguous-positive", "route-noisy-positive", "route-agents-negative",
        "route-script-negative", "route-native-negative", "route-noisy-negative",
        "audit-overlap", "audit-localize", "evaluate-sibling-collision", "evaluate-skipped-process",
        "install-zero-adaptation",
    }),
}
EXPECTED_CASE_IDS = frozenset().union(*EXPECTED_PARTITIONS.values())
EXPECTED_FILES = {
    "SKILL.md", "license.txt", "evals/cases.yaml",
    "workflows/create.md", "workflows/install.md", "workflows/audit.md", "workflows/update.md",
    "references/architecture.md", "references/authoring.md", "references/discovery.md",
    "references/source-strategy.md", "references/review.md", "references/validation.md",
    "references/evaluation.md", "references/test-environment.md", "references/qualification.md",
    "references/provenance.md", "references/routing.md",
    "scripts/generate_openai_yaml.py", "scripts/init_skill.py", "scripts/quick_validate.py",
    "scripts/test_validate_eval_cases.py", "scripts/validate_eval_cases.py",
}
UPSTREAM_MARKERS = (
    "Repository: `openai/codex`",
    "Ref: `dee21ec1bc26cdf9f3c4d77a17706cd19dcf05de`",
    "Source path: `codex-rs/skills/src/assets/samples/skill-creator/`",
    "License: Apache-2.0",
    "Baseline commit: `bb288fd`",
    "`scripts/generate_openai_yaml.py`, `870eefcea9bd0184806b8eb305526e883d2f7241`",
    "`scripts/init_skill.py`, `2ed2fa3125c720fcce60a29f3dd82d04b14d9fa0`",
    "`scripts/quick_validate.py`, `e27023ece4bd259ef36560e19995eec7b6a345bf`",
    "`license.txt`, `d645695673349e3947e8e5ae42332d0ac3164cd7`",
)


def _subprocess_env() -> dict[str, str]:
    """Keep inherited credentials/config, but never inherited Git routing state."""
    environment = os.environ.copy()
    for name in list(environment):
        if name.startswith("GIT_"):
            environment.pop(name, None)
    return environment


def load_cases(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError("evaluation file must contain a mapping")
    return data


def _cases_for_stage(data: dict, stage: str, case_ids: set[str] | None) -> list[dict]:
    stage_ids = {
        "smoke": {"route-explicit-positive", "route-implicit-positive", "route-explicit-negative"},
        "lifecycle": {
            "route-explicit-positive", "route-implicit-positive", "route-explicit-negative",
            "create-local-upstream", "update-bounded", "audit-overlap", "evaluate-good",
            "install-owned-lifecycle",
        },
        "full": {case["id"] for case in data["cases"]},
    }[stage]
    return [case for case in data["cases"] if case["id"] in stage_ids and (not case_ids or case["id"] in case_ids)]


def validate(path: Path) -> list[str]:
    try:
        data = load_cases(path)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError) as exc:
        return [str(exc)]
    errors: list[str] = []
    if data.get("schema_version") != 2 or data.get("skill") != "skill-creator":
        errors.append("schema_version 2 and skill skill-creator are required")
    gates = data.get("gates")
    if not isinstance(gates, list):
        errors.append("gates must be a list")
    else:
        gate_ids = {item.get("id") for item in gates if isinstance(item, dict)}
        errors.extend(f"missing gate: {gate}" for gate in sorted(GATES - gate_ids))
        if gate_ids - GATES:
            errors.append("gates contain an unknown id")
    cases = data.get("cases")
    if not isinstance(cases, list):
        return errors + ["cases must be a list"]
    seen: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"case {index} must be a mapping")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"case {index} requires id")
        elif case_id in seen:
            errors.append(f"duplicate case id: {case_id}")
        else:
            seen.add(case_id)
        if case.get("kind") not in KINDS:
            errors.append(f"{case_id}: kind must be one of {sorted(KINDS)}")
        if case.get("partition") not in PARTITIONS:
            errors.append(f"{case_id}: partition must be one of {sorted(PARTITIONS)}")
        if case.get("gate") not in GATES:
            errors.append(f"{case_id}: gate is invalid")
        case_gates = case.get("gates", [case.get("gate")])
        if not isinstance(case_gates, list) or not case_gates or any(gate not in GATES for gate in case_gates):
            errors.append(f"{case_id}: gates must contain only known gate ids")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            errors.append(f"{case_id}: prompt is required")
        if not isinstance(case.get("expected"), str) or not case["expected"].strip():
            errors.append(f"{case_id}: expected outcome is required")
        origin = case.get("origin")
        if (
            not isinstance(origin, dict)
            or origin.get("type") not in ORIGIN_TYPES
            or not isinstance(origin.get("source"), str)
            or not origin["source"].strip()
        ):
            errors.append(f"{case_id}: origin.type and non-empty origin.source are required")
        if case.get("kind") == "routing" and case.get("polarity") not in {"positive", "negative"}:
            errors.append(f"{case_id}: routing polarity must be positive or negative")
        if case.get("kind") != "routing" and not isinstance(case.get("trace_markers"), list):
            errors.append(f"{case_id}: lifecycle cases require trace_markers")
        if case.get("kind") == "INSTALL":
            outcome = case.get("installation_outcome")
            if outcome not in {"INSTALLED", "BLOCKED", "ROUTE"}:
                errors.append(f"{case_id}: INSTALL case requires installation_outcome INSTALLED, BLOCKED, or ROUTE")
            if outcome == "INSTALLED":
                source_fixture = case.get("source_fixture")
                package_files = case.get("package_files")
                if not all(isinstance(case.get(key), str) and case[key].strip() for key in ("source_repository", "source_ref", "source_license")):
                    errors.append(f"{case_id}: installed case must pin expected source repository, ref, and license")
                if not isinstance(case.get("source_revision"), str) or not re.fullmatch(r"[0-9a-f]{40}", case["source_revision"]):
                    errors.append(f"{case_id}: installed case must pin the expected immutable source revision")
                if not isinstance(source_fixture, str) or not _safe_relative_posix_path(source_fixture):
                    errors.append(f"{case_id}: installed case source_fixture must stay inside the fixture")
                if (
                    not isinstance(package_files, list)
                    or not package_files
                    or any(not isinstance(path, str) or not _safe_relative_posix_path(path) for path in package_files)
                    or len(package_files) != len(set(package_files))
                ):
                    errors.append(f"{case_id}: installed case package_files must be non-empty relative paths")
                if (
                    case.get("artifact") != "created"
                    or not isinstance(case.get("artifact_path"), str)
                    or not _safe_relative_posix_path(case["artifact_path"])
                    or not isinstance(case.get("side_effects"), list)
                    or not case["side_effects"]
                    or sum(
                        isinstance(effect, dict)
                        and isinstance(effect.get("path"), str)
                        and effect["path"].endswith("/SKILL.md")
                        for effect in case["side_effects"]
                    ) != 1
                    or len({effect.get("path") for effect in case["side_effects"] if isinstance(effect, dict)}) != len(case["side_effects"])
                    or any(
                        not isinstance(effect, dict)
                        or effect.get("operation") != "created"
                        or not isinstance(effect.get("path"), str)
                        or not _safe_relative_posix_path(effect["path"])
                        for effect in case["side_effects"]
                    )
                ):
                    errors.append(f"{case_id}: installed case requires a report artifact and explicit installed-file side effects")
            elif case.get("artifact") != "none":
                errors.append(f"{case_id}: blocked/routed install case must declare artifact none")
    routing = [case for case in cases if isinstance(case, dict) and case.get("kind") == "routing"]
    if seen != EXPECTED_CASE_IDS:
        errors.append(f"case ids must match the canonical {EXPECTED_CASE_COUNT}-case corpus")
    for partition, expected_ids in EXPECTED_PARTITIONS.items():
        actual_ids = {case.get("id") for case in cases if isinstance(case, dict) and case.get("partition") == partition}
        if actual_ids != expected_ids:
            errors.append(f"{partition} partition does not match the canonical corpus")
    if len(routing) < 10:
        errors.append("routing corpus requires at least 10 realistic prompts")
    if not any(case.get("partition") == "held_out" for case in cases if isinstance(case, dict)):
        errors.append("evaluation requires a held-out partition")
    if not any(case.get("paired") is True for case in cases if isinstance(case, dict)):
        errors.append("evaluation requires at least one paired with/without-skill case")
    action_cases = data.get("action_cases")
    if not isinstance(action_cases, list) or {case.get("id") for case in action_cases if isinstance(case, dict)} != {
        "explicit-create", "explicit-update", "explicit-install", "explicit-audit", "unknown-action", "ambiguous-lifecycle",
    }:
        errors.append("action_cases must cover the four actions, unknown action, and ambiguity")
    for case in action_cases or []:
        if not isinstance(case, dict) or not isinstance(case.get("prompt"), str) or not isinstance(case.get("expected"), str):
            errors.append("action cases require prompt and expected fields")
        elif case.get("action") in ACTIONS and not case["expected"].startswith("workflows/"):
            errors.append(f"{case.get('id')}: valid action must point to one workflow")
    return errors


def _text_from_event(event: dict) -> str:
    item = event.get("item")
    if not isinstance(item, dict):
        return ""
    value = item.get("text") or item.get("content")
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(part.get("text", "") for part in value if isinstance(part, dict))
    return ""


def _events(stdout: str) -> list[dict]:
    result = []
    for line in stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            result.append(value)
    return result


def _final_text(events: list[dict]) -> str:
    texts = [_text_from_event(event) for event in events]
    return next((text for text in reversed(texts) if text), "")


def _json_object(text: str) -> dict:
    cleaned = text.strip().strip("`").strip()
    if cleaned.startswith("json"):
        cleaned = cleaned[4:].strip()
    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", cleaned):
        try:
            value, _ = decoder.raw_decode(cleaned[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return {}


def _is_skill_creator_name(value: object) -> bool:
    if isinstance(value, str):
        name = value.strip().rstrip("/")
        return name == "skill-creator" or name.endswith("/skill-creator")
    if isinstance(value, dict):
        return any(_is_skill_creator_name(value.get(key)) for key in ("name", "skill", "id", "path"))
    return False


def _runtime_activation(events: list[dict]) -> str | None:
    """Return loaded/unloaded only from an explicit structured activation event."""
    observed: list[str] = []
    for event in events:
        for key in ("skill_loads", "loaded_skills", "loaded_skill"):
            if key not in event:
                continue
            value = event[key]
            if isinstance(value, list):
                observed.append("loaded" if any(_is_skill_creator_name(item) for item in value) else "unloaded")
                continue
            if _is_skill_creator_name(value):
                observed.append("loaded")
            elif isinstance(value, (str, dict)):
                observed.append("unloaded")
    if "loaded" in observed and any(state == "unloaded" for state in observed[observed.index("loaded") + 1:]):
        return None
    if "loaded" in observed:
        return "loaded"
    return "unloaded" if "unloaded" in observed else None


def _routing_status(case: dict, activation: str | None, observed: object) -> tuple[str, str]:
    if activation is None:
        return "NOT_ASSESSED", "runtime did not expose an explicit activation signal"
    expected_activation = "unloaded" if case.get("expected") == "none" else "loaded"
    if activation != expected_activation:
        return "FAIL", f"expected explicit {expected_activation} activation, observed {activation}"
    if observed != case.get("expected"):
        return "FAIL", f"expected {case['expected']}, observed {observed!r}"
    return "PASS", "expected outcome and explicit activation state observed"


def _process_observed(events: list[dict]) -> bool:
    """Require an execution/tool trace before claiming behavioral evidence."""
    for event in events:
        item = event.get("item")
        item_type = item.get("type") if isinstance(item, dict) else event.get("type")
        if item_type in PROCESS_ITEM_TYPES:
            return True
    return False


def _trace_matches(case: dict, events: list[dict]) -> bool:
    markers = case.get("trace_markers", [])
    if case.get("id") == "install-owned-lifecycle":
        observed = [event.get("runner_stage") for event in events if isinstance(event, dict) and event.get("runner_stage")]
        expected = [
            "after_initial_install", "after_same_revision", "after_changed_revision",
            "after_local_edit", "after_uninstall", "neighbor_preserved", "after_final_reinstall",
        ]
        cursor = -1
        for stage in expected:
            try:
                cursor = observed.index(stage, cursor + 1)
            except ValueError:
                return False
        return True
    payloads = [_process_payload(event) for event in events]
    for marker in markers:
        if not any(marker.lower() in payload for payload in payloads):
            return False
    return True


def _process_payload(event: dict) -> str:
    item = event.get("item") if isinstance(event.get("item"), dict) else event
    item_type = item.get("type") if isinstance(item, dict) else None
    if item_type not in PROCESS_ITEM_TYPES:
        return ""
    fields = {key: item.get(key) for key in ("command", "name", "arguments", "input", "call_id", "tool", "function", "output", "aggregated_output") if key in item}
    return json.dumps(fields, sort_keys=True).lower()


def _process_events(events: list[dict]) -> list[dict]:
    return [event for event in events if _process_payload(event)]


def _usage_tokens(events: list[dict]) -> int | None:
    total = 0
    observed = False
    for event in events:
        usage = event.get("usage")
        if not isinstance(usage, dict):
            response = event.get("response")
            usage = response.get("usage") if isinstance(response, dict) else None
        if not isinstance(usage, dict):
            continue
        values = [usage.get(key) for key in ("total_tokens", "input_tokens", "output_tokens")]
        numbers = [value for value in values if isinstance(value, int)]
        if numbers:
            observed = True
            total += usage.get("total_tokens") if isinstance(usage.get("total_tokens"), int) else sum(numbers)
    return total if observed else None


def _cost_metrics(events: list[dict], changed_paths: set[str]) -> dict:
    process_events = _process_events(events)
    commands = sum(
        1 for event in process_events
        if (event.get("item", event).get("type") if isinstance(event.get("item", event), dict) else None) == "command_execution"
    )
    tokens = _usage_tokens(events)
    return {
        "tool_calls": len(process_events),
        "command_count": commands,
        "token_count": tokens,
        "artifact_count": len(changed_paths),
        "tokens_observed": tokens is not None,
    }


def _snapshot_path_excluded(relative: Path) -> bool:
    return bool(
        {".codex-home", ".git", "__pycache__"}.intersection(relative.parts)
        or relative.suffix == ".pyc"
    )


def _snapshot(root: Path) -> dict[str, str]:
    entries: dict[str, str] = {}

    def fingerprint(path: Path) -> str:
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            payload = b"symlink\0" + os.readlink(path).encode("utf-8", "surrogateescape")
        elif stat.S_ISREG(mode):
            content = path.read_bytes()
            entries[f"{SNAPSHOT_CONTENT_PREFIX}{path.relative_to(root).as_posix()}"] = hashlib.sha256(content).hexdigest()
            payload = b"file\0" + content
        elif stat.S_ISDIR(mode):
            payload = b"directory\0"
        else:
            payload = b"special\0"
        return hashlib.sha256(str(mode).encode() + b"\0" + payload).hexdigest()

    def visit(directory: Path) -> None:
        for path in sorted(directory.iterdir(), key=lambda item: item.name):
            relative = path.relative_to(root)
            if _snapshot_path_excluded(relative):
                continue
            key = f"{SNAPSHOT_DIR_PREFIX}{relative.as_posix()}" if path.is_dir() and not path.is_symlink() else relative.as_posix()
            entries[key] = fingerprint(path)
            if path.is_dir() and not path.is_symlink():
                visit(path)

    visit(root)
    return entries


def _git_revision(root: Path, ref: str | None) -> str | None:
    if not ref:
        return None
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"], cwd=root, text=True, stderr=subprocess.DEVNULL,
            env=_subprocess_env(),
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _evidence_binding(skill_dir: Path, cases_path: Path, base_ref: str | None = None, candidate_ref: str | None = None) -> dict:
    """Bind reports to the repository snapshot that produced them."""
    try:
        repository_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=skill_dir, text=True, stderr=subprocess.DEVNULL, env=_subprocess_env(),
        ).strip()
        tree_digest = hashlib.sha256(
            json.dumps(_snapshot(skill_dir), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        cases_digest = hashlib.sha256(cases_path.read_bytes()).hexdigest()
        candidate_head = _git_revision(skill_dir, candidate_ref or "HEAD")
        current_head = _git_revision(skill_dir, "HEAD")
        if candidate_ref and (
            candidate_head is None
            or candidate_head != current_head
            or not _candidate_worktree_matches(skill_dir, candidate_head)
        ):
            candidate_head = None
    except (OSError, subprocess.CalledProcessError, UnicodeError):
        repository_root = ""
        tree_digest = ""
        cases_digest = ""
    return {
        "version": BINDING_VERSION,
        "repository_root": repository_root,
        "base_head": _git_revision(skill_dir, base_ref),
        "candidate_head": candidate_head,
        "skill_tree_sha256": tree_digest,
        "cases_sha256": cases_digest,
    }


def _candidate_worktree_matches(skill_dir: Path, candidate: str) -> bool:
    try:
        repository_root = Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=skill_dir, text=True, stderr=subprocess.DEVNULL, env=_subprocess_env(),
            ).strip()
        )
        package = str(skill_dir.resolve().relative_to(repository_root.resolve()))
        for args in (
            ("diff", "--quiet", candidate, "--", package),
            ("diff", "--quiet", "--cached", candidate, "--", package),
        ):
            if subprocess.run(["git", *args], cwd=repository_root, env=_subprocess_env(), capture_output=True).returncode != 0:
                return False
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all", "--", package],
            cwd=repository_root, text=True, capture_output=True, env=_subprocess_env(), check=False,
        )
        if status.returncode != 0 or status.stdout:
            return False
        ignored = subprocess.run(
            ["git", "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", package],
            cwd=repository_root, capture_output=True, env=_subprocess_env(), check=False,
        )
        if ignored.returncode != 0:
            return False
        for raw_path in ignored.stdout.split(b"\0"):
            if not raw_path:
                continue
            relative = Path(os.fsdecode(raw_path))
            if not _snapshot_path_excluded(relative):
                return False
        return True
    except (OSError, subprocess.CalledProcessError, ValueError):
        return False


def _valid_evidence_binding(binding: object) -> bool:
    if not isinstance(binding, dict) or binding.get("version") != BINDING_VERSION:
        return False
    if not isinstance(binding.get("repository_root"), str) or not binding["repository_root"].startswith("/"):
        return False
    for key in ("base_head", "candidate_head", "skill_tree_sha256", "cases_sha256"):
        value = binding.get(key)
        if not isinstance(value, str) or not value:
            return False
    return bool(
        re.fullmatch(r"[0-9a-f]{40}", binding["base_head"])
        and re.fullmatch(r"[0-9a-f]{40}", binding["candidate_head"])
        and re.fullmatch(r"[0-9a-f]{64}", binding["skill_tree_sha256"])
        and re.fullmatch(r"[0-9a-f]{64}", binding["cases_sha256"])
    )


def _changed_paths(before: dict[str, str], after: dict[str, str]) -> set[str]:
    return {
        path for path in set(before) | set(after)
        if not path.startswith((SNAPSHOT_DIR_PREFIX, SNAPSHOT_CONTENT_PREFIX)) and before.get(path) != after.get(path)
    }


def _content_tree_sha256(snapshot: dict[str, str], prefix: str, paths: list[str] | None = None) -> str | None:
    root = f"{SNAPSHOT_CONTENT_PREFIX}{prefix.rstrip('/')}/"
    files = {key[len(root):]: value for key, value in snapshot.items() if key.startswith(root)}
    if paths is not None:
        if any(path not in files for path in paths):
            return None
        files = {path: files[path] for path in paths}
    if not files:
        return None
    manifest = json.dumps(
        [[path, files[path]] for path in sorted(files)],
        ensure_ascii=False, separators=(",", ":"),
    )
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()


def _trial_fingerprint(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


def _trial_metadata(
    skill_dir: Path,
    case: dict,
    condition: str,
    context: dict | None = None,
    *,
    environment_kind: str = "temporary_copy",
    runtime_status: str = "READY",
) -> dict:
    context = context or {}
    return {
        "trial_id": str(uuid.uuid4()),
        "condition": condition,
        "environment_kind": environment_kind,
        "candidate_fingerprint": {
            "revision": context.get("candidate_revision"),
            "tree_sha256": context.get("candidate_tree_sha256") or _trial_fingerprint(_snapshot(skill_dir)),
        },
        "test_fingerprint": context.get("test_fingerprint") or _trial_fingerprint(case),
        "base_identity": context.get("base_identity"),
        "runtime_auth_status": runtime_status,
        "lifecycle": {
            "sequence": ["ALLOCATE", "PREPARE", "BASELINE", "RUN", "FREEZE", "REPORT", "ARCHIVE", "CLEAN"],
            "baseline": "paired_without_skill" if case.get("paired") else "NOT_REQUESTED",
            "evidence_frozen": False,
            "terminal_state": None,
        },
    }


def _trial_result(result: dict, trial: dict, *, terminal_state: str = "CLEANED") -> dict:
    lifecycle = trial["lifecycle"]
    lifecycle["evidence_frozen"] = True
    lifecycle["terminal_state"] = terminal_state
    result["trial"] = trial
    return result


def _unassessed_case(
    case: dict,
    skill_dir: Path,
    reason: str,
    context: dict,
    runtime_status: str,
    condition: str = "with_skill",
) -> dict:
    trial = _trial_metadata(
        skill_dir,
        case,
        condition,
        context,
        environment_kind="not_allocated",
        runtime_status=runtime_status,
    )
    return _trial_result({
        "case_id": case["id"],
        "kind": case["kind"],
        "expected": case["expected"],
        "condition": condition,
        "status": "NOT_ASSESSED",
        "runtime_evidence": {
            "skill_discovery": "NOT_ASSESSED",
            "explicit_invocation": "NOT_REQUESTED",
            "implicit_activation": "NOT_ASSESSED",
            "behavior": "NOT_ASSESSED",
        },
        "reason": reason,
    }, trial)


def _trial_record_is_valid(item: dict, binding: dict) -> bool:
    trial = item.get("trial")
    candidate = trial.get("candidate_fingerprint") if isinstance(trial, dict) else None
    lifecycle = trial.get("lifecycle") if isinstance(trial, dict) else None
    return bool(
        isinstance(trial, dict)
        and isinstance(trial.get("trial_id"), str)
        and re.fullmatch(r"[0-9a-f-]{36}", trial["trial_id"])
        and trial.get("condition") == item.get("condition")
        and trial.get("environment_kind") in {"temporary_copy", "worktree", "sandbox", "not_allocated"}
        and isinstance(candidate, dict)
        and candidate.get("revision") == binding.get("candidate_head")
        and candidate.get("tree_sha256") == binding.get("skill_tree_sha256")
        and trial.get("test_fingerprint") == binding.get("cases_sha256")
        and trial.get("base_identity") == binding.get("base_head")
        and isinstance(trial.get("runtime_auth_status"), str)
        and isinstance(lifecycle, dict)
        and lifecycle.get("sequence") == TRIAL_SEQUENCE
        and lifecycle.get("evidence_frozen") is True
        and lifecycle.get("terminal_state") in TRIAL_TERMINAL_STATES
    )


def _package_structure_ok(skill_dir: Path) -> bool:
    files = {
        path.relative_to(skill_dir).as_posix()
        for path in skill_dir.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    if files != EXPECTED_FILES:
        return False
    markdown = "\n".join(path.read_text(encoding="utf-8") for path in skill_dir.rglob("*.md"))
    links = re.findall(r"\]\(([^)#]+)", markdown)
    if any(link.startswith(("/", "file:")) for link in links):
        return False
    if any(not (skill_dir / link).is_file() for link in links if not link.startswith(("http:", "https:"))):
        return False
    if any(marker in markdown for marker in ("TODO", "TBD", "<path/to/", "<skill-name>")):
        return False
    return all((skill_dir / path).stat().st_size > 0 for path in files)


def _provenance_ok(skill_dir: Path) -> bool:
    path = skill_dir / "references" / "provenance.md"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    return all(marker in text for marker in UPSTREAM_MARKERS)


def _cost(result: dict | None) -> dict | None:
    metrics = result.get("cost_metrics") if result else None
    if not isinstance(metrics, dict):
        return None
    return {key: metrics.get(key) for key in ("tool_calls", "command_count", "token_count", "artifact_count")}


def _paired_evidence(with_skill: dict | None, without_skill: dict | None) -> dict:
    with_cost = _cost(with_skill)
    without_cost = _cost(without_skill)
    required_cost = ("tool_calls", "command_count", "artifact_count")
    cost_delta = (
        {key: with_cost[key] - without_cost[key] for key in with_cost if isinstance(with_cost[key], int) and isinstance(without_cost[key], int)}
        if with_cost is not None and without_cost is not None else None
    )
    cost_comparison_observed = bool(
        with_cost is not None and without_cost is not None
        and all(isinstance(with_cost[key], int) and isinstance(without_cost[key], int) for key in required_cost)
    )
    artifact_delta_observed = bool(
        with_skill and without_skill
        and with_skill.get("changed_paths") != without_skill.get("changed_paths")
    )
    outcome_delta_observed = bool(
        with_skill and without_skill
        and (with_skill.get("observed") != without_skill.get("observed") or artifact_delta_observed)
    )
    added_value_observed = bool(
        with_skill and with_skill.get("status") == "PASS"
        and with_skill.get("process_observed") and with_skill.get("trace_matches") and with_skill.get("artifact_ok")
        and without_skill and without_skill.get("status") == "OBSERVED"
        and without_skill.get("process_observed") and without_skill.get("trace_matches") and without_skill.get("artifact_ok")
        and cost_comparison_observed and outcome_delta_observed
    )
    return {
        "behavior_delta_observed": bool(with_skill and without_skill and with_skill.get("observed") != without_skill.get("observed")),
        "artifact_delta_observed": artifact_delta_observed,
        "outcome_delta_observed": outcome_delta_observed,
        "cost_observed": with_cost is not None and without_cost is not None,
        "cost_delta": cost_delta,
        "cost_comparison_observed": cost_comparison_observed,
        "added_value_observed": added_value_observed,
    }


def _artifact_contract(case: dict, with_skill: bool = True) -> dict:
    if case["id"] == "create-no-skill" or case.get("kind") == "ACTION" or case.get("artifact") == "none":
        return {}
    if case.get("artifact") and case.get("artifact_path"):
        contract = {"operation": case["artifact"], "path": case["artifact_path"]}
        if with_skill and case.get("side_effects"):
            contract["side_effects"] = case["side_effects"]
        return contract
    if case.get("kind") not in {"routing", "ACTION"}:
        return {"operation": "created", "path": f".evaluation/{case['id']}.json"}
    return {}


def _case_gates(case: dict) -> list[str]:
    return case.get("gates", [case["gate"]])


def _selected_action_cases(data: dict, stage: str, case_ids: set[str] | None) -> list[dict]:
    if stage != "full":
        return []
    return [
        case for case in data.get("action_cases", [])
        if not case_ids or case.get("id") in case_ids
    ]


def _install_evidence_ok(
    case: dict,
    report: dict,
    before: dict[str, str] | None = None,
    after: dict[str, str] | None = None,
    lifecycle_evidence: dict | None = None,
) -> tuple[bool, str]:
    """Recompute the minimum source, payload, validation, task, and ownership evidence for INSTALL."""
    if case.get("kind") != "INSTALL":
        return True, "installation evidence not applicable"
    evidence = report.get("installation")
    outcome = case.get("installation_outcome")
    if not isinstance(evidence, dict) or evidence.get("status") != outcome:
        return False, "structured installation outcome is missing or mismatched"
    if outcome == "BLOCKED":
        if evidence.get("workspace_changed") is not False or not isinstance(evidence.get("collision"), str) or len(evidence["collision"].strip()) < 10:
            return False, "blocked install must document the preserved collision and no workspace mutation"
        return True, "unmanaged collision was preserved"
    if outcome == "ROUTE":
        if evidence.get("workspace_changed") is not False or evidence.get("route") not in {"CREATE", "UPDATE"}:
            return False, "redesign route must select CREATE or UPDATE without mutation"
        if not isinstance(evidence.get("reason"), str) or len(evidence["reason"].strip()) < 20:
            return False, "redesign route needs a substantive reason"
        return True, "material redesign was routed without mutation"
    if outcome != "INSTALLED":
        return False, "unknown INSTALL case outcome"
    if evidence.get("workspace_changed") is not True:
        return False, "successful INSTALL must materialize the target payload in its isolated fixture"
    source, target, payload = (evidence.get(key) for key in ("source", "target", "payload"))
    audit, validation, real_task, ownership = (evidence.get(key) for key in ("audit", "validation", "real_task", "ownership"))
    if not all(isinstance(item, dict) for item in (source, target, payload, audit, validation, real_task, ownership)):
        return False, "install receipt is missing source, target, payload, audit, validation, real-task, or ownership sections"
    backend = evidence.get("backend")
    if not isinstance(backend, dict) or not all(
        isinstance(backend.get(key), str) and backend[key].strip()
        for key in ("identity", "version", "state_identity")
    ):
        return False, "backend identity, version, and observed state identity are required"
    native_revision = backend.get("native_revision")
    if native_revision is not None and (not isinstance(native_revision, str) or not re.fullmatch(r"[0-9a-f]{40}", native_revision)):
        return False, "backend native revision must be an immutable 40-character commit or null"
    if not all(isinstance(source.get(key), str) and source[key].strip() for key in ("repository", "requested_ref", "path", "license")):
        return False, "source identity requires repository, requested ref, path, and license"
    if not isinstance(source.get("revision"), str) or not re.fullmatch(r"[0-9a-f]{40}", source["revision"]):
        return False, "source revision must be an immutable 40-character commit"
    for source_key, case_key in (("repository", "source_repository"), ("requested_ref", "source_ref"), ("path", "source_fixture"), ("license", "source_license")):
        if case.get(case_key) is not None and source[source_key] != case[case_key]:
            return False, f"source {source_key} does not match the declared fixture contract"
    resolved_license = case.get("_resolved_license")
    if before is not None and after is not None and (not resolved_license or source["license"] != resolved_license):
        return False, "reported license does not match the source license marker inspected before the trial"
    resolved_revision = case.get("_resolved_revision")
    if before is not None and after is not None and (not resolved_revision or source["revision"] != resolved_revision):
        return False, "source revision does not match the fixture ref resolved before the trial"
    if not all(isinstance(target.get(key), str) and target[key].strip() for key in ("runtime", "path")) or target.get("scope") not in {"project", "global"} or target.get("mode") not in {"copy", "editable", "runtime"}:
        return False, "target requires runtime, project/global scope, path, and supported install mode"
    if not _safe_relative_posix_path(target["path"]):
        return False, "target path must remain within the selected scope"
    expected_target = next((
        effect["path"][:-len("/SKILL.md")]
        for effect in case.get("side_effects", [])
        if isinstance(effect, dict) and isinstance(effect.get("path"), str) and effect["path"].endswith("/SKILL.md")
    ), None)
    if expected_target is not None and target["path"] != expected_target:
        return False, "receipt target does not match the materialized skill path"
    hashes = [payload.get(key) for key in ("source_sha256", "selected_sha256", "installed_sha256")]
    if not all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) for value in hashes):
        return False, "source, selected, and installed payload fingerprints must be SHA-256 values"
    adaptation = payload.get("adaptation")
    adapted_files: dict[str, dict] = {}
    if adaptation != "none":
        if not isinstance(adaptation, dict) or not isinstance(adaptation.get("reason"), str) or len(adaptation["reason"].strip()) < 20 or not isinstance(adaptation.get("files"), list) or not adaptation["files"]:
            return False, "adaptation needs a substantive reason and per-file evidence"
        for item in adaptation["files"]:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("path"), str)
                or not _safe_relative_posix_path(item["path"])
                or not all(isinstance(item.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", item[key]) for key in ("source_sha256", "installed_sha256"))
                or item["path"] in adapted_files
            ):
                return False, "adaptation entries require unique safe file paths and source/installed SHA-256 values"
            adapted_files[item["path"]] = item
    if adaptation == "none" and hashes[1] != hashes[2]:
        return False, "installed payload does not match the selected payload"
    source_fixture = case.get("source_fixture")
    package_files = case.get("package_files")
    if before is not None and after is not None:
        if not isinstance(source_fixture, str) or not isinstance(package_files, list) or not package_files:
            return False, "install case must bind the source fixture and consumed package files"
        target_prefix = target["path"].rstrip("/")
        occupied_target = any(
            key.removeprefix(SNAPSHOT_DIR_PREFIX) == target_prefix
            or key.removeprefix(SNAPSHOT_DIR_PREFIX).startswith(f"{target_prefix}/")
            for key in before
        )
        if occupied_target:
            return False, "successful install target was not empty before materialization"
        if not set(adapted_files).issubset(package_files):
            return False, "adaptation receipt contains paths outside the selected package closure"
        for relative in package_files:
            if not isinstance(relative, str) or not _safe_relative_posix_path(relative):
                return False, "package file paths must remain within the selected source and target roots"
            source_path = f"{source_fixture.rstrip('/')}/{relative}"
            installed_path = f"{target['path'].rstrip('/')}/{relative}"
            source_fingerprint = before.get(source_path)
            installed_fingerprint = after.get(installed_path)
            source_content = before.get(f"{SNAPSHOT_CONTENT_PREFIX}{source_path}")
            installed_content = after.get(f"{SNAPSHOT_CONTENT_PREFIX}{installed_path}")
            if source_fingerprint is None or before.get(installed_path) is not None or installed_fingerprint is None:
                return False, f"installed package file is missing or the target was already occupied: {relative}"
            if source_content is None or installed_content is None:
                return False, f"raw file content hash is unavailable for package file: {relative}"
            if installed_fingerprint != source_fingerprint and relative not in adapted_files:
                return False, f"installed package file does not byte-match its fixture source: {relative}"
            if relative not in adapted_files and installed_content != source_content:
                return False, f"installed package content hash differs from its fixture source: {relative}"
            if relative in adapted_files and adapted_files[relative]["source_sha256"] == adapted_files[relative]["installed_sha256"]:
                return False, f"declared compatibility adaptation has no per-file hash delta: {relative}"
            if relative in adapted_files and (
                adapted_files[relative]["source_sha256"] != source_content
                or adapted_files[relative]["installed_sha256"] != installed_content
            ):
                return False, f"adaptation receipt hashes do not match source and installed contents: {relative}"
        state_paths = [
            effect["path"] for effect in case.get("side_effects", [])
            if isinstance(effect, dict) and isinstance(effect.get("path"), str)
            and "/.skill-installs/" in f"/{effect['path']}"
        ]
        if len(state_paths) != 1 or backend.get("state_identity") != after.get(f"{SNAPSHOT_CONTENT_PREFIX}{state_paths[0]}"):
            return False, "backend state identity must match the observed install-state manifest bytes"
        actual_source = _content_tree_sha256(before, source_fixture)
        actual_selected = _content_tree_sha256(before, source_fixture, package_files)
        actual_installed = _content_tree_sha256(after, target_prefix, package_files)
        if (payload["source_sha256"], payload["selected_sha256"], payload["installed_sha256"]) != (
            actual_source, actual_selected, actual_installed,
        ):
            return False, "reported payload fingerprints do not match snapshotted source, selected, and installed contents"
        file_receipts = payload.get("files")
        if not isinstance(file_receipts, list) or any(not isinstance(item, dict) for item in file_receipts):
            return False, "payload receipt must include per-file source and installed SHA-256 values"
        receipt_by_path = {item.get("path"): item for item in file_receipts if isinstance(item.get("path"), str)}
        if len(receipt_by_path) != len(file_receipts) or set(receipt_by_path) != set(package_files):
            return False, "payload file receipts must cover exactly the selected package paths"
        for relative in package_files:
            receipt = receipt_by_path[relative]
            if (
                receipt.get("source_sha256") != before.get(f"{SNAPSHOT_CONTENT_PREFIX}{source_fixture.rstrip('/')}/{relative}")
                or receipt.get("installed_sha256") != after.get(f"{SNAPSHOT_CONTENT_PREFIX}{target_prefix}/{relative}")
            ):
                return False, f"per-file payload receipt does not match snapshotted content: {relative}"
    if audit.get("status") != "PASS" or not isinstance(audit.get("backend"), str) or not audit["backend"].strip():
        return False, "a named static audit backend must pass before installation"
    if validation.get("status") != "PASS" or real_task.get("status") != "PASS":
        return False, "post-install validation and a real-task smoke must both pass"
    if not isinstance(ownership.get("receipt_id"), str) or not ownership["receipt_id"].strip() or not isinstance(ownership.get("uninstall"), str) or len(ownership["uninstall"].strip()) < 12:
        return False, "ownership identity and safe uninstall mechanism are required"
    if not isinstance(ownership.get("update_behavior"), str) or len(ownership["update_behavior"].strip()) < 12:
        return False, "ownership must document same/changed-revision reinstall behavior"
    if native_revision is None:
        if before is None or after is None:
            return False, "composite provenance requires runner-observed source and installed snapshots"
        binding = evidence.get("composite_provenance")
        if not isinstance(binding, dict) or binding.get("verified") is not True or (
            binding.get("source_revision") != source["revision"]
            or binding.get("selected_sha256") != payload["selected_sha256"]
            or binding.get("installed_sha256") != payload["installed_sha256"]
        ):
            return False, "a null backend revision requires verified composite source-to-installed provenance"
    if case.get("id") == "install-owned-lifecycle":
        revisions = lifecycle_evidence.get("source_revisions") if isinstance(lifecycle_evidence, dict) else None
        if (
            not _owned_lifecycle_snapshots_ok(case, lifecycle_evidence)
            or not isinstance(revisions, list) or not revisions or revisions[0] != source["revision"]
            or not _lifecycle_stage_reports_ok(case, lifecycle_evidence, backend["identity"], revisions)
        ):
            return False, "owned lifecycle transitions are NOT_ASSESSED: runner-owned intermediate state snapshots are incomplete or inconsistent"
    if case.get("id") == "install-zero-adaptation" and adaptation != "none":
        return False, "the clean control must install without manufacturing an adaptation"
    return True, "source-bound install lifecycle evidence observed"


LIFECYCLE_SNAPSHOT_STAGES = (
    "after_initial_install", "after_same_revision", "after_changed_revision",
    "after_local_edit", "after_uninstall", "after_final_reinstall",
)


def _owned_lifecycle_snapshots_ok(case: dict, evidence: dict | None) -> bool:
    """Validate filesystem snapshots captured by the runner around each backend process."""
    if not isinstance(evidence, dict):
        return False
    snapshots = evidence.get("snapshots")
    if not isinstance(snapshots, dict) or any(not isinstance(snapshots.get(stage), dict) for stage in LIFECYCLE_SNAPSHOT_STAGES):
        return False
    source_revisions = evidence.get("source_revisions")
    edited_path = evidence.get("edited_path")
    package_files = case.get("package_files")
    source_root = case.get("source_fixture")
    target = next((
        effect["path"].removesuffix("/SKILL.md")
        for effect in case.get("side_effects", [])
        if isinstance(effect, dict) and isinstance(effect.get("path"), str) and effect["path"].endswith("/SKILL.md")
    ), None)
    manifest = next((
        effect["path"] for effect in case.get("side_effects", [])
        if isinstance(effect, dict) and isinstance(effect.get("path"), str)
        and "/.skill-installs/" in f"/{effect['path']}"
    ), None)
    if (
        not isinstance(package_files, list) or not package_files
        or not isinstance(source_root, str) or not target or not manifest
        or not isinstance(source_revisions, list) or len(source_revisions) != 2
        or any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value) for value in source_revisions)
        or source_revisions[0] == source_revisions[1]
        or edited_path not in package_files
    ):
        return False
    states = [snapshots[stage] for stage in LIFECYCLE_SNAPSHOT_STAGES]
    source_prefix = f"{SNAPSHOT_CONTENT_PREFIX}{source_root.rstrip('/')}/"
    target_prefix = f"{SNAPSHOT_CONTENT_PREFIX}{target.rstrip('/')}/"
    neighbor = ".fixture-data/neighbor-canary.txt"
    neighbor_key = f"{SNAPSHOT_CONTENT_PREFIX}{neighbor}"
    neighbor_hash = states[0].get(neighbor_key)
    if not isinstance(neighbor_hash, str) or any(state.get(neighbor_key) != neighbor_hash for state in states):
        return False

    def payload(state: dict, prefix: str) -> dict[str, str]:
        return {
            path[len(prefix):]: value
            for path, value in state.items()
            if path.startswith(prefix)
        }

    def owned(state: dict) -> dict[str, str]:
        return payload(state, target_prefix)

    def only_expected_changes(left: dict, right: dict, allowed_dirs: set[str], allowed_files: set[str] = frozenset()) -> bool:
        changed_paths = {
            key.removeprefix(SNAPSHOT_CONTENT_PREFIX).removeprefix(SNAPSHOT_DIR_PREFIX)
            for key in set(left) | set(right) if left.get(key) != right.get(key)
        }
        return all(
            path in allowed_files or any(path == prefix or path.startswith(f"{prefix.rstrip('/')}/") for prefix in allowed_dirs)
            for path in changed_paths
        )

    initial, same, changed, edited, uninstalled, final = states
    initial_payload = owned(initial)
    changed_payload = owned(changed)
    expected_files = set(package_files)
    revision_hashes = evidence.get("source_revision_hashes")
    if not isinstance(revision_hashes, dict) or any(
        not isinstance(revision_hashes.get(revision), dict)
        or set(revision_hashes[revision]) != expected_files
        or any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value) for value in revision_hashes[revision].values())
        for revision in source_revisions
    ):
        return False
    for state, revision in zip(states, (source_revisions[0], source_revisions[0], source_revisions[1], source_revisions[1], source_revisions[1], source_revisions[1])):
        if payload(state, source_prefix) != revision_hashes[revision]:
            return False
    expected_initial = revision_hashes[source_revisions[0]]
    expected_changed = revision_hashes[source_revisions[1]]
    if (
        set(initial_payload) != expected_files
        or any(initial_payload.get(path) != expected_initial.get(path) for path in expected_files)
        or owned(same) != initial_payload
        or same.get(f"{SNAPSHOT_CONTENT_PREFIX}{manifest}") != initial.get(f"{SNAPSHOT_CONTENT_PREFIX}{manifest}")
        or set(changed_payload) != expected_files
        or any(changed_payload.get(path) != expected_changed.get(path) for path in expected_files)
        or not any(expected_changed.get(path) != expected_initial.get(path) for path in expected_files)
        or changed.get(f"{SNAPSHOT_CONTENT_PREFIX}{manifest}") == initial.get(f"{SNAPSHOT_CONTENT_PREFIX}{manifest}")
        or not only_expected_changes(initial, same, set())
        or not only_expected_changes(same, changed, {source_root.rstrip("/"), target.rstrip("/")}, {manifest})
        or not only_expected_changes(changed, edited, {target.rstrip("/")})
        or not only_expected_changes(edited, uninstalled, {target.rstrip("/")}, {manifest})
        or not only_expected_changes(uninstalled, final, {target.rstrip("/")}, {manifest})
        or set(owned(edited)) != expected_files
        or any(owned(edited).get(path) != changed_payload.get(path) for path in expected_files if path != edited_path)
        or owned(edited).get(edited_path) in {None, changed_payload.get(edited_path)}
        or owned(uninstalled) != {edited_path: owned(edited).get(edited_path)}
        or f"{SNAPSHOT_CONTENT_PREFIX}{manifest}" in uninstalled
        or set(owned(final)) != expected_files
        or any(owned(final).get(path) != expected_changed.get(path) for path in expected_files)
        or owned(final) != changed_payload
        or not isinstance(final.get(f"{SNAPSHOT_CONTENT_PREFIX}{manifest}"), str)
    ):
        return False
    return True


def _git_file_sha256(repository: Path, revision: str, relative_path: str) -> str | None:
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision) or not _safe_relative_posix_path(relative_path):
        return None
    try:
        result = subprocess.run(
            ["git", "show", f"{revision}:{relative_path}"],
            cwd=repository, capture_output=True, check=False, env=_subprocess_env(),
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return hashlib.sha256(result.stdout).hexdigest()


def _source_matches_revision(snapshot: dict, source_prefix: str, repository: Path, revision: str, paths: list[str]) -> bool:
    for relative in paths:
        expected = _git_file_sha256(repository, revision, relative)
        observed = snapshot.get(f"{SNAPSHOT_CONTENT_PREFIX}{source_prefix.rstrip('/')}/{relative}")
        if expected is None or observed != expected:
            return False
    return True


def _git_revision_hashes(repository: Path, revision: str, paths: list[str]) -> dict[str, str] | None:
    hashes = {relative: _git_file_sha256(repository, revision, relative) for relative in paths}
    return hashes if all(value is not None for value in hashes.values()) else None


def _lifecycle_stage_reports_ok(case: dict, evidence: dict, backend: str, revisions: list[str]) -> bool:
    reports = evidence.get("stage_reports")
    snapshots = evidence.get("snapshots")
    target = next((
        effect["path"].removesuffix("/SKILL.md")
        for effect in case.get("side_effects", [])
        if isinstance(effect, dict) and isinstance(effect.get("path"), str) and effect["path"].endswith("/SKILL.md")
    ), None)
    manifest = next((
        effect["path"] for effect in case.get("side_effects", [])
        if isinstance(effect, dict) and isinstance(effect.get("path"), str)
        and "/.skill-installs/" in f"/{effect['path']}"
    ), None)
    if not isinstance(reports, dict) or not isinstance(snapshots, dict) or not target or not manifest:
        return False
    expectations = {
        "after_same_revision": ("install", {"NO_OP", "UNCHANGED"}, revisions[0]),
        "after_changed_revision": ("update", {"UPDATED", "REINSTALLED"}, revisions[1]),
        "after_uninstall": ("uninstall", {"UNINSTALLED", "REMOVED"}, revisions[1]),
        "after_final_reinstall": ("install", {"INSTALLED", "REINSTALLED"}, revisions[1]),
    }
    return bool(
        isinstance(reports, dict)
        and all(
            isinstance(reports.get(stage), dict)
            and reports[stage].get("operation") == operation
            and reports[stage].get("status") in statuses
            and reports[stage].get("backend") == backend
            and reports[stage].get("source_revision") == revision
            and reports[stage].get("target") == target
            and reports[stage].get("state_identity") == snapshots[stage].get(f"{SNAPSHOT_CONTENT_PREFIX}{manifest}")
            for stage, (operation, statuses, revision) in expectations.items()
        )
    )


def _safe_relative_posix_path(value: str) -> bool:
    """Accept normalized relative POSIX package paths, independent of host OS."""
    if not value or value.startswith(("/", "~")) or "\\" in value or "\x00" in value or ":" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in {"", ".", ".."} for part in value.split("/"))


def _confined_regular_file(root: Path, path: Path) -> bool:
    try:
        resolved_root = root.resolve(strict=True)
        resolved_path = path.resolve(strict=True)
        resolved_path.relative_to(resolved_root)
        return not path.is_symlink() and stat.S_ISREG(path.stat().st_mode)
    except (OSError, ValueError):
        return False


def _artifact_ok(case: dict, before: dict[str, str], after: dict[str, str], with_skill: bool = True) -> tuple[bool, str]:
    contract = _artifact_contract(case, with_skill)
    changed = _changed_paths(before, after)
    changed_directories = {
        path for path in set(before) | set(after)
        if path.startswith(SNAPSHOT_DIR_PREFIX) and before.get(path) != after.get(path)
    }
    if not contract:
        return (not changed and not changed_directories, "no artifact required")
    path = contract["path"]
    operation = contract["operation"]
    side_effects = contract.get("side_effects", [])
    expected_paths = {path, *(effect["path"] for effect in side_effects)}
    expected_directories = {
        f"{SNAPSHOT_DIR_PREFIX}{parent.as_posix()}"
        for expected_path in expected_paths
        for parent in PurePosixPath(expected_path).parents
        if parent.as_posix() != "."
    }
    exists_before = path in before
    exists_after = path in after
    side_effects_ok = all(
        effect.get("operation") == "created" and effect["path"] not in before and effect["path"] in after
        or effect.get("operation") == "modified" and effect["path"] in before and effect["path"] in after and before[effect["path"]] != after[effect["path"]]
        or effect.get("operation") == "deleted" and effect["path"] in before and effect["path"] not in after
        for effect in side_effects
    )
    unexpected = (changed - expected_paths) | (changed_directories - expected_directories)
    if not side_effects_ok or unexpected:
        return False, f"unexpected changed paths outside the contracted artifacts: {sorted(unexpected)}"
    if not expected_paths.issubset(changed):
        return False, f"contracted artifact paths were not materialized: {sorted(expected_paths - changed)}"
    if operation == "created":
        return (not exists_before and exists_after, f"expected only created artifact {path}")
    if operation == "modified":
        return (exists_before and exists_after and before[path] != after[path], f"expected only modified artifact {path}")
    if operation == "deleted":
        return (exists_before and not exists_after, f"expected only deleted artifact {path}")
    return False, f"unknown artifact operation {operation}"


NECESSITY_CHECKS = {
    "native", "agents", "scripts", "project_or_user_skill", "maintained_candidate",
    "sibling_or_localization", "ordinary_instructions",
}
EXPECTED_NECESSITY_DISPOSITIONS = {
    "create-local-upstream": "REFERENCE_AND_ADAPT",
    "create-multimode-one-skill": "CLONE_AND_ADAPT",
    "create-no-skill": "REJECT",
    "update-bounded": "UPDATE_EXISTING",
    "update-substantive": "UPDATE_EXISTING",
    "audit-upstream-drift": "UPDATE_NEEDED",
    "audit-overlap": "MERGE",
    "audit-localize": "LOCALIZE",
    "audit-retire": "RETIRE",
}
CREATE_ADAPTATION_DISPOSITIONS = {"CLONE_AND_ADAPT", "REFERENCE_AND_ADAPT"}
CREATE_SOURCE_ROLES = {"DONOR_REFERENCE_ONLY", "INSTALLABLE_OWNER"}
COEXISTENCE_PATHS = {
    "audit-overlap": {".agents/skills/pdf/SKILL.md", ".agents/skills/overlap-skill/SKILL.md"},
    "audit-localize": {".agents/skills/pdf/SKILL.md", ".agents/skills/domain-workflow/SKILL.md"},
    "audit-retire": {".agents/skills/pdf/SKILL.md", ".agents/skills/stale-skill/SKILL.md"},
    "evaluate-sibling-collision": {".agents/skills/pdf/SKILL.md", ".agents/skills/candidate-skill/SKILL.md"},
}


def _necessity_ok(case: dict, report: dict) -> tuple[bool, str]:
    if case.get("kind") not in {"CREATE", "UPDATE", "AUDIT"}:
        return True, "necessity gate not applicable"
    evidence = report.get("necessity")
    if not isinstance(evidence, dict):
        return False, "structured necessity evidence is missing"
    disposition = evidence.get("disposition")
    if not isinstance(disposition, str) or disposition not in ACTION_DISPOSITIONS or disposition != EXPECTED_NECESSITY_DISPOSITIONS.get(case.get("id")):
        return False, "necessity evidence needs a typed disposition"
    alternatives = evidence.get("alternatives")
    if not isinstance(alternatives, dict) or not alternatives:
        return False, "necessity evidence needs available alternative states"
    if set(alternatives) - NECESSITY_CHECKS:
        return False, "necessity evidence contains an unknown alternative"
    if case.get("kind") == "CREATE" and disposition in CREATE_ADAPTATION_DISPOSITIONS:
        maintained = alternatives.get("maintained_candidate")
        if not isinstance(maintained, dict) or maintained.get("state") != "CHECKED":
            return False, "CREATE adaptation requires a checked maintained-source disposition"
        source_role = maintained.get("source_role")
        if source_role not in CREATE_SOURCE_ROLES:
            return False, "CREATE adaptation requires source_role DONOR_REFERENCE_ONLY or INSTALLABLE_OWNER"
        if source_role == "INSTALLABLE_OWNER" or maintained.get("disposition") == "INSTALL_EXISTING":
            return False, "installable maintained owner must route to INSTALL; CREATE cannot adapt it"
        if source_role != "DONOR_REFERENCE_ONLY" or maintained.get("disposition") not in CREATE_ADAPTATION_DISPOSITIONS:
            return False, "CREATE adaptation requires donor/reference-only maintained material"
    checked = 0
    for name, detail in alternatives.items():
        if not isinstance(detail, dict) or detail.get("state") not in NECESSITY_STATES:
            return False, f"necessity alternative {name} needs a valid evidence state"
        state = detail["state"]
        if state == "CHECKED":
            checked += 1
            if detail.get("disposition") not in ACTION_DISPOSITIONS:
                return False, f"checked alternative {name} needs a typed action disposition"
            reason = detail.get("reason")
            if not isinstance(reason, str) or len(reason.strip()) < 20:
                return False, f"checked alternative {name} needs substantive evidence"
        elif "disposition" in detail and detail["disposition"] is not None:
            return False, f"unavailable alternative {name} must not claim an action disposition"
    if not checked:
        return False, "necessity evidence needs at least one checked plausible alternative"
    if not isinstance(evidence.get("justification"), str) or not evidence["justification"].strip():
        return False, "necessity justification is missing"
    return True, "structured necessity evidence observed"


def _recomputed_record(item: dict, case: dict) -> dict | None:
    events = item.get("trace_events")
    before = item.get("before_snapshot")
    after = item.get("after_snapshot")
    report = item.get("final_report")
    if not isinstance(events, list) or not isinstance(before, dict) or not isinstance(after, dict) or not isinstance(report, dict):
        return None
    key = "selected_skill" if case["kind"] == "routing" else (
        "selected_workflow" if case["kind"] == "ACTION" else "disposition"
    )
    artifact_ok, artifact_reason = _artifact_ok(case, before, after, item.get("condition") != "without_skill")
    necessity_ok, necessity_reason = _necessity_ok(case, report)
    install_case = {
        **case,
        "_resolved_revision": case.get("source_revision"),
        "_resolved_license": case.get("source_license"),
    }
    install_ok, install_reason = _install_evidence_ok(install_case, report, before, after, item.get("lifecycle_evidence"))
    runtime_evidence = {
        "skill_discovery": "NOT_ASSESSED",
        "explicit_invocation": "NOT_REQUESTED",
        "implicit_activation": _runtime_activation(events) or "NOT_ASSESSED",
        "behavior": "OBSERVED" if report.get(key) is not None and (case["kind"] == "routing" or (_process_observed(events) and _trace_matches(case, events) and artifact_ok and install_ok)) else "NOT_ASSESSED",
    }
    changed_paths = sorted(_changed_paths(before, after))
    coexistence_ok = COEXISTENCE_PATHS.get(case["id"], set()).issubset(before)
    return {
        "observed": report.get(key),
        "activation": _runtime_activation(events),
        "runtime_evidence": runtime_evidence,
        "process_observed": _process_observed(events),
        "trace_matches": _trace_matches(case, events),
        "changed_paths": changed_paths,
        "artifact_ok": artifact_ok,
        "artifact_reason": artifact_reason,
        "necessity_observed": necessity_ok,
        "necessity_reason": necessity_reason,
        "installation_observed": install_ok,
        "installation_reason": install_reason,
        "coexistence_fixture": coexistence_ok,
        "cost_metrics": _cost_metrics(events, set(changed_paths)),
    }


def _seed_case(fixture_root: Path, case: dict) -> None:
    skills_root = fixture_root / ".agents" / "skills"
    case_id = case["id"]
    if case_id in {"update-bounded", "update-substantive", "audit-upstream-drift"}:
        target = skills_root / "existing-skill"
        (target / "references").mkdir(parents=True, exist_ok=True)
        (target / "SKILL.md").write_text(
            "---\nname: existing-skill\ndescription: Existing bounded skill.\n---\n\nBefore version.\n",
            encoding="utf-8",
        )
        (target / "references" / "provenance.md").write_text(
            "Pinned upstream baseline: old-ref\n",
            encoding="utf-8",
        )
    elif case_id == "audit-overlap":
        target = skills_root / "overlap-skill"
        target.mkdir(parents=True, exist_ok=True)
        (target / "SKILL.md").write_text(
            "---\nname: overlap-skill\ndescription: Rotate and inspect PDF files.\n---\n\nOverlapping workflow.\n",
            encoding="utf-8",
        )
    elif case_id == "audit-retire":
        target = skills_root / "stale-skill"
        target.mkdir(parents=True, exist_ok=True)
        (target / "SKILL.md").write_text(
            "---\nname: stale-skill\ndescription: Stale redundant workflow.\n---\n\nRetire me.\n",
            encoding="utf-8",
        )
    elif case_id.startswith("evaluate-"):
        target = skills_root / "candidate-skill"
        target.mkdir(parents=True, exist_ok=True)
        (target / "SKILL.md").write_text(
            "---\nname: candidate-skill\ndescription: Candidate evaluation fixture.\n---\n\nCandidate content.\n",
            encoding="utf-8",
        )
    elif case_id in {"install-healthy-copy", "install-zero-adaptation", "install-owned-lifecycle"}:
        source = fixture_root / case["source_fixture"]
        (source / "references").mkdir(parents=True, exist_ok=True)
        skill_name = "healthy" if case_id in {"install-healthy-copy", "install-owned-lifecycle"} else "clean-control"
        (source / "SKILL.md").write_text(
            f"---\nname: {skill_name}\ndescription: A maintained, portable fixture skill.\n---\n\nUse the included guide faithfully.\n",
            encoding="utf-8",
        )
        (source / "references" / "guide.md").write_text("Follow the task-specific steps and preserve supplied facts.\n", encoding="utf-8")
        (source / "LICENSE.txt").write_text("SPDX-License-Identifier: MIT\n", encoding="utf-8")
        license_text = (source / "LICENSE.txt").read_text(encoding="utf-8")
        license_match = re.search(r"(?m)^SPDX-License-Identifier:\s*([A-Za-z0-9.+-]+)\s*$", license_text)
        case["_resolved_license"] = license_match.group(1) if license_match else None
        subprocess.run(["git", "init", "--quiet"], cwd=source, check=True, env=_subprocess_env())
        subprocess.run(["git", "add", "."], cwd=source, check=True, env=_subprocess_env())
        commit_env = _subprocess_env()
        commit_env.update({
            "GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+00:00",
            "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+00:00",
        })
        subprocess.run(["git", "commit", "--quiet", "-m", "fixture source"], cwd=source, check=True, env=commit_env)
        subprocess.run(["git", "tag", "--", case["source_ref"]], cwd=source, check=True, env=_subprocess_env())
        case["_resolved_revision"] = _git_revision(source, case["source_ref"])
        if case_id == "install-owned-lifecycle":
            canary = fixture_root / ".fixture-data" / "neighbor-canary.txt"
            canary.parent.mkdir(parents=True, exist_ok=True)
            canary.write_text("unowned neighbor canary\n", encoding="utf-8")
    elif case_id == "install-collision-refused":
        target = skills_root / "existing-owned-skill"
        target.mkdir(parents=True, exist_ok=True)
        (target / "SKILL.md").write_text("Unmanaged collision canary; preserve exactly.\n", encoding="utf-8")
        (fixture_root / ".agents" / "neighbor-canary.txt").write_text("Unrelated file; preserve exactly.\n", encoding="utf-8")
    elif case_id == "install-redesign-routed":
        source = fixture_root / ".fixture-sources" / "redesign"
        source.mkdir(parents=True, exist_ok=True)
        (source / "SKILL.md").write_text("This source must be materially redesigned to meet the request.\n", encoding="utf-8")


@contextmanager
def _fixture(skill_dir: Path, with_skill: bool, case: dict | None = None) -> Iterator[Path]:
    with tempfile.TemporaryDirectory(prefix="skill-creator-eval-", dir=skill_dir.parents[1]) as directory:
        root = Path(directory)
        subprocess.run(
            ["git", "init", "--quiet"], cwd=root, check=True, capture_output=True, text=True,
            env=_subprocess_env(),
        )
        (root / "AGENTS.md").write_text(
            "# Isolated skill evaluation\n\nUse available skills only when the request matches their description.\n",
            encoding="utf-8",
        )
        fixture_root = root / "project" if case and case["id"] == "audit-localize" else root
        if case and case["id"] == "audit-localize":
            fixture_root.mkdir(parents=True, exist_ok=True)
        if with_skill:
            target = fixture_root / ".agents" / "skills" / "skill-creator"
            shutil.copytree(skill_dir, target, ignore=shutil.ignore_patterns("__pycache__"))
        if case and case["id"] in {"audit-overlap", "audit-localize", "audit-retire", "evaluate-sibling-collision"}:
            sibling = fixture_root / ".agents" / "skills" / "pdf"
            sibling.mkdir(parents=True, exist_ok=True)
            (sibling / "SKILL.md").write_text(
                "---\nname: pdf\ndescription: Rotate and inspect PDF files.\n---\n\nUse the PDF workflow.\n",
                encoding="utf-8",
            )
            if case["id"] == "audit-localize":
                local = fixture_root / ".agents" / "skills" / "domain-workflow"
                local.mkdir(parents=True, exist_ok=True)
                (local / "SKILL.md").write_text(
                    "---\nname: domain-workflow\ndescription: Repository-local domain workflow.\n---\n\nUse the local workflow.\n",
                    encoding="utf-8",
                )
            (fixture_root / ".fixture-coexistence").write_text("true\n", encoding="utf-8")
        if case:
            _seed_case(fixture_root, case)
        yield root


def _runtime_preflight(runtime: str, timeout: int) -> dict:
    if not shutil.which(runtime):
        return {"status": "NO_RUNTIME", "reason": f"runtime not found: {runtime}"}
    try:
        version_process = subprocess.run(
            [runtime, "--version"], capture_output=True, text=True,
            timeout=min(timeout, 5), check=False, env=_subprocess_env(),
        )
    except subprocess.TimeoutExpired:
        return {"status": "CONFIG_ERROR", "reason": "runtime version check timed out"}
    runtime_version = next((line.strip() for line in (version_process.stdout or "").splitlines() if line.strip()), None)
    if version_process.returncode != 0 or not runtime_version:
        return {"status": "CONFIG_ERROR", "reason": "runtime version check failed"}
    try:
        socket.getaddrinfo("chatgpt.com", 443)
    except OSError:
        return {"status": "PROVIDER_UNAVAILABLE", "reason": "provider hostname is not resolvable"}
    try:
        process = subprocess.run(
            [runtime, "login", "status"], capture_output=True, text=True,
            timeout=min(timeout, 10), check=False, env=_subprocess_env(),
        )
    except subprocess.TimeoutExpired:
        return {"status": "AUTH_TIMEOUT", "reason": "login status timed out"}
    output = f"{process.stdout}\n{process.stderr}".lower()
    if process.returncode != 0:
        if any(marker in output for marker in ("not logged", "not authenticated", "no credentials", "unauthorized")):
            return {"status": "NO_AUTH", "reason": "runtime is not authenticated"}
        return {"status": "CONFIG_ERROR", "reason": "login status failed"}
    return {"status": "READY", "reason": "saved runtime authentication is available", "runtime_version": runtime_version}


def _timeout_class(output: str) -> str:
    text = output.lower()
    if any(marker in text for marker in ("401", "unauthorized", "missing bearer", "not authenticated", "not logged")):
        return "AUTH_TIMEOUT"
    if any(marker in text for marker in ("lookup address", "stream disconnected", "websocket", "connection reset", "connection refused")):
        return "TRANSPORT_TIMEOUT"
    if any(marker in text for marker in ("process timeout", "process did not exit", "failed to spawn", "broken pipe", "signal")):
        return "PROCESS_TIMEOUT"
    return "TURN_TIMEOUT"


def _runtime_prompt(case: dict, operation_root: Path) -> str:
    if case["kind"] in {"routing", "ACTION"}:
        if case["kind"] == "ACTION":
            result_key = "selected_workflow"
            result_values = "the selected workflow path, fail-closed, clarify-or-no-route, or none"
        else:
            result_key = "selected_skill"
            result_values = "the selected skill name or none"
        task = (
            "Handle this natural user request in the isolated fixture. Do not change files. "
            f"Return exactly one JSON object with key {result_key}, whose value is {result_values}.\n\n"
            f"{case['prompt']}"
        )
    else:
        artifact = _artifact_contract(case)
        artifact_instruction = (
            "No artifact is required; preserve the fixture and reject unnecessary skill creation. "
            if not artifact else (
                f"The required observable artifact is {artifact['operation']} at "
                f"{artifact['path']}. Perform the operation, not just a plan. "
            )
        )
        allowed = ", ".join(sorted(ACTION_DISPOSITIONS if case["kind"] != "EVALUATE" else EVALUATION_DISPOSITIONS))
        candidates = ", ".join(sorted(NECESSITY_CHECKS))
        states = ", ".join(sorted(NECESSITY_STATES))
        task = (
            "Complete this natural user request in the isolated fixture using available instructions and tools. "
            "You may modify only the fixture. Return exactly one JSON object with top-level keys "
            f"disposition, necessity, artifacts, and process. The disposition must be one of: {allowed}. "
            "For CREATE, UPDATE, and AUDIT cases, necessity must contain a field named disposition with an action from the allowed enum, a non-empty justification, and "
            f"an alternatives object whose candidate keys come from: {candidates}. Each alternative must have "
            f"state {states}. Use CHECKED only when the fixture was actually inspected; a CHECKED alternative "
            "must include the fields disposition and reason, with disposition from the allowed action enum and reason of at least 20 characters. "
            "For CREATE, a checked maintained_candidate must also include source_role exactly INSTALLABLE_OWNER or DONOR_REFERENCE_ONLY. "
            "INSTALLABLE_OWNER or INSTALL_EXISTING means route to INSTALL and do not materialize CREATE; CREATE adaptation requires DONOR_REFERENCE_ONLY. "
            "Use NOT_AVAILABLE or NOT_RELEVANT when inspection is not possible or the candidate does not apply; "
            "do not invent unsupported plugin, upstream, global-catalog, or sibling facts. Include at least one "
            "checked plausible alternative. The artifacts value lists changed relative paths; the process value "
            f"lists the concrete steps performed. {artifact_instruction}\n\n{case['prompt']}"
        )
        if case["kind"] == "INSTALL":
            task += (
                " For INSTALL, include top-level installation evidence with status, workspace_changed, and: "
                "for INSTALLED, source {repository, requested_ref, revision, path, license}, target "
                "{runtime, scope, path, mode}, payload {source_sha256, selected_sha256, installed_sha256, adaptation, "
                "files [{path, source_sha256, installed_sha256}] with exactly one entry per package_files path and no extras}, "
                "backend {identity, version, state_identity, native_revision}, audit {status, backend}, validation {status}, "
                "where state_identity is the SHA-256 of the actual install-state manifest bytes in the fixture and native_revision is a 40-character immutable backend commit or null; "
                "real_task {status}, and ownership {receipt_id, update_behavior, uninstall}; if native_revision is null, "
                "include verified composite_provenance binding source revision, selected hash, and installed hash; "
                "when adaptation is none, selected_sha256 must equal installed_sha256; otherwise adaptation must contain a reason and files [{path, source_sha256, installed_sha256}]. For BLOCKED, document the unchanged unmanaged-target "
                "collision. For ROUTE, select CREATE or UPDATE, explain the material redesign, and make no mutation."
            )
            if case.get("id") == "install-owned-lifecycle":
                task += (
                    " The runner will invoke this initial installation, then exercise later lifecycle operations in separate "
                    "processes and capture the filesystem after each transition. Do not write or claim transition snapshots."
                )
    return (
        f"The isolated working directory is {operation_root}. Keep every read and write inside it. "
        "For apply_patch or file-change operations, use paths relative to this working directory; "
        "never pass an absolute path or a path prefixed with the working directory.\n\n"
        f"{task}"
    )


def _lifecycle_prompt(operation_root: Path, stage: str, source_ref: str = "fixture-v1") -> str:
    actions = {
        "after_initial_install": (
            f"Perform only the initial INSTALL of fixture/healthy from {source_ref} into the empty project target. "
            "Inspect the source and package, use the maintained installer/backend selected by the INSTALL workflow, "
            "validate it, run one guide-based task, write the required ordinary INSTALL receipt JSON, and return that receipt."
        ),
        "after_same_revision": (
            f"Re-run the existing receipt-owned installation of fixture/healthy from the same immutable ref {source_ref}. "
            "Use its selected maintained backend; report whether this is a no-op and do not alter unrelated files. "
            "Return JSON with operation=install, status=NO_OP or UNCHANGED, backend (the exact receipt identity), target (the receipt target path), source_revision (the resolved commit SHA), and state_identity (SHA-256 of the actual receipt manifest bytes)."
        ),
        "after_changed_revision": (
            f"Update the existing receipt-owned installation from fixture/healthy ref {source_ref}, whose immutable commit "
            "now differs from the installed revision. Use the selected backend and preserve unrelated files. "
            "Return JSON with operation=update, status=UPDATED or REINSTALLED, backend (the exact receipt identity), target (the receipt target path), source_revision (the resolved commit SHA), and state_identity (SHA-256 of the actual receipt manifest bytes)."
        ),
        "after_uninstall": (
            "Safely uninstall only this backend receipt's installation. Verify its owned payload before removing files; "
            "preserve any locally edited file and the unowned neighbor canary. Do not reinstall in this step. "
            "Return JSON with operation=uninstall, status=UNINSTALLED or REMOVED, backend (the exact receipt identity), target (the receipt target path), source_revision (the removed installation's commit SHA), and state_identity=null."
        ),
        "after_final_reinstall": (
            f"Reinstall fixture/healthy from its changed immutable ref {source_ref} using the selected maintained backend. "
            "Preserve the unowned neighbor canary. Return JSON with operation=install, status=INSTALLED or REINSTALLED, "
            "backend (the exact receipt identity), target (the receipt target path), source_revision (the resolved commit SHA), "
            "and state_identity (SHA-256 of the actual receipt manifest bytes)."
        ),
    }
    return (
        f"The isolated working directory is {operation_root}. Keep every read and write inside it. "
        "For apply_patch or file-change operations, use paths relative to this working directory; "
        "never pass an absolute path or a path prefixed with the working directory.\n\n"
        "This is one isolated lifecycle process; prior process state exists only in the fixture filesystem. "
        f"{actions[stage]} Return one JSON object describing the performed operation."
    )


def _run_owned_lifecycle(case, runtime, model, reasoning_effort, timeout, fixture, operation_root, base, trial, environment):
    """Run each backend transition in its own process and capture state outside the model fixture."""
    snapshots = {}
    events = []
    process_rows = []
    stage_reports = {}
    started = time.monotonic()
    source = fixture / case["source_fixture"]
    initial_revision = case.get("_resolved_revision")
    initial_hashes = _git_revision_hashes(source, initial_revision, case["package_files"])
    if not initial_hashes:
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": "source fixture revision could not be fingerprinted"}, trial)
    before = _snapshot(operation_root)
    if source.is_symlink() or not source.is_dir() or not _confined_regular_file(source, source / "SKILL.md"):
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": "source fixture escaped the isolated trial or is not a regular skill"}, trial)

    def run_stage(stage, prompt):
        command = [
            runtime, "exec", "--model", model, "-c", f'model_reasoning_effort="{reasoning_effort}"',
            "--json", "--ephemeral", "--sandbox", "workspace-write", "--skip-git-repo-check",
            "--ignore-user-config", "--add-dir", str(fixture), "--add-dir", str(fixture / ".agents"),
            "--cd", str(fixture), prompt,
        ]
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False, env=environment)
        except subprocess.TimeoutExpired as exc:
            return None, {"stage": stage, "timeout_class": _timeout_class(str(exc.stderr or ""))}
        stdout = process.stdout or ""
        stage_events = _events(stdout)
        events.extend(stage_events)
        process_rows.append({
            "stage": stage, "returncode": process.returncode,
            "event_count": len(stage_events), "process_observed": _process_observed(stage_events),
        })
        return (process, _json_object(_final_text(stage_events))), None

    initial_case = {
        **case,
        "prompt": "Perform only the initial installation of fixture/healthy from fixture-v1 into the empty project target; "
        "use the selected maintained backend, validate it, run one guide-based task, and write the complete ordinary INSTALL receipt.",
    }
    initial, error = run_stage("after_initial_install", _runtime_prompt(initial_case, operation_root))
    if error or initial is None:
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": f"initial lifecycle process unavailable: {error}"}, trial)
    initial_process, report = initial
    snapshots["after_initial_install"] = _snapshot(operation_root)
    events.append({"runner_stage": "after_initial_install"})
    if initial_process.returncode != 0 or not report:
        return _trial_result({**base, "status": "FAIL", "reason": "initial lifecycle INSTALL failed or returned no receipt", "trace_events": events, "after_snapshot": snapshots["after_initial_install"]}, trial)
    if not _source_matches_revision(snapshots["after_initial_install"], case["source_fixture"], source, initial_revision, case["package_files"]):
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": "initial source bytes no longer match the immutable fixture revision"}, trial)

    same, error = run_stage("after_same_revision", _lifecycle_prompt(operation_root, "after_same_revision"))
    if error or same is None or same[0].returncode != 0:
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": f"same-revision lifecycle process failed: {error or 'nonzero exit'}"}, trial)
    stage_reports["after_same_revision"] = same[1]
    snapshots["after_same_revision"] = _snapshot(operation_root)
    events.append({"runner_stage": "after_same_revision"})
    if not _source_matches_revision(snapshots["after_same_revision"], case["source_fixture"], source, initial_revision, case["package_files"]):
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": "same-revision process changed immutable source bytes"}, trial)

    guide = source / "references" / "guide.md"
    source_status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=source, capture_output=True, text=True, check=False, env=_subprocess_env(),
    )
    if source.is_symlink() or source_status.returncode != 0 or source_status.stdout.strip() or not _confined_regular_file(source, guide):
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": "source fixture changed outside the runner before changed-ref setup"}, trial)
    guide.write_text(guide.read_text(encoding="utf-8") + "Changed immutable fixture revision for lifecycle evaluation.\n", encoding="utf-8")
    subprocess.run(["git", "add", "references/guide.md"], cwd=source, check=True, env=_subprocess_env())
    commit_env = _subprocess_env()
    commit_env.update({
        "GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
        "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        "GIT_AUTHOR_DATE": "2000-01-02T00:00:00+00:00", "GIT_COMMITTER_DATE": "2000-01-02T00:00:00+00:00",
    })
    subprocess.run(["git", "commit", "--quiet", "-m", "fixture changed revision"], cwd=source, check=True, env=commit_env)
    subprocess.run(["git", "tag", "--", "fixture-v2"], cwd=source, check=True, env=_subprocess_env())
    changed_revision = _git_revision(source, "fixture-v2")
    if not changed_revision or changed_revision == case.get("_resolved_revision"):
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": "runner could not bind a fresh changed fixture revision"}, trial)
    changed_hashes = _git_revision_hashes(source, changed_revision, case["package_files"])
    if not changed_hashes:
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": "changed source revision could not be fingerprinted"}, trial)

    changed, error = run_stage("after_changed_revision", _lifecycle_prompt(operation_root, "after_changed_revision", "fixture-v2"))
    if error or changed is None or changed[0].returncode != 0:
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": f"changed-revision lifecycle process failed: {error or 'nonzero exit'}"}, trial)
    stage_reports["after_changed_revision"] = changed[1]
    snapshots["after_changed_revision"] = _snapshot(operation_root)
    events.append({"runner_stage": "after_changed_revision"})
    if not _source_matches_revision(snapshots["after_changed_revision"], case["source_fixture"], source, changed_revision, case["package_files"]):
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": "updated source bytes do not match the immutable changed revision"}, trial)

    edited_path = case["package_files"][0]
    edited_file = fixture / next(
        effect["path"].removesuffix("/SKILL.md") for effect in case["side_effects"]
        if effect["path"].endswith("/SKILL.md")
    ) / edited_path
    if not _confined_regular_file(operation_root, edited_file):
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": "local-edit target is missing, non-regular, or outside the isolated trial"}, trial)
    edited_file.write_bytes(edited_file.read_bytes() + b"\nUser-owned local edit.\n")
    snapshots["after_local_edit"] = _snapshot(operation_root)
    events.append({"runner_stage": "after_local_edit"})

    uninstalled, error = run_stage("after_uninstall", _lifecycle_prompt(operation_root, "after_uninstall"))
    if error or uninstalled is None or uninstalled[0].returncode != 0:
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": f"safe-uninstall lifecycle process failed: {error or 'nonzero exit'}"}, trial)
    stage_reports["after_uninstall"] = uninstalled[1]
    snapshots["after_uninstall"] = _snapshot(operation_root)
    events.extend([{"runner_stage": "after_uninstall"}, {"runner_stage": "neighbor_preserved"}])

    final, error = run_stage("after_final_reinstall", _lifecycle_prompt(operation_root, "after_final_reinstall", "fixture-v2"))
    if error or final is None or final[0].returncode != 0:
        return _trial_result({**base, "status": "NOT_ASSESSED", "reason": f"final-reinstall lifecycle process failed: {error or 'nonzero exit'}"}, trial)
    stage_reports["after_final_reinstall"] = final[1]
    snapshots["after_final_reinstall"] = _snapshot(operation_root)
    events.append({"runner_stage": "after_final_reinstall"})

    after = snapshots["after_initial_install"]
    artifact_ok, artifact_reason = _artifact_ok(case, before, after, True)
    install_ok, install_reason = _install_evidence_ok(case, report, before, after, {
        "snapshots": snapshots,
        "stage_reports": stage_reports,
        "source_revisions": [case.get("_resolved_revision"), changed_revision],
        "source_revision_hashes": {case.get("_resolved_revision"): initial_hashes, changed_revision: changed_hashes},
        "edited_path": edited_path,
    })
    activation = _runtime_activation(events)
    lifecycle_evidence = {
        "snapshots": snapshots,
        "stage_reports": stage_reports,
        "source_revisions": [case.get("_resolved_revision"), changed_revision],
        "source_revision_hashes": {case.get("_resolved_revision"): initial_hashes, changed_revision: changed_hashes},
        "edited_path": edited_path,
        "processes": process_rows,
    }
    trace_matches = _trace_matches(case, events)
    status = "PASS" if (
        initial_process.returncode == 0 and artifact_ok and install_ok and trace_matches
        and activation == "loaded" and len(process_rows) == 5
        and all(row["returncode"] == 0 and row["process_observed"] for row in process_rows)
    ) else "NOT_ASSESSED"
    reason = "runner observed each owned INSTALL lifecycle transition" if status == "PASS" else (
        "runtime did not expose the required skill-load signal" if activation != "loaded" else install_reason
    )
    return _trial_result({
        **base,
        "status": status,
        "observed": report.get("disposition"),
        "runtime_observed": activation == "loaded",
        "runtime_evidence": {"skill_discovery": "NOT_ASSESSED", "explicit_invocation": "NOT_REQUESTED", "implicit_activation": activation or "NOT_ASSESSED", "behavior": "OBSERVED" if status == "PASS" else "NOT_ASSESSED"},
        "activation": activation,
        "process_observed": all(row["process_observed"] for row in process_rows),
        "trace_matches": trace_matches,
        "installation_observed": install_ok,
        "installation_reason": install_reason,
        "artifact_ok": artifact_ok,
        "artifact_reason": artifact_reason,
        "changed_paths": sorted(_changed_paths(before, after)),
        "cost_metrics": _cost_metrics(events, _changed_paths(before, after)),
        "trace_events": events,
        "before_snapshot": before,
        "after_snapshot": after,
        "lifecycle_evidence": lifecycle_evidence,
        "final_report": report,
        "events": sum(row["event_count"] for row in process_rows),
        "returncode": initial_process.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "reason": reason,
    }, trial)


def _run_once(
    case: dict,
    runtime: str,
    model: str,
    reasoning_effort: str,
    timeout: int,
    skill_dir: Path,
    with_skill: bool,
    trial_context: dict | None = None,
    runtime_status: str = "READY",
) -> dict:
    trial = _trial_metadata(
        skill_dir,
        case,
        "with_skill" if with_skill else "without_skill",
        trial_context,
        runtime_status=runtime_status,
    )
    with _fixture(skill_dir, with_skill, case) as fixture:
        operation_root = fixture / "project" if case["id"] == "audit-localize" else fixture
        prompt = _runtime_prompt(case, operation_root)
        base = {
            "case_id": case["id"],
            "kind": case["kind"],
            "expected": case["expected"],
            "condition": "with_skill" if with_skill else "without_skill",
            "fixture": ("project/.agents/skills/skill-creator" if case["id"] == "audit-localize" else ".agents/skills/skill-creator") if with_skill else "no skill fixture",
            "runtime_evidence": {
                "skill_discovery": "NOT_ASSESSED",
                "explicit_invocation": "NOT_REQUESTED",
                "implicit_activation": "NOT_ASSESSED",
                "behavior": "NOT_ASSESSED",
            },
        }
        if case.get("kind") == "INSTALL" and case.get("installation_outcome") == "INSTALLED":
            base["source_revision_resolved"] = case.get("_resolved_revision")
            base["source_license_resolved"] = case.get("_resolved_license")
        if not shutil.which(runtime):
            return _trial_result(
                {**base, "status": "NOT_ASSESSED", "reason": f"runtime not found: {runtime}"},
                trial,
            )
        if case.get("id") == "install-owned-lifecycle" and with_skill:
            return _run_owned_lifecycle(
                case, runtime, model, reasoning_effort, timeout, fixture, operation_root,
                base, trial, _subprocess_env(),
            )
        sandbox = "read-only" if case["kind"] in {"routing", "ACTION"} else "workspace-write"
        command = [
            runtime, "exec", "--model", model, "-c", f'model_reasoning_effort="{reasoning_effort}"',
            "--json", "--ephemeral", "--sandbox", sandbox,
            "--skip-git-repo-check", "--ignore-user-config", "--add-dir", str(fixture),
            "--add-dir", str(fixture / ".agents"), "--cd",
            str(fixture / "project" if case["id"] == "audit-localize" else fixture), prompt,
        ]
        base["command"] = command
        # Reuse the caller's authenticated CODEX_HOME. The fixture remains isolated;
        # an empty per-case home only measures auth retry behavior, not skill behavior.
        environment = _subprocess_env()
        before_snapshot = _snapshot(operation_root)
        started = time.monotonic()
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False, env=environment)
        except subprocess.TimeoutExpired as exc:
            partial_stdout = str(exc.stdout or "")
            partial_stderr = str(exc.stderr or "")
            timeout_class = _timeout_class(partial_stderr)
            return _trial_result({
                **base,
                "status": "NOT_ASSESSED",
                "timeout_class": timeout_class,
                "reason": f"runtime {timeout_class.lower()} after {timeout}s",
                "stdout_tail": partial_stdout.splitlines()[-20:],
                "stderr_tail": partial_stderr.splitlines()[-20:],
            }, trial)
        stdout = process.stdout or ""
        events = _events(stdout)
        report = _json_object(_final_text(events))
        key = "selected_workflow" if case["kind"] == "ACTION" else ("selected_skill" if case["kind"] == "routing" else "disposition")
        observed = report.get(key)
        activation = _runtime_activation(events)
        loaded = activation == "loaded"
        process_observed = _process_observed(events)
        trace_matches = _trace_matches(case, events)
        after_snapshot = _snapshot(operation_root)
        changed_paths = _changed_paths(before_snapshot, after_snapshot)
        artifact_ok, artifact_reason = _artifact_ok(case, before_snapshot, after_snapshot, with_skill)
        necessity_ok, necessity_reason = _necessity_ok(case, report)
        install_ok, install_reason = _install_evidence_ok(case, report, before_snapshot, after_snapshot)
        coexistence_fixture = (((fixture / "project") if case["id"] == "audit-localize" else fixture) / ".fixture-coexistence").is_file()
        side_effect_free = not changed_paths
        runtime_evidence = {
            "skill_discovery": "NOT_ASSESSED",
            "explicit_invocation": "NOT_REQUESTED",
            "implicit_activation": activation or "NOT_ASSESSED",
            "behavior": "OBSERVED" if observed is not None and (case["kind"] in {"routing", "ACTION"} or (process_observed and trace_matches and artifact_ok and install_ok)) else "NOT_ASSESSED",
        }
        unavailable = any(
            marker in (process.stderr or "").lower()
            for marker in ("401 unauthorized", "missing bearer", "authentication")
        )
        if process.returncode != 0 and (not events or unavailable):
            status, reason = "NOT_ASSESSED", f"runtime exit {process.returncode}"
        elif process.returncode != 0:
            status, reason = "FAIL", f"runtime exit {process.returncode}"
        elif not with_skill:
            if observed is None or not process_observed:
                status, reason = "NOT_ASSESSED", "baseline outcome or process evidence was not observed"
            elif case["kind"] not in {"routing", "ACTION"} and not artifact_ok:
                status, reason = "NOT_ASSESSED", artifact_reason
            else:
                status, reason = "OBSERVED", "baseline output and evidence recorded without skill fixture"
        elif case["kind"] in {"routing", "ACTION"}:
            status, reason = _routing_status(case, activation, observed)
        elif activation is None:
            status, reason = "NOT_ASSESSED", "runtime did not expose a skill-load signal"
        elif observed != case["expected"]:
            status, reason = "FAIL", f"expected {case['expected']}, observed {observed!r}"
        elif case["kind"] in {"CREATE", "UPDATE", "AUDIT"} and with_skill and not necessity_ok:
            status, reason = "FAIL", necessity_reason
        elif case["kind"] == "INSTALL" and with_skill and not install_ok:
            status = "NOT_ASSESSED" if case.get("id") == "install-owned-lifecycle" else "FAIL"
            reason = install_reason
        elif with_skill and "G5_COEXISTENCE" in _case_gates(case) and not coexistence_fixture:
            status, reason = "FAIL", "coexistence fixture evidence is missing"
        elif case["kind"] not in {"routing", "ACTION"} and not (process_observed and trace_matches and artifact_ok):
            status, reason = "FAIL", artifact_reason if not artifact_ok else "required process trace was not observed"
        elif observed == case["expected"]:
            status, reason = "PASS", "expected outcome, process trace, and artifact evidence observed"
        else:
            status, reason = "NOT_ASSESSED", "runtime outcome unavailable"
        cost_metrics = _cost_metrics(events, changed_paths)
        return _trial_result({
            **base,
            "status": status,
            "observed": observed,
            "runtime_observed": loaded,
            "runtime_evidence": runtime_evidence,
            "activation": activation,
            "process_observed": process_observed,
            "trace_matches": trace_matches,
            "necessity_observed": necessity_ok,
            "necessity_reason": necessity_reason,
            "installation_observed": install_ok,
            "installation_reason": install_reason,
            "coexistence_fixture": coexistence_fixture,
            "side_effect_free": side_effect_free,
            "artifact_ok": artifact_ok,
            "artifact_reason": artifact_reason,
            "changed_paths": sorted(changed_paths),
            "cost_metrics": cost_metrics,
            "trace_events": events,
            "before_snapshot": before_snapshot,
            "after_snapshot": after_snapshot,
            "final_report": report,
            "events": len(events),
            "returncode": process.returncode,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "stdout_bytes": len(stdout.encode("utf-8")),
            "reason": reason,
            "stderr": (process.stderr or "").splitlines()[-5:],
        }, trial)


def _action_metrics(results: list[dict], cases: list[dict]) -> dict:
    expected = len(cases)
    expected_ids = {case.get("id") for case in cases}
    result_ids = [item.get("case_id") for item in results]
    assessed = [item for item in results if item.get("status") in {"PASS", "FAIL"}]
    if any(item.get("status") == "FAIL" for item in results):
        status = "FAIL"
    elif (
        len(results) == expected
        and set(result_ids) == expected_ids
        and len(assessed) == expected
        and all(
            _action_record_is_valid(item, {**case, "kind": "ACTION"})
            for item in results
            for case in cases
            if case.get("id") == item.get("case_id")
        )
    ):
        status = "PASS"
    else:
        status = "NOT_ASSESSED"
    return {
        "status": status,
        "assessed_cases": len(assessed),
        "total_cases": len(results),
        "expected_cases": expected,
    }


def _action_record_is_valid(item: dict, case: dict) -> bool:
    if (
        item.get("kind") != "ACTION"
        or item.get("condition") != "with_skill"
        or item.get("status") != "PASS"
        or item.get("expected") != case.get("expected")
        or item.get("observed") != case.get("expected")
        or item.get("activation") != "loaded"
        or item.get("runtime_observed") is not True
        or item.get("process_observed") is not True
        or item.get("trace_matches") is not True
        or item.get("artifact_ok") is not True
    ):
        return False
    recomputed = _recomputed_record(item, case)
    if recomputed is None:
        return False
    return all(
        item.get(field) == recomputed.get(field)
        for field in (
            "observed",
            "activation",
            "process_observed",
            "trace_matches",
            "changed_paths",
            "artifact_ok",
            "runtime_evidence",
            "cost_metrics",
        )
    )


def _routing_metrics(results: list[dict], cases: list[dict], action_results: list[dict] | None = None, action_cases: list[dict] | None = None) -> dict:
    by_id = {case["id"]: case for case in cases}
    assessed = [result for result in results if result.get("status") in {"PASS", "FAIL"} and result.get("observed") is not None]
    tp = sum(by_id[result["case_id"]].get("polarity") == "positive" for result in assessed if result.get("observed") == "skill-creator")
    fn = sum(by_id[result["case_id"]].get("polarity") == "positive" for result in assessed if result.get("observed") != "skill-creator")
    fp = sum(by_id[result["case_id"]].get("polarity") == "negative" for result in assessed if result.get("observed") == "skill-creator")
    tn = sum(by_id[result["case_id"]].get("polarity") == "negative" for result in assessed if result.get("observed") != "skill-creator")
    denominator_precision = tp + fp
    denominator_recall = tp + fn
    expected_cases = [case for case in cases if case.get("kind") == "routing"]
    complete = len(results) == len(expected_cases) and bool(results)
    action = _action_metrics(action_results, action_cases) if action_results is not None and action_cases is not None else {"status": "NOT_REQUESTED", "assessed_cases": 0, "total_cases": 0, "expected_cases": 0}
    status = "PASS" if complete and len(assessed) == len(results) and not any(item.get("status") == "FAIL" for item in results) and action["status"] in {"PASS", "NOT_REQUESTED"} else (
        "FAIL" if any(item.get("status") == "FAIL" for item in results) else "NOT_ASSESSED"
    )
    if action["status"] == "FAIL":
        status = "FAIL"
    elif action["status"] == "NOT_ASSESSED" and status == "PASS":
        status = "NOT_ASSESSED"
    return {
        "status": status,
        "TP": tp, "FN": fn, "FP": fp, "TN": tn,
        "precision": round(tp / denominator_precision, 3) if denominator_precision else None,
        "recall": round(tp / denominator_recall, 3) if denominator_recall else None,
        "false_positive_rate": round(fp / (fp + tn), 3) if fp + tn else None,
        "assessed_cases": len(assessed),
        "total_cases": len(results),
        "action_status": action["status"],
        "action_assessed_cases": action["assessed_cases"],
        "action_total_cases": action["total_cases"],
        "action_expected_cases": action["expected_cases"],
    }


def _case_gate_status(results: list[dict], gate: str) -> str:
    owned = [item for item in results if item.get("condition") == "with_skill" and gate in item.get("gates", [item.get("gate")])]
    if not owned:
        return "NOT_ASSESSED"
    if any(item.get("status") == "FAIL" for item in owned):
        return "FAIL"
    return "PASS" if all(item.get("status") == "PASS" for item in owned) else "NOT_ASSESSED"


def _compare(before_path: Path, after_path: Path, cases_path: Path | None = None, expected_binding: dict | None = None) -> dict:
    try:
        before = json.loads(before_path.read_text(encoding="utf-8"))
        after = json.loads(after_path.read_text(encoding="utf-8"))
        case_data = load_cases(cases_path) if cases_path else {}
        expected_cases = case_data.get("cases", [])
        expected_action_cases = case_data.get("action_cases", [])
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        return {"status": "REJECT", "validation_gated": False, "reason": "invalid before/after/case evidence"}
    bindings = [before.get("evidence_binding"), after.get("evidence_binding")]
    if not all(_valid_evidence_binding(binding) for binding in bindings) or bindings[0] != bindings[1]:
        return {"status": "REJECT", "validation_gated": False, "reason": "before/after evidence is not revision-bound"}
    if expected_binding is not None and bindings[0] != expected_binding:
        return {"status": "REJECT", "validation_gated": False, "reason": "evidence binding does not match the requested repository snapshot"}
    def with_skill(data: dict) -> list[dict]:
        return [item for item in data.get("results", []) if item.get("condition") == "with_skill"]

    def without_skill(data: dict) -> list[dict]:
        return [item for item in data.get("results", []) if item.get("condition") == "without_skill"]

    def evidence_complete(data: dict, results: list[dict], baseline_results: list[dict]) -> bool:
        coverage = data.get("coverage", {})
        gates = data.get("gates", {})
        routing = data.get("routing", {})
        cases_by_id = {case["id"]: case for case in expected_cases}
        if coverage.get("full_corpus") is not True or set(gates) != set(GATES):
            return False
        if any(gates.get(gate) not in {"PASS", "FAIL", "NOT_ASSESSED"} for gate in GATES):
            return False
        if gates.get("G7_INDEPENDENT_REVIEW") != "NOT_ASSESSED":
            return False
        if any(gates.get(gate) != "PASS" for gate in GATES if gate != "G7_INDEPENDENT_REVIEW"):
            return False
        action_results = data.get("action_cases")
        action_by_id = {case["id"]: case for case in expected_action_cases}
        if not isinstance(action_results, list) or {item.get("case_id") for item in action_results} != set(action_by_id) or len(action_results) != len(action_by_id):
            return False
        records = [*action_results, *results, *baseline_results]
        trial_ids = [item.get("trial", {}).get("trial_id") for item in records if isinstance(item.get("trial"), dict)]
        if len(trial_ids) != len(set(trial_ids)):
            return False
        for item in action_results:
            case = action_by_id.get(item.get("case_id"))
            if not case or not _trial_record_is_valid(item, bindings[0]) or not _action_record_is_valid(item, {**case, "kind": "ACTION"}):
                return False
        if routing.get("status") not in {"PASS", "FAIL"} or not all(
            isinstance(routing.get(field), (int, float)) for field in ("precision", "recall")
        ):
            return False
        routing_results = [item for item in results if item.get("kind") == "routing"]
        expected_routing_status = "FAIL" if any(item.get("status") == "FAIL" for item in routing_results) else "PASS"
        if routing.get("status") != expected_routing_status or gates.get("G3_ROUTING") != routing.get("status"):
            return False
        expected_paired = {case["id"] for case in expected_cases if case.get("paired") is True}
        paired = data.get("paired")
        if not isinstance(paired, list) or {item.get("case_id") for item in paired} != expected_paired:
            return False
        if gates.get("G6_EFFICIENCY") != "PASS" or any(
            item.get("added_value_observed") is not True
            or item.get("cost_comparison_observed") is not True
            or item.get("outcome_delta_observed") is not True
            for item in paired
        ):
            return False
        paired_cases = {case["id"]: case for case in expected_cases if case.get("paired") is True}
        baseline_by_case = {item.get("case_id"): item for item in baseline_results}
        with_by_case = {item.get("case_id"): item for item in results}
        for item in results + baseline_results:
            case = cases_by_id.get(item.get("case_id"))
            if not case or not _trial_record_is_valid(item, bindings[0]) or any(
                item.get(field) != expected
                for field, expected in (
                    ("kind", case["kind"]),
                    ("expected", case["expected"]),
                    ("partition", case["partition"]),
                    ("gate", case["gate"]),
                    ("gates", _case_gates(case)),
                )
            ):
                return False
        if set(baseline_by_case) != set(paired_cases) or len(baseline_results) != len(paired_cases):
            return False
        for case_id in paired_cases:
            baseline = baseline_by_case[case_id]
            if (
                baseline.get("status") != "OBSERVED"
                or baseline.get("observed") is None
                or not all(baseline.get(field) is True for field in ("process_observed", "trace_matches", "artifact_ok"))
            ):
                return False
            metrics = baseline.get("cost_metrics")
            if not isinstance(metrics, dict) or not all(isinstance(metrics.get(field), int) for field in ("tool_calls", "command_count", "artifact_count")):
                return False
            recomputed = _paired_evidence(with_by_case.get(case_id), baseline)
            summary = next(item for item in paired if item.get("case_id") == case_id)
            if any(summary.get(field) != recomputed.get(field) for field in recomputed):
                return False
        for item in results:
            case = cases_by_id[item["case_id"]]
            if item.get("status") != "PASS" or item.get("observed") != case["expected"]:
                return False
            recomputed = _recomputed_record(item, case)
            if recomputed is None or any(item.get(field) != recomputed.get(field) for field in (
                "observed", "activation", "process_observed", "trace_matches", "changed_paths",
                "artifact_ok", "necessity_observed", "installation_observed", "installation_reason",
                "coexistence_fixture", "cost_metrics", "runtime_evidence",
            )):
                return False
            if case["kind"] == "INSTALL" and recomputed["installation_observed"] is not True:
                return False
            activation = item.get("activation")
            if item.get("kind", "routing") == "routing":
                if activation not in {"loaded", "unloaded"}:
                    return False
                continue
            if activation != "loaded" or not all(item.get(field) is True for field in ("process_observed", "trace_matches", "artifact_ok")):
                return False
            metrics = item.get("cost_metrics")
            if not isinstance(metrics, dict) or not all(isinstance(metrics.get(field), int) for field in ("tool_calls", "command_count", "artifact_count")):
                return False
        for item in baseline_results:
            case = cases_by_id[item["case_id"]]
            recomputed = _recomputed_record(item, case)
            if recomputed is None or any(item.get(field) != recomputed.get(field) for field in (
                "observed", "activation", "process_observed", "trace_matches", "changed_paths",
                "artifact_ok", "necessity_observed", "installation_observed", "installation_reason",
                "coexistence_fixture", "cost_metrics", "runtime_evidence",
            )):
                return False
        recomputed_routing = []
        for item in results:
            if item.get("kind") != "routing":
                continue
            case = cases_by_id[item["case_id"]]
            recomputed = _recomputed_record(item, case)
            if recomputed is None:
                return False
            status, _ = _routing_status(case, recomputed["activation"], recomputed["observed"])
            recomputed_routing.append({"case_id": item["case_id"], "status": status, "observed": recomputed["observed"]})
        expected_routing = _routing_metrics(recomputed_routing, expected_cases, action_results, expected_action_cases)
        if any(routing.get(field) != expected_routing.get(field) for field in (
            "status", "TP", "FN", "FP", "TN", "precision", "recall", "false_positive_rate",
            "assessed_cases", "total_cases", "action_status", "action_assessed_cases", "action_total_cases", "action_expected_cases",
        )):
            return False
        for gate in GATES - {"G6_EFFICIENCY", "G7_INDEPENDENT_REVIEW"}:
            if _case_gate_status(results, gate) != gates.get(gate):
                return False
        return True

    before_results = with_skill(before)
    after_results = with_skill(after)
    before_baseline = without_skill(before)
    after_baseline = without_skill(after)
    before_keys = {(item.get("case_id"), item.get("partition")) for item in before_results}
    after_keys = {(item.get("case_id"), item.get("partition")) for item in after_results}
    expected_keys = {(case["id"], case["partition"]) for case in expected_cases}
    canonical_keys = {(case_id, partition) for partition, case_ids in EXPECTED_PARTITIONS.items() for case_id in case_ids}
    expected_baseline_keys = {(case["id"], case["partition"]) for case in expected_cases if case.get("paired") is True}
    before_baseline_keys = {(item.get("case_id"), item.get("partition")) for item in before_baseline}
    after_baseline_keys = {(item.get("case_id"), item.get("partition")) for item in after_baseline}
    statuses = {"PASS", "FAIL"}
    comparable = (
        len(expected_cases) == EXPECTED_CASE_COUNT
        and sum(case.get("kind") == "routing" for case in expected_cases) == EXPECTED_ROUTING_CASE_COUNT
        and sum(case.get("kind") != "routing" for case in expected_cases) == EXPECTED_LIFECYCLE_CASE_COUNT
        and expected_keys == canonical_keys
        and bool(before_results)
        and before_keys == after_keys
        and before_keys == expected_keys
        and len(before_results) == len(expected_keys)
        and len(after_results) == len(expected_keys)
        and before_baseline_keys == after_baseline_keys == expected_baseline_keys
        and len(before_baseline) == len(expected_baseline_keys)
        and len(after_baseline) == len(expected_baseline_keys)
        and all(item.get("status") in statuses for item in before_results + after_results)
        and evidence_complete(before, before_results, before_baseline)
        and evidence_complete(after, after_results, after_baseline)
    )

    def score(results: list[dict], partition: str, status: str = "PASS") -> int:
        return sum(item.get("status") == status and item.get("partition") == partition for item in results)

    before_held = score(before_results, "held_out")
    after_held = score(after_results, "held_out")
    before_regression = score(before_results, "regression", "FAIL")
    after_regression = score(after_results, "regression", "FAIL")
    before_must_pass_failures = sum(item.get("partition") == "must_pass" and item.get("status") != "PASS" for item in before_results)
    after_must_pass_failures = sum(item.get("partition") == "must_pass" and item.get("status") != "PASS" for item in after_results)
    before_by_case = {item.get("case_id"): item for item in before_results}
    after_by_case = {item.get("case_id"): item for item in after_results}
    case_deltas = [
        {
            "case_id": case_id,
            "before_status": before_by_case[case_id].get("status"),
            "after_status": after_by_case[case_id].get("status"),
            "before_observed": before_by_case[case_id].get("observed"),
            "after_observed": after_by_case[case_id].get("observed"),
            "before_changed_paths": before_by_case[case_id].get("changed_paths", []),
            "after_changed_paths": after_by_case[case_id].get("changed_paths", []),
            "status_changed": before_by_case[case_id].get("status") != after_by_case[case_id].get("status"),
        }
        for case_id in sorted(before_by_case)
    ]
    before_routing = before.get("routing", {})
    after_routing = after.get("routing", {})
    routing_comparable = all(
        isinstance(payload.get(field), (int, float))
        for payload in (before_routing, after_routing)
        for field in ("precision", "recall")
    )
    routing_non_regressing = routing_comparable and (
        after_routing["precision"] >= before_routing["precision"]
        and after_routing["recall"] >= before_routing["recall"]
    )
    return {
        "status": "PASS" if comparable and before_must_pass_failures == 0 and after_must_pass_failures == 0 and after_held > 0 and after_held >= before_held and after_regression <= before_regression and routing_non_regressing else "REJECT",
        "held_out_before": before_held,
        "held_out_after": after_held,
        "regression_failures_before": before_regression,
        "regression_failures_after": after_regression,
        "must_pass_failures_before": before_must_pass_failures,
        "must_pass_failures_after": after_must_pass_failures,
        "routing_precision_before": before_routing.get("precision"),
        "routing_precision_after": after_routing.get("precision"),
        "routing_recall_before": before_routing.get("recall"),
        "routing_recall_after": after_routing.get("recall"),
        "case_deltas": case_deltas,
        "validation_gated": comparable,
    }


def run(path: Path, skill_dir: Path, runtime: str, model: str, reasoning_effort: str, timeout: int, case_ids: set[str] | None, stage: str = "full", base_ref: str | None = None, candidate_ref: str | None = None) -> dict:
    data = load_cases(path)
    evidence_binding = _evidence_binding(skill_dir, path, base_ref, candidate_ref)
    trial_context = {
        "candidate_revision": evidence_binding.get("candidate_head"),
        "candidate_tree_sha256": evidence_binding.get("skill_tree_sha256"),
        "base_identity": evidence_binding.get("base_head"),
        "test_fingerprint": evidence_binding.get("cases_sha256") or _trial_fingerprint(data["cases"]),
    }
    cases = _cases_for_stage(data, stage, case_ids)
    action_cases = _selected_action_cases(data, stage, case_ids)
    if candidate_ref is not None and evidence_binding.get("candidate_head") is None:
        preflight = {
            "status": "CANDIDATE_MISMATCH",
            "reason": "requested candidate is not the current repository HEAD",
        }
    else:
        preflight = _runtime_preflight(runtime, timeout)
    if preflight["status"] != "READY":
        unavailable_results = []
        unavailable_actions = []
        for action_case in action_cases:
            action = {**action_case, "kind": "ACTION"}
            unavailable_actions.append(_unassessed_case(
                action, skill_dir, preflight["reason"], trial_context, preflight["status"],
            ))
        for case in cases:
            result = _unassessed_case(
                case, skill_dir, preflight["reason"], trial_context, preflight["status"],
            )
            result.update({"partition": case["partition"], "gate": case["gate"], "gates": _case_gates(case)})
            unavailable_results.append(result)
            if case.get("paired"):
                baseline = _unassessed_case(
                    case, skill_dir, preflight["reason"], trial_context, preflight["status"], "without_skill",
                )
                baseline.update({"partition": case["partition"], "gate": case["gate"], "gates": _case_gates(case)})
                unavailable_results.append(baseline)
        return {
            "schema_version": 2, "skill": "skill-creator",
            "coverage": {"requested_cases": len(cases), "total_cases": len(data["cases"]), "full_corpus": False},
            "runtime_preflight": preflight, "stage": stage,
            "evidence_binding": evidence_binding,
            "gates": {gate: "NOT_ASSESSED" for gate in GATES},
            "routing": {"status": "NOT_ASSESSED", "assessed_cases": 0, "total_cases": 0},
            "paired": [], "action_cases": unavailable_actions, "results": unavailable_results,
        }
    results = []
    action_results = []
    if action_cases:
        for action_case in action_cases:
            runtime_case = {
                **action_case,
                "kind": "ACTION",
                "trace_markers": [],
            }
            action_results.append(_run_once(
                runtime_case, runtime, model, reasoning_effort, timeout, skill_dir, True,
                trial_context, preflight["status"],
            ))
    for case in cases:
        result = _run_once(
            case, runtime, model, reasoning_effort, timeout, skill_dir, True,
            trial_context, preflight["status"],
        )
        result["runtime_version"] = preflight.get("runtime_version")
        result["partition"] = case["partition"]
        result["gate"] = case["gate"]
        result["gates"] = _case_gates(case)
        results.append(result)
        if case.get("paired"):
            baseline = _run_once(
                case, runtime, model, reasoning_effort, timeout, skill_dir, False,
                trial_context, preflight["status"],
            )
            baseline["runtime_version"] = preflight.get("runtime_version")
            baseline["partition"] = case["partition"]
            baseline["gate"] = case["gate"]
            baseline["gates"] = _case_gates(case)
            results.append(baseline)
    routing_ids = {case["id"] for case in cases if case["kind"] == "routing"}
    routing = _routing_metrics(
        [item for item in results if item["condition"] == "with_skill" and item["case_id"] in routing_ids],
        cases,
        action_results,
        action_cases,
    )
    paired = []
    for case in cases:
        if not case.get("paired"):
            continue
        pair = [item for item in results if item["case_id"] == case["id"]]
        with_skill = next((item for item in pair if item["condition"] == "with_skill"), None)
        without_skill = next((item for item in pair if item["condition"] == "without_skill"), None)
        paired.append({
            "case_id": case["id"],
            "with_status": with_skill.get("status") if with_skill else "NOT_ASSESSED",
            "without_status": without_skill.get("status") if without_skill else "NOT_ASSESSED",
            "with_runtime_observed": bool(with_skill and with_skill.get("runtime_observed")),
            "without_runtime_observed": bool(without_skill and without_skill.get("runtime_observed")),
            "with_process_observed": bool(with_skill and with_skill.get("process_observed")),
            "without_process_observed": bool(without_skill and without_skill.get("process_observed")),
            **_paired_evidence(with_skill, without_skill),
        })
    structure_check = subprocess.run(
        [sys.executable, str(skill_dir / "scripts" / "quick_validate.py"), str(skill_dir)],
        capture_output=True, text=True, check=False, env=_subprocess_env(),
    )
    structure_ok = structure_check.returncode == 0 and _package_structure_ok(skill_dir)
    provenance_ok = _provenance_ok(skill_dir)
    behavior_cases = [case for case in cases if case["kind"] != "routing"]
    behavior_results = [item for item in results if item["condition"] == "with_skill" and item["case_id"] in {case["id"] for case in behavior_cases}]
    paired_by_id = {item["case_id"]: item for item in paired}
    full_corpus = len(cases) == len(data["cases"])
    paired_complete = len(paired) == sum(case.get("paired") is True for case in cases)
    status_by_gate = {gate: _case_gate_status(results, gate) for gate in GATES}
    status_by_gate["G1_STRUCTURE"] = "FAIL" if not structure_ok else status_by_gate["G1_STRUCTURE"]
    status_by_gate["G2_PROVENANCE"] = "FAIL" if not provenance_ok else status_by_gate["G2_PROVENANCE"]
    status_by_gate["G3_ROUTING"] = routing["status"]
    if not full_corpus:
        for gate in GATES - {"G7_INDEPENDENT_REVIEW"}:
            if status_by_gate[gate] == "PASS":
                status_by_gate[gate] = "NOT_ASSESSED"
    efficiency_cases = [case for case in cases if "G6_EFFICIENCY" in _case_gates(case)]
    efficiency_pairs = [paired_by_id[case["id"]] for case in efficiency_cases if case.get("paired") and case["id"] in paired_by_id]
    status_by_gate["G6_EFFICIENCY"] = (
        "FAIL" if any(item.get("with_status") == "FAIL" for item in efficiency_pairs)
        else "PASS" if full_corpus and efficiency_pairs and len(efficiency_pairs) == len(efficiency_cases)
        and all(item["added_value_observed"] for item in efficiency_pairs)
        else "NOT_ASSESSED"
    )
    return {
        "schema_version": 2,
        "skill": "skill-creator",
        "coverage": {"requested_cases": len(cases), "total_cases": len(data["cases"]), "full_corpus": len(cases) == len(data["cases"])},
        "model": model,
        "reasoning_effort": reasoning_effort,
        "runtime_version": preflight.get("runtime_version"),
        "runtime_preflight": preflight,
        "evidence_binding": evidence_binding,
        "stage": stage,
        "gates": status_by_gate,
        "routing": routing,
        "paired": paired,
        "action_cases": action_results,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--case-id", action="append")
    parser.add_argument("--runtime", default="codex")
    parser.add_argument("--model", default="gpt-6-luna")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--stage", choices=("smoke", "lifecycle", "full"), default="full")
    parser.add_argument("--results", type=Path)
    parser.add_argument("--compare-before", type=Path)
    parser.add_argument("--compare-after", type=Path)
    parser.add_argument("--base", help="Base Git revision required for revision-bound evidence")
    parser.add_argument("--candidate", help="Candidate Git revision required for revision-bound evidence")
    args = parser.parse_args()
    errors = validate(args.cases)
    if errors:
        for error in errors:
            print(f"FAIL eval cases: {error}")
        return 1
    if args.compare_before and args.compare_after:
        expected_binding = _evidence_binding(args.skill_dir, args.cases, args.base, args.candidate)
        report = _compare(args.compare_before, args.compare_after, args.cases, expected_binding)
        print(json.dumps(report, sort_keys=True))
        return 0 if report["status"] == "PASS" else 1
    if not args.run:
        data = load_cases(args.cases)
        print(f"OK eval cases: {len(data['gates'])} gates, {sum(case['kind'] == 'routing' for case in data['cases'])} routing and {sum(case['kind'] != 'routing' for case in data['cases'])} lifecycle cases")
        return 0
    if not args.base or not args.candidate:
        print("FAIL eval cases: --run requires both --base and --candidate for revision-bound evidence")
        return 1
    report = run(args.cases, args.skill_dir, args.runtime, args.model, args.reasoning_effort, args.timeout, set(args.case_id) if args.case_id else None, args.stage, args.base, args.candidate)
    if args.results:
        args.results.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 1 if any(status == "FAIL" for status in report["gates"].values()) else (2 if any(status == "NOT_ASSESSED" for status in report["gates"].values()) else 0)


if __name__ == "__main__":
    sys.exit(main())
