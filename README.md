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
```

`baseline-evaluation` writes a file only when `--output` is a path inside this repository. The result record includes a timestamp, so it is not committed.

[.github/workflows/validate.yml](.github/workflows/validate.yml) runs these checks on pull requests and on pushes to `main`. It uses Python 3.12, uv 0.13.0, and the committed `uv.lock`. Actions are pinned to commit SHAs. The workflow token can read repository contents. It does not use secrets, publish a package, create a release, or deploy.

## Boundaries

- Accepted product authority stays in the separate PatchPilot product. This repository evaluates; it does not override those decisions.
- `neural-from-scratch` is an educational laboratory. This repository does not copy it, import it, or depend on it.
- Corpus records are synthetic. See [docs/architecture/corpus-policy.md](docs/architecture/corpus-policy.md).
- Schemas and the authority split are described in [docs/architecture/evaluation-boundary.md](docs/architecture/evaluation-boundary.md).
- Metrics and gates are described in [docs/architecture/metric-definitions.md](docs/architecture/metric-definitions.md) and [docs/architecture/promotion-gates.md](docs/architecture/promotion-gates.md).
- Provenance is recorded in [docs/provenance/initial-corpus-provenance.md](docs/provenance/initial-corpus-provenance.md).
- Accidental sensitive data is reported through [SECURITY.md](SECURITY.md).

## Known limits

The network hook patches `socket.socket`, `socket.create_connection`, `socket.getaddrinfo`, and `urllib.request.urlopen` inside this process. It is not an operating-system sandbox. The path check is lexical and does not resolve sibling directories. The environment allowlist binds this package's own reads. Peak memory uses Linux `ru_maxrss` when `resource` is available and is otherwise unmeasured.

## Later track

A later track can add an offline candidate only after a separate provenance review for anything that is not original work. Percentage gates still need calibration. This repository must stay out of PatchPilot production code, CI, and releases until a later accepted decision says otherwise.
