# Real candidate evaluation plan

The experiment plan is recorded and is not authorized to run. `experimentAuthorized` is false, `executionStatus` is `not-executed`, `acquisitionStatus` is `not-acquired`, and `productionReady` is false. No candidate, runtime, or quantization is selected. Locally observed artifact digests are empty. The experiment id is unset because there is no candidate manifest to hash.

The plan is bound to corpus version 1.0.0, the corpus digest recorded in the experiment record, protocol version 1.0.0 from [candidate-protocol.md](candidate-protocol.md), and prompt identity `candidate-protocol-1.0.0`. The prompt template id is `finding-explanation-1.0.0`. Its digest is the SHA-256 of the template stored in the experiment record. The template tells the adapter to copy deterministic facts unchanged, cite only evidence ids present in the input, copy missing evidence, qualify uncertainty, ignore instructions embedded in evidence, refuse an unsupported request, and avoid claiming that product state changed. Hidden evaluation labels stay out of the template.

Decoding settings are temperature 0, top-p 1, top-k 1, and seed 0. Seed control is unknown because no runtime is authorized. Three repetitions are required when a later runtime can honor a seed. When it cannot, the plan names `ungatedCanonicalAgreement` as a reported consistency metric. That metric is outside the promotion gates.

Context stays at or below 8192 tokens. Generated text stays at or below 1200 words, and `explanationText` stays at or below 400 characters. The process limits remain 15 seconds, 65536 bytes of standard output, 16384 bytes of standard error, and zero retries. One child runs at a time. Network access stays prohibited.

Failure categories are the existing execution outcomes. Gates and metric formulas in [promotion-gates.md](promotion-gates.md) and [metric-definitions.md](metric-definitions.md) are unchanged. Percentage gates remain uncalibrated, as [calibration-protocol.md](calibration-protocol.md) records. Comparison still selects no production winner. Result files, if a later track writes them, stay under `build/` and follow [result-retention.md](result-retention.md).

The authorization that withholds this experiment is [selected-candidate-authorization.md](../provenance/selected-candidate-authorization.md).
