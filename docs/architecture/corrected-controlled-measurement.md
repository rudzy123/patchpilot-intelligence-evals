# Corrected controlled measurement

Track 8B-R1 is a new measurement session. It does not reuse the consumed Track 8B plan. The specification is [intelligence-track-8b-r1.md](../specs/intelligence-track-8b-r1.md). The sealed plan digest is `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b`. The prior plan digest `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2` stays `consumed` and `reusable: false`.

The committed plan file stays `not-executed`. The committed operator approval stays `not-approved`. `measurementAuthorization` stays `not-authorized`. The 2026-11-16 retry stopped with `inference-failure` before CreateSession and before Run. That plan digest is consumed and is not reusable. `replacementPlanDigest` stays `not-issued`. Another real execution requires a new Session or explicitly reviewed retry authority, a new plan digest, a fresh empty result root, and a new operator checkpoint. `installationAuthorized` stays false. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `productionReady` stays false.

## Phase order

Preflight and template compatibility do not call session Run. Every later phase requires the previous record to be `success`.

1. `preflight`
2. `template-compatibility`
3. `one-token-smoke`
4. `short-generation`
5. `context-4096`
6. `context-8192`
7. `corpus-evaluation`

The smoke prompt is `Reply with one token.` and the new-token limit is 1. The short prompt is `Reply with the single word ready.` and the new-token limit is 32. Context phases repeat token id `574` exactly 4,096 times, then exactly 8,192 times, and request one new token. The 8,192-token phase starts only after the 4,096-token record is `success`. The corpus starts only after the 8,192-token record is `success`.

The corpus uses the existing 24 cases, three repetitions, the prompt-template digest `62774d0f8b65c959c5b038911af4293d3d774aae3933f0d7a24064691685250a`, and the existing metrics and gates. Gold stays out of the candidate input. `comparisonWinner` stays null.

## Template compatibility

Compatibility uses the verified publisher template bytes. The template digest is `f05bf4b967dc993bdc7a2fe6e43759ee218eb0eb340d68b063e1c4f8ad148176`. Rendering `synthetic-user` yields `5c61ee0b595fa4c5b295feb233b312c38b779f7840f3f39c82aef51da9061e5d`. The parser in [template-compatibility.md](template-compatibility.md) stays the authority. Spaces around operators do not decide compatibility, and the literal text `messages | length` is not required. The check runs in the parent before any model session and writes a no-Run result. The launcher refuses to start the child until that result is `supported` and the rendered digest matches.

## Memory and limits

The profile is `linux-bwrap-systemd-v1` version `1.0.0`. The result class is `measurement-retry-result`. Cgroup `MemoryMax` is `12884901888`. `MemorySwapMax` is 0. `TasksMax` is 32. `RLIMIT_AS` is `25769803776` and is address space. `MemoryMax` is the resident-memory control. Intra-op threads are 8. Inter-op threads are 1. The sample interval is 100 ms.

Records keep `memory.current`, `memory.peak`, and `memory.events` in separate fields from process RSS, process-tree RSS, and virtual size. Missing or contradictory telemetry, an out-of-memory event, or a peak above `12884901888` stops the current phase and every later phase. `within-ceiling` requires both required context phases, complete noncontradictory peaks at or below that ceiling, no OOM, and successful isolation and cleanup. No completed context phase is `unavailable`. A smoke-scope peak does not establish context-memory eligibility.

Decoding on every generation phase is greedy argmax, temperature 0, top-p 1, top-k 1, repetition penalty 1. Seed support is false. The recorded seed is 0 and is unused.

## What stays outside CI

Repository Contracts runs the retry validators, including the stopped-attempt, defect, corrected-closeout, plan-disposition, and implementation-review records. It does not call Run. `measurement-retry-preflight`, `measurement-retry-execute`, `measurement-retry-smoke`, `measurement-retry-short-generation`, `measurement-retry-context`, and `measurement-retry-corpus` stay out of `.github/workflows/validate.yml`. The runbook is [corrected-measurement-runbook.md](../operations/corrected-measurement-runbook.md).

Hardened inference and the Track 8A offline-load proof share one dependency closure. Approved standard host libraries are mounted read-only and individually. The ELF interpreter stays in the existing hardened execution policy. Provider libraries and broad host library directories stay unmounted.
