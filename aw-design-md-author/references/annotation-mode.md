# Annotation Mode

Read when the user explicitly requests deferred DESIGN.md comments. A token, key, reference, theme or formal-prose change uses normative maintenance, even if described as a note.

1. Inspect project instructions, the existing `DESIGN.md`, the owning section, and the implementation evidence behind the note. Preserve the current ownership mode.
2. Create a temporary baseline copy. Add standalone YAML `#` comments immediately before the owning key, or standalone HTML comments before the owning section. The bundled protection gate supports these forms conservatively; it does not treat inline comments or fenced samples as disposable annotation text.
3. Start the note with `TODO(DESIGN):` and make it detailed enough that a future agent can resolve it without reconstructing the current session. Include:
   - the current implementation or observed behavior, with affected surfaces or paths when known;
   - the candidate contract change or question to revisit;
   - the reason and evidence for recording it, plus why the decision is deferred;
   - affected tokens, components, surfaces, themes, and states;
   - unresolved decisions or tradeoffs;
   - the next review action and the criterion for resolving or deleting the TODO.
4. Keep normative YAML unchanged: do not alter exact values, keys, references, theme entries, or prose that changes the contract. Do not edit implementation solely to make the annotation true.
5. Do **not** increment the `DESIGN.md` version for an annotation-only change.
6. Run `scripts/check.sh CURRENT BASELINE --annotation`, then inspect the source diff and TODO adequacy. The gate checks parsed YAML, version and formal text; official diff alone cannot prove comment-only changes. Restore accidental normative edits. Switch to Normative Contract Mode only when that change is authorized by the complete conversation; otherwise keep the TODO deferred.

For a settled contract with pending implementation, label the TODO as implementation migration: record the decided contract/version and mapping, remaining repositories/files, reason for deferral, and acceptance criteria. Do not reopen the design decision or remove the TODO before implementation is verified. Changing the contract itself remains Normative Contract Mode.

Deferred TODOs may accumulate across implementation iterations. At the next normative design-system update, review relevant TODOs, implement already resolved decisions within scope, remove only their annotations, and apply project versioning once for that normative batch. The official `version: alpha` format marker is not a project release version; do not invent a numeric bump for it.


For CLI setup and status interpretation, read [validation guidance](lint-rules.md). For spacing migrations, also read [spacing tiers and migration](authoring-conventions.md#spacing-tiers-and-migration).
