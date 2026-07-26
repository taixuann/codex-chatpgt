#!/usr/bin/env python3
"""Deterministically validate workflow/job IO and cache policy."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import yaml

APPROVED_ROOTS = (Path.home() / ".codex", Path("/Users/tai/ai-labs/ops"))
SECRET_WORDS = ("password", "secret", "token", "api_key", "apikey", "credential", "private_key")

def validate_policy(policy: object, path: Path, label: str) -> str | None:
    if policy is None:
        policy = {"mode": "no-cache"}
    if not isinstance(policy, dict) or policy.get("mode") not in {"no-cache", "cache"}:
        return f"{label} cache_policy.mode must be no-cache or cache"
    if policy["mode"] == "no-cache" and "path" in policy:
        return f"{label} no-cache policy must not declare a path"
    if policy["mode"] == "cache":
        raw = policy.get("path")
        if not isinstance(raw, str) or not raw.strip() or not Path(raw).is_absolute():
            return f"{label} cache policy requires an absolute path"
        cache_path = Path(raw).expanduser().resolve()
        if not any(cache_path == root.resolve() or root.resolve() in cache_path.parents for root in APPROVED_ROOTS):
            return f"{label} cache path outside approved Codex operational roots: {raw}"
        if any(word in raw.lower() for word in SECRET_WORDS):
            return f"{label} cache path appears to contain credentials or secrets"
    return None

def validate_contract(data: dict, path: Path, label: str) -> str | None:
    for key in ("inputs", "outputs"):
        if key in data and (not isinstance(data[key], list) or any(not isinstance(v, (str, dict)) for v in data[key])):
            return f"{label} {key} must be a list of strings or mappings"
    if "overview" in data:
        overview = data["overview"]
        if (not isinstance(overview, dict) or not isinstance(overview.get("impact"), str)
                or not isinstance(overview.get("references", []), list)):
            return f"{label} overview requires string impact and list references"
    error = validate_policy(data.get("cache_policy"), path, label)
    if error:
        return error
    steps = data.get("steps")
    if steps is not None:
        if not isinstance(steps, list):
            return f"{label} steps must be a list"
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                return f"{label} step[{index}] must be a mapping"
            error = validate_contract(step, path, f"{label} step[{index}]")
            if error:
                return error
    return None

def validate(path: Path) -> int:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"FAIL {path}: invalid YAML: {exc}"); return 1
    if not isinstance(data, dict):
        print(f"FAIL {path}: document must be a mapping"); return 1
    error = validate_contract(data, path, "workflow")
    if error:
        print(f"FAIL {path}: {error}"); return 1
    policy = data.get("cache_policy", {"mode": "no-cache"})
    print(f"OK {path}: inputs/outputs and recursive steps valid; cache_policy={policy['mode']}")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    return max(validate(path) for path in args.paths)

if __name__ == "__main__":
    sys.exit(main())
