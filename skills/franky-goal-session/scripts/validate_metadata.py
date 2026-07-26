#!/usr/bin/env python3
"""Validate role references and shared stable-ID/node metadata."""
from pathlib import Path
import argparse
import subprocess
import sys

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ontology", type=Path, default=Path(__file__).resolve().parents[1] / "references/ontology.yaml")
    parser.add_argument("--roles", type=Path)
    args = parser.parse_args()
    script = Path(__file__).with_name("validate_ontology.py")
    command = [sys.executable, str(script), str(args.ontology)]
    if args.roles:
        command += ["--roles", str(args.roles)]
    result = subprocess.run(command, text=True, capture_output=True)
    print(result.stdout, end="")
    if result.returncode:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
