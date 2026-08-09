# Issue #2 runtime probe

## Scope and baseline

The existing `feat/context-strengthening-v1` branch was fast-forwarded from
the remote and rebased onto current `main` at `07a4de6`. The branch now carries
only its two PLAN commits above that baseline. No linked project, credential,
session, cache, or database path was inspected or changed.

Issue #2 and draft PR #3 were read from the public GitHub API. Both require a
behavior-first proof and explicitly allow a no-new-component outcome.

## Representative context-sufficient case

Question: “Does the canonical Franky workflow still satisfy its deterministic
repository contract?”

The parent can answer from the small set:

- `documentation/CURRENT.md`
- `documentation/OPERATING-WORKFLOW.md`
- `.github/workflows/franky-validate.yml`
- `workflows/franky/franky.yaml`
- the existing workflow validator

The direct validator run is sufficient for this known, bounded scope; Argus
delegation would add overhead without useful isolation or parallelism.

## Representative context-insufficient case

Question: “Execute Issue #2 and decide whether a reusable context-acquisition
component is earned.”

`CLOUD-BRIEF.md` alone is insufficient because it still describes the earlier
reconciliation objective. Reliable execution requires the active branch PLAN,
Issue #2 acceptance criteria, draft PR #3 review contract, current branch/base
refs, and the runtime/skill evidence listed in the packet. Acquiring those
specific sources materially changes the plan from “build a skill” to “prove
behavior first.”

## Direct parent versus Argus

The parent performed the focused repository and public-Issue inspection. A
bounded Argus probe independently inspected the same canonical sources and
returned exact paths, conflicts, uncertainties, and a packaging recommendation.

Argus added value for an independent relationship-heavy check, but not for the
small validator lookup. The native delegation surface did not expose the
custom TOML adapter/model/sandbox actually selected, so the probe demonstrates
bounded delegation behavior but cannot prove host-level adapter selection.

The worker made no file changes, did not recurse, and did not widen scope.

## Skill and workflow discovery

No installed package named `repository-exploration` or `context-retrieval` was
found under the repository or personal Codex skill roots. They remain unresolved
`preferred_skills` hints in `agents/argus.toml`. Existing repository validators
already provide deterministic contract checks, and the human-readable general
workflow already defines context sufficiency and conditional Argus routing.

## Packaging decision

**No new skill, workflow, agent, or context-strengthening framework is earned by
this slice.** The stable reusable surface currently consists of the existing
task-contract schema, a compact context-packet shape, and the documented
policy/procedure. Revisit packaging only after repeated runtime tasks show an
independent trigger, stable input/output contract, and reuse benefit.

## Acceptance mapping

| Issue criterion | Evidence |
| --- | --- |
| AC-01 | sufficient and insufficient representative cases above |
| AC-02 | exact canonical/supporting paths in `context-packet.yaml` |
| AC-03 | compact `canonical/repository_evidence/conflicts/uncertainties` packet |
| AC-04 | schema-shaped `task-contract.yaml` |
| AC-05 | `agents/argus.toml` plus bounded probe limitations |
| AC-06 | parent retained planning and synthesis authority |
| AC-07 | conditional direct-versus-delegated comparison |
| AC-08 | repository validators and packet checks listed in the change record |
| AC-09 | local branch/runtime/skill-discovery reconnaissance above |
| AC-10 | no new component; explicit packaging rationale |
| AC-11 | scoped evidence-only diff; no accepted CURRENT/DECISIONS mutation |

## Limitations

This is a conditional pass pending independent review. The host does not expose
enough runtime metadata to verify custom adapter selection, and no live Codex
parent-resume hook was available for automated observation. Those limitations
are evidence gaps, not claims of unsupported behavior.
