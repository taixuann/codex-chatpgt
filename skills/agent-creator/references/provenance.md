# Provenance and disposition

## Primary clone

- repository: `jscraik/Agent-Skills`
- ref: `d00c351fe53460afba860f8cdb1580d7cfece7e4`
- source: `Skills/agent-ops/codex-agent-creator/`
- license: Apache-2.0, copied to `skills/agent-creator/license.txt`
- source commit: `d00c351fe53460afba860f8cdb1580d7cfece7e4`

The unmodified source was fetched and reproduced before adaptation. The source
tree's pinned blob identities were:

```text
SKILL.md e456a55ec17aae2079cc3f6c196f6afc50546aa6
agents/openai.yaml 33eafa9626a86e5a6c149b6ff826689bd7bef458
references/contract.yaml 604ade211cef431e5a49f717a4e6366649523bed
references/discovery-interview.md aca4eb2a346a445826d0c5412dfac37413ddba83
references/evals.yaml 71e97b4b3639b0799d27fb1c0af6e82ae4b3f81b
references/role-config-examples.md 65c986977c07cd8b1afca06b97c3466923c58f1c
references/role-creation-guide.md 671988a141b558e4ecca2afba41e2ca582db1128
references/task-profile.json e88bff5ccf6403c6f73b9e404d3b1d97ebd1bb32
```

## File dispositions

| donor file | disposition | reason |
| --- | --- | --- |
| `SKILL.md` | `CLONE_AND_ADAPT` | retained necessity, role-shell, schema, safety, and validation semantics; removed donor-specific paths and ceremony |
| `references/role-creation-guide.md` | `ADAPT` | reduced to current role ownership, fields, capability, and scope contract as `role-contract.md` |
| `references/role-config-examples.md` | `ADAPT` | kept minimal standalone/project placement examples; removed stale registration assumptions |
| `references/evals.yaml` | `CONSUME_AND_RETIRE` | its old schema was rejected by the accepted skill-creator evaluator; categories informed the bounded qualification cases |
| `references/contract.yaml` | `CONSUME_AND_RETIRE` | no independent consumer after the skill-creator contract became the authority |
| `references/discovery-interview.md` | `CONSUME_AND_RETIRE` | interactive ceremony is not required by this bounded Issue contract |
| `references/task-profile.json` | `CONSUME_AND_RETIRE` | duplicated confidence/timing policy and had no current consumer |
| `agents/openai.yaml` | `REJECT` | no successful current-runtime consumer was demonstrated; native skill loading remains evidence-bound |
| donor repository `LICENSE` | `RETAIN` | Apache-2.0 attribution and redistribution terms |

No reference-only donor content was copied. The exact OpenAI source anchor and
official documentation used for runtime claims are listed in the Issue #105
audit and the final PR evidence.

## Reproduction before adaptation

- repository quick validator on the unmodified donor: `PASS`;
- donor YAML/JSON parse: `PASS`;
- repository eval-contract validation: `FAIL` because the donor corpus uses
  the retired schema and does not declare current gates/origins/lifecycle
  cases;
- executable donor helper surface: none.

The failure is retained as baseline evidence; it is not hidden by relabeling
the adapted corpus as a reproduction pass.
