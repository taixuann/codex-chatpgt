#!/usr/bin/env python3
"""Run a bounded synthetic Codex App Server role/delegation probe.

The probe deliberately uses a temporary fixture and a synthetic role. It never
loads repository files into the model context. Missing native metadata remains
NOT_ASSESSED in the receipt.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import select
import shutil
import subprocess
import tempfile
import time
from typing import Any


MODEL = "gpt-5.6-luna"
REASONING = "medium"
SKILL_NAME = "agent-creator"


class AppServer:
    def __init__(self, cwd: pathlib.Path, codex_home: pathlib.Path) -> None:
        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex_home)
        self.process = subprocess.Popen(
            ["codex", "app-server", "--listen", "stdio://"],
            cwd=cwd,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.sequence = 0
        self.events: list[dict[str, Any]] = []

    def send(self, method: str, params: dict[str, Any] | None = None, timeout: int = 60) -> dict[str, Any]:
        self.sequence += 1
        request_id = self.sequence
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps({"id": request_id, "method": method, "params": params or {}}) + "\n")
        self.process.stdin.flush()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            assert self.process.stdout is not None
            ready, _, _ = select.select([self.process.stdout], [], [], 1)
            if not ready:
                continue
            line = self.process.stdout.readline()
            if not line:
                break
            message = json.loads(line)
            if message.get("id") == request_id:
                return message
            self.events.append(message)
        raise RuntimeError(f"timed out waiting for App Server response: {method}")

    def close(self) -> str:
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
        stderr = self.process.stderr.read() if self.process.stderr else ""
        return stderr


def make_fixture() -> tuple[pathlib.Path, pathlib.Path]:
    fixture = pathlib.Path(tempfile.mkdtemp(prefix="agent-creator-native-fixture-"))
    (fixture / "probe.txt").write_text("probe-marker-issue105\n", encoding="utf-8")
    home = pathlib.Path(tempfile.mkdtemp(prefix="agent-creator-native-home-"))
    agents = home / "agents"
    agents.mkdir()
    (agents / "probe-reviewer.toml").write_text(
        """name = \"probe-reviewer\"
description = \"Use only for the isolated read-only probe fixture; not ordinary implementation.\"
model = \"gpt-5.6-luna\"
model_reasoning_effort = \"medium\"
sandbox_mode = \"read-only\"
developer_instructions = \"Read only probe.txt, report its marker, do not edit files, do not spawn agents.\"
""",
        encoding="utf-8",
    )
    for name in ("auth.json", "config.toml"):
        source = pathlib.Path("/Users/tai/.codex") / name
        if source.exists():
            (home / name).symlink_to(source)
    return fixture, home


def run_discovery_probe() -> dict[str, Any]:
    fixture, home = make_fixture()
    skill = fixture / "skills" / SKILL_NAME
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: agent-creator\ndescription: synthetic discovery probe\n---\n",
        encoding="utf-8",
    )
    server = AppServer(fixture, home)
    try:
        initialize = server.send(
            "initialize",
            {
                "clientInfo": {"name": "agent-creator-discovery-probe", "version": "0.1"},
                "capabilities": {"experimentalApi": True},
            },
        )
        assert server.process.stdin is not None
        server.process.stdin.write('{"method":"initialized","params":{}}\n')
        server.process.stdin.flush()
        default = server.send(
            "skills/list",
            {"cwds": [str(fixture)], "forceReload": True},
        )
        extra_root = fixture / "skills"
        extra = server.send(
            "skills/extraRoots/set",
            {"extraRoots": [str(extra_root)]},
        )
        listed = server.send(
            "skills/list",
            {"cwds": [str(fixture)], "forceReload": True},
        )
        default_skills = [
            item
            for entry in default.get("result", {}).get("data", [])
            for item in entry.get("skills", [])
            if item.get("name") == SKILL_NAME
        ]
        explicit_skills = [
            item
            for entry in listed.get("result", {}).get("data", [])
            for item in entry.get("skills", [])
            if item.get("name") == SKILL_NAME
        ]
        return {
            "runtime": initialize.get("result", {}).get("userAgent"),
            "probe": "codex app-server skills/list",
            "skill_name": SKILL_NAME,
            "repo_skill_name": SKILL_NAME,
            "api_probe": "OBSERVED",
            "repo_skill_discovery": "OBSERVED_WITH_EXPLICIT_EXTRA_ROOT" if explicit_skills else "NOT_ASSESSED",
            "default_repo_skill_discovery": "OBSERVED_EMPTY" if not default_skills else "OBSERVED",
            "default_repo_skill_match_count": len(default_skills),
            "explicit_extra_root_discovery": "OBSERVED" if explicit_skills else "NOT_ASSESSED",
            "explicit_extra_root_match_count": len(explicit_skills),
            "explicit_extra_root": str(extra_root),
            "matching_paths": [item.get("path") for item in explicit_skills],
            "extra_root_set": "OBSERVED" if "result" in extra else "NOT_ASSESSED",
            "extra_root_probe": {
                "protocol": "skills/extraRoots/set -> skills/list",
                "status": "OBSERVED" if explicit_skills else "NOT_ASSESSED",
                "repo_skill_match_count": len(explicit_skills),
                "matching_path": explicit_skills[0].get("path") if explicit_skills else None,
                "extra_root": str(extra_root),
            },
            "activation_status": "NOT_ASSESSED",
            "reason": "Native listing exposes discovery, not a per-turn skill-load or activation event.",
            "errors": default.get("error") or listed.get("error") or extra.get("error") or [],
        }
    finally:
        server.close()
        shutil.rmtree(fixture, ignore_errors=True)
        shutil.rmtree(home, ignore_errors=True)


def compact_thread(thread: dict[str, Any]) -> dict[str, Any]:
    return {key: thread.get(key) for key in ("id", "parentThreadId", "agentRole", "modelProvider", "cwd", "status")}


def run_role_spawn_probe(timeout_seconds: int = 240) -> dict[str, Any]:
    fixture, home = make_fixture()
    server = AppServer(fixture, home)
    child_ids: set[str] = set()
    try:
        initialize = server.send(
            "initialize",
            {
                "clientInfo": {"name": "agent-creator-native-probe", "version": "0.1"},
                "capabilities": {"experimentalApi": True},
            },
        )
        assert server.process.stdin is not None
        server.process.stdin.write('{"method":"initialized","params":{}}\n')
        server.process.stdin.flush()
        started = server.send(
            "thread/start",
            {
                "cwd": str(fixture),
                "model": MODEL,
                "config": {"model_reasoning_effort": REASONING},
                "approvalPolicy": "never",
                "sandbox": "read-only",
                "ephemeral": True,
                "serviceName": "agent-creator-native-probe",
            },
        )
        parent_id = started["result"]["thread"]["id"]
        turn = server.send(
            "turn/start",
            {
                "threadId": parent_id,
                "effort": REASONING,
                "input": [
                    {
                        "type": "text",
                        "text": (
                            "Use the collaboration spawn-agent tool to delegate one bounded read-only task "
                            "to custom agent role probe-reviewer. The child must read only probe.txt, report "
                            "the exact marker, and not edit or spawn. Wait for the child result. Do not simulate "
                            "delegation or claim it happened unless a tool event confirms it."
                        ),
                    }
                ],
            },
        )
        turn_id = turn["result"]["turn"]["id"]
        deadline = time.monotonic() + timeout_seconds
        completed = False
        while time.monotonic() < deadline:
            assert server.process.stdout is not None
            ready, _, _ = select.select([server.process.stdout], [], [], 2)
            if not ready:
                continue
            line = server.process.stdout.readline()
            if not line:
                break
            event = json.loads(line)
            server.events.append(event)
            params = event.get("params", {})
            item = params.get("item", {})
            child_ids.update(item.get("receiverThreadIds") or [])
            thread = params.get("thread", {})
            if thread.get("parentThreadId") == parent_id and thread.get("id"):
                child_ids.add(thread["id"])
            if event.get("method") == "turn/completed" and params.get("turn", {}).get("id") == turn_id:
                completed = True
                break
        collab_items = [
            event.get("params", {}).get("item", {})
            for event in server.events
            if event.get("params", {}).get("item", {}).get("type") == "collabAgentToolCall"
        ]
        child_metadata: list[dict[str, Any]] = []
        metadata_errors: list[str] = []
        for child_id in sorted(child_ids):
            response = server.send("thread/read", {"threadId": child_id}, timeout=15)
            thread = response.get("result", {}).get("thread")
            if thread:
                child_metadata.append(compact_thread(thread))
            elif response.get("error"):
                metadata_errors.append(str(response["error"]))
        if not child_metadata:
            listed = server.send(
                "thread/list",
                {"parentThreadId": parent_id, "limit": 20},
                timeout=15,
            )
            for thread in listed.get("result", {}).get("data", []):
                child_metadata.append(compact_thread(thread))
            if listed.get("error"):
                metadata_errors.append(str(listed["error"]))
        observed_roles = {item.get("agentRole") for item in child_metadata if item.get("agentRole")}
        started_thread = started.get("result", {}).get("thread", {})
        return {
            "runtime": initialize.get("result", {}).get("userAgent"),
            "model": MODEL,
            "requested_reasoning_effort": REASONING,
            "effective_reasoning_effort": started_thread.get("reasoningEffort", "NOT_EXPOSED"),
            "sandbox": "read-only",
            "fixture": "synthetic_only",
            "parent_thread_id": parent_id,
            "parent_turn_completed": completed,
            "return_completion": "OBSERVED" if completed else "NOT_ASSESSED",
            "collab_spawn_event": "OBSERVED" if collab_items else "NOT_ASSESSED",
            "sender_thread_id": collab_items[0].get("senderThreadId") if collab_items else None,
            "receiver_thread_ids": sorted(child_ids),
            "child_parent_relation": (
                "OBSERVED"
                if any(item.get("senderThreadId") == parent_id for item in collab_items)
                else "NOT_ASSESSED"
            ),
            "role_identity": "OBSERVED" if "probe-reviewer" in observed_roles else "NOT_ASSESSED",
            "child_thread_metadata": child_metadata,
            "child_metadata_observability": "OBSERVED" if child_metadata else "NOT_ASSESSED",
            "native_skill_load": "NOT_ASSESSED",
            "implicit_activation": "NOT_ASSESSED",
            "errors": metadata_errors,
        }
    finally:
        stderr = server.close()
        shutil.rmtree(fixture, ignore_errors=True)
        shutil.rmtree(home, ignore_errors=True)
        if stderr:
            # Plugin/MCP warnings are retained as a compact, non-authoritative diagnostic.
            pass


def add_capture_metadata(result: dict[str, Any], repo_root: pathlib.Path) -> dict[str, Any]:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, check=False, capture_output=True, text=True
    ).stdout.strip()
    result["captured_at_utc"] = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()
    result["capture_revision"] = revision or "NOT_ASSESSED"
    result["requested_model"] = MODEL
    result["requested_reasoning_effort"] = REASONING
    result["script"] = "skills/agent-creator/scripts/probe_runtime_agents.py"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("discovery", "role-spawn"), default="role-spawn")
    parser.add_argument("--repo-root", type=pathlib.Path, default=pathlib.Path(__file__).parents[3])
    parser.add_argument("--timeout-seconds", type=int, default=240)
    parser.add_argument("--json-out", type=pathlib.Path)
    args = parser.parse_args()
    result = run_discovery_probe() if args.mode == "discovery" else run_role_spawn_probe(args.timeout_seconds)
    result = add_capture_metadata(result, args.repo_root.resolve())
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        args.json_out.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
