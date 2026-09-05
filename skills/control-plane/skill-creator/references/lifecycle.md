# Skill lifecycle modes

Read only for CREATE, UPDATE, MAINTAIN, or EVALUATE work that needs the
corresponding detail. The mode is internal to `skill-creator`; it is not a
separate discoverable skill.

## CREATE

1. State the capability and inspect local, project-local, installed/global,
   and maintained upstream candidates.
2. Check whether `AGENTS.md`, a deterministic script, native model behavior,
   or an existing tool is the simpler owner.
3. Select the smallest disposition: `USE_EXISTING`, `CLONE_AND_ADAPT`,
   `UPDATE_EXISTING`, `LOCALIZE`, `MERGE`, `DISABLE_IMPLICIT`, `RETIRE`, or
   `REJECT`.
4. Use `CREATE_FROM_SCRATCH_WITH_JUSTIFICATION` only after recording why no
   suitable baseline exists.
5. Default project/domain-specific work to `<repo>/.agents/skills/`; global
   placement needs demonstrated cross-project reuse.

## UPDATE

Bind the change to the current skill name and provenance. Make the smallest
instruction or description change, preserve unrelated behavior, rerun the
structural and relevant behavioral/regression cases, and record changed
files. A substantive change requires fresh evidence rather than carrying
forward an old pass.

## MAINTAIN

Inspect upstream drift, local adaptation drift, overlapping skills,
localization needs, and whether the skill still earns global active status.
Use `MERGE`, `LOCALIZE`, `DISABLE_IMPLICIT`, `RETIRE`, or `REJECT` when keeping
the package active is no longer justified. Do not preserve two overlapping
implicitly active skills merely because both are valid in isolation.

## EVALUATE

Separate these gates:

- structure and resource references;
- positive, contextual/noisy, adjacent-negative, and sibling-conflict routing;
- observable CREATE/UPDATE/MAINTAIN/EVALUATE process behavior;
- resource necessity and portability;
- regression and independent review.

Use deterministic checks first. A final artifact that looks good but skipped
a required search, provenance check, placement decision, or regression run
fails behavioral proof. Compare with-skill and no-skill behavior only when the
harness can expose a meaningful difference; do not build a generic evaluator
for a single package.

## Evidence and review boundary

Record the source/ref/license, operation, changed and removed files, case IDs,
commands/results, runtime/model context when available, and explicit
`NOT_ASSESSED` limits. Prepare a bounded packet for Athena when the change is
global, fragile, or consequential. Athena reviews the actual revision and
cannot mutate or accept it. Repair material findings on the same work unit,
rerun affected checks, and obtain a fresh review.

## Side effects and stops

Only mutate authorized skill locations. Do not install dependencies globally,
rewrite `AGENTS.md` to admit a skill, create Issues/PRs without surrounding
authorization, or promote a skill without evidence and review. Stop when
license/provenance is unclear, a baseline is unavailable, a sibling collision
cannot be resolved, or the requested proof needs an unapproved platform.
