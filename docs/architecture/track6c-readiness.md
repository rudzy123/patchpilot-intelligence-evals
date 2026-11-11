# Track 6C readiness

Track 6C is a separate decision from Track 6B hardened-boundary readiness. The committed outcome is `not-ready`. The verdict is `TRACK 6C CONTROLLED STAGING NOT READY`.

A ready result would require one qualifying direct ONNX path or an authorized conversion path, resolved tokenizer provenance, no failed `bounded-subprocess-compatibility` criterion on that path, and hardened profile `linux-bwrap-systemd-v1` version `1.0.0`. Installation would still be unauthorized. The committed inputs fail both the direct path and the conversion path. A qualifying direct path would not be blocked by `conversion-not-authorized` alone. No such path is committed.

The committed blockers are `bounded-subprocess-compatibility`, `conversion-not-authorized`, `equivalence-not-measured`, `explicit-weight-use-license`, `no-qualifying-direct-onnx`, `onnx-directory-exceeds-artifact-cap`, `sources-not-independently-eligible`, `tokenizer-provenance`, and `toolchain-not-offline-closed`.

`runtimeInstallationStatus` is `not-installed`. Selection stays `no-selection`. Acquisition stays `not-acquired`. Conversion stays `not-performed`. Execution stays `not-executed`. `realModelExecuted` and `productionReady` stay false. Observed runtime and model digest lists stay empty.

An in-memory check can return ready when every prerequisite is supplied. That check does not change this record. It does not authorize installation, acquisition, conversion, or inference.

The format decision is in [candidate-format-resolution.md](candidate-format-resolution.md). The command is `track6c-readiness-validation`.
