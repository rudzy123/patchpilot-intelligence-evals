Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this specification, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 9A: Clean Corpus-Only Continuation

## Identity

- **Repository:** `patchpilot-intelligence-evals`

- **Session ID:** Intelligence Track 9A

- **Mission:** Execute one clean, complete, and comparable 24-case corpus-only evaluation of the externally verified LiquidAI finalist, retaining bounded raw candidate output and complete extraction, parsing, schema, truncation, and failure-authority evidence for every planned run.

- **Base commit:** The parent of the specification-only commit introducing this file. Before implementation, `git rev-parse HEAD^` must equal `git rev-parse origin/main`.

- **Expected repository state:** Track 9 merged; corpus-only continuation authorized in principle; current execution authority false; no future plan digest issued; no future result root created; accepted Track 8B-R2 memory evidence preserved; all previous execution plans consumed and non-reusable; candidate selection `no-selection`; calibration `not-approved`; comparison winner null; `productionReady` false.

- **Branch:** `feat/intelligence-track-9a-corpus-continuation`

- **Change type:** New corpus-only plan, operator checkpoint, bounded raw-output retention, complete 24-case execution, immutable diagnostics, evaluation summaries, candidate-disposition evidence, documentation, tests, and artifact-free CI validation.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** `feat(evals): record clean corpus evaluation`

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, merge, change GitHub settings, publish, release, deploy, acquire or replace artifacts, install project dependencies, select the candidate, or promote the candidate automatically.

## Architectural Outcome

Track 9A must answer:

1. Can the verified finalist complete all 24 existing synthetic corpus cases under the approved hardened boundary?

2. Can all three repetitions of every case be recorded under one uniform result identity?

3. Can bounded raw candidate output be retained safely for every run?

4. Can extraction, JSON parsing, response-schema validation, truncation, and output-limit behavior be attributed precisely?

5. Are failures attributable to candidate output, adapter behavior, protocol behavior, evaluator behavior, or infrastructure?

6. What do the existing metrics and gates show when applied to one complete and comparable result set?

7. What do the ten empirically unresolved capability measures show?

8. Is the evidence sufficient for a formal candidate disposition review?

The completed Session must:

1. Preserve accepted memory evidence without rerunning context measurements.

2. Preserve all historical plans and result roots unchanged.

3. Create one new corpus-only plan and digest.

4. Create one fresh empty result root.

5. Require explicit operator approval before candidate execution.

6. Use the exact verified runtime and candidate artifacts.

7. Recompute promoted artifact identities before execution.

8. Use the exact hardened execution profile.

9. Run exactly 24 cases.

10. Run exactly three repetitions per case.

11. Plan exactly 72 candidate executions.

12. Use zero automatic retries.

13. Preserve existing prompts, response schema, decoding, metrics, and gates.

14. Retain bounded raw output for every execution.

15. Record extraction, parsing, schema, truncation, and output-limit diagnostics separately.

16. Record failure authority for every failed result.

17. Hide all gold and evaluator data from the candidate.

18. Produce immutable run records and summaries.

19. Stop at the first security, identity, isolation, memory, output, or cleanup failure requiring Session termination.

20. Preserve candidate selection as `no-selection`.

21. Preserve calibration as `not-approved`.

22. Preserve comparison winner as null until Principal Architect review.

23. Preserve `productionReady: false`.

Track 9A authorizes corpus-only execution after its operator checkpoint.

It does not authorize memory remeasurement, candidate selection, PatchPilot integration, shadow mode, release, deployment, or production use.

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

- every current architecture, provenance, operations, authorization, defect, closeout, and review document;

- every current schema;

- candidate protocol and subprocess contract;

- immutable result-storage contract;

- comparison and calibration contracts;

- existing corpus, metrics, and promotion gates;

- Track 6A hardened execution profile;

- Track 6B corrected ONNX adapter;

- Track 7 finalist and no-selection records;

- Track 7A storage and promotion records;

- Track 7B memory and suitability contracts;

- Track 8A acquisition, artifact identities, load proof, and closeout;

- Track 8B, Track 8B-R1, and Track 8B-R2 plans, attempts, defects, evidence, and reviews;

- Track 9 evidence inventory, memory review, behavioral review, proportionality decision, continuation authorization, candidate disposition, and implementation review;

- current CLI commands and tests;

- Intelligence Track 2 through Track 9 specifications;

- synchronized protected-CI evidence from `main`.

Do not inspect or modify `patchpilot` or `neural-from-scratch`.

Do not perform new candidate, model, runtime, or artifact research.

## Authorized External Identities

Track 9A must derive the complete file-level identities from committed Track 8A evidence.

### Runtime

- ONNX Runtime version: `v1.31.1`

- Runtime archive SHA-256:

  `c849e36a1ef3e22d4ff217b9d1ce4a3cf5b9467b975610913ae959ad5b16bdc9`

- Verified runtime library: `libonnxruntime.so.1.31.1`

- Runtime-library SHA-256:

  `a96f132e5eb5ca04e23a7d2fc1078fb95aa591e8d71d0f237702ece3a1e0f4ea`

- Verified runtime attempt: `rp-c2fe1c88f694fc1e`

- External verified root supplied by the operator and never committed

### Candidate

- Candidate: `LiquidAI/LFM2.5-1.2B-Instruct`

- Source revision:

  `b9d816ab510f9a28dca37cb182e9da8b0226e13c`

- ONNX revision:

  `10f72e70abf67ac0fd7ebf15bc5854726891d864`

- Precision: FP32

- Verified candidate attempt: `cd-20b7ceee37a62cba`

- Verified files: 11

- Logical payload: `4,717,588,977` bytes

- Tokenizer SHA-256:

  `0a1f2cb9fc2769030ca1f4207e81c1af493319373d41b8d3cf5be53860c13760`

- External verified root supplied by the operator and never committed

### Publisher template

- Template SHA-256:

  `f05bf4b967dc993bdc7a2fe6e43759ee218eb0eb340d68b063e1c4f8ad148176`

- Synthetic compatibility-output SHA-256:

  `5c61ee0b595fa4c5b295feb233b312c38b779f7840f3f39c82aef51da9061e5d`

Every promoted artifact identity must match before execution.

## Historical Plan Authority

These plans remain consumed and non-reusable:

- Track 8B:

  `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2`

- Track 8B-R1:

  `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b`

- Track 8B-R2:

  `2133054bea8db11822cc65f6ea9c45f1ba1500f1aef67d314fbccca764155350`

Track 9A must not reuse, modify, append to, or reinterpret any historical plan or result root.

## Accepted Memory Evidence

Track 9A must not rerun memory-context phases.

The accepted measurements are:

- 4,096-token cold peak: `7,284,371,456` bytes

- 4,096-token warm peak: `8,511,131,648` bytes

- 8,192-token cold peak: `9,816,231,936` bytes

- 8,192-token warm peak: `12,271,669,248` bytes

- Resident ceiling: `12,884,901,888` bytes

- Minimum headroom: `613,232,640` bytes

- Memory conclusion: `within-ceiling-with-limited-headroom`

Track 9A must preserve:

- one candidate process at a time;

- identical thread configuration;

- the same cgroup memory ceiling;

- unchanged output limits;

- no larger contexts;

- no concurrent corpus runs.

## Invariants

### Deterministic PatchPilot authority

Candidate output remains advisory evaluation data.

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

- remediation-queue order;

- review state;

- Finding lifecycle;

- remediation completion;

- PatchPilot audit state.

### No new acquisition or artifact mutation

Track 9A must not:

- acquire or replace runtime files;

- acquire or replace model files;

- retrieve missing files automatically;

- replace tokenizer or configuration files;

- replace or rewrite the publisher template;

- change immutable revisions;

- modify verified artifacts;

- install a project runtime dependency;

- convert or quantize;

- append another execution provider.

Any identity mismatch is a stop condition.

### New corpus-only plan

Track 9A must create a new plan containing:

- exact artifact identities;

- all consumed prior-plan references;

- Track 9 continuation-authorization identity;

- corpus digest;

- prompt-template digest;

- response-schema identity;

- decoding configuration;

- hardened-profile identity;

- 24 case identities;

- three repetitions per case;

- 72 planned executions;

- raw-output retention policy;

- diagnostic policy;

- resource limits;

- phase ordering;

- stop conditions;

- cleanup behavior;

- frozen authority fields.

The plan digest must be generated through the repository’s authoritative canonical function.

### Fresh result root

The corpus continuation must use a new result root that:

- is outside Git and sibling repositories;

- differs from every historical result root;

- is empty before execution;

- is mode `0700`;

- is not a symlink;

- has sufficient capacity;

- refuses overwrite;

- contains only records for this corpus-only continuation.

### Operator checkpoint

Before the first candidate execution, Cursor must present:

- all historical-plan rejection results;

- new corpus-only plan digest;

- Track 9 continuation-authorization digest;

- recomputed runtime and candidate digests;

- template and compatibility digests;

- dependency-closure result;

- exact-sandbox dynamic-link precheck;

- fresh result-root validation;

- corpus digest;

- prompt-template digest;

- response-schema identity;

- exact 72-run inventory;

- raw-output retention parameters;

- decoding configuration;

- cgroup and resource limits;

- timeouts and output limits;

- stop and cleanup rules.

The human operator must explicitly approve the new plan digest.

### Execution scope

Track 9A may execute only:

- the existing 24 corpus cases;

- three repetitions per case;

- 72 total planned runs.

Track 9A must not run:

- smoke generation;

- short-generation qualification;

- 4,096-token memory measurement;

- 8,192-token memory measurement;

- calibration experiments;

- alternative prompts;

- additional repetitions;

- retries.

A bounded pre-execution dynamic-link check and template-compatibility check are permitted because neither invokes candidate inference.

### Hardened execution

Every candidate run must use:

- `linux-bwrap-systemd-v1`;

- OS-level network denial;

- verified runtime and candidate roots mounted read-only;

- approved individual dependency mounts;

- private writable per-run result directory;

- minimal environment;

- no home, SSH, cloud, sibling, gold, prior-result, or evaluator visibility;

- direct argument vectors;

- no shell;

- cgroup `MemoryMax=12,884,901,888`;

- `MemorySwapMax=0`;

- `TasksMax=32`;

- `RLIMIT_AS=25,769,803,776`;

- CPU and wall-clock limits;

- stdout and stderr limits;

- process-tree cleanup.

No plain-subprocess fallback is permitted.

### Candidate isolation between runs

Each run must be independent.

A candidate run must not receive:

- prior candidate outputs;

- prior raw outputs;

- prior extraction results;

- prior parser results;

- prior schema errors;

- prior scores;

- case labels;

- expected citations;

- gold claims;

- evaluator metadata;

- hidden case metadata;

- cross-case controls.

### Corpus identity

The corpus remains exactly 24 cases:

- 6 grounding and citation;

- 4 insufficient-evidence and refusal;

- 4 prompt-injection;

- 4 cross-tenant negative controls;

- 3 contradiction;

- 3 stale, unavailable, or incomparable-evidence.

The corpus content, taxonomy, and digest must remain unchanged.

### Prompt and decoding identity

Use the committed prompt-template digest:

`62774d0f8b65c959c5b038911af4293d3d774aae3933f0d7a24064691685250a`

Use the same approved decoding configuration:

- greedy argmax;

- temperature `0`;

- top-p `1`;

- top-k `1`;

- repetition penalty `1`;

- seed support false;

- recorded seed `0`, unused;

- EOS token ID `7`;

- maximum new tokens `256`;

- generation budget `15` seconds after session creation;

- wall timeout `900` seconds;

- CPU timeout `600` seconds;

- stdout limit `65,536` bytes;

- stderr limit `16,384` bytes;

- zero retries.

### Bounded raw-output retention

Every run must retain:

1. raw stdout bytes, bounded by the stdout limit;

2. raw stderr bytes, bounded by the stderr limit;

3. raw stdout SHA-256;

4. raw stderr SHA-256;

5. raw byte counts;

6. truncation status;

7. output-limit status;

8. extraction result;

9. extracted candidate-response bytes where present and within policy;

10. extracted-response digest;

11. JSON parse result;

12. parse error category and location where available;

13. response-schema validation result;

14. exact schema error categories;

15. missing required fields;

16. unexpected fields;

17. evidence-ID findings;

18. failure authority.

Raw output must:

- remain external during execution;

- be immutable after sealing;

- be inaccessible to later candidate runs;

- contain no gold or evaluator data;

- contain no absolute host paths or machine identity in committed records;

- be represented in committed evidence according to the repository’s synthetic-data retention policy.

### Failure authority

Each failed run must be classified as exactly one of:

- `candidate-output`;

- `adapter`;

- `protocol`;

- `evaluator`;

- `measurement-infrastructure`;

- `security-boundary`;

- `unresolved`.

The classification must cite the retained diagnostic evidence.

A schema failure may be attributed to `candidate-output` only when:

- raw output is retained;

- extraction behavior is known;

- JSON parsing behavior is known;

- schema errors are recorded;

- no adapter or protocol defect explains the result.

### Cgroup telemetry

Every candidate run must record:

- cgroup current memory;

- cgroup peak memory;

- cgroup events;

- process RSS where observable;

- process-tree RSS where observable;

- virtual size where observable;

- child-active and child-exited state;

- post-exit scope status;

- cleanup status.

The state-aware post-exit sampler must:

- preserve the last complete sample;

- tolerate expected post-exit scope removal only after a complete sample;

- fail unresolved when no complete sample exists;

- classify active-child scope disappearance as infrastructure failure;

- create an unclassified-launch record when child output exists but normal sealing cannot complete.

No launch may be silently omitted.

### Stop behavior

Stop the continuation and withhold all later runs on:

- artifact digest mismatch;

- template identity mismatch;

- dynamic-link precheck failure;

- unverified dependency;

- network violation;

- isolation failure;

- gold visibility;

- OOM;

- cgroup peak above the ceiling;

- missing or contradictory telemetry;

- excessive output;

- cleanup failure;

- result-root reuse;

- overwrite attempt;

- corpus identity mismatch;

- prompt identity mismatch;

- response-schema identity mismatch;

- evaluator infrastructure failure;

- inability to retain bounded raw output.

A candidate-attributed malformed response is a valid measured result and does not by itself stop the corpus, unless the existing protocol requires stopping.

### Metrics and gates

After all 72 planned runs are sealed or validly classified, apply the existing metrics and gates unchanged.

Do not:

- impute missing results;

- alter thresholds;

- add retries;

- discard failures selectively;

- change evaluator authority;

- recalibrate percentage gates;

- select a winner automatically.

### Immutable records

Every run record must include:

- Track 9A Session ID;

- plan digest;

- case ID;

- repetition;

- candidate and runtime identities;

- artifact digests;

- corpus and prompt identities;

- response-schema identity;

- decoding settings;

- resource limits;

- input digest;

- raw-output digests and lengths;

- extraction result;

- parse result;

- schema result;

- failure authority;

- memory telemetry;

- timings;

- exit classification;

- network result;

- cleanup result;

- repository commit;

- timestamp;

- frozen authority fields;

- `productionReady: false`.

Records must be overwrite-protected.

### No automatic selection

Regardless of measured results:

- `selectionOutcome` remains `no-selection`;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false;

- no PatchPilot integration is authorized.

Principal Architect review is required.

## Assumed Repository State

Before implementation, Cursor must prove:

- repository root is `patchpilot-intelligence-evals`;

- local `main` equals `origin/main`;

- Track 9 is merged;

- specification-only commit parent equals `origin/main`;

- working tree is clean after the specification commit;

- protected checks pass on synchronized `main`;

- Track 9 continuation is authorized in principle;

- current execution authority remains false;

- no future plan digest exists;

- no future result root exists;

- all three prior plans remain consumed and non-reusable;

- accepted memory evidence validates;

- Track 9 review digest validates;

- verified runtime and candidate roots remain present and unchanged;

- no project runtime dependency exists;

- no model or runtime artifact exists in Git;

- candidate selection remains no-selection;

- calibration remains not approved;

- comparison winner remains null;

- `productionReady` remains false;

- no sibling repository is nested in the Git tree.

If any assumption is false, stop.

## Allowed Change Surface

Permitted:

- `docs/specs/intelligence-track-9a.md`;

- corpus-only execution architecture;

- new plan and operator-approval records;

- raw-output-retention schemas and templates;

- run-diagnostic schemas;

- corpus run and summary schemas;

- failure-attribution records;

- metric and capability summaries;

- closeout and later review-readiness records;

- source modules for planning, preflight, raw-output capture, extraction diagnostics, parsing diagnostics, schema diagnostics, failure attribution, corpus execution, evaluation, closeout, and readiness;

- one new external result root;

- focused tests;

- manually invoked corpus-execution commands;

- Repository Contracts updates;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, and governance documentation;

- `.gitignore` for local execution metadata.

Not permitted:

- memory-context reruns;

- smoke or short-generation qualification reruns;

- new artifact acquisition;

- artifact replacement;

- historical-result mutation;

- project runtime installation;

- template replacement;

- response-schema changes;

- prompt changes;

- decoding changes;

- conversion or quantization;

- metric or gate changes;

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

│   ├── [clean-corpus-continuation.md](http://clean-corpus-continuation.md)

│   ├── [bounded-raw-output-retention.md](http://bounded-raw-output-retention.md)

│   └── [run-failure-attribution.md](http://run-failure-attribution.md)

├── operations/

│   ├── [corpus-continuation-runbook.md](http://corpus-continuation-runbook.md)

│   ├── [corpus-continuation-recovery.md](http://corpus-continuation-recovery.md)

│   └── [raw-output-retention.md](http://raw-output-retention.md)

├── provenance/

│   └── [track9a-corpus-evidence.md](http://track9a-corpus-evidence.md)

└── specs/

	└── [intelligence-track-9a.md](http://intelligence-track-9a.md)

schemas/

├── corpus-continuation-plan.schema.json

├── corpus-continuation-approval.schema.json

├── corpus-continuation-preflight.schema.json

├── bounded-raw-output.schema.json

├── run-diagnostics.schema.json

├── corpus-continuation-run.schema.json

├── corpus-continuation-summary.schema.json

├── corpus-continuation-closeout.schema.json

└── track10-readiness.schema.json

candidates/

├── authorization/

│   ├── corpus-continuation-plan.json

│   ├── corpus-continuation-approval.json

│   └── track10-readiness.json

└── templates/

	├── corpus-continuation-preflight-template.json

	├── bounded-raw-output-template.json

	├── run-diagnostics-template.json

	├── corpus-continuation-run-template.json

	├── corpus-continuation-summary-template.json

	└── corpus-continuation-closeout-template.json

src/patchpilot_intelligence_evals/

├── corpus_continuation_[plan.py](http://plan.py)

├── corpus_continuation_[preflight.py](http://preflight.py)

├── bounded_raw_[output.py](http://output.py)

├── output_[extraction.py](http://extraction.py)

├── response_[diagnostics.py](http://diagnostics.py)

├── failure_[attribution.py](http://attribution.py)

├── corpus_[continuation.py](http://continuation.py)

├── corpus_continuation_[closeout.py](http://closeout.py)

└── track10_[readiness.py](http://readiness.py)

tests/

├── test_corpus_continuation_[plan.py](http://plan.py)

├── test_corpus_continuation_[preflight.py](http://preflight.py)

├── test_bounded_raw_[output.py](http://output.py)

├── test_output_[extraction.py](http://extraction.py)

├── test_response_[diagnostics.py](http://diagnostics.py)

├── test_failure_[attribution.py](http://attribution.py)

├── test_corpus_[continuation.py](http://continuation.py)

├── test_corpus_continuation_[closeout.py](http://closeout.py)

└── test_track10_[readiness.py](http://readiness.py)

```

Exact paths may differ only to follow repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and records for:

1. corpus-continuation plan;

2. operator approval;

3. preflight;

4. bounded raw output;

5. per-run diagnostics;

6. corpus-continuation run;

7. corpus summary;

8. closeout;

9. Track 10 readiness.

Every schema must:

- have a stable ID and explicit version;

- use `additionalProperties: false`;

- reference Track 9 authorization;

- reference all consumed historical plans;

- identify exact runtime, candidate, corpus, prompt, schema, and template identities;

- distinguish raw, extracted, parsed, and validated output;

- represent truncation and output-limit behavior;

- represent failure authority;

- represent memory and cleanup evidence;

- prohibit absolute external paths;

- prohibit secrets and host identity;

- preserve `selectionOutcome: no-selection`;

- preserve `calibrationStatus: not-approved`;

- preserve `comparisonWinner: null`;

- preserve `productionReady: false`.

## Multi-Agent Execution Model

Cursor Plan is the parent corpus-continuation orchestrator.

Use Grok 4.7 Extra High for:

- execution authority;

- plan identity;

- raw-output security;

- diagnostic design;

- failure attribution;

- corpus completeness;

- metric interpretation;

- readiness;

- conflict resolution;

- independent verification.

Delegate bounded work to:

### Agent 1: Continuation-authority specialist

Owns historical-plan rejection, Track 9 authorization, new plan, result-root policy, operator checkpoint, frozen authority, and stop conditions.

### Agent 2: Raw-output specialist

Owns bounded stdout and stderr capture, immutable storage, digests, lengths, truncation, output-limit classification, and later-run isolation.

### Agent 3: Response-diagnostics specialist

Owns extraction, JSON parsing, response-schema validation, missing and unexpected fields, evidence-ID analysis, and failure-attribution inputs.

### Agent 4: Execution and telemetry specialist

Owns hardened execution, dependency closure, network denial, cgroup sampling, state-aware post-exit handling, cleanup, and unclassified-launch behavior.

### Agent 5: Corpus-evaluation specialist

Owns all 24 cases, three repetitions, run validation, metrics, gates, consistency, and the ten empirical capabilities.

### Agent 6: Closeout and readiness specialist

Owns summaries, comparison, calibration interpretation, closeout, Track 10 readiness, and preserved no-selection.

### Agent 7: Independent verifier

Runs after execution.

Must not own planning, raw-output capture, diagnostics, execution, evaluation, closeout, or readiness.

### Coordination Rules

The parent must:

- finish implementation and synthetic tests before execution;

- generate one new plan digest;

- stop for operator approval;

- execute cases serially;

- preserve three repetitions per case;

- seal every run before proceeding;

- stop on blocking security or infrastructure failures;

- preserve candidate-attributed malformed outputs as measured evidence;

- integrate centrally;

- commission a fresh independent verifier.

## Ordered Execution Plan

### Task 1: Verify the Track 9 Baseline

#### Allowed files or subsystem

Read-only Git state, Track 8A through Track 9 records, verified external roots, historical roots, workflows, tests, and authority.

#### Required behavior

Confirm all assumed state, Track 9 authorization, consumed plans, accepted memory evidence, artifact identities, and frozen authority.

#### Tests

Run existing validators and digest checks only.

#### Done condition

The baseline is proven and no candidate execution occurred.

### Task 2: Implement the Corpus-Only Plan and Operator Checkpoint

#### Allowed files or subsystem

Schemas, plan, approval record, validators, CLI, runbooks, and tests.

#### Required behavior

Create a new plan and digest binding:

- 24 cases;

- three repetitions;

- 72 run identities;

- exact artifacts;

- exact corpus and prompt;

- response schema;

- decoding;

- raw-output retention;

- diagnostics;

- resource limits;

- stop conditions;

- cleanup;

- frozen authority.

Create no operational authority until explicit approval.

#### Tests

Validate run count, identity uniqueness, phase order, old-plan rejection, result-root isolation, and approval binding.

#### Done condition

A complete corpus-only plan awaits operator approval.

### Task 3: Implement Raw-Output Retention and Diagnostics

#### Allowed files or subsystem

Raw-output schemas and templates, capture modules, extraction, parsing, validation, attribution, documentation, and tests.

#### Required behavior

Implement bounded immutable capture and complete diagnostic separation.

Ensure:

- raw output is retained before extraction;

- extraction cannot overwrite raw output;

- parsing cannot overwrite extracted output;

- schema validation cannot erase parse evidence;

- every failure has an attribution status;

- no later candidate run can see earlier output.

#### Tests

Cover valid output, malformed JSON, prose around JSON, missing fields, unexpected fields, malformed evidence IDs, truncation, excessive output, empty output, encoding failure, and infrastructure failure.

#### Done condition

Every future run can be attributed from retained evidence.

### Task 4: Implement and Validate Corpus Execution

#### Allowed files or subsystem

Verified roots, hardened launcher, candidate adapter, corpus input projection, new result root, run records.

#### Required behavior

After operator approval:

- execute 24 cases;

- execute three repetitions each;

- use zero retries;

- seal every run;

- record raw output and diagnostics;

- hide gold and evaluator data;

- stop on blocking security or infrastructure failure.

#### Tests

Synthetic execution and isolation tests must pass before real execution.

#### Done condition

All 72 runs are sealed or the continuation stops structurally.

### Task 5: Evaluate the Complete Result Set

#### Allowed files or subsystem

Sealed run records, evaluators, metrics, gates, empirical capabilities, summary records.

#### Required behavior

Only after the complete result set is available:

- validate every run;

- apply existing metrics;

- apply existing invariant and percentage gates;

- assess repetition consistency;

- assess ten empirical capabilities;

- classify failures by authority.

Do not impute missing runs.

#### Tests

Validate complete and incomplete result paths.

#### Done condition

The corpus is decision-grade or explicitly incomplete.

### Task 6: Produce Comparison and Calibration Interpretation

#### Allowed files or subsystem

Summaries, comparison, calibration interpretation, evidence records.

#### Required behavior

Produce comparison without selecting a winner.

Keep calibration `not-approved`.

Do not select the candidate.

#### Tests

Validate comparison and calibration authority.

#### Done condition

The evidence is ready for later architectural disposition.

### Task 7: Close the Continuation and Decide Track 10 Readiness

#### Allowed files or subsystem

Closeout, retained evidence, failed attempts, cleanup, Track 10 readiness.

#### Required behavior

Record:

- planned and completed runs;

- missing runs;

- failure authority;

- metric and gate results;

- memory residual;

- cleanup;

- retention;

- remaining blockers;

- Track 10 readiness.

Track 10 readiness is advisory pending Principal Architect review.

#### Tests

Validate ready, incomplete, and stopped outcomes.

#### Done condition

The continuation is durably closed.

### Task 8: Documentation, Repository Contracts, and Independent Verification

#### Allowed files or subsystem

Redacted records, documentation, workflows, tests, complete diff, and external evidence.

#### Required behavior

CI remains inference-free and artifact-free.

A fresh verifier must inspect:

- plan identity;

- Track 9 authority;

- run inventory;

- raw-output evidence;

- diagnostics;

- failure attribution;

- metrics;

- gates;

- cleanup;

- immutable external evidence;

- unchanged candidate authority.

#### Tests

Run every command in Verification.

#### Done condition

Track 9A is ready for Principal Architect review.

## Out of Scope

Track 9A must not:

- repeat memory-context measurements;

- run qualification smoke phases as evaluation evidence;

- acquire or replace artifacts;

- modify historical result roots;

- install project dependencies;

- replace the publisher template;

- change response schemas, prompts, decoding, corpus, metrics, gates, or calibration;

- convert or quantize;

- select the candidate;

- integrate with PatchPilot;

- authorize shadow mode;

- use production or tenant data;

- change GitHub settings;

- publish, release, or deploy.

## Stop Conditions

Stop if:

1. Specification parent differs from `origin/main`.

2. Working tree contains unrelated changes.

3. Track 9 is not merged.

4. Track 9 continuation authorization is absent or invalid.

5. A prior plan is reusable.

6. Artifact, template, corpus, prompt, or schema identity differs.

7. Verified external root is unavailable.

8. Fresh result root is nonempty.

9. Operator approval is absent or mismatched.

10. Dynamic-link or template precheck fails.

11. Raw-output retention cannot be guaranteed.

12. Gold or evaluator data is visible.

13. Candidate reaches a prior result.

14. Cgroup telemetry is unavailable or contradictory.

15. Memory exceeds the ceiling.

16. OOM occurs.

17. Network or isolation fails.

18. Output exceeds the committed boundary.

19. Cleanup fails.

20. A launch cannot be sealed or represented durably.

21. Existing metrics or gates must change.

22. A sibling repository must be accessed.

23. Work cannot fit in one PR-sized branch.

## Verification

Pass requires:

- frozen dependency synchronization;

- Ruff format and lint;

- strict mypy;

- complete pytest suite;

- every merged Track validator;

- every Track 9A schema and record validator;

- Track 9 authorization validation;

- consumed-plan rejection tests;

- plan and 72-run inventory tests;

- result-root isolation tests;

- operator-approval tests;

- raw-output-boundary tests;

- output-digest tests;

- extraction tests;

- JSON parsing tests;

- response-schema tests;

- evidence-ID tests;

- truncation tests;

- output-limit tests;

- failure-attribution tests;

- gold-isolation tests;

- prior-result-isolation tests;

- cgroup post-exit tests;

- no-silent-launch-loss tests;

- corpus completeness tests;

- repetition-consistency tests;

- metric and gate tests;

- empirical-capability tests;

- comparison and calibration tests;

- closeout tests;

- Track 10 readiness tests;

- workflow-policy validation;

- dependency-policy validation;

- prohibited-artifact scan;

- dependency and lockfile check;

- documentation checks;

- `git diff --check`;

- `git status --short --branch`.

Also confirm:

- no memory-context measurement reran;

- no new artifact was acquired;

- no project runtime dependency was added;

- historical result roots remained unchanged;

- exactly the approved corpus-only phases ran;

- no production or tenant data was used;

- candidate selection remains `no-selection`;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false.

## Handoff Requirements

Return:

1. Outcome

2. Base commit and branch

3. Track 9 authority

4. Historical-plan rejection

5. New plan and digest

6. Operator checkpoint

7. Runtime and candidate identities

8. Corpus, prompt, schema, and template identities

9. Result-root validation

10. Raw-output retention design

11. Planned run inventory

12. Completed run inventory

13. Missing or unsealed runs

14. Per-run raw-output identities

15. Extraction outcomes

16. JSON parsing outcomes

17. Schema-validation outcomes

18. Failure-authority outcomes

19. Truncation and output-limit outcomes

20. Cgroup and cleanup outcomes

21. Corpus completeness

22. Repetition consistency

23. Metrics and gates

24. Ten empirical capabilities

25. Comparison

26. Calibration interpretation

27. Closeout

28. Track 10 readiness

29. Files changed

30. External result files

31. Dependency impact

32. Complete verification

33. Independent verification

34. Scope compliance

35. Residual risks

36. Proposed commit and PR

37. Post-merge recommendation

Final verdict must be exactly one of:

- `TRACK 10 CANDIDATE DISPOSITION REVIEW READY`

- `TRACK 10 CANDIDATE DISPOSITION REVIEW READY WITH DOCUMENTED RESIDUALS`

- `TRACK 10 CANDIDATE DISPOSITION REVIEW NOT READY`

- `BLOCKED BY UNRESOLVED AUTHORITY`

Explicitly confirm:

- no memory-context rerun;

- no new acquisition;

- no project runtime installation;

- no template replacement;

- no response-schema, prompt, metric, or gate change;

- no conversion or quantization;

- no candidate selection;

- no PatchPilot integration;

- no automatic Git action;

- no GitHub setting change;

- no publication, release, or deployment;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false.

End with exactly one:

`INTELLIGENCE TRACK 9A READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT`

or:

`INTELLIGENCE TRACK 9A BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW`