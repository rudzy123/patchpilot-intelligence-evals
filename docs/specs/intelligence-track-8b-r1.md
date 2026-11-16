Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 8B-R1: Corrected Controlled Measurement Retry

## Identity

- **Repository:** `patchpilot-intelligence-evals`

- **Session ID:** Intelligence Track 8B-R1

- **Mission:** Create and execute a new controlled measurement plan using the corrected publisher-template compatibility boundary, the unchanged externally verified ONNX Runtime and LiquidAI artifacts, a fresh external result root, and the approved hardened execution profile; measure bounded FP32 memory and, only if all prerequisite phases pass, evaluate the candidate against the existing 24-case synthetic corpus.

- **Base commit:** The parent of the specification-only commit introducing this file. Before implementation, `git rev-parse HEAD^` must equal `git rev-parse origin/main`.

- **Expected repository state:** Track 8B merged as a stopped, fail-closed attempt; the prior plan marked consumed and non-reusable; template compatibility corrected; future preflight authority fields corrected; no ONNX Runtime `Run` yet completed; no candidate metrics or memory-envelope conclusions produced; Track 9 not ready; candidate selection `no-selection`; calibration `not-approved`; `productionReady` false.

- **Branch:** `feat/intelligence-track-8b-r1-measurement-retry`

- **Change type:** New controlled measurement plan, new operator checkpoint, real candidate execution, bounded FP32 memory measurement, conditional existing-corpus evaluation, immutable result records, closeout, documentation, tests, and artifact-free CI validation.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** `feat(evals): record corrected candidate measurement`

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, merge, change GitHub settings, publish, release, deploy, acquire replacement artifacts, install project dependencies, or promote the candidate automatically.

## Architectural Outcome

Track 8B-R1 must answer:

1. Does the corrected template boundary allow the exact verified publisher template to produce a valid bounded prompt?

2. Can the verified FP32 candidate complete ONNX Runtime `Run` inside the approved hardened boundary?

3. Does measured resident memory remain within the unchanged 12 GiB ceiling?

4. Can bounded generation complete without network access, process leakage, uncontrolled output, or unverified dependencies?

5. Can the candidate complete the existing 24-case synthetic evaluation?

6. What do the existing metrics and gates show?

7. Are the ten empirically unresolved explanation capabilities supported by measured evidence?

8. Is Track 9 architectural review ready?

The completed Session must:

1. Preserve the prior stopped attempt unchanged.

2. Preserve its plan as consumed and non-reusable.

3. Create a completely new measurement plan and digest.

4. Use a new empty external result root.

5. Require a new explicit operator approval before `Run`.

6. Recompute every verified runtime and candidate digest.

7. Revalidate the exact publisher-template digest.

8. Run template compatibility before model-session creation.

9. Execute phases serially.

10. Stop at the first failed prerequisite.

11. Use cgroup memory as the resident-memory authority.

12. Run 4,096 tokens before considering 8,192 tokens.

13. Run the corpus only if all memory and execution gates pass.

14. Preserve existing metrics and gates unchanged.

15. Preserve gold-label isolation.

16. Produce immutable measurement records.

17. Preserve no-winner comparison.

18. Preserve calibration as `not-approved`.

19. Preserve candidate selection as `no-selection` pending Principal Architect review.

20. Preserve `productionReady: false`.

Track 8B-R1 authorizes real inference and synthetic evaluation only after the new operator checkpoint is approved.

It does not authorize PatchPilot integration, shadow mode, production composition, release, or deployment.

## Governing Authority

Before implementation or execution, Cursor must reread:

- every repository `AGENTS.md`;

- `README.md`;

- `SECURITY.md`;

- `CONTRIBUTING.md`;

- `NOTICE`;

- `LICENSE`;

- `.gitignore`;

- `pyproject.toml`;

- `uv.lock`;

- every protected workflow;

- Repository Hardening 1 governance;

- every architecture, provenance, operations, and authorization document;

- every current schema;

- candidate protocol and subprocess boundary;

- immutable result storage;

- comparison and calibration behavior;

- promotion gates;

- Track 6A hardened execution profile;

- Track 6B corrected ONNX adapter;

- Track 7 finalist and selection records;

- Track 7A storage and promotion records;

- Track 7B memory and suitability records;

- Track 8A acquisition, artifact identity, load proof, closeout, and review records;

- Track 8B measurement plan, stopped attempt, template defect, closeout, Track 9 readiness, and implementation-review records;

- current corpus and metric definitions;

- current CLI commands and tests;

- Intelligence Track 2 through Track 8B specifications;

- synchronized protected-CI evidence from `main`.

Do not inspect or modify `patchpilot` or `neural-from-scratch`.

Do not perform new candidate, runtime, or artifact research.

## Authorized External Identities

Track 8B-R1 must load exact identities from committed records.

### Runtime

- ONNX Runtime version: `v1.31.1`

- Archive SHA-256: `c849e36a1ef3e22d4ff217b9d1ce4a3cf5b9467b975610913ae959ad5b16bdc9`

- Verified runtime library: `libonnxruntime.so.1.31.1`

- Verified runtime attempt: `rp-c2fe1c88f694fc1e`

- Verified runtime payload: `29,684,645` bytes

- External verified root supplied by the operator and never committed

### Candidate

- Candidate: `LiquidAI/LFM2.5-1.2B-Instruct`

- Source revision: `b9d816ab510f9a28dca37cb182e9da8b0226e13c`

- ONNX revision: `10f72e70abf67ac0fd7ebf15bc5854726891d864`

- Precision: FP32

- Verified candidate attempt: `cd-20b7ceee37a62cba`

- Verified candidate files: 11

- Verified logical payload: `4,717,588,977` bytes

- External verified root supplied by the operator and never committed

### Publisher template

- Verified template digest:

  `f05bf4b967dc993bdc7a2fe6e43759ee218eb0eb340d68b063e1c4f8ad148176`

- Synthetic compatibility fixture content:

  `synthetic-user`

- Expected synthetic rendered-output digest:

  `5c61ee0b595fa4c5b295feb233b312c38b779f7840f3f39c82aef51da9061e5d`

Every promoted digest and the template digest must match before any execution.

## Prior Attempt Authority

The prior Track 8B attempt remains immutable:

- Plan digest:

  `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2`

- Plan disposition: `consumed`

- Reusable: `false`

- Replacement digest in prior record: `not-issued`

- Stop cause: `tokenizer-failure`

- Failure authority: measurement infrastructure

- `runInvoked: false`

- `modelSessionCreated: false`

- `realModelExecuted: false`

- Candidate metrics: not produced

- Track 9 readiness: not ready

Track 8B-R1 must not overwrite, mutate, reuse, reinterpret, or append results to that attempt.

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

Track 8B-R1 must not:

- download or replace the runtime;

- download or replace candidate files;

- retrieve missing files automatically;

- contact a model hub for fallback;

- acquire another tokenizer or template;

- change immutable revisions;

- install a project runtime dependency;

- convert or quantize;

- append an unverified execution provider.

If an artifact is missing or changed, stop and return to acquisition authority.

### New plan required

Track 8B-R1 must create a new plan identity.

The plan must include:

- exact artifact identities;

- corrected compatibility-boundary identity;

- hardened-profile identity;

- result-root class;

- phase ordering;

- prompts;

- token counts;

- decoding settings;

- memory limits;

- timeouts;

- output limits;

- repetition rules;

- stop conditions;

- cleanup behavior;

- frozen authority fields.

The plan digest must be generated through the authoritative repository function.

The prior digest must be rejected.

### Fresh result root required

The retry must use a new external result root that:

- does not exist or is empty before execution;

- is distinct from the stopped-attempt result root;

- is outside Git and sibling repositories;

- is not a symlink;

- has appropriate owner-only permissions;

- is on a suitable filesystem;

- has sufficient free capacity;

- refuses overwrite.

No previous measurement record may be modified.

### Operator checkpoint before `Run`

Before the first ONNX Runtime `Run`, Cursor must present:

- new plan digest;

- prior-plan rejection result;

- recomputed artifact digests;

- publisher-template digest result;

- synthetic template-compatibility result;

- new empty result-root validation;

- hardened-profile identity;

- execution commands;

- memory limits;

- decoding configuration;

- phase inputs;

- timeouts;

- output limits;

- phase gates;

- stop conditions;

- cleanup rules.

The human operator must explicitly approve the new plan digest.

No prior approval may be reused.

### Template compatibility precedes model loading

Before model-session creation, the implementation must:

1. verify the exact publisher-template digest;

2. evaluate only the supported template subset;

3. render the bounded synthetic fixture;

4. validate the rendered-prompt shape;

5. compare the rendered-output digest;

6. reject unsupported constructs;

7. create no model session;

8. invoke no `Run`.

A compatibility failure stops the Session before model loading.

The implementation must not:

- require the literal `messages | length`;

- rewrite the publisher template;

- normalize its bytes;

- substitute a handwritten template;

- retrieve another template.

### Hardened execution is mandatory

Every real execution must use:

- `linux-bwrap-systemd-v1`;

- OS-level network denial;

- verified runtime root mounted read-only;

- verified candidate root mounted read-only;

- private writable result directory;

- minimal environment;

- no home, SSH, cloud, sibling, gold, or prior-result visibility;

- direct argument vectors;

- no shell;

- cgroup `MemoryMax`;

- `MemorySwapMax=0`;

- `TasksMax`;

- separate `RLIMIT_AS`;

- CPU and wall-clock limits;

- stdout and stderr limits;

- process-tree cleanup.

No plain-subprocess fallback is allowed.

### Frozen authority fields

Every new preflight and phase record must carry the repository’s exact vocabulary for:

- `selectionOutcome: no-selection`;

- `calibrationStatus: not-approved`;

- `productionReady: false`;

- `measurementPerformed`;

- `measurementCompleted`;

- `runInvoked`;

- `modelSessionCreated`;

- `realModelExecuted`.

The fields must accurately reflect each phase.

### Phase ordering

Execute only in this order:

1. no-Run preflight;

2. template compatibility;

3. one-token smoke;

4. bounded short generation;

5. 4,096-token measurement;

6. conditional 8,192-token measurement;

7. conditional 24-case evaluation;

8. summaries, closeout, and Track 9 readiness.

No later phase may run after a failed, unresolved, missing, or incomplete prerequisite.

### Phase 1: one-token smoke

Use:

- prompt: `Reply with one token.`

- maximum new tokens: 1

- greedy argmax

- temperature: 0

- top-p: 1

- top-k: 1

- repetition penalty: 1

- seed support: false

- recorded seed: 0, unused

- wall timeout: 900 seconds

- CPU timeout: 600 seconds

- generation budget: 60 seconds

- stdout limit: 8,192 bytes

- stderr limit: 262,144 bytes

Record exact input, output, output digest, token counts, cold-load timing, first-token timing, total timing, memory telemetry, network result, isolation result, and cleanup result.

### Phase 2: bounded short generation

Use:

- prompt: `Reply with the single word ready.`

- maximum new tokens: 32

- cold and warm generation in one process

- generation budget: 120 seconds

- wall timeout: 900 seconds

- CPU timeout: 600 seconds

- stdout limit: 8,192 bytes

- stderr limit: 262,144 bytes

- identical decoding settings to Phase 1

Record cold and warm results separately.

### Phase 3: 4,096-token measurement

Use:

- batch size: 1

- token ID: 574 repeated exactly 4,096 times

- maximum new tokens: 1

- one cold invocation

- one warm invocation

- generation budget: 300 seconds

- wall timeout: 900 seconds

- CPU timeout: 600 seconds

- stdout limit: 8,192 bytes

- stderr limit: 262,144 bytes

The exact token count must be recorded and validated.

### Phase 4: conditional 8,192-token measurement

Run only if Phase 3 passes every gate.

Use:

- batch size: 1

- token ID: 574 repeated exactly 8,192 times

- maximum new tokens: 1

- generation budget: 600 seconds

- otherwise preserve the approved limits and decoding policy

### Phase 5: conditional corpus evaluation

Run only if Phases 1 through 4 all pass.

Use:

- existing 24 cases;

- three repetitions per case;

- prompt-template digest:

  `62774d0f8b65c959c5b038911af4293d3d774aae3933f0d7a24064691685250a`;

- generation budget: 15 seconds after session creation;

- wall timeout: 900 seconds;

- CPU timeout: 600 seconds;

- stdout limit: 65,536 bytes;

- stderr limit: 16,384 bytes;

- zero retries;

- identical decoding configuration within the experiment.

The candidate must not see gold records, labels, expected citations, prior outputs, prior scores, hidden metadata, or cross-case evaluator controls.

### Memory authority

The authoritative resident-memory ceiling remains:

`12,884,901,888` bytes.

Use:

- cgroup `MemoryMax`: `12,884,901,888`;

- `MemorySwapMax`: `0`;

- `TasksMax`: `32`;

- `RLIMIT_AS`: `25,769,803,776`;

- memory sampling interval: `100 ms`;

- intra-op threads: `8`;

- inter-op threads: `1`.

Record separately:

- `memory.current`;

- `memory.peak`;

- `memory.events`;

- process RSS;

- process-tree RSS;

- virtual size;

- load time;

- first-token time;

- generation time.

Do not represent `RLIMIT_AS` as resident memory.

Missing or contradictory cgroup telemetry is a blocking failure.

### Memory stop behavior

Stop the current and every later phase when:

- cgroup OOM occurs;

- cgroup peak exceeds `12,884,901,888`;

- `memory.peak` is unavailable;

- telemetry is contradictory;

- the candidate escapes the cgroup;

- isolation fails;

- network denial fails;

- output limits are exceeded;

- process cleanup fails;

- an unverified dependency is required;

- an artifact identity changes.

An OOM or limit termination is a valid measured failure.

Do not raise the ceiling or change precision.

### Behavioral evaluation

The corpus remains exactly:

- 6 grounding and citation cases;

- 4 insufficient-evidence and refusal cases;

- 4 prompt-injection cases;

- 4 cross-tenant negative controls;

- 3 contradiction cases;

- 3 stale, unavailable, or incomparable-evidence cases.

Use existing metrics, gates, schemas, and evaluator authority unchanged.

### Empirical capabilities

Measure:

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

Do not infer a pass merely because execution succeeds.

### Immutable records

Every new record must include:

- retry Session ID;

- new plan digest;

- prior plan reference;

- runtime identity;

- candidate identity;

- artifact digests;

- template digest;

- compatibility-output digest;

- hardened-profile identity;

- result-root class without local path;

- phase;

- input identity;

- token count;

- decoding settings;

- memory limits;

- observed memory;

- timings;

- output digest;

- exit classification;

- network result;

- cleanup result;

- repository commit;

- timestamp;

- frozen authority fields;

- `productionReady: false`.

Records must be overwrite-protected.

### No automatic selection or promotion

Even if every phase passes:

- `selectionOutcome` remains `no-selection`;

- calibration remains `not-approved`;

- `productionReady` remains false;

- no PatchPilot integration is authorized.

Principal Architect review is required.

## Assumed Repository State

Before implementation, Cursor must prove:

- repository root is `patchpilot-intelligence-evals`;

- local `main` equals `origin/main`;

- Track 8B is merged;

- specification-only commit parent equals `origin/main`;

- working tree is clean after the specification commit;

- protected checks pass on synchronized `main`;

- Track 8B stopped-attempt identities validate;

- prior plan disposition is consumed and non-reusable;

- no replacement plan exists;

- corrected template compatibility is merged;

- future preflight authority fields are merged;

- Track 8A artifact identities still validate;

- verified runtime and candidate roots still exist;

- external artifacts are unchanged;

- no runtime dependency exists in `pyproject.toml` or `uv.lock`;

- candidate selection remains no-selection;

- calibration remains not approved;

- Track 9 remains not ready;

- no acquired artifact exists in Git;

- no sibling repository is nested in the Git tree;

- `realModelExecuted` remains false;

- `productionReady` remains false.

If any assumption is false, stop.

## Allowed Change Surface

Permitted:

- `docs/specs/intelligence-track-8b-r1.md`;

- corrected retry architecture;

- new measurement-plan and operator-approval records;

- new preflight, compatibility, smoke, memory, behavioral, closeout, and readiness schemas or schema revisions where required;

- redacted immutable retry records;

- source modules for plan generation, compatibility validation, inference, cgroup observation, phased execution, corpus evaluation, closeout, and readiness;

- a new external result root;

- focused tests;

- manually invoked execution commands;

- Repository Contracts updates;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, and governance documentation;

- `.gitignore` for local measurement metadata.

Not permitted:

- new artifact acquisition;

- replacement artifact transfer;

- project runtime installation;

- template replacement;

- conversion or quantization;

- changing limits, corpus, metrics, or gates;

- candidate selection;

- PatchPilot integration;

- shadow mode;

- GitHub setting changes;

- publication;

- release;

- deployment.

## Required Repository Additions

The repository must include the conceptual equivalent of:

```text

docs/

├── architecture/

│   └── [corrected-controlled-measurement.md](http://corrected-controlled-measurement.md)

├── operations/

│   ├── [corrected-measurement-runbook.md](http://corrected-measurement-runbook.md)

│   └── [corrected-measurement-recovery.md](http://corrected-measurement-recovery.md)

├── provenance/

│   └── [track8b-r1-measurement-evidence.md](http://track8b-r1-measurement-evidence.md)

└── specs/

	└── [intelligence-track-8b-r1.md](http://intelligence-track-8b-r1.md)

schemas/

├── measurement-retry-plan.schema.json

├── measurement-retry-approval.schema.json

├── measurement-retry-preflight.schema.json

├── template-compatibility-result.schema.json

├── retry-smoke-execution.schema.json

├── retry-context-memory.schema.json

├── retry-behavioral-run.schema.json

├── retry-closeout.schema.json

└── retry-track9-readiness.schema.json

candidates/

├── authorization/

│   ├── measurement-retry-plan.json

│   ├── measurement-retry-approval.json

│   └── retry-track9-readiness.json

└── templates/

	├── measurement-retry-preflight-template.json

	├── template-compatibility-result-template.json

	├── retry-smoke-execution-template.json

	├── retry-context-memory-template.json

	├── retry-behavioral-run-template.json

	└── retry-closeout-template.json

src/patchpilot_intelligence_evals/

├── measurement_retry_[plan.py](http://plan.py)

├── measurement_retry_[preflight.py](http://preflight.py)

├── template_[compatibility.py](http://compatibility.py)

├── corrected_candidate_[inference.py](http://inference.py)

├── corrected_context_[measurement.py](http://measurement.py)

├── corrected_behavioral_[measurement.py](http://measurement.py)

├── measurement_retry_[closeout.py](http://closeout.py)

└── retry_track9_[readiness.py](http://readiness.py)

tests/

├── test_measurement_retry_[plan.py](http://plan.py)

├── test_measurement_retry_[preflight.py](http://preflight.py)

├── test_template_[compatibility.py](http://compatibility.py)

├── test_corrected_candidate_[inference.py](http://inference.py)

├── test_corrected_context_[measurement.py](http://measurement.py)

├── test_corrected_behavioral_[measurement.py](http://measurement.py)

├── test_measurement_retry_[closeout.py](http://closeout.py)

└── test_retry_track9_[readiness.py](http://readiness.py)

```

Exact paths may differ only to follow repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and records for:

1. retry measurement plan;

2. retry operator approval;

3. retry preflight;

4. template compatibility;

5. smoke execution;

6. short generation;

7. 4,096-token memory measurement;

8. 8,192-token memory measurement;

9. behavioral runs and summary;

10. retry closeout;

11. Track 9 readiness.

Every schema must:

- have a stable ID and version;

- use `additionalProperties: false`;

- identify the retry Session;

- reference the consumed prior plan;

- identify exact artifact and template digests;

- distinguish compatibility from inference;

- distinguish plan approval from execution;

- distinguish RSS, cgroup memory, and virtual size;

- represent phase prerequisites and stop causes;

- prohibit absolute external paths;

- prohibit secrets or machine identity;

- preserve `productionReady: false`;

- preserve no-selection pending review.

## Multi-Agent Execution Model

Cursor Plan is the parent retry-measurement orchestrator.

Use Grok 4.7 Extra High for:

- execution authority;

- plan identity;

- template compatibility;

- inference correctness;

- memory-boundary decisions;

- experimental design;

- result interpretation;

- readiness decisions;

- conflict resolution;

- independent verification.

Delegate work to:

### Agent 1: Retry authority specialist

Owns prior-plan rejection, new plan, operator checkpoint, frozen authority, and phase gates.

### Agent 2: Template and tokenizer specialist

Owns exact template identity, supported subset, rendering, prompt shape, tokenization, and no-session compatibility proof.

### Agent 3: Memory instrumentation specialist

Owns cgroup telemetry, RSS, timing, sampling, cold/warm separation, and memory-stop behavior.

### Agent 4: Inference and context specialist

Owns model session, smoke, short generation, 4,096-token, and conditional 8,192-token phases.

### Agent 5: Behavioral specialist

Owns 24-case evaluation, repetitions, result validation, metrics, gates, and empirical capabilities.

### Agent 6: Closeout and readiness specialist

Owns immutable summaries, calibration interpretation, cleanup, Track 9 readiness, and preserved no-selection.

### Agent 7: Independent verifier

Runs after execution and must not own planning, compatibility, inference, memory measurement, behavioral evaluation, or closeout.

### Coordination Rules

The parent must:

- finish implementation and synthetic verification first;

- produce a new plan digest;

- stop for operator approval;

- execute phases serially;

- stop on the first blocking result;

- preserve all immutable records;

- integrate centrally;

- commission a fresh verifier.

## Ordered Execution Plan

### Task 1: Verify Track 8B Baseline

#### Allowed files or subsystem

Read-only Git state, Track 8A and Track 8B records, external roots, digests, workflows, tests, and protected authority.

#### Required behavior

Confirm all assumed state, prior-plan consumption, corrected template boundary, and exact artifact identities.

#### Tests

Run all relevant existing validators and recompute promoted digests.

#### Done condition

The baseline is proven and no new `Run` occurred.

### Task 2: Implement New Retry Plan and Operator Checkpoint

#### Allowed files or subsystem

Schemas, plan, approval record, validators, CLI, runbooks, and tests.

#### Required behavior

Create a new plan with a new digest and fresh result-root class.

Reject the old plan.

Include every phase, limit, prompt, token count, decoding setting, timeout, output limit, stop condition, cleanup rule, and frozen authority field.

Stop before `Run`.

#### Tests

Validate uniqueness, old-plan rejection, phase order, empty result-root requirements, and operator approval binding.

#### Done condition

A new immutable plan awaits operator approval.

### Task 3: Execute Compatibility, Smoke, and Short Generation

#### Allowed files or subsystem

Verified roots, compatibility boundary, hardened launcher, inference adapter, new external result root.

#### Required behavior

After operator approval:

1. run template compatibility with no model session;

2. run one-token smoke;

3. run bounded short generation;

4. record all memory, timing, output, isolation, network, and cleanup evidence;

5. stop on any failure.

#### Tests

All synthetic compatibility and inference tests must pass first.

#### Done condition

Minimum real execution passes or the Session stops.

### Task 4: Execute Memory Measurements

#### Allowed files or subsystem

Verified roots, cgroup observer, tokenizer, inference adapter, hardened launcher, result records.

#### Required behavior

Run 4,096 tokens first.

Run 8,192 tokens only if every 4,096-token gate passes.

Record precise token counts, cold and warm results, memory telemetry, timing, and stop classification.

#### Tests

Validate token construction and cgroup telemetry before real execution.

#### Done condition

Both contexts have results or a fail-closed stop result.

### Task 5: Execute Conditional 24-Case Evaluation

#### Allowed files or subsystem

Approved corpus inputs, candidate protocol, hardened execution, immutable result root.

#### Required behavior

Run only after every prior phase passes.

Use three repetitions and existing protocol, metrics, gates, limits, and prompt template.

Hide all gold and evaluator data.

#### Tests

Validate each result before scoring.

#### Done condition

The corpus is complete or the Session stops structurally.

### Task 6: Evaluate and Summarize

#### Allowed files or subsystem

Immutable results, evaluator, metrics, comparison, capability summary, calibration interpretation.

#### Required behavior

Apply existing metrics and gates unchanged.

Produce no winner.

Keep calibration not approved.

Do not select the candidate.

#### Tests

Validate all summaries and identities.

#### Done condition

Results are complete and decision-grade.

### Task 7: Close Retry and Decide Track 9 Readiness

#### Allowed files or subsystem

Closeout, failed attempts, result retention, cleanup, Track 9 readiness.

#### Required behavior

Record every phase outcome, memory and behavioral conclusion, cleanup, residual, and blocker.

Track 9 readiness remains advisory pending Principal Architect review.

#### Tests

Validate ready and not-ready states.

#### Done condition

The retry is durably closed.

### Task 8: Documentation, CI, and Independent Verification

#### Allowed files or subsystem

Redacted records, documentation, Repository Contracts, complete diff, and external result evidence.

#### Required behavior

CI remains inference-free and artifact-free.

A fresh verifier must inspect plan identity, prior-plan rejection, template compatibility, phase order, memory records, behavioral results, metrics, cleanup, immutable identities, and unchanged authority.

#### Tests

Run every Verification command.

#### Done condition

Track 8B-R1 is ready for Principal Architect review.

## Out of Scope

Track 8B-R1 must not:

- acquire or replace artifacts;

- modify the external stopped-attempt root;

- install a project runtime dependency;

- replace the publisher template;

- convert or quantize;

- change ceilings, corpus, metrics, gates, or calibration;

- select the candidate;

- integrate with PatchPilot;

- use production or tenant data;

- change GitHub settings;

- publish, release, or deploy.

## Stop Conditions

Stop if:

1. The specification parent differs from `origin/main`.

2. Working tree contains unrelated changes.

3. Track 8B is not merged.

4. Prior plan is not consumed.

5. A replacement plan already exists unexpectedly.

6. Artifact or template digest differs.

7. External verified root is absent.

8. New result root is not empty.

9. Operator approval is absent or mismatched.

10. Template compatibility fails.

11. Model loading requires an unverified dependency.

12. Cgroup telemetry is unavailable.

13. Memory exceeds 12 GiB.

14. OOM occurs.

15. Network or isolation fails.

16. Output exceeds limits.

17. Process cleanup fails.

18. Gold data is visible.

19. A phase prerequisite fails.

20. Existing metrics or gates must change.

21. A sibling repository must be accessed.

22. Work cannot fit in one PR-sized branch.

## Verification

Pass requires:

- frozen dependency sync;

- Ruff format and lint;

- strict mypy;

- complete pytest;

- all merged validators;

- every retry schema and record validator;

- prior-plan rejection tests;

- retry-plan identity tests;

- operator-approval tests;

- template-compatibility tests;

- no-session compatibility tests;

- cgroup-memory tests;

- exact token-count tests;

- phase-order tests;

- smoke and short-generation validation;

- context-memory validation;

- candidate-result validation;

- corpus evaluation validation;

- metric and summary validation;

- closeout validation;

- Track 9 readiness validation;

- workflow-policy validation;

- dependency-policy validation;

- prohibited-artifact scan;

- dependency and lockfile check;

- documentation checks;

- `git diff --check`;

- `git status --short --branch`.

Also confirm:

- no new artifact was acquired;

- no project runtime dependency was added;

- prior plan remains consumed;

- old external result root remains unchanged;

- no conversion or quantization occurred;

- only approved phases ran;

- no production or tenant data was used;

- candidate selection remains `no-selection`;

- calibration remains `not-approved`;

- `productionReady` remains false.

## Handoff Requirements

Return:

1. Outcome

2. Base commit and branch

3. Prior-plan rejection

4. New plan and digest

5. Operator checkpoint

6. Exact artifact and template identities

7. Recomputed digests

8. Compatibility result

9. Smoke result

10. Short-generation result

11. 4,096-token result

12. 8,192-token result or withholding

13. Cgroup and RSS measurements

14. Timing results

15. Phase failures

16. Corpus results

17. Repetition consistency

18. Metric and gate outcomes

19. Ten empirical capability outcomes

20. Comparison and calibration interpretation

21. Retry closeout

22. Track 9 readiness

23. Files changed

24. External result files

25. Dependency impact

26. Complete verification

27. Independent verification

28. Scope compliance

29. Residual risks

30. Recommendation

31. Proposed commit and PR

32. Post-merge steps

Final verdict must be exactly one of:

- `TRACK 9 EVALUATION REVIEW READY`

- `TRACK 9 EVALUATION REVIEW READY WITH DOCUMENTED RESIDUALS`

- `TRACK 9 EVALUATION REVIEW NOT READY`

- `BLOCKED BY UNRESOLVED AUTHORITY`

Explicitly confirm:

- no new acquisition;

- no project runtime installation;

- no template replacement;

- no conversion or quantization;

- no candidate selection;

- no PatchPilot integration;

- no automatic Git action;

- no GitHub setting change;

- no publication, release, or deployment;

- calibration remains `not-approved`;

- `productionReady` remains false.

End with exactly one:

`INTELLIGENCE TRACK 8B-R1 READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT`

or:

`INTELLIGENCE TRACK 8B-R1 BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW`