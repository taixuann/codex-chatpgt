# Architecture Delta — Git fact table

The delta diagram is a presentation of the following revision-pinned Git
facts. Every authored component/connection change is tied to a concrete diff
surface; no row is a runtime or mergeability inference.

| Diagram fact | Git evidence (`8ed22d5...` → `042d013...`) | Interpretation boundary |
|---|---|---|
| Argus adapter changed from a broad context compiler to three bounded profiles | `agents/argus.toml:1-62` (adapter description, responsibility, lifecycle, skill policy, return contract) | Contract wording changed; native routing is not observed |
| Three reconnaissance profiles were added | `skills/codebase-reconnaissance/SKILL.md:1-84`, `skills/research-source-discovery/SKILL.md:1-83`, `skills/reference-state-reconnaissance/SKILL.md:1-85`; matching `agents/openai.yaml` files | Added files are capability surfaces; behavior remains NOT_ASSESSED |
| One shared kernel and reference contracts were added | `skills/references/reconnaissance-kernel.md:1-33`, `argus-reference-source-contract.yaml:1-14`, `argus-reference-source-fixtures.yaml:1-29`, `argus-routing-evals.yaml:1-24`, `argus-upstream-adaptation-records.yaml:1-44` | Shared written contracts, not a runtime workflow engine |
| Reference/source validation helpers were added | `skills/references/validate_reconnaissance_kernel.py:1-23`, `validate_reference_source_contract.py:1-16`, `validate_argus_routing_evals.py:1-31` | Deterministic checks only |
| Argus repertoire changed to the three named profiles | `manifests/agent-capability-repertoires.yaml:124-126` | Eligibility metadata, not proof of model-mediated selection |
| Catalog and capability evidence expanded | `manifests/skill-catalog.yaml:30-62`, `:163-186` | Catalog disposition/evidence; no implicit admission claim |
| Shared lifecycle contract was narrowed to the new capability names | `manifests/agent-contracts.yaml:13-15` | Contract alignment only |
| Git allowlist now permits the three profile directories | `.gitignore:37-42`, `skills/control-plane-audit/scripts/validate_git_allowlist.py:30-31` | Repository inclusion boundary only |
| Historical packet validation exception was retained in CI | `.github/workflows/franky-validate.yml:2`, `:141-149` | Historical provenance handling; not part of Argus runtime |
| The delta removes the old broad “Skill surface” and “Shared lifecycle” nodes | No source files were deleted; the semantic removal is represented by the adapter/repertoire/catalog replacements above | Diagram-level simplification, not a claim that Git deleted those files |

The Archify receipt records the corresponding IR summary (four added
components, two removed, one moved; six added connections, two removed) and
the exact base/head SHA-256 inputs. The actual change set remains the Git diff
above.
