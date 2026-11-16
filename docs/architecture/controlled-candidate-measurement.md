# Controlled candidate measurement

Track 8B measurement is a separate record from Track 8A acquisition. The committed measurement plan file stays `not-executed`. The committed operator approval stays `not-approved`. The 2026-11-16 attempt stopped with `tokenizer-failure` before Run, and that plan digest is consumed and is not reusable. Another Run requires a new plan and a new operator approval. Historical `measurementAuthorization` stays `not-authorized`. `installationAuthorized` stays false. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `productionReady` stays false.

The plan seals the Track 8A runtime and candidate digests, the phase order, the decoding configuration, and the stop conditions. A manual command accepts that plan only when the operator passes its digest. Repository Contracts validates the committed records and does not launch a process.

Phases run only through `linux-bwrap-systemd-v1`. The order is preflight, one-token smoke, short generation, a 4,096-token context, a conditional 8,192-token context, and the existing 24-case protocol. A failed prerequisite withholds every later phase. The 8,192-token phase does not start unless the 4,096-token record passed with complete cgroup telemetry under the resident ceiling.

Decoding is greedy argmax: temperature `0`, top-p `1`, top-k `1`, repetition penalty `1`. Seed support is false. The recorded seed is `0` and is unused. The same settings apply to every repetition. `ungatedCanonicalAgreement` stays outside the promotion gates.

The child is `candidate_inference_main.py`. `offline_load_main.py` stays generation-free. The sandbox loads only the promoted `libonnxruntime.so.1.31.1` through ctypes. API indexes come from the retained header after the archive digest matches. The header is not mounted. Corpus files, gold fields, the home directory, and sibling repositories are not mounted. Network denial remains the bubblewrap network namespace.
