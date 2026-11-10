# Real candidate boundary

Track 5 adds one candidate kind, `offline-local-model`, beside the existing `deterministic-test-double` fixtures. The fixture schema, fixture digests, 15-second timeout, 64 KiB standard-output cap, and 16 KiB standard-error cap are unchanged. Fixture validation stays on `candidate-manifest-validation`.

An offline manifest names an official model, a 40-character revision, license and tokenizer URLs, a configuration source, and an expected safetensors inventory. Observed artifacts and locally verified digests are empty. `acquisitionStatus` is `not-acquired`, `executionStatus` is `not-executed`, quantization is `none`, network and remote code are prohibited, telemetry is disabled, and `productionReady` is false. Review status is `not-authorized`. The runtime id on the committed illustration is `none` until a runtime authorization record names an approved runtime. Any other runtime id is rejected.

The committed illustration is [offline-local-model-manifest.json](../../candidates/templates/offline-local-model-manifest.json). Its model id, revision, and `example.invalid` URLs are schema fixtures. They are not a selected candidate and not an upstream commit. `real-candidate-manifest-validation` checks that file. It does not download or execute anything.

Paths, credentials, host names, and IP addresses are rejected. A manifest cannot claim a local digest before acquisition. The external cache and verification rules are separate from this identity record.
