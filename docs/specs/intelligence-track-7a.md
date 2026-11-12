Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 7A: Artifact-Budget Model Review and Storage-Safety Analysis

## Identity

- **Repository:** patchpilot-intelligence-evals

- **Session ID:** Intelligence Track 7A

- **Mission:** Determine whether the approved external artifact-cache design can verify and promote an artifact set safely on one filesystem without retaining two complete model copies simultaneously, implement and test the resulting storage-state model using bounded synthetic artifacts, and recalculate Track 7 finalist storage eligibility without changing the approved 8 GiB artifact ceiling or authorizing acquisition.

- **Base commit:** The parent of the specification-only commit introducing this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.

- **Expected repository state:** Intelligence Track 7 and Repository Hardening 1 merged; protected Validation, CodeQL, and Dependency Review active; LiquidAI/LFM2.5-1.2B-Instruct recorded as the sole Track 7 finalist but disqualified; Track 8 acquisition not authorized; no runtime, model, tokenizer, configuration, ONNX, or conversion artifact acquired; calibration not approved; productionReady false.

- **Branch:** feat/intelligence-track-7a-storage-safety

- **Change type:** Artifact-cache state-machine implementation, storage-safety analysis, closed schemas, budget arithmetic, bounded synthetic tests, documentation, provenance, and CI enforcement. No artifact acquisition, runtime installation, candidate selection, conversion, quantization, or inference.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** feat(evals): implement atomic artifact promotion

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, merge, modify Git history, change GitHub repository settings, acquire artifacts, install a runtime, convert a model, execute inference, publish a package, create a release, or deploy.

## Architectural Outcome

Intelligence Track 7A must answer:

> Can an operator-controlled, same-filesystem artifact workflow verify a quarantine artifact set in place and atomically promote that same verified identity into the verified state without retaining a second complete model copy, while preserving fail-closed provenance, immutability, crash recovery, and execution prohibition?

The completed Session must:

1. Preserve the approved 8 GiB model-artifact ceiling.

2. Distinguish artifact size from temporary verification overhead and runtime-staging allowance.

3. Define the authoritative peak-disk-usage formula.

4. Define cache-device and filesystem identity requirements.

5. Define an in-place verification process for quarantine artifacts.

6. Define immutable verification-manifest generation.

7. Define an atomic same-filesystem promotion operation.

8. Reject cross-filesystem promotion.

9. Reject promotion through copy-and-delete fallback.

10. Preserve prohibition on execution from quarantine.

11. Preserve prohibition on execution during verification.

12. Detect file mutation during hashing and sealing.

13. Detect symlink, traversal, hard-link, and special-file hazards.

14. Define crash-consistent journal and recovery behavior.

15. Define verified-state immutability and revalidation rules.

16. Define rejection and cleanup behavior.

17. Generate machine-readable storage proofs using bounded synthetic artifacts.

18. Recalculate the Track 7 finalist’s storage footprint under each approved storage model.

19. Preserve FP32 memory as unknown.

20. Preserve explanation suitability as unresolved.

21. Preserve candidate weightedScore: null.

22. Preserve selectionOutcome: no-selection.

23. Preserve Track 8 authorizationOutcome: not-authorized.

24. Preserve every acquisition and execution state as disabled.

25. Preserve productionReady: false.

This is an implementation Session.

It authorizes repository-owned schemas, records, validation modules, cache-state logic, bounded synthetic fixtures, arithmetic checks, tests, CLI commands, documentation, provenance, and Repository Contracts integration.

It does not authorize real artifact acquisition or candidate selection.

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

- every protected workflow;

- Repository Hardening 1 governance and required-check records;

- every architecture document;

- every provenance document;

- every current JSON Schema;

- every candidate, runtime, cache, acquisition, conversion, execution, readiness, and implementation-review record;

- Track 4 hardware profile and candidate-selection criteria;

- Track 5 external artifact-cache policy and implementation;

- Track 5 artifact-verification implementation;

- Track 5 real-candidate manifest;

- Track 6A hardened execution profile;

- Track 6B runtime-staging and corrected ONNX adapter contract;

- Track 6C artifact-budget and direct-ONNX records;

- Track 7 candidate discovery, finalist, budget, suitability, selection, Track 8 authorization, and implementation-review records;

- current calibration and promotion-gate records;

- existing CLI commands;

- existing tests;

- Intelligence Track 2 through Track 7 specifications;

- Repository Hardening 1 specification and merged evidence.

Do not inspect local files in patchpilot or neural-from-scratch.

Public read-only research is permitted only for:

- official Linux filesystem and rename documentation;

- official Python filesystem API documentation;

- official POSIX or Linux rename semantics;

- official fsync, directory-sync, link, stat, and filesystem documentation;

- official documentation for filesystems identified generically by capability, without recording identity-bearing host paths;

- original maintainers of any repository dependency already authorized.

No external model, tokenizer, runtime, or candidate research is required.

## Invariants

### Deterministic PatchPilot authority

No storage calculation, cache state, artifact manifest, candidate, or research conclusion may become authoritative over:

- organization or tenant identity;

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

- remediation-queue order;

- priority review;

- Finding lifecycle;

- remediation completion;

- PatchPilot audit state.

All future model outputs remain advisory evaluation data.

### Existing candidate decision remains authoritative

Track 7A is not a candidate-selection Session.

The following remain authoritative:

- finalist: LiquidAI/LFM2.5-1.2B-Instruct;

- finalist selected-model inventory: 4,717,588,977 bytes;

- previously calculated complete footprint: 9,446,591,609 bytes;

- approved artifact ceiling: 8,589,934,592 bytes;

- FP32 peak memory: unknown;

- explanation suitability: unresolved;

- weightedScore: null;

- qualifyingCandidateCount: 0;

- selectionOutcome: no-selection;

- Track 8 authorizationOutcome: not-authorized;

- runtime installation: not-installed;

- acquisition: not-acquired;

- conversion: not-performed;

- execution: not-executed;

- realModelExecuted: false;

- productionReady: false.

Track 7A may recalculate storage eligibility only.

Track 7A must not change legal, tokenizer, explanation-suitability, memory, execution, or selection outcomes.

### The 8 GiB ceiling is unchanged

The approved artifact ceiling remains:

8,589,934,592 bytes.

Track 7A must not reinterpret the ceiling silently.

The storage model must distinguish:

1. **Logical artifact footprint**

   - all files required to represent the selected model artifact set;

   - ONNX graph;

   - ONNX external-data files;

   - tokenizer;

   - configuration;

   - required metadata, license, and notice files.

2. **Verification working overhead**

   - bounded metadata;

   - hash buffers;

   - journal;

   - temporary manifest;

   - filesystem and directory metadata;

   - explicitly modeled temporary files.

3. **Runtime-staging allowance**

   - separately authorized runtime files;

   - not model-artifact duplication.

4. **Transient acquisition overhead**

   - downloader-specific temporary files;

   - partial files;

   - archive extraction;

   - transport cache;

   - not authorized in Track 7A.

Track 7A must state which categories the 8 GiB ceiling governs.

Any changed interpretation requires a clear Principal Architect decision later.

### No real acquisition or inference

Track 7A must not:

- download runtime binaries, wheels, archives, libraries, or images;

- download model weights;

- download tokenizers;

- download configurations;

- download ONNX graphs or external-data files;

- populate a persistent real artifact cache;

- install a runtime;

- parse a real ONNX graph;

- perform conversion;

- perform quantization;

- execute inference;

- contact a model provider or model hub for artifacts;

- publish or redistribute artifacts.

Only bounded synthetic files created locally by tests are permitted.

### Same-filesystem atomic promotion

An atomic in-place promotion may be considered only when:

- quarantine and verified state directories are on the same mounted filesystem;

- source and destination device identities match;

- the filesystem supports atomic rename with the required semantics;

- promotion uses rename rather than byte copying;

- no copy-and-delete fallback exists;

- the expected target state does not already exist;

- the verified manifest is sealed before promotion;

- every artifact file is closed before final verification;

- required file data is synchronized before promotion;

- verification metadata is synchronized before promotion;

- the quarantine directory is synchronized before rename where supported;

- the destination parent directory is synchronized after rename;

- promotion remains fail-closed when any synchronization step fails;

- recovery behavior is deterministic after interruption.

Cross-device rename must fail with a structured category and must not trigger copying.

### Verification before promotion

The cache must preserve this order:

1. acquire into a unique quarantine attempt directory in a future Session;

2. prohibit execution and loading;

3. close all writer handles;

4. normalize and validate inventory;

5. reject traversal and symlinks;

6. inspect regular-file types and approved suffixes;

7. capture file metadata;

8. stream SHA-256 for every expected file;

9. re-read file metadata;

10. reject files changed during verification;

11. verify expected sizes and digests where available;

12. generate canonical verification metadata;

13. generate combined inventory identity;

14. write temporary sealed manifest;

15. synchronize file data and metadata;

16. atomically install the sealed manifest;

17. synchronize the quarantine directory;

18. atomically rename the complete attempt directory to verified state;

19. synchronize the verified-state parent;

20. emit a promotion receipt.

The exact implementation may vary when official operating-system semantics require it, but it must preserve the same fail-closed guarantees.

### No mutation during sealing

Verification must reject an artifact when any relevant property changes during the verification window, including:

- size;

- modification time at available precision;

- inode or file identity where applicable;

- device identity;

- file type;

- link count where policy requires uniqueness;

- path;

- content digest;

- expected inventory membership.

Synthetic race tests must attempt mutation during verification.

A successful digest alone is insufficient when the file changed during the verification process.

### Symlink, traversal, hard-link, and special-file safety

The verification and promotion boundary must reject:

- absolute artifact paths;

- .. traversal;

- symlinks;

- dangling symlinks;

- symlink escape;

- hard links to files outside the attempt directory;

- device files;

- sockets;

- FIFOs;

- unsupported special files;

- files resolving outside the attempt root;

- duplicate normalized paths;

- case-collision risks where the filesystem is case-insensitive;

- destination collisions.

If hard-link uniqueness cannot be proven reliably, multiple-link regular files must fail closed.

### Quarantine remains non-executable

Quarantine artifacts must never be eligible for:

- model loading;

- tokenizer loading;

- runtime execution;

- candidate execution;

- direct adapter use;

- evaluation.

The existence of digests or a partial manifest does not change quarantine authority.

Only a successfully promoted verified identity may become eligible for a later separately authorized Session.

### Verified-state immutability

Verified state must be immutable by repository policy.

Any change to a verified file must:

- invalidate the verification identity;

- prevent execution eligibility;

- require a new quarantine attempt;

- produce a new digest and inventory identity;

- never mutate the prior record silently.

Track 7A may implement verification and detection logic but must not claim kernel-enforced immutability unless that control is proven.

### Crash consistency

Define recovery for interruption:

- before manifest generation;

- during hashing;

- after temporary manifest write;

- after manifest synchronization;

- immediately before rename;

- immediately after rename but before parent-directory synchronization;

- after promotion receipt generation begins.

Recovery must classify every attempt as:

- resumable quarantine;

- rejected;

- verified;

- indeterminate and blocked pending operator review.

The state machine must not guess that an indeterminate attempt is verified.

### Cleanup and storage reclamation

Cleanup must:

- act only on explicitly identified attempts;

- prohibit deletion of a verified identity referenced by an evaluation record;

- reject paths outside the cache root;

- reject symlinked cleanup targets;

- preserve rejection metadata;

- avoid following links;

- report reclaimed bytes;

- remain idempotent;

- fail closed on partial deletion.

Track 7A must not implement automated background deletion.

### Sparse files and apparent size

Budget calculation must distinguish:

- logical file size;

- allocated blocks;

- sparse representation;

- compressed transport size;

- extracted size.

The 8 GiB artifact ceiling must use logical required artifact size, not sparse allocated size or compressed download size.

Synthetic sparse files may test arithmetic, but sparse allocation must not be used to claim that a model fits the logical artifact ceiling.

### Candidate storage recalculation

Track 7A may calculate these models:

#### Model A: Copy promotion

peak = quarantine artifact set + verified artifact set + verification overhead + runtime-staging allowance

This represents the previous conservative calculation.

#### Model B: Same-filesystem atomic rename

peak = one artifact set + verification overhead + runtime-staging allowance

This is eligible only if the complete atomic-promotion contract passes.

#### Model C: Cross-filesystem promotion

Must remain ineligible.

No copy fallback is allowed.

The recalculation must preserve the exact selected-model inventory of 4,717,588,977 bytes unless committed Track 7 records prove a correction is necessary.

### Memory and suitability remain unresolved

A passing storage recalculation does not resolve:

- FP32 peak process memory;

- model startup time;

- Finding Explanation Assistant suitability;

- safety limitations;

- citation-ID behavior;

- refusal behavior;

- uncertainty behavior;

- production readiness.

No candidate may be selected in Track 7A.

### No gate changes

Do not change:

- corpus contents;

- corpus taxonomy;

- corpus digest;

- metric definitions;

- invariant gates;

- percentage gates;

- calibration status;

- promotion status.

Calibration remains not-approved.

## Assumed Repository State

Before implementation, Cursor must prove:

- repository root is patchpilot-intelligence-evals;

- local main equals origin/main;

- Intelligence Track 7 is merged;

- Repository Hardening 1 is merged;

- specification-only commit parent equals origin/main;

- working tree is clean after the specification commit;

- protected Validation, CodeQL, and Dependency Review are active;

- protected CI passes on synchronized main;

- repository license remains Apache-2.0;

- Python remains &gt;=3.12,&lt;3.13;

- uv.lock exists and validates;

- the 24-case corpus and approved digest are unchanged;

- candidate protocol remains version 1.0.0;

- existing cache states remain quarantine, verified, and rejected;

- existing cache implementation rejects repository and sibling roots;

- existing cache implementation rejects traversal and symlink escape;

- hardened mechanism remains linux-bwrap-systemd-v1;

- authorized future runtime identity remains onnxruntime v1.31.1;

- runtime remains uninstalled;

- corrected adapter requires verified ONNX executable artifacts;

- Track 7 records exactly eight discovery candidates and one finalist;

- finalist remains LiquidAI/LFM2.5-1.2B-Instruct;

- selected-model inventory remains 4,717,588,977 bytes;

- complete planned footprint remains 9,446,591,609 bytes;

- approved ceiling remains 8,589,934,592 bytes;

- FP32 peak memory remains unknown;

- explanation suitability remains unresolved;

- weightedScore remains null;

- qualifying candidate count remains zero;

- selection remains no-selection;

- Track 8 remains not authorized;

- calibration remains not approved;

- no runtime or model artifact exists;

- no sibling repository is nested in the Git tree;

- realModelExecuted remains false;

- productionReady remains false.

If any material assumption is false, stop and report the conflict.

## Allowed Change Surface

Permitted:

- docs/specs/[intelligence-track-7a.md](http://intelligence-track-7a.md);

- artifact-budget architecture;

- cache-state-machine architecture;

- atomic-promotion architecture;

- storage-safety analysis;

- crash-recovery design;

- cleanup design;

- Track 7 finalist storage-recalculation records;

- Track 8A readiness or withholding records;

- closed schemas required by this Session;

- source modules implementing storage arithmetic, filesystem identity checks, verification sealing, synthetic atomic promotion, recovery classification, cleanup validation, and readiness logic;

- CLI validation and synthetic execution commands;

- bounded deterministic tests using temporary directories and synthetic files;

- Repository Contracts updates;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, and governance documentation;

- .gitignore only when required for generated synthetic outputs;

- pyproject.toml and uv.lock only if an essential non-runtime validation dependency is proven necessary, licensed, and approved.

Not permitted:

- real artifact acquisition;

- runtime installation;

- real ONNX parsing;

- inference;

- conversion;

- quantization;

- changing the 8 GiB ceiling;

- changing the 12 GiB memory ceiling;

- resolving memory through assumptions;

- resolving explanation suitability through assumptions;

- selecting a candidate;

- changing corpus or gates;

- inspecting sibling repositories;

- PatchPilot integration;

- GitHub repository-setting changes;

- package publication;

- release;

- deployment.

## Required Repository Additions

The repository must include the conceptual equivalent of:

```text
docs/
├── architecture/
│   ├── artifact-budget-model.md
│   ├── atomic-artifact-promotion.md
│   ├── artifact-cache-recovery.md
│   └── track8a-storage-readiness.md
├── provenance/
│   └── track7a-storage-analysis.md
└── specs/
    └── intelligence-track-7a.md

schemas/
├── artifact-storage-policy.schema.json
├── artifact-promotion-attempt.schema.json
├── artifact-verification-seal.schema.json
├── artifact-promotion-receipt.schema.json
├── artifact-recovery-decision.schema.json
├── artifact-budget-recalculation.schema.json
└── track8a-storage-readiness.schema.json

candidates/
└── authorization/
    ├── artifact-storage-policy.json
    ├── artifact-budget-recalculation.json
    └── track8a-storage-readiness.json

candidates/
└── templates/
    ├── artifact-promotion-attempt-template.json
    ├── artifact-verification-seal-template.json
    ├── artifact-promotion-receipt-template.json
    └── artifact-recovery-decision-template.json

src/patchpilot_intelligence_evals/
├── storage_budget.py
├── filesystem_identity.py
├── verification_seal.py
├── atomic_promotion.py
├── cache_recovery.py
├── cache_cleanup.py
└── track8a_readiness.py

tests/
├── test_storage_budget.py
├── test_filesystem_identity.py
├── test_verification_seal.py
├── test_atomic_promotion.py
├── test_cache_recovery.py
├── test_cache_cleanup.py
└── test_track8a_readiness.py
```

Exact filenames may differ only to follow existing repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and records for:

1. artifact storage policy;

2. artifact promotion attempt;

3. artifact verification seal;

4. artifact promotion receipt;

5. artifact recovery decision;

6. artifact-budget recalculation;

7. Track 8A storage readiness.

Every schema must:

- have a stable schema ID;

- declare an explicit version;

- use additionalProperties: false;

- distinguish logical size, allocated size, and transient overhead;

- distinguish quarantine, verified, rejected, and indeterminate states;

- identify filesystem and device equality without recording an identity-bearing host path;

- represent synchronization steps;

- represent pre-verification and post-verification metadata;

- represent expected and observed artifact identities;

- prohibit secrets and tenant identifiers;

- prohibit hostnames and IP addresses;

- prohibit identity-bearing local paths;

- prohibit claims that real acquisition occurred;

- preserve locally observed real-artifact digests as empty;

- preserve runtimeInstallationStatus: not-installed;

- preserve acquisitionStatus: not-acquired;

- preserve conversionStatus: not-performed;

- preserve executionStatus: not-executed;

- preserve realModelExecuted: false;

- preserve productionReady: false;

- support explicit fail-closed and not-ready outcomes.

The Track 8A record must preserve:

- selectionOutcome: no-selection;

- Track 8 authorizationOutcome: not-authorized;

- weightedScore: null;

- qualifyingCandidateCount: 0;

- FP32 peak memory: unresolved;

- explanation suitability: unresolved;

- empty locally observed artifact-digest arrays.

## Storage-State Machine

The implementation must represent these states:

- quarantine-open;

- quarantine-closed;

- verifying;

- sealed;

- promoting;

- verified;

- rejected;

- indeterminate.

Authorized transitions:

```text
quarantine-open -> quarantine-closed
quarantine-closed -> verifying
verifying -> sealed
verifying -> rejected
sealed -> promoting
sealed -> rejected
promoting -> verified
promoting -> indeterminate
indeterminate -> rejected
indeterminate -> verified only through explicit recovery proof
```

Prohibited transitions include:

```text
quarantine-open -> verified
quarantine-closed -> verified
verifying -> verified
rejected -> verified
verified -> quarantine
verified -> rejected through silent mutation
```

A new acquisition attempt is required after rejection.

## Multi-Agent Execution Model

Cursor Plan is the parent storage-safety orchestrator.

Use Grok 4.7 Extra High for:

- storage-model authority;

- filesystem and atomicity decisions;

- crash-consistency design;

- race-condition analysis;

- security boundaries;

- readiness decisions;

- conflicts;

- independent final verification.

Delegate parallel read-only investigation and controlled implementation to these specialists.

### Agent 1: Storage-budget specialist

Owns:

- authoritative budget categories;

- logical versus allocated size;

- peak-disk formulas;

- Track 7 finalist recalculation;

- exact-boundary arithmetic.

### Agent 2: Filesystem and atomicity specialist

Owns:

- same-device checks;

- rename semantics;

- synchronization order;

- cross-device rejection;

- destination-collision behavior;

- filesystem capability requirements.

### Agent 3: Verification-seal specialist

Owns:

- inventory normalization;

- streaming digests;

- before-and-after metadata;

- mutation detection;

- sealed manifest;

- combined inventory identity.

### Agent 4: Link and path-security specialist

Owns:

- traversal;

- symlinks;

- dangling links;

- hard links;

- special files;

- path collisions;

- root confinement;

- cleanup safety.

### Agent 5: Crash-recovery specialist

Owns:

- state journal;

- interruption points;

- recovery classification;

- idempotency;

- rejection and cleanup;

- operator-review requirements.

### Agent 6: Readiness specialist

Owns:

- storage-model comparison;

- Track 7 finalist storage-only recalculation;

- unresolved memory and suitability preservation;

- Track 8A readiness or withholding.

### Agent 7: Independent verification specialist

Runs after implementation.

Must not own:

- budget arithmetic;

- filesystem identity;

- atomic promotion;

- verification seal;

- path security;

- recovery;

- readiness.

### Coordination Rules

The parent agent must:

- run read-only investigations in parallel;

- synthesize one authoritative storage model before editing;

- assign exclusive file ownership;

- prevent overlapping implementation;

- preserve task order;

- use bounded synthetic fixtures;

- stop on unresolved atomicity or crash-consistency guarantees;

- integrate centrally;

- commission a fresh independent reviewer.

Every specialist must return:

- finding;

- governing evidence;

- architectural implication;

- files owned;

- tests required;

- unresolved conflict;

- recommendation.

## Ordered Execution Plan

Cursor Plan must create one to-do per task and execute all tasks in order.

### Task 1: Verify the Track 7 and Protected-CI Baseline

#### Allowed files or subsystem

Read-only Git state, workflows, Track 5 cache implementation, Track 7 records, schemas, tests, CLI, architecture, provenance, and governance.

#### Required behavior

Confirm all assumed-state items.

Record:

- synchronized main identity;

- protected-check state;

- cache-state authority;

- finalist inventory;

- current budget formula;

- current Track 8 decision;

- exact file ownership for Tasks 2 through 8.

#### Tests

Run safe Git inspection and existing locked validations as necessary.

#### Done condition

The baseline is proven, no stop condition exists, and file ownership is assigned.

### Task 2: Define and Implement the Authoritative Storage-Budget Model

#### Allowed files or subsystem

Budget architecture, storage-policy schema and record, arithmetic module, CLI, documentation, and focused tests.

#### Required behavior

Define:

- logical artifact footprint;

- allocated filesystem blocks;

- verification working overhead;

- runtime-staging allowance;

- transient acquisition overhead;

- copy-promotion peak;

- same-filesystem atomic-promotion peak;

- cross-filesystem ineligibility;

- exact ceiling comparison.

The policy must state which values count toward the 8 GiB ceiling and why.

Do not change the ceiling.

#### Tests

Cover:

- exact 8 GiB pass;

- one-byte-over failure;

- integer overflow protection;

- unknown required values;

- sparse logical-size behavior;

- copy model;

- atomic-rename model;

- cross-filesystem failure.

#### Done condition

One explicit storage model governs later calculations.

### Task 3: Implement Verification Sealing and Mutation Detection

#### Allowed files or subsystem

Seal schemas and templates, verification module, CLI, bounded synthetic fixtures, documentation, and focused tests.

#### Required behavior

Implement:

- normalized expected inventory;

- regular-file validation;

- metadata capture before hashing;

- streaming SHA-256;

- metadata capture after hashing;

- mutation detection;

- expected-size checks;

- expected-digest checks where supplied;

- combined inventory identity;

- canonical sealed-manifest generation;

- temporary-manifest write;

- synchronization behavior;

- no execution authority.

#### Tests

Cover:

- valid inventory;

- missing file;

- unexpected file;

- changed size;

- changed content;

- changed metadata;

- concurrent mutation;

- duplicate normalized path;

- non-UTF-8 path policy where applicable;

- deterministic canonical identity.

#### Done condition

A synthetic quarantine set can be sealed without becoming executable or verified prematurely.

### Task 4: Implement Safe Same-Filesystem Atomic Promotion

#### Allowed files or subsystem

Promotion schemas and templates, filesystem-identity module, atomic-promotion module, CLI, synthetic fixtures, documentation, and focused tests.

#### Required behavior

Implement:

- source and destination root validation;

- same-device validation;

- filesystem capability validation;

- sealed-state requirement;

- no existing destination;

- no copy fallback;

- synchronization preconditions;

- atomic rename;

- destination-parent synchronization;

- promotion receipt;

- immutable verified identity;

- structured failure categories.

Cross-device promotion must fail.

Track 7A must not copy the artifact set to simulate promotion.

#### Tests

Cover:

- successful same-filesystem promotion;

- cross-device rejection through deterministic mocking;

- missing seal;

- invalid seal;

- destination collision;

- synchronization failure;

- rename failure;

- post-rename directory-sync failure;

- changed source after sealing;

- receipt determinism;

- no copy fallback.

#### Done condition

Synthetic artifact sets promote atomically or fail closed.

### Task 5: Implement Link, Path, and Cleanup Safety

#### Allowed files or subsystem

Path validation, cleanup module, synthetic fixtures, documentation, and focused tests.

#### Required behavior

Reject:

- traversal;

- absolute paths;

- symlinks;

- dangling links;

- symlink escape;

- hard links outside the attempt;

- unsupported multi-link files;

- FIFOs;

- sockets;

- device files;

- unsupported special files;

- normalized-path duplicates;

- destination collisions;

- cleanup outside the cache root.

Implement explicit, idempotent synthetic cleanup behavior.

Do not implement background cleanup.

#### Tests

Cover every rejected path and file type, deterministic traversal, partial cleanup failure, repeated cleanup, and reclaim accounting.

#### Done condition

No link or cleanup operation can escape the authorized synthetic cache boundary.

### Task 6: Implement Crash-Recovery Classification

#### Allowed files or subsystem

Recovery schema and template, journal design, recovery module, CLI, synthetic fixtures, documentation, and focused tests.

#### Required behavior

Classify interruption at each material state transition.

The recovery implementation must:

- inspect state journal;

- inspect seal;

- inspect current directory location;

- inspect promotion receipt;

- inspect inventory identity;

- distinguish resumable, rejected, verified, and indeterminate;

- require operator review for unresolved indeterminate state;

- remain idempotent;

- never infer verified state from directory name alone.

#### Tests

Simulate interruption:

- before hashing;

- during hashing;

- before seal;

- after seal;

- before rename;

- after rename;

- before parent sync;

- after parent sync;

- before receipt;

- after receipt;

- with inconsistent journal;

- with modified inventory.

#### Done condition

Synthetic interrupted attempts recover deterministically or remain blocked.

### Task 7: Recalculate Track 7 Storage Eligibility and Decide Track 8A Readiness

#### Allowed files or subsystem

Budget-recalculation schema and record, readiness schema and record, readiness logic, CLI, documentation, and focused tests.

#### Required behavior

Recalculate the finalist under:

- copy promotion;

- same-filesystem atomic promotion;

- cross-filesystem promotion.

Use the committed finalist inventory.

Record separately:

- storage-only eligibility;

- memory eligibility;

- explanation-suitability eligibility;

- candidate-selection eligibility;

- acquisition authorization.

Even if storage-only eligibility passes under atomic promotion:

- FP32 peak memory remains unresolved;

- explanation suitability remains unresolved;

- weightedScore remains null;

- qualifying count remains zero;

- candidate selection remains no-selection;

- Track 8 remains not authorized.

Track 8A may state only whether the storage blocker is:

- resolved;

- unresolved;

- still failed.

#### Tests

Validate all three models, exact arithmetic, fail-closed unknowns, and preservation of non-storage blockers.

#### Done condition

The storage blocker has an evidence-backed decision without changing candidate or acquisition authority.

### Task 8: Documentation, CI, and Independent Verification

#### Allowed files or subsystem

README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, workflows, governance, and complete diff.

#### Required behavior

Document:

- budget semantics;

- state machine;

- verification sealing;

- promotion;

- link safety;

- crash recovery;

- cleanup;

- finalist recalculation;

- remaining blockers;

- no-acquisition boundary.

Update Repository Contracts to validate every Track 7A schema and record.

CI must use bounded synthetic files only.

CI must not:

- allocate multi-gigabyte real files;

- download artifacts;

- install runtimes;

- parse real ONNX graphs;

- perform inference;

- alter GitHub settings.

Assign independent verification to a fresh agent.

#### Tests

Run every command in Verification.

#### Done condition

Track 7A is documented, tested, protected, independently reviewed, and ready for Principal Architect review.

## Out of Scope

Intelligence Track 7A must not:

- change the 8 GiB ceiling;

- change the 12 GiB memory ceiling;

- acquire runtime or model artifacts;

- install a runtime;

- parse a real ONNX model;

- perform conversion or quantization;

- execute inference;

- select a candidate;

- approve Track 8 acquisition;

- resolve unknown memory through assumptions;

- resolve explanation suitability through assumptions;

- reopen candidate discovery;

- modify the corpus;

- change evaluation metrics or gates;

- modify patchpilot;

- modify neural-from-scratch;

- inspect sibling-repository files;

- use tenant or production data;

- implement PatchPilot integration;

- change GitHub settings;

- publish a package;

- create a release;

- deploy.

## Stop Conditions

Stop and report if:

1. The specification-only commit parent differs from origin/main.

2. The working tree contains unrelated changes.

3. Track 7 or Repository Hardening 1 is not merged.

4. Protected checks fail on synchronized main.

5. The Track 7 finalist inventory differs unexpectedly.

6. Implementation requires a real artifact.

7. Implementation requires multi-gigabyte committed or generated fixtures.

8. Atomicity requires unsupported assumptions.

9. Same-filesystem identity cannot be proven.

10. Cross-filesystem behavior would require copy fallback.

11. Required synchronization semantics cannot be represented safely.

12. Mutation detection cannot fail closed.

13. Hard-link escape cannot be rejected.

14. Crash recovery would infer verified state without proof.

15. The 8 GiB ceiling must change to produce a passing result.

16. Candidate selection would require treating storage success as full eligibility.

17. A sibling repository must be inspected.

18. Work cannot fit in one pull-request-sized branch.

On a stop condition:

- do not weaken storage safety;

- do not change the ceiling;

- do not select the candidate;

- do not authorize acquisition;

- do not download artifacts;

- record the exact blocker;

- recommend the smallest next architectural decision.

## Verification

Pass requires:

- uv sync --frozen;

- uv run ruff format --check .;

- uv run ruff check .;

- uv run mypy src tests;

- uv run pytest;

- corpus validation;

- baseline evaluation;

- every merged Track validator;

- fixture validation and evaluation;

- comparison validation;

- calibration validation;

- workflow-policy validation;

- dependency-architecture-policy validation;

- every Track 7A schema validation;

- every Track 7A record validation;

- storage-state transition tests;

- logical-size tests;

- sparse-file tests;

- exact 8 GiB boundary tests;

- one-byte-over tests;

- same-filesystem tests;

- cross-filesystem rejection tests;

- verification-seal tests;

- mutation-race tests;

- symlink tests;

- hard-link tests;

- special-file tests;

- atomic-rename tests;

- synchronization-failure tests;

- no-copy-fallback tests;

- crash-recovery tests;

- cleanup tests;

- idempotency tests;

- finalist budget-recalculation tests;

- non-storage-blocker preservation tests;

- Track 8A readiness tests;

- evidence-source validation;

- documentation and relative-link checks;

- license and provenance checks;

- workflow validation;

- prohibited-artifact scan;

- runtime-binary scan;

- model-artifact scan;

- git diff --check;

- git status --short --branch.

Also confirm:

- no runtime binary, wheel, image, or shared library was downloaded;

- no runtime was installed;

- no model, tokenizer, configuration, or ONNX artifact was acquired;

- no conversion or quantization occurred;

- no inference occurred;

- no multi-gigabyte real fixture was created;

- no candidate was selected;

- no Track 8 acquisition was authorized;

- no sibling repository was accessed;

- no provider was contacted for inference;

- no GitHub repository setting changed;

- no package was published;

- no release or deployment occurred;

- calibration remains not-approved;

- weightedScore remains null;

- qualifyingCandidateCount remains zero;

- selectionOutcome remains no-selection;

- Track 8 remains not-authorized;

- runtimeInstallationStatus remains not-installed;

- acquisitionStatus remains not-acquired;

- conversionStatus remains not-performed;

- executionStatus remains not-executed;

- realModelExecuted remains false;

- productionReady remains false.

## Handoff Requirements

Return one consolidated handoff containing:

1. Outcome

2. Base commit, branch, and working-tree state

3. Multi-agent execution summary

4. Track 7 and protected-CI baseline

5. Authoritative storage-budget semantics

6. Storage-state machine

7. Verification-seal behavior

8. Mutation-detection behavior

9. Filesystem identity and capability requirements

10. Atomic-promotion behavior

11. Link and path safety

12. Crash-recovery behavior

13. Cleanup behavior

14. Copy-promotion calculation

15. Atomic-promotion calculation

16. Cross-filesystem decision

17. Track 7 finalist storage recalculation

18. Storage-only eligibility outcome

19. Preserved memory blocker

20. Preserved explanation-suitability blocker

21. Preserved selection and authorization outcomes

22. Files changed

23. Dependency and lockfile impact

24. Every verification command and actual result

25. CI changes

26. Protected-check impact

27. Independent verification

28. Scope compliance

29. Unresolved decisions

30. Residual risks

31. Exact next-Session recommendation

32. Proposed Conventional Commit

33. Proposed PR title and summary

34. Required post-merge steps

Final verdict must be exactly one of:

- TRACK 7A STORAGE MODEL READY

- TRACK 7A STORAGE MODEL READY WITH DOCUMENTED RESIDUALS

- TRACK 7A STORAGE MODEL NOT READY

- BLOCKED BY UNRESOLVED AUTHORITY

Explicitly confirm:

- no runtime or model artifact was downloaded;

- no runtime was installed;

- no conversion or quantization occurred;

- no inference occurred;

- no multi-gigabyte real fixture was created;

- the 8 GiB ceiling was not changed;

- FP32 peak memory remains unresolved;

- explanation suitability remains unresolved;

- weightedScore remains null;

- qualifyingCandidateCount remains zero;

- selectionOutcome remains no-selection;

- Track 8 remains not-authorized;

- no sibling repository was accessed;

- no automatic commit or push occurred;

- no pull request was created automatically;

- no GitHub repository setting changed;

- no package was published;

- no release or deployment occurred;

- runtimeInstallationStatus remains not-installed;

- acquisitionStatus remains not-acquired;

- conversionStatus remains not-performed;

- executionStatus remains not-executed;

- realModelExecuted remains false;

- productionReady remains false.

End with exactly one:

INTELLIGENCE TRACK 7A READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT

or:

INTELLIGENCE TRACK 7A BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW