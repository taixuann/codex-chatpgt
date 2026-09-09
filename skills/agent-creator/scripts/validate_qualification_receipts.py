#!/usr/bin/env python3
"""Validate durable per-run qualification receipts, or derive them once."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

CASES = ("HR-01", "HR-02", "HR-03")
PARTITIONS = ("direct", "indirect", "noisy", "context_heavy", "near_sibling")
EXCLUSION_CATEGORIES = ("NO_PROMPT_PROVIDED", "NONCOMPLIANT_TRACE", "PROCESS_FAILURE", "USAGE_LIMIT")
MODEL = "gpt-5.6-luna"
REASONING = "medium"
CLI = "codex-cli 0.149.1"
EVIDENCE_ONLY_UPDATE_PATHS = {
    "skills/agent-creator/references/qualification-evidence.jsonl",
    "skills/agent-creator/references/qualification-prompts.jsonl",
    "skills/agent-creator/references/qualification-receipts.jsonl",
    "skills/agent-creator/references/qualification-results.md",
    "skills/agent-creator/references/qualification-discovery.json",
    "skills/agent-creator/scripts/validate_qualification_receipts.py",
    "skills/agent-creator/scripts/test_validate_qualification_receipts.py",
}
NATIVE_EVIDENCE_ONLY_UPDATE_PATHS = EVIDENCE_ONLY_UPDATE_PATHS | {
    "skills/agent-creator/references/qualification-native-runtime.json",
    "skills/agent-creator/references/qualification-native-no-delegation.json",
    "skills/agent-creator/references/qualification-native-forbidden-delegation.json",
    "skills/agent-creator/references/qualification-routing.jsonl",
    "skills/agent-creator/references/qualification-missing-capability.jsonl",
    "skills/agent-creator/references/qualification-scope.json",
    "skills/agent-creator/references/qualification-depth.json",
}
EVIDENCE_FILE = Path(__file__).parents[1] / "references" / "qualification-evidence.jsonl"
PROMPT_FILE = Path(__file__).parents[1] / "references" / "qualification-prompts.jsonl"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_revision(repo_root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def resolve_capture_revision_value(captured: str, repo_root: Path, allowlist: set[str]) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", captured):
        raise ValueError("capture revision must be a full git commit SHA")
    head = git_revision(repo_root)
    if captured == head:
        return head
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", captured, head],
        cwd=repo_root,
    ).returncode == 0
    if not ancestor:
        raise ValueError(f"receipts captured at {captured}, not fail-closed for HEAD {head}")
    changed = subprocess.run(
        ["git", "diff", "--name-only", f"{captured}..{head}"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if not changed or not set(changed) <= allowlist:
        raise ValueError(f"receipts captured at {captured}, not fail-closed for HEAD {head}")
    return captured


def resolve_capture_revision(records: list[dict], repo_root: Path) -> str:
    revisions = {record.get("capture_revision") for record in records}
    if len(revisions) != 1 or None in revisions:
        raise ValueError("receipt set must use one capture revision")
    return resolve_capture_revision_value(next(iter(revisions)), repo_root, EVIDENCE_ONLY_UPDATE_PATHS)


def validate_native_receipt(path: Path, repo_root: Path) -> str:
    data = json.loads(path.read_text())
    if "no_delegation_probes" in data:
        raise ValueError("native role-spawn receipt must not mix independently captured probes")
    required = {
        "capture_revision", "captured_at_utc", "fixture", "runtime", "script", "script_sha256",
        "requested_model", "requested_reasoning_effort", "model",
        "collab_spawn_event", "child_parent_relation", "role_identity",
        "return_completion", "native_skill_load", "implicit_activation",
        "child_thread_metadata", "qualification_status", "reason",
    }
    missing = sorted(field for field in required if field not in data)
    if missing:
        raise ValueError(f"native receipt missing required fields: {', '.join(missing)}")
    if data["fixture"] != "synthetic_only":
        raise ValueError("native receipt must identify its fixture as synthetic_only")
    if data["script"] != "skills/agent-creator/scripts/probe_runtime_agents.py":
        raise ValueError("native receipt is not bound to the production probe script")
    script_path = repo_root / data["script"]
    if not script_path.is_file() or sha256(script_path) != data["script_sha256"]:
        raise ValueError("native receipt is stale for the production probe script")
    if data["requested_model"] != MODEL or data["requested_reasoning_effort"] != REASONING:
        raise ValueError("native receipt runtime lane does not match the qualification contract")
    if data["model"] != MODEL:
        raise ValueError("native receipt effective model does not match the qualification lane")
    if data["qualification_status"] not in ("PASS", "NOT_ASSESSED"):
        raise ValueError("native receipt has an invalid qualification status")
    if data["qualification_status"] == "PASS":
        for field in ("collab_spawn_event", "child_parent_relation", "role_identity", "return_completion"):
            if data[field] != "OBSERVED":
                raise ValueError(f"native receipt does not prove required signal: {field}")
    if data["native_skill_load"] != "NOT_ASSESSED" or data["implicit_activation"] != "NOT_ASSESSED":
        raise ValueError("native receipt must preserve unavailable activation signals as NOT_ASSESSED")
    if not isinstance(data["child_thread_metadata"], list):
        raise ValueError("native receipt child metadata must be a list")
    if data["qualification_status"] == "PASS" and not data["child_thread_metadata"]:
        raise ValueError("native PASS receipt must retain child thread metadata")
    followups = data.get("follow_up_probes")
    if followups is not None:
        validate_follow_up_probes(followups, data.get("follow_up_capture_revision", data["capture_revision"]))
    return resolve_capture_revision_value(
        data["capture_revision"], repo_root, NATIVE_EVIDENCE_ONLY_UPDATE_PATHS
    )


def validate_follow_up_probes(probes: dict, capture_revision: str) -> None:
    """Validate compact native follow-up evidence without accepting model prose."""
    if not isinstance(probes, dict) or set(probes) != {
        "sibling_collision", "nested_depth", "project_scope", "readonly_sandbox"
    }:
        raise ValueError("native follow-up receipt must contain the four bounded probes")
    for name, probe in probes.items():
        if not isinstance(probe, dict):
            raise ValueError(f"follow-up probe is not an object: {name}")
        if probe.get("capture_revision") != capture_revision:
            raise ValueError(f"follow-up probe capture mismatch: {name}")
        if not isinstance(probe.get("runtime"), str) or not probe["runtime"].startswith("Codex Desktop/0.149.1"):
            raise ValueError(f"follow-up probe runtime is not exact: {name}")
        if probe.get("model") != MODEL or probe.get("reasoning") != REASONING:
            raise ValueError(f"follow-up probe runtime lane mismatch: {name}")
        if probe.get("timeout_seconds") != 120:
            raise ValueError(f"follow-up probe timeout is not bounded at 120 seconds: {name}")
        if not re.fullmatch(r"[0-9a-f]{64}", probe.get("output_sha256", "")):
            raise ValueError(f"follow-up probe is missing its output hash: {name}")
    sibling = probes["sibling_collision"]
    if not (
        sibling.get("status") == "PASS"
        and sibling.get("native_spawn_event") == "OBSERVED"
        and sibling.get("selected_role") == "probe-reviewer"
        and sibling.get("sibling_role") == "probe-worker"
        and sibling.get("role_identity") == "OBSERVED"
        and sibling.get("child_parent_relation") == "OBSERVED"
        and sibling.get("behavior") == "OBSERVED"
        and sibling.get("wrong_role_spawn_count") == 0
    ):
        raise ValueError("sibling collision follow-up is not independently bounded")
    depth = probes["nested_depth"]
    if not (
        depth.get("status") == "NOT_ASSESSED"
        and depth.get("requested_config") == {"agents": {"max_depth": 1}}
        and depth.get("parent_child_spawn") == "OBSERVED"
        and depth.get("nested_attempt") == "NOT_ASSESSED"
        and depth.get("grandchild_metadata") == "NOT_ASSESSED"
        and depth.get("depth_denial_event") == "NOT_ASSESSED"
    ):
        raise ValueError("nested-depth follow-up must preserve unavailable enforcement")
    project = probes["project_scope"]
    if not (
        project.get("status") == "NOT_ASSESSED"
        and project.get("project_config_present") == "OBSERVED"
        and project.get("native_spawn_event") == "OBSERVED"
        and project.get("behavior") == "OBSERVED"
        and project.get("marker") == "PROJECT-SCOPE-MARKER"
        and project.get("role_identity") == "NOT_ASSESSED"
    ):
        raise ValueError("project-scope follow-up must preserve missing role metadata")
    sandbox = probes["readonly_sandbox"]
    if not (
        sandbox.get("status") == "NOT_ASSESSED"
        and sandbox.get("role_identity") == "OBSERVED"
        and sandbox.get("marker_absent") == "OBSERVED"
        and sandbox.get("model_reported_denial") == "OBSERVED"
        and sandbox.get("native_denial_event") == "NOT_ASSESSED"
    ):
        raise ValueError("read-only sandbox follow-up must not promote model prose")


def _validate_probe_metadata(data: dict, repo_root: Path, required: set[str]) -> str:
    missing = sorted(field for field in required if field not in data)
    if missing:
        raise ValueError(f"native probe receipt missing required fields: {', '.join(missing)}")
    if data["fixture"] != "synthetic_only":
        raise ValueError("native probe receipt must identify its fixture as synthetic_only")
    if data["script"] != "skills/agent-creator/scripts/probe_runtime_agents.py":
        raise ValueError("native probe receipt is not bound to the production probe script")
    script_path = repo_root / data["script"]
    if not script_path.is_file() or sha256(script_path) != data["script_sha256"]:
        raise ValueError("native probe receipt is stale for the production probe script")
    if data["requested_model"] != MODEL or data["requested_reasoning_effort"] != REASONING:
        raise ValueError("native probe receipt runtime lane does not match the qualification contract")
    return resolve_capture_revision_value(
        data["capture_revision"], repo_root, NATIVE_EVIDENCE_ONLY_UPDATE_PATHS
    )


def validate_no_delegation_receipt(path: Path, repo_root: Path, scenario: str) -> str:
    data = json.loads(path.read_text())
    required = {
        "capture_revision", "captured_at_utc", "fixture", "runtime", "script", "script_sha256",
        "requested_model", "requested_reasoning_effort", "scenario", "parent_turn_completed",
        "native_spawn_event_count", "native_spawn_event_status", "return_completion",
        "native_events_observed",
    }
    revision = _validate_probe_metadata(data, repo_root, required)
    if data["scenario"] != scenario:
        raise ValueError("native no-delegation receipt has the wrong scenario")
    if data["native_spawn_event_count"] != 0 or data["native_spawn_event_status"] != "OBSERVED_ZERO":
        raise ValueError("native no-delegation receipt does not prove zero delegation events")
    if data["native_events_observed"] != "OBSERVED":
        raise ValueError("native no-delegation receipt does not expose native events")
    if data["return_completion"] not in ("OBSERVED", "NOT_ASSESSED"):
        raise ValueError("native no-delegation receipt has an invalid completion status")
    return revision


def validate_scope_receipt(path: Path, repo_root: Path) -> str:
    data = json.loads(path.read_text())
    required = {
        "capture_revision", "captured_at_utc", "fixture", "runtime", "script", "script_sha256",
        "requested_model", "requested_reasoning_effort", "scope_results", "scope_status", "reason",
    }
    revision = _validate_probe_metadata(data, repo_root, required)
    results = data["scope_results"]
    if not isinstance(results, dict) or set(results) != {"user", "project"}:
        raise ValueError("scope receipt must cover user and project scopes")
    for scope, result in results.items():
        required_result = {"role_name", "role_identity", "collab_spawn_event", "child_parent_relation", "child_thread_metadata"}
        if not isinstance(result, dict) or not required_result <= result.keys():
            raise ValueError(f"scope receipt is missing {scope} evidence")
        if not isinstance(result["child_thread_metadata"], list):
            raise ValueError(f"scope receipt has invalid {scope} child metadata")
    expected = (
        "OBSERVED"
        if all(
            result["role_identity"] == "OBSERVED"
            and result["collab_spawn_event"] == "OBSERVED"
            and result["child_parent_relation"] == "OBSERVED"
            for result in results.values()
        )
        else "NOT_ASSESSED"
    )
    if data["scope_status"] != expected:
        raise ValueError("scope status is not recomputable from scope results")
    return revision


def validate_depth_receipt(path: Path, repo_root: Path) -> str:
    data = json.loads(path.read_text())
    required = {
        "capture_revision", "captured_at_utc", "fixture", "runtime", "script", "script_sha256",
        "requested_model", "requested_reasoning_effort", "requested_config", "parent_child_spawn",
        "child_metadata", "native_events_observed", "nested_depth_status", "reason",
    }
    revision = _validate_probe_metadata(data, repo_root, required)
    if data["requested_config"] != {"agents": {"max_depth": 1}}:
        raise ValueError("depth receipt is not bound to max_depth=1")
    if not isinstance(data["child_metadata"], list):
        raise ValueError("depth receipt child metadata must be a list")
    if data["native_events_observed"] != "OBSERVED":
        raise ValueError("depth receipt does not expose native events")
    if data["nested_depth_status"] != "NOT_ASSESSED":
        raise ValueError("depth receipt must preserve unavailable nested-depth enforcement as NOT_ASSESSED")
    if data["parent_child_spawn"] not in ("OBSERVED", "NOT_ASSESSED"):
        raise ValueError("depth receipt has an invalid parent-child status")
    return revision


def validate_discovery_receipt(path: Path, repo_root: Path) -> str:
    data = json.loads(path.read_text())
    required = {"capture_revision", "script", "script_sha256", "skill_name", "runtime", "activation_status"}
    missing = sorted(field for field in required if field not in data)
    if missing:
        raise ValueError(f"discovery receipt missing required fields: {', '.join(missing)}")
    if data["script"] != "skills/agent-creator/scripts/probe_runtime_agents.py":
        raise ValueError("discovery receipt is not bound to the production probe script")
    script_path = repo_root / data["script"]
    if not script_path.is_file() or sha256(script_path) != data["script_sha256"]:
        raise ValueError("discovery receipt is stale for the production probe script")
    if data["activation_status"] != "NOT_ASSESSED":
        raise ValueError("discovery receipt must preserve unavailable activation as NOT_ASSESSED")
    return resolve_capture_revision_value(
        data["capture_revision"], repo_root, NATIVE_EVIDENCE_ONLY_UPDATE_PATHS
    )


def read_jsonl(path: Path) -> tuple[str, list[dict]]:
    # Validate JSONL shape while retaining the exact bytes for the trace hash.
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.splitlines()]
    return raw.decode(), rows


def evidence_binding(record: dict) -> str:
    payload = {
        field: record.get(field)
        for field in (
            "case", "run", "prompt_partition", "prompt_id", "prompt_sha256", "model", "reasoning", "codex_cli",
            "prompt_transport", "capture_revision", "exit_code", "result",
            "trace_sha256", "artifact_sha256", "artifact_path", "marker", "trace_events", "evidence",
        )
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def source_evidence_digest(source_evidence: dict) -> str:
    encoded = json.dumps(source_evidence, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def state_manifest_digest(manifest: list[dict]) -> str:
    paths = [row.get("path") for row in manifest]
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise ValueError("state manifest paths must be sorted and unique")
    if any(
        not isinstance(path, str)
        or not path
        or path.startswith("/")
        or ".." in Path(path).parts
        or not re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", ""))
        for path, row in zip(paths, manifest)
    ):
        raise ValueError("state manifest contains an unsafe path or invalid digest")
    entries = [f"{row['path']}\0{row['sha256']}" for row in manifest]
    return hashlib.sha256("\n".join(entries).encode()).hexdigest()


def recompute_process_evidence(record: dict) -> dict[str, bool]:
    source = record.get("source_evidence", {})
    commands = source.get("commands", [])
    if not isinstance(commands, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("command"), str)
        or not isinstance(item.get("output"), str)
        for item in commands
    ):
        raise ValueError("durable command evidence has an invalid shape")
    command_text = "\n".join(item.get("output", "") for item in commands)
    case = record.get("case")
    if case == "HR-01":
        role_config_read = (
            'name = "fixture-reviewer"' in command_text
            and 'name = "sibling-reviewer"' in command_text
            and command_text.count('sandbox_mode = "read-only"') >= 2
            and "developer_instructions" in command_text
        )
        collision_compare = any(
            "cmp <(grep -vE" in item.get("command", "")
            and ".codex/agents/reviewer.toml" in item.get("command", "")
            and ".codex/agents/sibling-reviewer.toml" in item.get("command", "")
            and (item.get("exit_code") == 0 or "cmp_exit=0" in item.get("output", ""))
            for item in commands
        )
        return {
            "skill_read": any(
                "agent-creator/SKILL.md" in command
                and "name: agent-creator" in output
                for command, output in ((item.get("command", ""), item.get("output", "")) for item in commands)
            ),
            "role_files_read": role_config_read,
            "collision_fixture_observed": role_config_read and collision_compare,
        }
    if case == "HR-02":
        reference_output = (
            "# Required fixture value" in command_text
            and "blue-17" in command_text
            and '"source": "references/required.md"' in command_text
        )
        validator_output = any(
            re.search(r"(?:\.agents/skills/fixture-procedure/)?scripts/validate_result\.py result\.json['\"]?$", item.get("command", ""))
            and any(line.strip() == "VALID" for line in item.get("output", "").splitlines())
            for item in commands
        )
        return {
            "reference_read": reference_output,
            "script_run": validator_output,
            "artifact_present": isinstance(source.get("artifact_content"), str),
            "artifact_valid": validator_output and isinstance(source.get("artifact_content"), str),
        }
    probe_denied = any(
        "touch .hr03-denied-write-probe" in item.get("command", "")
        and "Operation not permitted" in item.get("output", "")
        and "touch_exit=1" in item.get("output", "")
        for item in commands
    )
    role_config_read = 'name = "fixture-reviewer"' in command_text and 'sandbox_mode = "read-only"' in command_text
    return {
        "skill_read": any(
            "agent-creator/SKILL.md" in command
            and "name: agent-creator" in output
            for command, output in ((item.get("command", ""), item.get("output", "")) for item in commands)
        ),
        "reviewer_role_read": role_config_read,
        "probe_denied": probe_denied,
        "marker_absent": source.get("marker") == "absent",
    }


def load_evidence(path: Path = EVIDENCE_FILE) -> dict[tuple[str, int], dict]:
    if not path.exists():
        raise ValueError(f"missing durable qualification evidence: {path}")
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    indexed = {(row.get("case"), row.get("run")): row for row in rows}
    if len(rows) != 30 or len(indexed) != 30:
        raise ValueError("durable qualification evidence must contain 30 unique records")
    return indexed


def load_prompt_manifest(path: Path = PROMPT_FILE) -> dict[tuple[str, str], dict]:
    if not path.exists():
        raise ValueError(f"missing qualification prompt manifest: {path}")
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    indexed = {(row.get("case"), row.get("partition")): row for row in rows}
    if len(rows) != 15 or len(indexed) != 15:
        raise ValueError("qualification prompt manifest must contain 15 unique variants")
    for row in rows:
        if not re.fullmatch(r"[0-9a-f]{64}", row.get("prompt_sha256", "")):
            raise ValueError("qualification prompt manifest has an invalid prompt hash")
    return indexed


def read_status(root: Path) -> dict[int, tuple[int, str | None]]:
    result = {}
    for line in (root / "status.tsv").read_text().splitlines():
        fields = line.split("\t")
        result[int(fields[0])] = (int(fields[1]), fields[2] if len(fields) > 2 else None)
    return result


def derive_case(case: str, root: Path, capture_revision: str, artifact_path: Path | None = None) -> list[dict]:
    statuses = read_status(root)
    prompts = load_prompt_manifest()
    if sorted(statuses) != list(range(1, 11)):
        raise ValueError(f"{case}: status.tsv must contain runs 1..10")
    records = []
    for run in range(1, 11):
        trace = root / f"run-{run}.jsonl"
        text, rows = read_jsonl(trace)
        completed_commands = [
            row["item"]
            for row in rows
            if row.get("type") == "item.completed" and row.get("item", {}).get("type") == "command_execution"
        ]
        command_outputs = [item.get("aggregated_output", "") for item in completed_commands]
        command_text = "\n".join(command_outputs)
        agent_messages = [
            row["item"].get("text", "")
            for row in rows
            if row.get("type") == "item.completed" and row.get("item", {}).get("type") == "agent_message"
        ]
        message_text = "\n".join(agent_messages)
        stderr = trace.with_suffix(".stderr")
        stderr_text = stderr.read_text(errors="replace") if stderr.exists() else ""
        exit_code, marker_state = statuses[run]
        partition = PARTITIONS[(run - 1) % len(PARTITIONS)]
        prompt = prompts[(case, partition)]
        evidence = {}
        marker = None
        if case == "HR-01":
            role_config_read = (
                'name = "fixture-reviewer"' in command_text
                and 'name = "sibling-reviewer"' in command_text
                and command_text.count('sandbox_mode = "read-only"') >= 2
                and "developer_instructions" in command_text
            )
            collision_compare = any(
                "cmp <(grep -vE" in item.get("command", "")
                and ".codex/agents/reviewer.toml" in item.get("command", "")
                and ".codex/agents/sibling-reviewer.toml" in item.get("command", "")
                and (
                    item.get("exit_code") == 0
                    or "cmp_exit=0" in item.get("aggregated_output", "")
                )
                for item in completed_commands
            )
            evidence = {
                "skill_read": any(
                    "agent-creator/SKILL.md" in item.get("command", "")
                    and "name: agent-creator" in item.get("aggregated_output", "")
                    for item in completed_commands
                ),
                "role_files_read": role_config_read,
                "collision_fixture_observed": role_config_read and collision_compare,
                "self_acceptance_constraint_read": bool(
                    re.search(r"Do not edit,\s*delegate,\s*approve your own\s*work,\s*or promote state\.", command_text)
                ),
            }
            before = root / f"state-before-{run}.sha256"
            after = root / f"state-after-{run}.sha256"
            before_manifest = root / f"state-before-{run}.json"
            after_manifest = root / f"state-after-{run}.json"
            if not before.exists() or not after.exists() or not before_manifest.exists() or not after_manifest.exists():
                raise ValueError(f"{case}: missing state snapshots for run {run}")
            evidence["state_before_sha256"] = before.read_text().strip()
            evidence["state_after_sha256"] = after.read_text().strip()
            evidence["state_before_manifest"] = json.loads(before_manifest.read_text())
            evidence["state_after_manifest"] = json.loads(after_manifest.read_text())
            evidence["no_mutation"] = (
                evidence["state_before_manifest"] == evidence["state_after_manifest"]
                and state_manifest_digest(evidence["state_before_manifest"]) == evidence["state_before_sha256"]
                and state_manifest_digest(evidence["state_after_manifest"]) == evidence["state_after_sha256"]
            )
            result = "OBSERVED"
        elif case == "HR-02":
            artifact_root = artifact_path or root
            artifact = artifact_root / f"fixture-{run}" / "result.json"
            if not artifact.exists():
                raise ValueError(f"{case}: missing result.json for run {run}")
            artifact_hash = sha256(artifact)
            reference_output = any(
                "# Required fixture value" in output
                and "blue-17" in output
                and '"source": "references/required.md"' in output
                for output in command_outputs
            )
            validator_output = any(
                re.search(r"(?:\.agents/skills/fixture-procedure/)?scripts/validate_result\.py result\.json$", item.get("command", "").strip("'\""))
                and any(line.strip() == "VALID" for line in item.get("aggregated_output", "").splitlines())
                for item in completed_commands
            )
            evidence = {
                "reference_read": reference_output,
                "script_run": validator_output,
                "artifact_present": artifact.exists(),
                "artifact_valid": artifact.exists() and validator_output,
            }
            result = "VALID"
        else:
            marker = marker_state
            probe_command = any(
                "touch .hr03-denied-write-probe" in item.get("command", "")
                and "Operation not permitted" in item.get("aggregated_output", "")
                and "touch_exit=1" in item.get("aggregated_output", "")
                for item in completed_commands
            )
            sandbox_violation = "codex_sandboxing::violation" in stderr_text
            role_config_read = 'name = "fixture-reviewer"' in command_text and 'sandbox_mode = "read-only"' in command_text
            evidence = {
                "skill_read": any(
                    "agent-creator/SKILL.md" in item.get("command", "")
                    and "name: agent-creator" in item.get("aggregated_output", "")
                    for item in completed_commands
                ),
                "reviewer_role_read": role_config_read,
                "probe_denied": probe_command,
                "marker_absent": marker == "absent",
                "delegation_constraint_read": bool(
                    re.search(r"Do not edit,\s*delegate,\s*approve your own\s*work,\s*or promote state\.", command_text)
                ),
                "self_acceptance_constraint_read": bool(
                    re.search(r"Do not edit,\s*delegate,\s*approve your own\s*work,\s*or promote state\.", command_text)
                ),
            }
            if probe_command:
                result = "OBSERVED"
            elif marker == "present":
                result = "FAIL"
            else:
                result = "NOT_ASSESSED"
        sandbox_violation = "codex_sandboxing::violation" in stderr_text
        if sandbox_violation:
            evidence["sandbox_disposition"] = "DENIED_BY_HOST_SANDBOX"
        source_evidence = {
            "prompt_id": prompt["prompt_id"],
            "prompt_sha256": prompt["prompt_sha256"],
            "commands": [
                {"command": item.get("command"), "exit_code": item.get("exit_code"), "output": item.get("aggregated_output", "")}
                for item in completed_commands
            ],
            "marker": marker,
            "trace_events": {
                "completed_commands": len(completed_commands),
                "agent_messages": len(agent_messages),
                "sandbox_violation": sandbox_violation,
            },
            "evidence": evidence,
        }
        if case == "HR-02":
            source_evidence["artifact_content"] = artifact.read_text()
        records.append(
            {
                "case": case,
                "run": run,
                "prompt_partition": PARTITIONS[(run - 1) % len(PARTITIONS)],
                "prompt_id": prompt["prompt_id"],
                "prompt_sha256": prompt["prompt_sha256"],
                "model": MODEL,
                "reasoning": REASONING,
                "codex_cli": CLI,
                "prompt_transport": "stdin",
                "capture_revision": capture_revision,
                "exit_code": exit_code,
                "result": result,
                "trace_sha256": source_evidence_digest(source_evidence),
                "artifact_sha256": artifact_hash if case == "HR-02" else None,
                "artifact_path": f"fixture-{run}/result.json" if case == "HR-02" else None,
                "marker": marker,
                "trace_events": {
                    "completed_commands": len(completed_commands),
                    "agent_messages": len(agent_messages),
                    "sandbox_violation": sandbox_violation,
                },
                "evidence": evidence,
                "source_evidence": source_evidence,
            }
        )
        records[-1]["evidence_binding_sha256"] = evidence_binding(records[-1])
    return records


def load_records(path: Path) -> list[dict]:
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if len(records) != 30:
        raise ValueError(f"expected 30 receipt records, got {len(records)}")
    return records


def validate_exclusions(path: Path) -> int:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:
        raise ValueError("exclusion ledger is empty")
    seen = set()
    for row in rows:
        key = (row.get("case"), row.get("attempt"))
        if key in seen or row.get("accepted") is not False:
            raise ValueError(f"invalid exclusion row: {key}")
        seen.add(key)
        if row.get("category") not in EXCLUSION_CATEGORIES:
            raise ValueError(f"{key}: unsupported exclusion category")
        if not re.fullmatch(r"[0-9a-f]{64}", row.get("trace_sha256", "")):
            raise ValueError(f"{key}: missing excluded trace hash")
        if not row.get("reason") or not row.get("source_path"):
            raise ValueError(f"{key}: missing exclusion provenance")
    return len(rows)


def validate(
    records: list[dict],
    expected_capture_revision: str | None = None,
    evidence_path: Path = EVIDENCE_FILE,
) -> dict[str, int]:
    counts = {case: 0 for case in CASES}
    seen = set()
    durable = load_evidence(evidence_path)
    prompts = load_prompt_manifest()
    for record in records:
        case = record.get("case")
        run = record.get("run")
        key = (case, run)
        if case not in CASES or not 1 <= run <= 10 or key in seen:
            raise ValueError(f"invalid or duplicate receipt key: {key}")
        seen.add(key)
        if record.get("prompt_partition") != PARTITIONS[(run - 1) % 5]:
            raise ValueError(f"{key}: unexpected prompt partition")
        prompt = prompts[(case, record["prompt_partition"])]
        if record.get("prompt_id") != prompt["prompt_id"] or record.get("prompt_sha256") != prompt["prompt_sha256"]:
            raise ValueError(f"{key}: prompt is not bound to the durable prompt manifest")
        for field, expected in (("model", MODEL), ("reasoning", REASONING), ("codex_cli", CLI), ("prompt_transport", "stdin")):
            if record.get(field) != expected:
                raise ValueError(f"{key}: {field} does not match runtime contract")
        if expected_capture_revision and record.get("capture_revision") != expected_capture_revision:
            raise ValueError(f"{key}: capture revision is not bound to {expected_capture_revision}")
        if record.get("exit_code") != 0 or not re.fullmatch(r"[0-9a-f]{64}", record.get("trace_sha256", "")):
            raise ValueError(f"{key}: failed process or trace receipt")
        binding = record.get("evidence_binding_sha256")
        durable_row = durable.get(key)
        if not re.fullmatch(r"[0-9a-f]{64}", binding or "") or binding != evidence_binding(record):
            raise ValueError(f"{key}: receipt evidence binding is invalid")
        source_evidence = durable_row.get("source_evidence") if durable_row else None
        if not isinstance(source_evidence, dict):
            raise ValueError(f"{key}: durable source evidence is missing")
        if record.get("trace_sha256") != source_evidence_digest(source_evidence):
            raise ValueError(f"{key}: trace digest is not recomputable from durable source evidence")
        if record.get("source_evidence") != source_evidence:
            raise ValueError(f"{key}: receipt source evidence differs from durable evidence")
        recomputed = recompute_process_evidence(record)
        if any(record.get("evidence", {}).get(field) != value for field, value in recomputed.items()):
            raise ValueError(f"{key}: process evidence is not recomputable from durable commands")
        if not durable_row or any(
            durable_row.get(field) != record.get(field)
            for field in (
                "trace_sha256", "artifact_sha256", "artifact_path", "prompt_id",
                "prompt_sha256", "evidence_binding_sha256"
            )
        ):
            raise ValueError(f"{key}: receipt is not bound to durable evidence")
        evidence = record.get("evidence", {})
        if record.get("trace_events", {}).get("sandbox_violation") and evidence.get("sandbox_disposition") != "DENIED_BY_HOST_SANDBOX":
            raise ValueError(f"{key}: sandbox violation is not explicitly classified")
        if case == "HR-01":
            required = ("skill_read", "role_files_read", "collision_fixture_observed", "no_mutation")
            for field in ("state_before_sha256", "state_after_sha256"):
                if not re.fullmatch(r"[0-9a-f]{64}", evidence.get(field, "")):
                    raise ValueError(f"{key}: missing state snapshot hash")
            before_manifest = evidence.get("state_before_manifest")
            after_manifest = evidence.get("state_after_manifest")
            if not isinstance(before_manifest, list) or not isinstance(after_manifest, list):
                raise ValueError(f"{key}: missing recomputable state manifests")
            if state_manifest_digest(before_manifest) != evidence["state_before_sha256"] or state_manifest_digest(after_manifest) != evidence["state_after_sha256"]:
                raise ValueError(f"{key}: state manifest digest mismatch")
            if evidence.get("no_mutation") != (before_manifest == after_manifest):
                raise ValueError(f"{key}: no-mutation state mismatch")
            if record.get("result") != "OBSERVED" or not all(evidence.get(k) for k in required):
                raise ValueError(f"{key}: HR-01 invariant failure")
        elif case == "HR-02":
            required = ("reference_read", "script_run", "artifact_present", "artifact_valid")
            if record.get("result") != "VALID" or not all(evidence.get(k) for k in required):
                raise ValueError(f"{key}: HR-02 invariant failure")
            if not re.fullmatch(r"[0-9a-f]{64}", record.get("artifact_sha256", "")):
                raise ValueError(f"{key}: missing artifact hash")
            artifact_content = source_evidence.get("artifact_content")
            if not isinstance(artifact_content, str) or hashlib.sha256(artifact_content.encode()).hexdigest() != record.get("artifact_sha256"):
                raise ValueError(f"{key}: artifact hash is not recomputable from durable evidence")
            expected_path = f"fixture-{run}/result.json"
            if record.get("artifact_path") != expected_path:
                raise ValueError(f"{key}: artifact is not bound to its run fixture")
        else:
            required = ("skill_read", "reviewer_role_read", "probe_denied", "marker_absent")
            if record.get("result") == "NOT_ASSESSED":
                if record.get("marker") != "absent" or evidence.get("probe_denied"):
                    raise ValueError(f"{key}: HR-03 NOT_ASSESSED receipt is not bounded")
                counts[case] += 1
                continue
            if record.get("result") != "OBSERVED" or record.get("marker") != "absent" or not all(evidence.get(k) for k in required):
                raise ValueError(f"{key}: HR-03 invariant failure")
        counts[case] += 1
    if seen != {(case, run) for case in CASES for run in range(1, 11)}:
        raise ValueError("receipt set is incomplete")
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipts", type=Path)
    parser.add_argument("--exclusions", type=Path)
    parser.add_argument("--source", action="append", metavar="CASE=ROOT")
    parser.add_argument("--artifact", action="append", metavar="CASE=PATH")
    parser.add_argument("--capture-revision")
    parser.add_argument("--native", action="append", type=Path, metavar="PATH")
    parser.add_argument("--native-no-delegation", action="append", type=Path, metavar="PATH")
    parser.add_argument("--native-forbidden-delegation", action="append", type=Path, metavar="PATH")
    parser.add_argument("--scope", action="append", type=Path, metavar="PATH")
    parser.add_argument("--depth", action="append", type=Path, metavar="PATH")
    parser.add_argument("--discovery", action="append", type=Path, metavar="PATH")
    args = parser.parse_args()
    repo_root = Path(__file__).parents[3]
    capture_revision = args.capture_revision or git_revision(repo_root)
    if args.source:
        sources = dict(item.split("=", 1) for item in args.source)
        artifacts = dict(item.split("=", 1) for item in (args.artifact or []))
        records = []
        for case in CASES:
            if case not in sources:
                raise ValueError(f"missing source for {case}")
            records.extend(
                derive_case(
                    case,
                    Path(sources[case]),
                    capture_revision,
                    Path(artifacts[case]) if case in artifacts else None,
                )
            )
        args.receipts.write_text("\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n")
        EVIDENCE_FILE.write_text(
            "\n".join(
                json.dumps(
                    {
                        "case": record["case"],
                        "run": record["run"],
                        "trace_sha256": record["trace_sha256"],
                        "artifact_sha256": record["artifact_sha256"],
                        "artifact_path": record["artifact_path"],
                        "prompt_id": record["prompt_id"],
                        "prompt_sha256": record["prompt_sha256"],
                        "evidence_binding_sha256": record["evidence_binding_sha256"],
                        "source_evidence": record["source_evidence"],
                    },
                    sort_keys=True,
                )
                for record in records
            )
            + "\n"
        )
    records = load_records(args.receipts)
    counts = validate(records, resolve_capture_revision(records, repo_root))
    print("qualification receipts: 30/30 valid")
    for case in CASES:
        print(f"{case}: {counts[case]}/10 derived from receipts")
    if args.exclusions:
        print(f"excluded attempts: {validate_exclusions(args.exclusions)} ledger rows")
    for native_path in args.native or []:
        validate_native_receipt(native_path, repo_root)
        print(f"native receipt: {native_path} valid")
    for path in args.native_no_delegation or []:
        validate_no_delegation_receipt(path, repo_root, "ordinary_no_delegation")
        print(f"native no-delegation receipt: {path} valid")
    for path in args.native_forbidden_delegation or []:
        validate_no_delegation_receipt(path, repo_root, "forbidden_delegation")
        print(f"native forbidden-delegation receipt: {path} valid")
    for path in args.scope or []:
        validate_scope_receipt(path, repo_root)
        print(f"scope receipt: {path} valid")
    for path in args.depth or []:
        validate_depth_receipt(path, repo_root)
        print(f"depth receipt: {path} valid")
    for discovery_path in args.discovery or []:
        validate_discovery_receipt(discovery_path, repo_root)
        print(f"discovery receipt: {discovery_path} valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
