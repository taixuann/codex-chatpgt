# Plan packet contract

Minimal YAML shape:

```yaml
schema_version: 1
kind: plan_packet
source:
  kind: intent_packet       # intent_packet | github_issue
  locator: intent-packet:fixture
  confirmed: true            # required for an intent_packet source
  intent_source:             # required provenance copied from the intent packet
    kind: user               # user | github_issue
    locator: conversation
scenario: planning-and-task-breakdown
subskill: planning-and-task-breakdown
objective: "..."
assumptions: []
dependencies: []
tasks:
  - id: T1
    title: "..."
    acceptance:
      - "..."
    verification:
      - "..."
    depends_on: []
checkpoints:
  - "..."
out_of_scope:
  - "..."
open_questions: []
approved: false
side_effects: none
```

Task IDs must be unique and dependencies must form an acyclic graph.
`--ready-for-build` requires `approved: true` and no open questions. Approval
does not itself authorize code changes; the task contract still governs them.

When `source.kind` is `intent_packet`, the locator must be `conversation` or
`intent-packet:<ref>`, and `confirmed: true` plus the nested
`intent_source` provenance are required. The validator checks that provenance
against the intent source contract. When `source.kind` is `github_issue`, the
locator must use `owner/repo#<number>` or the canonical GitHub Issue URL form.
