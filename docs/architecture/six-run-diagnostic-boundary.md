# Six-run diagnostic boundary

The authorization record is [six-run-diagnostic-authorization.json](../../candidates/authorization/six-run-diagnostic-authorization.json). Its status is `authorized-in-principle`.

A later Session may run one case from each of the six committed corpus categories, with one repetition, for six runs. The representative case in each category is the minimum `caseId` under the committed manifest sort. This record does not store those case ids. `operationalCaseIds` stays `not-selected`.

The future Session keeps the verified runtime and candidate, the publisher template, the prompt template, the response schema, the greedy-argmax decoding configuration, the hardened execution boundary, the output limits, and gold isolation. It reuses the accepted memory evidence and does not repeat the context-memory measurements. Each run keeps bounded immutable raw output and records extraction, parse, schema, truncation, output-limit, evidence-id, and failure-authority diagnostics.

The diagnostic asks whether schema-invalid candidate output is systematic across categories. It is not a complete corpus evaluation, a percentage-metric result, a promotion-gate attempt, a calibration run, or a candidate-selection run. A later review may call the outcome systematic only when the six-run result is complete, raw output and diagnostics exist for every run, candidate-output authority is proven, and no adapter, protocol, evaluator, output-limit, truncation, or infrastructure defect explains the failures. The numeric threshold for that conclusion stays `deferred-to-future-diagnostic-specification`.

This record does not create a specification, a plan digest, an operator approval, or a result root. `futurePlanDigest` stays `not-issued`. The prerequisites for a later Session are [future-schema-diagnostic-prerequisites.md](../operations/future-schema-diagnostic-prerequisites.md).
