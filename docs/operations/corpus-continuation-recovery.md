# Corpus continuation recovery

A stopped continuation is closed with the stop code, the runs that were sealed, and the runs that were withheld. Missing runs are not imputed. Do not write into a historical Track 8A, Track 8B, Track 8B-R1, or Track 8B-R2 result root.

These stops withhold every later run: approval failure, cleanup failure, template incompatibility, corpus or prompt or response-schema mismatch, digest mismatch, evaluator failure, excessive output, gold visibility, isolation failure, memory above the ceiling, network violation, OOM, a consumed plan, precheck failure, inability to retain raw output, result-root reuse, unresolved telemetry, an unclassified launch, and an unverified dependency.

A malformed or schema-invalid response that is attributed to the candidate is kept as a measured run. The next case may continue. `excessive-output`, a security-boundary exit, and a measurement-infrastructure exit do not continue.

Raw stdout and stderr files stay in place when a later diagnostic seal fails. Recovery does not delete them to make the root look empty. Another real execution needs a new plan digest, a new operator checkpoint, and a fresh empty result root. The three consumed digests stay non-reusable. No R3 digest is issued by this record.

`selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false.
