Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 6C: Candidate Eligibility Closure and Direct-ONNX Reassessment

## Identity

- **Repository:** patchpilot-intelligence-evals

- **Session ID:** Intelligence Track 6C

- **Mission:** Reassess exactly the five previously reviewed candidate families using authoritative, revision-specific evidence; attempt to close their mandatory licensing, tokenizer, model-card, immutable-revision, artifact-format, digest, commercial-use, redistribution, and bounded-execution gaps; and authorize at most one candidate for a future direct official ONNX acquisition path.

- **Base commit:** The parent of the spec-only commit introducing this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.

- **Expected repository state:** Intelligence Track 6B merged with an external runtime-staging boundary, corrected ONNX Runtime adapter contract, direct official ONNX findings, conversion-plan withholding, resolutionOutcome: no-path, and Track 6C controlled staging not ready.

- **Branch:** docs/intelligence-track-6c-candidate-eligibility

- **Change type:** Primary-source research, evidence closure, candidate authorization records, closed schemas, validation code, tests, documentation, and CI enforcement. No artifact acquisition, runtime installation, model conversion, or inference.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, create a tag, publish a package, create a release, deploy, modify Git history, change GitHub repository settings, download runtime or model artifacts, install a runtime, perform conversion, or execute inference.

## Architectural Outcome

Intelligence Track 6C must answer:

> Does any one of the five existing candidate families now satisfy every mandatory legal, provenance, security, hardware, format, and evaluation criterion for future controlled acquisition as a direct official ONNX artifact?

The completed Session must:

1. Preserve the five-candidate boundary from Track 4.

2. Reassess each candidate using official revision-specific evidence.

3. Resolve or confirm every previously recorded mandatory blocker.

4. Distinguish model-source evidence from artifact-specific evidence.

5. Distinguish model-weight licensing from source-code licensing.

6. Distinguish tokenizer provenance and licensing from model licensing.

7. Distinguish official publisher-provided ONNX from third-party conversions.

8. Verify immutable repository and artifact identities where official metadata permits.

9. Assess direct official ONNX artifact size against the approved hardware budget.

10. Assess ONNX external-data inventories.

11. assess compatibility with the authorized ONNX Runtime identity.

12. assess compatibility with the hardened Track 6A execution boundary.

13. assess compatibility with the corrected Track 6B adapter contract.

14. apply the Track 4 mandatory criteria and scoring model without modification.

15. select at most one candidate.

16. produce a controlled-acquisition authorization or preserve no-selection.

17. keep all runtime and model artifacts unacquired.

18. keep all execution and production states disabled.

No candidate may be selected merely because an ONNX artifact exists.

## Governing Authority

Before research or editing, Cursor must reread:

- all repository [AGENTS.md](http://AGENTS.md) files;

- [README.md](http://README.md);

- [SECURITY.md](http://SECURITY.md);

- [CONTRIBUTING.md](http://CONTRIBUTING.md);

- NOTICE;

- LICENSE;

- .gitignore;

- pyproject.toml;

- uv.lock;

- all protected workflows;

- all documents under docs/architecture;

- all documents under docs/provenance;

- all current JSON Schemas;

- all candidate and authorization records;

- Track 4 candidate-selection criteria;

- Track 4 candidate shortlist;

- Track 4 approved no-selection decision;

- Track 5 candidate evidence-closure record;

- Track 5 runtime and acquisition decisions;

- Track 6A hardened execution profile;

- Track 6A runtime authorization;

- Track 6A implementation-review record;

- Track 6B runtime-staging boundary;

- Track 6B corrected runtime-adapter contract;

- Track 6B candidate-format resolution;

- Track 6B ONNX conversion plan;

- Track 6B Track 6C readiness record;

- existing CLI commands;

- existing tests;

- Intelligence Track 2 through Track 6B specifications;

- merged Track 6B implementation and protected-CI evidence.

Do not inspect local files in patchpilot or neural-from-scratch.

Public read-only research is permitted only for:

- official model-owner repositories;

- official immutable model revisions;

- official model cards;

- official weight-license instruments;

- official source-code licenses;

- official acceptable-use terms;

- official tokenizer repositories;

- official tokenizer-license instruments;

- official publisher-provided ONNX repositories;

- official artifact listings;

- official ONNX Runtime documentation;

- original publisher documentation;

- official security advisories.

Secondary sources may identify a possible gap. Secondary sources cannot close a mandatory criterion.

## Candidate Scope

Reassess exactly these five candidate families:

1. Qwen/Qwen2.5-1.5B-Instruct

2. Qwen/Qwen2.5-3B-Instruct

3. HuggingFaceTB/SmolLM2-1.7B-Instruct

4. allenai/OLMo-2-0425-1B-Instruct

5. google/gemma-3-1b-it

Do not add another candidate family.

Do not replace a candidate with a newer, larger, smaller, quantized, community-converted, fine-tuned, or similarly named model unless the artifact is an official representation of the same reviewed family and the relationship is explicitly documented by the model owner.

## Invariants

### Deterministic PatchPilot authority

No candidate, runtime, artifact, or research conclusion may become authoritative over:

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

- remediation-queue order;

- priority review;

- Finding lifecycle;

- remediation completion;

- PatchPilot audit state.

Any future candidate output remains advisory evaluation data.

### Existing fail-closed decisions remain authoritative

Unless Track 6C proves every mandatory requirement for one candidate:

- selectionOutcome remains no-selection;

- resolutionOutcome remains no-path;

- directOnnxQualified remains false;

- runtimeInstallationStatus remains not-installed;

- acquisitionStatus remains not-acquired;

- conversionStatus remains not-performed;

- executionStatus remains not-executed;

- realModelExecuted remains false;

- productionReady remains false.

### No acquisition, installation, conversion, or inference

Track 6C must not:

- download ONNX Runtime;

- download a wheel, archive, shared library, or container image;

- download model weights;

- download tokenizer files;

- download real model configuration files;

- install a runtime;

- install conversion tooling;

- perform conversion;

- parse a real ONNX graph;

- load a real tokenizer;

- execute inference;

- contact a hosted provider;

- populate a persistent artifact cache.

Official repository metadata, model cards, licenses, file listings, immutable revisions, and published digests may be inspected through read-only research.

### Official direct ONNX only

A direct ONNX path qualifies only when:

- the artifact is published by the official model owner or an explicitly authorized official publisher;

- the immutable revision is fixed;

- the relationship to the reviewed model family is explicit;

- the artifact is not an unreviewed community conversion;

- the model-weight license applies to the ONNX artifact;

- tokenizer provenance and licensing are resolved;

- commercial use is resolved;

- redistribution requirements are resolved or redistribution is unnecessary;

- acceptable-use restrictions are recorded;

- no remote code is required;

- expected artifact inventory is available;

- expected external-data inventory is available where applicable;

- expected size fits the approved hardware envelope;

- locally computed SHA-256 values can be produced during a later acquisition;

- the artifact is compatible with the authorized runtime identity;

- the artifact is compatible with the Track 6B adapter contract;

- the artifact can be evaluated through the Track 6A hardened launcher.

### Source and artifact licensing remain separate

The repository must distinguish:

- source-code license;

- model-weight license;

- tokenizer license;

- ONNX artifact license;

- acceptable-use restrictions;

- conversion rights;

- redistribution rights;

- commercial-use rights.

Do not infer any one of these from another without explicit authoritative evidence.

### Tokenizer closure

Tokenizer eligibility requires:

- official tokenizer source;

- immutable tokenizer revision or explicit inclusion in the model revision;

- tokenizer file inventory;

- tokenizer licensing;

- modification rights where relevant;

- commercial-use position;

- redistribution position;

- no remote-code requirement;

- no automatic retrieval requirement;

- compatibility with offline execution.

Assumed license inheritance is not sufficient.

### Model-card limitations

A candidate must have an official model card or equivalent official documentation that meaningfully states:

- intended use;

- excluded or inappropriate use;

- known limitations;

- language limitations where relevant;

- reliability limitations;

- safety limitations;

- training or data disclosures at the level published by the owner;

- model-family relationships;

- runtime or deployment caveats where relevant.

A missing limitations section cannot be replaced with assumptions based on benchmark results.

### Immutable artifact identity

A candidate path must identify:

- official repository;

- immutable revision;

- expected ONNX graph files;

- expected external-data files;

- expected tokenizer files;

- expected configuration files;

- expected license and notice files;

- expected file sizes where available;

- published digests where authoritative;

- which digests must be computed locally during later acquisition;

- whether Git LFS or another artifact mechanism is used.

A floating main branch is insufficient.

### Hardware and artifact budget

The approved evaluation-machine envelope remains:

- Linux;

- x86_64;

- 16 logical CPUs;

- approximately 30 GiB memory;

- no GPU compute;

- maximum model-artifact footprint of 8 GiB;

- estimated peak candidate-process memory at or below 12 GiB;

- context at or below 8,192 tokens;

- one candidate process at a time;

- no approved quantization.

Artifact size calculations must include:

- ONNX graph files;

- ONNX external-data files;

- tokenizer files;

- required configuration files;

- temporary verification overhead;

- runtime staging overhead where relevant.

An artifact footprint exceeding 8 GiB is disqualified unless a later Principal Architect decision changes the authority.

Track 6C must not change that limit.

### ONNX external-data integrity

Where ONNX external data is used, the authorization record must identify:

- graph filename;

- every required external-data filename;

- expected size of every file where available;

- expected relationship among the graph and external-data files;

- prohibition on additional external-data files;

- missing-file behavior;

- digest requirements;

- path normalization;

- symlink prohibition;

- immutable inventory identity.

A graph without a complete external-data inventory does not qualify.

### Bounded subprocess compatibility

A candidate is compatible only when the planned execution can preserve:

- one request and one response per process invocation;

- direct argument arrays;

- no shell;

- local verified runtime path;

- local verified ONNX path;

- local verified tokenizer and configuration paths;

- no automatic download;

- no remote code;

- no automatic conversion;

- offline mode;

- telemetry disabled;

- bounded startup;

- bounded generation;

- bounded output;

- process-tree cleanup;

- Track 6A hardened execution.

Compatibility must be supported by official runtime and model evidence, not assumed.

### Scoring remains subordinate to mandatory criteria

Candidates failing any mandatory criterion:

- remain disqualified;

- receive weightedScore: null;

- cannot be selected;

- cannot proceed to acquisition.

Only a candidate passing every mandatory criterion may receive a weighted score.

The Track 4 100-point scoring model and tie-break order remain unchanged.

### No conversion-path authorization

Track 6C focuses on direct official ONNX eligibility.

The Track 6B conversion decision remains not-authorized.

Track 6C must not authorize:

- safetensors-to-ONNX conversion;

- quantization;

- community-converted ONNX;

- local exporter installation;

- numerical-equivalence gates;

- conversion tooling.

If no direct official ONNX candidate qualifies, preserve resolutionOutcome: no-path.

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

Before editing, Cursor must prove:

- repository root is patchpilot-intelligence-evals;

- local main equals origin/main;

- Intelligence Track 6B is merged;

- spec-only commit parent equals origin/main;

- working tree is clean after the specification commit;

- repository license remains Apache-2.0;

- Python remains &gt;=3.12,&lt;3.13;

- uv.lock exists and validates;

- protected CI passes on synchronized main;

- 244 or more tests pass on synchronized main;

- the approved 24-case corpus is unchanged;

- approved corpus digest remains unchanged;

- candidate protocol remains version 1.0.0;

- Track 6A hardened profile remains approved with residuals;

- hardened mechanism remains linux-bwrap-systemd-v1;

- authorized future runtime identity remains onnxruntime v1.31.1;

- runtime installation remains unauthorized;

- corrected Track 6B adapter requires verified ONNX executable artifacts;

- safetensors is prohibited as an executable ONNX Runtime input;

- Track 6B direct ONNX outcome is unqualified;

- Track 6B conversion authorization remains not authorized;

- Track 6C readiness remains not ready;

- candidate selection remains no-selection;

- acquisition remains not acquired;

- conversion remains not performed;

- execution remains not executed;

- no runtime or model artifact exists;

- no runtime dependency exists;

- no provider SDK exists;

- no tenant or customer data exists;

- no sibling repository is nested in the Git tree;

- realModelExecuted remains false;

- productionReady remains false.

If a material assumption is false, stop and report the conflict.

## Allowed Change Surface

Permitted:

- docs/specs/[intelligence-track-6c.md](http://intelligence-track-6c.md);

- candidate eligibility architecture;

- candidate licensing and provenance records;

- tokenizer-eligibility records;

- direct official ONNX evidence records;

- bounded-subprocess compatibility records;

- artifact-budget records;

- candidate authorization or continued no-selection records;

- Track 6D acquisition-readiness records;

- closed JSON Schemas required by this Session;

- source modules for evidence-record validation, candidate eligibility, artifact-budget arithmetic, ONNX inventory validation, scoring validation, and readiness logic;

- CLI validation commands;

- deterministic tests using synthetic records and arithmetic;

- CI updates required to validate Track 6C;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, and provenance documents.

Not permitted:

- runtime or model download;

- tokenizer or configuration download;

- conversion;

- inference;

- runtime installation;

- candidate-family expansion;

- quantization;

- corpus or gate changes;

- sibling-repository inspection;

- PatchPilot integration;

- package publication;

- release;

- deployment.

## Required Repository Additions

The repository must include the conceptual equivalent of:

text</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">docs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── architecture/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [candidate-eligibility-closure.md](http://candidate-eligibility-closure.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [direct-onnx-eligibility.md](http://direct-onnx-eligibility.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [tokenizer-eligibility.md](http://tokenizer-eligibility.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [track6d-acquisition-readiness.md](http://track6d-acquisition-readiness.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── provenance/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [candidate-license-closure.md](http://candidate-license-closure.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [direct-onnx-evidence.md](http://direct-onnx-evidence.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">└── specs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── [intelligence-track-6c.md](http://intelligence-track-6c.md)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">schemas/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── candidate-eligibility-closure.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── tokenizer-eligibility.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── direct-onnx-artifact.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── candidate-artifact-budget.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── bounded-subprocess-compatibility.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">└── track6d-acquisition-readiness.schema.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">candidates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">└── authorization/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── candidate-eligibility-closure.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── tokenizer-eligibility.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── direct-onnx-artifacts.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── candidate-artifact-budget.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; ├── bounded-subprocess-compatibility.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── track6d-acquisition-readiness.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">src/patchpilot_intelligence_evals/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── candidate_[eligibility.py](http://eligibility.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── tokenizer_[eligibility.py](http://eligibility.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── direct_onnx_[evidence.py](http://evidence.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── artifact_[budget.py](http://budget.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── subprocess_[compatibility.py](http://compatibility.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">└── track6d_[readiness.py](http://readiness.py)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">tests/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── test_candidate_[eligibility.py](http://eligibility.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── test_tokenizer_[eligibility.py](http://eligibility.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── test_direct_onnx_[evidence.py](http://evidence.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── test_artifact_[budget.py](http://budget.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">├── test_subprocess_[compatibility.py](http://compatibility.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">└── test_track6d_[readiness.py](http://readiness.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794395100000,&quot;dataSource&quot;:0}">

Exact names may differ only to follow existing repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and validated records for:

1. candidate eligibility closure;

2. tokenizer eligibility;

3. direct official ONNX artifact evidence;

4. candidate artifact budget;

5. bounded subprocess compatibility;

6. Track 6D acquisition readiness.

Every schema must:

- have a stable schema ID;

- declare an explicit version;

- use additionalProperties: false;

- distinguish resolved, unresolved, conflicting, failed, and not-applicable states;

- identify exact candidate family and immutable revision;

- identify evidence sources;

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

- support explicit no-selection and not-ready outcomes.

The Track 6D readiness record must retain empty locally observed artifact digests.

## Source-Evidence Contract

Every material external claim must record:

- evidence ID;

- descriptive source name;

- exact URL;

- publisher or model owner;

- retrieval date in ISO 8601 format;

- immutable revision, where applicable;

- supported claim;

- evidence classification:

  - authoritative;

  - secondary;

  - conflicting;

  - unresolved;

- quote-free factual summary;

- applicability to the exact candidate family and revision;

- conflict disposition.

Do not copy complete licenses, model cards, or terms into the repository.

License decisions must cite official license or official terms.

Tokenizer decisions must cite official tokenizer evidence.

ONNX decisions must cite official artifact evidence.

If evidence conflicts, use the more restrictive interpretation.

## Multi-Agent Execution Model

Cursor Plan is the lead candidate-eligibility orchestrator.

Use Grok 4.7 Extra High for:

- license and provenance interpretation;

- tokenizer-eligibility decisions;

- ONNX artifact authority;

- commercial-use and redistribution decisions;

- bounded-execution compatibility;

- candidate selection;

- readiness decisions;

- conflict resolution;

- independent verification.

Delegate parallel read-only research and controlled implementation to these specialists.

### Agent 1: Qwen eligibility specialist

Owns eligibility evidence for:

- Qwen2.5 1.5B Instruct;

- Qwen2.5 3B Instruct.

Must keep each checkpoint and license instrument distinct.

### Agent 2: SmolLM2 eligibility specialist

Owns:

- model-weight licensing;

- tokenizer provenance;

- official ONNX evidence;

- artifact size;

- external-data inventory;

- hardware fit.

### Agent 3: OLMo eligibility specialist

Owns:

- model-weight licensing;

- responsible-use terms;

- tokenizer provenance;

- official ONNX evidence;

- immutable revision;

- commercial-use disposition.

### Agent 4: Gemma eligibility specialist

Owns:

- model terms;

- tokenizer rights;

- remote restriction clauses;

- official ONNX evidence;

- immutable revision;

- redistribution and commercial use.

### Agent 5: ONNX inventory and hardware specialist

Owns:

- direct official ONNX artifact inventories;

- external-data relationships;

- size arithmetic;

- 8 GiB ceiling;

- 12 GiB memory envelope;

- runtime-format compatibility.

### Agent 6: Subprocess and readiness specialist

Owns:

- bounded subprocess compatibility;

- corrected adapter requirements;

- hardened profile compatibility;

- Track 6D readiness logic;

- no-selection handling.

### Agent 7: Independent verification specialist

Runs after implementation.

Must not own:

- candidate evidence;

- tokenizer decisions;

- ONNX evidence;

- artifact budget;

- subprocess compatibility;

- readiness outcome.

### Coordination Rules

The parent agent must:

- run primary-source research in parallel;

- require decision-grade evidence from every specialist;

- synthesize authority before edits;

- assign exclusive file ownership;

- prevent overlapping edits;

- preserve the five-candidate boundary;

- stop on unresolved mandatory evidence;

- integrate centrally;

- commission a fresh independent reviewer.

Every specialist must return:

- finding;

- exact evidence;

- authority classification;

- mandatory-criterion implication;

- unresolved conflict;

- recommended decision;

- files owned;

- tests required.

## Ordered Execution Plan

Cursor Plan must create one to-do for each task and execute the tasks in order.

### Task 1: Verify the Track 6B Baseline

#### Allowed files or subsystem

Read-only Git state, Track 6B schemas, records, implementation, tests, workflow, and documentation.

#### Required behavior

Confirm every assumed-state item.

Record:

- corrected adapter identity;

- no-path decision;

- conversion withholding;

- no-selection state;

- runtime and hardened-profile identities;

- exact file ownership for Tasks 2 through 8.

#### Tests

Run safe Git inspection and existing locked validations as needed.

#### Done condition

The Track 6B baseline is proven and no stop condition exists.

### Task 2: Implement Candidate Eligibility and Evidence Closure

#### Allowed files or subsystem

Eligibility schema, structured record, validation module, CLI, documentation, and focused tests.

#### Required behavior

For each of the five candidates, record:

- exact candidate identity;

- immutable revision;

- prior blockers;

- current official evidence;

- model-weight license result;

- code-license result;

- commercial-use result;

- redistribution result;

- acceptable-use result;

- model-card limitations result;

- remote-code result;

- official-source result;

- unresolved conflicts;

- mandatory-criterion outcome;

- scoring eligibility;

- weighted score only when every mandatory criterion passes.

Disqualified candidates must have weightedScore: null.

#### Tests

Validate closure records and scoring rules.

#### Done condition

Every candidate has a complete fail-closed eligibility decision.

### Task 3: Implement Tokenizer Eligibility

#### Allowed files or subsystem

Tokenizer schema, record, validation module, CLI, documentation, and focused tests.

#### Required behavior

For each candidate family, record:

- tokenizer identity;

- source;

- immutable revision;

- file inventory where officially published;

- model relationship;

- license;

- commercial use;

- redistribution;

- modification;

- offline loading;

- remote-code requirement;

- automatic retrieval risk;

- eligibility outcome;

- unresolved conflicts.

Do not infer the tokenizer license from the model license.

#### Tests

Validate records and prove missing or assumed licenses fail eligibility.

#### Done condition

Every family has an explicit tokenizer eligibility decision.

### Task 4: Implement Direct Official ONNX Evidence

#### Allowed files or subsystem

Direct-ONNX schema, structured record, validation code, CLI, documentation, and focused tests.

#### Required behavior

For each family, record:

- direct official ONNX availability;

- publisher;

- source;

- immutable revision;

- graph inventory;

- external-data inventory;

- expected sizes;

- expected digests where authoritative;

- local digests as empty;

- model-family relationship;

- model and tokenizer licensing;

- remote-code requirement;

- runtime compatibility;

- official or unofficial status;

- direct-path eligibility;

- blockers.

Unofficial conversions must be rejected.

#### Tests

Validate direct-ONNX evidence, graph inventory, external-data completeness, and official-source rules.

#### Done condition

Every family has a direct official ONNX qualification or disqualification.

### Task 5: Implement Artifact-Budget and Hardware-Fit Validation

#### Allowed files or subsystem

Budget schema, records, arithmetic module, CLI, documentation, and focused tests.

#### Required behavior

Calculate:

- ONNX graph size;

- external-data total;

- tokenizer and configuration total;

- runtime-staging allowance;

- quarantine and verification overhead;

- complete artifact footprint;

- estimated peak process memory;

- fit against the 8 GiB artifact limit;

- fit against the 12 GiB process-memory envelope;

- context compatibility;

- storage headroom.

Unknown required values must fail eligibility.

Do not authorize quantization.

#### Tests

Test exact boundaries, overflow, unknown values, and multiple external-data files.

#### Done condition

Every direct path has an explicit hardware-fit decision.

### Task 6: Implement Bounded Subprocess Compatibility

#### Allowed files or subsystem

Compatibility schema, records, validation module, adapter contract references, documentation, and focused tests.

#### Required behavior

For each candidate path, determine whether the planned execution preserves:

- verified runtime identity;

- verified ONNX graph;

- complete verified external-data inventory;

- verified tokenizer and configuration;

- direct argument arrays;

- no shell;

- hardened launcher;

- offline execution;

- telemetry disabled;

- no automatic retrieval;

- no remote code;

- no automatic conversion;

- bounded startup and generation;

- one request and one response;

- process-tree cleanup.

Unknown or unsupported values must fail compatibility.

#### Tests

Validate compatible and incompatible synthetic records.

#### Done condition

Every candidate path has a bounded-execution decision.

### Task 7: Select One Candidate or Preserve No-Selection and Decide Track 6D Readiness

#### Allowed files or subsystem

Track 6D schema, record, selection logic, CLI, documentation, and focused tests.

#### Required behavior

Select at most one candidate only if:

- candidate eligibility passes;

- tokenizer eligibility passes;

- direct official ONNX eligibility passes;

- artifact budget passes;

- hardware fit passes;

- bounded subprocess compatibility passes;

- immutable revision is fixed;

- required evidence is authoritative;

- no unresolved mandatory conflict remains;

- no conversion or quantization is required.

If more than one candidate passes, use the existing Track 4 score and tie-break order.

If none passes:

- preserve selectionOutcome: no-selection;

- set readinessOutcome: not-ready;

- list exact blockers;

- preserve all disabled states.

If one passes, the record may recommend a future controlled acquisition Session, but must still preserve:

- runtime not installed;

- model not acquired;

- conversion not performed;

- execution not performed;

- local digests empty;

- real model not executed;

- production readiness false.

#### Tests

Validate selection, ties, disqualification, and not-ready behavior.

#### Done condition

Track 6D has an evidence-backed readiness or withholding decision.

### Task 8: Documentation, CI, and Independent Verification

#### Allowed files or subsystem

README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, workflow, and complete repository diff.

#### Required behavior

Document:

- candidate eligibility;

- tokenizer decisions;

- direct official ONNX findings;

- hardware and artifact-budget decisions;

- bounded subprocess compatibility;

- selection or no-selection;

- Track 6D outcome;

- residual risks;

- no-download boundary.

Update CI to validate every Track 6C schema and record.

CI must not:

- download model artifacts;

- use model hubs;

- install runtimes;

- perform conversion;

- execute inference.

Assign independent verification to a fresh agent.

#### Tests

Run every command in Verification.

#### Done condition

Candidate eligibility closure is documented, tested, CI-enforced, independently verified, and ready for Principal Architect review.

## Out of Scope

Intelligence Track 6C must not:

- install or download ONNX Runtime;

- acquire models, tokenizers, configurations, or ONNX artifacts;

- install conversion tools;

- perform conversion;

- perform inference;

- authorize quantization;

- add candidate families;

- weaken candidate criteria;

- modify corpus or gates;

- modify sibling repositories;

- modify PatchPilot;

- use tenant or production data;

- implement shadow mode;

- create production composition;

- publish a package;

- create a release;

- deploy.

## Stop Conditions

Stop and report if:

1. The spec-only commit parent differs from origin/main.

2. The working tree contains unrelated changes.

3. Track 6B is not merged.

4. The corrected adapter contract is absent.

5. A runtime or model artifact exists.

6. Mandatory evidence requires downloading artifacts.

7. Candidate eligibility depends on an unofficial conversion.

8. Tokenizer licensing is inferred rather than proven.

9. Commercial-use terms remain unclear for a proposed selected candidate.

10. Redistribution terms remain unclear when relevant.

11. Immutable revision is unavailable.

12. Required ONNX external-data inventory is unavailable.

13. Artifact footprint exceeds 8 GiB.

14. Estimated peak memory exceeds 12 GiB.

15. Bounded subprocess compatibility is unproven.

16. Candidate selection would require conversion or quantization.

17. Existing criteria or gates must be weakened.

18. A sibling repository must be inspected.

19. Work cannot fit in one PR-sized branch.

On a stop condition:

- do not select the candidate;

- do not authorize acquisition;

- do not download artifacts;

- do not weaken controls;

- record the exact blocker;

- recommend the smallest next decision.

## Verification

Pass requires:

- uv sync --frozen;

- uv run ruff format --check .;

- uv run ruff check .;

- uv run mypy src tests;

- uv run pytest;

- corpus validation;

- baseline evaluation;

- all Track 5 validations;

- all Track 6A validations;

- all Track 6B validations;

- fixture, comparison, and calibration validation;

- every Track 6C schema validation;

- every Track 6C record validation;

- candidate-eligibility tests;

- tokenizer-eligibility tests;

- official-source and immutable-revision tests;

- direct-ONNX inventory tests;

- external-data completeness tests;

- artifact-budget arithmetic tests;

- exact 8 GiB boundary tests;

- exact 12 GiB memory-boundary tests;

- bounded-subprocess compatibility tests;

- disqualification and null-score tests;

- selection and tie-break tests;

- Track 6D readiness tests;

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

- no runtime was downloaded or installed;

- no model, tokenizer, configuration, or ONNX artifact was acquired;

- no conversion occurred;

- no inference occurred;

- no candidate was selected unless every mandatory criterion passed;

- no sibling repository was accessed;

- no provider was contacted for inference;

- no privileged host changes occurred;

- no package was published;

- no release or deployment occurred;

- calibration remains not-approved;

- runtimeInstallationStatus remains not-installed;

- acquisitionStatus remains not-acquired;

- conversionStatus remains not-performed;

- executionStatus remains not-executed;

- realModelExecuted remains false;

- productionReady remains false.

Recommended Conventional Commit:

docs(evals): reassess direct ONNX candidate eligibility

Do not create the commit automatically.

## Handoff Requirements

Return one consolidated handoff containing:

1. Outcome

2. Base commit, branch, and working-tree state

3. Multi-agent execution summary

4. Track 6B baseline

5. Candidate eligibility results

6. Tokenizer eligibility results

7. Direct official ONNX findings

8. Official evidence reviewed

9. License and use-rights decisions

10. Immutable revisions

11. ONNX graph and external-data inventories

12. Artifact-budget calculations

13. Hardware-fit decisions

14. Bounded subprocess compatibility

15. Candidate scores or null scores

16. Selected candidate or continued no-selection

17. Track 6D readiness or withholding

18. Files changed

19. Dependency and lockfile impact

20. Every verification command and actual result

21. CI changes

22. Independent verification

23. Scope compliance

24. Unresolved decisions

25. Residual risks

26. Exact Track 6D recommendation

27. Proposed Conventional Commit

28. Proposed PR title and summary

29. Track 6D prerequisites

Final verdict must be exactly one of:

- TRACK 6D CONTROLLED ACQUISITION READY

- TRACK 6D CONTROLLED ACQUISITION READY WITH DOCUMENTED RESIDUALS

- TRACK 6D CONTROLLED ACQUISITION NOT READY

- BLOCKED BY UNRESOLVED AUTHORITY

Explicitly confirm:

- no runtime binary, wheel, image, or shared library was downloaded;

- no runtime was installed;

- no model, tokenizer, configuration, or ONNX artifact was acquired;

- no conversion occurred;

- no inference occurred;

- no candidate was selected unless every mandatory criterion passed;

- no sibling repository was accessed;

- no automatic commit or push occurred;

- no pull request was created automatically;

- no package was published;

- no release or deployment occurred;

- runtimeInstallationStatus remains not-installed;

- selectionOutcome remains no-selection unless fully authorized;

- acquisitionStatus remains not-acquired;

- conversionStatus remains not-performed;

- executionStatus remains not-executed;

- realModelExecuted remains false;

- productionReady remains false.

End with exactly one:

INTELLIGENCE TRACK 6C READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT

or:

INTELLIGENCE TRACK 6C BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW