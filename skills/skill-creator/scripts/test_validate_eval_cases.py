import importlib.util
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("validate_eval_cases.py")
INITIALIZER = Path(__file__).with_name("init_skill.py")


def load_module():
    spec = importlib.util.spec_from_file_location("validate_eval_cases", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_initializer():
    script_dir = str(INITIALIZER.parent)
    sys.path.insert(0, script_dir)
    try:
        spec = importlib.util.spec_from_file_location("init_skill", INITIALIZER)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(script_dir)


class EvalContractTests(unittest.TestCase):
    def test_ignored_skill_content_invalidates_candidate_binding(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = root / "skills" / "skill-creator"
            skill.mkdir(parents=True)
            (root / ".gitignore").write_text("**/*token*\n**/*.pyc\n**/__pycache__/\n**/.codex-home/\n", encoding="utf-8")
            (skill / "SKILL.md").write_text("candidate\n", encoding="utf-8")
            subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
            subprocess.run(["git", "add", ".gitignore", "skills/skill-creator/SKILL.md"], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--quiet", "-m", "candidate"], cwd=root, check=True)
            candidate = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            ignored = skill / "private-token.txt"
            ignored.write_text("untracked candidate input\n", encoding="utf-8")

            self.assertIn("\0content/private-token.txt", module._snapshot(skill))
            self.assertFalse(module._candidate_worktree_matches(skill, candidate))

            ignored.unlink()
            cache_files = [
                skill / "__pycache__" / "compiled.pyc",
                skill / ".codex-home" / "runtime.json",
                skill / "module.pyc",
            ]
            for cache_file in cache_files:
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                cache_file.write_text("runtime cache\n", encoding="utf-8")
                self.assertEqual(
                    subprocess.run(
                        ["git", "check-ignore", "--quiet", str(cache_file.relative_to(root))],
                        cwd=root,
                        check=False,
                    ).returncode,
                    0,
                )
            snapshot = module._snapshot(skill)
            for relative in (
                "__pycache__/compiled.pyc",
                ".codex-home/runtime.json",
                "module.pyc",
            ):
                self.assertNotIn(f"\0content/{relative}", snapshot)
            self.assertTrue(module._candidate_worktree_matches(skill, candidate))

    def test_install_is_a_behavioral_case_kind_with_canonical_cases(self):
        module = load_module()
        self.assertIn("INSTALL", module.KINDS)
        cases = module.load_cases(SCRIPT.parents[1] / "evals" / "cases.yaml")["cases"]
        install_cases = {case["id"]: case for case in cases if case["kind"] == "INSTALL"}
        self.assertEqual(set(install_cases), {
            "install-healthy-copy",
            "install-collision-refused",
            "install-redesign-routed",
            "install-zero-adaptation",
            "install-owned-lifecycle",
        })
        self.assertEqual(install_cases["install-healthy-copy"]["installation_outcome"], "INSTALLED")
        self.assertEqual(install_cases["install-collision-refused"]["installation_outcome"], "BLOCKED")
        self.assertEqual(install_cases["install-redesign-routed"]["installation_outcome"], "ROUTE")

    def test_case_filter_does_not_select_unrequested_action_probes(self):
        module = load_module()
        data = module.load_cases(SCRIPT.parents[1] / "evals" / "cases.yaml")
        self.assertEqual(module._selected_action_cases(data, "full", {"install-healthy-copy"}), [])
        selected = module._selected_action_cases(data, "full", {"explicit-install"})
        self.assertEqual([case["id"] for case in selected], ["explicit-install"])
        self.assertEqual(module._selected_action_cases(data, "smoke", None), [])

    def test_lifecycle_stage_includes_the_owned_install_trial(self):
        module = load_module()
        data = module.load_cases(SCRIPT.parents[1] / "evals" / "cases.yaml")
        selected = module._cases_for_stage(data, "lifecycle", {"install-owned-lifecycle"})
        self.assertEqual([case["id"] for case in selected], ["install-owned-lifecycle"])

    def test_install_receipt_requires_source_payload_runtime_validation_and_ownership(self):
        module = load_module()
        case = {"kind": "INSTALL", "installation_outcome": "INSTALLED"}
        digest = "a" * 64
        report = {"installation": {
            "status": "INSTALLED",
            "workspace_changed": True,
            "source": {"repository": "owner/skill", "requested_ref": "v1.0", "revision": "1" * 40, "path": "skill", "license": "MIT"},
            "target": {"runtime": "codex", "scope": "project", "path": ".agents/skills/skill", "mode": "copy"},
            "payload": {"source_sha256": digest, "selected_sha256": digest, "installed_sha256": digest, "adaptation": "none", "files": [{"path": "SKILL.md", "source_sha256": digest, "installed_sha256": digest}]},
            "backend": {"identity": "Agentport", "version": "0.2.0", "state_identity": "state-001", "native_revision": "2" * 40},
            "audit": {"status": "PASS", "backend": "skills-lint 1.0"},
            "validation": {"status": "PASS"},
            "real_task": {"status": "PASS"},
            "ownership": {"receipt_id": "install-001", "update_behavior": "same revision is a no-op; changed revision is explicit reinstall", "uninstall": "remove only receipt-owned unchanged files"},
        }}
        self.assertTrue(module._install_evidence_ok(case, report)[0])
        for invalid_revision in ("x", "unknown"):
            report["installation"]["backend"]["native_revision"] = invalid_revision
            self.assertFalse(module._install_evidence_ok(case, report)[0])
        report["installation"]["backend"]["native_revision"] = "2" * 40
        report["installation"]["payload"]["installed_sha256"] = "b" * 64
        self.assertFalse(module._install_evidence_ok(case, report)[0])

    def test_install_receipt_requires_backend_and_composite_provenance_when_backend_revision_is_null(self):
        module = load_module()
        source_hash = hashlib.sha256(b"skill").hexdigest()
        manifest_hash = hashlib.sha256(b"manifest").hexdigest()
        case = {
            "id": "install-healthy-copy", "kind": "INSTALL", "installation_outcome": "INSTALLED",
            "source_fixture": ".fixture-sources/healthy", "package_files": ["SKILL.md"],
            "source_repository": "owner/skill", "source_ref": "v1", "source_license": "MIT",
            "_resolved_revision": "1" * 40, "_resolved_license": "MIT",
            "side_effects": [{"path": ".agents/skills/skill/SKILL.md"}, {"path": ".agents/.skill-installs/skill.json"}],
        }
        before = {".fixture-sources/healthy/SKILL.md": "skill", "\0content/.fixture-sources/healthy/SKILL.md": source_hash}
        after = {
            **before,
            ".agents/skills/skill/SKILL.md": "skill", "\0content/.agents/skills/skill/SKILL.md": source_hash,
            ".agents/.skill-installs/skill.json": "manifest", "\0content/.agents/.skill-installs/skill.json": manifest_hash,
        }
        digest = module._content_tree_sha256(before, ".fixture-sources/healthy", ["SKILL.md"])
        report = {"installation": {
            "status": "INSTALLED", "workspace_changed": True,
            "source": {"repository": "owner/skill", "requested_ref": "v1", "revision": "1" * 40, "path": ".fixture-sources/healthy", "license": "MIT"},
            "target": {"runtime": "codex", "scope": "project", "path": ".agents/skills/skill", "mode": "copy"},
            "payload": {"source_sha256": digest, "selected_sha256": digest, "installed_sha256": digest, "adaptation": "none", "files": [{"path": "SKILL.md", "source_sha256": source_hash, "installed_sha256": source_hash}]},
            "backend": {"identity": "Agentport", "version": "0.2.0", "state_identity": manifest_hash, "native_revision": None},
            "composite_provenance": {"verified": True, "source_revision": "1" * 40, "selected_sha256": digest, "installed_sha256": digest},
            "audit": {"status": "PASS", "backend": "skills-lint 1.0"}, "validation": {"status": "PASS"},
            "real_task": {"status": "PASS"},
            "ownership": {"receipt_id": "receipt", "update_behavior": "same revision is no-op; changed revision is explicit reinstall", "uninstall": "remove receipt-owned unchanged files"},
        }}
        self.assertTrue(module._install_evidence_ok(case, report, before, after)[0])
        report["installation"].pop("composite_provenance")
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])
        report["installation"]["composite_provenance"] = {"verified": True, "source_revision": "2" * 40, "selected_sha256": digest, "installed_sha256": digest}
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])
        report["installation"]["composite_provenance"]["source_revision"] = "1" * 40
        report["installation"]["backend"].pop("state_identity")
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])

    def test_owned_lifecycle_report_is_not_independent_transition_evidence(self):
        module = load_module()
        case = {"id": "install-owned-lifecycle", "kind": "INSTALL", "installation_outcome": "INSTALLED"}
        digest = "a" * 64
        report = {"installation": {
            "status": "INSTALLED", "workspace_changed": True,
            "source": {"repository": "owner/skill", "requested_ref": "v1", "revision": "1" * 40, "path": "skill", "license": "MIT"},
            "target": {"runtime": "codex", "scope": "project", "path": ".agents/skills/skill", "mode": "copy"},
            "payload": {"source_sha256": digest, "selected_sha256": digest, "installed_sha256": digest, "adaptation": "none", "files": [{"path": "SKILL.md", "source_sha256": digest, "installed_sha256": digest}]},
            "backend": {"identity": "Agentport", "version": "0.2.0", "state_identity": "state-001", "native_revision": "2" * 40},
            "audit": {"status": "PASS", "backend": "skills-lint 1.0"}, "validation": {"status": "PASS"},
            "real_task": {"status": "PASS"},
            "ownership": {"receipt_id": "receipt", "update_behavior": "same revision is no-op; changed revision is explicit reinstall", "uninstall": "remove receipt-owned unchanged files"},
            "owned_lifecycle": {
                "trial_id": str(uuid.uuid4()), "source_revision": "1" * 40, "selected_sha256": digest, "receipt_id": "receipt",
                "locally_modified_paths": ["SKILL.md"],
                "neighbor_path": ".fixture-data/neighbor-canary.txt",
                "steps": {key: "PASS" for key in ("initial_install", "same_revision", "changed_revision", "local_edit_preserved", "safe_uninstall", "neighbor_preserved")},
                "neighbor_hash": "b" * 64,
                "snapshots": {
                    "after_install": {"owned_files": {"SKILL.md": digest}},
                    "after_same_revision": {"owned_files": {"SKILL.md": digest}},
                    "after_changed_revision": {"source_revision": "2" * 40, "owned_files": {"SKILL.md": "c" * 64}},
                    "after_local_edit": {"owned_files": {"SKILL.md": "d" * 64}},
                    "after_uninstall": {"owned_files": {}, "preserved_modified_files": {"SKILL.md": "d" * 64}, "neighbor_hash": "b" * 64},
                    "after_final_reinstall": {"source_revision": "1" * 40, "owned_files": {"SKILL.md": digest}},
                },
                "terminal_state": "CLEANED",
            },
        }}
        observed, reason = module._install_evidence_ok(case, report)
        self.assertFalse(observed)
        self.assertIn("NOT_ASSESSED", reason)
        self.assertIn("runner-owned intermediate state snapshots", reason)

    def test_runner_owned_lifecycle_snapshots_are_checked_at_every_transition(self):
        module = load_module()
        case = {
            "id": "install-owned-lifecycle", "kind": "INSTALL", "installation_outcome": "INSTALLED",
            "source_fixture": ".fixture-sources/healthy", "package_files": ["SKILL.md", "references/guide.md"],
            "side_effects": [
                {"path": ".agents/skills/healthy/SKILL.md"},
                {"path": ".agents/skills/healthy/references/guide.md"},
                {"path": ".agents/.skill-installs/healthy.json"},
            ],
        }
        prefix = module.SNAPSHOT_CONTENT_PREFIX
        paths = case["package_files"]
        old, new, edited = "a" * 64, "b" * 64, "c" * 64
        neighbor = hashlib.sha256(b"unowned neighbor canary\n").hexdigest()

        def state(source_hash, target_hash, manifest_hash, edited_hash=None):
            result = {
                f"{prefix}.fixture-data/neighbor-canary.txt": neighbor,
                f"{prefix}.agents/.skill-installs/healthy.json": manifest_hash,
                f"{prefix}.agents/.skill-installs/unrelated.json": "d" * 64,
            }
            for path in paths:
                result[f"{prefix}.fixture-sources/healthy/{path}"] = source_hash
                result[f"{prefix}.agents/skills/healthy/{path}"] = edited_hash if path == "SKILL.md" and edited_hash else target_hash
            return result

        initial = state(old, old, "1" * 64)
        changed = state(new, new, "2" * 64)
        edited_state = state(new, new, "2" * 64, edited)
        refused = dict(edited_state)
        uninstalled = state(new, new, "2" * 64, edited)
        uninstalled.pop(f"{prefix}.agents/.skill-installs/healthy.json")
        uninstalled.pop(f"{prefix}.agents/skills/healthy/references/guide.md")
        clean = dict(uninstalled)
        clean.pop(f"{prefix}.agents/skills/healthy/SKILL.md")
        evidence = {
            "source_revisions": ["1" * 40, "2" * 40], "edited_path": "SKILL.md",
            "source_revision_hashes": {
                "1" * 40: {path: old for path in paths},
                "2" * 40: {path: new for path in paths},
            },
            "stage_reports": {
                "after_same_revision": {"operation": "install", "status": "NO_OP", "backend": "fixture-backend", "source_revision": "1" * 40, "target": ".agents/skills/healthy", "state_identity": "1" * 64},
                "after_changed_revision": {"operation": "update", "status": "UPDATED", "backend": "fixture-backend", "source_revision": "2" * 40, "target": ".agents/skills/healthy", "state_identity": "2" * 64},
                "after_reinstall_with_local_edit": {"operation": "install", "status": "REFUSED", "backend": "fixture-backend", "source_revision": "2" * 40, "target": ".agents/skills/healthy", "state_identity": "2" * 64},
                "after_uninstall": {"operation": "uninstall", "status": "UNINSTALLED", "backend": "fixture-backend", "source_revision": "2" * 40, "target": ".agents/skills/healthy", "state_identity": None},
                "after_final_reinstall": {"operation": "install", "status": "INSTALLED", "backend": "fixture-backend", "source_revision": "2" * 40, "target": ".agents/skills/healthy", "state_identity": "3" * 64},
            },
            "snapshots": dict(zip(module.LIFECYCLE_SNAPSHOT_STAGES, (
                initial, dict(initial), changed, edited_state, refused,
                uninstalled, clean, state(new, new, "3" * 64),
            ))),
        }
        self.assertFalse(module._owned_lifecycle_snapshots_ok(case, None))
        self.assertTrue(module._owned_lifecycle_snapshots_ok(case, evidence))
        self.assertTrue(module._lifecycle_stage_reports_ok(case, evidence, "fixture-backend", evidence["source_revisions"]))
        for extra in (
            f"{module.SNAPSHOT_DIR_PREFIX}.agents/skills/healthy/unexpected",
            ".agents/skills/healthy/unexpected-link",
        ):
            evidence["snapshots"]["after_changed_revision"][extra] = "e" * 64
            self.assertFalse(module._owned_lifecycle_snapshots_ok(case, evidence), extra)
            evidence["snapshots"]["after_changed_revision"].pop(extra)
        evidence["snapshots"]["after_changed_revision"][f"{prefix}.agents/.skill-installs/unrelated.json"] = "e" * 64
        self.assertFalse(module._owned_lifecycle_snapshots_ok(case, evidence))
        evidence["snapshots"]["after_changed_revision"][f"{prefix}.agents/.skill-installs/unrelated.json"] = "d" * 64
        evidence["snapshots"]["after_changed_revision"][f"{prefix}.fixture-sources/healthy/SKILL.md"] = "f" * 64
        self.assertFalse(module._owned_lifecycle_snapshots_ok(case, evidence))
        evidence["snapshots"]["after_changed_revision"][f"{prefix}.fixture-sources/healthy/SKILL.md"] = new
        evidence["stage_reports"]["after_changed_revision"]["source_revision"] = "1" * 40
        self.assertFalse(module._lifecycle_stage_reports_ok(case, evidence, "fixture-backend", evidence["source_revisions"]))
        evidence["stage_reports"]["after_changed_revision"]["source_revision"] = "2" * 40
        evidence["snapshots"]["after_uninstall"].pop(f"{prefix}.agents/skills/healthy/SKILL.md")
        self.assertFalse(module._owned_lifecycle_snapshots_ok(case, evidence))

    def test_lifecycle_recomputation_requires_each_successful_observed_process(self):
        module = load_module()
        evidence = {"processes": [
            {"stage": stage, "returncode": 0, "process_observed": True}
            for stage in module.LIFECYCLE_PROCESS_STAGES
        ]}
        self.assertTrue(module._lifecycle_processes_ok(evidence))
        evidence["processes"][2]["process_observed"] = False
        self.assertFalse(module._lifecycle_processes_ok(evidence))
        evidence["processes"].pop()
        self.assertFalse(module._lifecycle_processes_ok(evidence))

    def test_runner_refuses_local_edit_through_a_fixture_symlink(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = root / "fixture"
            fixture.mkdir()
            outside = root / "outside.txt"
            outside.write_text("preserve", encoding="utf-8")
            link = fixture / "target.txt"
            link.symlink_to(outside)
            self.assertFalse(module._confined_regular_file(fixture, link))
            regular = fixture / "owned.txt"
            regular.write_text("owned", encoding="utf-8")
            self.assertTrue(module._confined_regular_file(fixture, regular))

    def test_owned_lifecycle_runner_refuses_edit_then_reinstalls_clean_target(self):
        module = load_module()
        cases_path = SCRIPT.parents[1] / "evals" / "cases.yaml"
        case = next(item for item in module.load_cases(cases_path)["cases"] if item["id"] == "install-owned-lifecycle")
        skill_dir = SCRIPT.parents[1]
        real_run = subprocess.run
        calls = []

        def install_payload(root, revision):
            source = root / case["source_fixture"]
            target = root / ".agents" / "skills" / "healthy"
            for relative in case["package_files"]:
                destination = target / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((source / relative).read_bytes())
            manifest = root / ".agents" / ".skill-installs" / "healthy.json"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(revision, encoding="utf-8")
            return manifest

        def fake_run(command, **kwargs):
            if command[0] != "fake-codex":
                return real_run(command, **kwargs)
            calls.append(command)
            root = Path(command[command.index("--cd") + 1])
            prompt = command[-1]
            if "initial installation" in prompt:
                source = root / case["source_fixture"]
                source_before = module._snapshot(root)
                manifest = install_payload(root, "receipt-v1")
                artifact = root / case["artifact_path"]
                artifact.parent.mkdir(parents=True, exist_ok=True)
                artifact.write_text("{}\n", encoding="utf-8")
                target_prefix = ".agents/skills/healthy"
                source_hashes = {path: source_before[f"{module.SNAPSHOT_CONTENT_PREFIX}{case['source_fixture']}/{path}"] for path in case["package_files"]}
                installed_snapshot = module._snapshot(root)
                installed_hashes = {path: installed_snapshot[f"{module.SNAPSHOT_CONTENT_PREFIX}{target_prefix}/{path}"] for path in case["package_files"]}
                selected = module._content_tree_sha256(source_before, case["source_fixture"], case["package_files"])
                report = {"disposition": "INSTALL_EXISTING", "installation": {
                    "status": "INSTALLED", "workspace_changed": True,
                    "source": {"repository": "fixture/healthy", "requested_ref": "fixture-v1", "revision": case["_resolved_revision"], "path": case["source_fixture"], "license": "MIT"},
                    "target": {"runtime": "codex", "scope": "project", "path": target_prefix, "mode": "copy"},
                    "payload": {"source_sha256": module._content_tree_sha256(source_before, case["source_fixture"]), "selected_sha256": selected, "installed_sha256": module._content_tree_sha256(installed_snapshot, target_prefix, case["package_files"]), "adaptation": "none", "files": [{"path": path, "source_sha256": source_hashes[path], "installed_sha256": installed_hashes[path]} for path in case["package_files"]]},
                    "backend": {"identity": "fixture-backend", "version": "1", "state_identity": hashlib.sha256(manifest.read_bytes()).hexdigest(), "native_revision": "2" * 40},
                    "audit": {"status": "PASS", "backend": "fixture-lint"}, "validation": {"status": "PASS"}, "real_task": {"status": "PASS"},
                    "ownership": {"receipt_id": "receipt-1", "update_behavior": "same revision is a no-op; changed revision updates explicitly", "uninstall": "remove only unchanged receipt-owned files"},
                }}
                message = json.dumps(report)
            elif "same immutable ref" in prompt:
                identity = hashlib.sha256((root / ".agents/.skill-installs/healthy.json").read_bytes()).hexdigest()
                message = json.dumps({"operation": "install", "status": "NO_OP", "backend": "fixture-backend", "target": ".agents/skills/healthy", "source_revision": case["_resolved_revision"], "state_identity": identity})
            elif "whose immutable commit" in prompt:
                manifest = install_payload(root, "receipt-v2")
                message = json.dumps({"operation": "update", "status": "UPDATED", "backend": "fixture-backend", "target": ".agents/skills/healthy", "source_revision": module._git_revision(root / case["source_fixture"], "fixture-v2"), "state_identity": hashlib.sha256(manifest.read_bytes()).hexdigest()})
            elif "while the user-owned local edit is still present" in prompt:
                identity = hashlib.sha256((root / ".agents/.skill-installs/healthy.json").read_bytes()).hexdigest()
                message = json.dumps({"operation": "install", "status": "REFUSED", "backend": "fixture-backend", "target": ".agents/skills/healthy", "source_revision": module._git_revision(root / case["source_fixture"], "fixture-v2"), "state_identity": identity})
            elif "Safely uninstall" in prompt:
                target = root / ".agents" / "skills" / "healthy"
                (target / "references" / "guide.md").unlink()
                (target / "LICENSE.txt").unlink()
                (root / ".agents" / ".skill-installs" / "healthy.json").unlink()
                message = json.dumps({"operation": "uninstall", "status": "UNINSTALLED", "backend": "fixture-backend", "target": ".agents/skills/healthy", "source_revision": module._git_revision(root / case["source_fixture"], "fixture-v2"), "state_identity": None})
            else:
                manifest = install_payload(root, "receipt-v3")
                message = json.dumps({"operation": "install", "status": "INSTALLED", "backend": "fixture-backend", "target": ".agents/skills/healthy", "source_revision": module._git_revision(root / case["source_fixture"], "fixture-v2"), "state_identity": hashlib.sha256(manifest.read_bytes()).hexdigest()})
            events = [
                {"skill_loads": ["skill-creator"], "item": {"type": "command_execution", "command": "fixture operation"}},
                {"item": {"type": "agent_message", "text": message}},
            ]
            stdout = "\n".join(json.dumps(event) for event in events)
            return subprocess.CompletedProcess(command, 0, stdout, "")

        with module._fixture(skill_dir, True, case) as fixture:
            trial = module._trial_metadata(skill_dir, case, "with_skill")
            with patch.object(module.subprocess, "run", side_effect=fake_run):
                result = module._run_owned_lifecycle(
                    case, "fake-codex", "gpt-6-luna", "max", 30,
                    fixture, fixture, {}, trial, {},
                )
        with module._fixture(skill_dir, True, case) as fixture:
            trial = module._trial_metadata(skill_dir, case, "with_skill")
            with patch.object(module.subprocess, "run", side_effect=fake_run), patch.object(module, "_runtime_activation", return_value=None):
                no_activation = module._run_owned_lifecycle(
                    case, "fake-codex", "gpt-6-luna", "max", 30,
                    fixture, fixture, {}, trial, {},
                )
        self.assertTrue(module._owned_lifecycle_snapshots_ok(case, result["lifecycle_evidence"]), result["lifecycle_evidence"])
        self.assertTrue(module._lifecycle_stage_reports_ok(case, result["lifecycle_evidence"], "fixture-backend", result["lifecycle_evidence"]["source_revisions"]), result["lifecycle_evidence"])
        self.assertEqual(result["lifecycle_evidence"]["source_revisions"][0], result["final_report"]["installation"]["source"]["revision"])
        self.assertEqual(result["status"], "PASS", result.get("reason"))
        self.assertEqual(len(calls), 12)
        self.assertEqual(set(result["lifecycle_evidence"]["snapshots"]), set(module.LIFECYCLE_SNAPSHOT_STAGES))
        self.assertTrue(result["installation_observed"])
        self.assertTrue(result["lifecycle_evidence"]["stage_reports"])
        self.assertTrue(module._recomputed_record(result, case)["installation_observed"])
        incomplete = json.loads(json.dumps(result))
        incomplete["lifecycle_evidence"].pop("processes")
        self.assertFalse(module._recomputed_record(incomplete, case)["installation_observed"])
        self.assertNotEqual(no_activation["status"], "PASS")
        self.assertFalse(no_activation["runtime_observed"])

    def test_install_fixture_ref_resolves_to_a_real_commit_and_package_closure(self):
        module = load_module()
        case = {
            "id": "install-healthy-copy", "source_fixture": ".fixture-sources/healthy",
            "source_ref": "fixture-v1", "source_revision": "d6f5e671b8c7d0a28ef4a32aaa4124d93a9b0b6f",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module._seed_case(root, case)
            source = root / case["source_fixture"]
            self.assertEqual(case["_resolved_revision"], module._git_revision(source, "fixture-v1"))
            self.assertEqual(case["_resolved_revision"], case["source_revision"])
            self.assertRegex(case["_resolved_revision"], r"^[0-9a-f]{40}$")
            self.assertTrue((source / "LICENSE.txt").is_file())
            self.assertEqual(case["_resolved_license"], "MIT")

    def test_snapshot_metadata_cannot_hide_a_real_at_content_path(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "foo").write_text("stable", encoding="utf-8")
            (root / "@content").mkdir()
            (root / "@content" / "foo").write_text("before", encoding="utf-8")
            before = module._snapshot(root)
            (root / "@content" / "foo").write_text("after", encoding="utf-8")
            after = module._snapshot(root)
            self.assertIn("@content/foo", module._changed_paths(before, after))

    def test_install_snapshot_rejects_path_escape_wrong_target_and_changed_payload(self):
        module = load_module()
        case = {
            "id": "install-healthy-copy", "kind": "INSTALL", "installation_outcome": "INSTALLED",
            "source_fixture": ".fixture-sources/healthy", "package_files": ["SKILL.md"],
            "side_effects": [{"path": ".agents/skills/healthy/SKILL.md"}, {"path": ".agents/.skill-installs/healthy.json"}],
            "_resolved_revision": "1" * 40, "_resolved_license": "MIT",
        }
        content_hash = hashlib.sha256(b"source").hexdigest()
        report = {"installation": {
            "status": "INSTALLED", "workspace_changed": True,
            "source": {"repository": "owner/skill", "requested_ref": "v1", "revision": "1" * 40, "path": ".fixture-sources/healthy", "license": "MIT"},
            "target": {"runtime": "codex", "scope": "project", "path": ".agents/skills/healthy", "mode": "copy"},
            "payload": {"source_sha256": "a" * 64, "selected_sha256": "a" * 64, "installed_sha256": "a" * 64, "adaptation": "none",
                "files": [{"path": "SKILL.md", "source_sha256": content_hash, "installed_sha256": content_hash}]},
            "backend": {"identity": "fixture", "version": "1", "state_identity": "fixture-state", "native_revision": "3" * 40},
            "audit": {"status": "PASS", "backend": "fixture"}, "validation": {"status": "PASS"},
            "real_task": {"status": "PASS"}, "ownership": {"receipt_id": "receipt", "update_behavior": "same revision no-op; changed revision reinstall", "uninstall": "remove receipt-owned unchanged file"},
        }}
        before = {
            ".fixture-sources/healthy/SKILL.md": "snapshot:source",
            "\0content/.fixture-sources/healthy/SKILL.md": content_hash,
        }
        after = {
            **before,
            ".agents/skills/healthy/SKILL.md": "snapshot:source",
            "\0content/.agents/skills/healthy/SKILL.md": content_hash,
            ".agents/.skill-installs/healthy.json": "manifest",
            "\0content/.agents/.skill-installs/healthy.json": hashlib.sha256(b"manifest").hexdigest(),
        }
        report["installation"]["backend"]["state_identity"] = after["\0content/.agents/.skill-installs/healthy.json"]
        digest = module._content_tree_sha256(before, ".fixture-sources/healthy", ["SKILL.md"])
        report["installation"]["payload"].update({"source_sha256": digest, "selected_sha256": digest, "installed_sha256": digest})
        ok, reason = module._install_evidence_ok(case, report, before, after)
        self.assertTrue(ok, reason)
        report["installation"]["backend"]["state_identity"] = "unbound-state"
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])
        report["installation"]["backend"]["state_identity"] = after["\0content/.agents/.skill-installs/healthy.json"]
        after[".agents/skills/healthy/SKILL.md"] = "sha256:changed"
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])
        after[".agents/skills/healthy/SKILL.md"] = "sha256:source"
        report["installation"]["target"]["path"] = "../outside"
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])
        report["installation"]["target"]["path"] = ".agents/skills/other"
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])
        report["installation"]["target"]["path"] = ".agents/skills/healthy"
        before[".agents/skills/healthy/unmanaged.txt"] = "canary"
        after[".agents/skills/healthy/unmanaged.txt"] = "canary"
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])

    def test_install_snapshot_rejects_fabricated_payload_digest(self):
        module = load_module()
        case = {
            "id": "install-healthy-copy", "kind": "INSTALL", "installation_outcome": "INSTALLED",
            "source_fixture": ".fixture-sources/healthy", "package_files": ["SKILL.md"],
            "side_effects": [{"path": ".agents/skills/healthy/SKILL.md"}, {"path": ".agents/.skill-installs/healthy.json"}],
            "source_repository": "fixture/healthy", "source_ref": "fixture-v1", "source_license": "MIT",
            "_resolved_revision": "1" * 40, "_resolved_license": "MIT",
        }
        source = "a" * 64
        before = {
            ".fixture-sources/healthy/SKILL.md": "snapshot:source",
            "\0content/.fixture-sources/healthy/SKILL.md": source,
        }
        after = {
            **before,
            ".agents/skills/healthy/SKILL.md": "snapshot:source",
            "\0content/.agents/skills/healthy/SKILL.md": source,
            ".agents/.skill-installs/healthy.json": "manifest",
            "\0content/.agents/.skill-installs/healthy.json": hashlib.sha256(b"manifest").hexdigest(),
        }
        digest = module._content_tree_sha256(before, ".fixture-sources/healthy", ["SKILL.md"])
        report = {"installation": {
            "status": "INSTALLED", "workspace_changed": True,
            "source": {"repository": "fixture/healthy", "requested_ref": "fixture-v1", "revision": "1" * 40, "path": ".fixture-sources/healthy", "license": "MIT"},
            "target": {"runtime": "codex", "scope": "project", "path": ".agents/skills/healthy", "mode": "copy"},
            "payload": {"source_sha256": digest, "selected_sha256": digest, "installed_sha256": digest, "adaptation": "none",
                "files": [{"path": "SKILL.md", "source_sha256": source, "installed_sha256": source}]},
            "backend": {"identity": "fixture", "version": "1", "state_identity": after["\0content/.agents/.skill-installs/healthy.json"], "native_revision": "3" * 40},
            "audit": {"status": "PASS", "backend": "fixture"}, "validation": {"status": "PASS"},
            "real_task": {"status": "PASS"}, "ownership": {"receipt_id": "receipt", "update_behavior": "same revision no-op; changed revision reinstall", "uninstall": "remove receipt-owned unchanged files"},
        }}
        self.assertTrue(module._install_evidence_ok(case, report, before, after)[0])
        case["_resolved_license"] = "GPL-3.0-only"
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])
        case["_resolved_license"] = "MIT"
        report["installation"]["source"]["revision"] = "2" * 40
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])
        report["installation"]["source"]["revision"] = "1" * 40
        report["installation"]["payload"]["selected_sha256"] = "a" * 64
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])

    def test_artifact_contract_allows_only_directories_needed_for_declared_files(self):
        module = load_module()
        case = {"id": "fixture", "kind": "CREATE", "artifact": "created", "artifact_path": ".evaluation/result.json"}
        before = {}
        after = {"\0dir/.evaluation": "dir", ".evaluation/result.json": "report"}
        self.assertTrue(module._artifact_ok(case, before, after)[0])
        after["\0dir/unexpected"] = "dir"
        self.assertFalse(module._artifact_ok(case, before, after)[0])

    def test_no_artifact_contract_rejects_empty_directory_mutation(self):
        module = load_module()
        self.assertFalse(module._artifact_ok(
            {"id": "blocked-install", "kind": "INSTALL", "artifact": "none"},
            {}, {"\0dir/.agents/skills/target": "dir"},
        )[0])

    def test_install_compatibility_adaptation_is_bounded_to_declared_files(self):
        module = load_module()
        case = {
            "id": "install-healthy-copy", "kind": "INSTALL", "installation_outcome": "INSTALLED",
            "source_fixture": ".fixture-sources/healthy", "package_files": ["SKILL.md", "references/guide.md"],
            "side_effects": [{"path": ".agents/skills/healthy/SKILL.md"}, {"path": ".agents/.skill-installs/healthy.json"}],
            "source_repository": "owner/skill", "source_ref": "v1", "source_license": "MIT",
            "_resolved_revision": "1" * 40, "_resolved_license": "MIT",
        }
        source_hash = hashlib.sha256(b"source-skill").hexdigest()
        installed_hash = hashlib.sha256(b"compat-adjusted").hexdigest()
        guide_hash = hashlib.sha256(b"guide").hexdigest()
        before = {
            ".fixture-sources/healthy/SKILL.md": "source-skill",
            ".fixture-sources/healthy/references/guide.md": "guide",
            "\0content/.fixture-sources/healthy/SKILL.md": source_hash,
            "\0content/.fixture-sources/healthy/references/guide.md": guide_hash,
        }
        after = {
            **before,
            ".agents/skills/healthy/SKILL.md": "compat-adjusted",
            ".agents/skills/healthy/references/guide.md": "guide",
            "\0content/.agents/skills/healthy/SKILL.md": installed_hash,
            "\0content/.agents/skills/healthy/references/guide.md": guide_hash,
            ".agents/.skill-installs/healthy.json": "manifest",
            "\0content/.agents/.skill-installs/healthy.json": hashlib.sha256(b"manifest").hexdigest(),
        }
        report = {"installation": {
            "status": "INSTALLED", "workspace_changed": True,
            "source": {"repository": "owner/skill", "requested_ref": "v1", "revision": "1" * 40, "path": ".fixture-sources/healthy", "license": "MIT"},
            "target": {"runtime": "codex", "scope": "project", "path": ".agents/skills/healthy", "mode": "copy"},
            "payload": {"source_sha256": module._content_tree_sha256(before, ".fixture-sources/healthy"),
                "selected_sha256": module._content_tree_sha256(before, ".fixture-sources/healthy", ["SKILL.md", "references/guide.md"]),
                "installed_sha256": module._content_tree_sha256(after, ".agents/skills/healthy", ["SKILL.md", "references/guide.md"]),
                "files": [
                    {"path": "SKILL.md", "source_sha256": source_hash, "installed_sha256": installed_hash},
                    {"path": "references/guide.md", "source_sha256": guide_hash, "installed_sha256": guide_hash},
                ],
                "adaptation": {"reason": "Adjust one documented runtime compatibility token.", "files": [{"path": "SKILL.md", "source_sha256": source_hash, "installed_sha256": installed_hash}]}},
            "backend": {"identity": "fixture", "version": "1", "state_identity": after["\0content/.agents/.skill-installs/healthy.json"], "native_revision": "3" * 40},
            "audit": {"status": "PASS", "backend": "fixture"}, "validation": {"status": "PASS"},
            "real_task": {"status": "PASS"}, "ownership": {"receipt_id": "receipt", "update_behavior": "same revision no-op; changed revision reinstall", "uninstall": "remove receipt-owned unchanged file"},
        }}
        ok, reason = module._install_evidence_ok(case, report, before, after)
        self.assertTrue(ok, reason)
        report["installation"]["payload"]["adaptation"]["files"].append({
            "path": "unselected.txt", "source_sha256": source_hash, "installed_sha256": installed_hash,
        })
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])
        report["installation"]["payload"]["adaptation"]["files"].pop()
        after[".agents/skills/healthy/references/guide.md"] = "also-adjusted"
        self.assertFalse(module._install_evidence_ok(case, report, before, after)[0])

    def test_install_collision_and_redesign_must_preserve_the_fixture(self):
        module = load_module()
        collision_before = {".agents/skills/healthy/SKILL.md": "owned", "\0content/.agents/skills/healthy/SKILL.md": "hash"}
        self.assertTrue(module._install_evidence_ok(
            {"kind": "INSTALL", "installation_outcome": "BLOCKED"},
            {"installation": {"status": "BLOCKED", "workspace_changed": False, "collision": "unmanaged target preserved"}},
            collision_before,
            dict(collision_before),
        )[0])
        collision_after = dict(collision_before)
        collision_after["\0content/.agents/skills/healthy/SKILL.md"] = "changed"
        self.assertFalse(module._install_evidence_ok(
            {"kind": "INSTALL", "installation_outcome": "BLOCKED"},
            {"installation": {"status": "BLOCKED", "workspace_changed": False, "collision": "unmanaged target preserved"}},
            collision_before,
            collision_after,
        )[0])
        self.assertTrue(module._install_evidence_ok(
            {"kind": "INSTALL", "installation_outcome": "ROUTE"},
            {"installation": {"status": "ROUTE", "workspace_changed": False, "route": "CREATE", "reason": "The requested source requires material workflow redesign."}},
        )[0])
        self.assertFalse(module._install_evidence_ok(
            {"kind": "INSTALL", "installation_outcome": "BLOCKED"},
            {"installation": {"status": "BLOCKED", "workspace_changed": True, "collision": "unmanaged target preserved"}},
        )[0])

    def test_install_workflow_is_operational_not_route_only(self):
        workflow = (SCRIPT.parents[1] / "workflows" / "install.md").read_text(encoding="utf-8").lower()
        for marker in ("resolve", "pin", "license", "package closure", "collision", "install receipt", "real-task", "cleanup"):
            self.assertIn(marker, workflow)
        self.assertNotIn("route-only", workflow)

    def test_runtime_fixture_uses_repo_skill_discovery_location(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        with module._fixture(skill_dir, True) as fixture:
            self.assertTrue((fixture / ".agents" / "skills" / "skill-creator" / "SKILL.md").is_file())

    def test_localize_coexistence_marker_is_in_project_fixture(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        case = {"id": "audit-localize", "kind": "AUDIT"}
        with module._fixture(skill_dir, True, case) as fixture:
            self.assertFalse((fixture / ".fixture-coexistence").is_file())
            self.assertTrue((fixture / "project" / ".fixture-coexistence").is_file())

    def test_snapshot_excludes_runtime_home(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex-home").mkdir()
            (root / ".codex-home" / "cache").write_text("runtime", encoding="utf-8")
            (root / "artifact.txt").write_text("artifact", encoding="utf-8")
            self.assertEqual(set(module._snapshot(root)), {"artifact.txt", "\0content/artifact.txt"})

    def test_trial_metadata_binds_identity_and_terminal_cleanup(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        case = {"id": "create-local-upstream", "kind": "CREATE", "paired": True}
        trial = module._trial_metadata(
            skill_dir,
            case,
            "with_skill",
            {"candidate_revision": "a" * 40, "base_identity": "b" * 40, "test_fingerprint": "c" * 64},
        )
        result = module._trial_result({"status": "PASS"}, trial)
        self.assertRegex(result["trial"]["trial_id"], r"^[0-9a-f-]{36}$")
        self.assertEqual(result["trial"]["candidate_fingerprint"]["revision"], "a" * 40)
        self.assertEqual(result["trial"]["base_identity"], "b" * 40)
        self.assertEqual(result["trial"]["test_fingerprint"], "c" * 64)
        self.assertEqual(result["trial"]["lifecycle"]["terminal_state"], "CLEANED")
        self.assertTrue(result["trial"]["lifecycle"]["evidence_frozen"])

    def test_unavailable_preflight_emits_per_case_not_assessed_records(self):
        module = load_module()
        cases_path = SCRIPT.parents[1] / "evals" / "cases.yaml"
        report = module.run(
            cases_path,
            SCRIPT.parents[1],
            "definitely-not-a-codex-runtime",
            "gpt-6-luna",
            "medium",
            1,
            None,
            "smoke",
            None,
            None,
        )
        self.assertEqual(report["runtime_preflight"]["status"], "NO_RUNTIME")
        self.assertEqual(len(report["results"]), 3)
        self.assertTrue(all(item["status"] == "NOT_ASSESSED" for item in report["results"]))
        self.assertTrue(all(item["trial"]["lifecycle"]["terminal_state"] == "CLEANED" for item in report["results"]))

    def test_fixture_is_a_nested_git_project_for_runtime_write_boundaries(self):
        module = load_module()
        with module._fixture(SCRIPT.parents[1], True) as fixture:
            self.assertTrue((fixture / ".git").is_dir())

    def test_repository_case_contract_has_all_gates_and_partitions(self):
        module = load_module()
        self.assertEqual(module.validate(SCRIPT.parents[1] / "evals" / "cases.yaml"), [])

    def test_action_contract_covers_four_actions_and_fail_closed_edges(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        cases = module.load_cases(skill_dir / "evals" / "cases.yaml")["action_cases"]
        self.assertEqual({case["action"] for case in cases[:4]}, {"create", "install", "update", "audit"})
        self.assertEqual(cases[4]["expected"], "fail-closed")
        self.assertEqual(cases[5]["expected"], "clarify-or-no-route")
        root = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(all(f"workflows/{action}.md" in root for action in ("create", "install", "update", "audit")))
        self.assertNotRegex(root, r"\bMAINTAIN\b")

    def test_shared_reference_contracts_preserve_operational_semantics(self):
        skill_dir = SCRIPT.parents[1]
        evaluation = (skill_dir / "references" / "evaluation.md").read_text(encoding="utf-8")
        authoring = (skill_dir / "references" / "authoring.md").read_text(encoding="utf-8")
        environment = (skill_dir / "references" / "test-environment.md").read_text(encoding="utf-8")
        architecture = (skill_dir / "references" / "architecture.md").read_text(encoding="utf-8")
        self.assertNotIn("G0_NECESSITY", evaluation)
        for marker in (
            "real-task selection", "portfolio", "outcome correctness", "workflow fidelity",
            "branch/checkpoint coverage", "held-out", "batch-before-repair", "stochastic",
            "persistent or creation-only", "failure classification",
        ):
            self.assertIn(marker, evaluation.lower())
        for marker in ("WHY", "WHEN", "WHAT", "HOW", "BRANCH", "OUTPUT", "RELATED RESOURCES"):
            self.assertIn(marker, authoring)
        for marker in ("RUN", "READ"):
            self.assertIn(marker, authoring)
        for marker in (
            "normal path before exceptions", "decision before enumeration",
            "resource routing by `when`", "consumer/load timing", "flat inventory",
        ):
            self.assertIn(marker, authoring.lower())
        for marker in (
            "ALLOCATE", "PREPARE", "BASELINE", "RUN", "FREEZE EVIDENCE", "REPORT",
            "ARCHIVE", "CLEAN", "CLEANED", "PRESERVED_FOR_REVIEW", "CLEANUP_BLOCKED",
            "temporary copy", "worktree", "sandbox", "candidate revision/tree fingerprint",
            "test/case fingerprint",
        ):
            self.assertIn(marker, environment)
        for marker in ("Phase Contract", "failure", "recovery", "forward trace", "reverse-trace"):
            self.assertIn(marker.lower(), architecture.lower())

    def test_create_install_boundary_and_multimode_case_are_current(self):
        module = load_module()
        skill_dir = SCRIPT.parents[1]
        create = (skill_dir / "workflows" / "create.md").read_text(encoding="utf-8").lower()
        cases = module.load_cases(skill_dir / "evals" / "cases.yaml")
        local_upstream = next(case for case in cases["cases"] if case["id"] == "create-local-upstream")
        self.assertEqual(local_upstream["expected"], "REFERENCE_AND_ADAPT")
        self.assertIn("donor/reference-only", local_upstream["prompt"].lower())
        self.assertIn("not independently installable", local_upstream["prompt"].lower())
        source_strategy = (skill_dir / "references" / "source-strategy.md").read_text(encoding="utf-8").lower()
        self.assertIn("installable owner", source_strategy)
        self.assertIn("donor/reference", source_strategy)
        multimode = next(case for case in cases["cases"] if case["id"] == "create-multimode-one-skill")
        self.assertIn("install", create)
        self.assertIn("donor", create)
        self.assertIn("create, install, update, and audit", multimode["prompt"].lower())
        self.assertIn("evaluate", multimode["prompt"].lower())
        self.assertNotIn("create, update, evaluate, and audit", multimode["prompt"].lower())

    def test_issue_fixture_has_no_unconsumed_duplicate(self):
        module = load_module()
        repo_root = SCRIPT.parents[3]
        tracked = module.subprocess.check_output(
            ["git", "ls-files", "fixtures/issue-121/skill-creator-v2"],
            cwd=repo_root,
            text=True,
        )
        self.assertEqual(tracked, "")

    def test_action_cases_have_a_runtime_workflow_observation_contract(self):
        module = load_module()
        case = {"id": "explicit-create", "kind": "ACTION", "prompt": "Create a reusable skill."}
        prompt = module._runtime_prompt(case, Path("/tmp/eval"))
        self.assertIn("selected_workflow", prompt)
        self.assertEqual(module._artifact_contract(case), {})

    def test_audit_workflow_is_read_only_and_returns_dispositions(self):
        audit = (SCRIPT.parents[1] / "workflows" / "audit.md").read_text(encoding="utf-8")
        self.assertIn("read-only", audit)
        self.assertIn("HEALTHY", audit)
        self.assertIn("BLOCKED", audit)
        self.assertNotIn("execute the selected disposition", audit)

    def test_initializer_omits_unsupported_metadata_by_default(self):
        module = load_initializer()
        with tempfile.TemporaryDirectory() as directory:
            result = module.init_skill("generated-skill", Path(directory), [], False, {})
            self.assertIsNotNone(result)
            self.assertTrue((result / "SKILL.md").is_file())
            self.assertFalse((result / "agents").exists())
        self.assertFalse((SCRIPT.parents[1] / "agents" / "openai.yaml").exists())

    def test_initializer_creates_metadata_only_for_explicit_interface_contract(self):
        module = load_initializer()
        with tempfile.TemporaryDirectory() as directory:
            result = module.init_skill(
                "generated-skill",
                Path(directory),
                [],
                False,
                ["short_description=Generate a reusable skill package"],
            )
            self.assertIsNotNone(result)
            self.assertTrue((result / "agents" / "openai.yaml").is_file())

    def test_compare_rejects_missing_before_or_after_evidence(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before = root / "before.json"
            after = root / "after.json"
            before.write_text(json.dumps({"results": []}), encoding="utf-8")
            after.write_text(json.dumps({"results": [{"partition": "held_out", "status": "PASS"}]}), encoding="utf-8")
            self.assertEqual(module._compare(before, after)["status"], "REJECT")

    def test_compare_rejects_unassessed_lifecycle_transition_claims(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            before = root / "before.json"
            after = root / "after.json"
            cases_path = SCRIPT.parents[1] / "evals" / "cases.yaml"
            cases = module.load_cases(cases_path)["cases"]
            binding = {
                "version": 1,
                "repository_root": "/tmp/repository",
                "base_head": "0" * 40,
                "candidate_head": "1" * 40,
                "skill_tree_sha256": "a" * 64,
                "cases_sha256": "b" * 64,
            }

            def trial(condition):
                return {
                    "trial_id": str(uuid.UUID(int=next(trial.counter))),
                    "condition": condition,
                    "environment_kind": "temporary_copy",
                    "candidate_fingerprint": {"revision": binding["candidate_head"], "tree_sha256": binding["skill_tree_sha256"]},
                    "test_fingerprint": binding["cases_sha256"],
                    "base_identity": binding["base_head"],
                    "runtime_auth_status": "READY",
                    "lifecycle": {"sequence": module.TRIAL_SEQUENCE, "baseline": "paired_without_skill", "evidence_frozen": True, "terminal_state": "CLEANED"},
                }
            trial.counter = iter(range(1, 1000))
            results = []
            for case in cases:
                with_skill_trial = trial("with_skill")
                routing = case["kind"] == "routing"
                expected = "none" if case.get("expected") == "none" else case["expected"]
                contract = {}
                if routing:
                    trace_events = [{"skill_loads": [] if expected == "none" else ["skill-creator"]}]
                    before_snapshot = {}
                    after_snapshot = {}
                else:
                    if case.get("id") == "install-owned-lifecycle":
                        trace_events = [{"skill_loads": ["skill-creator"]}, *(
                            {"item": {"type": "command_execution", "command": marker}}
                            for marker in case.get("trace_markers", [])
                        )]
                    else:
                        trace_events = [{"skill_loads": ["skill-creator"], "item": {"type": "command_execution", "command": " ".join(case.get("trace_markers", []))}}]
                    contract = module._artifact_contract(case)
                    if contract.get("operation") == "modified":
                        before_snapshot = {contract["path"]: "old"}
                        after_snapshot = {contract["path"]: "new"}
                    elif contract.get("operation") == "created":
                        before_snapshot = {}
                        after_snapshot = {contract["path"]: "new"}
                    else:
                        before_snapshot = {}
                        after_snapshot = {}
                    if case["kind"] == "INSTALL" and case["installation_outcome"] == "INSTALLED":
                        case["_resolved_revision"] = case["source_revision"]
                        case["_resolved_license"] = case.get("source_license", "MIT")
                        source_root = case["source_fixture"]
                        target_path = next(effect["path"] for effect in case["side_effects"] if effect["path"].endswith("/SKILL.md")).removesuffix("/SKILL.md")
                        for relative in case["package_files"]:
                            source_path = f"{source_root}/{relative}"
                            installed_path = f"{target_path}/{relative}"
                            before_snapshot[source_path] = f"bytes:{relative}"
                            after_snapshot[source_path] = f"bytes:{relative}"
                            after_snapshot[installed_path] = f"bytes:{relative}"
                            digest = hashlib.sha256(f"bytes:{relative}".encode()).hexdigest()
                            before_snapshot[f"\0content/{source_path}"] = digest
                            after_snapshot[f"\0content/{source_path}"] = digest
                            after_snapshot[f"\0content/{installed_path}"] = digest
                        for effect in case["side_effects"]:
                            after_snapshot.setdefault(effect["path"], f"owned:{effect['path']}")
                            if "/.skill-installs/" in f"/{effect['path']}":
                                after_snapshot[f"\0content/{effect['path']}"] = hashlib.sha256(f"owned:{effect['path']}".encode()).hexdigest()
                        if case["id"] == "install-owned-lifecycle":
                            canary_path = ".fixture-data/neighbor-canary.txt"
                            canary_hash = hashlib.sha256(b"unowned neighbor canary\n").hexdigest()
                            before_snapshot[f"\0content/{canary_path}"] = canary_hash
                            after_snapshot[f"\0content/{canary_path}"] = canary_hash
                    if "G5_COEXISTENCE" in case.get("gates", [case["gate"]]):
                        for path in module.COEXISTENCE_PATHS.get(case["id"], set()):
                            before_snapshot[path] = "fixture"
                            after_snapshot[path] = "fixture"
                for effect in contract.get("side_effects", []):
                    if effect["operation"] == "deleted":
                        after_snapshot.pop(effect["path"], None)
                final_report = {"selected_skill": expected} if routing else (
                    {"disposition": expected, "necessity": {"disposition": module.EXPECTED_NECESSITY_DISPOSITIONS[case["id"]], "alternatives": {check: {"state": "CHECKED", "disposition": module.EXPECTED_NECESSITY_DISPOSITIONS[case["id"]] if case["kind"] == "CREATE" and check == "maintained_candidate" else "USE_EXISTING", "reason": "fixture alternative was compared against the requested reusable capability", **({"source_role": "DONOR_REFERENCE_ONLY"} if case["kind"] == "CREATE" and check == "maintained_candidate" else {})} for check in module.NECESSITY_CHECKS}, "justification": "fixture alternatives compared"}}
                    if case["kind"] in {"CREATE", "UPDATE", "AUDIT"} else {"disposition": expected}
                )
                if case["kind"] == "INSTALL":
                    if case["installation_outcome"] == "INSTALLED":
                        target_path = next(effect["path"] for effect in case["side_effects"] if effect["path"].endswith("/SKILL.md")).removesuffix("/SKILL.md")
                        final_report = {"disposition": expected, "installation": {
                            "status": "INSTALLED", "workspace_changed": True,
                            "source": {"repository": case.get("source_repository", "owner/skill"), "requested_ref": case.get("source_ref", "v1"), "revision": case["source_revision"], "path": case["source_fixture"], "license": case.get("source_license", "MIT")},
                            "target": {"runtime": "codex", "scope": "project", "path": target_path, "mode": "copy"},
                            "payload": {
                                "source_sha256": module._content_tree_sha256(before_snapshot, case["source_fixture"]),
                                "selected_sha256": module._content_tree_sha256(before_snapshot, case["source_fixture"], case["package_files"]),
                                "installed_sha256": module._content_tree_sha256(after_snapshot, target_path, case["package_files"]),
                                "files": [{
                                    "path": relative,
                                    "source_sha256": before_snapshot[f"\0content/{case['source_fixture']}/{relative}"],
                                    "installed_sha256": after_snapshot[f"\0content/{target_path}/{relative}"],
                                } for relative in case["package_files"]],
                                "adaptation": "none",
                            },
                            "backend": {
                                "identity": "fixture", "version": "1",
                                "state_identity": next((after_snapshot.get(f"\0content/{effect['path']}") for effect in case["side_effects"] if "/.skill-installs/" in f"/{effect['path']}"), "fixture-state"),
                                "native_revision": "3" * 40,
                            },
                            "audit": {"status": "PASS", "backend": "fixture"}, "validation": {"status": "PASS"},
                            "real_task": {"status": "PASS"}, "ownership": {"receipt_id": "fixture-001", "update_behavior": "same revision no-op; changed revision reinstall", "uninstall": "remove only receipt-owned files"},
                        }}
                        if case["id"] == "install-owned-lifecycle":
                            installed_files = {item["path"]: item["installed_sha256"] for item in final_report["installation"]["payload"]["files"]}
                            changed_files = {path: hashlib.sha256(f"changed:{path}".encode()).hexdigest() for path in installed_files}
                            edited_files = {path: hashlib.sha256(f"edited:{path}".encode()).hexdigest() for path in installed_files}
                            neighbor_hash = hashlib.sha256(b"unowned neighbor canary\n").hexdigest()
                            final_report["installation"]["owned_lifecycle"] = {
                                "trial_id": with_skill_trial["trial_id"],
                                "source_revision": case["source_revision"],
                                "selected_sha256": final_report["installation"]["payload"]["selected_sha256"],
                                "receipt_id": "fixture-001",
                                "locally_modified_paths": sorted(installed_files),
                                "neighbor_path": ".fixture-data/neighbor-canary.txt",
                                "steps": {step: "PASS" for step in ("initial_install", "same_revision", "changed_revision", "local_edit_preserved", "safe_uninstall", "neighbor_preserved", "final_reinstall")},
                                "neighbor_hash": neighbor_hash,
                                "snapshots": {
                                    "after_install": {"owned_files": installed_files},
                                    "after_same_revision": {"owned_files": installed_files},
                                    "after_changed_revision": {"source_revision": "4" * 40, "owned_files": changed_files},
                                    "after_local_edit": {"owned_files": edited_files},
                                    "after_uninstall": {"owned_files": {}, "preserved_modified_files": edited_files, "neighbor_hash": neighbor_hash},
                                    "after_final_reinstall": {"source_revision": case["source_revision"], "owned_files": installed_files},
                                },
                                "terminal_state": "CLEANED",
                            }
                    elif case["installation_outcome"] == "BLOCKED":
                        final_report = {"disposition": expected, "installation": {"status": "BLOCKED", "workspace_changed": False, "collision": "unmanaged target preserved"}}
                    else:
                        final_report = {"disposition": expected, "installation": {"status": "ROUTE", "workspace_changed": False, "route": "CREATE", "reason": "Material behavior redesign is required."}}
                changed_paths = sorted(module._changed_paths(before_snapshot, after_snapshot))
                results.append({
                    "case_id": case["id"],
                    "kind": case["kind"],
                    "condition": "with_skill",
                    "expected": case["expected"],
                    "partition": case["partition"],
                    "gate": case["gate"],
                    "gates": case.get("gates", [case["gate"]]),
                    "status": "NOT_ASSESSED" if case.get("id") == "install-owned-lifecycle" else "PASS",
                    "observed": expected,
                    "activation": "unloaded" if expected == "none" else "loaded",
                    "runtime_evidence": {"skill_discovery": "NOT_ASSESSED", "explicit_invocation": "NOT_REQUESTED", "implicit_activation": "unloaded" if expected == "none" else "loaded", "behavior": "NOT_ASSESSED" if case.get("id") == "install-owned-lifecycle" else "OBSERVED"},
                    "process_observed": not routing,
                    "trace_matches": True,
                    "artifact_ok": True,
                    "necessity_observed": True,
                    "coexistence_fixture": module.COEXISTENCE_PATHS.get(case["id"], set()).issubset(before_snapshot),
                    "changed_paths": changed_paths,
                    "cost_metrics": module._cost_metrics(trace_events, set(changed_paths)),
                    "trace_events": trace_events,
                    "before_snapshot": before_snapshot,
                    "after_snapshot": after_snapshot,
                    "final_report": final_report,
                    **({"source_revision_resolved": case.get("_resolved_revision"), "source_license_resolved": case.get("_resolved_license")} if case["kind"] == "INSTALL" and case["installation_outcome"] == "INSTALLED" else {}),
                    "installation_observed": module._install_evidence_ok(case, final_report, before_snapshot, after_snapshot)[0],
                    "installation_reason": module._install_evidence_ok(case, final_report, before_snapshot, after_snapshot)[1],
                    "trial": with_skill_trial,
                })
            gates = {gate: "PASS" for gate in module.GATES}
            gates["G4_BEHAVIOR"] = "NOT_ASSESSED"
            gates["G5_COEXISTENCE"] = "NOT_ASSESSED"
            gates["G7_INDEPENDENT_REVIEW"] = "NOT_ASSESSED"
            baseline_results = []
            paired = []
            for case in cases:
                if case.get("paired") is not True:
                    continue
                contract = module._artifact_contract(case, False)
                if contract.get("operation") == "modified":
                    baseline_before = {contract["path"]: "old"}
                    baseline_after = {contract["path"]: "new"}
                elif contract.get("operation") == "created":
                    baseline_before = {}
                    baseline_after = {contract["path"]: "new"}
                else:
                    baseline_before = {}
                    baseline_after = {}
                if "G5_COEXISTENCE" in case.get("gates", [case["gate"]]):
                    for path in module.COEXISTENCE_PATHS[case["id"]]:
                        baseline_before[path] = "fixture"
                        baseline_after[path] = "fixture"
                baseline_changed_paths = sorted(module._changed_paths(baseline_before, baseline_after))
                baseline_events = [{"item": {"type": "command_execution", "command": " ".join(case.get("trace_markers", []))}}]
                baseline = {
                    "case_id": case["id"],
                    "kind": case["kind"],
                    "condition": "without_skill",
                    "expected": case["expected"],
                    "partition": case["partition"],
                    "gate": case["gate"],
                    "gates": case.get("gates", [case["gate"]]),
                    "status": "OBSERVED",
                    "observed": "baseline",
                    "activation": None,
                    "runtime_evidence": {"skill_discovery": "NOT_ASSESSED", "explicit_invocation": "NOT_REQUESTED", "implicit_activation": "NOT_ASSESSED", "behavior": "OBSERVED"},
                    "process_observed": True,
                    "trace_matches": True,
                    "artifact_ok": True,
                    "necessity_observed": case["kind"] == "EVALUATE",
                    "coexistence_fixture": module.COEXISTENCE_PATHS.get(case["id"], set()).issubset(baseline_before),
                    "changed_paths": baseline_changed_paths,
                    "cost_metrics": module._cost_metrics(baseline_events, set(baseline_changed_paths)),
                    "trace_events": baseline_events,
                    "before_snapshot": baseline_before,
                    "after_snapshot": baseline_after,
                    "final_report": {"disposition": "baseline"},
                    "installation_observed": module._install_evidence_ok(case, {"disposition": "baseline"}, baseline_before, baseline_after)[0],
                    "installation_reason": module._install_evidence_ok(case, {"disposition": "baseline"}, baseline_before, baseline_after)[1],
                    "trial": trial("without_skill"),
                }
                baseline_results.append(baseline)
                candidate = next(item for item in results if item["case_id"] == case["id"])
                paired.append({"case_id": case["id"], "with_status": "PASS", "without_status": "OBSERVED", **module._paired_evidence(candidate, baseline)})
            results.extend(baseline_results)
            action_cases = module.load_cases(cases_path)["action_cases"]
            action_results = [
                {
                    "case_id": case["id"],
                    "kind": "ACTION",
                    "condition": "with_skill",
                    "expected": case["expected"],
                    "status": "PASS",
                    "observed": case["expected"],
                    "activation": "loaded",
                    "runtime_observed": True,
                    "runtime_evidence": {"skill_discovery": "NOT_ASSESSED", "explicit_invocation": "NOT_REQUESTED", "implicit_activation": "loaded", "behavior": "OBSERVED"},
                    "process_observed": True,
                    "trace_matches": True,
                    "artifact_ok": True,
                    "changed_paths": [],
                    "cost_metrics": {"tool_calls": 1, "command_count": 1, "token_count": None, "tokens_observed": False, "artifact_count": 0},
                    "trace_events": [{"skill_loads": ["skill-creator"], "item": {"type": "command_execution", "command": "skill action probe"}}],
                    "before_snapshot": {},
                    "after_snapshot": {},
                    "final_report": {"selected_workflow": case["expected"]},
                    "trial": trial("with_skill"),
                }
                for case in action_cases
            ]
            payload = {
                "evidence_binding": binding,
                "coverage": {"full_corpus": True},
                "gates": gates,
                "routing": {"status": "PASS", "TP": 5, "FN": 0, "FP": 0, "TN": 7, "precision": 1.0, "recall": 1.0, "false_positive_rate": 0.0, "assessed_cases": 12, "total_cases": 12, "action_status": "PASS", "action_assessed_cases": 6, "action_total_cases": 6, "action_expected_cases": 6},
                "action_cases": action_results,
                "paired": paired,
                "results": results,
            }
            before.write_text(json.dumps(payload), encoding="utf-8")
            after.write_text(json.dumps(payload), encoding="utf-8")
            comparison = module._compare(before, after, cases_path)
            self.assertEqual(comparison["status"], "REJECT", comparison)
            invalid_install = json.loads(json.dumps(payload))
            install_case = next(case for case in module.load_cases(cases_path)["cases"] if case["id"] == "install-healthy-copy")
            install_record = next(item for item in invalid_install["results"] if item["case_id"] == "install-healthy-copy")
            install_record["final_report"]["installation"]["source"]["revision"] = "2" * 40
            recomputed_install = module._recomputed_record(install_record, install_case)
            install_record["installation_observed"] = recomputed_install["installation_observed"]
            install_record["installation_reason"] = recomputed_install["installation_reason"]
            install_record["runtime_evidence"] = recomputed_install["runtime_evidence"]
            before.write_text(json.dumps(invalid_install), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            correlated_tamper = json.loads(json.dumps(payload))
            install_record = next(item for item in correlated_tamper["results"] if item["case_id"] == "install-healthy-copy")
            install_record["final_report"]["installation"]["source"]["revision"] = "3" * 40
            install_record["source_revision_resolved"] = "3" * 40
            recomputed_install = module._recomputed_record(install_record, install_case)
            install_record["installation_observed"] = recomputed_install["installation_observed"]
            install_record["installation_reason"] = recomputed_install["installation_reason"]
            install_record["runtime_evidence"] = recomputed_install["runtime_evidence"]
            before.write_text(json.dumps(correlated_tamper), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            before.write_text(json.dumps(payload), encoding="utf-8")
            expected_binding = dict(payload["evidence_binding"])
            expected_binding["candidate_head"] = "2" * 40
            self.assertEqual(module._compare(before, after, cases_path, expected_binding)["status"], "REJECT")
            missing_binding = json.loads(json.dumps(payload))
            missing_binding.pop("evidence_binding")
            before.write_text(json.dumps(missing_binding), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            stale_binding = json.loads(json.dumps(payload))
            stale_binding["evidence_binding"]["candidate_head"] = "f" * 40
            before.write_text(json.dumps(stale_binding), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            incomplete = json.loads(json.dumps(payload))
            incomplete["results"][0].pop("activation")
            before.write_text(json.dumps(incomplete), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            missing_trial = json.loads(json.dumps(payload))
            missing_trial["results"][0].pop("trial")
            before.write_text(json.dumps(missing_trial), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            duplicate_trial = json.loads(json.dumps(payload))
            duplicate_trial["action_cases"][0]["trial"]["trial_id"] = duplicate_trial["results"][0]["trial"]["trial_id"]
            before.write_text(json.dumps(duplicate_trial), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            invalid_gate = json.loads(json.dumps(payload))
            invalid_gate["gates"]["G7_INDEPENDENT_REVIEW"] = "PASS"
            before.write_text(json.dumps(invalid_gate), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            missing_pair = json.loads(json.dumps(payload))
            missing_pair["paired"] = []
            before.write_text(json.dumps(missing_pair), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            missing_actions = json.loads(json.dumps(payload))
            missing_actions.pop("action_cases")
            before.write_text(json.dumps(missing_actions), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            missing_action_runtime = json.loads(json.dumps(payload))
            missing_action_runtime["action_cases"][0].pop("trace_events")
            before.write_text(json.dumps(missing_action_runtime), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            missing_baseline = json.loads(json.dumps(payload))
            missing_baseline["results"] = [item for item in missing_baseline["results"] if item["condition"] == "with_skill"]
            before.write_text(json.dumps(missing_baseline), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            relabeled = json.loads(json.dumps(payload))
            relabeled["results"][0]["kind"] = "CREATE"
            before.write_text(json.dumps(relabeled), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")
            gate_mismatch = json.loads(json.dumps(payload))
            next(item for item in gate_mismatch["results"] if item["case_id"] == "audit-overlap")["status"] = "FAIL"
            before.write_text(json.dumps(gate_mismatch), encoding="utf-8")
            self.assertEqual(module._compare(before, after, cases_path)["status"], "REJECT")

    def test_independent_review_is_not_caller_supplied(self):
        self.assertNotIn("--review-status", SCRIPT.read_text(encoding="utf-8"))

    def test_evidence_binding_rejects_candidate_ref_not_at_current_head(self):
        module = load_module()
        root = Path(__file__).resolve().parents[3]
        with patch.object(module, "_git_revision", side_effect=["0" * 40, "1" * 40, "2" * 40]):
            binding = module._evidence_binding(root / "skills" / "skill-creator", root / "skills" / "skill-creator" / "evals" / "cases.yaml", "base", "candidate")
        self.assertIsNone(binding["candidate_head"])
        self.assertFalse(module._valid_evidence_binding(binding))

    def test_evidence_binding_rejects_dirty_candidate_package(self):
        module = load_module()
        root = Path(__file__).resolve().parents[3]
        with patch.object(module, "_git_revision", side_effect=["a" * 40, "a" * 40, "b" * 40]), patch.object(module, "_candidate_worktree_matches", return_value=False):
            binding = module._evidence_binding(root / "skills" / "skill-creator", root / "skills" / "skill-creator" / "evals" / "cases.yaml", "base", "candidate")
        self.assertIsNone(binding["candidate_head"])

    def test_negative_activation_requires_explicit_empty_load_signal(self):
        module = load_module()
        self.assertEqual(module._runtime_activation([{"skill_loads": []}]), "unloaded")
        self.assertIsNone(module._runtime_activation([{"item": {"type": "agent_message", "text": "none"}}]))

    def test_activation_matching_is_exact_and_targeted(self):
        module = load_module()
        self.assertEqual(module._runtime_activation([{"skill_loads": ["skill-creator"]}]), "loaded")
        self.assertEqual(module._runtime_activation([{"skill_loads": [{"name": "skill-creator"}]}]), "loaded")
        self.assertEqual(module._runtime_activation([{"skill_loads": ["not-skill-creator"]}]), "unloaded")
        self.assertEqual(module._runtime_activation([{"loaded_skill": "another-skill"}]), "unloaded")
        self.assertEqual(module._runtime_activation([{"skill_loads": []}, {"skill_loads": ["skill-creator"]}]), "loaded")
        self.assertIsNone(module._runtime_activation([{"skill_loads": ["skill-creator"]}, {"skill_loads": []}]))

    def test_run_requires_revision_binding(self):
        module = load_module()
        original = sys.argv
        try:
            sys.argv = [str(SCRIPT), str(SCRIPT.parent.parent / "evals" / "cases.yaml"), "--run"]
            output = io.StringIO()
            with contextlib.redirect_stdout(output), patch.object(module, "run") as run:
                self.assertEqual(module.main(), 1)
            run.assert_not_called()
            self.assertIn("--run requires both --base and --candidate", output.getvalue())
        finally:
            sys.argv = original

    def test_routing_pass_requires_expected_activation_state(self):
        module = load_module()
        positive = {"kind": "routing", "expected": "skill-creator"}
        negative = {"kind": "routing", "expected": "none"}
        self.assertEqual(module._routing_status(positive, "loaded", "skill-creator")[0], "PASS")
        self.assertEqual(module._routing_status(positive, "unloaded", "skill-creator")[0], "FAIL")
        self.assertEqual(module._routing_status(negative, "unloaded", "none")[0], "PASS")
        self.assertEqual(module._routing_status(negative, "loaded", "none")[0], "FAIL")

    def test_nonrouting_run_rejects_explicitly_unloaded_skill(self):
        module = load_module()
        case = {"id": "audit-overlap", "kind": "AUDIT", "gate": "G4_BEHAVIOR", "expected": "HEALTHY", "prompt": "Review this fixture."}
        process = subprocess.CompletedProcess([], 0, "runtime output", "")
        with (
            patch.object(module.subprocess, "run", return_value=process),
            patch.object(module, "_events", return_value=[]),
            patch.object(module, "_final_text", return_value="{}"),
            patch.object(module, "_json_object", return_value={"disposition": "HEALTHY"}),
            patch.object(module, "_runtime_activation", return_value="unloaded"),
            patch.object(module, "_process_observed", return_value=True),
            patch.object(module, "_trace_matches", return_value=True),
            patch.object(module, "_artifact_ok", return_value=(True, "ok")),
            patch.object(module, "_necessity_ok", return_value=(True, "ok")),
            patch.object(module, "_install_evidence_ok", return_value=(True, "ok")),
        ):
            result = module._run_once(case, sys.executable, "gpt-6-luna", "max", 10, SCRIPT.parents[1], True)
        self.assertEqual(result["status"], "FAIL")

    def test_trace_markers_are_bound_to_process_payloads(self):
        module = load_module()
        case = {"trace_markers": ["clone"]}
        self.assertFalse(module._trace_matches(case, [{"item": {"type": "agent_message", "text": "clone"}}]))
        self.assertTrue(module._trace_matches(case, [{"item": {"type": "command_execution", "command": "git clone source"}}]))
        self.assertTrue(module._trace_matches(case, [{"item": {"type": "command_execution", "aggregated_output": "git clone source"}}]))

    def test_owned_lifecycle_trace_markers_require_distinct_ordered_process_events(self):
        module = load_module()
        case = {"id": "install-owned-lifecycle"}
        stages = ["after_initial_install", "after_same_revision", "after_changed_revision", "after_local_edit", "after_reinstall_with_local_edit", "after_uninstall", "neighbor_preserved", "after_clean_uninstall", "after_final_reinstall"]
        events = [{"runner_stage": stage} for stage in stages]
        self.assertTrue(module._trace_matches(case, events))
        self.assertFalse(module._trace_matches(case, [events[0], events[2], events[1]]))
        self.assertFalse(module._trace_matches(case, [{"item": {"type": "command_execution", "command": " ".join(stages)}}]))

    def test_runtime_prompt_does_not_leak_case_expected_disposition(self):
        module = load_module()
        case = {
            "id": "create-local-upstream",
            "kind": "CREATE",
            "expected": "CLONE_AND_ADAPT",
            "prompt": "Create the requested reusable local skill.",
            "artifact": "created",
            "artifact_path": ".agents/skills/generated-skill/SKILL.md",
        }
        prompt = module._runtime_prompt(case, Path("/tmp/eval"))
        self.assertNotIn("must be exactly", prompt)
        self.assertNotIn("matching the expected", prompt)
        self.assertEqual(prompt.count(case["expected"]), 1)

    def test_action_dispositions_do_not_use_no_match_state(self):
        module = load_module()
        self.assertNotIn("NO_MATCH", module.ACTION_DISPOSITIONS)
        self.assertIn("NOT_AVAILABLE", module.NECESSITY_STATES)

    def test_json_object_allows_trailing_prose(self):
        module = load_module()
        self.assertEqual(module._json_object('{"disposition":"REJECT"}\nDone.'), {"disposition": "REJECT"})

    def test_snapshot_ignores_runtime_bytecode(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "kept.txt").write_text("kept", encoding="utf-8")
            cache = root / "__pycache__"
            cache.mkdir()
            (cache / "generated.cpython-313.pyc").write_bytes(b"cache")
            snapshot = module._snapshot(root)
            self.assertEqual(set(snapshot), {"kept.txt", "\0content/kept.txt"})

    def test_snapshot_binds_directories_and_symlink_targets(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "target").mkdir()
            (root / "target" / "file.txt").write_text("one", encoding="utf-8")
            (root / "link").symlink_to("target", target_is_directory=True)
            first = module._snapshot(root)
            (root / "link").unlink()
            (root / "link").symlink_to("other", target_is_directory=True)
            second = module._snapshot(root)
            self.assertIn("\0dir/target", first)
            self.assertNotEqual(first["link"], second["link"])

    def test_routing_metrics_counts_observed_failures(self):
        module = load_module()
        cases = [
            {"id": "positive", "kind": "routing", "polarity": "positive"},
            {"id": "negative", "kind": "routing", "polarity": "negative"},
        ]
        results = [
            {"case_id": "positive", "status": "FAIL", "observed": "none"},
            {"case_id": "negative", "status": "PASS", "observed": "skill-creator"},
        ]
        report = module._routing_metrics(results, cases)
        self.assertEqual(report["FN"], 1)
        self.assertEqual(report["FP"], 1)
        self.assertEqual(report["status"], "FAIL")

    def test_action_probe_failures_are_qualification_failures(self):
        module = load_module()
        cases = [{"id": "explicit-create"}, {"id": "unknown-action"}]
        report = module._routing_metrics(
            [{"case_id": "positive", "status": "PASS", "observed": "skill-creator"}],
            [{"id": "positive", "kind": "routing", "polarity": "positive"}],
            [{"case_id": "explicit-create", "status": "FAIL"}, {"case_id": "unknown-action", "status": "PASS"}],
            cases,
        )
        self.assertEqual(report["action_status"], "FAIL")
        self.assertEqual(report["status"], "FAIL")

    def test_create_source_strategy_branches_are_valid_alternatives(self):
        module = load_module()
        self.assertIn("INSTALL_EXISTING", module.ACTION_DISPOSITIONS)
        self.assertIn("REFERENCE_AND_ADAPT", module.ACTION_DISPOSITIONS)
        alternatives = {
            check: {
                "state": "CHECKED",
                "disposition": "REFERENCE_AND_ADAPT" if check == "maintained_candidate" else "USE_EXISTING",
                "reason": "The candidate was inspected against the requested reusable capability.",
                **({"source_role": "DONOR_REFERENCE_ONLY"} if check == "maintained_candidate" else {}),
            }
            for check in module.NECESSITY_CHECKS
        }
        ok, reason = module._necessity_ok(
            {"id": "create-local-upstream", "kind": "CREATE"},
            {"necessity": {"disposition": "REFERENCE_AND_ADAPT", "alternatives": alternatives, "justification": "The baseline was compared before adaptation."}},
        )
        self.assertTrue(ok, reason)

    def test_create_rejects_installable_maintained_candidate(self):
        module = load_module()
        alternatives = {
            check: {
                "state": "CHECKED",
                "disposition": "INSTALL_EXISTING" if check == "maintained_candidate" else "USE_EXISTING",
                "reason": "The candidate was inspected against the requested reusable capability.",
                **({"source_role": "INSTALLABLE_OWNER"} if check == "maintained_candidate" else {}),
            }
            for check in module.NECESSITY_CHECKS
        }
        ok, reason = module._necessity_ok(
            {"id": "create-local-upstream", "kind": "CREATE"},
            {"necessity": {"disposition": "REFERENCE_AND_ADAPT", "alternatives": alternatives, "justification": "The maintained owner satisfies the requested capability."}},
        )
        self.assertFalse(ok)
        self.assertIn("INSTALL", reason)

    def test_artifact_contract_requires_real_change(self):
        module = load_module()
        case = {"id": "update-bounded", "kind": "UPDATE", "artifact": "modified", "artifact_path": "target/SKILL.md"}
        before = {"target/SKILL.md": "old"}
        self.assertEqual(module._artifact_ok(case, before, before)[0], False)
        self.assertEqual(module._artifact_ok(case, before, {"target/SKILL.md": "new"})[0], True)
        self.assertEqual(module._artifact_ok(case, before, {"target/SKILL.md": "new", "extra": "changed"})[0], False)

    def test_necessity_and_coexistence_evidence_are_structured(self):
        module = load_module()
        case = {"id": "create-local-upstream", "kind": "CREATE"}
        weak = {"necessity": {"disposition": "CLONE_AND_ADAPT", "alternatives": {"native": {"state": "CHECKED", "disposition": "REJECT", "reason": "x"}}, "justification": "x"}}
        self.assertFalse(module._necessity_ok(case, weak)[0])
        malformed = {"necessity": {"disposition": {}, "alternatives": {"native": {"state": "NOT_AVAILABLE", "disposition": "REJECT"}}, "justification": "malformed model output"}}
        self.assertFalse(module._necessity_ok(case, malformed)[0])
        strong = {"necessity": {"disposition": "REFERENCE_AND_ADAPT", "alternatives": {"native": {"state": "CHECKED", "disposition": "REJECT", "reason": "Native behavior was inspected and cannot own this reusable workflow."}, "maintained_candidate": {"state": "CHECKED", "disposition": "REFERENCE_AND_ADAPT", "source_role": "DONOR_REFERENCE_ONLY", "reason": "The maintained donor was inspected and is not independently installable."}, "project_or_user_skill": {"state": "NOT_AVAILABLE"}}, "justification": "The donor baseline is the smallest justified reference adaptation."}}
        self.assertTrue(module._necessity_ok(case, strong)[0])
        coexistence = {path: "hash" for path in module.COEXISTENCE_PATHS["audit-overlap"]}
        self.assertFalse(module._recomputed_record({"trace_events": [], "before_snapshot": {".fixture-coexistence": "hash"}, "after_snapshot": {}, "final_report": {}}, {"id": "audit-overlap", "kind": "AUDIT"})["coexistence_fixture"])
        self.assertTrue(module._recomputed_record({"trace_events": [], "before_snapshot": coexistence, "after_snapshot": coexistence, "final_report": {}}, {"id": "audit-overlap", "kind": "AUDIT"})["coexistence_fixture"])

    def test_audit_upstream_drift_uses_update_needed_disposition(self):
        module = load_module()
        case = {"id": "audit-upstream-drift", "kind": "AUDIT"}
        alternatives = {
            name: {
                "state": "CHECKED",
                "disposition": "USE_EXISTING",
                "reason": "checked alternative capability and captured evidence",
            }
            for name in module.NECESSITY_CHECKS
        }
        self.assertTrue(module._necessity_ok(case, {
            "necessity": {
                "disposition": "UPDATE_NEEDED",
                "alternatives": alternatives,
                "justification": "upstream drift requires a later update",
            }
        })[0])

    def test_runtime_preflight_rejects_missing_runtime_without_launching_cases(self):
        module = load_module()
        self.assertEqual(module._runtime_preflight("definitely-not-a-codex-runtime", 1)["status"], "NO_RUNTIME")

    def test_run_rejects_candidate_ref_that_is_not_current_head(self):
        module = load_module()
        cases_path = SCRIPT.parents[1] / "evals" / "cases.yaml"
        report = module.run(
            cases_path,
            SCRIPT.parents[1],
            "definitely-not-a-codex-runtime",
            "gpt-6-luna",
            "medium",
            1,
            None,
            "smoke",
            "HEAD",
            "HEAD~1",
        )
        self.assertEqual(report["runtime_preflight"]["status"], "CANDIDATE_MISMATCH")
        self.assertTrue(all(item["status"] == "NOT_ASSESSED" for item in report["results"]))

    def test_trial_record_validation_rejects_missing_lifecycle_evidence(self):
        module = load_module()
        binding = {"candidate_head": "a" * 40, "skill_tree_sha256": "b" * 64, "cases_sha256": "c" * 64, "base_head": "d" * 40}
        item = {"condition": "with_skill"}
        self.assertFalse(module._trial_record_is_valid(item, binding))

    def test_subprocess_env_strips_inherited_git_routing_state(self):
        module = load_module()
        with patch.dict(module.os.environ, {
            "GIT_DIR": "/tmp/redirected-git",
            "GIT_WORK_TREE": "/tmp/redirected-worktree",
            "GIT_CONFIG_GLOBAL": "/tmp/redirected-config",
        }, clear=False):
            environment = module._subprocess_env()
        self.assertNotIn("GIT_DIR", environment)
        self.assertNotIn("GIT_WORK_TREE", environment)
        self.assertNotIn("GIT_CONFIG_GLOBAL", environment)

    def test_timeout_classes_preserve_auth_transport_turn_and_process_causes(self):
        module = load_module()
        self.assertEqual(module._timeout_class("401 unauthorized"), "AUTH_TIMEOUT")
        self.assertEqual(module._timeout_class("websocket stream disconnected"), "TRANSPORT_TIMEOUT")
        self.assertEqual(module._timeout_class("process did not exit"), "PROCESS_TIMEOUT")
        self.assertEqual(module._timeout_class("model turn still running"), "TURN_TIMEOUT")

    def test_case_owned_gates_include_declared_additional_gates(self):
        module = load_module()
        result = {"condition": "with_skill", "status": "FAIL", "gates": ["G4_BEHAVIOR", "G6_EFFICIENCY"]}
        self.assertEqual(module._case_gate_status([result], "G6_EFFICIENCY"), "FAIL")
        self.assertEqual(module._case_gate_status([result], "G1_STRUCTURE"), "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
