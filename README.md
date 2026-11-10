# PatchPilot intelligence evaluations

This repository holds original synthetic evaluation cases, schemas, a deterministic baseline, and an offline harness for future PatchPilot intelligence experiments. It does not decide Product Match Evidence, Findings, KEV membership, affectedness, P1–P4 priority, queue rank, remediation state, or audit records. It does not compose intelligence into PatchPilot.

The package version is `0.0.0`. Nothing here is a release, and a passing baseline is harness validation only.

## Setup

Python 3.12 and uv are required. `uv lock` may download pinned wheels once. Tests and evaluation commands do not contact model hubs or providers.

```text
uv sync --frozen
```

A cold cache may fetch the wheels already named in `uv.lock`. That fetch is environment setup, not evaluation.

## Commands

```text
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
uv run patchpilot-evals --help
uv run patchpilot-evals corpus-validation
uv run patchpilot-evals baseline-evaluation
uv run patchpilot-evals candidate-manifest-validation --manifest candidates/fixtures/conforming/manifest.json
uv run patchpilot-evals candidate-evaluation --manifest candidates/fixtures/conforming/manifest.json --output-dir build/conforming
uv run patchpilot-evals calibration --output-dir build/calibration
uv run patchpilot-evals result-validation --result build/conforming/*/*/candidate-execution-result.json
uv run patchpilot-evals comparison-validation --result build/comparison/comparison-*.json
uv run patchpilot-evals calibration-validation --result build/calibration/*/*/calibration-record.json
uv run patchpilot-evals real-candidate-manifest-validation --manifest candidates/templates/offline-local-model-manifest.json
uv run patchpilot-evals artifact-cache-policy-validation
uv run patchpilot-evals artifact-verification-validation --manifest candidates/templates/model-artifact-verification-template.json
uv run patchpilot-evals runtime-assessment-validation
uv run patchpilot-evals runtime-authorization-validation
uv run patchpilot-evals isolation-profile-validation
uv run patchpilot-evals evidence-closure-validation
uv run patchpilot-evals track6-authorization-validation
uv run patchpilot-evals track5-review-validation
```

`baseline-evaluation` writes a file only when `--output` is a path inside this repository. The result record includes a timestamp, so it is not committed.

Candidate evaluation writes only under the explicit `--output-dir`, at a path derived from the experiment id, and it refuses to replace an existing artifact. `build/` is gitignored. `result-validation`, `comparison-validation`, and `calibration-validation` are the authoritative checks for those three artifacts. A conforming fixture run shows harness behavior on the authorized request. `productionReady` stays false.

[.github/workflows/validate.yml](.github/workflows/validate.yml) runs these checks on pull requests and on pushes to `main`. It uses Python 3.12, uv 0.13.0, and the committed `uv.lock`. Actions are pinned to commit SHAs. The workflow token can read repository contents. It does not use secrets, publish a package, create a release, or deploy.

## Boundaries

- Accepted product authority stays in the separate PatchPilot product. This repository evaluates; it does not override those decisions.
- `neural-from-scratch` is an educational laboratory. This repository does not copy it, import it, or depend on it.
- Corpus records are synthetic. See [docs/architecture/corpus-policy.md](docs/architecture/corpus-policy.md).
- Schemas and the authority split are described in [docs/architecture/evaluation-boundary.md](docs/architecture/evaluation-boundary.md).
- Metrics and gates are described in [docs/architecture/metric-definitions.md](docs/architecture/metric-definitions.md) and [docs/architecture/promotion-gates.md](docs/architecture/promotion-gates.md).
- Provenance is recorded in [docs/provenance/initial-corpus-provenance.md](docs/provenance/initial-corpus-provenance.md) and [docs/provenance/candidate-fixtures.md](docs/provenance/candidate-fixtures.md).
- The candidate protocol, subprocess boundary, calibration record, and result layout are described in [docs/architecture/candidate-protocol.md](docs/architecture/candidate-protocol.md), [docs/architecture/subprocess-isolation.md](docs/architecture/subprocess-isolation.md), [docs/architecture/calibration-protocol.md](docs/architecture/calibration-protocol.md), and [docs/architecture/result-retention.md](docs/architecture/result-retention.md).
- Accidental sensitive data is reported through [SECURITY.md](SECURITY.md).

## Known limits

The network hook patches `socket.socket`, `socket.create_connection`, `socket.getaddrinfo`, and `urllib.request.urlopen` inside this process. It is not an operating-system sandbox. The path check is lexical and does not resolve sibling directories. The environment allowlist binds this package's own reads. Peak memory uses Linux `ru_maxrss` when `resource` is available and is otherwise unmeasured.

## Later track

Intelligence Track 3 adds an offline candidate protocol and deterministic test doubles. It does not select, download, or execute a real model. A later track can evaluate a real offline candidate only after a separate provenance review for anything that is not original work, an operating-system isolation decision, and Principal Architect approval of any gate change. Percentage gates remain uncalibrated. This repository must stay out of PatchPilot production code, CI, and releases until a later accepted decision says otherwise.

Intelligence Track 4 records an accepted no-selection. Review status is `accepted-by-principal-systems-architect` on 2026-11-10. That acceptance covers the no-selection record only. No offline candidate, runtime, or artifact acquisition is authorized. The criteria, hardware envelope, acquisition template, isolation rules, and experiment contract are:

- [docs/architecture/real-candidate-selection.md](docs/architecture/real-candidate-selection.md)
- [docs/architecture/real-candidate-acquisition.md](docs/architecture/real-candidate-acquisition.md)
- [docs/architecture/real-candidate-isolation.md](docs/architecture/real-candidate-isolation.md)
- [docs/architecture/real-candidate-evaluation-plan.md](docs/architecture/real-candidate-evaluation-plan.md)
- [docs/provenance/candidate-shortlist.md](docs/provenance/candidate-shortlist.md)
- [docs/provenance/selected-candidate-authorization.md](docs/provenance/selected-candidate-authorization.md)

Intelligence Track 5 adds the real-candidate boundary. It does not authorize acquisition. Fixture manifests stay deterministic test doubles, with a 15-second timeout, 64 KiB of standard output, and 16 KiB of standard error. The offline-local-model file is an illustration: acquisition stays `not-acquired` and execution stays `not-executed`. Cache roots stay outside this repository. Executable sniffing is not malware detection. Linux resource limits and the Python hooks are not an operating-system sandbox. The runtime decision is no-runtime. The evidence closure keeps no-selection. Track 6 is `not-authorized`. `productionReady` stays false.

The Track 5 implementation review is `accepted-by-principal-systems-architect` on 2026-11-10 by the PatchPilot Principal Systems Architect. That acceptance covers the fail-closed boundary records only. It is recorded in [docs/provenance/track5-implementation-review.md](docs/provenance/track5-implementation-review.md).

- [docs/architecture/real-candidate-boundary.md](docs/architecture/real-candidate-boundary.md)
- [docs/architecture/external-artifact-cache.md](docs/architecture/external-artifact-cache.md)
- [docs/architecture/model-artifact-verification.md](docs/architecture/model-artifact-verification.md)
- [docs/architecture/runtime-selection.md](docs/architecture/runtime-selection.md)
- [docs/provenance/candidate-evidence-closure.md](docs/provenance/candidate-evidence-closure.md)
- [docs/architecture/track6-acquisition-boundary.md](docs/architecture/track6-acquisition-boundary.md)
