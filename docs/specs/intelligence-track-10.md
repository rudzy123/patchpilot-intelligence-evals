Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this specification, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 10: Candidate Disposition Review After Attributed Schema Failure

## Identity

- **Repository:** `patchpilot-intelligence-evals`

- **Session ID:** Intelligence Track 10

- **Mission:** Review the attributed candidate-output schema failure, the stopped Track 9A continuation, the accepted memory evidence, and the complete program investment to determine whether the candidate should be rejected, whether further investment should stop, or whether one final six-run diagnostic sample is proportionate.

- **Base commit:** The parent of the specification-only commit introducing this file. Before implementation, `git rev-parse HEAD^` must equal `git rev-parse origin/main`.

- **Expected repository state:** Track 9A merged; its plan consumed and non-reusable; one sealed corpus run retained; 71 planned runs missing; execution stopped because of a corrected measurement-infrastructure defect; one candidate-output response proven schema-invalid; candidate metrics not produced; Track 10 readiness `not-ready`; candidate selection `no-selection`; calibration `not-approved`; comparison winner null; `productionReady` false.

- **Branch:** `docs/intelligence-track-10-candidate-disposition`

- **Change type:** Review-only evidence synthesis, mandatory-invariant analysis, proportionality analysis, diagnostic-sample decision, candidate-disposition records, schemas, deterministic tests, documentation, and Repository Contracts integration. No execution, acquisition, plan generation, result-root creation, candidate selection, integration, release, or deployment.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** `docs(evals): review attributed schema failure`

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, merge, modify Git history, change GitHub settings, acquire or replace artifacts, create an execution plan, create a plan digest, create a result root, call ONNX Runtime `Run`, publish, release, or deploy.

## Architectural Outcome

Track 10 must answer:

> Does one proven candidate-output schema failure establish a mandatory candidate failure, or is one final six-run diagnostic sample required to determine whether the failure is systematic?

Track 10 must determine:

1. Whether response-schema conformance is a mandatory invariant, a percentage gate, or both.

2. Whether one schema-invalid response is sufficient for candidate rejection.

3. Whether the first response received the exact authorized response contract.

4. Whether the adapter, protocol, extraction, parser, or evaluator altered the candidate’s response shape.

5. Whether the malformed response represents a systematic candidate misunderstanding or an isolated failure.

6. Whether six diagnostic runs can answer that question without repeating the full corpus.

7. Whether a six-run diagnostic can preserve comparability and authority.

8. Whether a full 72-run corpus continuation remains proportionate.

9. Whether further investment should stop.

10. Whether the candidate should be rejected.

11. Whether one final diagnostic Session should be authorized in principle.

12. Whether candidate selection remains `no-selection`.

13. Whether calibration remains `not-approved`.

14. Whether comparison winner remains null.

15. Whether `productionReady` remains false.

Track 10 must end with exactly one disposition:

1. `candidate-rejected`;

2. `six-run-diagnostic-authorized-in-principle`;

3. `full-corpus-continuation-authorized-in-principle`;

4. `further-investment-stopped`;

5. `blocked-by-unresolved-authority`.

The Session must not execute any disposition.

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

- every current architecture, provenance, operations, authorization, defect, closeout, readiness, disposition, and implementation-review document;

- every current schema;

- candidate protocol and subprocess contracts;

- immutable result-storage contract;

- response-schema authority;

- comparison and calibration contracts;

- current corpus, metrics, and promotion gates;

- Track 4 candidate mandatory criteria and scoring authority;

- Track 6A hardened execution profile;

- Track 6B corrected ONNX adapter;

- Track 7 finalist and no-selection records;

- Track 7A storage and promotion records;

- Track 7B memory and suitability contracts;

- Track 8A acquisition, artifact identities, load proof, and closeout;

- Track 8B, Track 8B-R1, and Track 8B-R2 evidence and reviews;

- Track 9 evidence review, proportionality decision, continuation authorization, disposition, and implementation review;

- Track 9A plan, stopped attempt, raw-output evidence, response forensics, telemetry defect, corrected interpretation, plan disposition, readiness, and implementation review;

- current CLI commands and tests;

- Intelligence Track 2 through Track 9A specifications;

- synchronized protected-CI evidence from `main`.

Do not inspect or modify `patchpilot` or `neural-from-scratch`.

Do not perform new public model or runtime research.

## Authoritative Evidence Baseline

Track 10 must preserve the following facts unless a committed inconsistency is discovered.

### Runtime and candidate

- Runtime: ONNX Runtime `v1.31.1`

- Candidate: `LiquidAI/LFM2.5-1.2B-Instruct`

- Candidate precision: FP32

- Runtime and candidate remain externally verified

- Exact-sandbox runtime dependency loading passed

- Model-session creation passed

- ONNX Runtime `Run` passed

- Candidate selection remains `no-selection`

### Accepted memory evidence

- 4,096-token cold peak: `7,284,371,456` bytes

- 4,096-token warm peak: `8,511,131,648` bytes

- 8,192-token cold peak: `9,816,231,936` bytes

- 8,192-token warm peak: `12,271,669,248` bytes

- Resident ceiling: `12,884,901,888` bytes

- Minimum headroom: `613,232,640` bytes

- Memory conclusion: `within-ceiling-with-limited-headroom`

- One candidate process at a time remains mandatory

- Larger context and concurrent execution remain unauthorized

### Track 9A execution evidence

- Plan digest:

  `6c4a9e6c64a3afe3c1cbb36d19985880beb067fdb9b5634752e8c4d1482560f1`

- Plan disposition: `consumed`

- Reusable: false

- Replacement plan digest: `not-issued`

- Planned executions: 72

- Completed sealed executions: 1

- Missing executions: 71

- Behavioral measurement attempted: true

- Behavioral measurement completed: false

- Behavioral conclusion: `partial-inconclusive`

- Candidate metrics produced: false

- Candidate evaluated completely: false

- Track 10 readiness: `not-ready`

### Execution-stop authority

- Execution-stop authority: `measurement-infrastructure`

- Execution-stop cause: `telemetry-unresolved`

- The telemetry defect has been mechanically corrected

- The external historical record remains unchanged

- No additional execution occurred after correction

### Candidate-output evidence

Run identity:

`case-ground-001-r1`

Raw stdout:

- Length: `542` bytes

- SHA-256:

  `b28e9aa7f5db74d23040d9b3045b5fc927bc2289378bb6bf676e4568ec20b0b9`

Extracted response:

- Length: `264` bytes

- SHA-256:

  `8d5acd633059fd19ea765c0ce415bb37d4f53cc02ed848fcf6df490d55ab9d5d`

Observed response:

- valid UTF-8;

- extraction passed;

- JSON parsing passed;

- not truncated;

- output remained within limit;

- response-schema validation failed;

- response-failure authority: `candidate-output`.

Unexpected candidate fields:

- `deterministicFacts`

- `findingExplanation`

Missing required fields:

- `schemaVersion`

- `candidate`

- `authorizedOrganizationId`

- `findingId`

- `refused`

- `refusalReason`

- `preservedDeterministicFacts`

- `sourceFacts`

- `supportedClaims`

- `remediationSuggestions`

- `uncertainty`

- `citations`

- `safetyWarnings`

- `explanationText`

- `nonAuthoritative`

The authorized prompt contained response schema version `1.0.0` and the required explanation contract. Extraction and parsing preserved the candidate’s emitted keys. The adapter did not rename, remove, or add inner response fields. The intended evaluator schema was applied.

## Historical Plan Authority

The following plans are consumed and non-reusable:

- Track 8B:

  `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2`

- Track 8B-R1:

  `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b`

- Track 8B-R2:

  `2133054bea8db11822cc65f6ea9c45f1ba1500f1aef67d314fbccca764155350`

- Track 9A:

  `6c4a9e6c64a3afe3c1cbb36d19985880beb067fdb9b5634752e8c4d1482560f1`

No replacement plan exists.

## Invariants

### Review-only Session

Track 10 must not:

- call ONNX Runtime `Run`;

- create a model session;

- create a new measurement or diagnostic plan;

- generate an execution-plan digest;

- create an operator approval;

- create an external result root;

- acquire or modify artifacts;

- execute the corpus;

- execute a diagnostic case;

- modify any historical result root;

- modify retained raw output;

- alter the response schema, prompt, metrics, or gates.

Deterministic validation of Track 10 decision logic using synthetic records is permitted.

### Deterministic PatchPilot authority

No candidate evidence or Track 10 recommendation may become authoritative over:

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

### Evidence classification

Every material Track 10 finding must be classified as:

- `candidate-evidence`;

- `measurement-infrastructure-evidence`;

- `security-boundary-evidence`;

- `program-cost-evidence`;

- `unresolved`;

- `not-applicable`.

The candidate-output schema failure must remain candidate evidence.

The Track 9A telemetry stop must remain measurement-infrastructure evidence.

The two authorities must not be conflated.

### Response-schema authority

Track 10 must identify whether response-schema compliance is:

- a per-run validity requirement;

- an invariant gate;

- a percentage gate;

- a candidate-selection criterion;

- an execution-continuation criterion.

The analysis must cite committed schemas, metrics, gates, and candidate protocol authority.

Track 10 must not invent a new rejection rule.

### Single-failure interpretation

One candidate-attributed schema-invalid response proves:

- at least one authorized request received a schema-invalid candidate response;

- the candidate did not satisfy the required response contract for that run;

- the failure was not caused by truncation;

- the failure was not caused by output limits;

- the failure was not caused by extraction, parsing, adapter field rewriting, or evaluator-schema mismatch.

One response does not establish:

- systematic schema failure;

- corpus-wide schema-compliance rate;

- repetition consistency;

- category-wide behavior;

- behavior on refusal, injection, cross-tenant, contradiction, or stale-evidence cases;

- overall candidate suitability.

### Diagnostic objective

If a six-run diagnostic sample is authorized in principle, its sole purpose must be:

> Determine whether the candidate-output schema failure is systematic across corpus categories under the unchanged authorized protocol.

The diagnostic must not be represented as:

- a complete corpus evaluation;

- a substitute for percentage metrics;

- an attempt to pass promotion gates;

- a candidate-selection run;

- a calibration run.

### Six-run diagnostic boundary

A future diagnostic Session may be authorized in principle only when it can preserve all of the following:

- one representative case from each of the six corpus categories;

- one repetition per selected case;

- six total planned runs;

- same verified runtime and candidate;

- same publisher template;

- same prompt template;

- same response schema;

- same decoding configuration;

- same hardened execution boundary;

- same resource and output limits;

- accepted memory evidence reused;

- no context-memory rerun;

- bounded immutable raw-output retention;

- extraction, parsing, schema, truncation, output-limit, and evidence-ID diagnostics;

- failure authority for each run;

- gold and evaluator isolation;

- new future specification;

- new plan digest;

- fresh empty result root;

- new operator approval;

- no automatic candidate selection.

The six selected cases must be identified by deterministic committed rules. Track 10 must not operationally choose or execute the cases.

### Diagnostic decision rule

If a future diagnostic is authorized, its later disposition rules must be specified in principle.

A future review may conclude `systematic-schema-failure` when:

- the diagnostic result set is complete;

- raw output and diagnostics exist for every run;

- candidate-output authority is proven;

- schema-invalid candidate output occurs across a committed majority threshold;

- no adapter, protocol, evaluator, output-limit, truncation, or infrastructure defect explains the failures.

Track 10 must determine the exact closed threshold from existing authority or explicitly defer threshold selection to the future diagnostic specification.

Do not invent a hidden threshold.

### Rejection boundary

Candidate rejection is permitted only when:

- an existing mandatory criterion has a supported failure;

- or a committed future diagnostic decision rule is satisfied.

Track 10 must not reject based only on:

- incomplete evidence;

- engineering frustration;

- infrastructure defects;

- limited memory headroom that still passed the approved ceiling;

- the existence of multiple stopped Sessions;

- one schema-invalid response unless existing authority explicitly makes one such failure disqualifying.

### Full-corpus alternative

Track 10 must evaluate whether another clean 72-run corpus continuation remains proportionate.

Factors against a full rerun include:

- only one response is needed to establish the current diagnostic question;

- four execution plans have already been consumed;

- multiple infrastructure defects have required correction;

- memory headroom is limited;

- 72 runs carry materially greater runtime and operational cost;

- current uncertainty is narrower than complete candidate evaluation.

Factors supporting a full rerun include:

- only a complete 72-run result can produce full corpus metrics;

- schema compliance and empirical capabilities ultimately require complete evidence;

- a six-run diagnostic cannot produce promotion-gate results.

Track 10 must decide whether the six-run diagnostic should precede any full rerun.

### Stop-investment boundary

Stopping further investment is valid when:

- the expected evidence value is low;

- the opportunity cost is high;

- the candidate’s role does not justify more custom infrastructure;

- another infrastructure failure would likely provide little new candidate evidence;

- a different candidate or architecture is more proportionate.

Stopping must be recorded as a program decision, not a candidate-quality verdict, unless candidate failure is independently proven.

### Proportionality criteria

Track 10 must assess:

- candidate-evidence value;

- diagnostic run count;

- complete-corpus run count;

- expected wall-clock cost;

- CPU cost;

- external-storage cost;

- infrastructure complexity;

- residual security risk;

- probability of obtaining decision-grade attribution;

- consequence of another infrastructure failure;

- candidate memory fit and limited headroom;

- opportunity cost;

- expected value as a non-authoritative explanation assistant.

Use closed categorical values rather than unsupported numerical precision.

### Frozen authority

Regardless of disposition:

- `selectionOutcome` remains `no-selection`;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false;

- no PatchPilot integration is authorized;

- no shadow mode is authorized;

- no release or deployment is authorized.

## Decision Alternatives

Track 10 must evaluate exactly these alternatives.

### Alternative A: Reject candidate now

Determine whether the single proven schema-invalid candidate response violates an existing mandatory gate strongly enough to reject the candidate.

Reject this alternative if existing authority requires more than one result or a complete corpus.

### Alternative B: Authorize six-run diagnostic in principle

Evaluate one future run from each corpus category.

The diagnostic must answer whether schema-invalid output is systematic.

This is the preferred alternative if:

- one response is insufficient for rejection;

- another 72-run continuation is excessive for the narrow uncertainty;

- the six-run evidence can be decision-grade for schema-behavior attribution.

### Alternative C: Authorize full 24-case continuation in principle

Evaluate whether another 72-run continuation is justified immediately.

Do not select this alternative merely because Track 9 previously authorized it. Track 9A produced new candidate-output evidence that changes the proportionality question.

### Alternative D: Require protocol-focused forensics

Select only if a concrete protocol ambiguity remains that can be resolved without candidate execution.

Do not use this alternative if the retained evidence already proves the adapter, prompt, parser, and evaluator behavior.

### Alternative E: Stop further investment

Evaluate whether no additional candidate execution is proportionate.

This may be selected without declaring candidate failure.

## Preferred Decision

Unless committed authority establishes that one schema-invalid response is automatically disqualifying, the expected preferred disposition is:

`six-run-diagnostic-authorized-in-principle`

This preference is not a predetermined result. Cursor must derive the final decision from committed authority.

## Assumed Repository State

Before editing, Cursor must prove:

- repository root is `patchpilot-intelligence-evals`;

- local `main` equals `origin/main`;

- Track 9A is merged;

- specification-only commit parent equals `origin/main`;

- working tree is clean after the specification commit;

- protected checks pass on synchronized `main`;

- the Track 9A plan is consumed and non-reusable;

- no replacement plan exists;

- Track 9A external evidence is unchanged;

- Track 9A implementation-review digest validates;

- telemetry-finalization correction validates;

- response-forensics record validates;

- response-failure authority remains `candidate-output`;

- execution-stop authority remains `measurement-infrastructure`;

- behavioral conclusion remains `partial-inconclusive`;

- candidate metrics remain unavailable;

- Track 10 readiness remains not-ready;

- accepted memory evidence remains unchanged;

- no project runtime dependency exists;

- no artifact exists in Git;

- candidate selection remains no-selection;

- calibration remains not approved;

- comparison winner remains null;

- `productionReady` remains false;

- no sibling repository is nested in the Git tree.

If any material assumption is false, stop.

## Allowed Change Surface

Permitted:

- `docs/specs/intelligence-track-10.md`;

- candidate-disposition architecture;

- schema-invariant review;

- response-evidence review;

- proportionality analysis;

- six-run diagnostic authorization boundary;

- full-corpus continuation analysis;

- stop-investment analysis;

- candidate-disposition records;

- closed schemas;

- validation modules;

- deterministic decision tests using synthetic records;

- CLI validators;

- Repository Contracts updates;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, and governance documentation.

Not permitted:

- candidate execution;

- creation of an execution or diagnostic plan;

- creation of a plan digest;

- operator approval;

- result-root creation;

- artifact acquisition or mutation;

- historical-result mutation;

- project runtime installation;

- template, prompt, response-schema, corpus, metric, gate, decoding, or limit changes;

- conversion or quantization;

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

│   ├── [attributed-schema-failure-review.md](http://attributed-schema-failure-review.md)

│   ├── [six-run-diagnostic-boundary.md](http://six-run-diagnostic-boundary.md)

│   └── [candidate-investment-proportionality.md](http://candidate-investment-proportionality.md)

├── provenance/

│   └── [track10-candidate-disposition-review.md](http://track10-candidate-disposition-review.md)

├── operations/

│   └── [future-schema-diagnostic-prerequisites.md](http://future-schema-diagnostic-prerequisites.md)

└── specs/

	└── [intelligence-track-10.md](http://intelligence-track-10.md)

schemas/

├── attributed-response-evidence.schema.json

├── schema-invariant-review.schema.json

├── diagnostic-proportionality.schema.json

├── six-run-diagnostic-authorization.schema.json

├── investment-stop-decision.schema.json

└── track10-candidate-disposition.schema.json

candidates/

└── authorization/

	├── attributed-response-evidence.json

	├── schema-invariant-review.json

	├── diagnostic-proportionality.json

	├── six-run-diagnostic-authorization.json

	├── investment-stop-decision.json

	└── track10-candidate-disposition.json

src/patchpilot_intelligence_evals/

├── attributed_response_[review.py](http://review.py)

├── schema_invariant_[review.py](http://review.py)

├── diagnostic_[proportionality.py](http://proportionality.py)

├── six_run_diagnostic_[authorization.py](http://authorization.py)

├── investment_stop_[decision.py](http://decision.py)

└── track10_candidate_[disposition.py](http://disposition.py)

tests/

├── test_attributed_response_[review.py](http://review.py)

├── test_schema_invariant_[review.py](http://review.py)

├── test_diagnostic_[proportionality.py](http://proportionality.py)

├── test_six_run_diagnostic_[authorization.py](http://authorization.py)

├── test_investment_stop_[decision.py](http://decision.py)

└── test_track10_candidate_[disposition.py](http://disposition.py)

```

Exact names may differ only to follow established repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and records for:

1. attributed response evidence;

2. schema-invariant review;

3. diagnostic proportionality;

4. six-run diagnostic authorization;

5. investment-stop decision;

6. Track 10 candidate disposition.

Every schema must:

- have a stable ID and explicit version;

- use `additionalProperties: false`;

- identify exact candidate, runtime, prompt, response-schema, and output identities;

- reference Track 9A stopped-attempt authority;

- reference all consumed historical plans;

- distinguish candidate response failure from execution stop;

- represent evidence completeness;

- represent the five decision alternatives;

- prohibit an operational plan digest;

- prohibit operator approval;

- prohibit a result root;

- prohibit execution instructions;

- prohibit absolute external paths;

- prohibit secrets and host identity;

- preserve `selectionOutcome: no-selection`;

- preserve `calibrationStatus: not-approved`;

- preserve `comparisonWinner: null`;

- preserve `productionReady: false`;

- support every permitted Track 10 disposition.

The six-run authorization record may authorize only a future Session in principle.

## Evidence Decision Rules

### Attributed response review

The record must validate:

- raw-output identity;

- extracted-output identity;

- parsing success;

- schema failure;

- exact missing fields;

- exact unexpected fields;

- truncation false;

- output limit not exceeded;

- adapter preservation;

- prompt-contract presence;

- evaluator-schema identity;

- candidate-output authority.

### Schema-invariant review

The record must identify:

- schema-validity requirement source;

- whether one invalid run is an invariant failure;

- whether a full result set is required;

- whether repetition or percentage authority applies;

- whether rejection is currently supported;

- what additional evidence, if any, is required.

### Six-run authorization

If authorized in principle, the record must require:

- six corpus categories;

- one committed representative case-selection rule per category;

- one repetition per selected case;

- six total runs;

- same verified artifacts;

- same prompt and schema;

- same decoding and output limits;

- same hardened boundary;

- no memory rerun;

- bounded raw-output retention;

- extraction, parse, schema, truncation, and output-limit diagnostics;

- per-run failure attribution;

- new specification;

- new plan digest;

- fresh result root;

- new operator approval;

- no automatic candidate selection.

### Candidate disposition

Permitted values:

- `candidate-rejected`;

- `evaluation-incomplete-six-run-diagnostic-authorized-in-principle`;

- `full-corpus-continuation-authorized-in-principle`;

- `further-investment-stopped`;

- `blocked-by-unresolved-authority`.

## Multi-Agent Execution Model

Cursor Plan is the parent Track 10 review orchestrator.

Use Grok 4.7 Extra High for:

- evidence authority;

- candidate-versus-infrastructure attribution;

- schema-invariant interpretation;

- diagnostic design;

- proportionality;

- stopping criteria;

- candidate disposition;

- conflict resolution;

- independent verification.

Delegate read-only analysis and controlled implementation to:

### Agent 1: Response-evidence specialist

Owns raw-output identity, extraction, parsing, schema errors, adapter preservation, prompt authority, evaluator authority, and candidate-output attribution.

### Agent 2: Schema-authority specialist

Owns candidate protocol, response schema, invariant gates, percentage gates, repetition authority, and rejection criteria.

### Agent 3: Diagnostic-design specialist

Owns the six-category sample boundary, representative-case selection authority, raw-output requirements, decision rules, and future operator boundary.

### Agent 4: Full-corpus alternative specialist

Owns complete-corpus cost, comparability, expected metric value, and whether a 72-run rerun is proportionate.

### Agent 5: Proportionality specialist

Owns program cost, evidence value, infrastructure maturity, security risk, opportunity cost, memory residual, and stopping criteria.

### Agent 6: Disposition specialist

Owns the selected alternative, frozen authority, future Session boundary, and candidate disposition.

### Agent 7: Independent verifier

Runs after implementation.

Must not own response review, schema review, diagnostic design, full-corpus analysis, proportionality, or disposition.

### Coordination Rules

The parent must:

- perform no candidate execution;

- use committed evidence only;

- require exact identities;

- distinguish fact from recommendation;

- assign exclusive file ownership;

- prevent unsupported rejection;

- prevent unbounded continuation;

- integrate centrally;

- commission a fresh independent verifier.

Every specialist must return:

- findings;

- exact supporting records;

- evidence class;

- supported conclusions;

- unsupported conclusions;

- residual uncertainty;

- recommendation;

- owned files;

- tests required.

## Ordered Execution Plan

### Task 1: Verify the Post-Track-9A Baseline

#### Allowed files or subsystem

Read-only Git state, Track 8A through Track 9A records, schemas, workflows, tests, architecture, provenance, and authority.

#### Required behavior

Confirm every assumed-state item.

Record:

- synchronized `main`;

- Track 9A plan disposition;

- exact raw and extracted output identities;

- exact schema-forensics identity;

- exact memory evidence identity;

- exact readiness and implementation-review identities;

- file ownership for Tasks 2 through 8.

#### Tests

Run existing validators and digest checks only.

#### Done condition

The baseline is proven and no execution or external mutation occurred.

### Task 2: Build the Attributed Response-Evidence Record

#### Allowed files or subsystem

Response-evidence schema and record, validation module, CLI, documentation, and tests.

#### Required behavior

Represent the complete evidence chain from raw output through schema validation.

Keep execution-stop authority separate.

#### Tests

Validate exact identities, errors, authority classification, and evidence completeness.

#### Done condition

One authoritative attributed-response record exists.

### Task 3: Review Schema and Gate Authority

#### Allowed files or subsystem

Schema-invariant record, protocol and gate analysis, validator, documentation, and tests.

#### Required behavior

Determine whether one schema-invalid response is sufficient for rejection under existing authority.

Do not create a new rule.

#### Tests

Cover:

- single-run mandatory failure;

- percentage-gate requirement;

- repetition requirement;

- incomplete evidence;

- supported rejection;

- unsupported rejection.

#### Done condition

The rejection authority is explicit.

### Task 4: Evaluate the Six-Run Diagnostic Alternative

#### Allowed files or subsystem

Diagnostic architecture, authorization schema and record, deterministic selection rules, documentation, and tests.

#### Required behavior

Define whether one future case from each corpus category can determine if schema-invalid behavior is systematic.

Specify decision-grade evidence and future review rules.

Do not select operational case IDs or create a plan.

#### Tests

Validate six-category completeness, one repetition, unchanged protocol, raw-output requirements, and no operational authority.

#### Done condition

The diagnostic alternative is precisely bounded.

### Task 5: Evaluate the Full-Corpus and Stop Alternatives

#### Allowed files or subsystem

Proportionality record, full-corpus analysis, investment-stop record, documentation, and tests.

#### Required behavior

Compare:

- six-run diagnostic;

- full 72-run rerun;

- rejection now;

- protocol forensics;

- stopping investment.

Use closed categorical values.

#### Tests

Validate alternatives, trade-offs, and unsupported claims.

#### Done condition

The proportionality decision is reproducible.

### Task 6: Authorize or Withhold a Future Diagnostic Session

#### Allowed files or subsystem

Six-run authorization record, future prerequisites, validator, and tests.

#### Required behavior

Authorize only in principle when justified.

Require a later specification, new digest, fresh root, operator approval, and unchanged protocol.

Do not create any operational artifact.

#### Tests

Validate authorization and withholding paths.

#### Done condition

Future diagnostic authority is tightly bounded or withheld.

### Task 7: Record Candidate Disposition

#### Allowed files or subsystem

Disposition schema and record, decision module, CLI, documentation, and tests.

#### Required behavior

Record exactly one permitted disposition.

Preserve:

- `selectionOutcome: no-selection`;

- `calibrationStatus: not-approved`;

- `comparisonWinner: null`;

- `productionReady: false`.

#### Tests

Validate all dispositions and contradictory-authority rejection.

#### Done condition

Track 10 has a durable recommendation.

### Task 8: Documentation, Repository Contracts, and Independent Verification

#### Allowed files or subsystem

README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, workflows, tests, and complete diff.

#### Required behavior

Document:

- attributed response;

- schema authority;

- alternatives;

- proportionality;

- diagnostic boundary;

- candidate disposition;

- frozen authority.

Update Repository Contracts.

CI remains inference-free and artifact-free.

A fresh verifier must confirm no execution, no external mutation, exact evidence identities, valid decision rules, and no broadened authority.

#### Tests

Run every command in Verification.

#### Done condition

Track 10 is ready for Principal Architect review.

## Out of Scope

Track 10 must not:

- execute a candidate;

- create a diagnostic or evaluation plan;

- create a plan digest;

- create operator approval;

- create a result root;

- acquire or modify artifacts;

- modify historical evidence;

- change prompts, schema, decoding, corpus, metrics, gates, limits, or calibration;

- install dependencies;

- convert or quantize;

- select a candidate;

- integrate with PatchPilot;

- authorize shadow mode;

- change GitHub settings;

- publish, release, or deploy.

## Stop Conditions

Stop and report if:

1. Specification parent differs from `origin/main`.

2. Working tree contains unrelated changes.

3. Track 9A is not merged.

4. Track 9A plan is reusable.

5. A replacement plan exists.

6. Raw or extracted output identity differs.

7. Response-forensics authority differs.

8. Memory evidence differs.

9. Historical external evidence changed.

10. Analysis requires candidate execution.

11. Rejection requires inventing a new gate.

12. Diagnostic authority cannot remain separate from operational authority.

13. A future diagnostic cannot preserve the existing protocol.

14. Gold isolation cannot be guaranteed.

15. A sibling repository must be inspected.

16. Work cannot fit in one pull-request-sized branch.

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

- every Track 10 schema validation;

- every Track 10 record validation;

- response-evidence completeness tests;

- raw and extracted identity tests;

- authority-separation tests;

- schema-invariant tests;

- single-failure rejection tests;

- repetition and percentage-gate authority tests;

- six-category diagnostic tests;

- future-authorization boundary tests;

- full-corpus alternative tests;

- proportionality tests;

- stop-investment tests;

- disposition tests;

- contradictory-authority tests;

- no-operational-plan tests;

- documentation and relative-link checks;

- prohibited-artifact scan;

- no-execution validation;

- dependency and lockfile check;

- `git diff --check`;

- `git status --short --branch`.

Also confirm:

- no candidate execution occurred;

- no plan digest was created;

- no operator approval was created;

- no result root was created;

- no artifact changed;

- no project runtime dependency entered the repository;

- no conversion or quantization occurred;

- candidate selection remains `no-selection`;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false;

- no publication, release, or deployment occurred.

## Handoff Requirements

Return:

1. Outcome

2. Base commit, branch, and working-tree state

3. Multi-agent execution summary

4. Post-Track-9A baseline

5. Attributed response evidence

6. Raw and extracted identities

7. Adapter, protocol, evaluator, and prompt findings

8. Response-failure authority

9. Execution-stop authority

10. Schema requirement authority

11. Invariant-gate analysis

12. Percentage-gate analysis

13. Repetition authority

14. Whether one failure supports rejection

15. Alternative A analysis

16. Alternative B analysis

17. Alternative C analysis

18. Alternative D analysis

19. Alternative E analysis

20. Proportionality decision

21. Six-run diagnostic boundary

22. Future diagnostic authorization or withholding

23. Candidate disposition

24. Frozen authority

25. Files changed

26. Dependency and lockfile impact

27. Every verification command and result

28. CI changes

29. Independent verification

30. Scope compliance

31. Residual risks

32. Exact next recommendation

33. Proposed Conventional Commit

34. Proposed PR title and summary

35. Required post-merge steps

Final verdict must be exactly one of:

- `SIX-RUN DIAGNOSTIC AUTHORIZED IN PRINCIPLE`

- `FULL CORPUS CONTINUATION AUTHORIZED IN PRINCIPLE`

- `CANDIDATE REJECTED`

- `FURTHER INVESTMENT STOPPED`

- `BLOCKED BY UNRESOLVED AUTHORITY`

Explicitly confirm:

- no candidate execution occurred;

- no diagnostic or measurement plan was created;

- no execution-plan digest was issued;

- no operator approval was created;

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

`INTELLIGENCE TRACK 10 READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT`

or:

`INTELLIGENCE TRACK 10 BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW`