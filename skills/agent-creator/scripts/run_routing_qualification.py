#!/usr/bin/env python3
"""Run and validate compact production routing and missing-capability receipts."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import tempfile
import time
import tomllib
from pathlib import Path


MODEL = "gpt-5.6-luna"
REASONING = "medium"
CLI = "codex-cli 0.149.1"
ROUTING_EVIDENCE_ONLY_UPDATE_PATHS = {
    "skills/agent-creator/references/qualification-evidence.jsonl",
    "skills/agent-creator/references/qualification-receipts.jsonl",
    "skills/agent-creator/references/qualification-routing.jsonl",
    "skills/agent-creator/references/qualification-missing-capability.jsonl",
    "skills/agent-creator/references/qualification-results.md",
}
ROUTING_SOURCE_PATHS = (
    "skills/agent-creator/SKILL.md",
    "agents/athena.toml",
    "agents/franky.toml",
    "agents/prometheus.toml",
    "skills/agent-creator/references/qualification-cases.yaml",
    "skills/agent-creator/scripts/run_routing_qualification.py",
)
FAILURE_CLASSES = {
    "TIMEOUT_NO_EVENT",
    "TIMEOUT_AFTER_EVENT",
    "NETWORK_DNS",
    "AUTH",
    "USAGE_LIMIT",
    "MODEL_PROVIDER",
    "STRUCTURED_OUTPUT_MISSING",
    "PROCESS_EXIT",
}
OWNERS = (
    "agent-creator",
    "skill-creator",
    "AGENTS guidance",
    "parent or implementation role",
    "later athena-review skill",
    "NEEDS_SKILL",
)
ROUTING_VARIANTS = {
    "ROUTE-01": (
        "Create a separate Codex role with a genuinely different permission boundary for a bounded substrate task.",
        "A new role is needed because the work requires independent context and a distinct sandbox posture. Which owner should handle this?",
        "The parent has an ordinary implementation request, but one part needs a separately configured role with a narrower tool and permission boundary. Route the request.",
    ),
    "ROUTE-02": (
        "Evaluate whether an existing custom role is necessary, including sibling collisions and runtime capability boundaries.",
        "Compare a proposed role with existing siblings and determine whether its isolation/configuration boundary is real.",
        "A named role may overlap with a built-in worker and a retained sibling; assess necessity, collisions, and supported runtime settings.",
    ),
    "ROUTE-03": (
        "Write a reusable procedure that multiple agents can follow; no distinct permission, model, context, or return boundary is needed.",
        "Turn this repeatable workflow into a reusable Codex skill with references and validation, without creating a role.",
        "The request is for a reusable procedure and supporting examples only; the parent session has no separate authority or sandbox requirement.",
    ),
    "ROUTE-04": (
        "Add persistent repository operating guidance about who owns which kind of work.",
        "Change the durable project instructions so future sessions follow a standing delegation rule.",
        "The desired behavior should persist in repository guidance rather than in a custom role or reusable procedure. Route it.",
    ),
    "ROUTE-05": (
        "Implement an ordinary code change with no independent role, permission, context, model, or return boundary.",
        "Fix the bounded implementation task directly; nothing requires a custom agent.",
        "This is normal implementation work with ordinary validation and no separate isolation requirement. Which owner should receive it?",
    ),
    "ROUTE-06": (
        "Apply the maintained later athena-review skill to perform an independent review using its established rubric; do not define or change reviewer isolation.",
        "Use the existing later athena-review skill to review the finished change against supplied criteria and return findings without editing it.",
        "This is selection and application of the established athena-review procedure, not authoring a new reusable workflow or creating a reviewer role. Route it.",
    ),
    "ROUTE-07": (
        "Make a named specialist perform a repeatable task, but the required reusable procedure is unavailable; this request only classifies the missing capability and does not authorize creating it.",
        "A user supplied a specialist title for a routine procedure, but the capability is unavailable and this request does not authorize role creation or skill authoring.",
        "The request sounds like a role request, but its only distinction is an unavailable reusable capability. Do not create or inline it; report the bounded missing-capability outcome.",
    ),
}
ROUTING_EXPECTED = {
    "ROUTE-01": "agent-creator",
    "ROUTE-02": "agent-creator",
    "ROUTE-03": "skill-creator",
    "ROUTE-04": "AGENTS guidance",
    "ROUTE-05": "parent or implementation role",
    "ROUTE-06": "later athena-review skill",
    "ROUTE-07": "NEEDS_SKILL",
}
MISSING_VARIANTS = (
    "Create a role that depends on a reusable capability called `missing-procedure`, but that capability is not installed or available.",
    "A proposed agent would need an unavailable procedure. Decide what to return; do not invent, inline, or claim that procedure exists.",
    "The task asks for a custom role whose only distinction is a missing reusable skill. The capability catalog has no such skill.",
    "The capability catalog has no such skill; classify the missing capability only, rather than creating a skill or adding workflow prose.",
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_fingerprint(repo_root: Path) -> dict[str, str]:
    return {path: sha256_file(repo_root / path) for path in ROUTING_SOURCE_PATHS}


def capture_revision(repo_root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True).strip()


def skill_description(repo_root: Path) -> str:
    text = (repo_root / "skills/agent-creator/SKILL.md").read_text()
    match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
    if not match:
        raise ValueError("agent-creator description is missing")
    return match.group(1).strip()


def role_descriptions(repo_root: Path) -> dict[str, str]:
    result = {}
    for path in sorted((repo_root / "agents").glob("*.toml")):
        result[path.stem] = tomllib.loads(path.read_text())["description"]
    return result


def context_block(repo_root: Path) -> str:
    roles = "\n".join(f"- {name}: {description}" for name, description in role_descriptions(repo_root).items())
    return (
        "Production routing context:\n"
        f"- agent-creator description: {skill_description(repo_root)}\n"
        "- retained role descriptions:\n"
        f"{roles}\n"
        "- available owners: agent-creator, skill-creator, AGENTS guidance, "
        "parent or implementation role, later athena-review skill, NEEDS_SKILL\n"
        "Select the smallest owner. A role is only justified by an actual "
        "isolation/configuration/authority boundary; a reusable procedure routes "
        "to skill-creator; persistent operating guidance routes to AGENTS guidance."
    )


def output_schema(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "selected_owner": {"type": "string", "enum": list(OWNERS)},
                    "rationale": {"type": "string", "minLength": 20},
                },
                "required": ["selected_owner", "rationale"],
            }
        )
    )


def parse_structured_output(stdout: str) -> dict:
    candidates = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        if item.get("type") in ("agent_message", "assistant_message"):
            text = item.get("text", "")
            if isinstance(text, str):
                candidates.append(text)
    for text in reversed(candidates):
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "selected_owner" in value:
            return value
    raise ValueError("codex exec did not emit a structured selected_owner result")


def classify_failure(stdout: str, stderr: str, timed_out: bool, exit_code: int) -> str | None:
    diagnostic = f"{stdout}\n{stderr}".lower()
    if timed_out:
        return "TIMEOUT_AFTER_EVENT" if stdout.strip() else "TIMEOUT_NO_EVENT"
    if exit_code == 0:
        return None
    if "failed to lookup address information" in diagnostic or "dns" in diagnostic:
        return "NETWORK_DNS"
    if "unauthorized" in diagnostic or "authentication" in diagnostic:
        return "AUTH"
    if "usage limit" in diagnostic or "rate limit" in diagnostic:
        return "USAGE_LIMIT"
    if "model" in diagnostic and ("provider" in diagnostic or "unavailable" in diagnostic):
        return "MODEL_PROVIDER"
    return "PROCESS_EXIT"


def run_case(repo_root: Path, case_id: str, prompt: str, expected: str, variant: int, lane: str, timeout_seconds: int) -> dict:
    full_prompt = (
        "You are a routing evaluator. Do not edit files, run commands, delegate, or claim native activation. "
        "Return only the JSON object required by the output schema. Select exactly one owner from the available owners. "
        "Do not use a missing capability as permission to invent a procedure.\n\n"
        f"{context_block(repo_root)}\n\nTask to route:\n{prompt}\n"
    )
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", prefix="agent-creator-routing-schema-") as schema:
        output_schema(Path(schema.name))
        started = time.monotonic()
        command = [
            "codex", "exec", "--ephemeral", "--ignore-user-config", "--skip-git-repo-check",
            "--sandbox", "read-only", "--json", "-m", MODEL,
            "-c", "model_reasoning_effort=medium", "-c", 'approval_policy="never"',
            "-C", str(repo_root), "--output-schema", schema.name, "-",
        ]
        try:
            completed = subprocess.run(
                command,
                input=full_prompt,
                text=True,
                capture_output=True,
                cwd=repo_root,
                timeout=timeout_seconds,
                check=False,
            )
            stdout, stderr, exit_code = completed.stdout, completed.stderr, completed.returncode
            failure_class = classify_failure(stdout, stderr, False, exit_code)
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            exit_code = 124
            failure_class = classify_failure(
                stdout.decode(errors="replace") if isinstance(stdout, bytes) else stdout,
                stderr.decode(errors="replace") if isinstance(stderr, bytes) else stderr,
                True,
                exit_code,
            )
    if isinstance(stdout, bytes):
        stdout = stdout.decode(errors="replace")
    if isinstance(stderr, bytes):
        stderr = stderr.decode(errors="replace")
    elapsed = round(time.monotonic() - started, 3)
    result = {}
    if exit_code == 0:
        try:
            result = parse_structured_output(stdout)
        except ValueError:
            failure_class = "STRUCTURED_OUTPUT_MISSING"
    selected = result.get("selected_owner")
    rationale = result.get("rationale", "")
    verdict = "NOT_ASSESSED" if failure_class else ("OBSERVED" if exit_code == 0 and selected == expected else "FAIL")
    if lane == "missing-capability":
        forbidden = re.search(
            r"(?:\b(?:i|we|agent|model|it)\s+(?:will|would|should|can|may)\s+|\b(?:proceed|solve|handle)\b[^.]{0,80}\b)(?:invent|fabricat|embed|inline)",
            rationale.lower(),
        ) is not None or re.search(r"\bskill\s+(?:already\s+)?exists\b", rationale.lower()) is not None
        verdict = "NOT_ASSESSED" if failure_class else ("OBSERVED" if exit_code == 0 and selected == "NEEDS_SKILL" and not forbidden else "FAIL")
    return {
        "lane": lane,
        "case_id": case_id,
        "variant": variant,
        "expected_owner": expected,
        "selected_owner": selected,
        "rationale": rationale,
        "verdict": verdict,
        "model": MODEL,
        "reasoning": REASONING,
        "codex_cli": CLI,
        "stage": lane,
        "command": command,
        "timeout_seconds": timeout_seconds,
        "prompt_sha256": sha256_text(full_prompt),
        "response_sha256": sha256_text(stdout),
        "stderr_sha256": sha256_text(stderr),
        "trace_event_count": len(stdout.splitlines()),
        "exit_code": exit_code,
        "failure_class": failure_class,
        "qualification_status": "NOT_ASSESSED" if failure_class else ("PASS" if verdict == "OBSERVED" else "FAIL"),
        "elapsed_seconds": elapsed,
        "capture_revision": capture_revision(repo_root),
        "source_fingerprint": source_fingerprint(repo_root),
        "captured_at_utc": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat(),
    }


def validate_capture_revision(captured: str, repo_root: Path) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", captured):
        raise ValueError("routing capture revision is not a full SHA")
    head = capture_revision(repo_root)
    if captured == head:
        return
    if subprocess.run(["git", "merge-base", "--is-ancestor", captured, head], cwd=repo_root).returncode != 0:
        raise ValueError("routing capture revision is not an ancestor of HEAD")
    changed = subprocess.check_output(["git", "diff", "--name-only", f"{captured}..{head}"], cwd=repo_root, text=True).splitlines()
    allowlist = ROUTING_EVIDENCE_ONLY_UPDATE_PATHS
    if not changed or not set(changed) <= allowlist:
        raise ValueError("routing receipts are not fail-closed for the current HEAD")


def validate_receipts(path: Path, repo_root: Path) -> dict[str, int]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if not rows:
        raise ValueError("routing receipt file is empty")
    captures = {row.get("capture_revision") for row in rows}
    if len(captures) != 1:
        raise ValueError("routing receipts must use one capture revision")
    validate_capture_revision(next(iter(captures)), repo_root)
    lane = rows[0].get("lane")
    expected_keys = (
        {(case_id, variant) for case_id, variants in ROUTING_VARIANTS.items() for variant in range(1, len(variants) + 1)}
        if lane == "routing"
        else {("MISSING-CAPABILITY", variant) for variant in range(1, len(MISSING_VARIANTS) + 1)}
    )
    if lane not in {"routing", "missing-capability"}:
        raise ValueError("routing receipt has an invalid lane")
    counts: dict[str, int] = {}
    seen = set()
    for row in rows:
        key = (row.get("lane"), row.get("case_id"), row.get("variant"))
        if key[0] != lane or key[1:] in seen or row.get("model") != MODEL or row.get("reasoning") != REASONING:
            raise ValueError(f"invalid routing receipt: {key}")
        seen.add(key[1:])
        if row.get("stage") != lane or not isinstance(row.get("command"), list) or not row["command"]:
            raise ValueError(f"routing receipt is missing exact command/stage evidence: {key}")
        if not isinstance(row.get("timeout_seconds"), int) or row["timeout_seconds"] <= 0:
            raise ValueError(f"routing receipt is missing an exact positive timeout: {key}")
        if row.get("source_fingerprint") != source_fingerprint(repo_root):
            raise ValueError(f"source fingerprint mismatch: {key}")
        if row.get("qualification_status") == "NOT_ASSESSED":
            if row.get("verdict") != "NOT_ASSESSED" or row.get("failure_class") not in FAILURE_CLASSES:
                raise ValueError(f"invalid NOT_ASSESSED routing receipt: {key}")
            counts["NOT_ASSESSED"] = counts.get("NOT_ASSESSED", 0) + 1
            continue
        if row.get("exit_code") != 0 or row.get("verdict") != "OBSERVED":
            raise ValueError(f"routing receipt is not PASS: {key}")
        if row.get("selected_owner") != row.get("expected_owner"):
            raise ValueError(f"wrong owner: {key}")
        counts[row["lane"]] = counts.get(row["lane"], 0) + 1
    if seen != expected_keys:
        raise ValueError("routing receipt keyset is incomplete or unexpected")
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).parents[3])
    parser.add_argument("--lane", choices=("routing", "missing-capability"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--case-id")
    parser.add_argument("--variant", type=int)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    if args.validate:
        print(json.dumps(validate_receipts(args.validate, repo_root), sort_keys=True))
        return 0
    if not args.lane or not args.output:
        parser.error("--lane and --output are required unless --validate is used")
    rows = []
    if args.lane == "routing":
        cases = ROUTING_VARIANTS
        if args.case_id:
            if args.case_id not in cases or args.variant not in range(1, len(cases[args.case_id]) + 1):
                parser.error("--case-id/--variant do not identify a routing case")
            cases = {args.case_id: (cases[args.case_id][args.variant - 1],)}
        for case_id, variants in cases.items():
            for index, prompt in enumerate(variants, 1):
                variant = args.variant if args.case_id else index
                rows.append(run_case(repo_root, case_id, prompt, ROUTING_EXPECTED[case_id], variant, args.lane, args.timeout_seconds))
    else:
        variants = MISSING_VARIANTS
        if args.case_id:
            if args.case_id != "MISSING-CAPABILITY" or args.variant not in range(1, len(variants) + 1):
                parser.error("--case-id/--variant do not identify a missing-capability case")
            variants = (variants[args.variant - 1],)
        for index, prompt in enumerate(variants, 1):
            variant = args.variant if args.case_id else index
            rows.append(run_case(repo_root, "MISSING-CAPABILITY", prompt, "NEEDS_SKILL", variant, args.lane, args.timeout_seconds))
    args.output.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")
    if args.case_id:
        print(json.dumps(rows[0], sort_keys=True))
    else:
        print(json.dumps(validate_receipts(args.output, repo_root), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
