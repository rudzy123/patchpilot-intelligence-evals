Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Repository Hardening 1: Protected Validation, CodeQL, and Dependency Review

## Identity

- **Repository:** patchpilot-intelligence-evals

- **Session ID:** Repository Hardening 1

- **Mission:** Establish stable, least-privilege, supply-chain-aware GitHub Actions checks for every pull request targeting main and every push to main, then produce an operator-reviewed repository-ruleset procedure that prevents unverified changes from merging.

- **Base commit:** The parent of the spec-only commit introducing this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.

- **Expected repository state:** Intelligence Track 6C merged, protected validation green, working tree clean, no runtime or model artifacts, and all evaluation authorization states remaining fail-closed.

- **Branch:** chore/repository-hardening-1-protected-ci

- **Change type:** GitHub Actions, repository-governance documentation, workflow validation, security policy, and deterministic CI tests. No product, corpus, model, runtime, candidate, or evaluation-authority changes.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** ci: harden protected repository validation

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, merge, modify repository rulesets or branch protection, change GitHub repository settings, create a release, publish a package, install a runtime, download artifacts, or deploy.

## Architectural Outcome

Repository Hardening 1 must establish:

1. One authoritative general validation workflow.

2. Stable check names suitable for repository rules.

3. Pull-request validation before merge.

4. Post-merge validation on the exact main commit.

5. CodeQL analysis for Python.

6. Dependency Review for pull requests that change dependencies.

7. Full-commit-SHA pinning for every third-party action.

8. Least-privilege workflow permissions.

9. Explicit job timeouts.

10. Concurrency cancellation for superseded pull-request runs.

11. No secrets or write credentials in ordinary validation.

12. No model, runtime, tokenizer, converter, or image downloads.

13. No candidate inference or artifact acquisition in CI.

14. A fail-closed prohibited-artifact scan.

15. A documented list of required check names.

16. A read-only assessment of current GitHub repository protection.

17. An operator procedure for applying the main protection rules after the workflows merge.

18. Evidence tying every required check to a workflow and job that cannot silently skip.

The Session implements workflows and documentation.

The Session does not apply GitHub repository settings automatically.

## Governing Authority

Before editing, Cursor must reread:

- every repository [AGENTS.md](http://AGENTS.md);

- [README.md](http://README.md);

- [SECURITY.md](http://SECURITY.md);

- [CONTRIBUTING.md](http://CONTRIBUTING.md);

- LICENSE;

- NOTICE;

- .gitignore;

- pyproject.toml;

- uv.lock;

- every existing workflow under .github/workflows;

- all current architecture and provenance documentation;

- all current Session specifications;

- every existing CLI validation command;

- repository test configuration;

- current Track 2 through Track 6C validators;

- the latest synchronized main workflow results;

- current GitHub branch protection or repository rulesets through read-only GitHub CLI commands;

- official GitHub documentation for actions, CodeQL, Dependency Review, status checks, rulesets, and merge queues where relevant.

Use official GitHub repositories and documentation when resolving action versions and commit SHAs.

Do not inspect or modify patchpilot or neural-from-scratch.

## Invariants

### Evaluation authority remains unchanged

This Session must not change:

- corpus contents;

- corpus digest;

- schemas governing model evaluation outcomes;

- metric definitions;

- promotion gates;

- calibration status;

- candidate selection;

- runtime authorization;

- acquisition authorization;

- conversion authorization;

- execution authorization;

- productionReady.

All current fail-closed states remain authoritative.

### Required checks must be stable

The intended required check names are:

- Validation / Quality

- Validation / Tests

- Validation / Repository Contracts

- CodeQL / Analyze

- Dependency Review / Dependency Review

If GitHub renders a different context name, record the exact observed name after the first pull-request run and use that exact name in the operator ruleset procedure.

Do not make individual Track-specific commands separate required checks.

### Required jobs must not silently skip

Required workflows and required jobs must not use path filters or conditional expressions that allow an applicable pull request to report success without running the required validation.

A command may determine that a control is unsupported only when:

- the repository contract explicitly allows an unsupported result;

- the result is represented in a structured record;

- the job still runs;

- critical unsupported controls preserve a fail-closed readiness outcome.

### Least privilege

Default workflow permissions must be declared explicitly.

General validation requires no write permission and should use:

yaml</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402600000,&quot;dataSource&quot;:0}">permissions:</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402600000,&quot;dataSource&quot;:0}">&nbsp; contents: read</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402600000,&quot;dataSource&quot;:0}">

CodeQL may use only the permissions required for code scanning, normally:

yaml</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402600000,&quot;dataSource&quot;:0}">permissions:</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402600000,&quot;dataSource&quot;:0}">&nbsp; contents: read</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402600000,&quot;dataSource&quot;:0}">&nbsp; security-events: write</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402600000,&quot;dataSource&quot;:0}">

Add packages: read or actions: read only if official CodeQL documentation proves the permission is required for the selected event.

Dependency Review should use read-only repository contents unless an explicitly approved feature requires more.

Do not grant:

- contents: write;

- pull-requests: write;

- issues: write;

- packages: write;

- id-token: write;

- deployment permissions.

### Action integrity

Every external action must be pinned to a full 40-character commit SHA.

For each action, document:

- repository;

- semantic release or tag used for human review;

- exact commit SHA;

- official source;

- retrieval date;

- license;

- purpose.

Do not pin external actions only to:

- main;

- a floating major version;

- a floating tag;

- an unverified fork.

Action updates must remain visible, reviewed dependency changes.

### Workflow supply-chain boundary

Workflows must not:

- execute untrusted pull-request code with repository write permissions;

- use pull_request_target for validation;

- expose secrets to forked pull requests;

- persist checkout credentials;

- download model or tokenizer artifacts;

- download inference runtimes;

- pull container images;

- contact model providers or model hubs;

- upload candidate requests or outputs;

- upload generated model-evaluation artifacts;

- publish packages;

- create releases;

- deploy.

Use persist-credentials: false for checkout.

### Locked dependency execution

General validation must use:

text</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402600000,&quot;dataSource&quot;:0}">uv sync --frozen</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402600000,&quot;dataSource&quot;:0}">

The workflow must not update uv.lock.

No workflow may install undeclared dependencies.

### Post-merge evidence

The general validation and CodeQL workflows must run on:

- pull requests targeting main;

- pushes to main.

Dependency Review may remain pull-request-only because it evaluates dependency changes between base and head.

Post-merge validation must validate the exact commit placed on main.

### Concurrency

Pull-request workflows must cancel superseded runs for the same pull request.

A running workflow for one pull request must not cancel validation for:

- another pull request;

- a push to main;

- a scheduled CodeQL run.

Concurrency groups must include workflow identity and pull-request or commit identity.

### Timeouts

Every job must have an explicit timeout-minutes.

Initial upper bounds:

- Quality: 15 minutes;

- Tests: 30 minutes;

- Repository Contracts: 30 minutes;

- CodeQL: 30 minutes;

- Dependency Review: 15 minutes.

Any larger timeout requires documented evidence.

### Merge queue

Do not enable a merge queue in this Session.

If a merge queue is already enabled, the validation and CodeQL workflows must also support the merge_group event and the Session must document the exact resulting check names.

If no merge queue exists, record it as not enabled and do not broaden scope.

### Branch and ruleset enforcement

Workflow files alone do not constitute merge protection.

This Session must produce an operator procedure describing how to require:

- pull requests before merge;

- required status checks;

- branches up to date before merge, unless a future merge queue replaces that rule;

- conversation resolution;

- stale approval dismissal where supported;

- force-push prevention;

- branch-deletion prevention;

- linear history if the repository consistently uses squash merging;

- minimal or no bypass authority.

Cursor must not apply these settings.

## Assumed Repository State

Before implementation, Cursor must prove:

- repository root is patchpilot-intelligence-evals;

- local main equals origin/main;

- Track 6C is merged;

- spec-only commit parent equals origin/main;

- working tree is clean after the spec commit;

- current protected CI passes on synchronized main;

- existing validation workflow exists;

- current test suite passes;

- current schemas and records validate;

- uv.lock is committed and valid;

- no model or runtime dependency exists;

- no model, tokenizer, ONNX, runtime, wheel, archive, shared library, or container artifact exists;

- calibration remains not-approved;

- candidate selection and acquisition states remain fail-closed;

- no sibling repository is nested in this Git tree;

- no current GitHub workflow has unexpected write permission;

- current branch protection or ruleset state has been inspected read-only.

If a material assumption is false, stop and report the conflict.

## Allowed Change Surface

Permitted:

- docs/specs/[repository-hardening-1.md](http://repository-hardening-1.md);

- .github/workflows/validate.yml;

- one CodeQL workflow;

- one Dependency Review workflow;

- optional workflow-validation scripts or tests;

- repository-governance documentation;

- required-check documentation;

- action-pin provenance records;

- ruleset operator procedure;

- [README.md](http://README.md);

- [SECURITY.md](http://SECURITY.md);

- [CONTRIBUTING.md](http://CONTRIBUTING.md);

- [AGENTS.md](http://AGENTS.md);

- .gitignore only if required for CI-generated local output;

- focused workflow tests;

- pyproject.toml and uv.lock only if an essential workflow-validation dependency is proven necessary and approved.

Not permitted:

- evaluation behavior changes;

- corpus changes;

- schema changes unrelated to repository hardening;

- candidate, runtime, conversion, or acquisition changes;

- dependency upgrades unrelated to CI validation;

- model or runtime downloads;

- project releases;

- deployments;

- automatic GitHub ruleset changes.

## Required Repository Additions

The repository should contain the conceptual equivalent of:

text</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">.github/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">└── workflows/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── validate.yml</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── codeql.yml</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── dependency-review.yml</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">docs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">├── architecture/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [protected-repository-validation.md](http://protected-repository-validation.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">├── security/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [github-actions-supply-chain.md](http://github-actions-supply-chain.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">├── operations/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [required-checks.md](http://required-checks.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [main-ruleset-procedure.md](http://main-ruleset-procedure.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">├── provenance/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [github-action-pins.md](http://github-action-pins.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">└── specs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── [repository-hardening-1.md](http://repository-hardening-1.md)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">tests/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">└── test_[workflows.py](http://workflows.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794402900000,&quot;dataSource&quot;:0}">

Exact paths may follow existing repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create a closed, versioned machine-readable record for workflow governance.

The record must identify:

- workflow IDs;

- workflow file paths;

- stable workflow names;

- stable job names;

- intended check contexts;

- triggers;

- permissions;

- timeouts;

- concurrency behavior;

- action repositories;

- human-readable action versions;

- pinned action SHAs;

- action licenses;

- required or advisory status;

- applicable events;

- ruleset application status;

- manual operator steps.

The record must distinguish:

- workflow implemented;

- workflow observed on a pull request;

- check context observed on GitHub;

- ruleset required-check configuration applied;

- ruleset configuration not yet applied.

Do not claim repository settings were changed unless an operator actually performs and verifies the change.

## Multi-Agent Execution Model

Cursor Plan is the parent repository-hardening orchestrator.

Use Grok 4.7 Extra High for:

- workflow architecture;

- permissions analysis;

- supply-chain decisions;

- required-check design;

- ruleset guidance;

- conflicts;

- independent final verification.

Delegate parallel read-only investigation and controlled implementation to these specialists.

### Agent 1: Existing CI specialist

Owns:

- existing workflow inventory;

- current command coverage;

- current job names;

- current triggers;

- duplication analysis;

- proposed validation-job structure.

### Agent 2: GitHub Actions security specialist

Owns:

- workflow permissions;

- token exposure;

- event safety;

- checkout credentials;

- concurrency;

- timeouts;

- fork safety;

- cache safety;

- artifact-upload restrictions.

### Agent 3: Action provenance specialist

Owns:

- official action repositories;

- release tags;

- full commit SHAs;

- licenses;

- pin provenance;

- update policy.

### Agent 4: CodeQL specialist

Owns:

- Python CodeQL workflow;

- event triggers;

- schedule;

- permissions;

- stable check name;

- query configuration;

- security-event handling.

### Agent 5: Dependency Review specialist

Owns:

- dependency-review workflow;

- severity policy;

- license behavior;

- PR-only behavior;

- stable check name;

- false-positive and failure treatment.

### Agent 6: Ruleset and operations specialist

Owns:

- read-only current-protection inspection;

- required-check names;

- ruleset procedure;

- post-merge verification;

- recovery procedure;

- no-bypass recommendation.

### Agent 7: Independent verification specialist

Runs after implementation.

Must not own:

- validation workflow;

- CodeQL;

- Dependency Review;

- action pins;

- ruleset procedure.

### Coordination Rules

The parent agent must:

- perform read-only investigations in parallel;

- reconcile one workflow architecture before edits;

- preserve existing useful coverage;

- assign exclusive file ownership;

- prevent overlapping workflow edits;

- centralize integration;

- commission one fresh independent reviewer.

## Ordered Execution Plan

### Task 1: Establish Current Repository Protection and CI Baseline

#### Allowed files or subsystem

Read-only Git state, workflows, workflow runs, repository settings, documentation, and tests.

#### Required behavior

Record:

- current workflow files;

- workflow names and job names;

- triggers;

- permissions;

- action pins;

- current validation commands;

- latest passing pull-request runs;

- latest passing main runs;

- current branch protection;

- current rulesets;

- merge-queue status;

- missing checks;

- duplicate or obsolete commands.

Use read-only GitHub CLI and API calls.

#### Tests

Run existing workflow validation and repository tests as needed.

#### Done condition

The exact current state is known and the required-change boundary is assigned.

### Task 2: Rationalize the General Validation Workflow

#### Allowed files or subsystem

.github/workflows/validate.yml, workflow tests, and validation documentation.

#### Required behavior

Implement stable jobs:

1. Quality

2. Tests

3. Repository Contracts

Requirements:

- workflow name Validation;

- pull requests targeting main;

- pushes to main;

- workflow_dispatch for operator diagnostics;

- merge_group only if the repository already uses a merge queue;

- full-SHA-pinned actions;

- persist-credentials: false;

- least-privilege permissions;

- explicit timeouts;

- concurrency with safe cancellation;

- Python 3.12;

- frozen uv synchronization;

- no path filter that can skip a required job;

- no model or runtime download;

- no artifact upload containing evaluation bodies.

Repository Contracts must run all current authoritative repository validators, including all merged Track validators.

Do not duplicate the same expensive command across jobs without justification.

#### Tests

Validate YAML, action pins, permissions, triggers, stable names, timeouts, concurrency, and command coverage.

#### Done condition

One authoritative validation workflow covers all ordinary merge gates.

### Task 3: Add CodeQL

#### Allowed files or subsystem

CodeQL workflow, provenance record, workflow tests, and security documentation.

#### Required behavior

Add Python CodeQL using official GitHub actions.

Triggers:

- pull request targeting main;

- push to main;

- weekly schedule;

- workflow_dispatch;

- merge_group only if merge queue is enabled.

Requirements:

- workflow name CodeQL;

- job name Analyze;

- full-SHA-pinned CodeQL actions;

- least-privilege permissions;

- Python only;

- explicit timeout;

- safe concurrency;

- no model downloads;

- no package publication;

- no deployment.

Do not use autobuild when explicit project setup is more reliable, unless official analysis proves autobuild is appropriate for this repository.

#### Tests

Validate workflow structure, permissions, action pins, languages, triggers, and stable check context.

#### Done condition

Python security analysis is reproducible and independently enforceable.

### Task 4: Add Dependency Review

#### Allowed files or subsystem

Dependency Review workflow, policy documentation, provenance record, and tests.

#### Required behavior

Add official GitHub Dependency Review for pull requests targeting main.

Requirements:

- workflow name Dependency Review;

- job name Dependency Review;

- PR-only;

- contents read permission;

- full-SHA-pinned action;

- fail on high and critical vulnerabilities;

- document moderate findings for manual review;

- do not introduce an unreviewed broad license deny-list;

- fail or stop for any newly introduced model framework, inference runtime, provider SDK, model-hub SDK, conversion framework, vector database, or telemetry SDK unless authorized by a committed Session specification;

- explicit timeout;

- safe concurrency.

If the official action cannot enforce the project-specific dependency categories directly, preserve the official action and add a repository-owned deterministic dependency-policy check in Repository Contracts.

#### Tests

Validate permissions, triggers, severity policy, action pins, and repository dependency-policy behavior.

#### Done condition

Dependency changes receive an explicit security and architecture gate before merge.

### Task 5: Add Action-Pin and Workflow-Policy Validation

#### Allowed files or subsystem

Repository-owned validation code, CLI or test integration, documentation, and focused tests.

#### Required behavior

Fail validation when:

- an external action is not pinned to a full SHA;

- workflow permissions are absent or broader than allowed;

- checkout persists credentials;

- a job lacks a timeout;

- pull_request_target appears;

- a required workflow uses unsafe path filtering;

- a workflow downloads prohibited model or runtime artifacts;

- a workflow publishes or deploys without authority;

- an action pin lacks provenance.

 

The check must distinguish:

- GitHub-authored actions;

- repository-local actions;

- external third-party actions.

#### Tests

Use synthetic valid and invalid workflow fixtures.

#### Done condition

Workflow security conventions are mechanically enforced.

### Task 6: Document and Validate Required Check Names

#### Allowed files or subsystem

Required-check documentation, governance record, CLI/API read-only inspection, and tests.

#### Required behavior

Document intended contexts:

- Validation / Quality

- Validation / Tests

- Validation / Repository Contracts

- CodeQL / Analyze

- Dependency Review / Dependency Review

After the first PR run, record observed contexts separately.

Do not claim contexts were observed before GitHub emits them.

Document:

- PR applicability;

- push applicability;

- scheduled applicability;

- required versus advisory status;

- what to do if a check name changes;

- how to retire a required check safely.

#### Tests

Validate uniqueness, stability, and workflow-to-check mapping.

#### Done condition

The repository has one authoritative inventory of protected checks.

### Task 7: Create the main Ruleset Operator Procedure

#### Allowed files or subsystem

Operations documentation, governance record, and read-only GitHub inspection.

#### Required behavior

Create an operator procedure for configuring main with:

- pull requests required;

- required status checks;

- branch up-to-date requirement unless merge queue is intentionally enabled later;

- conversation resolution;

- stale approval dismissal where supported;

- force-push blocking;

- branch-deletion blocking;

- linear history if compatible with current merge policy;

- bypass restricted to recovery;

- required checks tied to observed contexts.

Include:

- read-only preflight commands;

- GitHub UI steps;

- optional reviewed gh api examples;

- rollback procedure;

- stale-check recovery;

- post-configuration verification.

Do not apply the ruleset automatically.

#### Tests

Validate documentation links, context names, and governance-record consistency.

#### Done condition

The operator can apply protection without making another architectural decision.

### Task 8: Complete Verification and Independent Review

#### Allowed files or subsystem

Complete diff, all workflows, governance records, documentation, and tests.

#### Required behavior

Run the full local repository suite plus workflow-policy tests.

A fresh independent agent must verify:

- no current validation coverage was lost;

- all external actions are SHA-pinned;

- permissions are least privilege;

- required jobs cannot silently skip;

- CodeQL is correctly scoped;

- Dependency Review is PR-only;

- no model or runtime downloads were added;

- stable check names are documented;

- repository settings were not changed;

- no candidate or evaluation decision changed;

- post-merge validation remains enabled.

#### Tests

Run every command in Verification.

#### Done condition

Repository hardening is implementation-complete and ready for Principal Architect review.

## Out of Scope

Repository Hardening 1 must not:

- modify candidate eligibility;

- change model, tokenizer, runtime, conversion, or acquisition decisions;

- modify the corpus;

- modify evaluation metrics or gates;

- download artifacts;

- install runtimes;

- execute inference;

- add deployment workflows;

- add release workflows;

- add model-evaluation schedules;

- add container builds;

- add artifact uploads containing prompts or outputs;

- modify sibling repositories;

- automatically modify GitHub rulesets or branch protection;

- enable a merge queue;

- publish packages;

- create releases;

- deploy.

## Stop Conditions

Stop and report if:

1. The spec-only commit parent differs from origin/main.

2. The working tree contains unrelated changes.

3. Track 6C is not merged.

4. Existing protected validation is failing on main.

5. A workflow must expose a secret to pull-request code.

6. Required validation needs pull_request_target.

7. An external action cannot be pinned to an official immutable SHA.

8. CodeQL requires unsupported or excessive permissions.

9. Dependency Review requires an unapproved license policy.

10. A required job can only work by silently skipping relevant PRs.

11. Repository settings must be changed automatically.

12. A model or runtime download is proposed.

13. Existing evaluation authority would change.

14. Work cannot fit in one pull-request-sized branch.

On a stop condition:

- do not weaken workflow security;

- do not remove tests;

- do not broaden permissions;

- do not change repository settings;

- cite the exact conflict;

- recommend the smallest corrective decision.

## Verification

Pass requires:

- uv sync --frozen;

- uv run ruff format --check .;

- uv run ruff check .;

- uv run mypy src tests;

- uv run pytest;

- corpus validation;

- baseline evaluation;

- all merged Track validation commands;

- fixture validation and evaluation;

- comparison validation;

- calibration validation;

- workflow YAML parsing;

- workflow-policy tests;

- full-SHA action-pin validation;

- action-provenance validation;

- permissions validation;

- timeout validation;

- concurrency validation;

- trigger validation;

- stable workflow-name validation;

- stable job-name validation;

- CodeQL workflow validation;

- Dependency Review workflow validation;

- dependency architecture-policy validation;

- required-check governance-record validation;

- documentation and relative-link checks;

- prohibited-artifact scan;

- model and runtime download-command scan;

- secret-pattern scan;

- git diff --check;

- git status --short --branch.

Also confirm:

- no model or runtime artifact was downloaded;

- no runtime was installed;

- no inference occurred;

- no GitHub repository setting changed;

- no candidate decision changed;

- calibration remains not-approved;

- acquisition and execution remain disabled;

- productionReady remains false;

- no commit, push, PR, release, or deployment occurred automatically.

Recommended Conventional Commit:

ci: harden protected repository validation

Do not create the commit automatically.

## Handoff Requirements

Return one consolidated handoff containing:

1. Outcome

2. Base commit, branch, and working-tree state

3. Multi-agent execution summary

4. Existing CI baseline

5. General validation workflow

6. Validation job and command coverage

7. CodeQL workflow

8. Dependency Review workflow

9. Action-pin inventory

10. Permissions analysis

11. Concurrency and timeout behavior

12. Fork and event safety

13. Workflow-policy enforcement

14. Intended required checks

15. Observed GitHub check contexts, if available

16. Current branch-protection or ruleset state

17. Main-ruleset operator procedure

18. Files changed

19. Dependency and lockfile impact

20. Every verification command and actual result

21. Independent verification findings

22. Scope compliance

23. Unresolved decisions

24. Residual risks

25. Exact ruleset recommendation

26. Proposed Conventional Commit

27. Proposed PR title and summary

28. Required post-merge operator steps

Final verdict must be exactly one of:

- REPOSITORY HARDENING READY FOR PRINCIPAL REVIEW

- REPOSITORY HARDENING READY WITH DOCUMENTED RESIDUALS

- REPOSITORY HARDENING NOT READY

- BLOCKED BY UNRESOLVED AUTHORITY

Explicitly confirm:

- no model or runtime artifact was downloaded;

- no runtime was installed;

- no inference occurred;

- no candidate or evaluation decision changed;

- no GitHub repository setting was changed;

- no automatic commit or push occurred;

- no pull request was created automatically;

- no package was published;

- no release or deployment occurred;

- calibration remains not-approved;

- productionReady remains false.

End with exactly one:

REPOSITORY HARDENING 1 READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT

or:

REPOSITORY HARDENING 1 BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW