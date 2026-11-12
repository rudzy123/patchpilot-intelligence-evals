# Empirical measurement boundary

Track 7B may recommend a later controlled measurement when resident memory or suitability still needs measurement, no capability is unsupported or officially disqualified, storage-only eligibility already passes, hardened execution `linux-bwrap-systemd-v1` `1.0.0` is the accepted profile, the runtime identity is `onnxruntime` `v1.31.1` revision `6af1a932e2286d5c58166085d24c68783033edee`, the adapter identity is `patchpilot-onnxruntime-adapter` `1.0.0`, and the ONNX revision stays `10f72e70abf67ac0fd7ebf15bc5854726891d864`.

The committed outcome is `authorized-with-documented-residuals`. The reason is `measurement-required`. The verdict is `TRACK 8B CONTROLLED MEASUREMENT AUTHORIZED WITH DOCUMENTED RESIDUALS`.

That recommendation does not set `installationAuthorized`. It does not authorize Track 8 acquisition. It does not select the candidate. This session does not install ONNX Runtime, download artifacts, parse a graph, convert, quantize, or execute a model.

## Scope

A future session that uses this recommendation is limited to:

- `fp32-resident-peak-at-4096-tokens`
- `fp32-resident-peak-at-8192-tokens`
- `existing-synthetic-corpus-metrics`

## Stop conditions

Measurement stops on any of these conditions:

- `ceiling-byte-exceeded`
- `official-disqualifier`
- `artifact-identity-drift`
- `graph-or-external-data-mismatch`
- `network-egress`
- `conversion-or-quantization`
- `production-use`

## Residuals

The committed residuals are `resident-upper-bound-unknown`, `safety-margin-unset`, `graph-not-parsed`, `local-digests-empty`, `behavioral-metrics-unmeasured`, `knowledge-task-caveat`, `installation-not-authorized`, and `adapter-executable-state-unavailable`.

Both envelopes stay `unresolved`. Suitability screening stays `eligible-for-controlled-evaluation`. `measurementPerformed` stays false. `selectionOutcome` stays `no-selection`. `weightedScore` stays null. `qualifyingCandidateCount` stays 0. `acquisitionAuthorization` stays `not-authorized`. `productionReady` stays false. `realModelExecuted` stays false. Local digests stay empty.

The record is [controlled-measurement-authorization.json](../../candidates/authorization/controlled-measurement-authorization.json). Readiness is recorded in [track8b-measurement-readiness.md](track8b-measurement-readiness.md).
