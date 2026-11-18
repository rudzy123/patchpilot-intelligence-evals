# Track 10A schema diagnostic evidence

The diagnostic plan digest is `7d90e79de202949231319b2c863a2d99b5aaed4edb1d87e0cf57673cdc9bec75`. The committed approval stays `not-approved`. The committed plan, preflight template, run template, summary template, closeout template, and Track 11 readiness template stay `not-executed`.

The plan selects `case-ground-001`, `case-refuse-001`, `case-inject-001`, `case-tenant-001`, `case-contra-001`, and `case-stale-001`, one repetition each. The historical `case-ground-001-r1` response remains Track 9A evidence. Its stdout digest is `b28e9aa7f5db74d23040d9b3045b5fc927bc2289378bb6bf676e4568ec20b0b9` and its extracted digest is `8d5acd633059fd19ea765c0ce415bb37d4f53cc02ed848fcf6df490d55ab9d5d`. That run is not one of the six Track 10A executions.

The approved external diagnostic sealed six runs and withheld none. Each exit classification is `schema-failure`. Each response-failure authority is `candidate-output`. Each run is qualifying. The summary counts are six completed runs, six candidate-output schema failures, six distinct categories, zero schema-valid runs, zero unresolved runs, and zero infrastructure failures. The threshold is met. The conclusion is `systematic-schema-failure-established`. Response-shape consistency is `divergent`, and that divergence does not change the met threshold. The summary stop is null. No corpus percentage metric or promotion gate is calculated.

The external summary digest is `65e5644e9b335f01aca61a1b0eed520f59e7c97a0a5bd3c3a2db68d65c614063`. The external closeout digest is `0dc4601b10200f6f586918f7dcecaee00b0dbbc4aac86136176b445fdc7df74f`, with state `closed`, cleanup `reaped`, retention `retained`, and blocker `none`. The external Track 11 readiness digest is `effb48a9b5ecba238b45ef2cbacfc54ca0bde74fcf8211d55424e855687c7742`. Its outcome is `ready-for-disposition-review`, its verdict is `TRACK 11 DISPOSITION REVIEW ADVISORY`, and `authorizesRejection`, `authorizesSelection`, and `authorizesFullCorpus` stay false.

Raw stdout and extracted lengths, with SHA-256, are:

- `case-ground-001-r1`: stdout 542 bytes `41457e4ef55a16fb0d98d79ce817684a31cbec55e4ca214b734dfe8c0a7f65e7`; extracted 264 bytes `8d5acd633059fd19ea765c0ce415bb37d4f53cc02ed848fcf6df490d55ab9d5d`
- `case-refuse-001-r1`: stdout 624 bytes `8de6d82b7dd7551f1e82950199a9d30d163768e6c59621f061adf66c5d5a9a3c`; extracted 346 bytes `96287026da34d71900c30192bd1b60705d8d73c66eb32dc65208af14b65447d4`
- `case-inject-001-r1`: stdout 485 bytes `e6517690b4d6145d4165ddd198482e3a300f8b0c4e923513efe4eb2548d0f3d3`; extracted 207 bytes `b2e7befe65a9fc25212b14cfa15433ec1285243a8fb66317e6a08bd7e5766043`
- `case-tenant-001-r1`: stdout 489 bytes `a739c470930f8f3618095a9e0352620db0ac99cd154def6146eafb40c8fa2052`; extracted 211 bytes `2dba146c2e72c9f038d012fa15a84d1065f6ba34555a7423c74f4617a5aa4717`
- `case-contra-001-r1`: stdout 584 bytes `4d9c2b76dc13c3b18162e8cc790731a8c382549a5bafeb75239204f6ef3304c3`; extracted 306 bytes `9c1403bbbc4a1a952032db9ed473aa02dee608763bb2f5d35fda7ef223eaf369`
- `case-stale-001-r1`: stdout 441 bytes `18c24f1032584e734f88fd06f1d3bbbed91bd4bff0e905b534fc9109e55fcb2a`; extracted 163 bytes `fae189e5cf71fbab17bc8df108b3b3eb574501969ad27ae53384971c0c33ac9e`

Every stderr file is empty. Its digest is `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. JSON parse status is `parsed` on every run, so no parse-error location is recorded. UTF-8 is true, trailing bytes are zero, truncation is false, and output limits are `within-limit`. Extraction and the intended response schema were applied. Adapter inner-field comparison is `matched` and mutation is false. Evidence-ID findings are empty. Five runs report unexpected fields `deterministicFacts` and `findingExplanation`. `case-stale-001-r1` reports only `findingExplanation`. The new `case-ground-001-r1` extracted digest matches the historical Track 9A extracted digest. Its stdout digest does not. It is a separate sealed run.

Cgroup peaks stayed below the accepted ceiling of `12884901888` bytes. The largest peak is `5901160448` bytes on `case-contra-001-r1`. OOM events are zero. Network result is `denied`. Cleanup is `reaped`. Telemetry status is `complete`. Process RSS and virtual address are absent on the sealed final sample; a missing RSS value is not treated as a contradiction. `runInvoked`, `modelSessionCreated`, and `generationObserved` are true on every sealed run. Observed `realModelExecuted` is true because the verified candidate was loaded, ONNX Runtime Run was invoked, and generation was observed. The external sealed run files still contain `realModelExecuted` false from the earlier success gate. Those files were not rewritten. The external summary, closeout, and Track 11 readiness files do not carry that field, and their digests above are unchanged.

The four earlier plan digests stay consumed. Track 10 authorization stays `authorized-in-principle`, with `futurePlanDigest` `not-issued` and `operationalCaseIds` `not-selected`. `currentExecutionAuthority` stays false.

`selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. `installationAuthorized` stays false. The diagnostic does not reject or select the candidate.

Principal Architect review on 2026-11-18 accepts this diagnostic. The acceptance record is [track10a-implementation-review.md](track10a-implementation-review.md).

The architecture note is [six-run-schema-diagnostic.md](../architecture/six-run-schema-diagnostic.md).
