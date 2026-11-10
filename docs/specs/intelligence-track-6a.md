Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 6A: Hardened Execution Environment and Runtime Authorization

## Identity

- **Repository:** patchpilot-intelligence-evals

- **Session ID:** Intelligence Track 6A

- **Mission:** Implement and verify the hardened operating-system execution boundary required for a future real offline candidate, resolve the nine isolation blockers recorded by Intelligence Track 5 where the current machine permits, and authorize exactly one pinned offline inference runtime or preserve the no-runtime decision.

- **Base commit:** The parent of the spec-only commit introducing this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.

- **Expected repository state:** Intelligence Track 5 merged with an approved real-candidate manifest boundary, external artifact-cache validation, synthetic artifact verification, real-candidate isolation profile, no-runtime decision, continued no-selection, and Track 6 acquisition not authorized.

- **Branch:** feat/intelligence-track-6a-hardened-execution

- **Change type:** Hardened evaluation infrastructure, runtime authorization, closed schemas, deterministic sandbox tests, documentation, and CI enforcement. No model acquisition or real inference.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, create a tag, publish a release, deploy, modify Git history, change GitHub repository settings, acquire model artifacts, install a real inference runtime into the project environment, or execute a real model.

## Architectural Outcome

Intelligence Track 6A must answer:

> Can the current Linux evaluation machine enforce a sufficiently strong, reproducible, and observable execution boundary for a future offline model candidate, and can one inference runtime be authorized without installing or executing it?

The completed repository must be able to:

1. Describe one versioned hardened-execution profile.

2. Detect available Linux isolation capabilities without recording sensitive machine identifiers.

3. Establish which controls are enforceable on the current machine.

4. Launch harmless deterministic fixtures inside the hardened boundary.

5. Mount or expose synthetic verified artifacts as read-only.

6. expose a minimal read-only candidate configuration.

7. provide a private writable result directory.

8. hide corpus gold labels.

9. hide prior candidate results.

10. hide sibling-repository paths.

11. hide the operator home directory.

12. hide SSH material and common cloud-credential locations.

13. deny outbound network at the operating-system boundary.

14. apply process, CPU, memory, file-size, open-file, and wall-clock limits.

15. terminate the complete process tree.

16. preserve direct-argument invocation with no shell.

17. emit a machine-readable execution-attestation record.

18. distinguish enforced, unavailable, unsupported, and failed isolation controls.

19. assess no more than three inference runtimes using official evidence.

20. authorize exactly one pinned runtime or preserve no-runtime.

21. determine whether hardened execution is sufficient for a future acquisition Session.

22. preserve Track 5’s no-selection and Track 6 not-authorized decisions unless every prerequisite is proven.

This Session must not acquire or execute a real model.

## Governing Authority

Before editing, Cursor must reread:

- every repository [AGENTS.md](http://AGENTS.md);

- [README.md](http://README.md);

- [SECURITY.md](http://SECURITY.md);

- [CONTRIBUTING.md](http://CONTRIBUTING.md);

- NOTICE;

- LICENSE;

- .gitignore;

- pyproject.toml;

- uv.lock;

- every protected validation workflow;

- all documents under docs/architecture;

- all documents under docs/provenance;

- all existing schemas;

- all candidate and authorization records;

- candidate protocol implementation;

- deterministic candidate runner;

- Track 5 real-candidate manifest implementation;

- Track 5 cache and artifact-verification implementation;

- Track 5 isolation profile;

- Track 5 runtime assessment and authorization;

- Track 5 evidence-closure record;

- Track 5 implementation-review record;

- Track 6 acquisition-authorization record;

- existing CLI commands;

- existing tests;

- Intelligence Track 2 through Track 5 specifications;

- merged Intelligence Track 5 implementation evidence.

Do not inspect local files in patchpilot or neural-from-scratch.

Public read-only research is permitted only for:

- official Linux documentation;

- official kernel documentation;

- official container-runtime documentation;

- official namespace and resource-limit documentation;

- official runtime repositories and documentation;

- official runtime licenses;

- official runtime security advisories;

- immutable official runtime revisions;

- original runtime maintainers.

Secondary sources may identify a concern but may not resolve mandatory security, licensing, provenance, or runtime-authority questions.

## Invariants

### Deterministic PatchPilot authority

No evaluation runtime, candidate, container, sandbox, or model may become authoritative over:

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

- due dates;

- remediation-queue ordering;

- priority review;

- Finding lifecycle;

- remediation completion;

- PatchPilot audit state.

All candidate outputs remain advisory evaluation artifacts.

### No model acquisition or inference

Intelligence Track 6A must not:

- download model weights;

- download tokenizer artifacts;

- download real model configuration artifacts;

- execute a language model;

- contact a hosted inference provider;

- contact a model hub through repository code;

- populate the real artifact cache;

- authorize a candidate solely because an execution boundary exists;

- add model artifacts to Git;

- publish or redistribute model artifacts.

### No runtime installation in the project environment

Track 6A may research and authorize one runtime.

Track 6A must not add the runtime as:

- a Python project dependency;

- a development dependency;

- a transitive dependency;

- a Git submodule;

- a vendored binary;

- a committed executable;

- a CI-downloaded binary;

- a container image pulled during ordinary tests.

The runtime may be represented through authorization records and synthetic adapter contracts only.

A later acquisition Session must install or stage the authorized runtime through a separately reviewed procedure.

### Hardened boundary before real execution

A real candidate must not execute until the following controls are either enforced or explicitly classified as unavailable and acquisition-blocking:

- unprivileged process identity;

- minimal environment;

- read-only verified artifacts;

- read-only candidate configuration;

- isolated writable result directory;

- no gold-label visibility;

- no prior-result visibility;

- no sibling-repository visibility;

- no home-directory visibility;

- no SSH-material visibility;

- no cloud-credential visibility;

- operating-system outbound-network denial;

- process-count limit;

- CPU-time limit;

- memory limit;

- wall-clock limit;

- file-size limit;

- open-file limit;

- process-tree termination;

- no shell;

- explicit working directory;

- canonical stdin and stdout protocol.

Documentation alone is insufficient. Every control claimed as enforced must have a deterministic test.

### Portable architecture, Linux implementation

The current implementation may target Linux because the approved evaluation machine is Linux.

The repository must distinguish:

- portable protocol requirements;

- Linux-specific implementation;

- unsupported platforms;

- degraded behavior;

- fail-closed behavior.

Unsupported platforms must not silently run with weaker isolation.

### Isolation-mechanism hierarchy

The implementation must evaluate and document the strongest practical mechanism available on the current machine.

Permitted mechanisms for assessment include:

- rootless Podman;

- rootless Docker;

- Bubblewrap;

- Linux user, mount, PID, IPC, UTS, and network namespaces;

- unshare;

- systemd-run --user;

- Linux resource limits;

- cgroup v2 delegation;

- seccomp where available.

The implementation must not assume that a command’s presence proves the control works.

Capability probes must test actual behavior with harmless deterministic fixtures.

### No privileged requirement

The architecture must prefer rootless and unprivileged controls.

Track 6A must not:

- require root for repository tests;

- modify system configuration;

- install system packages automatically;

- change firewall rules;

- change kernel parameters;

- add the user to privileged groups;

- start or modify a privileged daemon;

- change Docker or Podman configuration;

- create persistent system services.

If a critical control requires unavailable privilege, classify that control as an acquisition blocker.

### OS-level network denial

Python socket hooks are defense-in-depth only.

A hardened profile must deny network access below the candidate process.

The network test must attempt, without transmitting sensitive information:

- DNS resolution;

- IPv4 socket creation or connection;

- IPv6 socket creation or connection where supported;

- loopback access unless specifically required and authorized;

- Unix-domain socket access outside the sandbox where observable.

Tests must use reserved or non-routable destinations and must not contact real providers.

If OS-level denial cannot be proven, real-model execution remains unauthorized.

### Filesystem visibility

The hardened process must see only the minimum required logical filesystem:

- candidate executable or synthetic fixture;

- verified read-only artifact directory;

- read-only candidate configuration;

- minimal runtime libraries required by the selected mechanism;

- isolated writable result directory;

- minimal temporary directory;

- required pseudo-filesystems exposed read-only or minimally.

The process must not see:

- corpus gold records;

- previous evaluation results;

- sibling repositories;

- the operator home directory;

- .ssh;

- AWS, Azure, Google Cloud, Kubernetes, or other credential directories;

- Git credentials;

- package-manager credentials;

- arbitrary repository source beyond approved runtime files;

- external cache quarantine or rejected states.

### Synthetic-only verification

All Track 6A execution tests must use harmless deterministic fixtures and synthetic files.

Tests must not use:

- model weights;

- tokenizer files from a real model;

- real model configurations;

- tenant data;

- customer data;

- production data;

- raw SBOMs;

- raw advisory payloads;

- credentials.

### Resource enforcement

Where supported, the hardened boundary must apply:

- maximum process count;

- maximum address space or cgroup memory;

- maximum CPU time;

- wall-clock timeout;

- maximum file size;

- maximum standard output;

- maximum standard error;

- maximum open files;

- process-tree termination.

The implementation must document whether memory control is:

- RLIMIT_AS;

- cgroup memory;

- container memory;

- another mechanism.

Do not misrepresent virtual-address limits as resident-memory limits.

### Execution attestation

Every hardened synthetic execution must produce a closed, versioned attestation containing:

- profile ID;

- profile version;

- mechanism;

- mechanism version;

- operating-system family;

- architecture;

- enforced control IDs;

- unavailable control IDs;

- failed control IDs;

- runtime authorization ID, if any;

- fixture identity;

- fixture digest;

- input digest;

- output digest;

- exit classification;

- resource-limit configuration;

- network-test result;

- filesystem-visibility-test result;

- process-tree cleanup result;

- execution timestamp;

- repository commit;

- realModelExecuted: false;

- productionReady: false.

The attestation must not contain hostnames, usernames, IP addresses, environment contents, credential paths containing user identity, or sensitive filesystem data.

### Runtime authorization

Assess no more than three runtimes, including only runtimes relevant to the candidate class and CPU-only evaluation.

A runtime may be authorized only if:

- license is explicit;

- immutable version is fixed;

- official source is identified;

- supported artifact format is clear;

- CPU-only execution is supported;

- fully offline loading is supported;

- local artifact paths are supported;

- no remote code is required;

- no mandatory telemetry exists;

- telemetry can be disabled where applicable;

- deterministic settings are documented where supported;

- security advisories are reviewed;

- subprocess integration is feasible;

- runtime acquisition can later be verified independently;

- the runtime does not enter PatchPilot production dependencies.

Runtime authorization does not authorize runtime installation.

### Candidate selection remains unchanged

Track 6A must not select a model candidate.

The Track 5 outcome remains authoritative:

- selectionOutcome: no-selection;

- acquisitionStatus: not-acquired;

- executionStatus: not-executed;

- productionReady: false.

Candidate-specific licensing and provenance gaps remain unresolved unless a later Session explicitly closes them.

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

Calibration remains not-approved.

## Assumed Repository State

Before implementation, Cursor must prove:

- workspace root and Git root are patchpilot-intelligence-evals;

- local main equals origin/main;

- Intelligence Track 5 is merged;

- the spec-only commit parent equals origin/main;

- the working tree is clean after the spec-only commit;

- repository license is Apache-2.0;

- Python requirement remains &gt;=3.12,&lt;3.13;

- uv.lock exists and validates;

- protected validation CI passes on synchronized main;

- 180 or more tests pass on synchronized main;

- the 24-case corpus is unchanged;

- corpus digest remains 49fe79544a26de429afe865fbd2666828bf26a6da30efe6d87f3b0fdfbd0989c;

- candidate protocol remains version 1.0.0 unless synchronized main proves an authorized revision;

- eight deterministic candidate fixtures remain approved;

- no fixture reads corpus gold records;

- Track 5 real-candidate manifest exists;

- Track 5 cache and synthetic verification boundary exists;

- runtime authorization remains no-runtime;

- candidate selection remains no-selection;

- Track 6 acquisition remains not-authorized;

- Track 5 review status records Principal Architect acceptance;

- Track 5 review digest matches the committed record;

- nine isolation controls remain recorded as namespace or container blockers;

- acquisition status remains not-acquired;

- execution status remains not-executed;

- local model-artifact digests remain empty;

- no real model dependency exists;

- no model, tokenizer, or real-model configuration artifact exists;

- no provider SDK exists;

- no tenant or customer data exists;

- no PatchPilot integration exists;

- no sibling repository is nested in the Git tree;

- productionReady remains false.

If a material assumption is false, stop and report the conflict.

## Allowed Change Surface

Permitted:

- docs/specs/[intelligence-track-6a.md](http://intelligence-track-6a.md);

- hardened-execution architecture;

- runtime-selection documentation;

- sandbox-capability documentation;

- execution-attestation documentation;

- closed schemas and structured records required by this Session;

- source modules for capability probing, hardened execution, resource controls, filesystem policy, network tests, attestation generation, and runtime authorization validation;

- deterministic fixture programs;

- focused tests;

- CLI commands for capability probing, hardened fixture execution, attestation validation, and runtime authorization validation;

- CI updates that run safe Track 6A validations;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, and provenance documentation;

- .gitignore only where required for generated sandbox outputs;

- pyproject.toml and uv.lock only if a narrowly necessary non-runtime validation dependency is proven essential, licensed, and approved.

Not permitted:

- model or tokenizer acquisition;

- real-model configuration acquisition;

- runtime installation;

- real-model inference;

- changing Track 5 candidate decisions;

- changing the corpus or gates;

- modifying sibling repositories;

- PatchPilot product integration;

- privileged host modification;

- deployment.

## Required Repository Additions

The final repository should include the conceptual equivalent of:

text</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">docs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── architecture/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [hardened-execution.md](http://hardened-execution.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [linux-isolation-capabilities.md](http://linux-isolation-capabilities.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [runtime-authorization.md](http://runtime-authorization.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [track6b-acquisition-prerequisites.md](http://track6b-acquisition-prerequisites.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── provenance/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [runtime-evidence.md](http://runtime-evidence.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">└── specs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── [intelligence-track-6a.md](http://intelligence-track-6a.md)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">schemas/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── sandbox-capability-report.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── hardened-execution-profile.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── hardened-execution-attestation.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── runtime-security-assessment.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── runtime-authorization-v2.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">└── track6b-readiness.schema.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">candidates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">└── authorization/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── sandbox-capability-report.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── hardened-execution-profile.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── runtime-security-assessment.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── runtime-authorization-v2.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── track6b-readiness.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">src/patchpilot_intelligence_evals/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── sandbox_[capabilities.py](http://capabilities.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── hardened_[execution.py](http://execution.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── resource_[controls.py](http://controls.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── filesystem_[policy.py](http://policy.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── network_[policy.py](http://policy.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── execution_[attestation.py](http://attestation.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">└── runtime_[security.py](http://security.py)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">tests/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── test_sandbox_[capabilities.py](http://capabilities.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── test_hardened_[execution.py](http://execution.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── test_resource_[controls.py](http://controls.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── test_filesystem_[policy.py](http://policy.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── test_network_[policy.py](http://policy.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">├── test_execution_[attestation.py](http://attestation.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">└── test_runtime_[security.py](http://security.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794330900000,&quot;dataSource&quot;:0}">

Exact names may differ only to follow established repository conventions.

Do not create empty placeholder modules.

## Required Structured Records

Create closed, versioned schemas and validated records for:

1. sandbox capability report;

2. hardened execution profile;

3. hardened execution attestation;

4. runtime security assessment;

5. runtime authorization;

6. Track 6B readiness.

Every schema must:

- have a stable schema ID;

- have an explicit version;

- use additionalProperties: false;

- distinguish required, available, enforced, failed, unavailable, and deferred controls;

- prohibit credentials and tenant identifiers;

- prohibit hostnames and IP addresses;

- prohibit identity-bearing local paths;

- prohibit environment dumps;

- preserve realModelExecuted: false where applicable;

- preserve productionReady: false;

- support explicit no-runtime and not-ready outcomes.

The Track 6B readiness record must preserve:

- selectionOutcome: "no-selection";

- acquisitionStatus: "not-acquired";

- executionStatus: "not-executed";

- productionReady: false;

- empty local model-artifact digest arrays.

## Multi-Agent Execution Model

Cursor Plan is the lead hardened-execution orchestrator.

Use Grok 4.7 Extra High for:

- capability synthesis;

- Linux isolation decisions;

- network-denial decisions;

- runtime security and licensing;

- execution-profile design;

- readiness decisions;

- conflict resolution;

- independent final verification.

Delegate parallel read-only investigation and controlled implementation to these specialists.

### Agent 1: Linux capability specialist

Owns:

- capability probes;

- kernel and namespace support;

- cgroup support;

- rootless container support;

- Bubblewrap or unshare support;

- unsupported-platform behavior;

- capability-report schema and record.

### Agent 2: Filesystem-isolation specialist

Owns:

- read-only artifact exposure;

- configuration exposure;

- writable result isolation;

- hidden repository and home paths;

- symlink handling;

- filesystem-visibility tests.

### Agent 3: Network and credential-isolation specialist

Owns:

- OS-level network denial;

- DNS tests;

- IPv4 and IPv6 tests;

- loopback treatment;

- Unix-socket treatment;

- environment minimization;

- SSH and cloud-credential hiding.

### Agent 4: Resource-control specialist

Owns:

- process count;

- CPU time;

- memory;

- wall clock;

- file size;

- open files;

- stdout and stderr;

- process-tree cleanup;

- resource-control tests.

### Agent 5: Runtime authorization specialist

Assesses no more than three runtimes.

Owns:

- license;

- immutable version;

- official source;

- CPU support;

- offline loading;

- format support;

- telemetry;

- remote-code behavior;

- deterministic controls;

- security advisories;

- authorization or no-runtime recommendation.

### Agent 6: Attestation and CLI specialist

Owns:

- hardened-execution attestation;

- canonical evidence;

- CLI commands;

- digest behavior;

- realModelExecuted: false;

- validation and reproducibility.

### Agent 7: Independent verification specialist

Runs after implementation.

Must not own:

- capability probes;

- filesystem isolation;

- network policy;

- resource controls;

- runtime decision;

- attestation implementation;

- Track 6B readiness.

### Coordination Rules

The parent agent must:

- run read-only investigations in parallel;

- reconcile one design before edits;

- assign exclusive file ownership;

- prevent overlapping implementation;

- preserve dependency order;

- integrate centrally;

- stop when a critical control cannot be enforced;

- commission a fresh independent reviewer.

## Ordered Execution Plan

Cursor Plan must create one to-do for each task and execute them in order.

### Task 1: Verify the Intelligence Track 5 Baseline

#### Allowed files or subsystem

Read-only repository state, Track 5 records, schemas, code, tests, CI, and documentation.

#### Required behavior

Confirm every assumed-state item.

Record:

- Track 5 review digest;

- no-runtime decision;

- no-selection decision;

- Track 6 not-authorized decision;

- nine isolation blockers;

- current candidate protocol;

- current resource controls;

- exact file ownership for Tasks 2 through 8.

#### Tests

Run safe Git inspection and locked repository-validation commands where needed.

#### Done condition

The baseline is proven, no unrelated change exists, and exclusive ownership is assigned.

### Task 2: Implement Linux Capability Probes

#### Allowed files or subsystem

Capability architecture, schema, implementation, CLI, structured record, and focused tests.

#### Required behavior

Probe harmlessly for:

- operating-system family;

- architecture;

- user namespace availability;

- mount namespace availability;

- PID namespace availability;

- network namespace availability;

- cgroup v2 presence and delegation;

- rootless Podman availability and usability;

- rootless Docker availability and usability;

- Bubblewrap availability and usability;

- unshare availability and usability;

- systemd-run --user availability and usability;

- applicable resource-limit support;

- seccomp support where observable without privilege.

Do not record:

- hostname;

- username;

- IP addresses;

- serial numbers;

- device IDs;

- environment variables;

- identity-bearing paths.

A command’s presence is not enough. Record actual capability-test results.

#### Tests

Use deterministic probes and mocks where host capabilities differ.

Prove unsupported platforms fail closed.

#### Done condition

The repository has a truthful capability report showing what can actually be enforced.

### Task 3: Implement Hardened Filesystem Boundary

#### Allowed files or subsystem

Filesystem architecture, execution profile, implementation, fixtures, and tests.

#### Required behavior

Implement the strongest unprivileged boundary supported by Task 2.

Expose only:

- fixture executable;

- synthetic verified read-only artifacts;

- read-only synthetic configuration;

- isolated writable results;

- minimal temporary space;

- required runtime libraries for the chosen mechanism.

Hide or make unavailable:

- corpus gold labels;

- prior results;

- sibling-repository paths;

- the operator home directory;

- SSH material;

- cloud-credential locations;

- arbitrary repository source;

- quarantine and rejected cache states.

Do not use real model artifacts.

#### Tests

Prove visibility and invisibility using synthetic sentinel files.

Do not expose sentinel contents in logs.

#### Done condition

The supported hardened boundary demonstrates minimum necessary filesystem visibility.

### Task 4: Implement OS-Level Network, Environment, and Credential Isolation

#### Allowed files or subsystem

Network policy, environment policy, hardened launcher, fixtures, and tests.

#### Required behavior

Implement and test, where supported:

- OS-level outbound-network denial;

- DNS denial;

- IPv4 denial;

- IPv6 denial;

- loopback denial unless explicitly required;

- external Unix-socket denial where enforceable;

- minimal environment allowlist;

- no proxy variables;

- no provider credentials;

- no cloud credentials;

- no SSH-agent socket;

- no package-manager credentials;

- no home-directory inheritance.

Python-level hooks may remain as defense-in-depth.

#### Tests

Use reserved or non-routable destinations.

Do not contact real services.

If OS-level denial cannot be proven, record an acquisition blocker.

#### Done condition

The network and credential boundary is enforced and evidenced, or Track 6B remains not ready.

### Task 5: Implement Resource Controls and Process-Tree Cleanup

#### Allowed files or subsystem

Resource-control implementation, hardened launcher, harmless fixtures, and focused tests.

#### Required behavior

Implement, where supported:

- process-count limit;

- CPU-time limit;

- memory or address-space limit identified precisely;

- wall-clock timeout;

- file-size limit;

- open-file limit;

- stdout limit;

- stderr limit;

- process-tree termination;

- no automatic retry.

Use harmless deterministic fixtures that:

- allocate bounded memory;

- consume bounded CPU;

- spawn child processes;

- write controlled output;

- exceed one limit at a time.

#### Tests

Prove each enforced category and stable failure classification.

Do not misrepresent unavailable cgroup controls as enforced.

#### Done condition

Resource and cleanup behavior is deterministic and accurately classified.

### Task 6: Assess and Authorize One Runtime or Preserve No-Runtime

#### Allowed files or subsystem

Official primary-source research, schemas, records, documentation, and validation tests.

#### Required behavior

Assess no more than three runtimes.

For each runtime, record:

- official project;

- official source;

- license;

- immutable version;

- CPU-only support;

- artifact-format support;

- offline-loading support;

- local-path loading;

- telemetry behavior;

- remote-code behavior;

- deterministic controls;

- subprocess integration;

- known relevant security advisories;

- acquisition method;

- artifact-verification method;

- maintenance status;

- disqualifiers.

Authorize at most one runtime.

Do not install it.

A no-runtime outcome is valid.

#### Tests

Validate runtime records and decision arithmetic.

#### Done condition

One runtime is pinned for later acquisition or no-runtime remains authoritative.

### Task 7: Generate Hardened Attestation and Track 6B Readiness Decision

#### Allowed files or subsystem

Attestation schema, attestation generation, CLI, structured records, readiness logic, and focused tests.

#### Required behavior

Run harmless deterministic fixtures through the strongest supported boundary.

Create one or more attestations containing:

- profile and mechanism identity;

- enforced controls;

- unavailable controls;

- failed controls;

- fixture digests;

- input and output digests;

- execution classification;

- resource limits;

- network result;

- filesystem result;

- process cleanup result;

- repository commit;

- realModelExecuted: false;

- productionReady: false.

Track 6B may be marked ready only if:

- OS-level outbound-network denial is proven;

- required filesystem hiding is proven;

- verified artifacts can be exposed read-only;

- result output is isolated;

- home, SSH, cloud, sibling, gold, and prior-result visibility are denied;

- process-tree cleanup is proven;

- critical resource limits are enforced;

- one runtime is authorized;

- no candidate or artifact acquisition is implied.

If any condition fails:

- set readiness to not-ready;

- list blockers;

- preserve no-selection and not-acquired states.

#### Tests

Validate ready and not-ready logic.

Prove incomplete controls fail closed.

#### Done condition

Track 6B has an evidence-backed readiness decision.

### Task 8: Documentation, CI, and Independent Verification

#### Allowed files or subsystem

README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, workflow, and complete repository diff.

#### Required behavior

Document:

- supported hardened mechanism;

- unsupported platforms;

- filesystem visibility;

- network policy;

- resource controls;

- runtime decision;

- attestation semantics;

- remaining blockers;

- no-model boundary;

- Track 6B prerequisites.

Update CI to run only safe, portable validations.

Host-specific capability tests must:

- skip only with an explicit unsupported-capability result;

- never report a skip as an enforced control;

- preserve a not-ready outcome when critical capabilities are unavailable;

- avoid privileged execution;

- avoid runtime installation;

- avoid model acquisition.

Assign independent final verification to a fresh agent.

#### Tests

Run every command in the Verification section.

#### Done condition

The hardened execution boundary is documented, CI-enforced where portable, independently verified, and ready for Principal Architect review.

## Out of Scope

Intelligence Track 6A must not:

- download model or tokenizer artifacts;

- download real model configurations;

- install an inference runtime;

- execute a real model;

- select a model candidate;

- change Track 5 candidate evidence;

- change corpus cases;

- change metrics or gates;

- modify patchpilot;

- modify neural-from-scratch;

- inspect local sibling repositories;

- use tenant, customer, or production data;

- add embeddings;

- add a vector database;

- add RAG;

- fine-tune;

- use LoRA;

- use preference optimization;

- implement shadow mode;

- implement PatchPilot APIs or UI;

- create production composition;

- perform privileged host changes;

- publish a package;

- create a release;

- deploy.

## Stop Conditions

Stop and report if:

1. The spec-only commit parent differs from origin/main.

2. The working tree contains unrelated changes.

3. Intelligence Track 5 is not merged.

4. Track 5 review acceptance is absent or invalid.

5. A real model, tokenizer, or runtime artifact already exists.

6. The implementation requires privileged host modification.

7. The implementation requires installing a system package automatically.

8. OS-level network denial cannot be tested safely.

9. Filesystem hiding requires access to sibling repositories.

10. Tests require reading real credentials.

11. A runtime requires remote code.

12. Runtime licensing remains unresolved.

13. Runtime installation is required during this Session.

14. Track 6B readiness would require selecting or acquiring a candidate.

15. Existing corpus or promotion gates must change.

16. Unsupported capabilities would be reported as enforced.

17. The work cannot fit within one pull-request-sized branch.

On a stop condition:

- do not weaken isolation;

- do not authorize acquisition;

- do not install a runtime;

- record the exact blocker;

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

- all existing Track 5 validations;

- all existing fixture validations and evaluations;

- existing comparison validation;

- existing calibration validation;

- validation of every Track 6A schema;

- validation of every Track 6A structured record;

- capability-report validation;

- hardened-profile validation;

- filesystem-visibility tests;

- network-denial tests;

- environment-minimization tests;

- credential-visibility tests using synthetic sentinels;

- process-count tests;

- CPU-limit tests;

- memory-limit tests;

- wall-clock tests;

- file-size tests;

- open-file tests;

- process-tree cleanup tests;

- attestation validation;

- runtime-assessment validation;

- runtime-authorization validation;

- Track 6B readiness validation;

- documentation and relative-link checks;

- license and provenance checks;

- workflow validation;

- secret-pattern scan;

- prohibited-artifact scan;

- model-artifact scan;

- git diff --check;

- git status --short --branch.

Also confirm:

- no real model, tokenizer, or configuration was downloaded;

- no model was executed;

- no runtime was installed;

- no inference provider or model hub was contacted for inference;

- no privileged host change occurred;

- no tenant, customer, or production data was used;

- no sibling repository was accessed or modified;

- no PatchPilot integration was created;

- no package was published;

- no release or deployment occurred;

- no candidate was selected;

- acquisition remains not acquired;

- execution remains not executed;

- calibration remains not approved;

- productionReady remains false.

Recommended Conventional Commit:

feat(evals): add hardened execution boundary

Do not create the commit automatically.

## Handoff Requirements

Return one consolidated handoff containing:

1. Outcome

2. Base commit, branch, and working-tree state

3. Multi-agent execution summary

4. Intelligence Track 5 baseline

5. Capability report

6. Selected isolation mechanism

7. Filesystem boundary

8. Network boundary

9. Environment and credential boundary

10. Resource controls

11. Process-tree cleanup

12. Execution attestation

13. Runtime assessment

14. Runtime authorization or no-runtime outcome

15. Enforced controls

16. Unavailable controls

17. Deferred controls

18. Track 6B readiness or withholding

19. Files changed

20. Dependency and lockfile impact

21. Every verification command and actual result

22. CI workflow changes

23. Independent verification findings

24. Scope compliance

25. Unresolved decisions

26. Residual risks

27. Exact Track 6B recommendation

28. Proposed Conventional Commit

29. Proposed pull-request title and summary

30. Track 6B prerequisites

Final verdict must be exactly one of:

- TRACK 6B HARDENED ACQUISITION READY

- TRACK 6B HARDENED ACQUISITION READY WITH DOCUMENTED RESIDUALS

- TRACK 6B HARDENED ACQUISITION NOT READY

- BLOCKED BY UNRESOLVED AUTHORITY

Explicitly confirm:

- no model, tokenizer, or configuration artifact was downloaded;

- no real model was executed;

- no inference runtime was installed;

- no candidate was selected;

- no provider was contacted for inference;

- no privileged host change occurred;

- no tenant, customer, or production data was used;

- no sibling repository was accessed or modified;

- no PatchPilot integration was created;

- no automatic commit or push occurred;

- no pull request was created automatically;

- no package was published;

- no release or deployment occurred;

- selectionOutcome remains no-selection;

- acquisitionStatus remains not-acquired;

- executionStatus remains not-executed;

- productionReady remains false.

End with exactly one:

INTELLIGENCE TRACK 6A READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT

or:

INTELLIGENCE TRACK 6A BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW