Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 8B: Controlled FP32 Memory and Behavioral Measurement

## Identity

- **Repository:** patchpilot-intelligence-evals

- **Session ID:** Intelligence Track 8B

- **Mission:** Execute the verified LiquidAI finalist through the verified ONNX Runtime inside the approved hardened boundary, measure cold-load and generation-time memory at bounded context sizes, and evaluate the candidate against the existing 24-case synthetic corpus without changing deterministic PatchPilot authority, promotion gates, or production readiness.

- **Base commit:** The parent of the specification-only commit introducing this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.

- **Expected repository state:** Intelligence Track 8A merged; runtime and candidate artifacts externally acquired, verified, sealed, and atomically promoted; hardened offline loading passed; inference, generation, behavioral evaluation, and long-context measurement not yet performed; candidate selection remains no-selection; calibration remains not-approved; productionReady remains false.

- **Branch:** feat/intelligence-track-8b-controlled-measurement

- **Change type:** Controlled external-artifact measurement, ONNX Runtime execution, memory and timing instrumentation, immutable evaluation records, existing-corpus evaluation, documentation, tests, and CI validation that remains artifact-free.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** feat(evals): record controlled candidate measurement

- **Automatic Git actions:** Cursor must not commit, push, open a pull request, merge, alter GitHub settings, publish, release, deploy, or promote the candidate automatically.

## Architectural Outcome

Track 8B must answer:

1. Can the verified FP32 candidate execute inside the approved hardened boundary?

2. Does measured process memory remain within the 12 GiB ceiling?

3. Can bounded generation complete without network access, process leaks, or uncontrolled output?

4. How does the candidate perform on the existing 24-case synthetic corpus?

5. Do the ten empirically unresolved explanation capabilities pass the existing evaluation contracts?

6. Is further evaluation justified, or must the candidate remain disqualified?

The completed Session must:

1. Preserve exact Track 8A runtime and candidate identities.

2. Recompute promoted artifact digests before execution.

3. Require a new explicit operator checkpoint before the first Run call.

4. Start with a minimal one-token smoke execution.

5. Measure cold-load and warm-run behavior separately.

6. Measure bounded memory at 4,096 tokens.

7. Attempt 8,192 tokens only after the 4,096-token gate passes.

8. Enforce the 12 GiB cgroup memory ceiling.

9. Preserve operating-system network denial.

10. Preserve process-tree cleanup.

11. Use deterministic decoding where supported.

12. Run the existing 24-case corpus only after memory and smoke gates pass.

13. Use existing metrics and promotion gates without change.

14. Store immutable measurement and evaluation records.

15. Repeat cases according to the approved consistency policy.

16. Distinguish execution failure from evaluation failure.

17. Preserve no-winner comparison behavior.

18. Preserve calibration as not-approved.

19. Preserve candidate selection as no-selection pending Principal Architect review.

20. Preserve productionReady: false.

Track 8B authorizes measurement and synthetic evaluation only after its operator checkpoint is approved.

It does not authorize PatchPilot integration, shadow mode, production composition, or promotion.

## Governing Authority

Before implementation or execution, Cursor must reread:

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

- every architecture, provenance, operations, and authorization document;

- every current schema;

- candidate protocol and runner;

- immutable result storage;

- comparison and calibration behavior;

- promotion gates;

- Track 6A hardened execution profile;

- Track 6B corrected ONNX adapter;

- Track 7 finalist, suitability, and selection records;

- Track 7A storage and atomic-promotion records;

- Track 7B memory, suitability, and measurement-authorization records;

- Track 8A acquisition, digest, promotion, load-proof, closeout, prerequisite, and implementation-review records;

- current corpus and metric definitions;

- existing CLI commands and tests;

- Intelligence Track 2 through Track 8A specifications;

- protected post-merge evidence from synchronized main.

Do not inspect or modify patchpilot or neural-from-scratch.

Do not perform new public candidate research during Track 8B.

## Authorized External Identities

Track 8B must load exact identities from committed Track 8A records.

### Runtime

- ONNX Runtime version: v1.31.1

- Archive SHA-256: c849e36a1ef3e22d4ff217b9d1ce4a3cf5b9467b975610913ae959ad5b16bdc9

- Verified runtime library: [libonnxruntime.so](http://libonnxruntime.so).1.31.1

- Promoted runtime payload: 29,684,645 bytes

- External verified root: supplied by the operator and never committed

### Candidate

- Candidate: LiquidAI/LFM2.5-1.2B-Instruct

- Source revision: b9d816ab510f9a28dca37cb182e9da8b0226e13c

- ONNX revision: 10f72e70abf67ac0fd7ebf15bc5854726891d864

- Precision: FP32

- Verified files: 11

- Verified logical payload: 4,717,588,977 bytes

- External verified root: supplied by the operator and never committed

Every promoted file digest must match the committed Track 8A evidence before execution.

Any mismatch is a stop condition.

## Invariants

### Deterministic PatchPilot authority

The candidate remains advisory evaluation infrastructure.

Candidate output must never become authoritative over:

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

- Finding lifecycle;

- remediation completion;

- PatchPilot audit state.

### No new acquisition

Track 8B must not:

- download another runtime;

- download another candidate;

- download replacement files;

- change immutable revisions;

- use a model hub for fallback;

- install a project dependency;

- acquire quantized artifacts;

- perform conversion;

- retrieve missing files automatically.

If a required external artifact is absent or changed, stop and return to acquisition authority.

### Operator checkpoint before Run

Before the first ONNX Runtime Run invocation, Cursor must present:

- runtime and candidate identity results;

- recomputed digest results;

- external verified-root validation;

- hardened profile identity;

- proposed measurement commands;

- proposed memory and timeout limits;

- proposed decoding settings;

- output limits;

- smoke-test request;

- 4,096-token measurement request;

- conditional 8,192-token request;

- proposed corpus-evaluation plan;

- cleanup and stop rules.

The human operator must explicitly authorize the measurement phase.

Track 7B’s architectural authorization does not replace this checkpoint.

### Hardened execution is mandatory

Every execution must use:

- linux-bwrap-systemd-v1;

- OS-level network isolation;

- verified runtime root mounted read-only;

- verified candidate root mounted read-only;

- private writable result directory;

- minimal environment;

- no home-directory visibility;

- no SSH or cloud credentials;

- no corpus-gold visibility from the candidate;

- no prior-result visibility;

- no sibling-repository visibility;

- direct argument vectors;

- no shell;

- cgroup memory and task limits;

- Linux resource limits;

- wall-clock timeout;

- stdout and stderr limits;

- complete process-tree cleanup.

No plain-subprocess fallback is permitted.

### Execution phases

Track 8B must execute in this order:

1. **Preflight**

   - no Run;

   - recompute digests;

   - validate roots, identity, network boundary, and available output space.

2. **One-token smoke execution**

   - one minimal authorized request;

   - maximum one generated token or equivalent minimal graph execution;

   - validates that Run is operational;

   - records first-execution memory and timing.

3. **Bounded short generation**

   - small prompt;

   - maximum 32 generated tokens;

   - validates tokenizer, autoregressive loop, schema handling, and cleanup.

4. **4,096-token memory measurement**

   - batch size 1;

   - controlled synthetic tokenized input;

   - bounded output;

   - cold and warm observations;

   - memory gate must pass.

5. **8,192-token memory measurement**

   - permitted only if the 4,096-token phase passes;

   - same measurement discipline;

   - stop on memory or timing failure.

6. **24-case corpus evaluation**

   - permitted only if prior phases pass;

   - uses approved candidate protocol;

   - no gold-label visibility;

   - immutable result root;

   - existing metrics and gates.

7. **Comparison and calibration interpretation**

   - no winner selected;

   - calibration remains not-approved unless separately authorized later.

A later phase may not run after a failed prerequisite phase.

### Memory ceiling

The authoritative process-memory ceiling remains:

12,884,901,888 bytes.

The hardened execution profile must use cgroup MemoryMax as the primary resident-memory boundary.

Record separately:

- process RSS;

- process-tree RSS where available;

- cgroup current memory;

- cgroup peak memory;

- virtual address space where observable;

- runtime-reported allocator data where available;

- load time;

- first-token time;

- total generation time.

Do not substitute RLIMIT_AS for resident-memory measurement.

If cgroup peak memory cannot be observed reliably, the relevant measurement is unresolved.

### Memory stop behavior

Stop the current and all later phases when:

- cgroup OOM occurs;

- measured peak exceeds 12 GiB;

- process termination becomes unreliable;

- memory telemetry is incomplete or contradictory;

- the candidate process escapes the cgroup;

- cleanup leaves a descendant;

- output limits are exceeded;

- the hardened launcher fails.

An OOM or limit kill is a valid measured failure, not a reason to raise the ceiling.

### Context measurements

The 4,096-token and 8,192-token tests must define:

- exact token count;

- tokenizer identity;

- prompt construction;

- batch size 1;

- output-token allowance;

- decoding settings;

- cold or warm state;

- repetition count;

- timeout;

- memory collection interval;

- startup and cleanup boundaries.

Do not represent character count as token count.

### Decoding policy

Use the most deterministic supported settings.

The execution record must state:

- seed support;

- temperature;

- top-p;

- top-k;

- repetition penalty;

- maximum generated tokens;

- stop-token handling;

- tokenizer chat-template identity.

If exact deterministic replay is unsupported, record that fact and use the approved consistency policy.

### Behavioral evaluation

The corpus remains exactly 24 cases:

- 6 grounding and citation;

- 4 insufficient-evidence and refusal;

- 4 prompt-injection;

- 4 cross-tenant negative controls;

- 3 contradiction;

- 3 stale, unavailable, or incomparable-evidence.

The candidate may receive only authorized case inputs.

The candidate must not receive:

- gold claims;

- expected citations;

- labels;

- evaluator decisions;

- prior outputs;

- prior scores;

- cross-case controls;

- hidden case metadata.

### Empirical suitability capabilities

Track 8B must measure the ten unresolved capabilities:

- bounded generation;

- deterministic-fact separation;

- evidence-ID reproduction;

- missing-evidence reporting;

- uncertainty expression;

- unsupported-request refusal;

- embedded-instruction resistance;

- state-mutation avoidance;

- cross-tenant nondisclosure;

- schema compatibility.

The four capabilities supported in principle remain:

- instruction following;

- structured output;

- English language;

- context capacity.

Track 8B may measure those four but must not treat their prior evidence status as a guaranteed pass.

### Repetition policy

Use at least three repetitions per case when seed control and deterministic replay are meaningful.

If the runtime cannot provide meaningful seed control:

- record the limitation;

- preserve the first immutable run;

- run the approved alternate consistency measure;

- do not change existing promotion gates.

The same prompt template and decoding configuration must be used for every repetition within the experiment.

### Output and failure boundaries

Preserve existing protocol limits for:

- canonical input;

- stdout;

- stderr;

- response schema;

- timeout;

- immutable result identity;

- overwrite refusal.

Add candidate-specific limits only when stricter than the existing contract.

Classify failures separately:

- runtime startup failure;

- model load failure;

- tokenizer failure;

- inference failure;

- timeout;

- OOM;

- malformed response;

- schema failure;

- excessive output;

- nonzero exit;

- isolation failure;

- network violation;

- cleanup failure;

- evaluator failure.

### Immutable measurement records

Each phase must create a closed record containing:

- experiment ID;

- runtime identity;

- candidate identity;

- artifact digests;

- hardened-profile identity;

- host capability class without identity-bearing values;

- context length;

- decoding configuration;

- memory limits;

- observed memory;

- timing;

- exit classification;

- output digest;

- process-cleanup result;

- network result;

- repository commit;

- timestamp;

- productionReady: false.

Behavioral records must remain immutable and overwrite-protected.

### No automatic selection or promotion

Even if all technical and behavioral gates pass:

- candidate selection remains no-selection;

- calibration remains not-approved;

- productionReady remains false;

- no PatchPilot integration is authorized.

Principal Architect review is required after measurement.

### Repository contents

No runtime or candidate artifact may enter Git.

The repository may commit only:

- schemas;

- templates;

- redacted immutable measurement records;

- artifact digests;

- non-sensitive memory and timing measurements;

- evaluation results;

- comparison and calibration records;

- implementation code;

- tests;

- documentation.

Do not commit absolute external-cache paths or machine identity.

## Assumed Repository State

Before implementation, Cursor must prove:

- repository root is patchpilot-intelligence-evals;

- local main equals origin/main;

- Track 8A is merged;

- specification-only commit parent equals origin/main;

- working tree is clean after the specification commit;

- protected checks pass on synchronized main;

- pyproject.toml and uv.lock remain unchanged by runtime staging;

- Track 8A review digest matches committed authority;

- runtime and candidate acquisition evidence validates;

- Track 8B prerequisites are ready-with-documented-residuals;

- Track 8B measurement authorization remains not-authorized;

- external verified runtime and candidate roots still exist;

- every promoted digest still matches;

- no execution dependency exists outside the verified runtime root;

- hardened offline-load proof remains valid;

- candidate selection remains no-selection;

- calibration remains not approved;

- measurementPerformed remains false;

- no runtime or model artifact exists in Git;

- no sibling repository is nested in the Git tree;

- productionReady remains false.

If any material assumption is false, stop.

## Allowed Change Surface

Permitted:

- docs/specs/[intelligence-track-8b.md](http://intelligence-track-8b.md);

- measurement and evaluation architecture;

- measurement plans and operator checkpoints;

- memory-observation, execution, corpus-result, comparison, calibration-interpretation, and closeout schemas;

- redacted measurement records;

- source modules for measurement planning, cgroup observation, execution phases, deterministic generation, candidate adapter execution, result validation, corpus evaluation, and closeout;

- external immutable result generation;

- bounded tests using deterministic fixtures;

- manually invoked measurement commands;

- Repository Contracts updates;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, and governance documentation;

- .gitignore for local external measurement metadata where necessary.

Not permitted:

- new artifact acquisition;

- replacement artifact transfer;

- project runtime dependency;

- conversion or quantization;

- changing memory or artifact ceilings;

- changing the corpus;

- changing metrics or gates;

- candidate selection;

- PatchPilot integration;

- shadow mode;

- GitHub setting changes;

- package publication;

- release;

- deployment.

## Required Repository Additions

The repository must include the conceptual equivalent of:

text</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">docs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── architecture/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [controlled-candidate-measurement.md](http://controlled-candidate-measurement.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [fp32-memory-measurement.md](http://fp32-memory-measurement.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [behavioral-evaluation-execution.md](http://behavioral-evaluation-execution.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [track9-promotion-boundary.md](http://track9-promotion-boundary.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── operations/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [measurement-runbook.md](http://measurement-runbook.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [measurement-recovery.md](http://measurement-recovery.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [measurement-cleanup.md](http://measurement-cleanup.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── provenance/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [track8b-measurement-evidence.md](http://track8b-measurement-evidence.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">└── specs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── [intelligence-track-8b.md](http://intelligence-track-8b.md)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">schemas/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── measurement-plan.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── measurement-operator-approval.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── smoke-execution.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── context-memory-measurement.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── candidate-behavioral-run.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── candidate-behavioral-summary.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── measurement-closeout.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">└── track9-readiness.schema.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">candidates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── authorization/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── measurement-plan.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── measurement-operator-approval.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── track9-readiness.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── templates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── smoke-execution-template.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── context-memory-measurement-template.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── candidate-behavioral-run-template.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── candidate-behavioral-summary-template.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── measurement-closeout-template.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">└── local-records/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── ignored except for approved redacted records</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">src/patchpilot_intelligence_evals/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── measurement_[plan.py](http://plan.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── cgroup_[memory.py](http://memory.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── candidate_[inference.py](http://inference.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── context_[measurement.py](http://measurement.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── behavioral_[measurement.py](http://measurement.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── measurement_[closeout.py](http://closeout.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">└── track9_[readiness.py](http://readiness.py)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">tests/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── test_measurement_[plan.py](http://plan.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── test_cgroup_[memory.py](http://memory.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── test_candidate_[inference.py](http://inference.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── test_context_[measurement.py](http://measurement.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── test_behavioral_[measurement.py](http://measurement.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">├── test_measurement_[closeout.py](http://closeout.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">└── test_track9_[readiness.py](http://readiness.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794831600000,&quot;dataSource&quot;:0}">

Exact paths may differ only to follow repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and records for:

1. measurement plan;

2. operator approval;

3. smoke execution;

4. 4,096-token memory measurement;

5. 8,192-token memory measurement;

6. behavioral run;

7. behavioral summary;

8. measurement closeout;

9. Track 9 readiness.

Every schema must:

- have a stable ID and version;

- use additionalProperties: false;

- identify exact runtime and candidate digests;

- distinguish cold load, warm run, and generation;

- distinguish RSS, cgroup memory, and virtual address space;

- represent phase prerequisites;

- represent stop causes;

- prohibit secrets and identity-bearing host data;

- prohibit absolute cache paths in committed records;

- preserve productionReady: false;

- preserve candidate no-selection unless separately reviewed;

- distinguish measurement from promotion.

## Multi-Agent Execution Model

Cursor Plan is the parent measurement orchestrator.

Use Grok 4.7 Extra High for:

- execution authority;

- memory-boundary decisions;

- experimental design;

- failure interpretation;

- behavioral-result interpretation;

- readiness decisions;

- conflict resolution;

- independent verification.

Delegate work to:

### Agent 1: Measurement-authority specialist

Owns exact artifact identity, phase prerequisites, operator checkpoint, and stop rules.

### Agent 2: Memory-instrumentation specialist

Owns cgroup memory, RSS, timing, sample collection, cold and warm separation, and 12 GiB enforcement.

### Agent 3: Inference-adapter specialist

Owns verified runtime invocation, tokenizer use, deterministic decoding, response serialization, and no-network execution.

### Agent 4: Context-measurement specialist

Owns smoke, short generation, 4,096-token, and conditional 8,192-token phases.

### Agent 5: Behavioral-evaluation specialist

Owns the 24-case execution, repetitions, immutable results, and candidate-protocol compliance.

### Agent 6: Result and readiness specialist

Owns summaries, comparison, calibration interpretation, closeout, Track 9 readiness, and preserved no-selection.

### Agent 7: Independent verification specialist

Runs after measurement and must not own planning, execution, measurement, evaluation, or closeout.

### Coordination Rules

The parent must:

- finish implementation and synthetic tests before measurement;

- stop for operator approval before Run;

- execute phases serially;

- enforce phase gates;

- preserve immutable outputs;

- stop at the first blocking failure;

- commission a fresh verifier.

## Ordered Execution Plan

### Task 1: Verify Track 8A Baseline

#### Allowed files or subsystem

Read-only Git state, committed Track 8A evidence, external verified roots, digests, hardened profile, workflows, and tests.

#### Required behavior

Confirm exact identities, prerequisite state, artifact integrity, and external-root availability.

#### Tests

Recompute promoted digests and run existing validators.

#### Done condition

Baseline is proven and no Run has occurred.

### Task 2: Implement Measurement Plans and Operator Checkpoint

#### Allowed files or subsystem

Schemas, plans, validators, CLI, runbooks, and tests.

#### Required behavior

Define every phase, command, identity, context size, decoding setting, limit, timeout, output root, stop condition, cleanup action, and operator approval field.

Stop before execution.

#### Tests

Validate phase ordering and fail-closed plans.

#### Done condition

An immutable plan awaits operator approval.

### Task 3: Execute Smoke and Short-Generation Phases

#### Allowed files or subsystem

Verified external roots, hardened launcher, candidate adapter, external result root, and redacted records.

#### Required behavior

After explicit operator approval:

- run one-token smoke execution;

- run maximum 32-token generation;

- record memory, timing, network denial, cleanup, and output validity;

- stop on any failure.

#### Tests

Synthetic adapter tests must pass first.

#### Done condition

Minimum real inference is proven or measurement stops.

### Task 4: Measure 4,096-Token and Conditional 8,192-Token Memory

#### Allowed files or subsystem

Context generator, tokenizer, candidate adapter, cgroup observer, hardened launcher, result records.

#### Required behavior

Run 4,096-token measurement first.

Attempt 8,192 tokens only after the 4,096-token phase passes.

Record cold and warm observations where specified.

#### Tests

Validate exact token counts and memory telemetry.

#### Done condition

Both contexts have measured results or a structured stop outcome.

### Task 5: Execute the 24-Case Synthetic Corpus

#### Allowed files or subsystem

Approved corpus input, candidate protocol, hardened executions, immutable result root.

#### Required behavior

Run only after memory gates pass.

Use existing prompt, schema, timeout, output, and repetition contracts.

Never expose gold records to the candidate.

#### Tests

Validate every result before evaluation.

#### Done condition

All permitted runs are complete or a structured blocking result is recorded.

### Task 6: Evaluate Results and Produce Immutable Summaries

#### Allowed files or subsystem

Evaluator, metrics, results, comparison, calibration interpretation, summary records.

#### Required behavior

Apply existing metrics and gates unchanged.

Produce no-winner comparison.

Keep calibration not approved.

Do not select or promote the candidate.

#### Tests

Validate metric and summary identities.

#### Done condition

The result set is complete and interpretable.

### Task 7: Close Measurement and Decide Track 9 Readiness

#### Allowed files or subsystem

Closeout records, retention, failed attempts, readiness records.

#### Required behavior

Record phase outcomes, retained results, cleanup, memory conclusions, behavioral conclusions, and remaining blockers.

Track 9 may be marked ready only as a recommendation for later Principal Architect review.

#### Tests

Validate ready and not-ready scenarios.

#### Done condition

Closeout and readiness are durable.

### Task 8: Documentation, CI, and Independent Verification

#### Allowed files or subsystem

Redacted records, documentation, Repository Contracts, complete diff, and external result evidence.

#### Required behavior

CI remains artifact-free and inference-free.

A fresh verifier must recompute artifact identities, inspect measurement records, validate phase ordering, verify memory and behavioral calculations, and confirm no authority broadened.

#### Tests

Run every Verification command.

#### Done condition

Track 8B is ready for Principal Architect review.

## Out of Scope

Track 8B must not:

- acquire or replace artifacts;

- install a project runtime dependency;

- convert or quantize;

- change corpus, metrics, gates, ceilings, or calibration;

- select the candidate;

- integrate with PatchPilot;

- run production or tenant data;

- enable shadow mode;

- publish, release, or deploy.

## Stop Conditions

Stop if:

1. Specification parent differs from origin/main.

2. Working tree contains unrelated changes.

3. Track 8A is not merged.

4. Artifact digest differs.

5. External verified root is unavailable.

6. Operator approval is absent.

7. Hardened isolation or network denial fails.

8. Candidate reaches outside verified roots.

9. Required runtime dependency is missing.

10. Run requires unverified files.

11. Cgroup memory telemetry is unavailable.

12. Peak memory exceeds 12 GiB.

13. OOM occurs.

14. Process cleanup fails.

15. Output exceeds limits.

16. A phase prerequisite fails.

17. Gold data becomes visible.

18. Existing metrics or gates must change.

19. A sibling repository must be accessed.

20. Work cannot fit in one PR-sized branch.

## Verification

Pass requires:

- frozen dependency sync;

- Ruff format and lint;

- strict mypy;

- complete pytest;

- all merged validators;

- Track 8B schema and record validation;

- artifact digest revalidation;

- phase-order tests;

- operator-approval validation;

- cgroup-memory tests;

- token-count tests;

- smoke and short-generation validation;

- context-measurement validation;

- candidate-result validation;

- corpus evaluation validation;

- summary validation;

- closeout validation;

- Track 9 readiness validation;

- workflow and dependency-policy validation;

- prohibited-artifact scan;

- dependency and lockfile check;

- documentation checks;

- git diff --check;

- git status --short --branch.

Also confirm:

- no new artifact was acquired;

- no runtime dependency entered the project;

- no conversion or quantization occurred;

- only approved phases executed;

- no production or tenant data was used;

- candidate selection remains no-selection;

- calibration remains not-approved;

- productionReady remains false.

## Handoff Requirements

Return:

1. Outcome

2. Base commit and branch

3. Operator checkpoint

4. Exact runtime and candidate identities

5. Recomputed digests

6. Smoke execution

7. Short generation

8. 4,096-token measurement

9. 8,192-token measurement or withholding

10. Cgroup and RSS measurements

11. Timings

12. Phase failures

13. Corpus execution results

14. Repetition and consistency results

15. Metric results

16. Invariant-gate outcomes

17. Percentage-gate outcomes

18. Comparison

19. Calibration interpretation

20. The ten empirical capability outcomes

21. Measurement closeout

22. Track 9 readiness

23. Files changed

24. External result files

25. Dependency impact

26. Every verification command

27. Independent verification

28. Scope compliance

29. Residual risks

30. Exact next recommendation

31. Proposed commit and PR

32. Post-merge steps

Final verdict must be exactly one of:

- TRACK 9 EVALUATION REVIEW READY

- TRACK 9 EVALUATION REVIEW READY WITH DOCUMENTED RESIDUALS

- TRACK 9 EVALUATION REVIEW NOT READY

- BLOCKED BY UNRESOLVED AUTHORITY

Explicitly confirm:

- no new artifact acquisition;

- no project runtime installation;

- no conversion or quantization;

- no candidate selection;

- no PatchPilot integration;

- no automatic Git operation;

- no GitHub setting change;

- no publication, release, or deployment;

- calibration remains not-approved;

- productionReady remains false.

End with exactly one:

INTELLIGENCE TRACK 8B READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT

or:

INTELLIGENCE TRACK 8B BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW