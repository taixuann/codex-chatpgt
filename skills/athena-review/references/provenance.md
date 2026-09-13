# G0 provenance

All donors were shallow-cloned on 2026-09-09 and inspected at the exact refs
below. No donor source was copied into this repository.

| repository | ref | license | useful behavior | excess / disposition |
|---|---|---|---|---|
| `lliangcol/agentic-code-review` | `b5a8659bd24b3e3a549d58c06d2af0845c556659` | Apache-2.0 | diff-first review, implementation notes, structured review framing | broad bilingual docs/CLI; `REFERENCE_ONLY`, primary WORK baseline |
| `kadenn/skills` | `8a053b4ff36c0f7798ce06382567d3bd68e8e868` | MIT | `senior-review` cases and clean/security fixtures | large multi-skill catalog; `REFERENCE_ONLY` |
| `repath500/critique-review` | `06054df7d54a5abe5428b898b5130f5d0cefc32f` | MIT | compact critique rubric and explicit review invocation | npm wrapper/UI metadata; `REFERENCE_ONLY` |
| `William-Yeh/common-code-reviewer` | `5ef138d75e18bb66a86f6b44789bf228c10c7904` | Apache-2.0 | rule IDs, severity policy, language-scoped references | broad language/risk catalog; `REFERENCE_ONLY` |
| `Atharva-Kanherkar/review-checkpoint` | `91269d4e3c8f4976390f2241428202fbdfb503c8` | MIT | expectation lock and iterative review checkpoints | Claude-specific PR workflow; `REFERENCE_ONLY` |
| `HaloForgeAI/adac-skills` | `7fe283f28fb6de6bb48d5fc9a470d9e20a0db60a` | Apache-2.0 | acceptance matrix, risk scaling, human gates | general coding method/plugin surface; `REFERENCE_ONLY` |

Adaptation is limited to the smallest shared mechanics: diff-first retrieval,
criterion mapping, stable findings, evidence states, and explicit stop gates.
The local capability is `athena-review` with `mode: work_quality | goal_completion`;
domain is a bounded rubric selector, not another Skill.
