[i](http://intelligence-track-5.md)Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 5: Real-Candidate Boundary Implementation and Evidence Closure

## Identity

- **Repository:** patchpilot-intelligence-evals

- **Session ID:** Intelligence Track 5

- **Mission:** Implement the evaluation-only technical boundary required to represent, acquire, verify, isolate, and eventually execute one real offline candidate, while closing or confirming the mandatory evidence gaps that prevented candidate authorization in Intelligence Track 4.

- **Base commit:** The parent of the spec-only commit that introduces this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.

- **Expected repository state:** Intelligence Track 4 merged with an approved no-selection decision, five closed Track 4 schemas, five validated authorization records, a non-sensitive hardware profile, unchanged promotion gates, and no acquired model, tokenizer, configuration, or runtime artifact.

- **Branch prefix:** feat/intelligence-track-5-real-candidate-boundary

- **Change type:** Evaluation infrastructure, closed schemas, cache and artifact validation, isolation controls, security tests, runtime assessment, evidence closure, documentation, and CI enforcement. No model acquisition or real inference.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, create a tag, create a release, deploy, modify Git history, change GitHub repository settings, download model artifacts, install an inference runtime, or execute real-model inference.

## Architectural Outcome

Intelligence Track 5 must implement and verify the boundary required before one real offline candidate may be acquired.

The completed repository must be able to:

1. Represent a real offline candidate using one closed candidate kind.

2. Preserve compatibility with all existing deterministic test-double manifests.

3. Validate a repository-external artifact-cache root.

4. Represent quarantine, verified, and rejected artifact states.

5. Validate an expected model-artifact inventory.

6. Compute and validate artifact SHA-256 identities using synthetic fixtures.

7. Reject unexpected files, missing files, traversal, symlink escapes, unsupported formats, and digest mismatches.

8. Prevent execution from quarantine.

9. Preserve immutable verified-artifact identity.

10. Assess no more than three offline inference runtimes without installing them.

11. Authorize at most one runtime or record a no-runtime decision.

12. Define and validate the stronger isolation profile required for real-model execution.

13. Revisit the five Intelligence Track 4 candidate checkpoints using revision-specific primary evidence.

14. Select at most one candidate or preserve the approved no-selection decision.

15. Produce an Intelligence Track 6 acquisition authorization or an explicit not-authorized decision.

16. Preserve not-acquired, not-executed, and productionReady: false.

This is an implementation Session.

It must create executable validation code, CLI commands, closed schemas, structured records, tests, security controls, documentation, and CI enforcement.

It must not download or execute a real model.

## Strategic Boundary

This repository remains an evaluation system.

A future candidate may generate advisory explanations from approved synthetic inputs, but no candidate may become authoritative over:

- organization or tenant identity;

- asset identity;

- package identity;

- Product Match Evidence;

- affectedness;

- Finding creation;

- KEV membership;

- policy facts;

- P1-P4 priority;

- escalation;

- due-date recommendations;

- remediation-queue ordering;

- priority review;

- Finding lifecycle;

- remediation completion;

- PatchPilot audit state.

Candidate results remain evaluation artifacts.

Candidate results must never become PatchPilot Evidence, Findings, RiskCalculations, priority reviews, remediation state, or audit events.

## Governing Authority

Before implementation, Cursor must reread:

- every repository [AGENTS.md](http://AGENTS.md);

- [README.md](http://README.md);

- [SECURITY.md](http://SECURITY.md);

- [CONTRIBUTING.md](http://CONTRIBUTING.md);

- NOTICE;

- LICENSE;

- .gitignore;

- pyproject.toml;

- uv.lock;

- all protected validation workflows;

- all documents beneath docs/architecture;

- all documents beneath docs/provenance;

- all existing JSON Schemas;

- all candidate manifests;

- candidate-protocol implementation;

- subprocess runner;

- network guard;

- result storage;

- comparison behavior;

- calibration implementation;

- promotion gates;

- Intelligence Track 4 selection criteria;

- Intelligence Track 4 candidate shortlist;

- Intelligence Track 4 approved no-selection authorization;

- Intelligence Track 4 hardware profile;

- Intelligence Track 4 acquisition template;

- Intelligence Track 4 experiment-plan record;

- existing CLI commands;

- existing tests;

- Intelligence Track 2, Track 3, and Track 4 specifications;

- merged Intelligence Track 4 implementation evidence.

Do not inspect local files in patchpilot or neural-from-scratch.

Public read-only research is permitted only for:

- official model repositories;

- official model cards;

- official model-weight licenses and acceptable-use terms;

- official tokenizer repositories;

- official runtime repositories and documentation;

- official security advisories;

- immutable upstream revisions;

- original publisher documentation.

Secondary sources may identify a concern but cannot satisfy mandatory licensing, tokenizer, provenance, immutable-revision, remote-code, runtime, or commercial-use requirements.

## Invariants

### Deterministic PatchPilot authority

No candidate may become authoritative over:

- organization or tenant identity;

- asset identity;

- package identity;

- Product Match Evidence;

- affectedness;

- Finding creation;

- KEV membership;

- policy facts;

- P1-P4 priority;

- escalation;

- due-date recommendations;

- remediation-queue ordering;

- priority review;

- Finding lifecycle;

- remediation completion;

- PatchPilot audit state.

Candidate responses remain evaluation artifacts.

Candidate responses must never become PatchPilot Evidence, Findings, RiskCalculations, priority reviews, remediation state, or audit events.

### No acquisition or inference

Intelligence Track 5 must not:

- download model weights;

- download tokenizer artifacts;

- download model configuration artifacts;

- install an inference runtime;

- execute a real model;

- invoke a hosted inference provider;

- invoke a model hub through repository code;

- add weights to Git;

- create a persistent model cache;

- publish or redistribute model artifacts;

- add a PatchPilot runtime dependency.

Official public documentation and repository metadata may be researched.

### Track 4 no-selection remains authoritative

The Track 4 no-selection decision remains authoritative unless all of the following become true:

- every mandatory candidate criterion passes;

- the real-candidate manifest boundary is implemented and tested;

- one runtime is authorized;

- the external artifact-cache boundary is implemented and tested;

- the artifact-verification contract is implemented and tested;

- the isolation profile has no acquisition-blocking deficiency;

- the candidate fits the approved hardware envelope;

- immutable artifact sources are fixed;

- model-weight and tokenizer licensing are resolved;

- independent verification finds no unresolved mandatory concern;

- Principal Architect approval is recorded in a later review.

Expanding the protocol does not automatically make a disqualified candidate eligible.

### Real-candidate manifest kind

Add exactly one candidate kind:

offline-local-model

Existing deterministic test-double manifests must remain valid without semantic change.

An offline-local-model manifest must include:

- schema version;

- protocol version;

- candidate ID;

- candidate version;

- official model ID;

- immutable upstream revision;

- model owner;

- official source URL;

- model-card URL;

- weight-license URL;

- source-code-license URL where applicable;

- tokenizer source URL;

- tokenizer-license URL;

- configuration source;

- expected artifact inventory;

- expected artifact sizes;

- expected upstream digests where authoritative;

- locally verified artifact identities;

- runtime ID;

- runtime-version requirement;

- model format;

- quantization identity;

- context limit;

- generation limit;

- peak-memory budget;

- startup timeout;

- warm per-case timeout;

- network policy;

- remote-code policy;

- telemetry policy;

- permitted uses;

- prohibited uses;

- acquisition status;

- execution status;

- review status;

- productionReady: false.

Before Intelligence Track 6:

- acquisitionStatus must be not-acquired;

- executionStatus must be not-executed;

- locally verified artifacts and digests must be empty;

- productionReady must be false.

### External artifact-cache boundary

Real-candidate artifacts must remain outside the Git repository.

Implement and validate these logical states:

1. quarantine

2. verified

3. rejected

The cache root must:

- be supplied explicitly;

- resolve outside this Git repository;

- resolve outside known sibling-repository roots;

- reject traversal;

- reject symlink escape;

- reject a repository-contained root;

- reject roots that change during validation;

- never contain tenant or production data;

- never be uploaded by CI;

- never be tracked by Git.

Quarantine rules:

- no execution;

- no tokenizer loading;

- no model loading;

- no network fallback;

- no promotion until every required check passes.

Verified rules:

- every file has a computed SHA-256;

- expected and observed filenames are represented separately;

- expected and observed sizes are represented separately;

- unexpected files are rejected;

- missing files are rejected;

- verified artifact identity is immutable;

- any changed byte invalidates verification;

- only verified artifacts may be considered for Intelligence Track 6 execution.

Rejected rules:

- rejected artifacts cannot execute;

- rejected artifacts cannot promote without a new acquisition attempt;

- rejection reasons are retained;

- sensitive artifact content is not copied into metadata;

- cleanup behavior is explicit.

### Artifact verification

Artifact validation must implement:

- canonical path normalization;

- symlink resolution;

- expected-filename validation;

- unexpected-file rejection;

- missing-file rejection;

- file-count validation;

- size validation;

- SHA-256 computation;

- authoritative upstream-digest comparison where available;

- approved-format validation;

- approved-configuration validation;

- tokenizer-provenance validation;

- license-reference validation;

- remote-code requirement rejection;

- executable-content detection within documented limitations;

- immutable verification-manifest generation.

Do not claim malware detection or complete binary safety.

Only synthetic temporary artifacts may be used in Track 5 tests.

### Runtime assessment

Assess no more than three runtimes.

Authorize at most one runtime.

A runtime must satisfy:

- explicit open-source license;

- immutable version;

- offline local loading;

- CPU support;

- approved model-format support;

- no mandatory cloud service;

- no mandatory telemetry;

- explicit telemetry disablement where applicable;

- no trust_remote_code;

- deterministic generation controls where supported;

- local artifact paths;

- bounded context and output;

- subprocess compatibility;

- maintainable security posture;

- documented artifact loading;

- no PatchPilot production dependency.

Do not install a runtime during this Session.

A no-runtime outcome is valid.

### Stronger real-candidate isolation

A future real candidate must not run under only the Python safeguards used for deterministic fixtures.

Create a structured isolation profile addressing:

- unprivileged execution;

- minimal environment;

- read-only verified artifacts;

- read-only candidate configuration;

- isolated writable results;

- no gold-label access;

- no prior-result access;

- no sibling-repository access;

- no home-directory access;

- no SSH configuration access;

- no cloud credentials;

- no outbound network;

- process-count limit;

- CPU-time limit;

- memory limit;

- wall-clock limit;

- file-size limit;

- open-file limit;

- process-tree termination;

- no shell;

- no elevated execution;

- explicit working directory;

- canonical stdin and stdout protocol.

Classify every control as:

- enforced by the current Python harness;

- enforceable through Linux resource limits;

- requires namespace or container support;

- unavailable on the current machine;

- deferred blocker.

Do not claim complete operating-system sandboxing.

### Execution budgets

The existing 15-second deterministic-fixture timeout is not automatically suitable for real-model startup.

Define separate ceilings for:

- artifact verification;

- runtime startup;

- model loading;

- warm candidate invocation;

- per-case generation;

- complete 24-case execution;

- cleanup.

Maximum planning ceilings:

- startup and load: 180 seconds;

- warm per-case generation: 120 seconds;

- complete single-repetition corpus run: 90 minutes;

- standard output: no more than the existing protocol permits;

- standard error: 64 KiB;

- one candidate process at a time;

- one real-candidate evaluation at a time;

- zero automatic retries.

Lower values are preferred when supported by evidence.

### Hardware boundary

The approved Track 4 hardware profile is the starting authority:

- Linux;

- x86_64;

- 16 logical CPUs;

- approximately 30 GiB system memory;

- approximately 1.4 TB available storage;

- no available GPU compute;

- maximum model artifacts of 8 GiB;

- estimated peak candidate-process memory of 12 GiB;

- maximum context of 8,192 tokens;

- one real-candidate process;

- no approved quantization.

Do not record:

- hostnames;

- usernames;

- IP addresses;

- MAC addresses;

- serial numbers;

- device IDs;

- environment values;

- identity-bearing local paths.

### Quantization

No quantization is authorized by default.

A quantization plan may be authorized only if:

- the unquantized candidate is fully authorized;

- quantization rights are explicit;

- the quantized artifact is official or reproducibly generated locally;

- the quantization method and tool are documented;

- the tool version is pinned;

- original and quantized artifact identities remain separate;

- evaluation limitations are documented;

- no unverified community conversion is used.

Do not perform quantization during this Session.

### Candidate evidence closure

A mandatory criterion may be closed only with authoritative, revision-specific evidence.

The following do not close a gap:

- community comments;

- assumptions based on related models;

- model-directory metadata alone;

- mirrors;

- copied terms from another revision;

- assumptions that tokenizer licensing follows model licensing;

- popularity;

- download count;

- leaderboard position;

- benchmark performance.

When authoritative sources conflict:

- record the conflict;

- apply the more restrictive interpretation;

- retain disqualification unless the conflict is resolved.

### No gate changes

Do not change:

- the 24-case corpus;

- corpus taxonomy;

- corpus digest;

- metric definitions;

- invariant gates;

- percentage thresholds;

- calibration status;

- promotion status.

productionReady remains false.

## Assumed Repository State

Before implementation, Cursor must prove:

- workspace root and Git root are patchpilot-intelligence-evals;

- local main equals origin/main;

- Intelligence Track 4 is merged;

- the spec-only commit parent equals origin/main;

- the working tree is clean after the spec-only commit;

- repository license is Apache-2.0;

- Python requirement is &gt;=3.12,&lt;3.13;

- uv.lock exists and validates;

- protected validation CI passes on synchronized main;

- the approved 24-case corpus is unchanged;

- protocol version remains 1.0.0 unless synchronized main proves an authorized revision;

- eight deterministic fixtures remain approved;

- no fixture reads gold labels;

- evaluation artifacts remain immutable and overwrite-protected;

- comparison selects no production winner;

- calibration remains not approved;

- Track 4 selection outcome is no-selection;

- all five Track 4 candidates remain disqualified;

- weighted scores remain null;

- Track 4 acquisition status is not-acquired;

- Track 4 execution status is not-executed;

- locally observed artifact digests remain empty;

- no model or tokenizer artifact exists;

- no inference-runtime dependency exists;

- no provider SDK exists;

- no tenant or customer data exists;

- no PatchPilot production integration exists;

- no sibling repository is nested in this Git tree;

- productionReady remains false.

If a material assumption is false, stop and report the conflict.

## Allowed Change Surface

Permitted:

- docs/specs/[intelligence-track-5.md](http://intelligence-track-5.md);

- real-candidate architecture;

- external-cache architecture;

- artifact-verification architecture;

- runtime assessment and authorization;

- runtime security review;

- real-candidate isolation profile;

- candidate evidence-closure records;

- revised candidate shortlist;

- selected-candidate or continued-no-selection authorization;

- Track 6 acquisition authorization or withholding;

- closed JSON Schemas required by this Session;

- source modules implementing cache-path validation, artifact-set verification, digest calculation, manifest validation, isolation-profile validation, evidence-record validation, and Track 6 authorization validation;

- CLI commands for Track 5 validation;

- deterministic tests using synthetic temporary files and directories;

- CI updates required to run Track 5 checks;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, and provenance documentation;

- pyproject.toml and uv.lock only if an essential non-runtime validation dependency is proven necessary, licensed, and approved.

Not permitted:

- downloading model artifacts;

- downloading tokenizer artifacts;

- downloading model configurations;

- installing an inference runtime;

- executing real inference;

- changing corpus cases;

- changing evaluation gates;

- modifying sibling repositories;

- PatchPilot product integration;

- deployment.

## Required Repository Additions

The final repository must include the conceptual equivalent of:

text</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">docs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── architecture/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [real-candidate-boundary.md](http://real-candidate-boundary.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [external-artifact-cache.md](http://external-artifact-cache.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [model-artifact-verification.md](http://model-artifact-verification.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [real-candidate-isolation.md](http://real-candidate-isolation.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [runtime-selection.md](http://runtime-selection.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [track6-acquisition-boundary.md](http://track6-acquisition-boundary.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── provenance/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [candidate-evidence-closure.md](http://candidate-evidence-closure.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">└── specs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── [intelligence-track-5.md](http://intelligence-track-5.md)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">schemas/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── offline-local-model-manifest.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── external-artifact-cache-policy.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── model-artifact-verification.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── runtime-assessment.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── runtime-authorization.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── real-candidate-isolation-profile.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── candidate-evidence-closure.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">└── track6-acquisition-authorization.schema.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">candidates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── authorization/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── external-artifact-cache-policy.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── runtime-assessment.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── runtime-authorization.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── real-candidate-isolation-profile.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── candidate-evidence-closure.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── track6-acquisition-authorization.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">└── templates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── model-artifact-verification-template.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">src/patchpilot_intelligence_evals/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── real_candidate_[manifest.py](http://manifest.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── artifact_[cache.py](http://cache.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── artifact_[verification.py](http://verification.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── runtime_[authorization.py](http://authorization.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── isolation_[profile.py](http://profile.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── evidence_[closure.py](http://closure.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">└── acquisition_[authorization.py](http://authorization.py)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">tests/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── test_real_candidate_[manifest.py](http://manifest.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── test_artifact_[cache.py](http://cache.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── test_artifact_[verification.py](http://verification.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── test_runtime_[authorization.py](http://authorization.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── test_isolation_[profile.py](http://profile.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">├── test_evidence_[closure.py](http://closure.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">└── test_acquisition_[authorization.py](http://authorization.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794318600000,&quot;dataSource&quot;:0}">

Exact names may differ only to follow established repository conventions.

Do not create empty placeholder modules.

## Required Structured Records

Create closed, versioned schemas and validated records for:

1. real-candidate manifest extension;

2. external artifact-cache policy;

3. artifact-verification manifest;

4. runtime assessment;

5. runtime authorization;

6. real-candidate isolation profile;

7. candidate evidence closure;

8. Track 6 acquisition authorization.

Every schema must:

- have a stable schema ID;

- have an explicit version;

- use additionalProperties: false;

- distinguish expected and observed values;

- prohibit credentials and tenant identifiers;

- prohibit hostnames and IP addresses;

- prohibit identity-bearing local paths;

- preserve productionReady: false;

- support an explicit not-authorized outcome;

- preserve not-acquired and not-executed before Track 6.

The Track 6 authorization record must retain:

- acquisitionStatus: "not-acquired";

- executionStatus: "not-executed";

- productionReady: false;

- empty local artifact-digest arrays.

## Multi-Agent Execution Model

Cursor Plan is the lead real-candidate-boundary orchestrator.

Use Grok 4.7 Extra High for:

- manifest-boundary design;

- artifact-cache security;

- verification architecture;

- runtime assessment;

- license and provenance interpretation;

- operating-system isolation;

- evidence closure;

- Track 6 authorization;

- conflict resolution;

- independent final verification.

Delegate parallel read-only investigation and controlled implementation to:

### Agent 1: Real-candidate manifest specialist

Owns:

- offline-local-model;

- manifest schema;

- backward compatibility;

- model and tokenizer identity;

- runtime identity;

- expected and observed artifacts;

- acquisition and execution state;

- tests.

### Agent 2: Cache and supply-chain specialist

Owns:

- quarantine, verified, and rejected states;

- path validation;

- traversal and symlink controls;

- digest validation;

- file-inventory validation;

- promotion and rejection;

- cleanup;

- no-Git and no-CI-upload controls.

### Agent 3: Runtime specialist

Assesses no more than three runtimes.

Owns:

- license;

- version;

- offline support;

- telemetry;

- model-format support;

- CPU support;

- deterministic controls;

- subprocess compatibility;

- security advisories;

- authorization recommendation.

### Agent 4: Isolation specialist

Owns:

- process identity;

- resource limits;

- environment;

- filesystem access;

- network restrictions;

- process cleanup;

- enforcement classifications;

- limitation documentation.

### Agent 5: Evidence-closure specialist

Revisits the five Track 4 candidates.

Owns:

- weight licensing;

- commercial use;

- tokenizer licensing;

- immutable revision;

- model-card limitations;

- digest conflicts;

- eligibility or continued disqualification.

### Agent 6: Track 6 authorization specialist

Owns:

- acquisition prerequisites;

- artifact verification;

- runtime requirement;

- isolation requirement;

- hardware fit;

- candidate status;

- authorization and stop conditions.

### Agent 7: Independent verification specialist

Runs after implementation.

Must not own:

- manifest extension;

- cache implementation;

- artifact verification;

- runtime decision;

- isolation profile;

- evidence closure;

- Track 6 authorization.

### Coordination Rules

The parent agent must:

- parallelize read-only investigations;

- reconcile one architecture before edits;

- assign exclusive file ownership;

- prevent overlapping edits;

- preserve dependency order;

- stop on unresolved mandatory evidence;

- use a fresh independent verifier.

## Ordered Execution Plan

Cursor Plan must create one to-do per task and execute them in order.

### Task 1: Verify Intelligence Track 4 Baseline

#### Allowed files or subsystem

Read-only repository state, Track 4 records, schemas, protocol, runner, fixtures, evaluator, calibration, CI, and documentation.

#### Required behavior

Confirm every assumed-state item.

Record:

- corpus and protocol identity;

- no-selection identity;

- hardware profile;

- five candidate disqualifications;

- current path and timeout restrictions;

- manifest vocabulary;

- promotion gates;

- exact ownership for later tasks.

#### Tests

Run safe Git checks and locked repository validation commands as needed.

#### Done condition

The baseline is proven and no stop condition exists.

### Task 2: Implement Real-Candidate Manifest Extension

#### Allowed files or subsystem

Manifest architecture, schema, validator, CLI registration, examples, and tests.

#### Required behavior

Add exactly one candidate kind:

offline-local-model

Preserve all deterministic manifests.

Validate:

- official model identity;

- immutable revision;

- licenses;

- tokenizer provenance;

- configuration provenance;

- expected and observed artifacts;

- runtime;

- format;

- quantization;

- resource envelope;

- isolation profile;

- acquisition and execution states;

- local digests;

- review status;

- productionReady: false.

Reject:

- floating revisions;

- missing licenses;

- missing tokenizer provenance;

- missing runtime authorization;

- fabricated observed artifacts;

- local verification claims before acquisition;

- remote-code requirements;

- mandatory telemetry;

- unauthorized runtime;

- paths outside cache policy;

- production readiness.

#### Tests

Prove:

- deterministic fixtures remain valid;

- valid not-acquired real-candidate examples pass;

- unsupported candidate kinds fail;

- floating revisions fail;

- fabricated digests fail;

- missing provenance fails;

- remote code fails;

- unauthorized runtime fails;

- production readiness fails.

#### Done condition

A real candidate can be represented safely without acquisition or execution.

### Task 3: Implement External Artifact Cache and Verification

#### Allowed files or subsystem

Cache architecture, schemas, code, CLI, templates, synthetic fixtures, and tests.

#### Required behavior

Implement:

- quarantine;

- verified;

- rejected.

Enforce:

- explicit external root;

- no repository-contained root;

- no sibling root;

- no traversal;

- no symlink escape;

- no quarantine execution;

- no unexpected files;

- no missing files;

- expected and observed values remain separate;

- SHA-256 validation;

- size validation;

- approved-format validation;

- immutable verified identity;

- persistent rejected state;

- no CI upload;

- no Git tracking.

Use synthetic temporary artifacts only.

Do not create a persistent real cache.

#### Tests

Prove:

- repository root fails;

- sibling-like root fails;

- traversal fails;

- symlink escape fails;

- quarantine execution fails;

- unexpected and missing files fail;

- digest and size mismatches fail;

- valid synthetic inventory promotes;

- changed verified file invalidates identity;

- rejected inventory cannot promote without a new attempt.

#### Done condition

The external-cache boundary is executable and tested without real model artifacts.

### Task 4: Assess and Authorize a Runtime or Record No-Runtime

#### Allowed files or subsystem

Primary-source research, schemas, records, documentation, and tests.

#### Required behavior

Assess no more than three runtimes.

For each runtime record:

- official project and source;

- license;

- immutable version;

- model formats;

- CPU support;

- offline loading;

- telemetry;

- remote-code behavior;

- deterministic controls;

- security advisories;

- subprocess compatibility;

- artifact-loading behavior;

- memory behavior;

- maintenance status;

- disqualifiers.

Authorize at most one runtime.

Do not install the runtime.

An explicit no-runtime result is valid.

#### Tests

Validate runtime schemas and records.

Confirm exactly one authorized runtime or one no-runtime decision.

#### Done condition

Track 6 has a pinned runtime authorization or an explicit blocker.

### Task 5: Implement Real-Candidate Isolation Profile

#### Allowed files or subsystem

Isolation architecture, schema, record, validator, harmless process tests, and documentation.

#### Required behavior

Define and validate:

- unprivileged execution;

- minimal environment;

- read-only artifacts and configuration;

- isolated writable results;

- no gold labels;

- no prior results;

- no sibling repositories;

- no home directory;

- no SSH or cloud credentials;

- no outbound network;

- process, CPU, memory, wall-clock, file-size, and open-file limits;

- process-tree cleanup;

- explicit working directory;

- no shell;

- canonical protocol.

Classify each control as:

- current harness;

- Linux resource limit;

- namespace or container required;

- unavailable;

- deferred blocker.

Use harmless deterministic processes only.

#### Tests

Validate the profile and exercise enforceable controls.

#### Done condition

The profile truthfully determines whether Track 6 can proceed.

### Task 6: Close or Confirm Candidate Evidence Gaps

#### Allowed files or subsystem

Primary research, evidence schemas and records, shortlist update, scoring validation, and documentation.

#### Required behavior

Revisit the five Track 4 candidates using newly available or previously omitted official evidence only.

For each candidate record:

- previous blocker;

- new evidence;

- resolved or unresolved status;

- restrictive interpretation;

- mandatory-criterion outcome;

- scoring eligibility;

- weighted score only if every mandatory criterion passes.

Do not score disqualified candidates.

Use the Track 4 tie-breaker if more than one candidate qualifies.

Select at most one.

#### Tests

Validate evidence, source references, mandatory outcomes, and scores.

#### Done condition

One candidate qualifies fully or no-selection remains authoritative.

### Task 7: Authorize or Withhold Intelligence Track 6

#### Allowed files or subsystem

Track 6 schema, record, acquisition boundary, and tests.

#### Required behavior

Authorize Track 6 only if:

- one candidate qualifies;

- one runtime is authorized;

- cache and verification pass;

- isolation has no acquisition blocker;

- hardware fit is credible;

- immutable source and revision are fixed;

- tokenizer provenance is resolved;

- license and commercial use are resolved;

- unauthorized redistribution is unnecessary;

- no gate change is required.

If any prerequisite fails:

- set authorizationOutcome to not-authorized;

- list every blocker;

- retain no-selection;

- retain empty local digests.

Even when authorization is granted, preserve:

- acquisitionStatus: "not-acquired";

- executionStatus: "not-executed";

- productionReady: false;

- empty local artifact digests.

#### Tests

Validate both authorized and not-authorized examples.

Prove incomplete prerequisites fail closed.

#### Done condition

Track 6 has a durable authorization or withholding decision.

### Task 8: Documentation, CI, and Independent Verification

#### Allowed files or subsystem

README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, workflows, and complete diff.

#### Required behavior

Document:

- real-candidate manifest;

- external cache;

- verification process;

- runtime decision;

- isolation profile;

- evidence closure;

- Track 6 decision;

- residual risks;

- no-acquisition boundary.

Update CI to run:

- existing Track 2 and 3 checks;

- every Track 5 schema validation;

- every Track 5 record validation;

- path, traversal, and symlink tests;

- synthetic cache verification;

- runtime validation;

- isolation validation;

- evidence-closure validation;

- Track 6 authorization validation.

CI must not install a runtime or acquire a model.

Assign a fresh independent verifier.

#### Tests

Run every command in the Verification section.

#### Done condition

The implemented boundary is documented, CI-enforced, independently verified, and ready for Principal Architect review.

## Out of Scope

Intelligence Track 5 must not:

- download model or tokenizer artifacts;

- download real model configurations;

- install an inference runtime;

- execute real inference;

- modify patchpilot;

- modify neural-from-scratch;

- inspect local sibling repositories;

- use tenant, customer, or production data;

- change corpus cases;

- change metrics or gates;

- add embeddings;

- add a vector database;

- add RAG;

- fine-tune;

- use LoRA;

- use preference optimization;

- implement shadow mode;

- implement PatchPilot APIs or UI;

- create production composition;

- publish a package;

- redistribute weights;

- create a release;

- deploy.

## Stop Conditions

Stop and report if:

1. The spec-only commit parent differs from origin/main.

2. The working tree contains unrelated changes.

3. Intelligence Track 4 is not merged.

4. Track 4 no-selection is absent.

5. A real model artifact already exists.

6. Cache implementation requires Git-tracked artifacts.

7. Runtime requires remote code.

8. Runtime licensing is unresolved.

9. Candidate weight licensing is unresolved.

10. Tokenizer provenance is unresolved for a proposed selected candidate.

11. Immutable revision is unavailable.

12. Candidate exceeds hardware limits.

13. Candidate requires a hosted provider.

14. Candidate requires online evaluation.

15. Isolation has a critical unresolved acquisition control.

16. Acquisition requires an unverified mirror.

17. Candidate would receive gold labels.

18. Existing gates must change to authorize acquisition.

19. A runtime must be installed in this Session.

20. A sibling repository must be inspected.

21. Work cannot fit in one pull-request-sized branch.

On a stop condition:

- do not authorize acquisition;

- do not acquire artifacts;

- do not weaken controls;

- cite the blocker;

- recommend the smallest next decision.

## Verification

Pass requires:

- uv sync --frozen;

- uv run ruff format --check .;

- uv run ruff check .;

- uv run mypy src tests;

- uv run pytest;

- uv run patchpilot-evals corpus-validation;

- uv run patchpilot-evals baseline-evaluation;

- validation of every Track 5 schema;

- validation of every Track 5 record;

- existing deterministic-manifest validation;

- existing candidate-evaluation validation;

- existing comparison validation;

- existing calibration validation;

- real-candidate-manifest compatibility tests;

- external-cache root tests;

- repository-root rejection tests;

- sibling-like root rejection tests;

- traversal tests;

- symlink-escape tests;

- unexpected-file and missing-file tests;

- digest and size mismatch tests;

- quarantine and promotion tests;

- immutable verified-identity tests;

- runtime-assessment validation;

- runtime-authorization validation;

- isolation-profile validation;

- harmless resource-limit tests;

- evidence-closure validation;

- scoring and disqualification tests;

- Track 6 authorization validation;

- documentation and relative-link checks;

- license and provenance checks;

- workflow validation;

- secret-pattern scan;

- prohibited-artifact scan;

- model-artifact scan;

- git diff --check;

- git status --short --branch.

Also confirm:

- no real model or tokenizer was downloaded;

- no model was executed;

- no runtime was installed;

- no provider or model hub was contacted for inference;

- no tenant, customer, or production data was used;

- no sibling repository was accessed or modified;

- no PatchPilot production integration was created;

- no package was published;

- no release or deployment occurred;

- current gates remain unchanged;

- productionReady remains false.

Recommended Conventional Commit:

feat(evals): implement real candidate boundary

Do not create the commit automatically.

## Handoff Requirements

Return one consolidated handoff containing:

1. Outcome

2. Base commit, branch, and working-tree state

3. Multi-agent execution summary

4. Intelligence Track 4 baseline

5. Real-candidate manifest extension

6. Backward compatibility

7. External artifact-cache implementation

8. Artifact-verification behavior

9. Runtime assessment

10. Runtime authorization or no-runtime outcome

11. Isolation profile

12. Enforced isolation controls

13. Deferred isolation controls

14. Candidate evidence-closure results

15. Selected candidate or continued no-selection

16. Hardware fit

17. Track 6 authorization or withholding

18. Files changed

19. Dependency and lockfile impact

20. Every verification command and result

21. CI workflow changes

22. Independent verification findings

23. Scope compliance

24. Unresolved decisions

25. Residual risks

26. Exact Track 6 recommendation

27. Proposed Conventional Commit

28. Proposed pull-request title and summary

29. Intelligence Track 6 prerequisites

Final verdict:

- TRACK 6 ACQUISITION AUTHORIZED

- TRACK 6 ACQUISITION AUTHORIZED WITH DOCUMENTED RESIDUALS

- TRACK 6 ACQUISITION NOT AUTHORIZED

- BLOCKED BY UNRESOLVED AUTHORITY

Explicitly confirm:

- no model, tokenizer, or configuration artifact was downloaded;

- no real model was executed;

- no inference runtime was installed;

- no inference provider was contacted;

- no tenant, customer, or production data was used;

- no sibling repository was accessed or modified;

- no PatchPilot production integration was created;

- no automatic commit or push occurred;

- no pull request was created automatically;

- no package was published;

- no release or deployment occurred;

- acquisitionStatus remains not-acquired;

- executionStatus remains not-executed;

- productionReady remains false.

End with exactly one:

INTELLIGENCE TRACK 5 READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT

or:

INTELLIGENCE TRACK 5 BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW