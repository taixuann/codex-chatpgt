# Authoring

Owner: bounded package writing and allocation. Consumers: CREATE/UPDATE build
and mutation phases. Persistence: runtime package files only when consumed.
Non-overlap: architecture decides responsibility; validation checks mechanics.

## Semantic spine

Every reusable instruction should make the reader's path explicit:

```text
WHY → WHEN → WHAT → HOW
    → BRANCH / FAILURE
    → OUTPUT / DONE
    → RELATED RESOURCES
```

Put the normal path before exceptions, decision before enumeration, and make
resource routing by `WHEN` explicit. Say whether a script is meant to be run or merely read;
do not hide a required action in a reference file. State consumer/load timing
when a resource is created during authoring but not shipped at runtime. A flat inventory is not a package contract.

## Package conventions

- `SKILL.md` is a discriminating router: describe why the skill applies, its boundaries, and the next workflow/reference to load.
- Workflow docs own ordered decisions, branches, failure handling, terminal output, and related resources.
- Reference docs own reusable contracts and definitions; do not duplicate workflow steps across references.
- Scripts own deterministic mechanics, validation, and machine-readable errors; document invocation and expected outputs.
- Assets/templates exist only with a named consumer and a validation path.
- Eval cases and reports belong to the evaluation surface; creation-only traces and baselines stay outside the runtime package.

Use the following file-format semantics:

| resource | contract |
| --- | --- |
| `SKILL.md` | discriminating router: why/when it applies, boundaries, and the next workflow or reference |
| workflow docs | ordered decisions, normal path, branches, failure handling, terminal output, related resources |
| reference docs | reusable definitions and contracts; no duplicated workflow ownership |
| scripts | executable mechanics, invocation, deterministic validation, and machine-readable errors; say `RUN` or `READ` |
| assets/templates | only with a named consumer, load timing, and validation path |
| eval cases/reports | evaluation inputs and evidence; creation-only traces/baselines remain outside the shipped package |

Before mutation, map each file to behavior, source, consumer, validation,
lifetime, and runtime/creation-only status. Prefer deletion or navigation over
duplicate rules. Do not add placeholders, UI metadata, assets, or abstractions
without a demonstrated consumer.
