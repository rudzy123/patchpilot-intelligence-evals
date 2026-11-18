# Security

This repository stores synthetic evaluation fixtures and an offline harness. It is not a production service and it does not hold tenant data by design.

## Accidental sensitive data

If a case, result, log, or commit contains a real credential, tenant identifier, customer record, raw SBOM, or raw advisory payload:

1. Report it to the repository maintainers through a private GitHub security advisory.
2. Do not open a public issue that contains the data.
3. Do not paste the data into chat, logs, or a pull request description.
4. Remove the data in a follow-up change after a maintainer reviews it.
5. Leave published history unchanged unless a maintainer decides otherwise. A report does not mean existing clones have been purged.

## What the controls actually do

- Corpus validation rejects probable credential patterns, connection strings, email addresses, IP addresses, and `http` or `https` URLs whose host does not end in `.invalid`. A rejected pattern is not proof that no real identifier exists.
- Evaluation and tests install an in-process hook on `socket.socket`, `socket.create_connection`, `socket.getaddrinfo`, and `urllib.request.urlopen`. Direct use of the private socket implementation, a subprocess that does not go through the candidate runner, or a socket opened before the hook is outside this control. This is not seccomp, a network namespace, or a firewall.
- Paths that lexically leave the repository root are rejected before this package opens them. The check does not resolve `../patchpilot` or `../neural-from-scratch`. Symlinks and already-open file descriptors are outside this control.
- Application code in this package reads environment variables only through an explicit tooling allowlist. The interpreter and development tools still see the process environment. Provider credentials are not on the allowlist.
- Logs from evaluation may contain case identifiers, metric names, and statuses. They omit assistance-request text and explanation bodies.

## Candidate subprocess

The candidate runner is a separate Python process. It is not a container and it is not an operating-system sandbox.

The harness enforces an argument array with `shell=False`, a temporary working directory that contains only the copied fixture files, a minimal environment, a 15-second wall-clock limit, a 64 KiB standard-output limit, a 16 KiB standard-error limit, one request, and no retry. On timeout or oversize output it sends `SIGKILL` to the child process group when the platform permits, and otherwise kills the direct child. The child installs the same Python socket, DNS, and urllib hook, and an open hook that rejects corpus paths, prior result artifacts, and sibling repository names. A hooked network call exits 86 and is classified as `network-policy-failure`.

The harness does not enforce process namespaces, seccomp, containers, cgroups, filesystem mount isolation, user namespaces, or operating-system outbound network policy. Symlinks, raw system calls, file descriptors opened before the hook, and a nested executable are outside the Python hook.

## Real-candidate boundary

Track 5 does not acquire a model or execute one. The cache policy stores rules only. A caller passes a repository-external root, and quarantine cannot execute, load a tokenizer, or load a model.

Artifact verification compares expected and observed names, sizes, and SHA-256 values. Executable detection is limited to mode bits, a shebang, and ELF magic. That check is not malware detection.

The real-candidate profile can set `RLIMIT_CPU`, `RLIMIT_AS`, `RLIMIT_FSIZE`, `RLIMIT_NOFILE`, and `RLIMIT_NPROC` on a child. `RLIMIT_AS` limits address space, not resident memory. `RLIMIT_NPROC` is a per-user limit. Read-only mounts, hidden home and credential files, and operating-system network denial are deferred acquisition blockers on that profile. Those limits and the Python hooks are not an operating-system sandbox.

## Hardened fixture launcher

Synthetic fixtures can run through a separate launcher: bubblewrap namespaces inside a transient systemd user scope. That launcher is the operating-system boundary for those fixtures. It does not replace the candidate runner above. The candidate runner still has no namespace, cgroup, or operating-system network denial.

The launcher keeps a private network namespace. Host loopback, external IPv4, external IPv6, DNS, and host Unix sockets outside the mount are denied. Sandbox-local loopback comes up with the namespace; a connection there is refused by the absence of a listener, and seccomp does not currently block `socket`. Seccomp stays unproven. `MemoryMax` limits cgroup memory. `RLIMIT_AS` limits address space. `TasksMax` limits process count. `RLIMIT_NPROC` is not used as a private process limit.

The launcher mounts a staged interpreter, the fixture, read-only synthetic inputs, and a private result directory. It does not mount the repository root, home directory, or credential directories. The child environment is an allowlist. Attestations omit host names, user names, addresses, and environment values. The launcher does not execute a model. `productionReady` stays false.

## External runtime root

A future ONNX Runtime archive is staged outside this repository, outside the model-artifact cache, and outside the output directory. The committed policy stores no host path. Quarantine and rejected trees cannot be executed. Promotion requires a verified inventory. Shared libraries must be ELF. Other staged files must not be executable. `malwareDetectionClaimed` stays false. These checks are not an operating-system sandbox. This repository contains no runtime archive. Installation stays unauthorized.

## Track 6D readiness

Track 6D acquisition readiness is `not-ready`. The record does not authorize runtime installation, model or tokenizer acquisition, model conversion, candidate selection, or real inference. Validation reads local records only.

## Track 7 candidate landscape

Track 7 selection is `no-selection`. Track 8 authorization is `not-authorized`. Principal Architect review on 2026-11-11 approves that fail-closed landscape and does not authorize acquisition. Validation reads the local candidate records and does not acquire artifacts, install a runtime, convert a model, or execute inference. `productionReady` stays false.

## Track 7A storage safety

Track 7A storage readiness is `not-ready`. Principal Architect review on 2026-11-12 approves the storage model and same-filesystem atomic promotion with documented residuals. The atomic storage blocker is `resolved`. Copy promotion remains over the ceiling, and cross-filesystem promotion is ineligible. Selection stays `no-selection`. Track 8 authorization stays `not-authorized`. The synthetic CI check creates a temporary file outside the repository and does not download, install, convert, or execute a model. `productionReady` stays false.

## Track 7B evidence closure

Track 7B leaves both FP32 resident envelopes `unresolved` and leaves behavioral suitability unmeasured. Track 8B readiness is `ready-for-controlled-measurement` with documented residuals. Principal Architect review on 2026-11-12 approves that evidence closure and authorizes a future measurement Session in principle. The approval does not install ONNX Runtime, acquire a model or tokenizer, parse a graph, convert, quantize, or execute inference. Selection stays `no-selection`. Track 8 acquisition stays `not-authorized`. `installationAuthorized` stays false. `productionReady` stays false.

## Track 8A acquisition tooling

Track 8A validators read the committed plan, allowlist, redacted evidence, implementation review, and empty templates. They do not transfer. The manual acquire commands require the plan digest and write only under operator-supplied roots outside this repository, outside home directories, and outside sibling repositories. Quarantine bytes are not executed. Hashing and the offline load proof require bubblewrap's network namespace. The in-process network hook is not that boundary. `RLIMIT_AS` is address space. Cgroup `MemoryMax` is the resident-memory control. The 2026-11-16 review records one external acquisition and does not authorize Track 8B measurement. `measurementPerformed` stays false. `productionReady` stays false.

## Track 8B measurement records

Track 8B validators read the committed plan, the not-approved operator checkpoint, the not-executed templates, the stopped-attempt records, and the Track 9 recommendation. They do not create a session. Manual measurement commands write only under an operator-supplied result root outside this repository. The 2026-11-16 attempt stopped with `tokenizer-failure` before Run. That plan digest is consumed and is not reusable. Another Run requires a new plan and a new operator approval. Historical authorization records stay `not-authorized`. `installationAuthorized` stays false. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `productionReady` stays false.

## Track 8B-R1 retry records

Track 8B-R1 validators read the committed retry plan, the not-approved operator checkpoint, the not-executed templates, the stopped-attempt records, and the advisory Track 9 recommendation. They do not create a session. Manual retry commands write only under a fresh operator-supplied result root outside this repository. The consumed Track 8B plan and the consumed retry plan are refused before Run. `replacementPlanDigest` stays `not-issued`. `installationAuthorized` stays false. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `productionReady` stays false.

## Track 8B-R2 inference retry

Track 8B-R2 validators read the committed inference-retry plan, the not-approved operator checkpoint, the not-executed templates, and the consumed-plan disposition. They do not create a session and they do not call Run. Manual commands write only under a fresh result root outside this repository. The R2 plan digest and both earlier plan digests are refused before Run. No R3 digest is issued. The dynamic-link precheck may load the verified runtime library and resolve `OrtGetApiBase`. It does not create a model session. `installationAuthorized` stays false. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `productionReady` stays false.

## Track 9 evidence review

Track 9 validators read the committed evidence inventory, memory review, behavioral review, proportionality decision, continuation authorization, candidate disposition, and implementation review. They do not create a session and they do not call Run. Principal Architect review on 2026-11-17 approves the evidence review. The in-principle corpus-only continuation does not create a plan, a plan digest, an operator approval, or a result root. It does not select the candidate. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. The acceptance record is [docs/provenance/track9-implementation-review.md](docs/provenance/track9-implementation-review.md). The boundary is [docs/architecture/corpus-continuation-boundary.md](docs/architecture/corpus-continuation-boundary.md).

## Track 9A corpus continuation

Track 9A validators read the separate corpus-only plan, the not-approved operator record, the not-executed templates, and the stopped-attempt records. They do not create a session and they do not call Run. `corpus-continuation-preflight` and `corpus-continuation-execute` are not CI steps. The plan digest is consumed and non-reusable, so execute refuses it before Run. The external result root stays the immutable stopped attempt and is not rewritten by these records. The committed approval stays `not-approved`. Historical plan digests stay consumed. No replacement corpus plan digest is issued. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. `installationAuthorized` stays false. The runbook is [docs/operations/corpus-continuation-runbook.md](docs/operations/corpus-continuation-runbook.md).

## Track 10 candidate disposition

Track 10 validators read the attributed-response record, the schema-invariant review, the proportionality decision, the six-run authorization, the investment-stop decision, the candidate disposition, and the implementation review. They do not create a session and they do not call Run. Principal Architect review on 2026-11-18 approves the disposition. The in-principle six-run diagnostic does not create a plan, a plan digest, an operator approval, or a result root. It does not select the candidate. The readiness snapshot stays `not-executed`. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. `installationAuthorized` stays false. The boundary is [docs/architecture/six-run-diagnostic-boundary.md](docs/architecture/six-run-diagnostic-boundary.md). The disposition review is [docs/provenance/track10-candidate-disposition-review.md](docs/provenance/track10-candidate-disposition-review.md). The acceptance record is [docs/provenance/track10-implementation-review.md](docs/provenance/track10-implementation-review.md).

## Track 10A schema diagnostic

Track 10A validators read the diagnostic plan, the not-approved operator record, and the not-executed templates. They do not create a session and they do not call Run. `schema-diagnostic-preflight` and `schema-diagnostic-execute` are not CI steps. Execute refuses the four consumed plan digests before Run. The external attempt sealed six qualifying candidate-output schema failures and met the precommitted threshold. Principal Architect review on 2026-11-18 accepts that result. Observed `realModelExecuted` is true because the verified candidate was loaded, ONNX Runtime Run was invoked, and generation was observed. The external sealed files were not rewritten. `track10a-implementation-review-validation` reads the acceptance record and does not call Run. That result does not authorize automatic rejection, selection, calibration approval, full corpus evaluation, PatchPilot integration, shadow mode, production use, release, deployment, or another Run. The committed approval stays `not-approved`. The plan digest is `7d90e79de202949231319b2c863a2d99b5aaed4edb1d87e0cf57673cdc9bec75`. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. `installationAuthorized` stays false. The runbook is [docs/operations/schema-diagnostic-runbook.md](docs/operations/schema-diagnostic-runbook.md).

## GitHub Actions

Workflows read repository contents. CodeQL may also write code-scanning results. They do not receive secrets, persist checkout credentials, or use `pull_request_target`. Action pins and the dependency rules are in [docs/security/github-actions-supply-chain.md](docs/security/github-actions-supply-chain.md). A workflow does not change branch protection or repository rulesets. The operator procedure is [docs/operations/main-ruleset-procedure.md](docs/operations/main-ruleset-procedure.md). `productionReady` stays false.

## Supported use

Offline harness checks and future offline candidate runs inside this repository. Do not use these fixtures for production decisions.
