# CREATE workflow

CREATE is a mutating lifecycle, not immediate file generation. It must remain
traceable from the user's repeated capability to a qualified package.

## Intent state

Begin by creating or resuming the Issue/session `intent.md`. Keep it outside
the runtime package. Start with only:

```text
Goal
Done when
Workflow skeleton
```

Progressively enrich each material step with its purpose, input/source,
produced state or artifact, verification, and stop/block condition. Keep the
state vocabulary small: `DISCOVERY`, `DESIGN`, `BUILD`, `PROBE`, `EVALUATE`,
`QUALIFY`, `DONE`, or `BLOCKED`; steps are `pending`, `active`, `done`, or
`blocked`.

## End-to-end phases

| Phase | Produces | Verify | Stop/block |
|---|---|---|---|
| Intake | bound request and intent.md | Issue, repository, CWD, and session match | stale authority or dirty overlap |
| Goal + skeleton | goal, done condition, first workflow | mutation and approval boundaries are visible | materially ambiguous goal |
| Necessity / owner | owner comparison and disposition | native, AGENTS, skill, script/tool, plugin, local, and new-skill options are considered | duplicate or unjustified owner |
| Evidence / anchors | mapped sources and provenance | source/ref/path/license plus adopted and rejected scope | unresolved provenance or license |
| Step enrichment | inspectable workflow steps | purpose, input, output, verify, and block fields are present | unobservable success |
| Build map + cases | justified files and small case corpus | each file/case maps to a workflow need | ceremonial resource or missing boundary case |
| Baseline decision | USE_EXISTING, UPDATE_EXISTING, CLONE_AND_ADAPT, MERGE, LOCALIZE, REJECT, or justified from-scratch decision | maintained baseline copied before adaptation | suitable owner not preserved |
| Implement | minimal package | actual files match build map | unauthorized or out-of-scope mutation |
| Validate + probe | structural receipt and manual observations | links/scripts/side effects and realistic requests are checked | failure requires repair or BLOCKED |
| Evaluate + qualify | case results, limitations, and receipt | PASS/FAIL/NOT_ASSESSED are evidence-backed | required runtime/review evidence unavailable |
| Cleanup + freeze | clean final package and frozen evidence | no scratch, intent, render, or stale artifacts leak | cleanup failure |

Do not force fields onto trivial steps. Do not fabricate unknown detail merely
to fill the brief.

## Required CREATE evidence

Record representative positive, negative, sibling, unsupported, blocked, and
side-effect cases as applicable. Search user, repository, existing-skill,
maintained-upstream, and external sources in that order when material. Prefer
`USE_EXISTING`, `UPDATE_EXISTING`, `CLONE_AND_ADAPT`, `MERGE`, `LOCALIZE`, or
`REJECT` before a from-scratch skill.

After the first viable package, manually probe a few realistic requests before
the initial evaluation. Turn material failures into targeted fixes or
regression cases. The final receipt must explain why the skill exists, why its
owner/location is justified, which anchor was used, what was created/adapted,
which cases ran, what validation/evaluation observed, and what remains
`NOT_ASSESSED`.

Use this reference when a request may justify a new reusable skill. Start with
the capability, not a file.

## Decision sequence

`REQUEST → NECESSITY → DISCOVERY → SOURCE SELECTION → CLONE → BASELINE
REPRODUCTION → ADAPT → DESCRIPTION → STRUCTURE → ROUTING → BEHAVIOR → REVIEW`

1. State the repeated capability and concrete user examples.
2. Check whether the need belongs in `AGENTS.md`, an existing skill, a
   deterministic script, a native Codex feature, or a project-local procedure.
3. Inspect local, project-local, installed/global, and maintained upstream
   candidates. Check equivalence, sibling overlap, composition, ownership, and
   global versus local placement.
4. Prefer `USE_EXISTING`, `UPDATE_EXISTING`, `CLONE_AND_ADAPT`, `MERGE`,
   `LOCALIZE`, `DISABLE_IMPLICIT`, `RETIRE`, or `REJECT` over new content.
5. If a maintained baseline exists, copy it unchanged first, record repository,
   ref, path, license, and hashes, then make the smallest adaptation. Use
   `CREATE_FROM_SCRATCH_WITH_JUSTIFICATION` only when no suitable baseline
   exists and record why.
6. Validate the description, structure, resource necessity, routing, behavior,
   and provenance before asking for independent review.

Project/domain-specific skills default to `<repo>/.agents/skills/`; global
placement needs demonstrated cross-project reuse. Creating a skill is never a
substitute for first checking an existing reference or simpler owner.
