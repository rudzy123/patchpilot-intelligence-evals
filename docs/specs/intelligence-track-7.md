Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 7: Candidate Landscape Refresh and Eligibility Pre-Screen

## Identity

- **Repository:** patchpilot-intelligence-evals

- **Session ID:** Intelligence Track 7

- **Mission:** Identify and assess a tightly bounded new landscape of small, CPU-capable, offline candidates that are better aligned with PatchPilot’s hardened execution, ONNX Runtime, licensing, provenance, tokenizer, artifact-budget, and evidence-grounded explanation requirements; authorize at most one candidate for a future controlled acquisition Session; or preserve no-selection when no candidate satisfies every mandatory requirement.

- **Base commit:** The parent of the specification-only commit introducing this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.

- **Expected repository state:** Intelligence Track 6C and Repository Hardening 1 merged; protected Validation, CodeQL, and Dependency Review active; the five prior candidate families disqualified; no candidate selected; ONNX Runtime authorized only as an uninstalled future runtime identity; no model, tokenizer, configuration, runtime, or conversion artifact acquired; calibration not approved; productionReady false.

- **Branch:** docs/intelligence-track-7-candidate-refresh

- **Change type:** Primary-source research, eligibility pre-screening, structured evidence, closed schemas, validation code, deterministic tests, documentation, and CI enforcement. No artifact acquisition, runtime installation, conversion, inference, or PatchPilot integration.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** docs(evals): refresh offline candidate landscape

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, merge, modify Git history, change GitHub repository settings, acquire artifacts, install a runtime, perform conversion, execute inference, publish a package, create a release, or deploy.

## Architectural Outcome

Intelligence Track 7 must answer:

> Does a new small-model landscape contain one candidate that satisfies every mandatory legal, provenance, tokenizer, security, hardware, direct-ONNX, runtime, and evaluation criterion for a future controlled acquisition?

The completed Session must:

1. Preserve all deterministic PatchPilot authority.

2. Preserve the five previously disqualified candidate-family decisions.

3. Define a bounded discovery universe for new candidate families.

4. Identify no more than eight candidate families during discovery.

5. Reduce the discovery universe to no more than four fully researched finalists.

6. Exclude candidates requiring conversion or unapproved quantization.

7. Require official publisher-provided ONNX artifacts.

8. Require explicit model-weight, tokenizer, commercial-use, and redistribution evidence.

9. Require immutable official revisions.

10. Require complete ONNX graph and external-data inventories.

11. Require compatibility with the approved artifact and memory budgets.

12. Require compatibility with ONNX Runtime and the hardened execution boundary.

13. Require meaningful official limitations and intended-use documentation.

14. Assess suitability for evidence-grounded Finding explanation.

15. Apply exact mandatory criteria before scoring.

16. Score only candidates passing every mandatory criterion.

17. Select at most one candidate.

18. Create a Track 8 controlled-acquisition authorization or a not-authorized record.

19. Preserve all acquisition and execution states as disabled.

20. Preserve productionReady: false.

This Session may implement schemas, structured records, validators, arithmetic checks, documentation, deterministic tests, and CI validation.

This Session may not download or execute candidate artifacts.

## Governing Authority

Before research or editing, Cursor must reread:

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

- repository-hardening governance and required-check records;

- every architecture document;

- every provenance document;

- every existing schema;

- every candidate, runtime, acquisition, conversion, and readiness record;

- Track 4 candidate-selection criteria and scoring model;

- Track 4 hardware profile;

- Track 5 real-candidate boundary;

- Track 5 external artifact-cache policy;

- Track 6A hardened execution profile and runtime authorization;

- Track 6B runtime-staging and corrected ONNX adapter contract;

- Track 6B direct-ONNX and conversion findings;

- Track 6C eligibility, tokenizer, ONNX, artifact-budget, bounded-execution, and readiness records;

- current calibration and promotion-gate records;

- existing CLI commands;

- existing tests;

- Intelligence Track 2 through Track 6C specifications;

- Repository Hardening 1 specification and merged evidence.

Do not inspect local files in patchpilot or neural-from-scratch.

Public read-only research is permitted only through:

- official model-owner repositories;

- official model cards;

- official immutable revisions;

- official weight-license instruments;

- official source-code licenses;

- official tokenizer repositories;

- official tokenizer-license instruments;

- official acceptable-use policies;

- official publisher-provided ONNX repositories;

- official artifact inventories;

- official digest records;

- official ONNX Runtime compatibility documentation;

- official technical reports;

- original publisher documentation;

- official security advisories.

Secondary sources may identify candidates or concerns. Secondary sources cannot satisfy a mandatory criterion.

## Prior Candidate Exclusion

The following candidate families were already assessed and must not be reintroduced as new Track 7 candidates:

1. Qwen/Qwen2.5-1.5B-Instruct

2. Qwen/Qwen2.5-3B-Instruct

3. HuggingFaceTB/SmolLM2-1.7B-Instruct

4. allenai/OLMo-2-0425-1B-Instruct

5. google/gemma-3-1b-it

Track 7 may reference their records for comparison but must not:

- reopen their decisions;

- select a newer revision of the same checkpoint;

- use a quantized or community-converted form;

- treat a renamed mirror as a new candidate;

- silently substitute another size from the same family.

A materially different official model generation from the same publisher may enter the discovery universe only when:

- it has a different official model-family identity;

- it has an independent model card;

- it has independent licensing evidence;

- it has a distinct immutable revision;

- it is not merely a revision of a previously disqualified checkpoint;

- the parent agent records why it is materially different.

## Candidate Discovery Boundary

Discovery may identify no more than eight candidate families.

Full research may cover no more than four finalists.

A discovery candidate must initially appear capable of satisfying:

- approximately 0.5 billion to 3 billion parameters;

- CPU-only execution;

- model-artifact footprint at or below 8 GiB;

- estimated process memory at or below 12 GiB;

- context window of at least 4,096 tokens;

- instruction-following or structured text-generation capability;

- official model card;

- official immutable revision;

- explicit weight terms;

- identifiable tokenizer provenance;

- no mandatory hosted API;

- no mandatory telemetry;

- no remote-code requirement;

- direct official ONNX availability;

- compatibility with offline evaluation;

- plausible suitability for evidence-grounded explanation.

A discovery candidate that clearly fails one of these criteria must not advance to the finalist set.

## Invariants

### Deterministic PatchPilot authority

No candidate, model, tokenizer, runtime, artifact, score, or research conclusion may become authoritative over:

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

### Existing fail-closed states remain authoritative

Unless exactly one Track 7 candidate passes every mandatory criterion and later receives Principal Architect approval:

- selectionOutcome remains no-selection;

- runtimeInstallationStatus remains not-installed;

- acquisitionStatus remains not-acquired;

- conversionStatus remains not-performed;

- executionStatus remains not-executed;

- realModelExecuted remains false;

- productionReady remains false.

### No acquisition, installation, conversion, or inference

Track 7 must not:

- download runtime binaries, wheels, archives, shared libraries, or images;

- install ONNX Runtime;

- download model weights;

- download tokenizers;

- download model configurations;

- download ONNX graphs or external-data files;

- populate the runtime or model cache;

- install conversion tools;

- perform conversion;

- perform quantization;

- parse a real ONNX graph;

- load a real tokenizer;

- execute inference;

- contact a hosted inference provider;

- publish or redistribute artifacts.

Read-only official metadata and documentation research is permitted.

### Direct official ONNX required

A Track 7 candidate may qualify only with a direct official ONNX path.

The ONNX artifact must be:

- published by the model owner or an explicitly authorized official publisher;

- linked to the exact reviewed model family;

- pinned to an immutable revision;

- licensed consistently with the source model;

- accompanied by a complete expected inventory;

- free of unreviewed remote code;

- compatible with the corrected Track 6B adapter;

- compatible with the Track 6A hardened launcher.

Track 7 must not authorize:

- community conversions;

- local conversion;

- unofficial mirrors;

- unverified quantization;

- format reinterpretation;

- automatic retrieval.

### Weight, code, tokenizer, and artifact licenses remain separate

For every finalist, evaluate independently:

- source-code license;

- model-weight license;

- tokenizer license;

- ONNX artifact license;

- acceptable-use terms;

- commercial-use rights;

- modification rights;

- redistribution rights;

- attribution obligations.

Do not infer one from another.

Mere co-location in one repository does not prove applicability unless the authoritative instrument clearly applies repository-wide.

### Tokenizer eligibility

Tokenizer eligibility requires:

- official source;

- exact relationship to the model revision;

- immutable identity or explicit inclusion in the pinned model revision;

- expected tokenizer inventory;

- explicit licensing applicability;

- commercial-use disposition;

- modification disposition;

- redistribution disposition;

- offline loading;

- no remote-code requirement;

- no automatic network retrieval.

Unknown or inferred tokenizer licensing fails eligibility.

### Model-card quality

Every selected candidate must have official documentation addressing:

- intended use;

- excluded use or unacceptable use;

- known limitations;

- reliability limitations;

- language limitations where relevant;

- safety limitations;

- model-family relationship;

- architecture and context information;

- training or data disclosures at the level provided by the owner;

- runtime or deployment caveats where relevant.

Absence of meaningful limitations documentation fails the mandatory criterion.

### Immutable artifact identity

Every finalist must identify:

- official model repository;

- immutable model revision;

- official ONNX repository or subdirectory;

- immutable ONNX revision;

- graph filenames;

- every required external-data filename;

- tokenizer filenames;

- configuration filenames;

- license and notice filenames;

- expected file sizes where officially available;

- published digests where authoritative;

- fields requiring locally computed digests during future acquisition;

- artifact transport mechanism such as Git LFS where applicable.

A floating branch, rolling release, or latest tag is insufficient.

### Artifact and hardware budget

The authoritative evaluation envelope remains:

- Linux x86_64;

- 16 logical CPUs;

- approximately 30 GiB memory;

- no GPU compute;

- total model-artifact ceiling of 8 GiB;

- estimated peak candidate-process memory at or below 12 GiB;

- maximum context of 8,192 tokens;

- one candidate process at a time;

- no approved quantization.

The complete artifact footprint must include:

- ONNX graph;

- ONNX external data;

- tokenizer;

- configuration;

- required supporting model metadata;

- verification overhead;

- runtime-staging allowance.

Unknown required sizes fail eligibility.

Exactly 8 GiB may pass.

One byte above 8 GiB fails.

Exactly 12 GiB estimated process memory may pass.

One byte above 12 GiB fails.

### ONNX external-data integrity

For external-data models, qualification requires:

- graph filename;

- complete external-data filename inventory;

- authoritative graph-to-external-data relationship;

- expected size of every file where available;

- no unspecified external-data file;

- path normalization;

- no path traversal;

- no symlink dependence;

- digest requirements;

- immutable combined inventory identity.

A graph listing beside data files is not enough unless official evidence establishes the relationship.

### Bounded execution compatibility

Each finalist must satisfy the planned execution contract:

- authorized ONNX Runtime identity;

- verified runtime staging;

- verified ONNX graph;

- verified complete external-data inventory;

- verified tokenizer;

- verified configuration;

- direct argument vectors;

- no shell;

- Track 6A hardened launcher;

- offline mode;

- telemetry disabled;

- no remote code;

- no automatic retrieval;

- no automatic conversion;

- bounded startup;

- bounded generation;

- bounded output;

- one request and one response;

- process-tree cleanup;

- structured failure behavior.

Unknown behavior fails eligibility.

### Finding Explanation Assistant suitability

A finalist must plausibly support the approved first capability without being treated as authoritative.

Assess:

- structured instruction following;

- concise explanation;

- citation-ID reproduction;

- uncertainty expression;

- refusal behavior;

- distinction between deterministic facts and generated explanation;

- resistance to embedded instructions;

- output within the current schema and size limits;

- English-language suitability.

Use official evidence only during Track 7.

Do not infer actual model quality from benchmark prestige.

This suitability screen authorizes evaluation only, not production use.

### Mandatory criteria precede scoring

A candidate failing any mandatory criterion:

- is disqualified;

- receives weightedScore: null;

- cannot be selected;

- cannot receive acquisition authorization.

Only candidates passing every mandatory criterion may be scored.

Use the existing Track 4 100-point model:

- license, weight-use clarity, and provenance: 25 points;

- security, remote-code avoidance, and offline isolation: 20 points;

- local hardware and memory fit: 20 points;

- Finding Explanation Assistant evaluation suitability: 20 points;

- model-card completeness and limitation disclosure: 10 points;

- runtime maturity and reproducibility: 5 points.

Tie-breaking remains:

1. clearer weight and tokenizer licensing;

2. no custom or remote code;

3. lower estimated peak memory;

4. smaller artifact size;

5. stronger immutable artifact identity;

6. better model-card disclosure;

7. more mature offline runtime support.

Popularity, download count, benchmark rank, and company reputation are not tie-breakers.

### No gate changes

Do not change:

- corpus content;

- corpus taxonomy;

- corpus digest;

- metric definitions;

- invariant gates;

- percentage gates;

- calibration status;

- promotion status.

Calibration remains not-approved.

productionReady remains false.

## Assumed Repository State

Before editing, Cursor must prove:

- repository root is patchpilot-intelligence-evals;

- local main equals origin/main;

- Intelligence Track 6C is merged;

- Repository Hardening 1 is merged;

- specification-only commit parent equals origin/main;

- working tree is clean after the specification commit;

- repository license remains Apache-2.0;

- Python remains &gt;=3.12,&lt;3.13;

- uv.lock exists and validates;

- protected Validation, CodeQL, and Dependency Review are configured as documented;

- protected CI passes on synchronized main;

- the 24-case corpus and approved digest are unchanged;

- candidate protocol remains version 1.0.0;

- hardened mechanism remains linux-bwrap-systemd-v1;

- authorized future runtime identity remains onnxruntime v1.31.1;

- runtime installation remains unauthorized;

- corrected adapter requires verified ONNX executable artifacts;

- safetensors is prohibited as executable ONNX input;

- all five prior candidates remain disqualified;

- no prior candidate is selected;

- direct ONNX qualification remains absent;

- conversion remains not authorized;

- no runtime or model artifact exists;

- no inference-runtime dependency exists;

- no provider SDK exists;

- calibration remains not-approved;

- acquisition remains not-acquired;

- execution remains not-executed;

- realModelExecuted remains false;

- productionReady remains false;

- no sibling repository is nested in the Git tree.

If a material assumption is false, stop and report the conflict.

## Allowed Change Surface

Permitted:

- docs/specs/[intelligence-track-7.md](http://intelligence-track-7.md);

- candidate-discovery architecture;

- pre-screen criteria;

- candidate landscape and finalist records;

- model, tokenizer, ONNX, license, artifact-budget, hardware, suitability, and bounded-execution evidence;

- one selected-candidate or continued-no-selection record;

- Track 8 acquisition-authorization record;

- closed schemas required by Track 7;

- source modules for landscape validation, eligibility validation, evidence validation, budget arithmetic, suitability pre-screening, scoring, and readiness logic;

- CLI validation commands;

- deterministic tests;

- CI updates required to validate Track 7;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, and governance documentation.

Not permitted:

- artifact acquisition;

- runtime installation;

- model conversion;

- quantization;

- inference;

- reopening the five prior candidate decisions;

- adding more than eight discovery candidates;

- researching more than four finalists;

- weakening mandatory criteria;

- corpus or gate changes;

- sibling-repository inspection;

- PatchPilot integration;

- package publication;

- release;

- deployment.

## Required Repository Additions

The repository must include the conceptual equivalent of:

text</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">docs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── architecture/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [candidate-landscape-refresh.md](http://candidate-landscape-refresh.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [candidate-pre-screen.md](http://candidate-pre-screen.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [direct-onnx-selection.md](http://direct-onnx-selection.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [track8-acquisition-boundary.md](http://track8-acquisition-boundary.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── provenance/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [track7-candidate-evidence.md](http://track7-candidate-evidence.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [track7-source-register.md](http://track7-source-register.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">└── specs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── [intelligence-track-7.md](http://intelligence-track-7.md)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">schemas/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── candidate-discovery.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── finalist-eligibility.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── finalist-tokenizer.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── finalist-direct-onnx.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── finalist-artifact-budget.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── finalist-explanation-suitability.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── track7-selection.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">└── track8-acquisition-authorization.schema.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">candidates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">└── authorization/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── candidate-discovery.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── finalist-eligibility.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── finalist-tokenizer.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── finalist-direct-onnx.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── finalist-artifact-budget.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── finalist-explanation-suitability.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── track7-selection.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── track8-acquisition-authorization.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">src/patchpilot_intelligence_evals/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── candidate_[discovery.py](http://discovery.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── finalist_[eligibility.py](http://eligibility.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── finalist_[tokenizer.py](http://tokenizer.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── finalist_[onnx.py](http://onnx.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── finalist_[budget.py](http://budget.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── explanation_[suitability.py](http://suitability.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── track7_[selection.py](http://selection.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">└── track8_[authorization.py](http://authorization.py)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">tests/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── test_candidate_[discovery.py](http://discovery.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── test_finalist_[eligibility.py](http://eligibility.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── test_finalist_[tokenizer.py](http://tokenizer.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── test_finalist_[onnx.py](http://onnx.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── test_finalist_[budget.py](http://budget.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── test_explanation_[suitability.py](http://suitability.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">├── test_track7_[selection.py](http://selection.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">└── test_track8_[authorization.py](http://authorization.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794417900000,&quot;dataSource&quot;:0}">

Exact filenames may differ only to follow repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and records for:

1. candidate discovery universe;

2. finalist eligibility;

3. finalist tokenizer eligibility;

4. finalist direct official ONNX evidence;

5. finalist artifact and hardware budget;

6. finalist explanation suitability;

7. Track 7 selection;

8. Track 8 acquisition authorization.

Every schema must:

- have a stable schema ID;

- declare an explicit version;

- use additionalProperties: false;

- distinguish discovery candidates from finalists;

- enforce no more than eight discovery candidates;

- enforce no more than four finalists;

- prohibit the five prior candidate checkpoints;

- distinguish resolved, unresolved, conflicting, failed, and not-applicable states;

- identify exact official model and immutable revision;

- identify exact evidence sources;

- prohibit secrets and tenant identifiers;

- prohibit hostnames and IP addresses;

- prohibit identity-bearing local paths;

- prohibit locally observed artifact claims before acquisition;

- preserve runtimeInstallationStatus: not-installed;

- preserve acquisitionStatus: not-acquired;

- preserve conversionStatus: not-performed;

- preserve executionStatus: not-executed;

- preserve realModelExecuted: false;

- preserve productionReady: false;

- support explicit no-selection and not-authorized outcomes.

The Track 8 authorization record must retain:

- empty locally observed runtime digests;

- empty locally observed model digests;

- empty locally observed tokenizer digests;

- empty locally observed configuration digests.

## Source-Evidence Contract

Every material external claim must record:

- evidence ID;

- descriptive source name;

- exact URL;

- publisher or model owner;

- retrieval date in ISO 8601 format;

- immutable revision where applicable;

- supported claim;

- candidate applicability;

- evidence classification:

  - authoritative;

  - secondary;

  - conflicting;

  - unresolved;

- quote-free factual summary;

- conflict disposition.

License conclusions must cite official licenses or terms.

Tokenizer conclusions must cite official tokenizer evidence.

ONNX conclusions must cite official publisher evidence.

Runtime compatibility claims must cite official ONNX Runtime or publisher documentation.

Do not reproduce complete licenses, model cards, or terms.

When evidence conflicts, use the more restrictive interpretation.

## Multi-Agent Execution Model

Cursor Plan is the lead candidate-landscape orchestrator.

Use Grok 4.7 Extra High for:

- discovery-boundary synthesis;

- license and provenance interpretation;

- tokenizer decisions;

- ONNX artifact authority;

- commercial-use and redistribution decisions;

- candidate selection;

- Track 8 authorization;

- conflicts;

- independent final verification.

Delegate parallel read-only research and controlled implementation to these specialists.

### Agent 1: Landscape-discovery specialist

Owns:

- bounded discovery universe;

- duplicate and prior-family detection;

- initial mandatory pre-screen;

- discovery-to-finalist reduction.

### Agent 2: Licensing and provenance specialist

Owns:

- weight licenses;

- source licenses;

- commercial use;

- redistribution;

- modification rights;

- acceptable-use terms;

- immutable revision evidence.

### Agent 3: Tokenizer specialist

Owns:

- tokenizer identity;

- tokenizer licensing;

- tokenizer file inventory;

- offline behavior;

- network-retrieval risk;

- remote-code risk.

### Agent 4: Direct-ONNX specialist

Owns:

- official ONNX provenance;

- graph and external-data inventories;

- immutable revisions;

- runtime compatibility;

- official-versus-community classification.

### Agent 5: Hardware and execution specialist

Owns:

- artifact budgets;

- memory estimates;

- context limits;

- ONNX Runtime compatibility;

- hardened execution;

- bounded subprocess compatibility.

### Agent 6: Explanation-suitability and selection specialist

Owns:

- model-card limitations;

- Finding Explanation Assistant suitability;

- mandatory criteria;

- scoring;

- tie-breaking;

- Track 7 selection;

- Track 8 authorization.

### Agent 7: Independent verification specialist

Runs after implementation.

Must not own:

- discovery;

- licensing;

- tokenizer decisions;

- ONNX evidence;

- budget arithmetic;

- suitability assessment;

- selection or authorization.

### Coordination Rules

The parent agent must:

- run discovery research in parallel;

- deduplicate before full research;

- enforce candidate and finalist limits;

- require decision-grade evidence;

- synthesize authority before edits;

- assign exclusive file ownership;

- prevent overlapping edits;

- preserve task order;

- stop on unresolved mandatory evidence;

- integrate centrally;

- commission a fresh independent reviewer.

Every specialist must return:

- finding;

- exact authoritative evidence;

- evidence classification;

- mandatory-criterion effect;

- unresolved conflict;

- recommendation;

- files owned;

- tests required.

## Ordered Execution Plan

Cursor Plan must create one to-do for each task and execute the tasks in order.

### Task 1: Verify the Post-Hardening Baseline

#### Allowed files or subsystem

Read-only Git state, repository workflows, governance, candidate records, schemas, tests, CLI, architecture, and provenance.

#### Required behavior

Confirm every assumed-state item.

Record:

- synchronized main identity;

- protected-check state;

- previous candidate exclusions;

- runtime identity;

- hardened-profile identity;

- adapter identity;

- artifact and memory limits;

- exact ownership for Tasks 2 through 8.

#### Tests

Run safe Git inspection and existing locked validation commands as necessary.

#### Done condition

The baseline is proven, no stop condition exists, and file ownership is assigned.

### Task 2: Build the Bounded Candidate Discovery Universe

#### Allowed files or subsystem

Official read-only research, discovery schema, discovery record, validation module, CLI, documentation, and focused tests.

#### Required behavior

Identify no more than eight candidate families.

For each discovery candidate, record:

- official family and checkpoint identity;

- publisher;

- parameter count;

- context length;

- instruction capability;

- official model card;

- immutable revision availability;

- initial weight-license status;

- initial tokenizer-evidence status;

- official direct ONNX indication;

- approximate published artifact size;

- CPU-only plausibility;

- remote-code indication;

- prior-family duplicate status;

- pre-screen outcome;

- exclusion reason or finalist advancement.

Reject:

- previous five checkpoints;

- mirrors;

- community conversions;

- candidates outside the parameter range without approved justification;

- candidates requiring conversion;

- candidates requiring quantization;

- hosted-only candidates;

- candidates without official documentation.

#### Tests

Validate candidate limits, duplicate detection, prior-candidate exclusion, and pre-screen behavior.

#### Done condition

A bounded discovery universe is recorded and no more than four finalists advance.

### Task 3: Close Finalist Licensing, Provenance, and Model-Card Evidence

#### Allowed files or subsystem

Official research, finalist eligibility schema, record, validator, CLI, documentation, and tests.

#### Required behavior

For each finalist, record:

- official identity;

- exact immutable revision;

- source-code license;

- model-weight license;

- commercial-use status;

- redistribution status;

- modification rights;

- acceptable-use restrictions;

- attribution requirements;

- intended use;

- excluded use;

- known limitations;

- language limitations;

- safety and reliability caveats;

- remote-code requirement;

- mandatory-criterion status.

Unknown, inferred, conflicting, or revision-inapplicable evidence fails the criterion.

#### Tests

Validate evidence completeness, revision applicability, and fail-closed decisions.

#### Done condition

Every finalist has a complete legal, provenance, and model-card decision.

### Task 4: Close Finalist Tokenizer and Direct-ONNX Evidence

#### Allowed files or subsystem

Official research, tokenizer and ONNX schemas, records, validators, CLI, documentation, and tests.

#### Required behavior

For each finalist, record tokenizer:

- official source;

- immutable identity;

- file inventory;

- license applicability;

- commercial use;

- redistribution;

- modification;

- offline operation;

- automatic retrieval risk;

- remote-code requirement.

Record direct ONNX:

- official publisher;

- exact model relationship;

- immutable revision;

- graph inventory;

- external-data inventory;

- tokenizer and configuration relationship;

- expected sizes;

- expected published digests;

- fields requiring future local digests;

- remote-code requirement;

- official-versus-community status;

- ONNX Runtime compatibility.

Unknown or incomplete inventory fails direct-ONNX eligibility.

#### Tests

Validate license applicability, official-source rules, graph inventories, external-data completeness, and immutable revisions.

#### Done condition

Every finalist has explicit tokenizer and direct-ONNX qualification or disqualification.

### Task 5: Validate Artifact Budget, Hardware Fit, and Bounded Execution

#### Allowed files or subsystem

Budget and execution records, validators, arithmetic modules, CLI, documentation, and tests.

#### Required behavior

For every finalist, calculate:

- ONNX graph size;

- external-data total;

- tokenizer and configuration total;

- required metadata total;

- runtime-staging allowance;

- quarantine and verification overhead;

- complete artifact footprint;

- estimated peak process memory;

- context compatibility;

- storage headroom;

- CPU-only viability.

Validate execution compatibility:

- authorized future runtime identity;

- verified artifact requirements;

- corrected adapter contract;

- hardened launcher;

- offline operation;

- telemetry disabled;

- no remote code;

- no automatic retrieval;

- no conversion;

- no quantization;

- bounded startup;

- bounded generation;

- bounded output;

- process-tree cleanup.

Unknown required values fail eligibility.

#### Tests

Cover exact limits, one-byte-over limits, unknown values, multiple external-data files, and incompatible execution states.

#### Done condition

Every finalist has a fail-closed hardware and execution decision.

### Task 6: Assess Finding Explanation Assistant Suitability

#### Allowed files or subsystem

Official model documentation, suitability schema and record, validator, documentation, and tests.

#### Required behavior

Assess only from official evidence:

- instruction-following support;

- structured-output support;

- English-language capability;

- context sufficiency;

- concise generation support;

- limitations relevant to factual explanation;

- safety limitations;

- citation-ID reproduction plausibility;

- refusal and uncertainty support;

- deployment caveats.

Do not claim measured grounding or hallucination performance.

The result is:

- suitable for offline evaluation;

- unsuitable;

- unresolved.

Unresolved mandatory suitability fails selection.

#### Tests

Validate evidence completeness and prohibit unsupported quality claims.

#### Done condition

Every finalist has an evidence-bounded explanation-suitability decision.

### Task 7: Select One Candidate or Preserve No-Selection and Decide Track 8 Authorization

#### Allowed files or subsystem

Selection schema, authorization schema, records, scoring and readiness modules, CLI, documentation, and tests.

#### Required behavior

A candidate may be selected only when:

- every mandatory legal criterion passes;

- tokenizer eligibility passes;

- direct official ONNX eligibility passes;

- artifact budget passes;

- hardware fit passes;

- bounded execution passes;

- explanation suitability passes;

- immutable identities are fixed;

- no unresolved conflict remains;

- no conversion or quantization is required.

Disqualified candidates retain weightedScore: null.

Score only fully eligible candidates.

Apply the Track 4 tie-break order if needed.

If no candidate passes:

- preserve selectionOutcome: no-selection;

- set Track 8 authorizationOutcome: not-authorized;

- list exact blockers;

- preserve all disabled states.

If one candidate passes:

- recommend it for a later controlled acquisition Session;

- do not acquire anything;

- preserve all observed digest arrays as empty;

- preserve runtime not installed;

- preserve model not acquired;

- preserve execution not performed;

- preserve production readiness false.

#### Tests

Validate no-selection, single selection, score arithmetic, ties, disqualifications, and fail-closed authorization.

#### Done condition

Track 7 has one evidence-backed selection or a durable no-selection decision, and Track 8 is either authorized in principle or explicitly withheld.

### Task 8: Documentation, CI, and Independent Verification

#### Allowed files or subsystem

README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, workflows, governance, and complete diff.

#### Required behavior

Document:

- discovery method;

- candidate universe;

- finalist reduction;

- evidence standards;

- legal decisions;

- tokenizer decisions;

- direct-ONNX decisions;

- budget and hardware decisions;

- execution compatibility;

- suitability;

- selection;

- Track 8 outcome;

- residual risks;

- no-download boundary.

Update Repository Contracts to validate every Track 7 schema and record.

CI must not:

- download candidate artifacts;

- install runtimes;

- use model hubs for artifacts;

- perform conversion;

- perform inference;

- upload research output containing copied license or model-card text.

Assign verification to a fresh independent agent.

#### Tests

Run every command in Verification.

#### Done condition

Track 7 is documented, validated, CI-enforced, independently reviewed, and ready for Principal Architect review.

## Out of Scope

Intelligence Track 7 must not:

- reopen the five prior candidate decisions;

- add more than eight discovery candidates;

- advance more than four finalists;

- download runtimes, models, tokenizers, configurations, or ONNX artifacts;

- install runtimes;

- perform conversion;

- authorize quantization;

- perform inference;

- change the corpus;

- change evaluation metrics or gates;

- modify patchpilot;

- modify neural-from-scratch;

- inspect sibling-repository files;

- use tenant or production data;

- implement shadow mode;

- implement PatchPilot APIs or UI;

- create production composition;

- publish packages;

- create releases;

- deploy.

## Stop Conditions

Stop and report if:

1. The specification-only commit parent differs from origin/main.

2. The working tree contains unrelated changes.

3. Track 6C or Repository Hardening 1 is not merged.

4. Protected checks are failing on synchronized main.

5. Candidate discovery requires downloading artifacts.

6. More than eight candidate families are needed.

7. More than four finalists are needed.

8. A candidate is only available through an unofficial conversion.

9. A candidate requires conversion or quantization.

10. Weight licensing is unresolved for a proposed finalist.

11. Tokenizer licensing is unresolved for a proposed finalist.

12. Commercial-use or redistribution terms are unclear for a proposed finalist.

13. A candidate lacks an immutable official revision.

14. A candidate lacks meaningful official limitations.

15. A complete ONNX external-data inventory is unavailable.

16. Required artifact sizes are unknown.

17. Artifact footprint exceeds 8 GiB.

18. Estimated process memory exceeds 12 GiB.

19. Remote code is required.

20. Bounded hardened execution is unproven.

21. Existing criteria or gates must be weakened.

22. A sibling repository must be inspected.

23. Work cannot fit in one pull-request-sized branch.

On a stop condition:

- do not select a candidate;

- do not authorize acquisition;

- do not download artifacts;

- do not weaken criteria;

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

- every Track 7 schema validation;

- every Track 7 record validation;

- candidate-count tests;

- finalist-count tests;

- prior-candidate exclusion tests;

- duplicate-family tests;

- immutable-revision tests;

- license-applicability tests;

- tokenizer-eligibility tests;

- official-ONNX-source tests;

- external-data inventory tests;

- artifact-budget tests;

- exact 8 GiB boundary tests;

- exact 12 GiB memory-boundary tests;

- bounded-execution tests;

- explanation-suitability tests;

- unsupported-quality-claim tests;

- null-score tests;

- scoring and tie-break tests;

- Track 8 authorization tests;

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

- no candidate was selected unless every mandatory criterion passed;

- no prior disqualified checkpoint was reopened;

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

4. Post-hardening baseline

5. Discovery methodology

6. Discovery universe

7. Pre-screen exclusions

8. Finalist set

9. Official evidence reviewed

10. License and use-rights findings

11. Tokenizer findings

12. Direct official ONNX findings

13. ONNX graph and external-data inventories

14. Artifact-budget calculations

15. Hardware-fit decisions

16. Bounded-execution compatibility

17. Explanation-suitability findings

18. Mandatory-criterion outcomes

19. Scores or null scores

20. Selected candidate or no-selection

21. Track 8 authorization or withholding

22. Files changed

23. Dependency and lockfile impact

24. Every verification command and actual result

25. CI changes

26. Protected-check impact

27. Independent verification

28. Scope compliance

29. Unresolved decisions

30. Residual risks

31. Exact Track 8 recommendation

32. Proposed Conventional Commit

33. Proposed PR title and summary

34. Required post-merge steps

Final verdict must be exactly one of:

- TRACK 8 CONTROLLED ACQUISITION AUTHORIZED

- TRACK 8 CONTROLLED ACQUISITION AUTHORIZED WITH DOCUMENTED RESIDUALS

- TRACK 8 CONTROLLED ACQUISITION NOT AUTHORIZED

- BLOCKED BY UNRESOLVED AUTHORITY

Explicitly confirm:

- no runtime binary, wheel, image, or shared library was downloaded;

- no runtime was installed;

- no model, tokenizer, configuration, or ONNX artifact was acquired;

- no conversion or quantization occurred;

- no inference occurred;

- no prior disqualified checkpoint was reopened;

- no candidate was selected unless every mandatory criterion passed;

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

INTELLIGENCE TRACK 7 READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT

or:

INTELLIGENCE TRACK 7 BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW