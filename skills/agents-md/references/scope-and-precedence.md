# Scope and precedence

Start from the real repository root and the intended execution CWD. Confirm
that the CWD is inside the root. Walk from root to CWD and inspect, at each
directory, `AGENTS.override.md` first and `AGENTS.md` otherwise. Record both
the selected source and absent/ignored candidates; do not infer that a file
outside the chain is active.

Fallback filenames are project-chain candidates only. Global guidance uses
only `AGENTS.override.md` / `AGENTS.md`; when fallback names are supplied, the
report records them as `NOT_APPLIED` candidates rather than allowing them to
become global guidance.

For native Codex Skill reachability, walk the same ancestor chain and record
only `.agents/skills/` roots. A package is a native candidate only when its
directory contains `SKILL.md`. The repository's top-level `skills/` tree is a
canonical source/package root for this control-plane; inspect and report it
separately, but do not call it native discovery evidence unless an explicit
installation or runtime binding proves that relationship. Filesystem
reachability is not proof of host selection or loading.

Default placement is root-first:

```text
repo/
├── AGENTS.md
├── .agents/skills/       # native repo Skill discovery
│   └── conditional-workflow/
└── skills/               # repository package/source tree
    └── control-plane-package/
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

The project instruction budget is cumulative across the selected root-to-CWD
project chain, with an assumed default of 32 KiB when the runtime configuration
is not available. Report the global guidance size separately: global guidance
is loaded in its own scope and is not charged against the project budget. If a
configured project limit was not observed, report `configured_limit:
NOT_ASSESSED` and retain the assumed default rather than inventing a configured
value.

When a CWD, override, root marker, or Skill location changes, invalidate the
affected qualification and recompute the chain and discovery fingerprint.
