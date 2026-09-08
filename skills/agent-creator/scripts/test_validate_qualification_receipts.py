import copy
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

RECEIPTS = SCRIPT.parent.parent / "references" / "qualification-receipts.jsonl"
EXCLUSIONS = SCRIPT.parent.parent / "references" / "qualification-exclusions.jsonl"


class QualificationReceiptTests(unittest.TestCase):
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
        target = next(record for record in tampered if record["case"] == "HR-03")
        target["evidence"]["probe_denied"] = False
        target["evidence"]["delegation_constraint_read"] = True
        with self.assertRaises(ValueError):
            MODULE.validate(tampered)

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
        native = json.loads((SCRIPT.parent.parent / "references" / "qualification-native-runtime.json").read_text())
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
            }
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as handle:
                json.dump(native, handle)
                handle.flush()
                with self.assertRaises(ValueError):
                    MODULE.validate_native_receipt(Path(handle.name), repo)

    def test_native_receipt_rejects_missing_required_evidence(self):
        native = json.loads((SCRIPT.parent.parent / "references" / "qualification-native-runtime.json").read_text())
        native.pop("child_parent_relation")
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as handle:
            json.dump(native, handle)
            handle.flush()
            with self.assertRaises(ValueError):
                MODULE.validate_native_receipt(Path(handle.name), SCRIPT.parents[3])


if __name__ == "__main__":
    unittest.main()
