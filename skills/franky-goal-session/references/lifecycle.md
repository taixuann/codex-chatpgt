# Goal/session lifecycle

Every governed Franky run uses these ordered states:

`qualify -> select_role -> load_role_ontology -> draft -> validate -> human_review -> materialize -> execute -> revise`

`human_review` is a blocking approval gate. An unapproved package may be
validated and proposed, but may not authorize configuration, link, destructive,
external, scientific, or publication changes.

An approved `GOAL.md` is stable. A revision copies the package state into
`revisions/REV-<n>.yaml`, records the SHA-256 digest and parent revision, then
advances `revisions/current.yaml`. Existing files are never edited in place by
the revision helper. Routine progress belongs in `TASKS.md` and walkthroughs.

Each workflow run carries `workflow_id`, `workflow_version`, `goal_id`,
`step_id`, `allowed_skill`, `operation`, `input_artifact_ids`, and an
`approval_record`; validate it with `validate_run.py`.
