# Future schema-diagnostic prerequisites

A six-run diagnostic requires a new Session. The in-principle boundary is [six-run-diagnostic-boundary.md](../architecture/six-run-diagnostic-boundary.md).

That Session needs its own specification, its own plan digest, a fresh empty result root, and a new operator approval. It uses the same verified runtime and candidate, the same publisher template, prompt, response schema, decoding configuration, hardened boundary, and output limits. It reuses the accepted memory evidence and does not repeat the 4,096-token or 8,192-token measurements. Gold and evaluator records stay hidden. Raw output retention stays bounded and immutable. The representative case in each corpus category is chosen by the committed minimum-`caseId` rule when that future specification is written.

The Track 9A plan digest and the three earlier measurement plan digests stay consumed. No replacement digest is issued by Track 10. `corpus-continuation-execute` stays outside CI. A diagnostic execute command is not part of this track.

`selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. `installationAuthorized` stays false.
