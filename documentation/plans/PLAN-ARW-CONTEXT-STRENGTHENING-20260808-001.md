---
id: PLAN-ARW-CONTEXT-STRENGTHENING-20260808-001
title: Context Acquisition v1 Vertical Slice
status: conditional-pass
date: 2026-08-08
issue: 2
scope: global-context-acquisition-vertical-slice
---

# Objective

Prove bounded context acquisition end-to-end before deciding which parts deserve permanent skill/workflow packaging.

Required behavior:

`main detects insufficient context -> bounded acquisition -> compact evidence/context packet -> parent resumes planning`

This PLAN intentionally distinguishes required behavior from candidate implementation.

# Starting state

The reconciled baseline already provides:

- root and scoped guidance;
- bounded runtime adapters including read-only Argus;
- canonical CURRENT/DECISIONS/CLOUD-BRIEF state;
- the task-contract schema;
- existing Franky/shared skills and workflows;
- deterministic control-plane validation.

The current repository does not yet prove that a dedicated `context-strengthening` skill is necessary. That is an implementation hypothesis to test, not a requirement.

## Evidence outcome

Runtime reconnaissance and one bounded Argus comparison are recorded in:

- `ops/changes/2026/CHG-20260809-001/runtime-probe.md`
- `ops/changes/2026/CHG-20260809-001/context-packet.yaml`
- `ops/changes/2026/CHG-20260809-001/task-contract.yaml`

The current evidence supports a conditional pass for the vertical slice and a
no-new-component packaging decision. Direct parent inspection is preferred for
small known scopes; Argus adds value for independent, broad, or relationship-
heavy exploration. The host surface does not expose enough metadata to prove
that the custom `agents/argus.toml` adapter was selected by native delegation,
so that limitation remains explicit.

Athena independently reviewed the slice and returned a conditional pass. The
review findings and evidence-backed corrections are recorded in
`ops/changes/2026/CHG-20260809-001/runtime-probe.md` and
`ops/changes/2026/CHG-20260809-001/validation-output.md`. Issue #2 remains open
and PR #3 remains draft because custom adapter selection is still not
host-observable.

# Runtime reconnaissance first

Before creating new capability files, inspect the actual installed runtime and record:

1. how applicable AGENTS/instructions are discovered;
2. what repository exploration the parent already performs effectively;
3. whether Argus can be invoked with the expected bounded/read-only semantics;
4. what context is inherited versus explicitly supplied to a bounded worker;
5. how skills are currently discovered/selected and what metadata drives routing;
6. which task-contract fields are useful in practice;
7. which existing validators/scripts can be reused;
8. any runtime/config mismatch that would invalidate an architectural assumption.

Do not infer success from configuration text alone.

# Required behavior

## Context sufficiency

The parent must be able to distinguish at least one representative case where existing context is sufficient and one where additional internal context materially improves reliable planning/review.

## Bounded repository acquisition

Retrieve only the applicable instructions, relevant files/relationships, and exact evidence needed by the task. Avoid broad repository/history dumping.

A reusable `repository-exploration` skill is a likely implementation if the probe confirms a stable trigger, procedure, and return contract. Reuse existing capability instead if one already provides equivalent behavior.

## Delegation choice

Compare direct parent inspection with bounded Argus delegation.

Delegate only when:

- the exploration task is independently executable;
- context isolation/parallelism materially helps;
- expected value exceeds delegation overhead.

Argus must remain read-only, non-recursive, and unable to redesign the parent plan or create global rules.

## Context packet

Prefer a compact representation such as:

```yaml
canonical: []
repository_evidence: []
conflicts: []
uncertainties: []
```

A simpler equivalent is acceptable if runtime evidence shows it is easier and equally traceable.

# Packaging decision

After the representative run, classify each candidate behavior:

- **policy/instruction** if it should apply broadly and needs no reusable procedure;
- **skill** if it has a clear trigger, stable input/output, and reusable procedure;
- **script/tool** if the operation is deterministic;
- **workflow** only if real lifecycle/state/gate semantics require it;
- **no new component** if existing behavior is sufficient.

Do not create `context-strengthening` as a standalone skill merely for symmetry. Create it only if the run demonstrates independent reuse value.

# Representative task contract

If delegation is used, include one bounded contract using the existing schema with:

- objective;
- include/exclude scope;
- minimal canonical/supporting context;
- role hint only where useful;
- required capability;
- expected evidence output;
- validation;
- stop conditions.

Do not embed the full parent conversation.

# Expected changed components

Exact files are deliberately not fixed before runtime reconnaissance.

Likely changes may include:

- one repository-exploration capability surface if justified;
- one representative task-contract fixture/example;
- context-packet schema/fixture only if it improves validation;
- deterministic validation additions where justified;
- minimal durable-state updates only after accepted behavior changes.

Any additional workflow, agent, top-level folder, memory integration, research integration, or broad Franky refactor is out of scope.

# Validation plan

Validate:

1. sufficient vs insufficient context decision with representative cases;
2. bounded evidence retrieval and exact paths;
3. task-contract schema if delegation is used;
4. Argus read-only/bounded behavior if Argus is used;
5. context-packet shape/traceability;
6. existing repository validation remains passing;
7. actual runtime/skill-discovery behavior;
8. diff scope and absence of speculative architecture.

Record limitations explicitly.

# Acceptance mapping

| Issue AC | PLAN evidence |
| --- | --- |
| AC-01 | sufficient vs insufficient representative cases |
| AC-02 | bounded repository evidence retrieval |
| AC-03 | compact context packet/example |
| AC-04 | schema-valid task contract when delegation is used |
| AC-05 | Argus boundary evidence when used |
| AC-06 | parent resumes planning/synthesis |
| AC-07 | direct-vs-delegated comparison |
| AC-08 | deterministic validation results |
| AC-09 | runtime reconnaissance/probe record |
| AC-10 | packaging rationale for every new component |
| AC-11 | scoped diff + minimal durable-state updates |

# Failure modes

- Runtime already performs the proposed behavior adequately: prefer no new component and document the finding.
- Argus/runtime controls differ from assumptions: record the mismatch and adapt the smallest viable path.
- Skill routing overlaps with existing skills: reuse/generalize rather than add another wrapper.
- Context packet adds more ceremony than value: simplify the representation.
- Validation cannot prove a runtime semantic deterministically: separate observable evidence from reviewer judgment.

# Review gate

Review against Issue #2, canonical CURRENT/DECISIONS, actual diff, runtime evidence, and validation.

The reviewer must answer:

1. Did context acquisition improve the task?
2. Was delegation useful enough to justify overhead?
3. Did any new skill/workflow actually earn its existence?
4. Did the implementation avoid duplicate existing/official capabilities?
5. Is the resulting path easier to understand and maintain than the pre-change state?

# Definition of done

The slice is complete when the required behavior is demonstrated and the packaging decision is evidence-backed. A valid outcome may include fewer new skills/files than originally expected.
