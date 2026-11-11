# Protected repository validation

Repository Hardening 1 makes three workflows the merge and post-merge gates. The machine-readable inventory is [workflow-governance.json](../operations/workflow-governance.json). Action pins are in [github-action-pins.md](../provenance/github-action-pins.md). Permissions and event rules are in [github-actions-supply-chain.md](../security/github-actions-supply-chain.md).

The workflows do not apply branch protection or a repository ruleset. The operator procedure is [main-ruleset-procedure.md](../operations/main-ruleset-procedure.md). Until that procedure is performed, `rulesetApplicationStatus` stays `not-applied` and check contexts stay `not-observed`.

## Workflows

[validate.yml](../../.github/workflows/validate.yml) is named `Validation`. It runs on pull requests that target `main`, on pushes to `main`, and on `workflow_dispatch`. Its jobs are parallel. Each job checks out the repository with `persist-credentials: false`, installs Python 3.12 and uv 0.13.0, and runs `uv sync --frozen` once.

- `Quality` runs formatting, lint, and `mypy`. The timeout is 15 minutes.
- `Tests` runs `pytest` only. The timeout is 30 minutes.
- `Repository Contracts` runs the corpus, baseline, fixture, comparison, calibration, and Track 4 through Track 7 validators that the previous single job ran. The Track 7 commands sit before `workflow-policy-validation` and `dependency-architecture-policy-validation`. The timeout is 30 minutes.

`hardened-fixture-execution` stays out of CI. It is an execution probe, not a committed-record validator. No job uploads evaluation bodies or enables an Actions cache.

[codeql.yml](../../.github/workflows/codeql.yml) is named `CodeQL`. Job `Analyze` uses Python and `build-mode: none`. It also runs on a weekly schedule, Monday 06:17 UTC. The timeout is 30 minutes. There is no matrix, so the job name does not gain a language suffix.

[dependency-review.yml](../../.github/workflows/dependency-review.yml) is named `Dependency Review`. It runs only on pull requests that target `main`. The timeout is 15 minutes. `fail-on-severity: high` fails the job for high and critical advisories. Moderate and low findings stay in the job log for a person to read. License checks are off. This repository does not add a license allow-list or deny-list.

The official Dependency Review action cannot express this repository's prohibited dependency categories. `dependency-architecture-policy-validation` reads `pyproject.toml` and `uv.lock` directly. It runs inside Repository Contracts, including on a push to `main`. The deny list is [dependency-architecture-policy.json](../security/dependency-architecture-policy.json). The current allow list is empty.

## Checks that cannot skip

These workflows have no path filters and no job-level `if`. A pull request to `main` cannot succeed by skipping Quality, Tests, Repository Contracts, CodeQL, or Dependency Review. Dependency Review does not run on a push. That is the event boundary, not a path filter. The category check still runs on the push through Repository Contracts.

A merge queue is not enabled. The workflows do not listen for `merge_group`.

## Intended check names

The intended contexts are listed in [required-checks.md](../operations/required-checks.md). GitHub has not emitted them yet. The current ruleset still requires the check-run name `validate`.
