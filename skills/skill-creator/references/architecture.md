# Architecture

Owner: generic target-skill design. Consumers: CREATE and UPDATE. Persistence: workflow design in intent.md, not a second state store. Non-overlap: authoring owns prose/package allocation; qualification owns eligibility.

Define the four views: Skill Architecture, Behavior/Action Logic, Workflow/State Flow, and Artifact Architecture. Check forward and reverse traceability, reachable branches, bounded loops, mutation authority, side effects, and creation/runtime separation.

Classify changes as NON_MATERIAL, MATERIAL_LOCAL, or MATERIAL_ARCHITECTURAL. Material changes include action surface, ownership, state/recovery, mutation boundary, persistent artifacts, dependencies, human authority, or qualification contract. Validate the classification against the impact map and record design invalidation rather than hiding it in a diff.
