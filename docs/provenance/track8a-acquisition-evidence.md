# Track 8A acquisition evidence

Principal Architect review on 2026-11-16 accepts the observed Track 8A acquisition. This document records that observation. It does not rewrite the historical pre-Track-8A authorization records. Those records stay `not-authorized` or `not-acquired`, including [track8-acquisition-authorization.json](../../candidates/authorization/track8-acquisition-authorization.json), [track8a-storage-readiness.json](../../candidates/authorization/track8a-storage-readiness.json), and [track8b-readiness.json](../../candidates/authorization/track8b-readiness.json).

The committed plan and allowlist remain preflight records. Their `acquisitionStatus` stays `not-acquired`, and the plan's `operatorApproval` stays `required`. The accepted session approval is recorded here and in the implementation review. Absolute cache roots are not recorded.

The structured evidence is [track8a-acquisition-evidence.json](../../candidates/authorization/track8a-acquisition-evidence.json). Its `identityDigest` is the SHA-256 of the canonical record with that field removed.

## Approval identity

- review date: 2026-11-16
- operator approval: `accepted`
- plan digest: `349c1d666bb4106e284cd0b41f6bac6b4ea65b9d2c5edee8eb358dfc006aec92`
- allowlist digest: `cce59885779e2a0e41761205fde5275df5606bea040fc9366a839017fdf4108e`
- runtime acquisition: `acquired-and-verified`
- candidate acquisition: `acquired-and-verified`
- runtime atomic promotion: passed
- candidate atomic promotion: passed
- copy fallback used: false
- same-filesystem promotion: true
- hardened offline load: passed
- operating-system network denial: passed
- process cleanup: passed
- inference performed: false
- generation performed: false
- corpus executed: false
- long-context measurement performed: false
- `measurementPerformed`: false
- candidate selection: `no-selection`
- calibration `approvalStatus`: `not-approved`
- `realModelExecuted`: false under the committed no-inference semantics
- `productionReady`: false
- Track 8B measurement authorization: `not-authorized`

## Runtime archive

- filename: `onnxruntime-linux-x64-1.31.1.tgz`
- size: 11,413,655 bytes
- SHA-256: `c849e36a1ef3e22d4ff217b9d1ce4a3cf5b9467b975610913ae959ad5b16bdc9`

The archive remains quarantined digest evidence. It is not an execution dependency of the verified library.

## Promoted runtime files

- `libonnxruntime.so.1.31.1`: 29,345,384 bytes, local SHA-256 `a96f132e5eb5ca04e23a7d2fc1078fb95aa591e8d71d0f237702ece3a1e0f4ea`
- `LICENSE`: 1,073 bytes, local SHA-256 `2f07c72751aed99790b8a4869cf2311df85a860b22ded05fa22803587a48922c`
- `ThirdPartyNotices.txt`: 338,088 bytes, local SHA-256 `143764b952fdb1a7c69ce653bfba74a7744d6a8a573bfb73e235fba356c83de3`
- `runtime-identity.json`: 100 bytes, local SHA-256 `7acf64c903f72486d2ae596d4b8343ba03b245155573998e8d4380a23f752028`

## Promoted candidate files

Published ONNX digests match the local SHA-256 values. Files without an authoritative upstream digest still have a local SHA-256.

- `onnx/model.onnx`: 140,810 bytes, `240b836266733940519db3893df325b4cfac8bb87222acbfa0f05dd8c87a6639`
- `onnx/model.onnx_data`: 2,063,007,744 bytes, `04339fb19070d30e0b5523dfecf21b5a469dd3056a43ccd050ce6e756f039ebe`
- `onnx/model.onnx_data_1`: 2,072,240,128 bytes, `cf2d2083fb09ebc8dfcdc46709ed1b9bc978dd7a08a83a6993f30c078b3e6fc5`
- `onnx/model.onnx_data_2`: 578,879,488 bytes, `5817c9c46604164ef96aa9524e34422edc3ffa86e480bafbbcc80de38c0a7759`
- `tokenizer.json`: 3,297,799 bytes, `0a1f2cb9fc2769030ca1f4207e81c1af493319373d41b8d3cf5be53860c13760`
- `config.json`: 1,599 bytes, `dd5d4c6e32a992ad7ddac5c07f5e4711e42c69125f2b94287af7a8ec19963be5`
- `generation_config.json`: 131 bytes, `25f750b7e6a790f86ed01cd6f128f905152cb60bbfe2e6618ceca833b452cf80`
- `tokenizer_config.json`: 2,391 bytes, `0f11f4ffa5750369414bb24e41f26e2bbf23f1d01def533cad5f584e59ae3bef`
- `chat_template.jinja`: 1,783 bytes, `f05bf4b967dc993bdc7a2fe6e43759ee218eb0eb340d68b063e1c4f8ad148176`
- `LICENSE`: 10,596 bytes, `5188f2b355da20647257a3156db5834c794e5fb5e6d8dc4d4cdbb3180e75b85b`
- `README.md`: 6,508 bytes, `262795fd562da67904b5d5c638b15d5ca394053b13dc4d8cda9a372b5798ea14`

## Provider-shared library

`libonnxruntime_providers_shared.so` is not required for the authorized CPU-only path. ONNX Runtime `v1.31.1` compiles the CPU execution provider into the main library. Its Unix build states that `onnxruntime_providers_shared` is not directly linked and is loaded with `RTLD_GLOBAL` for shared providers. The official package import target and pkg-config link line name only `libonnxruntime.so.1.31.1`. The verified library defines `OrtSessionOptionsAppendExecutionProvider_CPU`, and its dynamic needed set does not include the shared provider library. That shared object exports `Provider_GetHost` and `Provider_SetHost`.

The excluded file was 14,632 bytes, local SHA-256 `086ec1d5388f64153d9c63470d126693db9a182c8ce236d3a1119068471b8a0d`. It was not promoted. Both extracted copies were deleted. Track 8B has no transport-attempt library to reach. Run was not called.

## Attempt closeout

Cleanup used the explicit root-confined command. Rejected attempts keep `rejection.json`. Quarantine payload directories were removed. The verified runtime and candidate identities were not deleted. Reclaimed payload bytes are 31,938,441. Every listed attempt has executable eligibility false and verified-state eligibility false.

- `rp-6ae550e563c80876`: rejected promotion, final state `rejection-metadata-retained`, reason `unexpected-file; payload already absent`, cleanup `already-clean`, reclaimed 0 bytes, retained evidence `rejection-record`
- `rp-9e0d257950c038e7`: rejected promotion, final state `rejection-metadata-retained`, reason `missing-file; superseded payload deleted`, cleanup `clean`, reclaimed 29,684,545 bytes, retained evidence `rejection-record`
- `rm-d993520d8fb9c771`: duplicate transport, final state `removed`, reason `superseded duplicate extract deleted`, cleanup `clean`, reclaimed 1,126,948 bytes, retained evidence `none`
- `rm-48372d57a0ec2f91`: empty quarantine, final state `removed`, reason `empty superseded attempt deleted`, cleanup `clean`, reclaimed 0 bytes, retained evidence `none`
- `rm-35b0d6b6e52c93d0`: superseded transport, final state `removed`, reason `excluded unpack members deleted`, cleanup `clean`, reclaimed 1,126,948 bytes, retained evidence `none`

Retained identities:

- `rt-e791f1518ae46ead`: runtime archive, retained, cleanup not authorized, verified-state eligibility false
- `rp-c2fe1c88f694fc1e`: verified runtime, promoted, cleanup not authorized, verified-state eligibility true
- `cd-20b7ceee37a62cba`: verified candidate, promoted, cleanup not authorized, verified-state eligibility true

No acquired artifact is Git-tracked. The acceptance narrative is [track8a-implementation-review.md](track8a-implementation-review.md).
