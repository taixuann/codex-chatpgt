#!/usr/bin/env python3
"""Validate the metadata and links of a bounded session packet."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

import yaml


SESSION_ID = re.compile(r"^[0-9]{8}_[a-z0-9]+(?:-[a-z0-9]+)*_[0-9]{3}$")
REQUIRED = {"context.md", "plan.md", "task.md", "references.yaml"}
OPTIONAL = {"spec.md", "franky.ticket.yaml", "franky.results.yaml"}
ARTIFACT_KEYS = {"context", "spec", "plan", "tasks", "ticket", "results", "references", "rag_manifest"}
REQUIRED_ARTIFACT_KEYS = {"context", "plan", "tasks", "references"}
STATUSES = {"proposed", "observed", "in_progress", "needs_review", "blocked", "acceptance_ready", "closed", "archived", "not_assessed"}
ARTIFACT_META = {
    "context.md": "context",
    "spec.md": "spec",
    "plan.md": "plan",
    "task.md": "tasks",
}


class PacketError(ValueError):
    pass


def _load(path: Path) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PacketError(f"invalid YAML: {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise PacketError(f"expected a YAML mapping: {path.name}")
    return value


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise PacketError(f"missing frontmatter: {path.name}")
    try:
        _, header, _ = text.split("---\n", 2)
        value = yaml.safe_load(header)
    except (ValueError, yaml.YAMLError) as exc:
        raise PacketError(f"invalid frontmatter: {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise PacketError(f"frontmatter must be a mapping: {path.name}")
    return value


def _check_link(packet: Path, raw: object, *, optional: bool = False) -> None:
    if not isinstance(raw, str) or not raw:
        raise PacketError(f"invalid artifact link in {packet.name}")
    target = (packet.parent / raw).resolve()
    if packet.parent.resolve() not in target.parents and target != packet.parent.resolve():
        raise PacketError(f"artifact link escapes packet: {packet.name}: {raw}")
    if not target.exists() and optional:
        return
    if not target.exists():
        raise PacketError(f"missing artifact link: {packet.name}: {raw}")


def validate(packet: Path) -> None:
    if packet.is_symlink() or not packet.is_dir():
        raise PacketError("packet root must be a regular directory")
    session_path = packet / "session.yaml"
    if not session_path.is_file():
        raise PacketError("session.yaml is required")
    session = _load(session_path)
    session_id = session.get("session_id")
    if not isinstance(session_id, str) or not SESSION_ID.fullmatch(session_id):
        raise PacketError("session_id must match YYYYMMDD_slug_NNN")
    if packet.name != session_id:
        raise PacketError("packet directory name must equal session_id")
    if session.get("kind") != "codex.session-packet.v1":
        raise PacketError("session.yaml kind must be codex.session-packet.v1")
    source_state = session.get("source_state")
    if not isinstance(source_state, dict) or not source_state.get("commit") or not source_state.get("recorded_at"):
        raise PacketError("session.yaml source_state.commit and recorded_at are required")
    repository_root = session.get("repository_root")
    packet_root = session.get("packet_root")
    if not isinstance(repository_root, str) or not repository_root:
        raise PacketError("session.yaml repository_root is required")
    if not isinstance(packet_root, str) or not packet_root:
        raise PacketError("session.yaml packet_root is required")
    repository_path = Path(repository_root).expanduser()
    if not repository_path.is_absolute() or not repository_path.is_dir():
        raise PacketError("session.yaml repository_root must be an existing absolute directory")
    if Path(packet_root).is_absolute():
        raise PacketError("session.yaml packet_root must be relative to repository_root")
    expected_packet = (repository_path / packet_root).resolve()
    if expected_packet != packet.resolve():
        raise PacketError("session.yaml packet_root must resolve to the validated packet")
    if session.get("status") not in STATUSES:
        raise PacketError("session.yaml status is invalid")

    artifacts = session.get("artifacts")
    if not isinstance(artifacts, dict):
        raise PacketError("session.yaml artifacts mapping is required")
    unknown_keys = set(artifacts) - ARTIFACT_KEYS
    if unknown_keys:
        raise PacketError(f"unknown artifact-map key(s): {sorted(unknown_keys)}")
    missing_keys = REQUIRED_ARTIFACT_KEYS - set(artifacts)
    if missing_keys:
        raise PacketError(f"missing artifact-map key(s): {sorted(missing_keys)}")
    names = {path.name for path in packet.iterdir() if path.is_file()}
    missing = REQUIRED - names
    if missing:
        raise PacketError(f"missing required artifacts: {sorted(missing)}")
    unknown = names - {"session.yaml", *REQUIRED, *OPTIONAL}
    if unknown:
        raise PacketError(f"unexpected packet files: {sorted(unknown)}")

    for key, raw in artifacts.items():
        if not isinstance(raw, str):
            raise PacketError(f"artifact path must be a string: {key}")
        _check_link(session_path, raw, optional=key in {"spec", "ticket", "results", "rag_manifest"})

    expected_names = {
        "context": "context.md",
        "spec": "spec.md",
        "plan": "plan.md",
        "tasks": "task.md",
        "ticket": "franky.ticket.yaml",
        "results": "franky.results.yaml",
        "references": "references.yaml",
        "rag_manifest": ".rag/manifest.yaml",
    }
    for key, expected in expected_names.items():
        if key in artifacts and Path(artifacts[key]).as_posix() != expected:
            raise PacketError(f"artifact-map path for {key} must be {expected}")

    frontmatter_links: dict[str, dict[str, list[str]]] = {}
    artifact_link_names: dict[str, dict[str, list[str]]] = {}
    for name in sorted(REQUIRED | OPTIONAL):
        path = packet / name
        if not path.exists():
            continue
        if name.endswith(".md"):
            metadata = _frontmatter(path)
            if metadata.get("kind") != "codex.session-artifact.v1":
                raise PacketError(f"invalid artifact kind: {name}")
            expected_artifact = ARTIFACT_META[name]
            if metadata.get("artifact") != expected_artifact:
                raise PacketError(f"artifact identity mismatch: {name}")
            if metadata.get("session_id") != session_id:
                raise PacketError(f"session_id mismatch: {name}")
            if metadata.get("status") not in STATUSES:
                raise PacketError(f"invalid artifact status: {name}")
            provenance = metadata.get("provenance")
            if not isinstance(provenance, dict) or not provenance.get("source_commit") or not provenance.get("observed_at") or not provenance.get("recorded_by"):
                raise PacketError(f"provenance source_commit, observed_at, and recorded_by are required: {name}")
            frontmatter_links[name] = {"upstream": [], "downstream": []}
            artifact_link_names[name] = {"upstream": [], "downstream": []}
            for direction in ("upstream", "downstream"):
                links = metadata.get(direction, [])
                if not isinstance(links, list):
                    raise PacketError(f"{direction} must be a list: {name}")
                for link in links:
                    optional_link = isinstance(link, str) and Path(link).name in OPTIONAL
                    _check_link(path, link, optional=optional_link)
                    if isinstance(link, str):
                        target_name = Path(link).name
                        artifact_link_names[name][direction].append(target_name)
                        if target_name in ARTIFACT_META:
                            frontmatter_links[name][direction].append(target_name)
        elif name in {"franky.ticket.yaml", "franky.results.yaml"}:
            record = _load(path)
            expected_kind = "franky.task.v1" if name.startswith("franky.ticket") else "franky.result.v1"
            if record.get("kind") != expected_kind:
                raise PacketError(f"invalid record kind: {name}")
        elif name == "references.yaml":
            references = _load(path)
            if references.get("kind") != "codex.session-references.v1":
                raise PacketError("references.yaml kind is invalid")
            if references.get("session_id") != session_id:
                raise PacketError("references.yaml session_id mismatch")
            entries = references.get("references")
            if not isinstance(entries, list) or not entries:
                raise PacketError("references.yaml references must be a non-empty list")
            required_reference_fields = {"path", "kind", "state", "commit_or_hash", "observed_at", "relationship"}
            for index, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    raise PacketError(f"references.yaml entry {index} must be a mapping")
                missing_fields = required_reference_fields - set(entry)
                if missing_fields:
                    raise PacketError(f"references.yaml entry {index} missing fields: {sorted(missing_fields)}")
                for field in required_reference_fields:
                    if not isinstance(entry[field], str) or not entry[field] or entry[field].startswith("<"):
                        raise PacketError(f"references.yaml entry {index} field {field} must be concrete")
                parsed = urlparse(entry["path"])
                if not parsed.scheme and Path(entry["path"]).is_absolute():
                    raise PacketError(f"references.yaml entry {index} path must be relative or a URL")

    for name, links in frontmatter_links.items():
        for target in links["downstream"]:
            reciprocal = frontmatter_links.get(target, {}).get("upstream", [])
            if name not in reciprocal:
                raise PacketError(f"missing reciprocal upstream link: {name} -> {target}")
        for target in links["upstream"]:
            reciprocal = frontmatter_links.get(target, {}).get("downstream", [])
            if name not in reciprocal:
                raise PacketError(f"missing reciprocal downstream link: {target} -> {name}")

    rag = packet / ".rag"
    if rag.exists():
        if rag.is_symlink() or not rag.is_dir():
            raise PacketError(".rag must be a regular directory")
        manifest_path = rag / "manifest.yaml"
        if not manifest_path.is_file():
            raise PacketError(".rag/manifest.yaml is required when .rag exists")
        manifest = _load(manifest_path)
        if manifest.get("kind") != "codex.session-rag-index.v1":
            raise PacketError("invalid .rag manifest kind")
        if manifest.get("session_id") != session_id:
            raise PacketError(".rag manifest session_id mismatch")
        if manifest.get("engine") != "lightrag":
            raise PacketError(".rag manifest engine must be lightrag")
        if not isinstance(manifest.get("index_version"), (str, int)) or not manifest.get("generated_at"):
            raise PacketError(".rag manifest index_version and generated_at are required")
        if not isinstance(manifest.get("source_root"), str) or not manifest["source_root"]:
            raise PacketError(".rag manifest source_root is required")
        if not isinstance(manifest.get("included"), list) or not isinstance(manifest.get("excluded"), list):
            raise PacketError(".rag manifest included and excluded lists are required")
        if manifest.get("status") not in {"ready", "stale", "not_assessed", "degraded"}:
            raise PacketError(".rag manifest status is invalid")

    ticket = packet / "franky.ticket.yaml"
    result = packet / "franky.results.yaml"
    if ticket.exists() != result.exists():
        raise PacketError("franky.ticket.yaml and franky.results.yaml must be provided together")
    if ticket.exists():
        if artifacts.get("ticket") != "franky.ticket.yaml" or artifacts.get("results") != "franky.results.yaml":
            raise PacketError("ticket and result files must be declared in the artifact map")
        task_links = artifact_link_names.get("task.md", {})
        if "franky.ticket.yaml" not in task_links.get("upstream", []) or "franky.results.yaml" not in task_links.get("downstream", []):
            raise PacketError("task.md must link to the Franky ticket upstream and result downstream")
    if ticket.is_file() and result.is_file():
        root = next((candidate for candidate in (packet, *packet.parents) if (candidate / "ops/schemas/franky-task.schema.yaml").is_file()), None)
        if root is not None:
            validator_path = root / "ops/scripts/validate_franky_contracts.py"
            spec = importlib.util.spec_from_file_location("franky_contracts", validator_path)
            if spec is None or spec.loader is None:
                raise PacketError("cannot load Franky contract validator")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            try:
                module.validate(ticket, result, root / "manifests/agent-capability-repertoires.yaml")
            except (OSError, ValueError) as exc:
                raise PacketError(f"Franky contract validation failed: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    args = parser.parse_args(argv)
    try:
        validate(args.packet)
    except (OSError, PacketError) as exc:
        print(f"FAIL session-packet: {exc}", file=sys.stderr)
        return 1
    print(f"PASS session-packet: {args.packet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
