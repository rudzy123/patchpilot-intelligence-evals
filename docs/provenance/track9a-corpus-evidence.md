# Track 9A corpus evidence

This note records the committed Track 9A plan and the stopped corpus attempt. It does not rewrite the external result files.

The plan digest `6c4a9e6c64a3afe3c1cbb36d19985880beb067fdb9b5634752e8c4d1482560f1` is consumed and non-reusable. No replacement corpus plan digest is issued. The committed plan file stays `not-executed`. The committed approval stays `not-approved`. `corpus-continuation-execute` refuses that digest before Run.

The external attempt stopped after one sealed run. Seventy-two runs were planned, one completed sealed run is retained, and seventy-one runs are missing. They are not imputed. The execution stop authority is `measurement-infrastructure` and the execution stop cause is `telemetry-unresolved`. The retained explanation object is schema-invalid. That response-failure authority is recorded separately and does not replace the execution stop.

The committed Track 10 snapshot stays `not-executed`. The corrected Track 10 reading is `TRACK 10 CANDIDATE DISPOSITION REVIEW NOT READY` with reason `telemetry-unresolved`. Behavioral measurement was attempted and did not complete. The conclusion is `partial-inconclusive`. No candidate metrics were produced.

The stopped-attempt, telemetry-finalization, schema-forensics, interpretation, plan-disposition, proportionality, Track 10, and implementation-review records are under `candidates/authorization/`. Templates for preflight, raw output, diagnostics, runs, the summary, and closeout stay under `candidates/templates/`.

The Track 9 authorization digest remains `e7325c76745505e533afaf12b108470fb6a2a2c765e5f7335b3b1ce1ef6c7477`. That record does not gain a plan digest. The three consumed digests remain non-reusable:

- `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2`
- `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b`
- `2133054bea8db11822cc65f6ea9c45f1ba1500f1aef67d314fbccca764155350`

Accepted memory evidence stays the Track 9 review conclusion `within-ceiling-with-limited-headroom` with ceiling `12884901888`. It is not remeasured here. No runtime, tokenizer, template, or candidate artifact is replaced. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. `installationAuthorized` stays false.
