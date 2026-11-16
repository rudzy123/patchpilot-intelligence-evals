Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 8B-R2: Hardened Inference Execution Retry

## Identity

- **Repository:** `patchpilot-intelligence-evals`

- **Session ID:** Intelligence Track 8B-R2

- **Mission:** Perform one final bounded inference retry using the unchanged verified runtime and candidate artifacts, the merged authoritative runtime dependency closure, a new in-sandbox dynamic-link precheck, a new measurement-plan digest, a fresh external result root, and a new operator checkpoint; proceed serially through smoke execution, bounded generation, context-memory measurement, and the existing 24-case evaluation only while every prerequisite passes.

- **Base commit:** The parent of the specification-only commit introducing this file. Before implementation, `git rev-parse HEAD^` must equal `git rev-parse origin/main`.

- **Expected repository state:** Track 8B-R1 merged as a stopped, fail-closed infrastructure attempt; its plan consumed and non-reusable; shared runtime dependency closure merged; vacuous memory-pass defect corrected; no successful ONNX Runtime `Run`; no candidate memory or behavioral conclusion; candidate selection `no-selection`; calibration `not-approved`; Track 9 `not-ready`; `productionReady` false.

- **Branch:** `feat/intelligence-track-8b-r2-inference-retry`

- **Change type:** Final bounded inference retry, exact-sandbox dependency validation, new plan and operator checkpoint, phased memory measurement, conditional corpus evaluation, immutable records, closeout, documentation, tests, and artifact-free CI enforcement.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** `feat(evals): record hardened inference measurement`

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, merge, change GitHub settings, publish, release, deploy, acquire or replace artifacts, install project dependencies, or promote the candidate automatically.

## Architectural Outcome

Track 8B-R2 must answer:

1. Can the exact hardened measurement sandbox load the complete approved runtime dependency closure before model-session creation?

2. Can the verified ONNX Runtime create a session and invoke `Run` with the verified FP32 candidate?

3. Does measured resident memory remain within the unchanged 12 GiB ceiling?

4. Can bounded generation complete without network access, dependency escape, process leakage, or uncontrolled output?

5. Can the candidate complete the existing 24-case synthetic evaluation?

6. What do the existing metrics and gates show?

7. Are the ten empirically unresolved explanation capabilities supported by observed evidence?

8. Is Track 9 evaluation review ready?

The completed Session must:

1. Preserve both prior stopped attempts unchanged.

2. Preserve both prior plan digests as consumed and non-reusable.

3. Preserve all Track 8A artifacts unchanged.

4. Use the merged authoritative runtime dependency closure.

5. Add an exact-sandbox dynamic-link precheck before model-session creation.

6. Create a new plan and digest.

7. Use a fresh external result root.

8. Require explicit operator approval before the first `Run`.

9. Execute every phase serially.

10. Stop on the first failed or unresolved prerequisite.

11. Use cgroup memory as resident-memory authority.

12. Run 4,096 tokens before considering 8,192 tokens.

13. Run the corpus only if smoke, bounded generation, and both context phases pass.

14. Apply existing metrics and gates unchanged.

15. Preserve gold-label isolation.

16. Produce immutable records.

17. Preserve no-winner comparison.

18. Preserve calibration as `not-approved`.

19. Preserve candidate selection as `no-selection` pending Principal Architect review.

20. Preserve `productionReady: false`.

This is the final pre-Track-9 infrastructure retry currently authorized in principle.

If Track 8B-R2 stops because of another independent measurement-infrastructure defect, the next architectural review must determine whether continuing the custom inference path remains proportionate. Another retry must not be assumed automatically.

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

- Track 8A acquisition, load-proof, closeout, and review records;

- Track 8B stopped attempt, template correction, closeout, and review records;

- Track 8B-R1 stopped attempt, dependency-mount correction, memory-conclusion correction, closeout, and review records;

- current corpus and metric definitions;

- current CLI commands and tests;

- Intelligence Track 2 through Track 8B-R1 specifications;

- synchronized protected-CI evidence from `main`.

Do not inspect or modify `patchpilot` or `neural-from-scratch`.

Do not perform new model, runtime, or candidate research.

## Authorized External Identities

Track 8B-R2 must load exact identities from committed authority.

### Runtime

- ONNX Runtime version: `v1.31.1`

- Archive SHA-256: `c849e36a1ef3e22d4ff217b9d1ce4a3cf5b9467b975610913ae959ad5b16bdc9`

- Verified runtime library: `libonnxruntime.so.1.31.1`

- Verified runtime-library SHA-256: `a96f132e5eb5ca04e23a7d2fc1078fb95aa591e8d71d0f237702ece3a1e0f4ea`

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

- Verified tokenizer SHA-256: `0a1f2cb9fc2769030ca1f4207e81c1af493319373d41b8d3cf5be53860c13760`

- External verified root supplied by the operator and never committed

### Publisher template

- Verified template SHA-256:

  `f05bf4b967dc993bdc7a2fe6e43759ee218eb0eb340d68b063e1c4f8ad148176`

- Synthetic fixture content: `synthetic-user`

- Expected rendered-output SHA-256:

  `5c61ee0b595fa4c5b295feb233b312c38b779f7840f3f39c82aef51da9061e5d`

Every promoted artifact digest and template identity must match before execution.

## Prior Attempt Authority

### Track 8B

- Plan digest:

  `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2`

- Disposition: `consumed`

- Reusable: false

- Outcome: stopped before session creation

- `runInvoked: false`

### Track 8B-R1

- Plan digest:

  `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b`

- Disposition: `consumed`

- Reusable: false

- Replacement digest: `not-issued`

- Outcome: stopped with `inference-failure`

- Failure authority: measurement infrastructure

- `runInvoked: false`

- `modelSessionCreated: false`

- Memory conclusion: `unavailable`

- Behavioral conclusion: `unavailable`

Track 8B-R2 must not overwrite, append to, reuse, or reinterpret either historical result root.

## Invariants

### Deterministic PatchPilot authority

Candidate output remains advisory evaluation data and must never become authoritative over:

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

- review state;

- Finding lifecycle;

- remediation completion;

- PatchPilot audit state.

### No new acquisition or artifact mutation

Track 8B-R2 must not:

- download or replace the runtime;

- download or replace candidate files;

- retrieve missing files automatically;

- contact a model hub for fallback;

- replace the tokenizer or publisher template;

- change immutable revisions;

- modify verified artifact bytes;

- install a project runtime dependency;

- convert or quantize;

- append an unverified execution provider.

If an expected artifact is absent or changed, stop.

### New plan and result root required

Track 8B-R2 must create:

- a new measurement plan;

- a new plan digest;

- a new approval record;

- a fresh empty external result root;

- a new execution identity.

The new plan must reference both consumed prior plans.

The result root must:

- be outside Git and sibling repositories;

- be distinct from both historical roots;

- be empty or newly created;

- be mode `0700`;

- reject symlink use;

- have adequate capacity;

- refuse overwrite.

### Operator checkpoint before `Run`

Before the first `Run`, Cursor must present:

- both prior-plan rejection results;

- new plan digest;

- recomputed artifact digests;

- exact template digest;

- synthetic compatibility result;

- authoritative dependency-closure result;

- exact-sandbox dynamic-link precheck result;

- fresh result-root validation;

- execution commands;

- prompts and token counts;

- decoding configuration;

- cgroup and resource limits;

- timeouts and output limits;

- phase gates;

- cleanup and stop rules.

The human operator must approve the new digest explicitly.

### Authoritative runtime dependency closure

Track 8A load proof and Track 8B-R2 must use the same repository-owned dependency-closure implementation.

The closure may include only:

- verified `libonnxruntime.so.1.31.1`;

- approved standard system dependencies;

- the approved ELF interpreter through hardened-execution policy.

The closure must reject:

- unresolved dependencies;

- unapproved provider libraries;

- `libonnxruntime_providers_shared.so`;

- broad host `/lib` or `/usr/lib` mounts;

- writable sources;

- symlink escape;

- transport-attempt files;

- quarantine paths;

- repository paths;

- project virtual environments;

- home-directory paths;

- network fallback.

Dependencies must be mounted individually and read-only.

Committed records may contain basenames, classifications, and non-sensitive identities, but not absolute host paths.

### Exact-sandbox dynamic-link precheck

Before model-session creation, the exact measurement sandbox must:

1. use the same Bubblewrap and systemd scope configuration intended for inference;

2. use the same minimal environment;

3. mount the verified runtime root read-only;

4. mount the approved dependency closure individually and read-only;

5. preserve OS-level network denial;

6. call a bounded child that loads the verified runtime library;

7. resolve required exported symbols;

8. report loaded dependency basenames and identities;

9. confirm no provider library is loaded;

10. confirm no unexpected file is opened from outside approved mounts;

11. close the runtime library;

12. exit without creating a model session;

13. invoke no `Run`;

14. generate a sealed precheck record.

If the precheck fails, stop before operator-approved inference.

The precheck must run before the operator checkpoint unless the implementation requires `Run` authority for an operation. Loading the runtime library and resolving symbols without model-session creation is permitted for preflight.

### Template compatibility

Before model-session creation:

1. verify the publisher-template digest;

2. evaluate only the supported subset;

3. render the bounded synthetic fixture;

4. validate prompt shape;

5. compare the rendered-output digest;

6. reject unsupported constructs;

7. create no model session;

8. call no `Run`.

Do not rewrite or replace the template.

### Hardened execution

Every real execution must use:

- `linux-bwrap-systemd-v1`;

- OS-level network denial;

- verified runtime and candidate roots mounted read-only;

- approved dependency mounts only;

- private writable result directory;

- minimal environment;

- no home, SSH, cloud, sibling, gold, or prior-result visibility;

- direct argument vectors;

- no shell;

- cgroup `MemoryMax`;

- `MemorySwapMax=0`;

- `TasksMax=32`;

- separate `RLIMIT_AS`;

- CPU and wall-clock limits;

- stdout and stderr limits;

- complete process-tree cleanup.

No plain-subprocess fallback is permitted.

### Frozen authority fields

Every record must represent accurately:

- `selectionOutcome: no-selection`;

- `calibrationStatus: not-approved`;

- `productionReady: false`;

- `measurementAttempted`;

- `measurementCompleted`;

- `runInvoked`;

- `modelSessionCreated`;

- `realModelExecuted`.

### Phase ordering

Execute in this order:

1. no-Run preflight;

2. publisher-template compatibility;

3. exact-sandbox dynamic-link precheck;

4. operator checkpoint;

5. one-token smoke;

6. bounded short generation;

7. 4,096-token memory measurement;

8. conditional 8,192-token memory measurement;

9. conditional 24-case evaluation;

10. summaries, closeout, and Track 9 readiness.

No later phase may run when a prerequisite is failed, unresolved, missing, or incomplete.

### Smoke phase

Use:

- prompt: `Reply with one token.`

- maximum new tokens: 1

- greedy argmax;

- temperature 0;

- top-p 1;

- top-k 1;

- repetition penalty 1;

- seed unsupported;

- recorded seed 0, unused;

- EOS token ID 7;

- generation budget 60 seconds;

- wall timeout 900 seconds;

- CPU timeout 600 seconds;

- stdout limit 8,192 bytes;

- stderr limit 262,144 bytes.

### Short-generation phase

Use:

- prompt: `Reply with the single word ready.`

- maximum new tokens: 32;

- cold and warm windows in one process;

- generation budget 120 seconds;

- wall timeout 900 seconds;

- CPU timeout 600 seconds;

- stdout limit 8,192 bytes;

- stderr limit 262,144 bytes;

- same decoding configuration as smoke.

### 4,096-token phase

Use:

- batch size 1;

- token ID 574 repeated exactly 4,096 times;

- maximum new tokens 1;

- one cold invocation;

- one warm invocation;

- generation budget 300 seconds;

- wall timeout 900 seconds;

- CPU timeout 600 seconds;

- stdout limit 8,192 bytes;

- stderr limit 262,144 bytes.

### Conditional 8,192-token phase

Run only after the complete 4,096-token gate passes.

Use:

- batch size 1;

- token ID 574 repeated exactly 8,192 times;

- maximum new tokens 1;

- generation budget 600 seconds;

- otherwise unchanged controls.

### Conditional corpus evaluation

Run only after smoke, short generation, 4,096 tokens, and 8,192 tokens all pass.

Use:

- existing 24 cases;

- three repetitions per case;

- zero retries;

- prompt-template digest:

  `62774d0f8b65c959c5b038911af4293d3d774aae3933f0d7a24064691685250a`;

- maximum new tokens 256;

- generation budget 15 seconds after session creation;

- wall timeout 900 seconds;

- CPU timeout 600 seconds;

- stdout limit 65,536 bytes;

- stderr limit 16,384 bytes;

- consistent approved decoding settings.

Gold claims, expected citations, labels, prior outputs, prior scores, hidden metadata, and evaluator controls must remain invisible to the candidate.

### Memory authority

Use:

- cgroup `MemoryMax`: `12,884,901,888`;

- `MemorySwapMax`: `0`;

- `TasksMax`: `32`;

- `RLIMIT_AS`: `25,769,803,776`;

- sampling interval: `100 ms`;

- intra-op threads: `8`;

- inter-op threads: `1`.

Record separately:

- `memory.current`;

- `memory.peak`;

- `memory.events`;

- process RSS;

- process-tree RSS;

- virtual size;

- session-creation time;

- first-token time;

- generation time.

Do not represent `RLIMIT_AS` as resident memory.

### Memory conclusion

`within-ceiling` requires:

- both required context phases present;

- completed count equals required count;

- both phases succeeded;

- complete, noncontradictory cgroup telemetry;

- both peaks at or below `12,884,901,888`;

- no OOM;

- successful isolation;

- successful cleanup.

Otherwise use:

- `unavailable` when required phases did not run;

- `unresolved` for missing or contradictory telemetry;

- `exceeds-ceiling` for a completed phase above the ceiling;

- measured failure for OOM or limit termination.

Smoke-only memory must not establish context-memory eligibility.

### Behavioral evaluation

Apply existing metrics and gates unchanged.

Measure the ten unresolved capabilities:

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

Do not infer a pass merely from successful execution.

### Immutable records

Each record must include:

- Track 8B-R2 Session ID;

- new plan digest;

- both prior-plan references;

- runtime and candidate identities;

- artifact digests;

- template and compatibility digests;

- dependency-closure identity;

- dynamic-link precheck identity;

- hardened-profile identity;

- result-root class without absolute path;

- phase;

- phase prerequisites;

- input identity;

- token count;

- decoding configuration;

- resource limits;

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

### No automatic selection

Even if all phases pass:

- candidate selection remains `no-selection`;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false;

- no PatchPilot integration is authorized.

Principal Architect review remains mandatory.

## Assumed Repository State

Before implementation, Cursor must prove:

- repository root is `patchpilot-intelligence-evals`;

- local `main` equals `origin/main`;

- Track 8B-R1 is merged;

- specification-only commit parent equals `origin/main`;

- working tree is clean after the specification commit;

- protected checks pass on synchronized `main`;

- both prior plans validate as consumed and non-reusable;

- no replacement plan exists;

- template compatibility correction is merged;

- authoritative dependency closure is merged;

- corrected memory-conclusion logic is merged;

- Track 8A artifact identities validate;

- verified external roots exist and remain unchanged;

- no runtime dependency exists in `pyproject.toml` or `uv.lock`;

- candidate selection remains no-selection;

- calibration remains not approved;

- Track 9 remains not ready;

- no acquired artifact exists in Git;

- no sibling repository is nested in the Git tree;

- `productionReady` remains false.

If any assumption is false, stop.

## Allowed Change Surface

Permitted:

- `docs/specs/intelligence-track-8b-r2.md`;

- R2 architecture;

- new measurement-plan and approval records;

- dynamic-link precheck schemas and records;

- new preflight, smoke, context, behavioral, closeout, and Track 9 records;

- source modules for plan generation, dependency precheck, inference, memory observation, phased execution, evaluation, closeout, and readiness;

- new external result root;

- focused tests;

- manually invoked execution commands;

- Repository Contracts updates;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, and governance documentation;

- `.gitignore` for local measurement metadata.

Not permitted:

- new artifact acquisition;

- artifact replacement;

- historical-result mutation;

- project runtime installation;

- template replacement;

- conversion or quantization;

- limit, corpus, metric, or gate changes;

- candidate selection;

- PatchPilot integration;

- GitHub setting changes;

- publication;

- release;

- deployment.

## Required Repository Additions

The repository must include the conceptual equivalent of:

```text

docs/

├── architecture/

│   └── [hardened-inference-retry.md](http://hardened-inference-retry.md)

├── operations/

│   ├── [inference-retry-runbook.md](http://inference-retry-runbook.md)

│   └── [inference-retry-recovery.md](http://inference-retry-recovery.md)

├── provenance/

│   └── [track8b-r2-measurement-evidence.md](http://track8b-r2-measurement-evidence.md)

└── specs/

	└── [intelligence-track-8b-r2.md](http://intelligence-track-8b-r2.md)

schemas/

├── inference-retry-plan.schema.json

├── inference-retry-approval.schema.json

├── inference-retry-preflight.schema.json

├── dynamic-link-precheck.schema.json

├── inference-retry-smoke.schema.json

├── inference-retry-context-memory.schema.json

├── inference-retry-behavioral-run.schema.json

├── inference-retry-closeout.schema.json

└── inference-retry-track9-readiness.schema.json

candidates/

├── authorization/

│   ├── inference-retry-plan.json

│   ├── inference-retry-approval.json

│   └── inference-retry-track9-readiness.json

└── templates/

	├── inference-retry-preflight-template.json

	├── dynamic-link-precheck-template.json

	├── inference-retry-smoke-template.json

	├── inference-retry-context-memory-template.json

	├── inference-retry-behavioral-run-template.json

	└── inference-retry-closeout-template.json

src/patchpilot_intelligence_evals/

├── inference_retry_[plan.py](http://plan.py)

├── dynamic_link_[precheck.py](http://precheck.py)

├── hardened_candidate_[inference.py](http://inference.py)

├── inference_context_[measurement.py](http://measurement.py)

├── inference_behavioral_[measurement.py](http://measurement.py)

├── inference_retry_[closeout.py](http://closeout.py)

└── inference_retry_[track9.py](http://track9.py)

tests/

├── test_inference_retry_[plan.py](http://plan.py)

├── test_dynamic_link_[precheck.py](http://precheck.py)

├── test_hardened_candidate_[inference.py](http://inference.py)

├── test_inference_context_[measurement.py](http://measurement.py)

├── test_inference_behavioral_[measurement.py](http://measurement.py)

├── test_inference_retry_[closeout.py](http://closeout.py)

└── test_inference_retry_[track9.py](http://track9.py)

```

Exact paths may differ only to follow repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and records for:

1. new inference-retry plan;

2. operator approval;

3. preflight;

4. publisher-template compatibility;

5. dynamic-link precheck;

6. smoke execution;

7. short generation;

8. 4,096-token measurement;

9. 8,192-token measurement;

10. behavioral runs and summary;

11. closeout;

12. Track 9 readiness.

Every schema must:

- have a stable ID and version;

- use `additionalProperties: false`;

- reference both consumed prior plans;

- identify exact artifact and template digests;

- distinguish precheck, session creation, and `Run`;

- distinguish RSS, cgroup memory, and virtual size;

- represent phase prerequisites and stop causes;

- prohibit absolute external paths;

- prohibit secrets and host identity;

- preserve `productionReady: false`;

- preserve candidate no-selection pending review.

## Multi-Agent Execution Model

Cursor Plan is the parent Track 8B-R2 orchestrator.

Use Grok 4.7 Extra High for:

- execution authority;

- dependency-closure safety;

- sandbox-precheck design;

- inference correctness;

- memory-boundary decisions;

- experimental design;

- result interpretation;

- proportionality decision;

- Track 9 readiness;

- independent verification.

Delegate bounded work to:

### Agent 1: Retry authority specialist

Owns prior-plan rejection, new plan, approval, frozen authority, result-root policy, and phase gates.

### Agent 2: Dynamic-link and sandbox specialist

Owns dependency closure, exact-sandbox precheck, read-only mounts, symbol validation, no-session proof, and closure identity.

### Agent 3: Memory specialist

Owns cgroup telemetry, RSS, sampling, timings, cold and warm separation, and fail-closed memory conclusions.

### Agent 4: Inference specialist

Owns template use, tokenization, model session, smoke, short generation, 4,096-token, and conditional 8,192-token phases.

### Agent 5: Behavioral specialist

Owns 24-case execution, repetitions, result validation, metrics, gates, and empirical capabilities.

### Agent 6: Closeout and proportionality specialist

Owns summaries, no-winner comparison, calibration interpretation, cleanup, Track 9 readiness, and any recommendation to stop further retries.

### Agent 7: Independent verifier

Runs after execution and must not own planning, precheck, inference, measurement, evaluation, or closeout.

### Coordination Rules

The parent must:

- finish implementation and synthetic verification first;

- generate a new plan digest;

- validate both prior plans as consumed;

- run the exact-sandbox no-session precheck;

- stop for operator approval;

- execute phases serially;

- stop on the first blocking result;

- preserve immutable records;

- integrate centrally;

- commission a fresh verifier.

## Ordered Execution Plan

### Task 1: Verify Track 8B-R1 Baseline

#### Allowed files or subsystem

Read-only Git state, committed records, verified external roots, historical result roots, workflows, tests, and authority.

#### Required behavior

Confirm all assumed state, prior-plan dispositions, artifact identities, template identity, dependency closure, and corrected memory logic.

#### Tests

Run relevant validators and recompute promoted digests.

#### Done condition

The baseline is proven and no new `Run` occurred.

### Task 2: Implement New Plan, Result-Root Policy, and Operator Checkpoint

#### Allowed files or subsystem

Schemas, plan, approval, CLI, runbooks, validators, and tests.

#### Required behavior

Generate a new plan and digest, reject both prior plans, require a fresh empty result root, and bind all approved phases and limits.

Stop before `Run`.

#### Tests

Validate uniqueness, old-plan rejection, result-root isolation, phase order, and approval binding.

#### Done condition

A new immutable plan awaits approval.

### Task 3: Implement Exact-Sandbox Dynamic-Link Precheck

#### Allowed files or subsystem

Authoritative dependency closure, hardened launcher, precheck child, schemas, records, CLI, documentation, and tests.

#### Required behavior

Inside the exact measurement sandbox:

- mount the verified runtime and approved closure;

- preserve network denial;

- load the runtime library;

- resolve required exported symbols;

- record non-sensitive dependency identities;

- verify no provider library;

- close the library;

- exit without model-session creation or `Run`.

#### Tests

Prove accepted closure, rejected dependencies, read-only mounts, no broad directory mounts, no session creation, and no `Run`.

#### Done condition

The exact sandbox is proven capable of loading the runtime composition.

### Task 4: Execute Compatibility, Smoke, and Short Generation

#### Allowed files or subsystem

Verified roots, hardened launcher, inference adapter, fresh result root.

#### Required behavior

After operator approval:

1. reconfirm template compatibility;

2. run one-token smoke;

3. run bounded short generation;

4. record memory, timing, output, network, isolation, and cleanup evidence;

5. stop on any failure.

#### Tests

All synthetic inference tests must pass first.

#### Done condition

Minimum inference passes or the Session stops.

### Task 5: Execute Context-Memory Measurements

#### Allowed files or subsystem

Verified roots, tokenizer, inference adapter, cgroup observer, hardened launcher, result records.

#### Required behavior

Run 4,096 tokens first.

Run 8,192 tokens only after the 4,096-token phase passes every gate.

Record exact token counts, cold and warm results, telemetry, timings, and classification.

#### Tests

Validate token construction and cgroup telemetry first.

#### Done condition

Both contexts have results or a structured stop outcome.

### Task 6: Execute Conditional 24-Case Evaluation

#### Allowed files or subsystem

Approved corpus input, candidate protocol, hardened execution, immutable result root.

#### Required behavior

Run only after all prior phases pass.

Use three repetitions, zero retries, existing protocol, existing prompt digest, metrics, gates, and limits.

Hide gold and evaluator data.

#### Tests

Validate results before scoring.

#### Done condition

The corpus completes or stops structurally.

### Task 7: Evaluate, Close, and Decide Track 9 Readiness

#### Allowed files or subsystem

Immutable results, evaluator, comparison, calibration interpretation, closeout, cleanup, Track 9 readiness.

#### Required behavior

Apply existing metrics and gates unchanged.

Produce no winner.

Keep calibration not approved.

Do not select the candidate.

If another independent infrastructure defect blocks execution, make an explicit proportionality recommendation about whether further retry investment is justified.

#### Tests

Validate all outcomes and readiness states.

#### Done condition

The attempt is durably closed.

### Task 8: Documentation, CI, and Independent Verification

#### Allowed files or subsystem

Redacted records, documentation, Repository Contracts, complete diff, external evidence.

#### Required behavior

CI remains inference-free and artifact-free.

A fresh verifier must inspect plan identity, prior-plan rejection, dependency closure, precheck, phase order, telemetry, results, calculations, cleanup, external evidence, and unchanged authority.

#### Tests

Run every command in Verification.

#### Done condition

Track 8B-R2 is ready for Principal Architect review.

## Out of Scope

Track 8B-R2 must not:

- acquire or replace artifacts;

- modify historical result roots;

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

1. Specification parent differs from `origin/main`.

2. Working tree contains unrelated changes.

3. Track 8B-R1 is not merged.

4. Either prior plan is reusable or not consumed.

5. Artifact or template digest differs.

6. Verified external root is absent.

7. Fresh result root is not empty.

8. Dependency closure differs unexpectedly.

9. Dynamic-link precheck fails.

10. Operator approval is absent or mismatched.

11. Model loading requires an unverified dependency.

12. Cgroup telemetry is unavailable.

13. Memory exceeds 12 GiB.

14. OOM occurs.

15. Network or isolation fails.

16. Output exceeds limits.

17. Process cleanup fails.

18. Gold data is visible.

19. A prerequisite phase fails.

20. Existing metrics or gates must change.

21. A sibling repository must be accessed.

22. Work cannot fit in one PR-sized branch.

## Verification

Pass requires:

- frozen dependency sync;

- Ruff format and lint;

- strict mypy;

- complete pytest suite;

- every merged validator;

- every R2 schema and record validator;

- prior-plan rejection tests;

- new-plan identity tests;

- result-root isolation tests;

- operator-approval tests;

- dependency-closure tests;

- dynamic-link precheck tests;

- no-session and no-Run precheck tests;

- template-compatibility tests;

- cgroup-memory tests;

- exact token-count tests;

- phase-order tests;

- smoke and short-generation validation;

- context-memory validation;

- corpus-result validation;

- metric and gate validation;

- fail-closed memory-conclusion tests;

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

- no new artifact acquisition;

- no project runtime dependency;

- both prior plans remain consumed;

- historical result roots remain unchanged;

- no conversion or quantization;

- only approved phases ran;

- no production or tenant data;

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

6. Artifact and template identities

7. Dependency-closure result

8. Dynamic-link precheck

9. Compatibility result

10. Smoke result

11. Short-generation result

12. 4,096-token result

13. 8,192-token result or withholding

14. Cgroup and RSS measurements

15. Timings

16. Phase failures

17. Corpus results

18. Repetition consistency

19. Metrics and gates

20. Ten empirical capability outcomes

21. Comparison and calibration interpretation

22. Closeout

23. Track 9 readiness

24. Proportionality recommendation if infrastructure blocks again

25. Files changed

26. External result files

27. Dependency impact

28. Complete verification

29. Independent verification

30. Scope compliance

31. Residual risks

32. Proposed commit and PR

33. Post-merge steps

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

`INTELLIGENCE TRACK 8B-R2 READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT`

or:

`INTELLIGENCE TRACK 8B-R2 BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW`