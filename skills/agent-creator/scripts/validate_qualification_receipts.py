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
EXCLUSION_CATEGORIES = ("NO_PROMPT_PROVIDED", "NONCOMPLIANT_TRACE", "USAGE_LIMIT")
MODEL = "gpt-5.6-luna"
REASONING = "medium"
CLI = "codex-cli 0.149.1"
EVIDENCE_ONLY_UPDATE_PATHS = {
    "skills/agent-creator/references/qualification-evidence.jsonl",
    "skills/agent-creator/references/qualification-receipts.jsonl",
    "skills/agent-creator/references/qualification-results.md",
}
EVIDENCE_FILE = Path(__file__).parents[1] / "references" / "qualification-evidence.jsonl"


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


def resolve_capture_revision(records: list[dict], repo_root: Path) -> str:
    revisions = {record.get("capture_revision") for record in records}
    if len(revisions) != 1 or None in revisions:
        raise ValueError("receipt set must use one capture revision")
    captured = next(iter(revisions))
    head = git_revision(repo_root)
    if captured == head:
        return head
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", captured, head],
        cwd=repo_root,
    ).returncode == 0
    changed = subprocess.run(
        ["git", "diff", "--name-only", f"{captured}..{head}"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if not ancestor or not changed or not set(changed) <= EVIDENCE_ONLY_UPDATE_PATHS:
        raise ValueError(f"receipts captured at {captured}, not fail-closed for HEAD {head}")
    return captured


def read_jsonl(path: Path) -> tuple[str, list[dict]]:
    # Validate JSONL shape while retaining the exact bytes for the trace hash.
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.splitlines()]
    return raw.decode(), rows


def evidence_binding(record: dict) -> str:
    payload = {
        field: record.get(field)
        for field in (
            "case", "run", "prompt_partition", "model", "reasoning", "codex_cli",
            "prompt_transport", "capture_revision", "exit_code", "result",
            "artifact_sha256", "artifact_path", "marker", "trace_events", "evidence",
        )
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_evidence(path: Path = EVIDENCE_FILE) -> dict[tuple[str, int], dict]:
    if not path.exists():
        raise ValueError(f"missing durable qualification evidence: {path}")
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    indexed = {(row.get("case"), row.get("run")): row for row in rows}
    if len(rows) != 30 or len(indexed) != 30:
        raise ValueError("durable qualification evidence must contain 30 unique records")
    return indexed


def read_status(root: Path) -> dict[int, tuple[int, str | None]]:
    result = {}
    for line in (root / "status.tsv").read_text().splitlines():
        fields = line.split("\t")
        result[int(fields[0])] = (int(fields[1]), fields[2] if len(fields) > 2 else None)
    return result


def derive_case(case: str, root: Path, capture_revision: str, artifact_path: Path | None = None) -> list[dict]:
    statuses = read_status(root)
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
        evidence = {}
        marker = None
        if case == "HR-01":
            role_config_read = (
                'name = "fixture-reviewer"' in command_text
                and 'name = "sibling-reviewer"' in command_text
                and command_text.count('sandbox_mode = "read-only"') >= 2
                and "developer_instructions" in command_text
            )
            evidence = {
                "skill_read": any(
                    "agent-creator/SKILL.md" in item.get("command", "")
                    and "name: agent-creator" in item.get("aggregated_output", "")
                    for item in completed_commands
                ),
                "role_files_read": role_config_read,
                "collision_observed": role_config_read and bool(
                    re.search(r"\b(?:duplicate|collision|REJECT_AGENT|MERGE_ROLES|REUSE_EXISTING)\b", message_text, re.IGNORECASE)
                ),
                "self_acceptance_constraint_read": bool(
                    re.search(r"Do not edit,\s*delegate,\s*approve your own\s*work,\s*or promote state\.", command_text)
                ),
            }
            before = root / f"state-before-{run}.sha256"
            after = root / f"state-after-{run}.sha256"
            if not before.exists() or not after.exists():
                raise ValueError(f"{case}: missing state snapshots for run {run}")
            evidence["state_before_sha256"] = before.read_text().strip()
            evidence["state_after_sha256"] = after.read_text().strip()
            evidence["no_mutation"] = evidence["state_before_sha256"] == evidence["state_after_sha256"]
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
            result = "OBSERVED"
        sandbox_violation = "codex_sandboxing::violation" in stderr_text
        if sandbox_violation:
            evidence["sandbox_disposition"] = "DENIED_BY_HOST_SANDBOX"
        records.append(
            {
                "case": case,
                "run": run,
                "prompt_partition": PARTITIONS[(run - 1) % len(PARTITIONS)],
                "model": MODEL,
                "reasoning": REASONING,
                "codex_cli": CLI,
                "prompt_transport": "stdin",
                "capture_revision": capture_revision,
                "exit_code": exit_code,
                "result": result,
                "trace_sha256": sha256(trace),
                "artifact_sha256": artifact_hash if case == "HR-02" else None,
                "artifact_path": f"fixture-{run}/result.json" if case == "HR-02" else None,
                "marker": marker,
                "trace_events": {
                    "completed_commands": len(completed_commands),
                    "agent_messages": len(agent_messages),
                    "sandbox_violation": sandbox_violation,
                },
                "evidence": evidence,
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
    for record in records:
        case = record.get("case")
        run = record.get("run")
        key = (case, run)
        if case not in CASES or not 1 <= run <= 10 or key in seen:
            raise ValueError(f"invalid or duplicate receipt key: {key}")
        seen.add(key)
        if record.get("prompt_partition") != PARTITIONS[(run - 1) % 5]:
            raise ValueError(f"{key}: unexpected prompt partition")
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
        if not durable_row or any(
            durable_row.get(field) != record.get(field)
            for field in ("trace_sha256", "artifact_sha256", "artifact_path", "evidence_binding_sha256")
        ):
            raise ValueError(f"{key}: receipt is not bound to durable evidence")
        evidence = record.get("evidence", {})
        if record.get("trace_events", {}).get("sandbox_violation") and evidence.get("sandbox_disposition") != "DENIED_BY_HOST_SANDBOX":
            raise ValueError(f"{key}: sandbox violation is not explicitly classified")
        if case == "HR-01":
            required = ("skill_read", "role_files_read", "collision_observed", "no_mutation")
            for field in ("state_before_sha256", "state_after_sha256"):
                if not re.fullmatch(r"[0-9a-f]{64}", evidence.get(field, "")):
                    raise ValueError(f"{key}: missing state snapshot hash")
            if evidence.get("no_mutation") != (evidence["state_before_sha256"] == evidence["state_after_sha256"]):
                raise ValueError(f"{key}: no-mutation state mismatch")
            if record.get("result") != "OBSERVED" or not all(evidence.get(k) for k in required):
                raise ValueError(f"{key}: HR-01 invariant failure")
        elif case == "HR-02":
            required = ("reference_read", "script_run", "artifact_present", "artifact_valid")
            if record.get("result") != "VALID" or not all(evidence.get(k) for k in required):
                raise ValueError(f"{key}: HR-02 invariant failure")
            if not re.fullmatch(r"[0-9a-f]{64}", record.get("artifact_sha256", "")):
                raise ValueError(f"{key}: missing artifact hash")
            expected_path = f"fixture-{run}/result.json"
            if record.get("artifact_path") != expected_path:
                raise ValueError(f"{key}: artifact is not bound to its run fixture")
        else:
            required = ("skill_read", "reviewer_role_read", "probe_denied", "marker_absent")
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
                        "evidence_binding_sha256": record["evidence_binding_sha256"],
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
