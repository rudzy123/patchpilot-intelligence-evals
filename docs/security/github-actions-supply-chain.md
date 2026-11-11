# GitHub Actions supply chain

Workflows in this repository are read-only except for the CodeQL result upload. They do not use `pull_request_target`, do not receive secrets, and do not persist checkout credentials. Pins and licenses are recorded in [github-action-pins.md](../provenance/github-action-pins.md). The closed record is [workflow-governance.json](../operations/workflow-governance.json).

## Permissions

`Validation` and `Dependency Review` set only `contents: read`.

`CodeQL` sets `contents: read` and `security-events: write`. Official CodeQL guidance requires `security-events: write` so `analyze` can upload results. This repository is public, the workflow does not load a private query pack, and the selected events do not add `packages: read` or `actions: read`. Those scopes are not granted.

No workflow grants `contents: write`, `pull-requests: write`, `issues: write`, `packages: write`, `id-token: write`, or a deployment permission. Dependency Review sets `comment-summary-in-pr: never` so it does not need pull-request write.

A fork pull request runs the workflow from the merge commit in the base repository. The token stays read-only. A fork run does not receive repository secrets. None of these workflows reference the secrets context.

## Concurrency and time limits

Each workflow uses one concurrency group. The group contains the workflow name. A pull request group also contains that pull request's number, and only that pull request's older run is cancelled. A push, a schedule, and `workflow_dispatch` each use a unique run id, so they do not cancel one another or a different pull request.

Job timeouts are 15 minutes for Quality and Dependency Review, and 30 minutes for Tests, Repository Contracts, and CodeQL. A longer timeout needs a new reviewed decision.

## What CI is allowed to download

`astral-sh/setup-uv` downloads the pinned uv release. `uv sync --frozen` installs the locked wheels. CodeQL `init` downloads the official CodeQL bundle for that action commit. Those are the only expected network fetches. The workflows do not pull a container image, upload an artifact, cache dependencies, publish a package, create a release, or deploy.

They do not download a model, tokenizer, converter, or inference runtime, and they do not execute a candidate. `enable-cache` is false and the setup action's GitHub token input is empty.

## Dependency policy

Dependency Review compares the GitHub dependency graph for a pull request. `fail-on-severity: high` treats severity as a threshold, so high and critical advisories fail the check. Moderate and low advisories do not fail it. `fail-on-scopes` includes runtime, development, and unknown. `license-check` is false. There is no license deny-list.

The dependency graph's documented ecosystems do not list `uv.lock`. Advisory coverage of the lockfile is therefore unproven. The official action still runs. The repository-owned check is what reads both `pyproject.toml` and `uv.lock` on every Repository Contracts run. It fails when a normalized distribution name is on the deny list in [dependency-architecture-policy.json](dependency-architecture-policy.json), including the `opentelemetry-` prefix. That list names the model, hub, tokenizer, and runtime distributions `datasets`, `diffusers`, `tokenizers`, `sentencepiece`, `tiktoken`, `torch-geometric`, `torchdata`, and `torchtext`. A prefix shorter than eight characters is rejected, so `torch-` is not a prefix. An allow entry is a normalized name plus a repository-relative Session spec that names that package. The committed allow list is empty.

A package name `onnx` fails the category check. A command name such as `onnx-conversion-plan-validation` is not a distribution name and does not fail it.

## Enforcement

`workflow-policy-validation` parses `.github/workflows` and fails on an unpinned external action, a pin without provenance, a missing or broader permission, a checkout that can persist credentials, a missing or excessive timeout, `pull_request_target`, a path filter, a job or step condition, or `continue-on-error`. It fails on a prohibited download, image pull, container run, runtime install, release-asset download, or publish or deploy action. Before that scan, a backslash immediately followed by LF or CRLF is deleted with the break and no space is inserted. A final backslash with no newline is left unchanged. Ordinary whitespace is not collapsed, so this is not a shell parser: quote splitting, parameter expansion, command substitution, aliases, and encoded payloads stay uninterpreted. The same joined text is scanned for workflow `run` blocks, composite action `run` blocks, and other readable files under a repository-local action. It fails on a `secrets` or `github` token expression, including bracket form. A `./` action is walked in sorted order and every directory is listed. A missing action fails closed. A path that cannot be listed, stat-ed, resolved, or read, a dangling symlink, a symlink that leaves the action root, and a non-UTF-8 file fail as `unreadable-local-action`. A FIFO, device, or other non-regular file fails as `unsupported-local-action-file`. It also fails if the governance record claims that a ruleset was applied or that a check context was observed. This Session has not observed those GitHub results and has not changed repository settings.

Required-check names and the operator procedure are in [required-checks.md](../operations/required-checks.md) and [main-ruleset-procedure.md](../operations/main-ruleset-procedure.md). The validation layout is in [protected-repository-validation.md](../architecture/protected-repository-validation.md).
