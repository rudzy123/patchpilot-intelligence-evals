# Main ruleset procedure

This procedure updates repository ruleset `26864084`, named `Require validation`, on `rudzy123/patchpilot-intelligence-evals`. An operator performs it. A workflow, a pull request, and this Session must not send the update.

The committed record stays `rulesetApplicationStatus: not-applied` until a later reviewed change records an operator verification. See [workflow-governance.json](workflow-governance.json) and [required-checks.md](required-checks.md).

## Current state

Read this before editing. Classic branch protection is absent. One active ruleset targets `~DEFAULT_BRANCH`. Its bypass list is empty. It requires the status check `validate`, pull requests, conversation resolution, and blocks deletion and force-push. Required approving reviews are 0. Stale-review dismissal is off. Branches are not required to be up to date. `do_not_enforce_on_create` is true. Allowed merge methods are merge, squash, and rebase. Linear history is not required. A merge queue is not enabled.

`main` contains merge commits, and merge commits remain allowed. Do not enable linear history. Do not enable a merge queue. Do not add `merge_group` to a workflow as part of this procedure.

The repository Actions setting allows all actions and does not require SHA pinning at the platform layer. Leave that setting unchanged. Pinning is enforced by `workflow-policy-validation`. The default workflow token permission is read. Leave it unchanged.

Code scanning default setup is `not-configured`. If the CodeQL job later fails because default setup is enabled, stop. Do not add permissions from this procedure.

## Order

The renamed workflow stops reporting the check `validate`. The open hardening pull request will stay blocked on that missing check until this edit replaces it. That block is expected. Do not merge by disabling the ruleset.

1. Open the pull request and wait until Validation, CodeQL, and Dependency Review have completed on it.
2. Read the check-run names. Use those exact strings. Do not assume the slash form.
3. Edit ruleset `26864084` once. Replace `validate`, turn on strict up-to-date, and turn on stale-review dismissal in that same edit.
4. Read the ruleset back.
5. Merge only after every required observed check is green.

## Read-only preflight

```text
gh api repos/rudzy123/patchpilot-intelligence-evals/rulesets/26864084
gh api repos/rudzy123/patchpilot-intelligence-evals/branches/main/protection
gh api repos/rudzy123/patchpilot-intelligence-evals/rules/branches/main
gh api repos/rudzy123/patchpilot-intelligence-evals/commits/COMMIT_SHA/check-runs --jq '.check_runs[].name'
```

`COMMIT_SHA` is the pull request head, or the merge commit the workflow ran, not an older main commit. The checks API for the pre-change main commit still shows `validate`.

Replace `OBSERVED_QUALITY`, `OBSERVED_TESTS`, `OBSERVED_CONTRACTS`, `OBSERVED_CODEQL`, and `OBSERVED_DEPENDENCY_REVIEW` below with those names. The intended names, used only when the API returns them, are `Validation / Quality`, `Validation / Tests`, `Validation / Repository Contracts`, `CodeQL / Analyze`, and `Dependency Review / Dependency Review`.

## GitHub UI

Open the repository Settings, then Rules, then Rulesets, then `Require validation`.

Keep the target on the default branch, enforcement active, and the bypass list empty.

Under pull requests, keep pull requests required, required approving reviews at 0, conversation resolution required, and the extra approval for unattributed changes required. Turn on "Dismiss stale pull request approvals when new commits are pushed". Leave the allowed merge methods as merge, squash, and rebase.

Under required status checks, remove `validate` and add the five observed names. Turn on "Require branches to be up to date before merging". Leave "Do not require status checks on creation" as it is.

Leave deletion blocked and force-push blocked. Do not add a linear-history rule. Do not add a merge queue rule. Do not add a bypass actor. Save the ruleset.

## API example

Do not run this from a workflow or from this Session. An operator may send it after substituting the observed names and reviewing the body against the preflight output.

```text
gh api --method PUT repos/rudzy123/patchpilot-intelligence-evals/rulesets/26864084 --input ruleset.json
```

`ruleset.json` keeps the current rules and changes only the status-check list, `strict_required_status_checks_policy`, and `dismiss_stale_reviews_on_push`:

```json
{
  "name": "Require validation",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
  "bypass_actors": [],
  "rules": [
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": true,
        "required_status_checks": [
          {"context": "OBSERVED_QUALITY", "integration_id": 15368},
          {"context": "OBSERVED_TESTS", "integration_id": 15368},
          {"context": "OBSERVED_CONTRACTS", "integration_id": 15368},
          {"context": "OBSERVED_CODEQL", "integration_id": 15368},
          {"context": "OBSERVED_DEPENDENCY_REVIEW", "integration_id": 15368}
        ]
      }
    },
    {"type": "deletion"},
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "require_extra_approval_for_unattributed_changes": true,
        "required_reviewers": [],
        "allowed_merge_methods": ["merge", "squash", "rebase"]
      }
    },
    {"type": "non_fast_forward"}
  ]
}
```

`integration_id` 15368 is GitHub Actions, which is the integration on the current `validate` check.

## After the edit

```text
gh api repos/rudzy123/patchpilot-intelligence-evals/rulesets/26864084
gh api repos/rudzy123/patchpilot-intelligence-evals/rules/branches/main
```

Confirm enforcement is active, bypass actors are empty, the five observed contexts are required, strict is true, stale dismissal is true, deletion and force-push remain blocked, linear history is absent, and a merge queue is absent. Confirm the pull request's required checks are the green runs just observed. Then merge.

A later reviewed commit may copy the observed names into `observedCheckContexts` and set `rulesetApplicationStatus` to `applied` only after this read-back matches. This procedure does not make that commit.

## Rollback

If the edit was not saved, discard it.

If it was saved and the new workflow files are not on `main`, restore context `validate`, set strict back to false, and set stale dismissal back to false. Leave deletion and force-push blocking in place.

If the new workflow files are already on `main`, do not restore `validate`. That check no longer runs. Correct the contexts to the check-run names from the API. Do not force-push. Do not turn off deletion or force-push protection to unblock a merge.

## Stale or missing checks

Concurrency cancels an older run of the same workflow on the same pull request. Use the latest run. Re-run a failed job from the Actions tab. Do not rerun with a write token or a secret.

If a required context does not match any check-run name, the pull request stays blocked. Update the ruleset to the names the API returned. Do not mark the old context as skipped.

If CodeQL cannot upload because code scanning is unavailable, leave the workflow unchanged and treat the upload failure as an operator platform issue. Do not switch the workflow to `pull_request_target` and do not add `actions: read` or `packages: read` without a new reviewed decision.

The validation design is in [protected-repository-validation.md](../architecture/protected-repository-validation.md). The permission boundary is in [github-actions-supply-chain.md](../security/github-actions-supply-chain.md).
