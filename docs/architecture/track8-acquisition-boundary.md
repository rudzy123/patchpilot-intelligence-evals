# Track 8 acquisition boundary

Track 7 selection is `no-selection`. Track 8 authorization is `not-authorized`, with verdict `TRACK 8 CONTROLLED ACQUISITION NOT AUTHORIZED`.

The finalist `LiquidAI/LFM2.5-1.2B-Instruct` fails `local-resource-fit`. Its weighted score stays null. Explanation suitability is `unresolved` because the card does not state safety limitations, citation-ID behavior, or refusal behavior. An unresolved safety conflict remains. The blocker list is in [track8-acquisition-authorization.json](../../candidates/authorization/track8-acquisition-authorization.json). The selection record is [track7-selection.json](../../candidates/authorization/track7-selection.json).

Authorization leaves these arrays empty:

- locally observed runtime digests
- locally observed model digests
- locally observed tokenizer digests
- locally observed configuration digests

`installationAuthorized` stays false. `conversionAuthorized` stays false. `quantizationApproved` stays false. `runtimeInstallationStatus` stays `not-installed`. `acquisitionStatus` stays `not-acquired`. `conversionStatus` stays `not-performed`. `executionStatus` stays `not-executed`. `realModelExecuted` stays false. `productionReady` stays false.

A later acquisition Session would still need a separate authorization. This record does not acquire, install, convert, quantize, or execute anything. The landscape is described in [candidate-landscape-refresh.md](candidate-landscape-refresh.md).
