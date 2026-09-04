# Architecture-preflight retrieval policy

Load a reference only when the accepted Intent contains a matching material
decision and the repository has no canonical pattern that already resolves it.
Retrieve at most two focused references for one preflight. Record each source
path and the decision it informed in the Plan packet.

| Signal | Retrieval focus |
| --- | --- |
| shared interfaces or bounded contexts | software-design/domain boundaries |
| durable state, migration, retries, recovery | data-systems/operations |
| trust boundary, authorization, external input | threat-modeling |
| agent, model, RAG, or tool orchestration | ai-engineering/agent design |

This policy is passive decision support, not a question corpus or a second
planning procedure. If no signal is material, retrieve nothing. Existing
canonical evidence takes precedence over expanding references.
