Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 8A: Controlled Runtime and Candidate Acquisition for Measurement

## Identity

- **Repository:** patchpilot-intelligence-evals

- **Session ID:** Intelligence Track 8A

- **Mission:** Acquire, quarantine, verify, seal, and atomically promote the exact authorized ONNX Runtime and LiquidAI finalist artifacts required for a later controlled measurement Session, then prove offline loading inside the approved hardened boundary without performing behavioral evaluation or candidate selection.

- **Base commit:** The parent of the specification-only commit introducing this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.

- **Expected repository state:** Intelligence Track 7B merged; Repository Hardening 1 active; same-filesystem atomic promotion approved; memory upper bounds unresolved; explanation suitability eligible only for controlled empirical evaluation; controlled measurement authorized in principle but acquisition, runtime installation, and execution not yet authorized.

- **Branch:** feat/intelligence-track-8a-controlled-acquisition

- **Change type:** Operator-controlled runtime and candidate acquisition, quarantine verification, local digest generation, sealed atomic promotion, hardened offline-load proof, closed records, tests, documentation, and CI validation that remains artifact-free.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** feat(evals): add controlled measurement acquisition

- **Automatic Git actions:** Cursor must not commit, push, open a pull request, merge, change GitHub settings, publish, release, deploy, or begin full behavioral evaluation automatically.

## Architectural Outcome

Track 8A must answer:

> Can the exact authorized runtime and finalist artifacts be acquired from approved official sources, verified locally, atomically promoted, and loaded offline inside the hardened execution boundary without violating licensing, provenance, resource, network, or authority constraints?

The completed Session must:

1. Preserve deterministic PatchPilot authority.

2. Authorize only the exact runtime and finalist identities committed by prior Tracks.

3. Require explicit operator approval before any network acquisition.

4. Acquire artifacts only from approved official sources.

5. Use a unique external quarantine directory.

6. Record source URLs, immutable revisions, names, sizes, and acquisition timestamps.

7. Compute local SHA-256 digests for every acquired file.

8. Verify expected and observed inventories separately.

9. Verify licenses, notices, tokenizer provenance, configuration provenance, and format.

10. Reject missing, unexpected, changed, executable, remotely loaded, or unapproved files.

11. Preserve no execution from quarantine.

12. Seal verified inventories.

13. Promote with same-filesystem atomic no-replace rename.

14. Prohibit cross-filesystem copy fallback.

15. Stage the exact authorized runtime externally.

16. Prove the runtime and model can be discovered and initialized offline.

17. Perform only the minimum load proof needed to establish staging correctness.

18. Produce hardened execution and network-denial attestations.

19. Measure acquisition, verification, promotion, startup, and loader observations separately.

20. Stop before 4,096-token or 8,192-token generation measurement.

21. Stop before the 24-case behavioral evaluation.

22. Preserve candidate selection as no-selection.

23. Preserve calibration as not-approved.

24. Preserve productionReady: false.

Track 8A authorizes controlled acquisition and offline-load proof only after its specification is committed and its preflight gates pass.

It does not authorize full candidate measurement, evaluation, product integration, or production use.

## Governing Authority

Before planning or performing acquisition, Cursor must reread:

- every repository [AGENTS.md](http://AGENTS.md);

- [README.md](http://README.md);

- [SECURITY.md](http://SECURITY.md);

- [CONTRIBUTING.md](http://CONTRIBUTING.md);

- NOTICE;

- LICENSE;

- .gitignore;

- pyproject.toml;

- uv.lock;

- every protected workflow;

- Repository Hardening 1 governance;

- every architecture and provenance document;

- every current schema and authorization record;

- Track 5 artifact-cache policy and verification implementation;

- Track 6A hardened execution profile and runtime authorization;

- Track 6B runtime staging, corrected adapter contract, and format-resolution records;

- Track 6C candidate eligibility records;

- Track 7 finalist, direct-ONNX, tokenizer, artifact-budget, and selection records;

- Track 7A storage policy, atomic promotion, recovery, and review records;

- Track 7B memory, suitability, controlled-measurement, readiness, and review records;

- current calibration and promotion-gate records;

- current CLI commands and tests;

- Intelligence Track 2 through Track 7B specifications;

- protected post-merge evidence from main.

Do not inspect or modify patchpilot or neural-from-scratch.

Official public sources may be accessed only for the exact authorized artifacts, immutable revisions, licenses, notices, published inventories, and approved runtime distribution.

## Authorized Identities

Track 8A must derive exact values from committed authorization records and must not substitute values from this specification when repository authority differs.

The expected identities are:

### Runtime

- **Runtime family:** ONNX Runtime

- **Authorized version:** v1.31.1

- **Platform:** Linux x86_64

- **Distribution:** official publisher distribution authorized by the committed runtime record

- **Installation model:** external verified staging, not a project dependency

- **Project dependency status:** prohibited

- **Telemetry:** disabled

- **Network fallback:** prohibited

### Candidate

- **Candidate:** LiquidAI/LFM2.5-1.2B-Instruct

- **Source revision:** b9d816ab510f9a28dca37cb182e9da8b0226e13c

- **ONNX revision:** 10f72e70abf67ac0fd7ebf15bc5854726891d864

- **Precision:** FP32

- **Selected model inventory:** 4,717,588,977 bytes

- **Quantization:** prohibited

- **Conversion:** prohibited

- **Community artifacts:** prohibited

Any mismatch with the committed records is a stop condition.

## Invariants

### Deterministic PatchPilot authority

No runtime, candidate, loader, artifact, digest, measurement, or generated output may become authoritative over:

- tenant or organization identity;

- asset identity;

- package identity;

- Product Match Evidence;

- affectedness;

- Finding creation;

- KEV interpretation;

- policy facts;

- P1-P4 priority;

- escalation;

- due dates;

- remediation-queue ordering;

- review state;

- remediation completion;

- PatchPilot audit state.

### Acquisition is operator-controlled

Cursor may implement and prepare acquisition commands, but the human maintainer controls whether acquisition begins.

Before the first network transfer, Cursor must present:

- exact source URL;

- immutable revision;

- expected filenames;

- expected sizes;

- license and notice disposition;

- destination quarantine root;

- available storage;

- planned network commands;

- planned verification commands;

- cleanup procedure;

- stop conditions.

The operator must explicitly authorize that step in the Cursor chat.

No prior architectural approval substitutes for this operator checkpoint.

### External roots only

Runtime and candidate artifacts must remain outside:

- the Git repository;

- sibling repositories;

- the operator home directory when the committed policy prohibits it;

- the build output directory;

- CI workspaces;

- source-controlled paths.

The operator must supply explicit external roots.

The implementation must validate:

- path normalization;

- root confinement;

- separation of runtime and model caches;

- separation of quarantine, verified, rejected, and output roots;

- same-filesystem promotion requirement;

- no symlink escape;

- no identity-bearing path in committed records.

### Network phases

Network authority exists only during the explicit acquisition phase.

The Session must distinguish:

1. **Preflight**

   - no artifact transfer;

   - source and policy validation.

2. **Acquisition**

   - network permitted only to approved official hosts and exact source paths;

   - operator initiated;

   - files written only to quarantine;

   - no execution.

3. **Verification and promotion**

   - network disabled;

   - all files local;

   - no execution from quarantine.

4. **Offline-load proof**

   - OS-level network denial;

   - verified artifacts only;

   - hardened launcher required.

5. **Cleanup and closeout**

   - network disabled;

   - rejected or temporary data handled according to policy.

No network permission may persist into verification, loading, or later measurement.

### Runtime staging

The runtime must:

- be acquired from the approved official source;

- match the authorized version and platform;

- remain external to the project environment;

- not modify pyproject.toml or uv.lock;

- not be installed globally;

- not be installed into the repository virtual environment;

- be inventoried and hashed locally;

- include required license and notice material;

- reject unexpected binaries or shared libraries;

- be sealed and atomically promoted;

- be invoked only through the approved adapter and hardened launcher.

### Candidate acquisition

Candidate acquisition must:

- use the exact immutable revisions;

- acquire only the approved FP32 ONNX inventory;

- acquire the approved tokenizer and configuration inventory;

- reject quantized files;

- reject conversion products;

- reject community mirrors;

- reject unapproved auxiliary files;

- reject remote-code files;

- reject incomplete external-data inventories;

- preserve model, tokenizer, configuration, license, and notice identities separately.

### Local digest authority

Every acquired file must receive a locally computed SHA-256.

The verification record must distinguish:

- upstream-published digest;

- locally computed digest;

- digest authority;

- match result;

- absence of upstream digest.

Absence of an upstream digest does not permit omission of the local digest.

Local digest arrays remain empty until actual acquisition and verification occur.

### Verified promotion

Promotion requires:

- complete expected inventory;

- no unexpected files;

- exact observed sizes;

- local SHA-256 for every file;

- applicable upstream digest matches;

- license and notice presence;

- tokenizer and configuration provenance;

- approved file formats;

- no remote-code requirement;

- verification seal;

- no post-seal mutation;

- same-filesystem identity;

- atomic no-replace rename;

- parent-directory synchronization;

- promotion receipt.

No copy-and-delete fallback is permitted.

### Hardened offline-load proof

Offline-load proof must use:

- linux-bwrap-systemd-v1;

- the approved runtime adapter;

- direct argument vectors;

- no shell;

- verified runtime;

- verified ONNX graph and complete external data;

- verified tokenizer and configuration;

- read-only artifact mounts;

- private writable result directory;

- minimal environment;

- OS-level network denial;

- no home, SSH, cloud, corpus-gold, prior-result, or sibling visibility;

- memory and process limits;

- process-tree cleanup;

- execution attestation.

The proof may:

- initialize the runtime;

- open the verified graph;

- create the runtime session if necessary;

- validate model input and output metadata;

- initialize the tokenizer offline;

- exit without generating a substantive candidate response.

The proof must not:

- run the 24-case corpus;

- perform 4,096-token generation;

- perform 8,192-token generation;

- measure behavioral quality;

- claim memory eligibility;

- select the candidate.

### Resource stop conditions

The acquisition operator must stop if:

- required free disk space is unavailable;

- runtime or model identity differs;

- an unexpected file appears;

- a required file is absent;

- observed size differs outside an authorized rule;

- digest mismatch occurs;

- remote code is required;

- the verified root is on another filesystem;

- promotion would copy;

- runtime staging changes project dependencies;

- offline load attempts network access;

- hardened isolation fails;

- process memory exceeds the existing 12 GiB ceiling during load proof;

- process cleanup fails;

- any current authorization state would be broadened implicitly.

### Result boundaries

Track 8A may produce:

- acquisition manifests;

- locally verified digests;

- quarantine and promotion records;

- runtime verification;

- model verification;

- hardened load attestation;

- loader timing;

- observed loader memory, clearly labeled as load-proof observation only;

- cleanup and retention records.

Track 8A must not produce or claim:

- complete FP32 measurement eligibility;

- behavioral evaluation results;

- grounding or refusal performance;

- candidate score;

- candidate selection;

- calibration approval;

- production readiness.

### Repository contents

No acquired artifact may be committed.

The repository may commit only:

- schemas;

- templates;

- redacted records;

- expected identities;

- locally computed digest values;

- non-sensitive sizes and timestamps;

- verification and promotion receipts without host paths;

- load attestations without identity-bearing host data;

- implementation code;

- tests;

- documentation.

### No gate changes

Do not change:

- corpus contents;

- corpus taxonomy;

- corpus digest;

- metrics;

- invariant gates;

- percentage thresholds;

- calibration status;

- promotion status;

- 8 GiB artifact ceiling;

- 12 GiB process-memory ceiling.

## Assumed Repository State

Before implementation, Cursor must prove:

- repository root is patchpilot-intelligence-evals;

- local main equals origin/main;

- Intelligence Track 7B is merged;

- Repository Hardening 1 is merged;

- specification-only commit parent equals origin/main;

- working tree is clean after the specification commit;

- protected checks pass on synchronized main;

- repository license remains Apache-2.0;

- Python remains &gt;=3.12,&lt;3.13;

- uv.lock exists and validates;

- exact finalist and revision identities match committed records;

- storage-only blocker remains resolved;

- atomic promotion remains approved;

- memory envelopes remain unresolved;

- controlled measurement is authorized in principle only;

- ONNX Runtime identity is authorized but uninstalled;

- runtime staging and adapter contracts are approved;

- hardened execution is approved;

- candidate selection remains no-selection;

- acquisition remains not acquired;

- execution remains not executed;

- local runtime and artifact digests are empty;

- calibration remains not approved;

- no real model or runtime artifact exists in the repository;

- no sibling repository is nested in the Git tree;

- realModelExecuted remains false;

- productionReady remains false.

If any material assumption is false, stop and report the conflict.

## Allowed Change Surface

Permitted:

- docs/specs/[intelligence-track-8a.md](http://intelligence-track-8a.md);

- controlled-acquisition architecture;

- runtime and candidate acquisition procedures;

- acquisition allowlist;

- artifact inventory, verification, promotion, load-proof, retention, and cleanup schemas;

- structured external-artifact records;

- source modules for acquisition planning, source allowlisting, streaming transfer coordination, inventory validation, digest verification, promotion coordination, hardened load proof, attestation, and closeout;

- operator-confirmation checkpoints;

- deterministic synthetic tests;

- optional manually invoked acquisition commands;

- Repository Contracts updates;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, and governance documentation;

- .gitignore for local operator outputs and cache metadata where needed.

Not permitted:

- adding ONNX Runtime to project dependencies;

- committing acquired artifacts;

- automatic acquisition in CI;

- scheduled acquisition;

- automatic model-hub access;

- conversion;

- quantization;

- full corpus evaluation;

- behavioral scoring;

- candidate selection;

- PatchPilot integration;

- changing GitHub settings;

- publication;

- release;

- deployment.

## Required Repository Additions

The repository must include the conceptual equivalent of:

text</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">docs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── architecture/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [controlled-artifact-acquisition.md](http://controlled-artifact-acquisition.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [external-runtime-installation.md](http://external-runtime-installation.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [hardened-offline-load-proof.md](http://hardened-offline-load-proof.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [track8b-measurement-prerequisites.md](http://track8b-measurement-prerequisites.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── operations/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [runtime-acquisition-runbook.md](http://runtime-acquisition-runbook.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [candidate-acquisition-runbook.md](http://candidate-acquisition-runbook.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [acquisition-recovery.md](http://acquisition-recovery.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [artifact-cleanup.md](http://artifact-cleanup.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── provenance/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [track8a-acquisition-evidence.md](http://track8a-acquisition-evidence.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">└── specs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── [intelligence-track-8a.md](http://intelligence-track-8a.md)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">schemas/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── acquisition-plan.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── acquisition-allowlist.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── acquired-runtime-manifest.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── acquired-candidate-manifest.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── local-artifact-digests.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── hardened-load-attestation.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── acquisition-closeout.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">└── track8b-measurement-prerequisites.schema.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">candidates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── authorization/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── acquisition-plan.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── acquisition-allowlist.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── track8b-measurement-prerequisites.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── templates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── acquired-runtime-manifest-template.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── acquired-candidate-manifest-template.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── local-artifact-digests-template.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── hardened-load-attestation-template.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── acquisition-closeout-template.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">└── local-records/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── ignored by Git except for explicitly redacted approved records</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">src/patchpilot_intelligence_evals/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── acquisition_[plan.py](http://plan.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── acquisition_[allowlist.py](http://allowlist.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── acquisition_[runner.py](http://runner.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── acquired_artifact_[validation.py](http://validation.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── runtime_[staging.py](http://staging.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── candidate_[staging.py](http://staging.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── hardened_load_[proof.py](http://proof.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── acquisition_[closeout.py](http://closeout.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">└── track8b_[prerequisites.py](http://prerequisites.py)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">tests/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── test_acquisition_[plan.py](http://plan.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── test_acquisition_[allowlist.py](http://allowlist.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── test_acquisition_[runner.py](http://runner.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── test_acquired_artifact_[validation.py](http://validation.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── test_runtime_[staging.py](http://staging.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── test_candidate_[staging.py](http://staging.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── test_hardened_load_[proof.py](http://proof.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">├── test_acquisition_[closeout.py](http://closeout.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">└── test_track8b_[prerequisites.py](http://prerequisites.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794493800000,&quot;dataSource&quot;:0}">

Exact paths may differ only to follow established repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed schemas and records for:

1. acquisition plan;

2. source and host allowlist;

3. acquired runtime manifest;

4. acquired candidate manifest;

5. local artifact digests;

6. hardened load attestation;

7. acquisition closeout;

8. Track 8B measurement prerequisites.

Every schema must:

- have a stable ID and explicit version;

- use additionalProperties: false;

- distinguish expected and observed data;

- identify exact immutable revisions;

- distinguish upstream and local digests;

- prohibit credentials and access tokens;

- prohibit hostnames and IP addresses;

- prohibit identity-bearing local paths;

- prohibit raw environment contents;

- prohibit model data from being embedded;

- preserve productionReady: false;

- preserve candidate no-selection;

- distinguish acquisition, verification, promotion, loading, measurement, and evaluation states.

Committed records may contain digest values but not local cache paths.

## Multi-Agent Execution Model

Cursor Plan is the parent controlled-acquisition orchestrator.

Use Grok 4.7 Extra High for:

- acquisition authority;

- source allowlisting;

- licenses and provenance;

- supply-chain validation;

- runtime staging;

- model verification;

- hardened load proof;

- stop decisions;

- independent verification.

Delegate the work to these specialists.

### Agent 1: Acquisition-authority specialist

Owns:

- exact authorized identities;

- source allowlist;

- immutable revisions;

- license and notice preflight;

- operator checkpoint.

### Agent 2: Runtime-staging specialist

Owns:

- runtime inventory;

- official distribution;

- runtime quarantine;

- runtime digest verification;

- external verified staging;

- project-dependency prohibition.

### Agent 3: Candidate-acquisition specialist

Owns:

- model, ONNX, tokenizer, and configuration inventory;

- official source paths;

- acquisition into quarantine;

- incomplete-transfer handling;

- unexpected-file rejection.

### Agent 4: Verification and promotion specialist

Owns:

- local SHA-256;

- size and format validation;

- verification seals;

- same-filesystem atomic promotion;

- receipts;

- recovery.

### Agent 5: Hardened-load specialist

Owns:

- adapter integration;

- hardened launcher;

- offline network denial;

- read-only mounts;

- runtime and graph initialization;

- no-generation proof;

- process cleanup.

### Agent 6: Closeout and readiness specialist

Owns:

- retention;

- rejected-artifact cleanup;

- redacted records;

- Track 8B prerequisites;

- preserved no-selection and non-production states.

### Agent 7: Independent verification specialist

Runs after implementation and operator-authorized acquisition.

Must not own:

- acquisition authority;

- transfers;

- runtime staging;

- candidate staging;

- verification;

- promotion;

- load proof;

- closeout.

### Coordination Rules

The parent agent must:

- complete read-only preflight before any transfer;

- assign exclusive ownership;

- stop before acquisition for operator approval;

- serialize network transfer and verification phases;

- disable network before verification;

- permit no execution from quarantine;

- integrate records centrally;

- stop on every mismatch;

- commission a fresh independent verifier.

## Ordered Execution Plan

### Task 1: Verify the Track 7B Baseline

#### Allowed files or subsystem

Read-only Git state, records, workflows, architecture, provenance, tests, and authorization.

#### Required behavior

Confirm every assumed-state item and exact identity.

Produce the proposed file ownership and acquisition checkpoint.

#### Tests

Run safe Git and repository validation as needed.

#### Done condition

The baseline is proven and no transfer has occurred.

### Task 2: Implement Acquisition Plans, Allowlists, and Operator Checkpoint

#### Allowed files or subsystem

Schemas, plans, allowlists, validators, CLI, runbooks, and tests.

#### Required behavior

Define exact:

- source hosts;

- URLs or immutable source patterns;

- revisions;

- expected files;

- expected sizes;

- licenses;

- destination classes;

- network phase;

- timeout and retry policy;

- cleanup policy;

- operator-approval record.

No transfer may occur until the operator approves the exact plan in the Cursor chat.

#### Tests

Validate allowed and prohibited sources, revisions, filenames, and states.

#### Done condition

A complete plan awaits explicit operator approval.

### Task 3: Acquire and Verify the Runtime

#### Allowed files or subsystem

External runtime quarantine, acquisition runner, runtime manifest, digests, and redacted evidence.

#### Required behavior

After explicit operator approval:

- acquire only the authorized runtime;

- write only to runtime quarantine;

- inventory all files;

- calculate local SHA-256 values;

- verify version, platform, license, notice, binary format, and shared libraries;

- reject unexpected files;

- disable network;

- seal and atomically promote;

- record verified runtime identity.

Do not modify project dependencies.

#### Tests

Run preflight and synthetic tests before real transfer.

#### Done condition

The runtime is externally verified or the Session stops.

### Task 4: Acquire and Verify Candidate Artifacts

#### Allowed files or subsystem

External model quarantine, candidate manifest, tokenizer and configuration inventory, local digests, and redacted evidence.

#### Required behavior

After runtime verification and continued operator authority:

- acquire only the authorized FP32 ONNX inventory;

- acquire approved tokenizer and configuration files;

- acquire applicable license and notice files;

- reject missing and unexpected artifacts;

- compute local SHA-256;

- verify sizes and identities;

- prohibit execution;

- disable network;

- seal and atomically promote.

#### Tests

Run inventory and failure checks before promotion.

#### Done condition

Candidate artifacts are verified externally or the Session stops.

### Task 5: Produce Hardened Offline-Load Proof

#### Allowed files or subsystem

Verified external runtime and candidate roots, hardened launcher, adapter, load-proof records, and result directory.

#### Required behavior

Use the approved hardened boundary to:

- mount verified inputs read-only;

- deny host network;

- construct minimal environment;

- initialize the runtime;

- open the verified ONNX artifact;

- validate input and output metadata;

- initialize tokenizer offline where required;

- perform no substantive generation;

- record startup and loader observations;

- terminate the process tree;

- produce an attestation.

#### Tests

Prove network denial, filesystem isolation, process cleanup, and no-generation behavior.

#### Done condition

Offline loading succeeds or fails with a structured result.

### Task 6: Close Acquisition, Retention, and Recovery

#### Allowed files or subsystem

Closeout records, rejected files, quarantine attempts, verified stores, cleanup logic, and documentation.

#### Required behavior

Record:

- successful and failed attempts;

- promoted identities;

- retained evidence;

- rejected-artifact cleanup;

- incomplete-transfer cleanup;

- storage reclaimed;

- operator decisions;

- no Git-tracked artifact.

#### Tests

Validate idempotency and path confinement.

#### Done condition

External state is closed and auditable.

### Task 7: Decide Track 8B Measurement Prerequisites

#### Allowed files or subsystem

Prerequisite schema, record, validator, CLI, and tests.

#### Required behavior

Track 8B may be marked ready only when:

- runtime verification passes;

- model verification passes;

- tokenizer and configuration verification pass;

- all local digests exist;

- atomic promotion passes;

- hardened load proof passes;

- network denial passes;

- no artifact mismatch remains;

- no project dependency changed;

- no selection or production authority is implied.

Preserve measurement as not performed.

#### Tests

Validate ready and not-ready paths.

#### Done condition

Track 8B receives an evidence-backed prerequisite decision.

### Task 8: Documentation, CI, and Independent Verification

#### Allowed files or subsystem

Documentation, redacted committed records, Repository Contracts, complete diff, and external-state evidence.

#### Required behavior

Document the complete acquisition and load-proof result.

CI must remain artifact-free and must validate schemas, templates, redacted records, and synthetic behavior only.

A fresh independent verifier must:

- inspect committed and external identities;

- recompute selected local digests where feasible;

- verify no repository artifact exists;

- verify no dependency changed;

- verify network denial;

- verify no generation or behavioral evaluation occurred;

- verify all disabled authority states.

#### Tests

Run every command in Verification.

#### Done condition

Track 8A is ready for Principal Architect review.

## Out of Scope

Track 8A must not:

- run the 24-case behavioral corpus;

- perform 4,096-token or 8,192-token generation measurement;

- claim the memory blocker is closed;

- claim behavioral suitability is measured;

- select the candidate;

- approve production use;

- modify PatchPilot;

- modify neural-from-scratch;

- change corpus, metrics, gates, calibration, storage ceiling, or memory ceiling;

- convert or quantize artifacts;

- publish or redistribute artifacts;

- commit binaries or model files;

- automate acquisition in CI;

- create a release;

- deploy.

## Stop Conditions

Stop immediately if:

1. Specification parent differs from origin/main.

2. Working tree contains unrelated changes.

3. Track 7B is not merged.

4. Protected checks fail on main.

5. Identity or revision differs from committed authority.

6. Exact acquisition plan is not approved by the operator.

7. Source is unofficial or redirects to an unauthorized host.

8. License or notice differs.

9. Required file is missing.

10. Unexpected file appears.

11. Size or digest mismatch occurs.

12. Remote code is required.

13. Quantization or conversion is required.

14. Runtime installation would change project dependencies.

15. Cache roots are not external and same-filesystem where required.

16. Promotion would copy.

17. Network cannot be disabled before verification or loading.

18. Hardened isolation fails.

19. Loader process exceeds 12 GiB.

20. Process-tree cleanup fails.

21. Full evaluation would be required to prove loading.

22. A sibling repository must be accessed.

23. Work cannot fit in one PR-sized branch.

On a stop condition:

- cease transfer or execution;

- preserve evidence;

- reject or quarantine affected files;

- do not broaden authorization;

- report the smallest corrective decision.

## Verification

Pass requires:

- uv sync --frozen;

- Ruff format and lint;

- strict mypy;

- complete pytest suite;

- corpus and baseline validation;

- every merged Track validator;

- fixture, comparison, and calibration validation;

- workflow and dependency policy validation;

- every Track 8A schema and record validation;

- acquisition-plan validation;

- source-allowlist validation;

- runtime-manifest validation;

- candidate-manifest validation;

- local-digest validation;

- seal and promotion validation;

- hardened-load attestation validation;

- network-denial validation;

- process-cleanup validation;

- closeout validation;

- Track 8B prerequisite validation;

- prohibited-artifact scan;

- Git-tracked binary and model scan;

- dependency and lockfile diff check;

- documentation and relative-link checks;

- git diff --check;

- git status --short --branch.

Also confirm:

- no acquired artifact is inside Git;

- no runtime was added to project dependencies;

- no conversion or quantization occurred;

- no full behavioral evaluation occurred;

- no 4,096-token or 8,192-token generation measurement occurred;

- no candidate was selected;

- calibration remains not-approved;

- selectionOutcome remains no-selection;

- measurementPerformed remains false;

- realModelExecuted reflects only the precise load-proof semantics defined by the approved schema and must not imply inference;

- productionReady remains false.

## Handoff Requirements

Return one consolidated handoff containing:

1. Outcome

2. Base commit, branch, and working-tree state

3. Multi-agent execution summary

4. Track 7B baseline

5. Operator acquisition checkpoint

6. Authorized sources and revisions

7. Runtime acquisition result

8. Runtime inventory and local digests

9. Candidate acquisition result

10. Model, tokenizer, configuration, license, and notice inventories

11. Local candidate digests

12. Quarantine and promotion results

13. Storage usage

14. Hardened offline-load result

15. Network-denial result

16. Process-cleanup result

17. Loader observations

18. Acquisition closeout

19. Rejected or incomplete attempts

20. Track 8B prerequisites

21. Files changed

22. External files created

23. Dependency and lockfile impact

24. Every verification command and result

25. CI changes

26. Independent verification

27. Scope compliance

28. Unresolved decisions

29. Residual risks

30. Exact Track 8B recommendation

31. Proposed commit

32. Proposed PR title and summary

33. Required post-merge steps

Final verdict must be exactly one of:

- TRACK 8B CONTROLLED MEASUREMENT READY

- TRACK 8B CONTROLLED MEASUREMENT READY WITH DOCUMENTED RESIDUALS

- TRACK 8B CONTROLLED MEASUREMENT NOT READY

- BLOCKED BY UNRESOLVED AUTHORITY

Explicitly confirm:

- exact artifacts acquired or not acquired;

- no acquired artifact entered Git;

- no runtime dependency entered the project;

- no conversion or quantization occurred;

- no full behavioral evaluation occurred;

- no 4,096-token or 8,192-token generation measurement occurred;

- no candidate was selected;

- no sibling repository was accessed;

- no automatic commit, push, PR, or merge occurred;

- no GitHub setting changed;

- no package was published;

- no release or deployment occurred;

- calibration remains not-approved;

- selectionOutcome remains no-selection;

- measurementPerformed remains false;

- productionReady remains false.

End with exactly one:

INTELLIGENCE TRACK 8A READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT

or:

INTELLIGENCE TRACK 8A BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW