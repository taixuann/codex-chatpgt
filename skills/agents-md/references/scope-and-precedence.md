# Scope and precedence

Start from the real repository root and the intended execution CWD. Confirm
that the CWD is inside the root. Walk from root to CWD and inspect, at each
directory, `AGENTS.override.md` first and `AGENTS.md` otherwise. Record both
the selected source and absent/ignored candidates; do not infer that a file
outside the chain is active.

For Skill reachability, walk the same ancestor chain and record existing
`skills/` and `.agents/skills/` roots. A package is a candidate only when its
directory contains `SKILL.md`. Filesystem reachability is not proof of host
selection or loading.

Default placement is root-first:

```text
repo/
├── AGENTS.md
└── skills/
    └── conditional-workflow/
```

Use a nested AGENTS file only when all are true:

1. the subtree has durable operational divergence;
2. root guidance would be wrong, unsafe, or materially inefficient there;
3. supported execution is launched from or through that subtree;
4. the nested file contains only the delta.

Use a nested Skill root only when the subtree is independently operated, the
launch CWD reaches it, it should remain invisible elsewhere, and that scope
reduces collision/noise compared with precise root metadata.

Same-name Skills are not overrides. If two workflows differ, name them
distinctly; if they are one workflow, keep one Skill with bounded variants.

When a CWD, override, root marker, or Skill location changes, invalidate the
affected qualification and recompute the chain and discovery fingerprint.
