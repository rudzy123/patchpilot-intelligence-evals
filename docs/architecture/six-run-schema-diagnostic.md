# Six-run schema diagnostic

Track 10A asks whether schema-invalid candidate output is systematic across the six committed corpus categories. The plan is [schema-diagnostic-plan.json](../../candidates/authorization/schema-diagnostic-plan.json). Its digest is `7d90e79de202949231319b2c863a2d99b5aaed4edb1d87e0cf57673cdc9bec75`.

The diagnostic selects one case from each category, runs that case once, and retains bounded raw output before extraction. It does not rerun the 4,096-token or 8,192-token measurements, qualification smoke, short generation, or the 24-case corpus. It does not calculate percentage metrics or promotion gates.

The committed plan stays `not-executed`. The committed approval stays `not-approved`. `schema-diagnostic-preflight` and `schema-diagnostic-execute` are manual commands. Repository Contracts validates the records and does not call Run.

The external attempt sealed all six planned runs. Each is a qualifying `candidate-output` schema failure. The threshold is met. The conclusion is `systematic-schema-failure-established`. Response shapes are divergent: five runs include unexpected fields `deterministicFacts` and `findingExplanation`, and `case-stale-001-r1` includes only `findingExplanation`. That divergence is a limitation and does not change the met threshold. The evidence note is [track10a-schema-diagnostic-evidence.md](../provenance/track10a-schema-diagnostic-evidence.md).

Principal Architect review on 2026-11-18 accepts that conclusion. The acceptance record is [track10a-implementation-review.md](../provenance/track10a-implementation-review.md). Observed `realModelExecuted` is true when the verified candidate was loaded, ONNX Runtime Run was invoked, and generation was observed. The external sealed files were not rewritten.

`selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. `installationAuthorized` stays false.

The case rule is [diagnostic-case-selection.md](diagnostic-case-selection.md). The threshold is [systematic-schema-failure.md](systematic-schema-failure.md). The operator steps are [schema-diagnostic-runbook.md](../operations/schema-diagnostic-runbook.md).
