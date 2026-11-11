# Agent rules

These rules bind automated edits in this repository.

- Treat PatchPilot product authority as accepted: this repository cannot decide asset identity, package identity, Product Match Evidence, affectedness, Findings, KEV membership, policy facts, P1–P4, queue rank, remediation completion, or audit state.
- Treat schema field names, metric formulas, and the deterministic baseline as implementation recommendations for harness validation. Do not describe the baseline as a model. Deterministic candidate fixtures are test doubles, not models.
- Do not read or modify the local `patchpilot` or `neural-from-scratch` repositories.
- Do not download a model or add a provider credential.
- Track 5 does not authorize model acquisition, tokenizer acquisition, runtime installation, provider contact, or real-model execution. `acquisitionStatus` stays `not-acquired`, `executionStatus` stays `not-executed`, and `productionReady` stays false.
- Track 6A does not authorize runtime installation, model download, or model execution. The Track 6 acquisition record stays `not-authorized`. `installationAuthorized` stays false.
- Track 6B readiness means the hardened execution boundary is ready for the next controlled architectural Session. It does not authorize runtime installation, model or tokenizer acquisition, model conversion, candidate selection, real inference, evaluation-gate changes, shadow mode, or PatchPilot production composition.
- Track 6C readiness is a separate decision. The recorded outcome is `not-ready`. It does not authorize runtime installation, model or tokenizer acquisition, model conversion, candidate selection, real inference, or PatchPilot production composition.
- Keep corpus records synthetic and Apache-2.0. The provenance sentence in [docs/provenance/initial-corpus-provenance.md](docs/provenance/initial-corpus-provenance.md) stays identical to the corpus manifest.
- Do not log assistance-request text or explanation bodies.
- Do not claim the in-process network hook or the candidate subprocess is an operating-system sandbox. The hardened fixture launcher is a separate bubblewrap and systemd-user-scope boundary. Do not describe seccomp, Podman, Docker, `unshare`, or direct cgroup delegation as enforced. `RLIMIT_AS` is address space. Cgroup `MemoryMax` is the resident-memory control.
- Do not commit, push, tag, or open a pull request unless a person asks for that action.
