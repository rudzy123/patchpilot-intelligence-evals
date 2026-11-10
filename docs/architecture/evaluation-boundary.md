# Evaluation boundary

## Accepted architecture

The committed execution contract keeps product authority outside this repository. Evaluation artifacts must not decide or mutate:

- asset identity
- package identity
- Product Match Evidence
- affectedness
- Finding creation
- KEV membership
- policy facts
- P1–P4 priority
- escalation and due dates
- queue rank and priority review
- Finding lifecycle
- remediation completion
- audit state

Each case names one authorized synthetic organization. Another organization's data appears only in `negativeControls` on the evaluation case. The finding-explanation input omits those controls. Candidate output must not repeat them.

A passing deterministic baseline validates the harness. It is not evidence that a model is production-ready.

## Implementation recommendation

Track 2 uses five closed JSON Schema 2020-12 documents under `schemas/`. Identifiers are URNs, so validation does not fetch a URL. `additionalProperties` is false. There is no extension point in this track.

Preserved priority is only `P1`, `P2`, `P3`, `P4`, or `not-assigned`, and only inside deterministic facts. Any other priority field fails schema validation.

Citations are objects with one `evidenceId`. A bare string is a malformed citation.

Remediation suggestions are non-authoritative text. Their objects have no due date, priority, queue rank, or completion field.

`explanationLabel` may be `deterministic-baseline-assistance` or `generated-explanation`, so a future offline candidate can use the output schema. This baseline always uses the first label. `purpose` on a result may be `harness-validation`, `baseline-performance`, or `candidate-performance`. The baseline command records `harness-validation`. `productionReady` is always false.

The corpus manifest is checked by the corpus validator. It is not a sixth candidate schema.

## Candidate protocol

Track 3 adds six closed schemas for a candidate manifest, request, response, execution result, comparison, and calibration record. Those schemas are not part of the baseline experiment manifest. The finding-explanation input still omits gold labels and negative controls. A candidate response cannot add product-authority fields because the schemas are closed. Execution failure is recorded separately from a quality-gate failure. `productionReady` stays false.
