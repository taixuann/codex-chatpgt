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
        "Perform an independent review procedure using an established rubric; do not define or change reviewer isolation.",
        "Review the finished change against the supplied criteria and return findings without editing it.",
        "The task is the reusable independent-review workflow itself, not creation of a reviewer role or a permission profile. Route it.",
    ),
    "ROUTE-07": (
        "Make a named specialist perform a repeatable task, but no distinct runtime boundary or role isolation is required.",
        "A user supplied a specialist title for a routine procedure; there is no different model, sandbox, context, authority, or return contract.",
        "The request sounds like a role request, but after inspection it is only a repeatable procedure with no role boundary. Choose the correct disposition.",
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
    "Do not solve the absent-capability request by adding workflow prose to developer_instructions. Select the bounded outcome.",
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


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
            failure_class = None
        except subprocess.TimeoutExpired as error:
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            exit_code = 124
            failure_class = "TIMEOUT"
    elapsed = round(time.monotonic() - started, 3)
    result = parse_structured_output(stdout) if exit_code == 0 else {}
    selected = result.get("selected_owner")
    rationale = result.get("rationale", "")
    verdict = "NOT_ASSESSED" if failure_class else ("OBSERVED" if exit_code == 0 and selected == expected else "FAIL")
    if lane == "missing-capability":
        forbidden = re.search(r"invent|fabricat|embed.*(procedure|workflow)|skill.*exists", rationale.lower()) is not None
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
        "prompt_sha256": sha256_text(full_prompt),
        "response_sha256": sha256_text(stdout),
        "stderr_sha256": sha256_text(stderr),
        "trace_event_count": len(stdout.splitlines()),
        "exit_code": exit_code,
        "failure_class": failure_class,
        "qualification_status": "NOT_ASSESSED" if failure_class else ("PASS" if verdict == "OBSERVED" else "FAIL"),
        "elapsed_seconds": elapsed,
        "capture_revision": capture_revision(repo_root),
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
    allowlist = {
        "skills/agent-creator/references/qualification-routing.jsonl",
        "skills/agent-creator/references/qualification-missing-capability.jsonl",
        "skills/agent-creator/references/qualification-results.md",
    }
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
    counts: dict[str, int] = {}
    seen = set()
    for row in rows:
        key = (row.get("lane"), row.get("case_id"), row.get("variant"))
        if key in seen or row.get("model") != MODEL or row.get("reasoning") != REASONING:
            raise ValueError(f"invalid routing receipt: {key}")
        seen.add(key)
        if row.get("qualification_status") == "NOT_ASSESSED":
            if row.get("verdict") != "NOT_ASSESSED" or row.get("failure_class") != "TIMEOUT":
                raise ValueError(f"invalid NOT_ASSESSED routing receipt: {key}")
            counts["NOT_ASSESSED"] = counts.get("NOT_ASSESSED", 0) + 1
            continue
        if row.get("exit_code") != 0 or row.get("verdict") != "OBSERVED":
            raise ValueError(f"routing receipt is not PASS: {key}")
        if row.get("selected_owner") != row.get("expected_owner"):
            raise ValueError(f"wrong owner: {key}")
        counts[row["lane"]] = counts.get(row["lane"], 0) + 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).parents[3])
    parser.add_argument("--lane", choices=("routing", "missing-capability"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=60)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    if args.validate:
        print(json.dumps(validate_receipts(args.validate, repo_root), sort_keys=True))
        return 0
    if not args.lane or not args.output:
        parser.error("--lane and --output are required unless --validate is used")
    rows = []
    if args.lane == "routing":
        for case_id, variants in ROUTING_VARIANTS.items():
            for index, prompt in enumerate(variants, 1):
                rows.append(run_case(repo_root, case_id, prompt, ROUTING_EXPECTED[case_id], index, args.lane, args.timeout_seconds))
    else:
        for index, prompt in enumerate(MISSING_VARIANTS, 1):
            rows.append(run_case(repo_root, "MISSING-CAPABILITY", prompt, "NEEDS_SKILL", index, args.lane, args.timeout_seconds))
    args.output.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")
    print(json.dumps(validate_receipts(args.output, repo_root), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
