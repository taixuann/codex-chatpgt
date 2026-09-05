# UPDATE

Use this reference for a bounded change to an existing skill. A changed file is
not evidence of an improved skill.

## Validation-gated change

`CURRENT → BASELINE EVAL → CANDIDATE CHANGE → CANDIDATE EVAL → COMPARE →
ACCEPT or REJECT`

- Bind the request to the current skill name, source, ref, license, and
  adaptation boundary.
- Run the baseline cases before a substantive edit and retain the result.
- Change only the smallest instruction, description, reference, or helper that
  addresses the observed problem. Preserve unrelated upstream content.
- Run must-pass, regression, and held-out cases against the candidate.
- Accept only when the candidate is no worse on must-pass/held-out cases, adds
  no critical regression, and any improvement is observable. Otherwise reject
  or revert the candidate.

For a narrow wording change, structural and affected routing checks may be
enough. Do not call a change substantive without fresh comparison evidence.
