# Intent packet contract

Minimal YAML shape:

```yaml
schema_version: 1
kind: intent_packet
source:
  kind: user                 # user | github_issue
  locator: conversation
scenario: define-goal        # interview-me | idea-refine | define-goal
subskill: define-goal
objective: "..."
success_criteria:
  - "..."
scope:
  - "..."
out_of_scope:
  - "..."
assumptions: []
open_questions: []
confirmed: false
confidence: 70
side_effects: none
```

`confirmed: true` means the user explicitly accepted the restated intent; it is
not inferred from “sounds good” or silence. `--ready-for-plan` requires
confirmation, at least one success criterion, and no open questions.
