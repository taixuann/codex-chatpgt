# Source Strategy

Owner: targeted upstream/donor/source decisions. Consumers: INSTALL source resolution, CREATE baseline, and UPDATE only when current external facts are necessary. Persistence: provenance records and intent.md; no copied donor collection. Non-overlap: self history belongs in references/provenance.md.

Use USE_EXISTING, INSTALL_EXISTING, UPDATE_EXISTING, CLONE_AND_ADAPT, REFERENCE_AND_ADAPT, or CREATE_FROM_SCRATCH_WITH_JUSTIFICATION. An installable maintained owner routes to INSTALL_EXISTING; CREATE may use CLONE_AND_ADAPT only for a donor/reference baseline that is not independently installable as the requested target, and REFERENCE_AND_ADAPT is preferred when only concepts or bounded material are reused. For a donor/reference baseline, copy it unchanged first and record repository, ref, path, license, and hashes before adapting it.

The source boundary is therefore: installable owner → INSTALL; donor/reference-only material → CREATE adaptation; no suitable implementation → CREATE_FROM_SCRATCH_WITH_JUSTIFICATION. A maintained source is not automatically a CREATE baseline.

Donor material remains reference-only unless its license, package closure, runtime compatibility, and adaptation boundary support installation. Search only as deeply as an unresolved ownership, compatibility, failure, or qualification decision requires.
