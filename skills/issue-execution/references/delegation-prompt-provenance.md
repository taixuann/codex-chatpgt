# Delegation prompt renderer provenance

This is a selective adaptation of `nidhinjs/prompt-master` at commit
`2bd92518e26bf659e21e3d9ab90573fcf3ddeccb`, whose upstream `SKILL.md` declares
version `1.8.0` and MIT licensing. The inspected donor files were
`SKILL.md`, `references/templates.md`, and `references/patterns.md`.

Retained concepts are contract sections for objective, file scope, starting and
target state, acceptance, validation, return shape, and stop conditions. The
renderer also uses the donor's file-scope, stop-condition, auditable-output,
Template G, Template H, Template M, and relevant agentic-pattern ideas.

The adaptation is deterministic and contract-first. The parent supplies
`agy`, `prometheus`, or the explicit `identity` qualification baseline. The
renderer never chooses an executor, reconstructs memory or conversation
history, asks clarification questions, decomposes tasks, persists prompts, or
requests hidden reasoning. Generic RTF/CO-STAR/RISEN/CRISPE routing, persona
assignment, model recency lookup, and few-shot generation are intentionally
rejected. The renderer is an executor adapter, not a general prompt optimizer.

No substantial upstream prose or template was copied into the repository.
