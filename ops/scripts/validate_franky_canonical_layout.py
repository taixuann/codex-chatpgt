#!/usr/bin/env python3
"""Validate the canonical Franky entrypoint and compatibility adapters."""

from pathlib import Path
import sys
import yaml


ROOT = Path(__file__).resolve().parents[2] / "workflows" / "franky"
EXPECTED = {
    "franky.yaml": "WF-FRANKY-CANONICAL",
}


def main() -> int:
    try:
        for filename, workflow_id in EXPECTED.items():
            path = ROOT / filename
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            if data.get("id") != workflow_id:
                raise ValueError(f"{filename} has unexpected workflow ID")
        canonical = yaml.safe_load((ROOT / "franky.yaml").read_text(encoding="utf-8"))
        if canonical.get("canonical") is not True or len(canonical.get("pipelines", [])) != 15:
            raise ValueError("canonical workflow must expose all 15 purpose branches")
        if canonical.get("authority_scope") != "franky_control_plane":
            raise ValueError("canonical workflow must declare Franky control-plane scope")
        retired = set(canonical.get("retired_entrypoint_ids", []))
        if retired != {"WF-FRANKY-INSTALL", "WF-FRANKY-MAINTENANCE"}:
            raise ValueError("canonical workflow must record all retired entrypoint IDs")
        for forbidden in ("README.md", "workflow-catalog.yaml", "scripts", "tests"):
            if (ROOT / forbidden).exists():
                raise ValueError(f"runtime workflow tree still contains removed clutter: {forbidden}")
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL {ROOT}: {exc}")
        return 1
    print(f"OK {ROOT}: canonical entrypoint and branch tree are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
