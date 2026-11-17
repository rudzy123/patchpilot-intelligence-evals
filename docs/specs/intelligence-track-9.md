Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this specification, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 9: Evaluation Evidence Review and Proportionality Decision

## Identity

- **Repository:** `patchpilot-intelligence-evals`

- **Session ID:** Intelligence Track 9

- **Mission:** Review the complete evidence produced through Track 8B-R2, determine what conclusions are supported about memory, execution safety, and behavioral suitability, and decide whether one narrowly bounded corpus-only continuation is proportionate or whether further investment in the current candidate should stop.

- **Base commit:** The parent of the specification-only commit introducing this file. Before implementation, `git rev-parse HEAD^` must equal `git rev-parse origin/main`.

- **Expected repository state:** Track 8B-R2 merged; protected checks passing; real ONNX execution proven; 4,096-token and 8,192-token memory measurements completed; corpus evaluation partial and inconclusive; 15 immutable run records present; 19 cases without complete results; schema-failure authority unresolved; R2 plan consumed and non-reusable; no R3 plan issued; candidate selection `no-selection`; calibration `not-approved`; Track 9 readiness `not-ready`; `productionReady` false.

- **Branch:** `docs/intelligence-track-9-evidence-review`

- **Change type:** Evidence synthesis, proportionality analysis, decision records, closed schemas, deterministic validation, documentation, tests, and Repository Contracts integration. No candidate execution, artifact acquisition, plan creation, measurement, behavioral rerun, candidate selection, product integration, release, or deployment.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** `docs(evals): review candidate measurement evidence`

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, merge, alter GitHub settings, acquire artifacts, install dependencies, create a new execution plan, create a new result root, call ONNX Runtime `Run`, publish, release, or deploy.

## Architectural Outcome

Track 9 must answer:

> Given the complete committed evidence from Track 8B-R2, is one clean corpus-only continuation justified, or should evaluation of the current candidate stop?

Track 9 must determine:

1. Which Track 8B-R2 findings are valid candidate evidence.

2. Which findings are infrastructure evidence.

3. Which findings remain unresolved.

4. Whether the measured memory result is sufficient for continued single-process evaluation.

5. Whether the 15 schema-failure records support any candidate-quality conclusion.

6. Whether the missing raw outputs prevent reliable failure attribution.

7. Whether the existing corpus can be completed without repeating accepted memory measurements.

8. Whether a continuation can be substantially narrower than Track 8B-R2.

9. Whether bounded raw-output retention is required.

10. Whether all 24 cases must be rerun or only the remaining 19 cases.

11. Whether comparable three-repetition results require a clean 24-case rerun.

12. Whether another execution is proportionate given the engineering cost and remaining uncertainty.

13. Whether the candidate should be rejected without further execution.

14. Whether further investment should stop.

15. Whether a separate corpus-only continuation Session should be authorized in principle.

16. Whether candidate selection remains `no-selection`.

17. Whether calibration remains `not-approved`.

18. Whether `productionReady` remains false.

Track 9 must end with exactly one disposition:

1. `candidate-rejected`;

2. `corpus-only-continuation-authorized-in-principle`;

3. `narrow-forensic-session-required`;

4. `further-investment-stopped`;

5. `blocked-by-unresolved-authority`.

The Session must not operationally execute any disposition.

## Governing Authority

Before analysis or editing, Cursor must reread:

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

- every architecture, provenance, operations, authorization, closeout, defect, and implementation-review document;

- every current schema;

- original candidate protocol;

- immutable result-storage contract;

- comparison and calibration contracts;

- promotion gates;

- Track 4 selection and scoring authority;

- Track 5 real-candidate and artifact-cache boundaries;

- Track 6A hardened execution profile;

- Track 6B corrected ONNX adapter;

- Track 7 finalist and no-selection records;

- Track 7A storage and promotion records;

- Track 7B memory and suitability contracts;

- Track 8A acquisition and verified-artifact identities;

- Track 8B stopped attempt and template correction;

- Track 8B-R1 stopped attempt, dependency-closure correction, and memory-conclusion correction;

- Track 8B-R2 real-execution records, memory evidence, schema forensics, corrected behavioral interpretation, proportionality review, plan disposition, closeout, Track 9 readiness, and implementation review;

- current corpus and metric definitions;

- current CLI commands and tests;

- Intelligence Track 2 through Track 8B-R2 specifications;

- synchronized protected-CI evidence from `main`.

Do not inspect or modify `patchpilot` or `neural-from-scratch`.

Do not perform new public candidate or runtime research. Track 9 is based on committed program evidence.

## Authoritative Evidence Baseline

Track 9 must preserve these facts unless a committed inconsistency is discovered.

### Runtime and candidate

- Runtime: ONNX Runtime `v1.31.1`

- Candidate: `LiquidAI/LFM2.5-1.2B-Instruct`

- Candidate precision: FP32

- Runtime and candidate remain externally verified

- No runtime or model artifact is committed to Git

- Candidate selection remains `no-selection`

### Execution

- Exact-sandbox dependency loading passed

- ONNX Runtime session creation passed

- ONNX Runtime `Run` passed

- One-token smoke passed

- Bounded short generation passed

- OS-level network denial passed

- Hardened isolation passed

- Process cleanup passed for completed phases

- No production or tenant data was used

### Memory

Process-memory ceiling:

`12,884,901,888` bytes

Measured cgroup peaks:

- 4,096-token cold: `7,284,371,456` bytes

- 4,096-token warm: `8,511,131,648` bytes

- 8,192-token cold: `9,816,231,936` bytes

- 8,192-token warm: `12,271,669,248` bytes

Minimum measured headroom:

`613,232,640` bytes

Memory conclusion:

`within-ceiling-with-limited-headroom`

Operational constraint:

- one candidate process at a time;

- same thread and context configuration;

- same cgroup ceiling;

- no increased context or output authority;

- no concurrency inference.

### Behavioral evidence

- Behavioral measurement attempted: true

- Behavioral measurement completed: false

- Behavioral conclusion: `partial-inconclusive`

- Candidate metrics produced: false

- Candidate evaluated completely: false

- Sealed corpus run records: 15

- Case/repetition groups completed: 5

- Cases without complete results: 19

- Unsealed launch: 1

- Summary stop: `telemetry-unresolved`

- All 15 sealed runs classified as schema failures

- Raw candidate output was not retained

- Exact JSON parse and schema errors were not retained

- Failure authority for all 15 runs: `unresolved`

- No candidate schema-compliance conclusion is supported

- No invariant or percentage gates were scored

- Comparison winner remains null

- Calibration remains `not-approved`

### Plan disposition

The following plans remain consumed and non-reusable:

- Track 8B plan:

  `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2`

- Track 8B-R1 plan:

  `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b`

- Track 8B-R2 plan:

  `2133054bea8db11822cc65f6ea9c45f1ba1500f1aef67d314fbccca764155350`

No replacement or R3 plan exists.

## Invariants

### Review-only Session

Track 9 must not:

- call ONNX Runtime `Run`;

- create a model session;

- create a new measurement plan;

- generate a plan digest for execution;

- create a new external result root;

- modify any historical result root;

- acquire or replace artifacts;

- install runtime dependencies;

- execute the corpus;

- rerun any case;

- create additional candidate output;

- change the corpus, prompts, schemas, metrics, or gates.

Synthetic validation of Track 9 decision logic is permitted.

### Deterministic PatchPilot authority

No candidate evidence or Track 9 recommendation may become authoritative over:

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

### Evidence classification

Every material finding must be classified as:

- `candidate-evidence`;

- `measurement-infrastructure-evidence`;

- `security-boundary-evidence`;

- `unresolved`;

- `not-applicable`.

Track 9 must not use infrastructure defects as candidate-quality evidence.

Track 9 must not discard valid memory measurements merely because the corpus later stopped.

### Memory interpretation

The measured memory result is valid for:

- exact FP32 artifact identity;

- exact runtime identity;

- batch size 1;

- one candidate process;

- approved thread configuration;

- approved 4,096-token and 8,192-token inputs;

- bounded generated output;

- approved hardened environment.

It is not evidence for:

- concurrent candidate processes;

- larger contexts;

- longer outputs;

- production capacity;

- unrestricted workloads;

- additional execution providers;

- different precision or artifacts.

The limited 613,232,640-byte headroom must remain an explicit residual risk.

### Behavioral interpretation

The 15 sealed runs must not be scored because:

- corpus execution is incomplete;

- only five case groups have sealed records;

- raw output is absent;

- exact parse and schema errors are absent;

- failure authority is unresolved;

- 19 cases lack complete results.

Track 9 must not:

- mark schema compatibility failed;

- mark any empirical capability failed;

- calculate percentage metrics from incomplete evidence;

- impute missing cases;

- treat all missing cases as failures;

- treat all missing cases as passes;

- compare the candidate as though the corpus were complete.

### Continuation alternatives

Track 9 must evaluate these alternatives.

#### Alternative A: Reject candidate now

Consider:

- limited memory headroom;

- incomplete behavior evidence;

- three infrastructure-stop cycles;

- engineering cost;

- inability to establish schema compliance.

Reject only if existing evidence contains a supported mandatory failure.

Absence of evidence alone is not a measured candidate failure.

#### Alternative B: Continue only remaining 19 cases

Consider:

- lower execution cost;

- preservation of 15 existing records;

- inability to compare results uniformly because raw-output retention and telemetry behavior would differ;

- potential inconsistency between old and new records;

- incomplete three-repetition comparability across the corpus.

This alternative must fail if the result set would not meet the existing immutable comparison contract.

#### Alternative C: Clean 24-case corpus-only rerun

Consider:

- accepted memory evidence need not be repeated;

- runtime and candidate identities remain verified;

- real execution is proven;

- corrected cgroup finalization is merged;

- raw-output retention can provide failure attribution;

- one clean result identity provides consistent three-repetition records;

- execution cost remains bounded to 72 runs;

- no context-memory repetition is necessary.

This is the preferred continuation only if all safeguards can be specified without changing prompts, metrics, gates, or candidate behavior.

#### Alternative D: Narrow forensic Session

Consider only when a decision can be reached through further analysis without candidate execution.

Do not use this alternative to postpone a decision without identifying a concrete missing record or authority conflict.

#### Alternative E: Stop further investment

Consider:

- accumulated engineering cost;

- candidate’s expected value;

- limited memory headroom;

- repeated infrastructure defects;

- uncertainty about output validity;

- opportunity cost of evaluating another candidate or ending the program.

Stopping is valid even when no candidate failure is proven, but it must be characterized as a proportionality decision rather than a candidate-quality verdict.

### Preferred continuation boundary

If Track 9 authorizes a corpus-only continuation in principle, that later Session must:

- reuse accepted memory evidence;

- not rerun 4,096-token or 8,192-token measurements;

- use the same verified runtime and candidate;

- use the same hardened boundary;

- use the same corpus, prompt-template digest, decoding settings, metrics, and gates;

- execute all 24 cases under one new result identity;

- run three repetitions per case;

- retain bounded raw candidate output for every run;

- distinguish raw output from extracted and parsed output;

- record JSON parse errors;

- record response-schema errors;

- record truncation and output-limit behavior;

- classify failure authority;

- retain output digests;

- keep gold and evaluator records hidden;

- use a new plan digest;

- use a fresh empty result root;

- require a new operator checkpoint;

- stop on memory, network, isolation, output, cleanup, identity, or telemetry failure;

- preserve no-selection, calibration not-approved, and `productionReady: false`.

The later Session must not automatically select or promote the candidate.

### Raw-output retention boundary

If continuation is authorized, raw-output retention must be:

- bounded by existing stdout limits;

- external during execution;

- redacted only according to committed synthetic-data rules;

- immutable;

- digest-identified;

- associated with case ID and repetition;

- unavailable to later candidate runs;

- unavailable to the candidate itself;

- free of gold or evaluator data;

- represented in committed evidence through digests, lengths, classifications, and approved bounded content where policy permits.

Raw-output retention must not expose host paths or machine identity.

### Proportionality criteria

Track 9 must score or classify, without inventing false precision:

- evidence value of completing the corpus;

- estimated run count;

- expected wall-clock and CPU cost;

- external storage cost;

- infrastructure complexity;

- residual security risk;

- probability of obtaining decision-grade evidence;

- effect of another infrastructure failure;

- opportunity cost;

- candidate’s memory fit;

- candidate’s expected role as a non-authoritative explanation assistant.

The proportionality record must use explicit ordinal or closed categorical values.

### Selection and production remain frozen

Regardless of Track 9’s recommendation:

- `selectionOutcome` remains `no-selection`;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false;

- no PatchPilot integration is authorized;

- no shadow mode is authorized;

- no release or deployment is authorized.

## Assumed Repository State

Before editing, Cursor must prove:

- repository root is `patchpilot-intelligence-evals`;

- local `main` equals `origin/main`;

- Track 8B-R2 is merged;

- specification-only commit parent equals `origin/main`;

- working tree is clean after the specification commit;

- protected checks pass on synchronized `main`;

- all three measurement plans are consumed and non-reusable;

- no replacement or R3 plan exists;

- Track 8B-R2 memory evidence validates;

- Track 8B-R2 schema forensics validate;

- corrected behavioral interpretation validates;

- proportionality review validates;

- implementation-review digest validates;

- Track 9 readiness remains not-ready;

- external verified artifacts remain available but unused;

- historical result roots remain unchanged;

- no project runtime dependency exists;

- no model or runtime artifact exists in Git;

- candidate selection remains no-selection;

- calibration remains not approved;

- `productionReady` remains false;

- no sibling repository is nested in the Git tree.

If any material assumption is false, stop.

## Allowed Change Surface

Permitted:

- `docs/specs/intelligence-track-9.md`;

- evidence-review architecture;

- evidence-classification records;

- memory-review records;

- behavioral-evidence review;

- proportionality analysis;

- continuation-decision records;

- future corpus-only boundary documentation;

- closed schemas;

- validation modules;

- deterministic synthetic decision tests;

- CLI validators;

- Repository Contracts updates;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, and governance documentation.

Not permitted:

- candidate execution;

- new result root;

- new measurement plan;

- plan digest for execution;

- artifact acquisition;

- artifact mutation;

- template replacement;

- project runtime installation;

- conversion or quantization;

- corpus changes;

- prompt changes;

- schema changes to candidate response;

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

│   ├── [evaluation-evidence-review.md](http://evaluation-evidence-review.md)

│   ├── [corpus-continuation-boundary.md](http://corpus-continuation-boundary.md)

│   └── [candidate-disposition-authority.md](http://candidate-disposition-authority.md)

├── provenance/

│   └── [track9-evidence-review.md](http://track9-evidence-review.md)

├── operations/

│   └── [corpus-only-continuation-prerequisites.md](http://corpus-only-continuation-prerequisites.md)

└── specs/

	└── [intelligence-track-9.md](http://intelligence-track-9.md)

schemas/

├── evaluation-evidence-inventory.schema.json

├── memory-evidence-review.schema.json

├── behavioral-evidence-review.schema.json

├── proportionality-decision.schema.json

├── corpus-continuation-authorization.schema.json

└── candidate-disposition.schema.json

candidates/

└── authorization/

	├── evaluation-evidence-inventory.json

	├── memory-evidence-review.json

	├── behavioral-evidence-review.json

	├── proportionality-decision.json

	├── corpus-continuation-authorization.json

	└── candidate-disposition.json

src/patchpilot_intelligence_evals/

├── evaluation_evidence_[review.py](http://review.py)

├── memory_evidence_[review.py](http://review.py)

├── behavioral_evidence_[review.py](http://review.py)

├── proportionality_[decision.py](http://decision.py)

├── corpus_continuation_[authorization.py](http://authorization.py)

└── candidate_[disposition.py](http://disposition.py)

tests/

├── test_evaluation_evidence_[review.py](http://review.py)

├── test_memory_evidence_[review.py](http://review.py)

├── test_behavioral_evidence_[review.py](http://review.py)

├── test_proportionality_[decision.py](http://decision.py)

├── test_corpus_continuation_[authorization.py](http://authorization.py)

└── test_candidate_[disposition.py](http://disposition.py)

```

Exact paths may differ only to follow repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and records for:

1. evaluation evidence inventory;

2. memory evidence review;

3. behavioral evidence review;

4. proportionality decision;

5. corpus-continuation authorization;

6. candidate disposition.

Every schema must:

- have a stable ID and explicit version;

- use `additionalProperties: false`;

- identify exact candidate and runtime identities;

- reference all three consumed plans;

- distinguish candidate evidence from infrastructure evidence;

- represent incomplete evidence;

- represent unresolved failure authority;

- prohibit execution instructions;

- prohibit a new plan digest;

- prohibit absolute external paths;

- prohibit secrets and host identity;

- preserve `selectionOutcome: no-selection`;

- preserve `calibrationStatus: not-approved`;

- preserve `comparisonWinner: null`;

- preserve `productionReady: false`;

- support every permitted Track 9 disposition.

The continuation-authorization record may authorize only a future Session in principle. It must not contain operator approval or current execution authority.

## Evidence Decision Rules

### Memory review

The memory review must validate exact arithmetic:

```text

ceiling:

12,884,901,888

maximum measured peak:

12,271,669,248

headroom:

613,232,640

```

The review must classify:

- memory gate: passed;

- headroom: limited;

- concurrency: prohibited;

- larger context: not authorized;

- production capacity: not established.

### Behavioral review

The behavioral review must classify:

- attempted: true;

- completed: false;

- metrics produced: false;

- schema failures observed: 15;

- schema-failure authority: unresolved;

- missing completed cases: 19;

- candidate-quality conclusion: unavailable;

- schema-compliance conclusion: unavailable;

- empirical-capability conclusions: unavailable.

### Continuation authorization

A continuation may be `authorized-in-principle` only when:

- accepted memory evidence eliminates the need to repeat context phases;

- execution safety remains proven;

- corrected telemetry finalization is merged and tested;

- exact artifact identities remain fixed;

- bounded raw-output retention is specified;

- execution remains corpus-only;

- all 24 cases run under one fresh identity;

- the existing prompt, schema, metrics, and gates remain unchanged;

- three repetitions remain required;

- gold isolation remains mandatory;

- a new future specification and operator checkpoint remain mandatory;

- execution cost is judged proportionate.

### Candidate disposition

Track 9 must not select the candidate.

Permitted disposition values:

- `evaluation-incomplete-continuation-authorized-in-principle`;

- `candidate-rejected`;

- `further-forensics-required`;

- `further-investment-stopped`;

- `blocked-by-unresolved-authority`.

## Multi-Agent Execution Model

Cursor Plan is the parent evidence-review orchestrator.

Use Grok 4.7 Extra High for:

- evidence authority;

- candidate-versus-infrastructure attribution;

- memory interpretation;

- behavioral-evidence interpretation;

- proportionality;

- continuation boundaries;

- candidate disposition;

- conflict resolution;

- independent verification.

Delegate read-only and controlled implementation to:

### Agent 1: Evidence-inventory specialist

Owns all committed Track 8B, R1, and R2 evidence identities, completeness, provenance, and classification.

### Agent 2: Memory-review specialist

Owns memory arithmetic, scope of applicability, headroom interpretation, and residual risk.

### Agent 3: Behavioral-review specialist

Owns corpus completeness, schema-forensics limitations, missing evidence, and candidate-versus-infrastructure attribution.

### Agent 4: Continuation-design specialist

Owns clean 24-case corpus-only boundary, raw-output retention, result identity, execution constraints, and future operator checkpoint requirements.

### Agent 5: Proportionality specialist

Owns cost, expected evidence value, infrastructure maturity, failure risk, opportunity cost, and stopping criteria.

### Agent 6: Disposition specialist

Owns the final recommendation, no-selection preservation, calibration interpretation, and future authority boundary.

### Agent 7: Independent verifier

Runs after implementation.

Must not own evidence inventory, memory review, behavioral review, continuation design, proportionality, or disposition.

### Coordination Rules

The parent must:

- perform no candidate execution;

- inspect evidence read-only;

- require exact record identities;

- distinguish observed fact from recommendation;

- assign exclusive file ownership;

- prevent unsupported conclusions;

- integrate centrally;

- commission a fresh independent verifier.

Every specialist must return:

- finding;

- exact supporting records;

- evidence class;

- supported conclusion;

- unsupported conclusion;

- residual uncertainty;

- recommendation;

- owned files;

- tests required.

## Ordered Execution Plan

### Task 1: Verify the Post-R2 Baseline

#### Allowed files or subsystem

Read-only Git state, all Track 8A through Track 8B-R2 records, external-evidence identities, workflows, tests, architecture, and provenance.

#### Required behavior

Confirm every assumed-state item.

Record:

- synchronized `main` identity;

- all three consumed plans;

- exact memory evidence identities;

- exact behavioral evidence identities;

- exact external-result inventories without modifying them;

- exact file ownership for Tasks 2 through 8.

#### Tests

Run existing validators and digest checks only.

#### Done condition

The baseline is proven and no execution or external mutation occurred.

### Task 2: Build the Evaluation Evidence Inventory

#### Allowed files or subsystem

Evidence-inventory schema and record, validation module, CLI, documentation, and tests.

#### Required behavior

Inventory every material item from Track 8B, R1, and R2.

Classify each item as:

- candidate evidence;

- measurement-infrastructure evidence;

- security-boundary evidence;

- unresolved;

- not applicable.

Record whether each item supports:

- memory conclusions;

- execution conclusions;

- behavioral conclusions;

- continuation decisions;

- candidate disposition.

#### Tests

Validate completeness, uniqueness, identity references, and authority classifications.

#### Done condition

One authoritative evidence inventory exists.

### Task 3: Review the Memory Evidence

#### Allowed files or subsystem

Memory-review schema and record, arithmetic validator, CLI, documentation, and tests.

#### Required behavior

Validate the four measured peaks, ceiling, maximum, and headroom.

Document exact applicability and non-applicability.

Classify:

- 4,096-token memory gate;

- 8,192-token memory gate;

- limited-headroom risk;

- concurrency prohibition;

- production-capacity uncertainty.

#### Tests

Validate exact arithmetic, boundary behavior, and prohibited inference.

#### Done condition

The memory result has a precise decision scope.

### Task 4: Review the Behavioral Evidence

#### Allowed files or subsystem

Behavioral-review schema and record, validator, documentation, and tests.

#### Required behavior

Review:

- 15 sealed run records;

- five complete case/repetition groups;

- one unsealed launch;

- 19 cases without complete results;

- absent raw outputs;

- unresolved schema-failure authority;

- absent metrics and gate decisions.

Determine which conclusions are supported and which remain unavailable.

#### Tests

Prevent scoring incomplete evidence, imputing missing cases, or assigning unsupported failure authority.

#### Done condition

The behavioral evidence has a precise, fail-closed interpretation.

### Task 5: Evaluate Continuation Alternatives

#### Allowed files or subsystem

Continuation architecture, proportionality schema and record, deterministic decision logic, documentation, and tests.

#### Required behavior

Evaluate:

- reject now;

- remaining-19 continuation;

- clean 24-case corpus-only rerun;

- narrow forensic Session;

- stop investment.

For each, record:

- evidence value;

- comparability;

- execution scope;

- estimated runs;

- expected resource cost;

- infrastructure risk;

- security risk;

- decision value;

- disqualifiers.

Use a closed categorical scale rather than unsupported numeric precision.

#### Tests

Validate each alternative and prohibit a continuation that changes prompts, metrics, gates, or artifacts.

#### Done condition

The proportionality decision is explicit and reproducible.

### Task 6: Define or Withhold Corpus-Only Continuation Authority

#### Allowed files or subsystem

Continuation-authorization schema and record, future boundary documentation, validation module, and tests.

#### Required behavior

If continuation is justified, authorize only a future corpus-only Session in principle.

Require:

- clean execution of all 24 cases;

- three repetitions per case;

- 72 planned runs;

- bounded raw-output retention;

- parse and schema diagnostics;

- failure-authority classification;

- accepted memory evidence reused;

- no 4,096-token or 8,192-token rerun;

- same verified artifacts;

- new plan and digest;

- fresh result root;

- new operator approval;

- unchanged prompts, schema, metrics, and gates;

- hardened execution;

- stop at the first security, memory, identity, output, or cleanup failure.

Do not create the future plan.

If continuation is not justified, record that explicitly.

#### Tests

Validate authorization-in-principle and withholding paths.

#### Done condition

Future execution authority is either narrowly bounded or withheld.

### Task 7: Record Candidate Disposition

#### Allowed files or subsystem

Disposition schema and record, decision logic, CLI, documentation, and tests.

#### Required behavior

Record exactly one Track 9 disposition.

Preserve:

- `selectionOutcome: no-selection`;

- `calibrationStatus: not-approved`;

- `comparisonWinner: null`;

- `productionReady: false`.

Do not represent continuation authority as candidate selection.

#### Tests

Validate all allowed dispositions and prohibit contradictory authority.

#### Done condition

Track 9 has a durable recommendation.

### Task 8: Documentation, Repository Contracts, and Independent Verification

#### Allowed files or subsystem

README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, workflows, tests, and complete diff.

#### Required behavior

Document:

- evidence inventory;

- memory decision;

- behavioral limitations;

- proportionality analysis;

- continuation boundary;

- candidate disposition;

- preserved authority.

Update Repository Contracts to validate all Track 9 records.

CI must remain artifact-free and inference-free.

A fresh independent verifier must confirm:

- no execution occurred;

- no external evidence changed;

- all arithmetic is exact;

- behavioral evidence was not overinterpreted;

- the final disposition follows the committed decision rules;

- no authority was broadened beyond the decision record.

#### Tests

Run every command in Verification.

#### Done condition

Track 9 is ready for Principal Architect review.

## Out of Scope

Track 9 must not:

- create or approve an operational execution plan;

- call `Run`;

- create a model session;

- create a result root;

- acquire or replace artifacts;

- modify historical evidence;

- alter the candidate template;

- alter response schemas;

- alter corpus prompts;

- alter metrics or gates;

- install dependencies;

- convert or quantize;

- select the candidate;

- integrate with PatchPilot;

- authorize shadow mode;

- change GitHub settings;

- publish, release, or deploy.

## Stop Conditions

Stop and report if:

1. Specification parent differs from `origin/main`.

2. Working tree contains unrelated changes.

3. Track 8B-R2 is not merged.

4. Any consumed plan appears reusable.

5. A replacement or R3 plan exists unexpectedly.

6. Memory evidence differs.

7. Behavioral evidence differs.

8. Historical external evidence changed.

9. Analysis requires candidate execution.

10. Analysis requires changing metrics or gates.

11. A candidate failure would need to be inferred from unresolved evidence.

12. A future continuation cannot preserve a clean comparable result identity.

13. Gold isolation cannot be guaranteed.

14. A sibling repository must be inspected.

15. Work cannot fit in one pull-request-sized branch.

## Verification

Pass requires:

- `uv sync --frozen`;

- `uv run ruff format --check .`;

- `uv run ruff check .`;

- `uv run mypy src tests`;

- `uv run pytest`;

- corpus validation;

- baseline evaluation;

- every merged Track validator;

- fixture, comparison, and calibration validation;

- workflow-policy validation;

- dependency-architecture-policy validation;

- every Track 9 schema validation;

- every Track 9 record validation;

- evidence-inventory completeness tests;

- evidence-classification tests;

- exact memory-arithmetic tests;

- memory-scope tests;

- incomplete-behavioral-evidence tests;

- no-imputation tests;

- unresolved-authority tests;

- alternative-comparison tests;

- proportionality-decision tests;

- continuation-boundary tests;

- raw-output-retention requirement tests;

- candidate-disposition tests;

- contradictory-authority tests;

- documentation and relative-link checks;

- prohibited-artifact scan;

- no-execution-command validation;

- dependency and lockfile check;

- `git diff --check`;

- `git status --short --branch`.

Also confirm:

- no candidate execution occurred;

- no new plan digest was created;

- no new result root was created;

- no external result changed;

- no artifact was acquired or modified;

- no runtime dependency entered the project;

- no conversion or quantization occurred;

- candidate selection remains `no-selection`;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false;

- no publication, release, or deployment occurred.

## Handoff Requirements

Return one consolidated handoff containing:

1. Outcome

2. Base commit, branch, and working-tree state

3. Multi-agent execution summary

4. Post-R2 baseline

5. Evidence inventory

6. Candidate evidence

7. Infrastructure evidence

8. Security-boundary evidence

9. Unresolved evidence

10. Memory evidence review

11. Exact memory arithmetic

12. Memory applicability and limitations

13. Behavioral evidence review

14. Schema-failure authority

15. Missing evidence

16. Candidate conclusions supported

17. Candidate conclusions unsupported

18. Alternative A analysis

19. Alternative B analysis

20. Alternative C analysis

21. Alternative D analysis

22. Alternative E analysis

23. Proportionality decision

24. Continuation authorization or withholding

25. Raw-output-retention boundary

26. Candidate disposition

27. Files changed

28. Dependency and lockfile impact

29. Every verification command and result

30. CI changes

31. Independent verification

32. Scope compliance

33. Residual risks

34. Exact next recommendation

35. Proposed Conventional Commit

36. Proposed PR title and summary

37. Required post-merge steps

Final verdict must be exactly one of:

- `CORPUS-ONLY CONTINUATION AUTHORIZED IN PRINCIPLE`

- `CANDIDATE REJECTED`

- `NARROW FORENSIC SESSION REQUIRED`

- `FURTHER INVESTMENT STOPPED`

- `BLOCKED BY UNRESOLVED AUTHORITY`

Explicitly confirm:

- no candidate execution occurred;

- no new measurement plan was created;

- no plan digest for execution was issued;

- no result root was created;

- no artifact was acquired or changed;

- no project runtime installation occurred;

- no conversion or quantization occurred;

- no candidate selection occurred;

- no PatchPilot integration occurred;

- no automatic Git action occurred;

- no GitHub setting changed;

- no package was published;

- no release or deployment occurred;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false.

End with exactly one:

`INTELLIGENCE TRACK 9 READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT`

or:

`INTELLIGENCE TRACK 9 BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW`