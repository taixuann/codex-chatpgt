#!/usr/bin/env python3
"""Validate the compact skill-creator routing/lifecycle case contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

import yaml


REQUIRED_ROUTING = {
    "route-explicit-positive",
    "route-implicit-positive",
    "route-contextual-positive",
    "route-adjacent-negative",
    "route-sibling-conflict",
}
REQUIRED_BEHAVIOR = {
    "create-local-upstream",
    "create-multimode-one-skill",
    "create-no-skill",
    "update-bounded",
    "update-substantive",
    "maintain-upstream-drift",
    "maintain-overlap",
    "maintain-localize",
    "maintain-retire",
    "evaluate-good",
    "evaluate-broad-description",
    "evaluate-sibling-collision",
    "evaluate-decorative-resources",
    "evaluate-skipped-process",
}


def validate(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    cases = data.get("cases")
    if data.get("schema_version") != 1 or data.get("skill") != "skill-creator":
        return ["schema_version 1 and skill skill-creator are required"]
    if not isinstance(cases, list):
        return ["cases must be a list"]
    seen = {case.get("id") for case in cases if isinstance(case, dict)}
    errors = [f"missing case: {case_id}" for case_id in sorted((REQUIRED_ROUTING | REQUIRED_BEHAVIOR) - seen)]
    if len(seen) != len(cases):
        errors.append("case IDs must be unique and every case must be a mapping")
    for case in cases:
        if not isinstance(case, dict) or not case.get("prompt") or not case.get("kind"):
            errors.append("every case requires kind and prompt")
            continue
        if not isinstance(case.get("expected"), str) or not case["expected"].strip():
            errors.append(f"{case['id']}: expected outcome is required")
    return errors


def _final_text(events: list[dict]) -> str:
    texts = []
    for event in events:
        item = event.get("item") if isinstance(event, dict) else None
        if not isinstance(item, dict) or item.get("type") not in {"agent_message", "assistant_message", "message"}:
            continue
        value = item.get("text") or item.get("content")
        if isinstance(value, str):
            texts.append(value)
    return texts[-1] if texts else ""


def _json_object(text: str) -> dict:
    try:
        value = json.loads(text.strip().strip("`").removeprefix("json").strip())
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _runtime_observed(events: list[dict], stdout: str) -> bool:
    """Require an observable load signal before reporting a behavioral pass."""
    for event in events:
        for key in ("skill_loads", "loaded_skills", "loaded_skill"):
            value = event.get(key) if isinstance(event, dict) else None
            values = value if isinstance(value, list) else [value]
            if any(isinstance(item, str) and "skill-creator" in item for item in values):
                return True
    return "skill-creator/SKILL.md" in stdout


def run_case(case: dict, runtime: str, timeout: int) -> dict:
    prompt = (
        "Run this bounded read-only skill-creator evaluation. Use the skill-creator "
        "skill if the host loads it. Return exactly one JSON object with keys "
        "selected_skill and disposition; selected_skill is skill-creator or none.\n\n"
        f"Case {case['id']} ({case['kind']}): {case['prompt']}"
    )
    base = {"case_id": case["id"], "expected": case["expected"]}
    if not shutil.which(runtime):
        return {**base, "status": "NOT_ASSESSED", "reason": f"runtime not found: {runtime}"}
    command = [runtime, "exec", "--json", "--ephemeral", "--sandbox", "read-only", "--skip-git-repo-check", "--ignore-user-config", prompt]
    started = time.monotonic()
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {**base, "status": "NOT_ASSESSED", "reason": f"runtime timeout after {timeout}s"}
    stdout = process.stdout or ""
    events = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    report = _json_object(_final_text(events))
    key = "selected_skill" if case["kind"] == "routing" else "disposition"
    observed = report.get(key)
    loaded = _runtime_observed(events, stdout)
    if process.returncode != 0:
        status, reason = "NOT_ASSESSED", f"runtime exit {process.returncode}"
    elif not loaded:
        status, reason = "NOT_ASSESSED", "runtime did not expose a skill-load signal"
    elif observed == case["expected"]:
        status, reason = "PASS", "runtime load and expected outcome observed"
    else:
        status, reason = "FAIL", f"expected {case['expected']}, observed {observed!r}"
    return {
        **base,
        "observed": observed,
        "status": status,
        "runtime_observed": loaded,
        "events": len(events),
        "returncode": process.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "reason": reason,
        "stderr": (process.stderr or "").splitlines()[-5:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", type=Path)
    parser.add_argument("--run", action="store_true", help="execute bounded runtime cases")
    parser.add_argument("--case-id", action="append", help="run only this case; repeatable")
    parser.add_argument("--runtime", default="codex")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--results", type=Path, help="write structured JSON results")
    args = parser.parse_args()
    try:
        errors = validate(args.cases)
        data = yaml.safe_load(args.cases.read_text(encoding="utf-8")) or {}
        cases = data.get("cases", [])
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        print(f"FAIL eval cases: {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"FAIL eval cases: {error}")
        return 1
    if not args.run:
        print(f"OK eval cases: {len(REQUIRED_ROUTING)} routing and {len(REQUIRED_BEHAVIOR)} behavioral cases")
        return 0
    selected = [case for case in cases if not args.case_id or case["id"] in args.case_id]
    results = [run_case(case, args.runtime, args.timeout) for case in selected]
    if args.results:
        args.results.write_text(json.dumps({"schema_version": 1, "results": results}, indent=2) + "\n", encoding="utf-8")
    counts = {status: sum(result["status"] == status for result in results) for status in ("PASS", "FAIL", "NOT_ASSESSED")}
    print(json.dumps({"status": "OK", "cases": len(results), "counts": counts, "results": results}, sort_keys=True))
    return 1 if counts["FAIL"] else (2 if counts["NOT_ASSESSED"] else 0)


if __name__ == "__main__":
    sys.exit(main())
