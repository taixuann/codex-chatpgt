#!/usr/bin/env python3
"""Project a validated plan packet into a deterministic task list."""
from __future__ import annotations
import argparse
from pathlib import Path
import yaml
import importlib.util
_spec = importlib.util.spec_from_file_location("validate_plan_packet", Path(__file__).with_name("validate_plan_packet.py")); assert _spec and _spec.loader
_validator = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_validator)
validate = _validator.validate

def project(packet: dict, *, ready: bool = False, packet_path: Path | None = None) -> dict:
    validate(packet, ready_for_build=ready, deep=ready, packet_path=packet_path)
    tasks = [{"id": t["id"], "title": t["title"], "acceptance": t["acceptance"], "verification": t["verification"], "depends_on": t.get("depends_on", [])} for t in packet["tasks"]]
    return {"schema_version": 1, "kind": "plan_task_projection", "source": packet.get("revision", packet["source"]["locator"]), "objective": packet["objective"], "checkpoints": packet["checkpoints"], "out_of_scope": packet["out_of_scope"], "tasks": tasks}

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("packet", type=Path); parser.add_argument("--output", type=Path); parser.add_argument("--ready", action="store_true")
    args = parser.parse_args(); result = project(yaml.safe_load(args.packet.read_text(encoding="utf-8")), ready=args.ready, packet_path=args.packet); rendered = yaml.safe_dump(result, sort_keys=False)
    if args.output:
        if args.output.exists() and args.output.read_text(encoding="utf-8") != rendered: raise SystemExit("existing projection differs; refusing non-idempotent overwrite")
        args.output.write_text(rendered, encoding="utf-8")
    else: print(rendered, end="")
    return 0
if __name__ == "__main__": raise SystemExit(main())
