#!/usr/bin/env python3
"""Reproduce and verify the pinned agent-creator donor without adapting it."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


DONOR_REPOSITORY = "jscraik/Agent-Skills"
DONOR_URL = f"https://github.com/{DONOR_REPOSITORY}.git"
DONOR_COMMIT = "d00c351fe53460afba860f8cdb1580d7cfece7e4"
DONOR_SUBTREE = Path("Skills/agent-ops/codex-agent-creator")
EXPECTED_BLOBS = {
    "SKILL.md": "e456a55ec17aae2079cc3f6c196f6afc50546aa6",
    "agents/openai.yaml": "33eafa9626a86e5a6c149b6ff826689bd7bef458",
    "references/contract.yaml": "604ade211cef431e5a49f717a4e6366649523bed",
    "references/discovery-interview.md": "aca4eb2a346a445826d0c5412dfac37413ddba83",
    "references/evals.yaml": "71e97b4b3639b0799d27fb1c0af6e82ae4b3f81b",
    "references/role-config-examples.md": "65c986977c07cd8b1afca06b97c3466923c58f1c",
    "references/role-creation-guide.md": "671988a141b558e4ecca2afba41e2ca582db1128",
    "references/task-profile.json": "e88bff5ccf6403c6f73b9e404d3b1d97ebd1bb32",
}


def run(command: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=check, capture_output=True, text=True)


def clone_baseline(destination: Path) -> None:
    run(["git", "init", "--quiet"], destination)
    run(["git", "remote", "add", "origin", DONOR_URL], destination)
    run(["git", "fetch", "--quiet", "--depth", "1", "origin", DONOR_COMMIT], destination)
    run(["git", "checkout", "--quiet", "--detach", "FETCH_HEAD"], destination)


def verify_tree(source: Path) -> dict[str, str]:
    commit = run(["git", "rev-parse", "HEAD"], source).stdout.strip()
    if commit != DONOR_COMMIT:
        raise RuntimeError(f"donor commit mismatch: {commit} != {DONOR_COMMIT}")
    observed: dict[str, str] = {}
    for relative, expected in EXPECTED_BLOBS.items():
        path = source / DONOR_SUBTREE / relative
        if not path.is_file():
            raise RuntimeError(f"missing donor file: {relative}")
        blob = run(["git", "hash-object", str(DONOR_SUBTREE / relative)], source).stdout.strip()
        if blob != expected:
            raise RuntimeError(f"blob mismatch for {relative}: {blob} != {expected}")
        observed[relative] = blob
    license_text = (source / "LICENSE").read_text(encoding="utf-8")
    if not license_text.startswith("                                 Apache License"):
        raise RuntimeError("donor LICENSE is not the expected Apache-2.0 text")
    return observed


def parse_donor_files(source: Path) -> None:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - CI installs the contract dependency
        raise RuntimeError("PyYAML is required for donor reproduction") from exc
    json.loads((source / DONOR_SUBTREE / "references/task-profile.json").read_text())
    for name in ("references/contract.yaml", "references/evals.yaml"):
        yaml.safe_load((source / DONOR_SUBTREE / name).read_text(encoding="utf-8"))


def current_validation(repo_root: Path, source: Path) -> dict[str, object]:
    quick = repo_root / "skills/skill-creator/scripts/quick_validate.py"
    quick_result = run(["python3", str(quick), str(source / DONOR_SUBTREE)], repo_root, check=False)
    eval_validator = repo_root / "skills/skill-creator/scripts/validate_eval_cases.py"
    eval_result = run(
        ["python3", str(eval_validator), str(source / DONOR_SUBTREE / "references/evals.yaml")],
        repo_root,
        check=False,
    )
    if quick_result.returncode != 0:
        raise RuntimeError("donor structural validation unexpectedly failed")
    if eval_result.returncode == 0:
        raise RuntimeError("donor eval contract unexpectedly passes the current contract")
    return {
        "quick_validate": "PASS",
        "current_eval_contract": "EXPECTED_FAIL_CLOSED",
        "current_eval_exit_code": eval_result.returncode,
        "current_eval_failure_digest": hashlib.sha256(eval_result.stdout.encode()).hexdigest(),
    }


def reproduce(repo_root: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="agent-creator-donor-") as directory:
        source = Path(directory)
        clone_baseline(source)
        blobs = verify_tree(source)
        parse_donor_files(source)
        validation = current_validation(repo_root, source)
    return {
        "repository": DONOR_REPOSITORY,
        "ref": DONOR_COMMIT,
        "source": str(DONOR_SUBTREE) + "/",
        "license": "Apache-2.0",
        "blob_sha1": blobs,
        "parse": "PASS",
        **validation,
        "script": "skills/agent-creator/scripts/verify_upstream_baseline.py",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).parents[3])
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    result = reproduce(args.repo_root.resolve())
    result["captured_at_utc"] = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()
    result["capture_revision"] = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=args.repo_root.resolve(), check=False, capture_output=True, text=True
    ).stdout.strip() or "NOT_ASSESSED"
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        args.json_out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
