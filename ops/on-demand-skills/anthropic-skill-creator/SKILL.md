---
name: anthropic-skill-creator
description: Use when the user explicitly requests the Anthropic skill-creator method, or a Codex skill needs deliberate trigger and outcome evaluation with human-reviewed cases. Do not use for ordinary skill scaffolding, and never run Claude CLI automation from this package.
metadata:
  last_reviewed: 2026-08-11
  review_interval_days: 90
  upstream_repository: anthropics/skills
  upstream_ref: f17010c9bb483898c1d9c9f42dde2b3a98889434
---

# Anthropic skill-creator method for Codex

Use the upstream methodology, not its Claude-specific execution loop. The
immutable upstream source is available explicitly at
`vendor-skills/anthropic/f17010c9bb483898c1d9c9f42dde2b3a98889434/skill-creator`.

The canonical Codex `skill-creator` now contains the adapted evaluation loop
and local helpers. Use this package when the user explicitly wants the
Anthropic methodology called out, or when a deliberate evaluation pass should
be kept separate from ordinary scaffolding.

## Scope

Use this procedure when a proposed or existing Codex skill needs a deliberate
design and evaluation pass. For basic scaffolding, use the bundled
`skill-creator` instead. Do not replace `.system/skill-creator`, invoke
`claude -p`, create `.claude/` files, or claim that a Claude trigger benchmark
proves Codex behavior.

## Procedure

1. Confirm the capability should be a skill rather than a policy, script,
   reference, existing package, plugin, or task contract.
2. Inspect installed and maintained upstream alternatives. Record the selected
   disposition: `USE_EXISTING`, `ADAPT_EXISTING`, `CREATE_LOCAL`,
   `REFERENCE_ONLY`, or `DEFER`.
3. Define a small evaluation set before changing the package:
   - intended direct request;
   - intended indirect request;
   - adjacent request that must not trigger;
   - conflict request where a neighboring skill should win.
4. Keep the package focused: concise routing metadata, progressive disclosure,
   explicit boundaries, deterministic helpers only where they improve
   reliability, and no hidden installation or publication.
5. Validate structural and security requirements with the local quality gate:

   ```text
   python3 skills/control-plane/control-plane-audit/scripts/validate_skill_quality.py <skill-path>
   ```

6. Run a real Codex task and collect raw outcome evidence. Separate static
   package validity from routing behavior and from utility lift versus a
   no-skill baseline.
7. Have the human review material examples before a consequential revision or
   promotion. Mark untested runtime behavior as `NOT_ASSESSED`.

## Reusable upstream material

The upstream package's schemas, evaluator roles, report generator, and
packaging utility may be inspected or adapted only after checking host
compatibility. Its `run_eval.py`, `run_loop.py`, and
`improve_description.py` call Claude Code and are not Codex validators.
