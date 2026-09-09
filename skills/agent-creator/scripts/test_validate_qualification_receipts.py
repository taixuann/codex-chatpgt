import copy
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate_qualification_receipts.py")
SPEC = importlib.util.spec_from_file_location("validate_qualification_receipts", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

RECEIPTS = EXCLUSIONS = EVIDENCE = PROMPTS = NATIVE = DISCOVERY = SCOPE = DEPTH = None


def _sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


class QualificationReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global RECEIPTS, EXCLUSIONS, EVIDENCE, PROMPTS, NATIVE, DISCOVERY, SCOPE, DEPTH
        cls.tempdir = tempfile.TemporaryDirectory()
        root = Path(cls.tempdir.name)
        RECEIPTS, EXCLUSIONS = root / "receipts.jsonl", root / "exclusions.jsonl"
        EVIDENCE, PROMPTS = root / "evidence.jsonl", root / "prompts.jsonl"
        NATIVE, DISCOVERY = root / "native.json", root / "discovery.json"
        SCOPE, DEPTH = root / "scope.json", root / "depth.json"

        prompt_rows = []
        for case in MODULE.CASES:
            for partition in MODULE.PARTITIONS:
                prompt_rows.append({
                    "case": case,
                    "partition": partition,
                    "prompt_id": f"{case}-{partition}",
                    "prompt_sha256": _sha(f"{case}:{partition}"),
                })
        PROMPTS.write_text("\n".join(json.dumps(row) for row in prompt_rows) + "\n")

        empty_manifest = []
        empty_digest = MODULE.state_manifest_digest(empty_manifest)
        records = []
        for case in MODULE.CASES:
            for run in range(1, 11):
                partition = MODULE.PARTITIONS[(run - 1) % 5]
                prompt = next(row for row in prompt_rows if row["case"] == case and row["partition"] == partition)
                if case == "HR-01":
                    commands = [{
                        "command": "sed -n '1,80p' .agents/skills/agent-creator/SKILL.md; cmp <(grep -vE x .codex/agents/reviewer.toml) .codex/agents/sibling-reviewer.toml",
                        "exit_code": 0,
                        "output": (
                            "name: agent-creator\nname = \"fixture-reviewer\"\n"
                            "name = \"sibling-reviewer\"\nsandbox_mode = \"read-only\"\n"
                            "sandbox_mode = \"read-only\"\ndeveloper_instructions\n"
                        ),
                    }]
                    evidence = {
                        "skill_read": True, "role_files_read": True,
                        "collision_fixture_observed": True, "no_mutation": True,
                        "state_before_sha256": empty_digest, "state_after_sha256": empty_digest,
                        "state_before_manifest": empty_manifest, "state_after_manifest": empty_manifest,
                    }
                    result, marker, artifact_content = "OBSERVED", None, None
                elif case == "HR-02":
                    commands = [{
                        "command": "scripts/validate_result.py result.json",
                        "exit_code": 0,
                        "output": '# Required fixture value blue-17 {"source": "references/required.md"}\nVALID\n',
                    }]
                    artifact_content = "{}\n"
                    evidence = {"reference_read": True, "script_run": True, "artifact_present": True, "artifact_valid": True}
                    result, marker = "VALID", None
                else:
                    commands = []
                    evidence = {"skill_read": False, "reviewer_role_read": False, "probe_denied": False, "marker_absent": True}
                    result, marker, artifact_content = "NOT_ASSESSED", "absent", None
                source = {
                    "prompt_id": prompt["prompt_id"], "prompt_sha256": prompt["prompt_sha256"],
                    "commands": commands, "marker": marker,
                    "trace_events": {"completed_commands": len(commands), "agent_messages": 0, "sandbox_violation": False},
                    "evidence": evidence,
                }
                if artifact_content is not None:
                    source["artifact_content"] = artifact_content
                trace = MODULE.source_evidence_digest(source)
                record = {
                    "case": case, "run": run, "prompt_partition": partition,
                    "prompt_id": prompt["prompt_id"], "prompt_sha256": prompt["prompt_sha256"],
                    "model": MODULE.MODEL, "reasoning": MODULE.REASONING, "codex_cli": MODULE.CLI,
                    "prompt_transport": "stdin", "capture_revision": MODULE.git_revision(SCRIPT.parents[3]),
                    "exit_code": 0, "result": result, "trace_sha256": trace,
                    "artifact_sha256": _sha(artifact_content) if artifact_content is not None else None,
                    "artifact_path": f"fixture-{run}/result.json" if artifact_content is not None else None,
                    "marker": marker, "trace_events": source["trace_events"], "evidence": evidence,
                    "source_evidence": source,
                }
                record["evidence_binding_sha256"] = MODULE.evidence_binding(record)
                records.append(record)
        RECEIPTS.write_text("\n".join(json.dumps(row, sort_keys=True) for row in records) + "\n")
        EVIDENCE.write_text("\n".join(json.dumps({key: row[key] for key in (
            "case", "run", "trace_sha256", "artifact_sha256", "artifact_path", "prompt_id",
            "prompt_sha256", "evidence_binding_sha256", "source_evidence"
        )}, sort_keys=True) for row in records) + "\n")
        EXCLUSIONS.write_text("\n".join(json.dumps({
            "case": "HR-01", "attempt": attempt, "accepted": False,
            "category": "PROCESS_FAILURE", "trace_sha256": "0" * 64,
            "reason": "synthetic excluded attempt", "source_path": f"external/attempt-{attempt}.jsonl",
        }) for attempt in range(1, 10)) + "\n")

        native = {
            "capture_revision": MODULE.git_revision(SCRIPT.parents[3]),
            "captured_at_utc": "2026-01-01T00:00:00+00:00", "fixture": "synthetic_only",
            "runtime": "Codex Desktop/0.149.1", "script": "skills/agent-creator/scripts/probe_runtime_agents.py",
            "script_sha256": MODULE.sha256(SCRIPT.parent / "probe_runtime_agents.py"),
            "requested_model": MODULE.MODEL, "requested_reasoning_effort": MODULE.REASONING,
            "model": MODULE.MODEL, "collab_spawn_event": "OBSERVED", "child_parent_relation": "OBSERVED",
            "role_identity": "OBSERVED", "return_completion": "OBSERVED", "native_skill_load": "NOT_ASSESSED",
            "implicit_activation": "NOT_ASSESSED", "child_thread_metadata": [{"agentRole": "probe-reviewer"}],
            "qualification_status": "PASS", "reason": "synthetic test receipt",
        }
        NATIVE.write_text(json.dumps(native))
        DISCOVERY.write_text(json.dumps({
            "capture_revision": native["capture_revision"], "script": native["script"],
            "script_sha256": native["script_sha256"], "skill_name": "agent-creator",
            "runtime": native["runtime"], "activation_status": "NOT_ASSESSED",
        }))
        SCOPE.write_text(json.dumps({
            "capture_revision": native["capture_revision"], "captured_at_utc": native["captured_at_utc"],
            "fixture": native["fixture"], "runtime": native["runtime"], "script": native["script"],
            "script_sha256": native["script_sha256"], "requested_model": MODULE.MODEL,
            "requested_reasoning_effort": MODULE.REASONING, "scope_status": "NOT_ASSESSED",
            "reason": "synthetic test receipt", "scope_results": {
                "user": {"role_name": "probe-reviewer", "role_identity": "NOT_ASSESSED",
                          "collab_spawn_event": "NOT_ASSESSED", "child_parent_relation": "NOT_ASSESSED",
                          "child_thread_metadata": []},
                "project": {"role_name": "probe-reviewer", "role_identity": "NOT_ASSESSED",
                             "collab_spawn_event": "NOT_ASSESSED", "child_parent_relation": "NOT_ASSESSED",
                             "child_thread_metadata": []},
            },
        }))
        DEPTH.write_text(json.dumps({
            "capture_revision": native["capture_revision"], "captured_at_utc": native["captured_at_utc"],
            "fixture": native["fixture"], "runtime": native["runtime"], "script": native["script"],
            "script_sha256": native["script_sha256"], "requested_model": MODULE.MODEL,
            "requested_reasoning_effort": MODULE.REASONING, "requested_config": {"agents": {"max_depth": 1}},
            "parent_child_spawn": "NOT_ASSESSED", "child_metadata": [], "native_events_observed": "OBSERVED",
            "nested_depth_status": "NOT_ASSESSED", "reason": "synthetic test receipt",
        }))

        original_validate, original_load = MODULE.validate, MODULE.load_evidence
        MODULE.validate = lambda records, expected_capture_revision=None, evidence_path=None, prompt_path=None: original_validate(
            records, expected_capture_revision, evidence_path or EVIDENCE, prompt_path or PROMPTS
        )
        MODULE.load_evidence = lambda path=None: original_load(path or EVIDENCE)
    def test_current_receipts_derive_all_lanes(self):
        records = MODULE.load_records(RECEIPTS)
        self.assertEqual(MODULE.validate(records), {"HR-01": 10, "HR-02": 10, "HR-03": 10})

    def test_stale_capture_revision_is_rejected(self):
        records = MODULE.load_records(RECEIPTS)
        with self.assertRaises(ValueError):
            MODULE.validate(records, "0" * 40)

    def test_invalid_artifact_result_is_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-02")
        target["evidence"]["artifact_valid"] = False
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_invalid_process_result_is_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-03")
        target["marker"] = "present"
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_exclusion_ledger_is_validated(self):
        self.assertEqual(MODULE.validate_exclusions(EXCLUSIONS), 9)

    def test_unclassified_sandbox_violation_is_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-03")
        target["trace_events"]["sandbox_violation"] = True
        target["evidence"].pop("sandbox_disposition", None)
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_prompt_constraint_does_not_prove_hr03_behavior(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-03" and record["run"] == 8)
        self.assertEqual(target["result"], "NOT_ASSESSED")
        self.assertFalse(target["evidence"]["probe_denied"])
        self.assertEqual(MODULE.validate(tampered)["HR-03"], 10)

    def test_shared_artifact_path_is_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-02" and record["run"] == 2)
        target["artifact_path"] = "fixture-1/result.json"
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_model_prose_does_not_prove_hr01_no_mutation(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-01")
        target["evidence"]["state_after_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_hr01_requires_deterministic_collision_proof(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-01")
        target["evidence"]["collision_fixture_observed"] = False
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_hr01_requires_recomputable_state_manifests(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-01")
        target["evidence"].pop("state_before_manifest")
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_durable_command_tampering_is_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-01")
        target["source_evidence"]["commands"] = []
        target["trace_sha256"] = MODULE.source_evidence_digest(target["source_evidence"])
        target["evidence_binding_sha256"] = MODULE.evidence_binding(target)
        durable = MODULE.load_evidence()
        row = durable[("HR-01", target["run"])]
        row["source_evidence"] = target["source_evidence"]
        row["trace_sha256"] = target["trace_sha256"]
        row["evidence_binding_sha256"] = target["evidence_binding_sha256"]
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl") as handle:
            handle.write("\n".join(json.dumps(value, sort_keys=True) for value in durable.values()) + "\n")
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate(tampered, evidence_path=Path(handle.name))

    def test_forged_hash_shaped_receipt_is_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-02")
        target["trace_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_forged_hash_and_durable_mirror_are_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-01")
        target["trace_sha256"] = "0" * 64
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".jsonl") as handle:
            durable = MODULE.load_evidence()
            rows = []
            for key, row in durable.items():
                row = copy.deepcopy(row)
                if key == ("HR-01", target["run"]):
                    row["trace_sha256"] = "0" * 64
                rows.append(row)
            handle.write("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n")
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate(tampered, evidence_path=Path(handle.name))

    def test_unbound_prompt_hash_is_rejected(self):
        tampered = copy.deepcopy(MODULE.load_records(RECEIPTS))
        target = next(record for record in tampered if record["case"] == "HR-03")
        target["prompt_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

    def test_native_receipt_rejects_non_ancestor_capture(self):
        native = json.loads(NATIVE.read_text())
        native["capture_revision"] = "0" * 40
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as handle:
            json.dump(native, handle)
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_native_receipt(Path(handle.name), SCRIPT.parents[3])

    def test_native_receipt_rejects_probe_script_change_after_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            probe = repo / "skills/agent-creator/scripts/probe_runtime_agents.py"
            probe.parent.mkdir(parents=True)
            probe.write_text("baseline\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-q", "-m", "base"],
                cwd=repo,
                check=True,
            )
            capture = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            probe.write_text("changed\n")
            native = {
                "capture_revision": capture,
                "captured_at_utc": "2026-01-01T00:00:00+00:00",
                "fixture": "synthetic_only",
                "runtime": "Codex Desktop/0.149.1",
                "script": "skills/agent-creator/scripts/probe_runtime_agents.py",
                "script_sha256": "0" * 64,
                "requested_model": MODULE.MODEL,
                "requested_reasoning_effort": MODULE.REASONING,
                "model": MODULE.MODEL,
                "collab_spawn_event": "OBSERVED",
                "child_parent_relation": "OBSERVED",
                "role_identity": "OBSERVED",
                "return_completion": "OBSERVED",
                "native_skill_load": "NOT_ASSESSED",
                "implicit_activation": "NOT_ASSESSED",
                "child_thread_metadata": [{"agentRole": "probe-reviewer"}],
                "qualification_status": "PASS",
                "reason": "synthetic test receipt",
            }
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as handle:
                json.dump(native, handle)
                handle.flush()
                with self.assertRaises(ValueError):
                    MODULE.validate_native_receipt(Path(handle.name), repo)

    def test_native_receipt_rejects_missing_required_evidence(self):
        native = json.loads(NATIVE.read_text())
        native.pop("child_parent_relation")
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as handle:
            json.dump(native, handle)
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_native_receipt(Path(handle.name), SCRIPT.parents[3])

    def test_native_receipt_rejects_mixed_nested_probe_capture(self):
        native = json.loads(NATIVE.read_text())
        native["no_delegation_probes"] = [{"capture_revision": native["capture_revision"]}]
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as handle:
            json.dump(native, handle)
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_native_receipt(Path(handle.name), SCRIPT.parents[3])

    def test_native_receipt_rejects_effective_model_mismatch(self):
        native = json.loads(NATIVE.read_text())
        native["qualification_status"] = "PASS"
        native["model"] = "wrong-model"
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as handle:
            json.dump(native, handle)
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_native_receipt(Path(handle.name), SCRIPT.parents[3])

    def test_discovery_receipt_rejects_stale_script_hash(self):
        discovery = json.loads(DISCOVERY.read_text())
        discovery["script_sha256"] = "0" * 64
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as handle:
            json.dump(discovery, handle)
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_discovery_receipt(Path(handle.name), SCRIPT.parents[3])

    def test_scope_receipt_requires_both_scopes(self):
        scope = json.loads(SCOPE.read_text())
        scope["script"] = "skills/agent-creator/scripts/probe_runtime_agents.py"
        scope["script_sha256"] = MODULE.sha256(SCRIPT.parent / "probe_runtime_agents.py")
        scope["scope_results"] = {
            name: {
                "role_name": value["role_name"],
                "role_identity": value["role_identity"],
                "collab_spawn_event": "NOT_ASSESSED",
                "child_parent_relation": value["child_parent_relation"],
                "child_thread_metadata": [],
            }
            for name, value in scope["scope_results"].items()
        }
        scope["scope_results"].pop("project")
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as handle:
            json.dump(scope, handle)
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_scope_receipt(Path(handle.name), SCRIPT.parents[3])

    def test_depth_receipt_preserves_unassessed_nested_limit(self):
        depth = json.loads(DEPTH.read_text())
        depth["nested_depth_status"] = "PASS"
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as handle:
            json.dump(depth, handle)
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_depth_receipt(Path(handle.name), SCRIPT.parents[3])


if __name__ == "__main__":
    unittest.main()
