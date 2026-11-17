# Corpus-only continuation prerequisites

A later Session may run the corpus only after a new specification, a new plan digest, a fresh empty result root, and a new operator checkpoint. Track 9 does not create those artifacts.

The later Session reuses the accepted memory evidence, the verified runtime `v1.31.1`, and the candidate `LiquidAI/LFM2.5-1.2B-Instruct` at FP32. It does not repeat the 4,096-token or 8,192-token measurements. It does not change prompts, the response schema, metrics, or gates. It keeps the hardened boundary and stops at the first memory, network, isolation, output, cleanup, identity, or telemetry failure.

Bounded raw-output retention is specified in [corpus-continuation-boundary.md](../architecture/corpus-continuation-boundary.md). The disposition stays [candidate-disposition-authority.md](../architecture/candidate-disposition-authority.md).

`installationAuthorized` stays false. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false.
