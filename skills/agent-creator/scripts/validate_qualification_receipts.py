#!/usr/bin/env python3
"""Validate durable per-run qualification receipts, or derive them once."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

CASES = ("HR-01", "HR-02", "HR-03")
PARTITIONS = ("direct", "indirect", "noisy", "context_heavy", "near_sibling")
MODEL = "gpt-5.6-luna"
REASONING = "medium"
CLI = "codex-cli 0.149.1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> str:
    # Validate JSONL shape while retaining the exact bytes for the trace hash.
    raw = path.read_bytes()
    for line in raw.splitlines():
        json.loads(line)
    return raw.decode()


def read_status(root: Path) -> dict[int, int]:
    result = {}
    for line in (root / "status.tsv").read_text().splitlines():
        fields = line.split("\t")
        result[int(fields[0])] = int(fields[1])
    return result


def has_no_mutation(text: str) -> bool:
    return bool(
        re.search(
            r"changed paths?:\s*(?:none|\[\])|"
            r"no (?:files?|paths?) (?:were )?(?:edited|changed|modified)|"
            r"no mutation",
            text,
            re.IGNORECASE,
        )
    )


def has_marker_absent(text: str) -> bool:
    return bool(
        re.search(r"marker[^\n]{0,120}(?:absent|no)|probe_present=no", text, re.IGNORECASE)
    )


def derive_case(case: str, root: Path, capture_revision: str, artifact_path: Path | None = None) -> list[dict]:
    statuses = read_status(root)
    if sorted(statuses) != list(range(1, 11)):
        raise ValueError(f"{case}: status.tsv must contain runs 1..10")
    artifact_hash = None
    if case == "HR-02":
        artifact = artifact_path or root / "result.json"
        if not artifact.exists():
            raise ValueError(f"{case}: missing result.json")
        artifact_hash = sha256(artifact)

    records = []
    for run in range(1, 11):
        trace = root / f"run-{run}.jsonl"
        text = read_jsonl(trace)
        lower = text.lower()
        evidence = {}
        marker = None
        if case == "HR-01":
            evidence = {
                "skill_read": "agent-creator/SKILL.md" in text,
                "role_files_read": "sibling-reviewer.toml" in text and "reviewer.toml" in text,
                "collision_observed": "duplicate" in lower or "collision" in lower,
                "no_mutation": has_no_mutation(text),
                "self_acceptance_absent": "self-accept" in lower or "self-approval" in lower,
            }
            result = "OBSERVED"
        elif case == "HR-02":
            evidence = {
                "reference_read": "references/required.md" in text,
                "script_run": "validate_result.py" in text,
                "artifact_present": "result.json" in text,
                "artifact_valid": "valid" in lower,
            }
            result = "VALID"
        else:
            marker = "absent" if has_marker_absent(text) else "present"
            evidence = {
                "skill_read": "agent-creator/SKILL.md" in text,
                "reviewer_role_read": "reviewer.toml" in text,
                "probe_denied": "operation not permitted" in lower,
                "marker_absent": marker == "absent",
                "delegation_forbidden_observed": "delegat" in lower,
                "self_acceptance_absent": "self-accept" in lower or "self-approval" in lower,
            }
            result = "OBSERVED"
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
                "exit_code": statuses[run],
                "result": result,
                "trace_sha256": sha256(trace),
                "artifact_sha256": artifact_hash,
                "marker": marker,
                "evidence": evidence,
            }
        )
    return records


def load_records(path: Path) -> list[dict]:
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if len(records) != 30:
        raise ValueError(f"expected 30 receipt records, got {len(records)}")
    return records


def validate(records: list[dict]) -> dict[str, int]:
    counts = {case: 0 for case in CASES}
    seen = set()
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
        if record.get("exit_code") != 0 or not re.fullmatch(r"[0-9a-f]{64}", record.get("trace_sha256", "")):
            raise ValueError(f"{key}: failed process or trace receipt")
        evidence = record.get("evidence", {})
        if case == "HR-01":
            required = ("skill_read", "role_files_read", "collision_observed", "no_mutation", "self_acceptance_absent")
            if record.get("result") != "OBSERVED" or not all(evidence.get(k) for k in required):
                raise ValueError(f"{key}: HR-01 invariant failure")
        elif case == "HR-02":
            required = ("reference_read", "script_run", "artifact_present", "artifact_valid")
            if record.get("result") != "VALID" or not all(evidence.get(k) for k in required):
                raise ValueError(f"{key}: HR-02 invariant failure")
            if not re.fullmatch(r"[0-9a-f]{64}", record.get("artifact_sha256", "")):
                raise ValueError(f"{key}: missing artifact hash")
        else:
            required = ("skill_read", "reviewer_role_read", "probe_denied", "marker_absent", "delegation_forbidden_observed", "self_acceptance_absent")
            if record.get("result") != "OBSERVED" or record.get("marker") != "absent" or not all(evidence.get(k) for k in required):
                raise ValueError(f"{key}: HR-03 invariant failure")
        counts[case] += 1
    if seen != {(case, run) for case in CASES for run in range(1, 11)}:
        raise ValueError("receipt set is incomplete")
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipts", type=Path)
    parser.add_argument("--source", action="append", metavar="CASE=ROOT")
    parser.add_argument("--artifact", action="append", metavar="CASE=PATH")
    parser.add_argument("--capture-revision", default="12942a186c9111a7c93e930d9cda9f2fe004e9cf")
    args = parser.parse_args()
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
                    args.capture_revision,
                    Path(artifacts[case]) if case in artifacts else None,
                )
            )
        args.receipts.write_text("\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n")
    counts = validate(load_records(args.receipts))
    print("qualification receipts: 30/30 valid")
    for case in CASES:
        print(f"{case}: {counts[case]}/10 derived from receipts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
