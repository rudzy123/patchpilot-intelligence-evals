# Agent rules

These rules bind automated edits in this repository.

- Treat PatchPilot product authority as accepted: this repository cannot decide asset identity, package identity, Product Match Evidence, affectedness, Findings, KEV membership, policy facts, P1–P4, queue rank, remediation completion, or audit state.
- Treat schema field names, metric formulas, and the deterministic baseline as implementation recommendations for harness validation. Do not describe the baseline as a model. Deterministic candidate fixtures are test doubles, not models.
- Do not read or modify the local `patchpilot` or `neural-from-scratch` repositories.
- Do not download a model or add a provider credential.
- Keep corpus records synthetic and Apache-2.0. The provenance sentence in [docs/provenance/initial-corpus-provenance.md](docs/provenance/initial-corpus-provenance.md) stays identical to the corpus manifest.
- Do not log assistance-request text or explanation bodies.
- Do not claim the in-process network hook or the candidate subprocess is an operating-system sandbox.
- Do not commit, push, tag, or open a pull request unless a person asks for that action.
