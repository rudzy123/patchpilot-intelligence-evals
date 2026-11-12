Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 7B: Memory-Budget Evidence and Explanation-Suitability Closure

## Identity

- **Repository:** patchpilot-intelligence-evals

- **Session ID:** Intelligence Track 7B

- **Mission:** Determine whether authoritative publisher, ONNX Runtime, architecture, and model-card evidence can close the remaining FP32 peak-memory and Finding Explanation Assistant suitability blockers for the Track 7 finalist; otherwise define whether one narrowly controlled future acquisition-and-measurement Session is justified without authorizing acquisition in this Session.

- **Base commit:** The parent of the specification-only commit introducing this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.

- **Expected repository state:** Intelligence Track 7A merged; protected Validation, CodeQL, Dependency Review, and Repository Contracts active; same-filesystem atomic promotion approved with documented residuals; the storage-only blocker resolved; candidate selection still no-selection; Track 8 acquisition still not-authorized; FP32 peak memory unknown; explanation suitability unresolved; no runtime or model artifacts acquired.

- **Branch:** docs/intelligence-track-7b-evidence-closure

- **Change type:** Primary-source evidence closure, deterministic resource modeling, suitability-contract analysis, closed schemas, structured records, validation code, bounded synthetic tests, documentation, and CI enforcement. No runtime installation, model acquisition, tokenizer acquisition, model execution, inference, conversion, quantization, or PatchPilot integration.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** docs(evals): close candidate memory and suitability evidence

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, merge, modify Git history, change GitHub repository settings, acquire artifacts, install a runtime, convert or quantize a model, execute inference, publish a package, create a release, or deploy.

## Architectural Outcome

Intelligence Track 7B must answer:

> Can the remaining FP32 peak-memory and Finding Explanation Assistant suitability blockers for LiquidAI/LFM2.5-1.2B-Instruct be closed through authoritative evidence alone, or is one narrowly controlled future acquisition-and-measurement Session necessary and justified?

The completed Session must:

1. Preserve the Track 7 finalist identity.

2. Preserve the Track 7A storage decision.

3. Define the authoritative memory-budget model.

4. Separate static model storage from runtime process memory.

5. Separate model parameters from graph, allocator, activation, attention, tokenizer, and process overhead.

6. Calculate explicit 4,096-token and 8,192-token memory envelopes.

7. Distinguish publisher-provided figures from calculated estimates.

8. Distinguish proven bounds from unresolved values.

9. Fail closed when a required input is unknown.

10. Research official ONNX Runtime CPU memory behavior relevant to the finalist.

11. Research official finalist architecture and model-loading information.

12. Define the approved Finding Explanation Assistant capability contract.

13. Map official model evidence to that contract without claiming measured behavior.

14. Separate evidence-supported suitability from behavior requiring empirical evaluation.

15. Determine whether evidence alone closes the memory blocker.

16. Determine whether evidence alone closes the explanation-suitability blocker.

17. Preserve weightedScore: null unless every mandatory criterion truly passes.

18. Preserve selectionOutcome: no-selection unless every mandatory criterion passes.

19. Decide whether a future narrowly controlled measurement Session is justified.

20. Produce a Track 8 measurement authorization or explicit withholding record.

21. Preserve model acquisition and execution as disabled.

22. Preserve productionReady: false.

This is an evidence, modeling, validation, and authorization Session.

It may implement schemas, records, validators, deterministic arithmetic, synthetic test fixtures, documentation, CLI commands, and Repository Contracts checks.

It must not download or execute a real model.

## Governing Authority

Before research or implementation, Cursor must reread:

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

- every candidate, runtime, artifact-cache, acquisition, conversion, execution, readiness, and implementation-review record;

- Track 4 candidate-selection criteria and scoring model;

- Track 4 hardware profile;

- Track 5 real-candidate and artifact-cache boundaries;

- Track 6A hardened execution profile and ONNX Runtime authorization;

- Track 6B corrected ONNX adapter and conversion withholding;

- Track 6C candidate eligibility and direct-ONNX findings;

- Track 7 discovery, finalist, suitability, selection, and Track 8 authorization records;

- Track 7A storage policy, atomic-promotion implementation, budget recalculation, readiness, and implementation-review records;

- current calibration and promotion-gate records;

- existing CLI commands;

- existing tests;

- Intelligence Track 2 through Track 7A specifications;

- Repository Hardening 1 specification and merged evidence.

Do not inspect local files in patchpilot or neural-from-scratch.

Public read-only research is permitted only through:

- official Liquid AI repositories and documentation;

- official LiquidAI/LFM2.5-1.2B-Instruct model card;

- official immutable model and ONNX revisions;

- official model architecture documentation;

- official tokenizer documentation;

- official ONNX Runtime documentation;

- official ONNX Runtime memory and allocator documentation;

- official ONNX specifications;

- official CPU execution-provider documentation;

- official technical reports from the model owner;

- official security advisories;

- original maintainers or publishers.

Secondary sources may identify a possible concern. Secondary sources cannot satisfy a mandatory criterion.

## Candidate Scope

Track 7B is limited to:

LiquidAI/LFM2.5-1.2B-Instruct

Track 7B must not:

- add another candidate;

- reopen the Track 7 discovery universe;

- substitute another Liquid AI checkpoint;

- substitute a quantized checkpoint;

- substitute a community conversion;

- substitute a newer revision silently;

- alter the committed immutable source or ONNX identities.

Any revision discrepancy is a stop condition.

## Invariants

### Deterministic PatchPilot authority

No memory estimate, model card, candidate, result, runtime, or research conclusion may become authoritative over:

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

Any future candidate output remains advisory evaluation data.

### Existing Track 7 and Track 7A authority

The following remain authoritative unless this Session provides sufficient evidence under the committed rules:

- finalist: LiquidAI/LFM2.5-1.2B-Instruct;

- source revision: b9d816ab510f9a28dca37cb182e9da8b0226e13c;

- ONNX revision: 10f72e70abf67ac0fd7ebf15bc5854726891d864;

- parameter count: 1,170,340,608;

- context capability recorded as 32,768 tokens;

- selected FP32 inventory: 4,717,588,977 bytes;

- atomic-promotion peak: 4,730,231,432 bytes;

- storage-only blocker: resolved;

- FP32 peak process memory: unresolved;

- explanation suitability: unresolved;

- weightedScore: null;

- qualifyingCandidateCount: 0;

- selectionOutcome: no-selection;

- Track 8 authorizationOutcome: not-authorized;

- Track 8A readinessOutcome: not-ready;

- runtime installation: not-installed;

- acquisition: not-acquired;

- conversion: not-performed;

- execution: not-executed;

- realModelExecuted: false;

- productionReady: false.

Track 7B must not reopen the storage calculation unless a committed inconsistency is discovered.

### No acquisition, installation, conversion, or inference

Track 7B must not:

- download ONNX Runtime;

- download runtime binaries, wheels, archives, libraries, or images;

- download model weights;

- download tokenizer files;

- download model configurations;

- download ONNX graphs or external-data files;

- install a runtime;

- install memory profilers requiring runtime installation;

- populate the real artifact cache;

- perform conversion;

- perform quantization;

- parse a real ONNX graph;

- load a real tokenizer;

- execute inference;

- contact a hosted inference provider;

- claim measured behavior without execution.

Only official public documentation and bounded synthetic arithmetic tests are permitted.

### Memory model categories

The memory model must distinguish:

1. **Static parameter bytes**

   - exact parameter count;

   - precision;

   - bytes per parameter;

   - weight sharing where officially documented.

2. **ONNX graph and constant memory**

   - mapped versus resident behavior;

   - external-data behavior;

   - graph metadata;

   - initializer loading behavior;

   - evidence source.

3. **Runtime process baseline**

   - interpreter or runtime process;

   - loaded shared libraries;

   - ONNX Runtime session;

   - CPU execution provider.

4. **Allocator overhead**

   - arena allocator;

   - memory patterns;

   - graph optimization;

   - temporary buffers;

   - thread pools.

5. **Activation memory**

   - batch size;

   - sequence length;

   - hidden dimensions;

   - layer behavior;

   - precision;

   - architecture-specific information.

6. **Attention-state or recurrent-state memory**

   - key-value cache where applicable;

   - recurrent or convolutional state where applicable;

   - architecture-specific state;

   - context growth.

7. **Input and output tensors**

   - token IDs;

   - masks;

   - logits;

   - generated-token handling.

8. **Tokenizer and configuration memory**

   - tokenizer implementation;

   - vocabulary and auxiliary data;

   - configuration objects.

9. **Hardened execution overhead**

   - staged runtime closure;

   - launcher;

   - IPC and protocol buffers;

   - result capture;

   - attestation.

10. **Safety margin**

	- explicit percentage or byte allowance;

	- evidence-based rationale;

	- no hidden buffer.

Each category must be classified as:

- authoritative measured value;

- authoritative published bound;

- deterministic calculation;

- conservative assumption;

- unresolved.

A required unresolved category prevents a proven memory pass.

### Memory limits

The approved process-memory ceiling remains:

12 GiB = 12,884,901,888 bytes

The Session must calculate at least:

- 4,096-token envelope;

- 8,192-token envelope.

The Session must use:

- batch size 1;

- one candidate process;

- CPU-only execution;

- FP32 artifacts;

- no quantization;

- no speculative execution;

- no automatic batching;

- no concurrent candidate processes.

Exactly 12 GiB may pass.

One byte over 12 GiB fails.

An unresolved required component produces unresolved, not a pass.

### Memory arithmetic must be reproducible

Every calculated value must identify:

- formula;

- input fields;

- units;

- byte-versus-GiB conversion;

- evidence source;

- rounding rule;

- overflow handling;

- uncertainty status.

Do not mix:

- decimal GB;

- binary GiB;

- compressed artifact size;

- logical file size;

- resident memory;

- virtual address space;

- allocated arena capacity.

RLIMIT_AS evidence must not be treated as resident-memory evidence.

### Publisher evidence versus runtime measurement

Official publisher and ONNX Runtime evidence may close a memory criterion only when the evidence applies to:

- the exact candidate;

- the exact FP32 ONNX artifact;

- the exact architecture;

- CPU execution;

- the relevant context sizes;

- the relevant runtime mode.

A generic statement that a model “runs on edge devices” is insufficient.

A generic parameter-count calculation alone is insufficient to establish complete peak process memory.

### Explanation-suitability contract

Track 7B must define the evidence requirements for the approved first capability.

The candidate would need to:

- accept authorized synthetic Finding evidence only;

- distinguish deterministic PatchPilot facts from generated explanation;

- reproduce evidence IDs without inventing them;

- identify missing evidence;

- express uncertainty;

- refuse unsupported requests;

- resist instructions embedded in evidence;

- avoid state-mutation claims;

- avoid cross-tenant disclosure;

- produce schema-compatible bounded output;

- operate in English;

- fit the approved context and output limits.

Track 7B may determine that official evidence supports a capability in principle.

Track 7B must not claim that official evidence proves observed grounding, refusal, citation accuracy, prompt-injection resistance, tenant isolation, or hallucination rates.

Those behaviors normally require empirical evaluation.

### Suitability evidence categories

For each capability, record:

- official evidence;

- applicability;

- result:

  - supported-in-principle;

  - unsupported;

  - unresolved;

  - requires-empirical-evaluation;

- mandatory-screen effect;

- required future measurement.

The candidate may be considered **eligible for controlled evaluation** when:

- official evidence supports the general instruction and output capabilities;

- no official limitation disqualifies the use;

- all safety-critical behaviors are explicitly deferred to the mandatory synthetic evaluation harness;

- the record does not represent deferred behaviors as proven.

The candidate may not be considered production suitable.

### Suitability cannot be inferred from benchmarks

Do not use leaderboard rank or general benchmark performance to establish:

- citation fidelity;

- grounding;

- refusal;

- uncertainty calibration;

- prompt-injection resistance;

- tenant isolation;

- security explanation accuracy.

Benchmarks may provide background only when published officially. They cannot close mandatory behavioral evidence.

### Controlled measurement authorization

If authoritative evidence cannot close memory or suitability, Track 7B may recommend a future controlled measurement Session only when:

- the remaining unknown cannot reasonably be resolved from official evidence;

- the question is material to candidate eligibility;

- storage safety is already approved;

- hardened execution is approved;

- runtime and adapter identities are authorized;

- the exact artifact identity is fixed;

- acquisition can remain operator-controlled;

- tests can use the existing synthetic corpus;

- no production integration is implied;

- the future measurement scope is narrower than full evaluation;

- explicit stop conditions are defined.

Track 7B must not perform the measurement.

### Candidate selection remains fail-closed

A storage pass does not make the candidate selected.

The candidate remains unselected when:

- memory remains unresolved;

- explanation-suitability screening fails;

- any mandatory legal, tokenizer, provenance, artifact, execution, or evidence criterion fails;

- controlled measurement has not occurred where required.

Disqualified or unresolved candidates retain weightedScore: null.

### No gate changes

Do not change:

- corpus content;

- corpus taxonomy;

- corpus digest;

- metric definitions;

- invariant gates;

- percentage thresholds;

- calibration status;

- promotion status.

Calibration remains not-approved.

productionReady remains false.

## Assumed Repository State

Before implementation, Cursor must prove:

- repository root is patchpilot-intelligence-evals;

- local main equals origin/main;

- Intelligence Track 7A is merged;

- Repository Hardening 1 is merged;

- specification-only commit parent equals origin/main;

- working tree is clean after the specification commit;

- protected Validation, CodeQL, Dependency Review, and Repository Contracts are active;

- protected CI passes on synchronized main;

- repository license remains Apache-2.0;

- Python remains &gt;=3.12,&lt;3.13;

- uv.lock exists and validates;

- the 24-case corpus and approved digest are unchanged;

- candidate protocol remains version 1.0.0;

- hardened execution remains approved;

- future runtime identity remains onnxruntime v1.31.1;

- runtime remains uninstalled;

- corrected adapter requires verified ONNX executable artifacts;

- finalist identity and revisions match the committed Track 7 records;

- selected FP32 inventory remains 4,717,588,977 bytes;

- atomic storage peak remains 4,730,231,432 bytes;

- storage-only blocker is resolved;

- FP32 peak process memory remains unresolved;

- explanation suitability remains unresolved;

- weightedScore remains null;

- qualifying candidate count remains zero;

- candidate selection remains no-selection;

- Track 8 remains not authorized;

- Track 8A remains not ready;

- calibration remains not approved;

- no runtime or model artifacts exist;

- no inference-runtime dependency exists;

- no provider SDK exists;

- no sibling repository is nested in the Git tree;

- realModelExecuted remains false;

- productionReady remains false.

If any material assumption is false, stop and report the conflict.

## Allowed Change Surface

Permitted:

- docs/specs/[intelligence-track-7b.md](http://intelligence-track-7b.md);

- memory-budget architecture;

- memory-evidence documentation;

- explanation-suitability architecture;

- capability-to-evidence mapping;

- measurement-authorization documentation;

- closed schemas required by Track 7B;

- structured memory, suitability, and readiness records;

- source modules implementing deterministic memory arithmetic, evidence completeness, suitability classification, and measurement-authorization logic;

- CLI validators;

- bounded synthetic arithmetic tests;

- Repository Contracts updates;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, and governance documentation;

- pyproject.toml and uv.lock only if an essential non-runtime validation dependency is proven necessary, licensed, and approved.

Not permitted:

- runtime or model download;

- runtime installation;

- real tokenizer or configuration acquisition;

- ONNX parsing;

- model execution;

- conversion;

- quantization;

- changing the storage decision;

- changing the 12 GiB ceiling;

- selecting the candidate on incomplete evidence;

- changing corpus or gates;

- inspecting sibling repositories;

- PatchPilot integration;

- GitHub repository-setting changes;

- package publication;

- release;

- deployment.

## Required Repository Additions

The repository must include the conceptual equivalent of:

text</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">docs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── architecture/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [candidate-memory-budget.md](http://candidate-memory-budget.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [explanation-suitability-contract.md](http://explanation-suitability-contract.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [empirical-measurement-boundary.md](http://empirical-measurement-boundary.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [track8b-measurement-readiness.md](http://track8b-measurement-readiness.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── provenance/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [finalist-memory-evidence.md](http://finalist-memory-evidence.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [finalist-suitability-evidence.md](http://finalist-suitability-evidence.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">└── specs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── [intelligence-track-7b.md](http://intelligence-track-7b.md)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">schemas/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── candidate-memory-model.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── candidate-memory-evidence.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── candidate-memory-budget.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── explanation-suitability-contract.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── explanation-suitability-evidence.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── controlled-measurement-authorization.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">└── track8b-readiness.schema.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">candidates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">└── authorization/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── candidate-memory-model.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── candidate-memory-evidence.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── candidate-memory-budget.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── explanation-suitability-contract.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── explanation-suitability-evidence.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── controlled-measurement-authorization.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── track8b-readiness.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">src/patchpilot_intelligence_evals/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── memory_[model.py](http://model.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── memory_[evidence.py](http://evidence.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── memory_[budget.py](http://budget.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── suitability_[contract.py](http://contract.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── suitability_[evidence.py](http://evidence.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── measurement_[authorization.py](http://authorization.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">└── track8b_[readiness.py](http://readiness.py)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">tests/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── test_memory_[model.py](http://model.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── test_memory_[evidence.py](http://evidence.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── test_memory_[budget.py](http://budget.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── test_suitability_[contract.py](http://contract.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── test_suitability_[evidence.py](http://evidence.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">├── test_measurement_[authorization.py](http://authorization.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">└── test_track8b_[readiness.py](http://readiness.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">

Exact filenames may differ only to follow established repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and validated records for:

1. candidate memory model;

2. candidate memory evidence;

3. candidate memory budget;

4. explanation-suitability contract;

5. explanation-suitability evidence;

6. controlled-measurement authorization;

7. Track 8B readiness.

Every schema must:

- have a stable schema ID;

- declare an explicit version;

- use additionalProperties: false;

- identify the exact candidate and immutable revisions;

- distinguish publisher evidence from runtime evidence;

- distinguish measured, published, calculated, assumed, and unresolved values;

- require explicit units;

- distinguish virtual memory, resident memory, logical artifact size, and allocator capacity;

- prohibit secrets and tenant identifiers;

- prohibit hostnames and IP addresses;

- prohibit identity-bearing local paths;

- prohibit claims that artifacts were acquired;

- prohibit claims that inference occurred;

- preserve empty locally observed artifact digests;

- preserve runtimeInstallationStatus: not-installed;

- preserve acquisitionStatus: not-acquired;

- preserve conversionStatus: not-performed;

- preserve executionStatus: not-executed;

- preserve realModelExecuted: false;

- preserve productionReady: false;

- support not-authorized and not-ready outcomes.

The readiness record must preserve:

- selectionOutcome: no-selection unless every mandatory criterion passes;

- weightedScore: null unless every mandatory criterion passes;

- qualifyingCandidateCount: 0 unless every mandatory criterion passes;

- Track 8 acquisition as not authorized;

- Track 8A storage readiness as not ready or historical storage-only resolution, following existing schema authority.

## Source-Evidence Contract

Every material external claim must record:

- evidence ID;

- descriptive source name;

- exact URL;

- publisher;

- retrieval date in ISO 8601 format;

- immutable revision or documentation version where applicable;

- supported claim;

- applicability to the exact finalist and runtime mode;

- evidence classification:

  - authoritative;

  - secondary;

  - conflicting;

  - unresolved;

- value type:

  - published-measurement;

  - published-bound;

  - calculated;

  - assumption;

  - not-provided;

- units;

- quote-free factual summary;

- conflict disposition.

Do not copy complete model cards, reports, or terms into the repository.

When evidence conflicts, use the more restrictive interpretation.

## Memory-Budget Formula Contract

The total planned peak memory must be represented as:

text</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">peak_process_memory =</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; static_parameter_memory</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp; + graph_and_initializer_overhead</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp; + runtime_process_baseline</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp; + allocator_and_optimization_overhead</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp; + activation_memory</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp; + architecture_state_memory</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp; + input_output_tensor_memory</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp; + tokenizer_and_configuration_memory</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp; + hardened_execution_overhead</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">&nbsp; + safety_margin</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794486900000,&quot;dataSource&quot;:0}">

The record must not double count a category.

For each category, include:

- category ID;

- byte value or null;

- lower bound where available;

- upper bound where available;

- evidence status;

- formula;

- inputs;

- source evidence;

- uncertainty;

- included-in-total flag.

A total may be classified as:

- proven-pass;

- proven-fail;

- unresolved.

A total cannot be proven-pass when a required upper bound is unknown.

## Explanation-Suitability Decision Contract

Each capability must be classified independently.

Required capability IDs:

- instruction-following;

- structured-output;

- english-language;

- context-capacity;

- bounded-generation;

- deterministic-fact-separation;

- evidence-id-reproduction;

- missing-evidence-reporting;

- uncertainty-expression;

- unsupported-request-refusal;

- embedded-instruction-resistance;

- state-mutation-avoidance;

- cross-tenant-nondisclosure;

- schema-compatibility.

Each record must include:

- official evidence;

- evidence-supported status;

- empirical evaluation required;

- disqualifying official limitation;

- Track 2 or Track 3 metric mapping;

- future test category;

- decision rationale.

Official documentation may establish general capability support.

Only empirical evaluation may establish actual metric performance.

## Multi-Agent Execution Model

Cursor Plan is the parent memory-and-suitability orchestrator.

Use Grok 4.7 Extra High for:

- evidence authority;

- memory-model synthesis;

- architecture-specific memory decisions;

- suitability-boundary decisions;

- measurement authorization;

- readiness decisions;

- conflicts;

- independent final verification.

Delegate parallel read-only research and controlled implementation to these specialists.

### Agent 1: Finalist architecture specialist

Owns:

- model architecture evidence;

- parameter representation;

- architecture state;

- context behavior;

- official immutable applicability.

### Agent 2: ONNX Runtime memory specialist

Owns:

- CPU execution-provider memory behavior;

- graph and initializer loading;

- allocator behavior;

- arena settings;

- graph optimization;

- memory patterns;

- runtime baseline evidence.

### Agent 3: Memory arithmetic specialist

Owns:

- formulas;

- units;

- 4,096-token envelope;

- 8,192-token envelope;

- safety margin;

- exact 12 GiB comparison;

- unresolved-value behavior.

### Agent 4: Model-card suitability specialist

Owns:

- intended use;

- limitations;

- language support;

- instruction support;

- structured generation;

- safety and deployment caveats.

### Agent 5: Evaluation-contract specialist

Owns:

- citation behavior;

- refusal;

- uncertainty;

- prompt-injection resistance;

- tenant isolation;

- schema compatibility;

- mapping to existing corpus and metrics;

- empirical-test requirements.

### Agent 6: Measurement-authorization specialist

Owns:

- unresolved-question inventory;

- necessity and proportionality;

- future acquisition boundary;

- stop conditions;

- Track 8B readiness or withholding.

### Agent 7: Independent verification specialist

Runs after implementation.

Must not own:

- architecture evidence;

- runtime memory evidence;

- memory arithmetic;

- suitability evidence;

- evaluation mapping;

- measurement authorization;

- readiness.

### Coordination Rules

The parent agent must:

- run independent research in parallel;

- require exact source applicability;

- reconcile one memory model before edits;

- assign exclusive file ownership;

- prevent overlapping edits;

- preserve task dependency order;

- stop on unsupported authority claims;

- separate evidence from calculation;

- integrate centrally;

- commission a fresh independent reviewer.

Every specialist must return:

- finding;

- exact authoritative evidence;

- applicability;

- calculation or architectural implication;

- unresolved uncertainty;

- recommendation;

- files owned;

- tests required.

## Ordered Execution Plan

Cursor Plan must create one to-do for every task and execute the tasks in order.

### Task 1: Verify Track 7A and Protected-CI Baseline

#### Allowed files or subsystem

Read-only Git state, workflows, Track 7 and Track 7A records, schemas, implementation, tests, architecture, provenance, and authorization.

#### Required behavior

Confirm every assumed-state item.

Record:

- synchronized main identity;

- finalist and revision identities;

- runtime identity;

- hardened-profile identity;

- storage decision;

- remaining blocker identities;

- exact file ownership for Tasks 2 through 8.

#### Tests

Run safe Git inspection and existing locked validation commands as necessary.

#### Done condition

The baseline is proven, no stop condition exists, and file ownership is assigned.

### Task 2: Define the Authoritative Memory Model

#### Allowed files or subsystem

Memory architecture, memory-model schema and record, arithmetic module, CLI, documentation, and focused tests.

#### Required behavior

Define all required memory categories.

For each category:

- define meaning;

- prevent double counting;

- define units;

- define required evidence;

- define formula;

- define unresolved behavior;

- define inclusion in the 4,096-token and 8,192-token envelopes.

Clearly distinguish:

- logical storage;

- mapped file pages;

- resident memory;

- virtual address space;

- allocator reservation;

- allocator use;

- peak process memory.

#### Tests

Cover:

- complete model;

- missing category;

- duplicate category;

- double counting;

- unit mismatch;

- binary versus decimal units;

- integer overflow;

- unknown upper bound;

- exact 12 GiB boundary;

- one-byte-over boundary.

#### Done condition

One closed memory model governs Track 7B.

### Task 3: Collect and Validate Authoritative Memory Evidence

#### Allowed files or subsystem

Official read-only research, memory-evidence schema and record, validator, documentation, and focused tests.

#### Required behavior

Collect only official evidence relevant to:

- exact finalist architecture;

- exact FP32 representation;

- exact ONNX revision where applicable;

- CPU-only ONNX Runtime execution;

- 4,096-token context;

- 8,192-token context;

- batch size 1;

- allocator and graph-optimization behavior;

- architecture-specific state.

Record missing values explicitly.

Do not treat generic edge-device claims as memory evidence.

#### Tests

Validate source authority, revision applicability, units, evidence types, conflicts, and unresolved classifications.

#### Done condition

Every memory category has authoritative evidence, a reproducible calculation, or an explicit unresolved state.

### Task 4: Calculate 4,096-Token and 8,192-Token Memory Envelopes

#### Allowed files or subsystem

Memory-budget schema and record, arithmetic module, CLI, documentation, and focused tests.

#### Required behavior

Calculate both envelopes using the authoritative model.

Record:

- lower bound;

- upper bound;

- unresolved components;

- safety margin;

- total classification;

- comparison with 12,884,901,888 bytes;

- assumptions;

- measurement-required fields.

A missing required upper bound must produce unresolved.

Do not manufacture a total by substituting zero for unknown categories.

#### Tests

Cover:

- proven pass;

- proven fail;

- unresolved;

- exact ceiling;

- one byte over;

- missing upper bound;

- multiple context sizes;

- deterministic serialization.

#### Done condition

Both context sizes have reproducible and fail-closed memory decisions.

### Task 5: Define the Explanation-Suitability Contract

#### Allowed files or subsystem

Suitability architecture, contract schema and record, validator, CLI, documentation, and focused tests.

#### Required behavior

Define the fourteen required capability IDs.

Map each capability to:

- existing Track 2 or Track 3 metric;

- relevant synthetic corpus category;

- official-evidence requirement;

- mandatory empirical test;

- pass authority;

- disqualifying official limitation.

Do not change existing metrics or thresholds.

#### Tests

Validate capability completeness, uniqueness, metric mapping, corpus mapping, and prohibition on unsupported quality claims.

#### Done condition

The exact evaluation-suitability contract is explicit and versioned.

### Task 6: Assess Official Suitability Evidence

#### Allowed files or subsystem

Official read-only research, suitability-evidence schema and record, validator, documentation, and focused tests.

#### Required behavior

For each capability, record:

- official evidence;

- applicability;

- supported-in-principle status;

- disqualifying limitation;

- empirical evaluation requirement;

- unresolved questions.

Do not claim actual grounding, refusal, citation, uncertainty, injection resistance, tenant isolation, or schema-validity performance.

#### Tests

Validate evidence authority, capability coverage, unsupported-claim rejection, and empirical-measurement flags.

#### Done condition

The finalist has an evidence-bounded suitability decision.

### Task 7: Authorize or Withhold a Controlled Measurement Session

#### Allowed files or subsystem

Measurement-authorization schema and record, Track 8B readiness schema and record, logic module, CLI, documentation, and focused tests.

#### Required behavior

Determine whether evidence:

- closes memory;

- closes suitability screening;

- leaves questions requiring empirical measurement;

- reveals a disqualifying limitation.

A future controlled measurement Session may be recommended only when:

- no known mandatory disqualifier exists;

- unresolved questions require real measurement;

- the questions are material;

- storage safety passes;

- hardened execution passes;

- runtime and adapter identities are authorized;

- exact candidate artifacts remain fixed;

- acquisition can be narrow and operator-controlled;

- measurement scope is explicit;

- stop conditions are explicit;

- no production use is implied.

Track 7B must not authorize broad evaluation or production deployment.

Even when controlled measurement is recommended, preserve:

- acquisition not performed;

- runtime not installed;

- execution not performed;

- local digests empty;

- real model not executed;

- production readiness false.

If prerequisites fail:

- set measurement authorization to not-authorized;

- list blockers;

- preserve no-selection.

#### Tests

Validate:

- evidence-closed path;

- measurement-justified path;

- disqualified path;

- unresolved-without-justification path;

- preservation of disabled states.

#### Done condition

Track 8B has a durable measurement-readiness or withholding decision.

### Task 8: Documentation, CI, and Independent Verification

#### Allowed files or subsystem

README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, workflows, governance, and complete diff.

#### Required behavior

Document:

- memory categories;

- formulas;

- evidence;

- context envelopes;

- unresolved memory;

- suitability contract;

- official suitability evidence;

- empirical-measurement requirements;

- Track 8B decision;

- residual risks;

- no-acquisition boundary.

Update Repository Contracts for every Track 7B schema and record.

CI must not:

- download candidate artifacts;

- install ONNX Runtime;

- use model hubs for artifacts;

- execute inference;

- allocate multi-gigabyte physical fixtures;

- change GitHub settings.

Assign independent verification to a fresh agent.

#### Tests

Run every command in Verification.

#### Done condition

Track 7B is documented, validated, CI-enforced, independently reviewed, and ready for Principal Architect review.

## Out of Scope

Intelligence Track 7B must not:

- download or install ONNX Runtime;

- acquire model, tokenizer, configuration, ONNX, or external-data artifacts;

- parse a real ONNX graph;

- execute inference;

- perform conversion;

- authorize quantization;

- alter the Track 7A storage decision;

- change the 12 GiB memory ceiling;

- infer memory from artifact size alone;

- infer quality from benchmarks;

- select the candidate on unresolved evidence;

- modify corpus contents;

- change metrics or gates;

- modify patchpilot;

- modify neural-from-scratch;

- inspect sibling-repository files;

- use tenant or production data;

- implement PatchPilot APIs or UI;

- create production composition;

- change GitHub settings;

- publish a package;

- create a release;

- deploy.

## Stop Conditions

Stop and report if:

1. The specification-only commit parent differs from origin/main.

2. The working tree contains unrelated changes.

3. Track 7A or Repository Hardening 1 is not merged.

4. Protected checks fail on synchronized main.

5. Finalist identity or revision differs from committed authority.

6. Storage decision differs unexpectedly.

7. Memory evidence requires downloading artifacts.

8. Suitability evidence requires executing the model in this Session.

9. A required memory category cannot be represented safely.

10. A calculation would substitute zero for an unknown category.

11. Virtual memory would be represented as resident memory.

12. Generic parameter size would be represented as complete peak memory.

13. Benchmark performance would be represented as grounding or refusal evidence.

14. Candidate selection requires unresolved mandatory evidence.

15. The 12 GiB ceiling must change to produce a pass.

16. Existing evaluation metrics or gates must change.

17. A sibling repository must be inspected.

18. Work cannot fit in one pull-request-sized branch.

On a stop condition:

- do not invent evidence;

- do not weaken the memory model;

- do not select the candidate;

- do not authorize acquisition;

- do not execute the model;

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

- every Track 7B schema validation;

- every Track 7B record validation;

- memory-category completeness tests;

- double-counting tests;

- unit-conversion tests;

- integer-overflow tests;

- evidence-authority tests;

- exact-revision applicability tests;

- 4,096-token memory tests;

- 8,192-token memory tests;

- exact 12 GiB boundary tests;

- one-byte-over memory tests;

- unresolved-upper-bound tests;

- suitability-capability completeness tests;

- metric and corpus mapping tests;

- unsupported-quality-claim tests;

- empirical-measurement flag tests;

- controlled-measurement authorization tests;

- Track 8B readiness tests;

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

- no model, tokenizer, configuration, ONNX graph, or external data was acquired;

- no conversion or quantization occurred;

- no inference occurred;

- no real-model memory measurement occurred;

- no candidate was selected on unresolved evidence;

- the storage decision remains unchanged;

- no sibling repository was accessed;

- no provider was contacted for inference;

- no GitHub repository setting changed;

- no package was published;

- no release or deployment occurred;

- calibration remains not-approved;

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

4. Track 7A and protected-CI baseline

5. Finalist and immutable identities

6. Authoritative memory model

7. Memory evidence reviewed

8. Memory categories and formulas

9. 4,096-token envelope

10. 8,192-token envelope

11. 12 GiB comparison

12. Unresolved memory values

13. Explanation-suitability contract

14. Official suitability evidence

15. Supported-in-principle capabilities

16. Empirical-measurement requirements

17. Disqualifying limitations, if any

18. Memory-blocker outcome

19. Suitability-blocker outcome

20. Controlled-measurement authorization or withholding

21. Track 8B readiness or withholding

22. Preserved candidate-selection state

23. Files changed

24. Dependency and lockfile impact

25. Every verification command and actual result

26. CI changes

27. Protected-check impact

28. Independent verification

29. Scope compliance

30. Unresolved decisions

31. Residual risks

32. Exact next-Session recommendation

33. Proposed Conventional Commit

34. Proposed PR title and summary

35. Required post-merge steps

Final verdict must be exactly one of:

- TRACK 8B CONTROLLED MEASUREMENT AUTHORIZED

- TRACK 8B CONTROLLED MEASUREMENT AUTHORIZED WITH DOCUMENTED RESIDUALS

- TRACK 8B CONTROLLED MEASUREMENT NOT AUTHORIZED

- BLOCKED BY UNRESOLVED AUTHORITY

Explicitly confirm:

- no runtime or model artifact was downloaded;

- no runtime was installed;

- no conversion or quantization occurred;

- no inference occurred;

- no real-model memory measurement occurred;

- the Track 7A storage decision remains unchanged;

- the 12 GiB ceiling remains unchanged;

- no candidate was selected on unresolved evidence;

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

INTELLIGENCE TRACK 7B READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT

or:

INTELLIGENCE TRACK 7B BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW