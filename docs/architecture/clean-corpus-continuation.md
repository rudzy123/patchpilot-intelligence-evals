# Clean corpus continuation

Track 9A is a separate corpus-only continuation. It cites the Track 9 authorization digest and does not edit that record. `futurePlanDigest` on the authorization stays `not-issued`.

The sealed plan is [corpus-continuation-plan.json](../../candidates/authorization/corpus-continuation-plan.json). The committed approval is [corpus-continuation-approval.json](../../candidates/authorization/corpus-continuation-approval.json). That approval stays `not-approved`. Repository Contracts validates both records and does not call Run.

The continuation runs the 24 synthetic cases in `CASE_IDS` order, three repetitions each, for 72 serial runs and zero retries. It reuses the accepted memory evidence and does not repeat the 4,096-token or 8,192-token measurements. Prompts, response schemas, decoding, metrics, and gates stay unchanged.

The hardened profile is `linux-bwrap-systemd-v1`. `MemoryMax` is the resident ceiling, 12884901888 bytes. `MemorySwapMax` is 0. `TasksMax` is 32. `RLIMIT_AS` is address space, 25769803776 bytes. Wall time is 900 seconds, CPU time is 600 seconds, and the generation budget is 15 seconds. Stdout is bounded at 65536 bytes and stderr at 16384 bytes. Decoding is greedy argmax with temperature 0, top-p 1, top-k 1, repetition penalty 1, and an unused seed 0. The EOS token id is 7.

`selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. `installationAuthorized` stays false.

The advisory Track 10 snapshot is [track10-readiness.json](../../candidates/authorization/track10-readiness.json). That committed snapshot stays `not-executed`. The corpus attempt stopped after one sealed run. The plan digest is consumed and non-reusable, and no replacement digest is issued. Track 10 stays `TRACK 10 CANDIDATE DISPOSITION REVIEW NOT READY`.
