#!/usr/bin/env python3
"""Run and aggregate bounded, read-only Codex skill-quality observations.

This is an evidence harness, not a router. It never changes the catalog or
rewrites skill descriptions. Host-side selection is reported only when the
JSONL trace exposes it; a model's final self-report is marked separately.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import yaml


GOVERNANCE = "OBSERVE -> PROPOSE -> REVIEW -> ACCEPT -> UPDATE"
SELECTION_KEYS = {"selected_skill", "selected_skills", "skill", "skills"}
SKILL_PATH_PATTERN = re.compile(r"(?:\.agents/skills|skills)/(?:[A-Za-z0-9._-]+/)?([A-Za-z0-9._-]+)/SKILL\.md")
CANONICAL_ACTIVE = {
    "control-plane-audit",
    "external-handoff",
    "instruction-maintenance",
    "project-bootstrap",
    "runtime-adapter-management",
    "shared-session-closeout",
}


def _text(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def _walk(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _first_text(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("text", "message", "content"):
            item = value.get(key)
            if isinstance(item, str):
                return item
        for item in value.values():
            found = _first_text(item)
            if found:
                return found
    if isinstance(value, list):
        for item in value:
            found = _first_text(item)
            if found:
                return found
    return None


def _number(value: Any) -> int | float | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def summarize_trace(stdout: str, stderr: str) -> dict[str, Any]:
    """Extract observable facts from Codex JSONL without inferring selection."""
    stdout = _text(stdout)
    stderr = _text(stderr)
    events: list[dict[str, Any]] = []
    commands: list[str] = []
    tools: list[str] = []
    usage: dict[str, int | float] = {}
    final_answer: str | None = None
    host_selection: Any = None
    procedure_loads: set[str] = set()
    parse_errors: list[str] = []

    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            parse_errors.append(str(exc))
            continue
        if not isinstance(event, dict):
            continue
        events.append(event)
        item = event.get("item")
        if isinstance(item, dict):
            if item.get("type") in {"agent_message", "assistant_message", "message"}:
                final_answer = _first_text(item) or final_answer
            if item.get("type") == "command_execution":
                command = item.get("command") or item.get("cmd")
                if isinstance(command, str):
                    commands.append(command)
            if "tool" in item or item.get("type") in {"tool_call", "mcp_tool_call"}:
                tool = item.get("name") or item.get("tool") or item.get("server")
                if isinstance(tool, str):
                    tools.append(tool)

        for key, value in _walk(event):
            if key in {"input_tokens", "output_tokens", "total_tokens", "cached_input_tokens"}:
                number = _number(value)
                if number is not None:
                    usage[key] = number
            if key in SELECTION_KEYS and key.startswith("selected"):
                host_selection = value

    stderr_lines = [line for line in stderr.splitlines() if line.strip()]
    for command in commands:
        procedure_loads.update(SKILL_PATH_PATTERN.findall(command))
    if "total_tokens" not in usage and {"input_tokens", "output_tokens"} <= usage.keys():
        usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
    has_error_event = any(event.get("type") == "error" for event in events)
    completed = any(event.get("type") == "turn.completed" for event in events)
    if host_selection is not None:
        selection_source = "host_trace"
    elif len(procedure_loads) == 1:
        selection_source = "procedure_load_trace"
    elif final_answer:
        selection_source = "final_response_self_report"
    else:
        selection_source = "none"
    return {
        "status": "completed" if completed and not has_error_event else "blocked",
        "events": len(events),
        "final_answer": final_answer,
        "host_selection": host_selection,
        "procedure_loads": sorted(procedure_loads),
        "selection_source": selection_source,
        "usage": usage,
        "commands": commands,
        "tools": tools,
        "stderr": stderr_lines[-20:],
        "parse_errors": parse_errors,
    }


def reported_result(final_answer: str | None) -> dict[str, Any]:
    if not final_answer:
        return {}
    candidate = final_answer.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*|\s*```$", "", candidate, flags=re.IGNORECASE | re.DOTALL)
    try:
        value = json.loads(candidate)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", candidate, flags=re.DOTALL)
        if not match:
            return {}
        try:
            value = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}
    return value if isinstance(value, dict) else {}


def _normalise_actual(value: Any) -> str:
    if isinstance(value, list):
        value = value[0] if value else "none"
    if not isinstance(value, str) or not value.strip():
        return "none"
    value = value.strip()
    if value.lower() in {"none", "null", "no skill", "no_skill"}:
        return "none"
    return value


def actual_from_trace(trace: dict[str, Any], tracked: set[str]) -> str:
    """Use host selection or an observed single procedure load, never self-report."""
    if trace.get("selection_source") == "host_trace":
        actual = _normalise_actual(trace.get("host_selection"))
        return actual if actual == "none" or actual in tracked else "unknown"
    if trace.get("selection_source") != "procedure_load_trace":
        return "none"
    loads = trace.get("procedure_loads", [])
    actual = _normalise_actual(loads[0] if len(loads) == 1 else "unknown")
    return actual if actual == "none" or actual in tracked else "unknown"


def routing_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated = [record for record in records if record.get("status", "completed") == "completed"]
    true_positives = sum(
        1 for record in evaluated if record.get("expected") != "none" and record.get("actual") == record.get("expected")
    )
    none_records = [record for record in evaluated if record.get("expected") == "none"]
    correct_none = sum(1 for record in none_records if record.get("actual") == "none")
    false_positives = sum(
        1 for record in evaluated if record.get("actual") != "none" and record.get("actual") != record.get("expected")
    )
    expected_skill = [record for record in evaluated if record.get("expected") != "none"]
    recall_denominator = len(expected_skill)
    precision_denominator = true_positives + false_positives
    confusion: Counter[str] = Counter(
        f"{record.get('expected')}->{record.get('actual')}" for record in evaluated
    )
    return {
        "evaluated": len(evaluated),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": sum(1 for record in expected_skill if record.get("actual") != record.get("expected")),
        "precision": true_positives / precision_denominator if precision_denominator else None,
        "recall": true_positives / recall_denominator if recall_denominator else None,
        "none_accuracy": correct_none / len(none_records) if none_records else None,
        "confusion_matrix": dict(sorted(confusion.items())),
    }


def utility_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    comparable = [
        record
        for record in records
        if record.get("with_status") in {"pass", "fail"}
        and record.get("without_status") in {"pass", "fail"}
    ]
    token_delta = sum(
        (record.get("with_tokens") or 0) - (record.get("without_tokens") or 0)
        for record in comparable
    )
    return {
        "evaluated": len(comparable),
        "load_bearing_passes": sum(
            1 for record in comparable if record["with_status"] == "pass" and record["without_status"] == "fail"
        ),
        "redundancy_candidates": sum(
            1 for record in comparable if record["with_status"] == "pass" and record["without_status"] == "pass"
        ),
        "harmful_with_failures": sum(
            1 for record in comparable if record["with_status"] == "fail" and record["without_status"] == "pass"
        ),
        "token_delta_total": token_delta,
    }


def regression_record(case: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case.get("id", case.get("case_id")),
        "prompt": case.get("prompt", observation.get("prompt", "")),
        "expected": case.get("expected", "none"),
        "actual": observation.get("actual", "none"),
        "selection_source": observation.get("selection_source", "none"),
        "governance": GOVERNANCE,
    }


def load_cases(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("benchmark fixture requires a non-empty cases list")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get("id"), str):
            raise ValueError("each benchmark case requires an id")
        if case["id"] in seen:
            raise ValueError(f"duplicate benchmark case: {case['id']}")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise ValueError(f"{case['id']}: prompt is required")
        if not isinstance(case.get("expected"), str):
            raise ValueError(f"{case['id']}: expected is required")
        seen.add(case["id"])
        result.append(case)
    return result


def benchmark_prompt(case: dict[str, Any], active_skills: list[str], mode: str) -> str:
    skill_list = ", ".join(active_skills)
    return f"""You are participating in a read-only skill routing benchmark.

Task prompt:
{case['prompt']}

The co-loaded candidate skill folders are: {skill_list}.
This is the {mode} condition. Perform the task in a read-only way: do not
modify files, create artifacts, or make external writes. For a write-oriented
request, report the proposed change without applying it. After the bounded
task, report the exact folder name only if the host exposed or loaded it; do
not invent a selection from the task wording.

Return exactly one JSON object and no Markdown:
{{"selected_skill":"<folder name or none>","task_status":"pass or fail","reason":"one short sentence"}}
"""


def _link_if_present(source: Path, target: Path) -> None:
    if source.exists():
        target.symlink_to(source)


def evaluation_home(root: Path, condition: str, active_skills: list[str]) -> tempfile.TemporaryDirectory[str]:
    """Create an isolated skill home for one evaluation condition."""
    temporary = tempfile.TemporaryDirectory(prefix="codex-skill-eval-", dir=str(root / ".tmp"))
    home = Path(temporary.name)
    # Preserve the authenticated ChatGPT Codex credential when the caller has
    # not overridden CODEX_HOME. The evaluator's temporary home must isolate
    # skills, but it must not silently replace the host's auth source with the
    # repository root (which normally has no auth.json).
    source_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    _link_if_present(source_home / "auth.json", home / "auth.json")
    if condition == "with":
        skill_root = home / ".agents" / "skills"
        skill_root.mkdir(parents=True)
        for name in active_skills:
            matches = [path.parent for path in (root / "skills").rglob("SKILL.md") if path.parent.name == name]
            if len(matches) != 1:
                raise ValueError(f"expected one package named {name}, found {len(matches)}")
            source = matches[0]
            destination = skill_root / name
            shutil.copytree(source, destination)
            policy = destination / "agents" / "openai.yaml"
            text = policy.read_text(encoding="utf-8")
            text = re.sub(
                r"(allow_implicit_invocation:\s*)false\b",
                r"\1true",
                text,
            )
            policy.write_text(text, encoding="utf-8")
    else:
        (home / ".agents" / "skills").mkdir(parents=True)
    return temporary


def run_codex(
    root: Path,
    prompt: str,
    condition: str,
    active_skills: list[str],
    model: str | None,
    reasoning_effort: str | None,
    timeout: int,
) -> tuple[dict[str, Any], int, float]:
    command = [
        "codex",
        "exec",
        "--json",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "--ignore-user-config",
    ]
    if model:
        command.extend(["--model", model])
    if reasoning_effort:
        command.extend(["-c", f"model_reasoning_effort=\"{reasoning_effort}\""])
    command.append(prompt)
    started = time.monotonic()
    (root / ".tmp").mkdir(exist_ok=True)
    temporary_home = evaluation_home(root, condition, active_skills)
    environment = os.environ.copy()
    environment["CODEX_HOME"] = temporary_home.name
    try:
        process = subprocess.Popen(
            command,
            cwd=temporary_home.name,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            trace = summarize_trace(stdout, stderr)
            return trace, process.returncode, time.monotonic() - started
        except subprocess.TimeoutExpired as exc:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()
            trace = summarize_trace(stdout or _text(exc.stdout), stderr or _text(exc.stderr))
            trace["status"] = "blocked"
            trace["stderr"].append(f"timeout after {timeout}s")
            return trace, 124, time.monotonic() - started
    finally:
        temporary_home.cleanup()


def validate_fixture(path: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    cases = load_cases(path)
    counts = Counter(case.get("expected") for case in cases)
    expected_skills = set(counts) - {"none"}
    if expected_skills != CANONICAL_ACTIVE:
        raise ValueError("benchmark fixture must cover exactly the six canonical active skills")
    if any(count < 10 for count in counts.values() if count):
        raise ValueError("each expected skill requires at least 10 benchmark cases")
    for case in cases:
        neighbors = case.get("neighbors", [])
        if not isinstance(neighbors, list) or any(neighbor not in CANONICAL_ACTIVE for neighbor in neighbors):
            raise ValueError(f"{case['id']}: neighbors must be canonical active skill names")
    return cases, dict(counts)


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def aggregate_results(path: Path) -> dict[str, Any]:
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    routing = routing_metrics(records)
    by_skill: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_skill[record.get("expected", "none")].append(record)
    pairs: dict[tuple[int, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for record in records:
        pairs[(record.get("run", 0), record.get("case_id", ""))][record.get("condition", "with")] = record
    utility_records: list[dict[str, Any]] = []
    for conditions in pairs.values():
        with_record = conditions.get("with")
        without_record = conditions.get("without")
        if with_record and without_record:
            utility_records.append(
                {
                    "with_status": with_record.get("task_status"),
                    "without_status": without_record.get("task_status"),
                    "with_tokens": (with_record.get("usage") or {}).get("total_tokens"),
                    "without_tokens": (without_record.get("usage") or {}).get("total_tokens"),
                }
            )
    return {
        "records": len(records),
        "routing": routing,
        "by_skill": {skill: routing_metrics(items) for skill, items in sorted(by_skill.items())},
        "utility": utility_metrics(utility_records) if utility_records else {"status": "NOT_ASSESSED"},
        "regressions": [
            regression_record(record, record)
            for record in records
            if record.get("status") == "completed" and record.get("expected") != record.get("actual")
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--results", type=Path)
    parser.add_argument("--mode", choices=("validate", "benchmark", "aggregate"), default="validate")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--condition", choices=("with", "without", "both"), default="with")
    parser.add_argument("--utility-only", action="store_true")
    parser.add_argument("--model")
    parser.add_argument("--reasoning-effort")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    root = args.root.resolve()
    fixture = args.fixture.resolve()
    try:
        cases, counts = validate_fixture(fixture)
        if args.mode == "validate":
            print(json.dumps({"status": "OK", "cases": len(cases), "by_expected": counts}, sort_keys=True))
            return 0
        if not args.results:
            raise ValueError("--results is required for benchmark and aggregate modes")
        results = args.results.resolve()
        if args.mode == "aggregate":
            print(json.dumps(aggregate_results(results), indent=2, sort_keys=True))
            return 0
        if args.runs < 1:
            raise ValueError("--runs must be positive")
        active = sorted({case["expected"] for case in cases if case["expected"] != "none"})
        if args.utility_only:
            selected_cases = [
                next(case for case in cases if case["expected"] == skill and case.get("style") == "direct")
                for skill in active
            ]
        else:
            selected_cases = cases[: args.limit] if args.limit else cases
        conditions = ("with", "without") if args.condition == "both" else (args.condition,)
        records: list[dict[str, Any]] = []
        for run in range(1, args.runs + 1):
            for condition in conditions:
                for case in selected_cases:
                    condition_name = "WITH-SKILL" if condition == "with" else "WITHOUT-SKILL"
                    trace, returncode, elapsed = run_codex(
                        root,
                        benchmark_prompt(case, active, condition_name),
                        condition,
                        active,
                        args.model,
                        args.reasoning_effort,
                        args.timeout,
                    )
                    report = reported_result(trace.get("final_answer"))
                    records.append(
                        {
                            "run": run,
                            "condition": condition,
                            "case_id": case["id"],
                            "prompt": case["prompt"],
                            "kind": case.get("kind"),
                            "style": case.get("style"),
                            "expected": case["expected"],
                            "actual": actual_from_trace(trace, set(active)),
                            "reported_skill": _normalise_actual(report.get("selected_skill")),
                            "task_status": report.get("task_status"),
                            "selection_source": trace["selection_source"],
                            "procedure_loads": trace["procedure_loads"],
                            "status": trace["status"],
                            "returncode": returncode,
                            "elapsed_seconds": round(elapsed, 3),
                            "usage": trace["usage"],
                            "commands": trace["commands"],
                            "tools": trace["tools"],
                            "trace": trace,
                        }
                    )
        write_jsonl(results, records)
        print(json.dumps({"status": "OK", "results": str(results), "records": len(records)}, sort_keys=True))
        return 0
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(f"FAIL skill evaluation: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
