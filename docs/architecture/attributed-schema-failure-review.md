# Attributed schema-failure review

Track 10 reviews the sealed Track 9A run `case-ground-001-r1`. The record is [attributed-response-evidence.json](../../candidates/authorization/attributed-response-evidence.json).

Raw stdout is 542 bytes, digest `b28e9aa7f5db74d23040d9b3045b5fc927bc2289378bb6bf676e4568ec20b0b9`. The extracted response is 264 bytes, digest `8d5acd633059fd19ea765c0ce415bb37d4f53cc02ed848fcf6df490d55ab9d5d`. UTF-8 extraction and JSON parsing passed. The output was not truncated and stayed within the output limit. Response-schema validation failed. The adapter wrapped the protocol envelope and left the inner keys unchanged. The prompt carried response schema `1.0.0` and the explanation contract. The intended evaluator schemas were applied.

The response-failure authority is `candidate-output`. That evidence class is `candidate-evidence`. The execution stop remains `measurement-infrastructure` with cause `telemetry-unresolved`. That evidence class is `measurement-infrastructure-evidence`. The two authorities stay separate. `candidateMetricsProduced` stays false. `behavioralConclusion` stays `partial-inconclusive`.

The schema-authority record is [schema-invariant-review.json](../../candidates/authorization/schema-invariant-review.json). Response-schema conformance is a per-run validity requirement and a proposed percentage gate, `outputSchemaValidity`, at exactly 100 percent once a complete scored result exists. It is not one of the four invariant gates. The candidate path does not score a schema-invalid run, so this run stays unmeasured. One repetition does not establish repetition consistency. No committed majority threshold exists; threshold selection stays deferred to a future diagnostic specification. One schema-invalid response does not support candidate rejection.

The diagnostic boundary is [six-run-diagnostic-boundary.md](six-run-diagnostic-boundary.md). The proportionality record is [candidate-investment-proportionality.md](candidate-investment-proportionality.md).
