# Calibration protocol

Calibration describes how the current gates behave on deterministic fixtures. It does not change invariant gates, percentage thresholds, metric definitions, the corpus taxonomy, or promotion status.

The record is generated from the eight committed test doubles:

- the conforming double uses only the authorized request and is expected to pass the gates that can be decided from that input
- the unsupported-claim, prompt-injection, and cross-tenant doubles are expected to fail one additional intended gate
- the timeout, malformed-output, excessive-output, and nonzero-exit doubles are expected to return those execution categories and leave quality gates unmeasured

Boundary checks call the existing integer formulas. Nineteen of twenty meets 95 percent. Eighteen of nineteen does not. One of fifty meets the 2 percent cap. One of forty-nine does not. A zero denominator stays unmeasured. If those results change, calibration fails closed instead of adopting the new threshold.

The record also lists corpus imbalance, metrics with no promotion threshold, false-positive risk from stdin-only restatement, and false-negative risk from unscored execution output. Expected citations and refusal labels stay out of the request, so those gates are not treated as evidence of label-complete behavior. Proposed adjustments are stored with `adopted: false` and `approvalStatus: not-approved`.

`productionReady` stays false. The record does not authorize a model, a provider, shadow mode, production composition, or a gate change.

A future real offline candidate still needs its own provenance review, an operating-system isolation decision, and Principal Architect approval. Fixture results are not evidence of model quality.
