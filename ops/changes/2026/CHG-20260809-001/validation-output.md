# Validation output

Recorded `2026-08-09T07:55:39Z` UTC during the reconciliation working tree,
with `origin/main` at `07a4de669b2714f799c13e03be635142f1626fd8`.
The preview digest is the SHA-256 of the staged diff excluding the
self-referential `change.yaml` and `audit-record.yaml` envelopes.

All commands below completed successfully:

```text
python3 skills/franky-agent-installer/scripts/validate_agent_toml.py agents/argus.toml
OK agents/argus.toml: argus

python3 skills/franky-maintenance/scripts/validate_audit_record.py ops/changes/2026/CHG-20260809-001/audit-record.yaml
OK ops/changes/2026/CHG-20260809-001/audit-record.yaml: franky.audit

python3 ops/scripts/validate_franky_change_record.py ops/changes/2026/CHG-20260809-001/change.yaml
OK ops/changes/2026/CHG-20260809-001/change.yaml: CHG-20260809-001

python3 ops/scripts/validate_franky_canonical_layout.py .
OK canonical Franky layout

python3 skills/franky-maintenance/scripts/validate_skill_interfaces.py skills
OK skill interfaces

python3 skills/franky-maintenance/scripts/validate_workflow_layout.py workflows/franky
OK workflow layout

python3 skills/franky-workflow-organizer/scripts/validate_workflow.py workflows/franky/franky.yaml
OK workflows/franky/franky.yaml: 9 steps, 18 nested pipelines

python3 skills/franky-maintenance/scripts/validate_git_allowlist.py .
OK git allowlist

git diff --check
OK

python3 -m unittest discover -s skills/franky-maintenance/tests -p 'test_*.py'
...
----------------------------------------------------------------------
Ran 3 tests in 0.021s

OK

python3 -m unittest discover -s skills/franky-workflow-factory/tests -p 'test_*.py'
....
----------------------------------------------------------------------
Ran 4 tests in 0.291s

OK

python3 -m unittest discover -s skills/franky-workflow-organizer/tests -p 'test_*.py'
......
----------------------------------------------------------------------
Ran 6 tests in 0.138s

OK
```

The task contract was checked against every declared schema requirement,
including required fields, nested `scope`/`context` requirements, string
non-empty constraints, array item types, `review.required` boolean,
`review.reason` string, and rejection of undeclared top-level or nested keys:

```text
OK task-contract.yaml: all declared task-contract schema constraints
```

The check is an evidence-run assertion rather than a new runtime component.
The repository does not currently ship a JSON-Schema execution dependency, so
the command validates the concrete schema surface used by this fixture and
records that limitation explicitly.

Independent review result:

```text
Athena: CONDITIONAL-PASS
Scope, validators, and no-new-component decision: pass
Remaining limitation: native custom Argus adapter/model/sandbox selection is not host-observable
```

CI-equivalent control-plane checks also passed:

```text
validate_agent_changelog.py agents: OK (3 changelog entries)
validate_io_cache.py: OK (canonical workflow + 18 nested workflows; no-cache)
validate_audit_record.py audit template: OK
validate_scheduler.py: OK
run_session_inventory.py fixture: OK (failure_file_count=0, correction_file_count=0, unresolved_file_count=0)
validate_git_allowlist.py: OK (185 tracked paths within allowlist)
```
