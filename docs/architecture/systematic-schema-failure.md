# Systematic schema failure

Systematic schema failure is established only when all six diagnostic runs are sealed, at least four of them are schema-invalid with `candidate-output` authority, and those failures span at least three corpus categories.

Every counted failure must also have retained raw output, established extraction, established JSON parse, the intended response schema, no adapter inner-field mutation, no truncation, no output-limit excess, and no blocking infrastructure or security explanation.

The threshold is fixed in the plan before any observation:

- `requiredCompletedRuns`: 6
- `minimumQualifyingFailures`: 4
- `minimumDistinctCategories`: 3
- counted authority: `candidate-output`

Other sealed results use one of these conclusions:

- `systematic-schema-failure-not-established` when all six runs are sealed, there is zero or one qualifying failure, and no content failure stays unresolved.
- `schema-behavior-unreliable-or-unresolved` when all six runs are sealed and the threshold is not met because of two or three qualifying failures, four or more qualifying failures in fewer than three categories, unresolved content authority, or divergent malformed shapes.
- `diagnostic-incomplete` when fewer than six runs are sealed or a blocking infrastructure stop occurs.
- `blocked-by-unresolved-authority` when identity, approval, gold visibility, or another authority stop prevents the conclusion.

A met threshold is not vetoed by divergent response shapes. The shape is recorded as a limitation. The conclusion does not reject or select the candidate, and it does not authorize a 72-run corpus.

Track 11 readiness is advisory. Established systematic failure makes a later disposition review eligible. It does not apply rejection.
