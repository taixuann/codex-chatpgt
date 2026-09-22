# Architecture

Owner: generic target-skill design. Consumers: CREATE and UPDATE. Persistence: workflow design in intent.md, not a second state store. Non-overlap: authoring owns prose/package allocation; qualification owns eligibility.

Define the four views: Skill Architecture, Behavior/Action Logic, Workflow/State Flow, and Artifact Architecture. Check forward and reverse traceability, reachable branches, bounded loops, mutation authority, side effects, and creation/runtime separation.

## Phase Contract

For each phase, record its entry condition, owner, inputs, decision, allowed
mutation, emitted evidence, exit condition, and terminal state. The phase
contract must forward trace Goal → actions → states → material steps → branches and
failures → artifacts → validation → cases → qualification. Reverse-trace every
persistent file, script, template, and eval to the phase and behavior that
consumes it.

Failure is a state, not an exception to the design. Name the failure class,
the preserved evidence, the safe recovery owner, the re-entry phase, and the
authority required to resume. Do not hide invalidated design, dirty overlap,
missing runtime evidence, or blocked cleanup in a successful terminal state.

Recovery must be bounded: freeze the current candidate and raw evidence, repair
at the earliest invalidated owner, invalidate downstream receipts, and re-enter
from the recorded phase. A static walkthrough proves traversability only; it
does not promote a failure or `NOT_ASSESSED` result to PASS.

Classify changes as NON_MATERIAL, MATERIAL_LOCAL, or MATERIAL_ARCHITECTURAL. Material changes include action surface, ownership, state/recovery, mutation boundary, persistent artifacts, dependencies, human authority, or qualification contract. Validate the classification against the impact map and record design invalidation rather than hiding it in a diff.
