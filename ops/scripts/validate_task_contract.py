#!/usr/bin/env python3
"""Validate a Codex task contract against the checked-in YAML schema."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "task-contract.schema.yaml"
TYPE_MAP = {"object": dict, "array": list, "string": str, "boolean": bool, "integer": int}


def _type_ok(value: object, expected: str) -> bool:
    actual = TYPE_MAP[expected]
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, actual)


def _validate(value: object, spec: dict, path: str) -> None:
    expected = spec.get("type")
    if expected and not _type_ok(value, expected):
        raise ValueError(f"{path}: expected {expected}")
    if expected == "string" and len(value) < spec.get("minLength", 0):
        raise ValueError(f"{path}: must not be empty")
    if expected == "object":
        required = spec.get("required", [])
        missing = [key for key in required if key not in value]
        if missing:
            raise ValueError(f"{path}: missing required field(s): {', '.join(missing)}")
        properties = spec.get("properties", {})
        if spec.get("additionalProperties") is False:
            unknown = sorted(set(value) - set(properties))
            if unknown:
                raise ValueError(f"{path}: undeclared field(s): {', '.join(unknown)}")
        for key, child in value.items():
            if key in properties:
                _validate(child, properties[key], f"{path}.{key}")
    if expected == "array":
        item_spec = spec.get("items", {})
        for index, child in enumerate(value):
            _validate(child, item_spec, f"{path}[{index}]")


def validate(contract_path: Path) -> None:
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    _validate(contract, schema, "$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path)
    args = parser.parse_args()
    try:
        validate(args.contract)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {args.contract}: {exc}")
        return 1
    print(f"OK {args.contract}: task-contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
