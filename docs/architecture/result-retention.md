# Result retention

Candidate artifacts are research records. They are not PatchPilot audit records, Findings, Product Match Evidence, RiskCalculations, or priority reviews.

A complete evaluation writes only when the caller passes an output directory inside this repository. The path is `{output-dir}/{experiment-id}/candidate-execution-result.json`. The experiment id is the SHA-256 of the canonical JSON of protocol version, candidate manifest digest, corpus digest, evaluator version `0.0.0`, and purpose `candidate-performance`. Timestamp, commit, operating system, and Python version are stored on the record and are not part of the id.

The writer refuses to replace an existing result or experiment manifest. A one-case run uses the same experiment id as a complete run of that candidate, so it needs a different output directory if both artifacts must be kept.

The result is canonical JSON. It stores digests, execution categories, metrics, and gate statuses. It does not store the process environment, the assistance request, or the explanation body. `productionReady` is false.

A Track 2 experiment manifest is written beside the result so its digest can be recorded. That manifest uses candidate kind `future-candidate` because the Track 2 schema has no test-double kind. The execution result keeps `deterministic-test-double`.

Comparison requires the same corpus digest, corpus version, and protocol version, and both results must be complete. Otherwise the status is `incomparable` or `missing-result`, the gate list is empty, and no winner is declared. A comparable result still has `winner: null` and `productionReady: false`.

`result-validation` checks a candidate execution result. `comparison-validation` checks a comparison result. `calibration-validation` checks a calibration record. Each command exits 0 for a valid artifact of that kind and exits nonzero for an invalid artifact or a different kind.

Do not commit evaluation artifacts. `build/` is gitignored.
