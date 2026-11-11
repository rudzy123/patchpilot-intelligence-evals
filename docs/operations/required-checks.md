# Required checks

The authoritative inventory is [workflow-governance.json](workflow-governance.json). Intended contexts, in order:

1. `Validation / Quality`
2. `Validation / Tests`
3. `Validation / Repository Contracts`
4. `CodeQL / Analyze`
5. `Dependency Review / Dependency Review`

Each name is the workflow `name` plus the job `name`. These strings are intended names. They are not observed GitHub check contexts. `pullRequestObservationStatus` is `not-observed`, and `observedCheckContexts` is empty, until a pull request run emits check runs.

The current ruleset `26864084` requires the context `validate`. On the latest main commit that context matched the check-run `name` `validate`. It was not stored as `validate / validate`. After the new workflows run, read `.check_runs[].name` and use those exact strings in the ruleset. Do not type the slash form into the ruleset unless the API returns it. The procedure is [main-ruleset-procedure.md](main-ruleset-procedure.md).

## Where each check applies

`Validation / Quality`, `Validation / Tests`, and `Validation / Repository Contracts` apply to a pull request targeting `main`, a push to `main`, and `workflow_dispatch`. They are required.

`CodeQL / Analyze` applies to those same events and to the weekly schedule. It is required on the pull request and the push. The schedule is additional evidence. It is not a separate required context.

`Dependency Review / Dependency Review` applies only to a pull request targeting `main`. It is required there. It does not run on a push. The dependency category check still runs on the push because Repository Contracts invokes `dependency-architecture-policy-validation`.

No Track-specific command is its own required check. Those commands stay inside Repository Contracts.

## If a name changes

A job rename changes the check-run name and will block merge once that name is required. To retire a required check:

1. Add the replacement job and let a pull request emit its check-run name.
2. Edit the ruleset so the required contexts are the observed names of the jobs that still exist. Do this in one edit, before removing the old job from the default branch.
3. Merge only after the new required checks are green.
4. Record the observed names in a later reviewed update of the governance record. Do not mark `rulesetApplicationStatus` as applied in the same change that only renames a workflow.

Do not delete the only required check and leave `main` without a status requirement. Do not keep a dummy job named `validate` to satisfy the old ruleset. The operator replaces `validate` after the new names exist.

Layout and coverage are described in [protected-repository-validation.md](../architecture/protected-repository-validation.md). Permissions are described in [github-actions-supply-chain.md](../security/github-actions-supply-chain.md). Pins are described in [github-action-pins.md](../provenance/github-action-pins.md).
