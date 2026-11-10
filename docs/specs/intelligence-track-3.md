Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 3: Offline Candidate Adapter and Evaluation Protocol

## Identity

- **Repository:** patchpilot-intelligence-evals

- **Session ID:** Intelligence Track 3

- **Mission:** Add a provider-neutral offline candidate protocol, bounded subprocess execution, deterministic candidate test doubles, reproducible evaluation artifacts, candidate comparison, and a calibration protocol for future real-model evaluation.

- **Base commit:** The parent of the spec-only commit introducing this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.

- **Expected repository state:** Intelligence Track 2 merged with 24 approved synthetic cases, five closed schemas, a deterministic baseline, explicit promotion gates, protected validation CI, and productionReady set to false.

- **Branch prefix:** feat/intelligence-track-3-candidate-protocol

- **Change type:** Offline evaluation infrastructure only.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, create a tag, publish a release, deploy, modify Git history, or change GitHub repository settings.

## Architectural Outcome

Intelligence Track 3 must establish a safe, reproducible boundary through which future candidate systems can be evaluated without entering PatchPilot production.

The completed repository must be able to:

1. Describe a candidate through a closed, versioned manifest.

2. Invoke a candidate through one provider-neutral protocol.

3. Run each invocation in a bounded child process.

4. Pass one validated synthetic evaluation input to the child process.

5. Receive one closed, schema-valid explanation response.

6. Enforce documented time, output-size, environment, working-directory, and network restrictions.

7. Distinguish candidate failure from evaluator or harness failure.

8. Record exact candidate, corpus, protocol, configuration, software, and execution identities.

9. Evaluate deterministic candidate fixtures through the approved 24-case synthetic corpus.

10. Preserve case-level and aggregate results as canonical evaluation artifacts.

11. Compare candidate results without silently changing promotion gates.

12. Calibrate evaluator sensitivity using conforming, unsafe, and operationally broken fixtures.

13. Support future offline real-model candidates without selecting, downloading, or executing one in this Session.

14. Keep productionReady false regardless of deterministic-fixture performance.

This Session must not compose any intelligence capability into PatchPilot.

## Repository Role

patchpilot-intelligence-evals remains the independent evaluation authority for original PatchPilot-specific:

- synthetic corpora;

- candidate protocols;

- schemas;

- manifests;

- deterministic test doubles;

- experiment manifests;

- offline evaluation harnesses;

- grounding and citation measurements;

- privacy and security evaluations;

- candidate comparisons;

- calibration records;

- model cards;

- promotion evidence.

The repository remains outside:

- PatchPilot runtime dependencies;

- PatchPilot build dependencies;

- PatchPilot Docker images;

- PatchPilot deployment;

- PatchPilot tenant-data workflows;

- neural-from-scratch;

- model-provider infrastructure.

## Governing Authority

Before editing, Cursor must reread:

- all repository [AGENTS.md](http://AGENTS.md) files;

- [README.md](http://README.md);

- [SECURITY.md](http://SECURITY.md);

- [CONTRIBUTING.md](http://CONTRIBUTING.md);

- NOTICE;

- LICENSE;

- .gitignore;

- pyproject.toml;

- uv.lock;

- the protected validation workflow;

- all documents under docs/architecture;

- all documents under docs/provenance;

- corpus/manifest.json;

- all existing corpus cases;

- all existing JSON Schemas;

- deterministic baseline implementation;

- evaluator and metrics implementation;

- schema-loading implementation;

- provenance implementation;

- network and sensitive-data protections;

- existing CLI;

- existing tests;

- Intelligence Track 2 specification;

- merged Intelligence Track 2 implementation evidence.

The following external architecture remains authoritative but must not be copied into this repository:

- PatchPilot deterministic authority over affectedness, Findings, KEV interpretation, P1-P4 priority, queue ordering, human review, and remediation state;

- PatchPilot Intelligence Track 1 boundaries;

- the independent educational role of neural-from-scratch.

Do not inspect local files in either sibling repository.

## Invariants

### No candidate authority

No candidate may become authoritative over:

- organization or tenant identity;

- asset identity;

- package identity;

- Product Match Evidence;

- affectedness;

- Finding creation;

- KEV membership;

- policy facts;

- P1-P4 priority;

- escalation;

- due-date recommendations;

- remediation-queue order;

- human priority review;

- Finding lifecycle;

- remediation completion;

- audit state.

The candidate protocol must contain no command for mutating those states.

Candidate responses remain advisory evaluation data.

### No real model during Intelligence Track 3

This Session must not:

- select a production model;

- download model weights;

- execute a real language model;

- contact a model provider;

- contact a model hub;

- add a hosted-provider SDK;

- add a local inference framework;

- add PyTorch;

- add Transformers;

- add TensorFlow;

- add JAX;

- add llama.cpp bindings;

- add an embedding system;

- add a vector database;

- add RAG;

- add fine-tuning;

- add LoRA;

- add preference optimization.

Only deterministic candidate fixtures and test doubles are authorized.

### Provider-neutral protocol

The core protocol must not depend on:

- one vendor;

- one model family;

- one inference library;

- one tokenizer;

- one prompt syntax;

- one model-download mechanism;

- one hosted API;

- one operating system beyond documented Python and subprocess requirements.

The protocol must support future:

- local candidates;

- self-hosted candidates;

- explicitly approved hosted candidates through a later adapter;

- deterministic test doubles;

- unavailable candidates;

- rejected candidates.

Hosted providers remain prohibited in this Session.

### One request, one response

Each candidate invocation must use:

- one canonical UTF-8 JSON request on standard input;

- one canonical UTF-8 JSON response on standard output;

- one process invocation per evaluation case;

- no interactive session;

- no streaming protocol;

- no shell interpolation;

- no automatic retry;

- no hidden provider-specific side channel.

Protocol noise or multiple response objects must fail closed.

### Process isolation

Candidate execution must occur outside the evaluator process through a child-process boundary.

The evaluator must enforce, where the supported platform permits:

- explicit executable and entry-point validation;

- an argument array with no shell;

- bounded wall-clock timeout;

- bounded standard output;

- bounded standard error;

- minimal environment allowlist;

- repository-contained working directory;

- no inherited secrets;

- deterministic exit-code capture;

- structured failure classification;

- termination on timeout;

- one request and one response per invocation;

- no writes outside explicit result directories.

The implementation and documentation must not claim full operating-system sandboxing.

The documentation must identify controls that require later operating-system isolation, including:

- process namespaces;

- seccomp;

- container isolation;

- cgroups;

- filesystem mount isolation;

- user-namespace isolation;

- operating-system outbound network enforcement.

### Offline execution

Candidate and evaluator execution must not require network access.

Tests and evaluation commands must not contact:

- GitHub;

- PyPI;

- CISA;

- OSV;

- npm;

- package registries;

- model hubs;

- hosted inference APIs;

- telemetry services;

- arbitrary URLs.

Dependency installation during environment construction is separate from evaluation execution.

Any observable candidate network attempt must be classified as a failure.

### Synthetic-only data

Only the approved synthetic corpus may be used.

No tenant, customer, employee, production, credential, SBOM, advisory-payload, private source-code, private prompt, or real Finding data may enter:

- candidate requests;

- candidate responses;

- fixtures;

- logs;

- result artifacts;

- comparison records;

- calibration records.

Cross-tenant negative controls must remain excluded from the authorized candidate context.

### Result integrity

Every evaluation result must identify:

- result schema version;

- protocol version;

- candidate manifest digest;

- candidate ID;

- candidate version;

- candidate kind;

- corpus version;

- corpus digest;

- experiment manifest digest;

- repository commit;

- evaluator version;

- Python version;

- operating-system description;

- execution timestamp;

- case-level execution outcomes;

- aggregate metrics;

- invariant-gate outcomes;

- percentage-gate outcomes;

- unmeasured metrics;

- execution-failure categories;

- productionReady: false.

Evaluation artifacts are research records. They are not PatchPilot audit records, Findings, Product Match Evidence, RiskCalculations, or priority reviews.

### Candidate provenance

Every executable candidate must have a manifest recording:

- stable candidate ID;

- candidate kind;

- candidate version;

- supported protocol version;

- implementation entry point;

- implementation digest;

- configuration digest;

- source;

- license;

- permitted use;

- prohibited use;

- execution requirements;

- expected determinism;

- network policy;

- data-retention policy;

- review status.

Deterministic fixtures must identify themselves as test doubles, not models.

### Immutable evaluation artifacts

Evaluation output must:

- be written only when the caller supplies an explicit output directory;

- use a path derived from stable experiment identity;

- refuse overwrite by default;

- use canonical JSON;

- include all required digests;

- avoid raw process environment values;

- avoid unnecessary complete prompt bodies;

- avoid secrets and sensitive data;

- remain distinguishable from source corpus data.

### Calibration integrity

Existing gates remain unchanged in this Session.

Calibration must not silently change:

- invariant gates;

- percentage thresholds;

- metric definitions;

- corpus taxonomy;

- promotion status.

Calibration records must distinguish:

- current gate definitions;

- conforming-fixture behavior;

- deliberately faulty-fixture behavior;

- evaluator sensitivity;

- potential false positives;

- potential false negatives;

- corpus blind spots;

- proposed future adjustments;

- Principal Architect approval status.

No proposed adjustment becomes authoritative during Intelligence Track 3.

## Assumed Repository State

Before editing, Cursor must prove:

- workspace root and Git root are patchpilot-intelligence-evals;

- local main equals origin/main;

- Intelligence Track 2 is merged;

- the spec-only commit parent equals origin/main;

- the working tree is clean after the spec-only commit;

- repository license is Apache-2.0;

- Python requirement remains &gt;=3.12,&lt;3.13;

- uv.lock exists and validates;

- protected validation workflow exists;

- exactly 24 synthetic cases exist;

- taxonomy counts remain:

  - 6 grounding and citation;

  - 4 insufficient-evidence and refusal;

  - 4 prompt-injection;

  - 4 cross-tenant negative-control;

  - 3 contradiction;

  - 3 stale, unavailable, or incomparable;

- corpus digest is 49fe79544a26de429afe865fbd2666828bf26a6da30efe6d87f3b0fdfbd0989c, unless synchronized main proves an authorized replacement digest;

- corpus review status records Principal Architect approval for harness and future offline-candidate evaluation;

- five closed Intelligence Track 2 JSON Schemas exist;

- deterministic baseline exists and remains non-authoritative;

- productionReady remains false;

- at least 43 tests pass on synchronized main;

- no real model dependency exists;

- no model weight exists;

- no provider SDK exists;

- no tenant or customer data exists;

- no sibling repository is nested in this Git tree;

- no PatchPilot production integration exists.

If a material assumption is false, stop and report the conflict.

## Allowed Change Surface

Permitted:

- docs/specs/[intelligence-track-3.md](http://intelligence-track-3.md);

- candidate-protocol architecture documentation;

- subprocess-isolation documentation;

- calibration-protocol documentation;

- result-retention documentation;

- candidate-manifest and fixture-provenance documentation;

- new closed JSON Schemas required by this Session;

- source modules implementing candidate manifests, protocol framing, subprocess execution, failure classification, result writing, comparison, and calibration;

- deterministic candidate fixtures;

- focused tests;

- CLI commands for candidate validation, execution, complete evaluation, result validation, comparison, and calibration;

- existing documentation files where required to describe the new evaluation boundary;

- existing validation workflow only to run newly authorized checks;

- pyproject.toml and uv.lock only if a narrowly necessary, non-model dependency is proven necessary and approved by repository rules.

Not permitted:

- changes to patchpilot;

- changes to neural-from-scratch;

- real model dependencies;

- real model weights;

- provider credentials;

- production prompts;

- tenant or customer data;

- external inference APIs;

- PatchPilot product integration;

- deployment;

- package publication;

- release creation.

## Required Repository Additions

The final repository should contain the conceptual equivalent of:

Exact file names may change only to follow existing repository conventions.

Do not create empty placeholders.

## **Multi-Agent Execution Model**

Cursor Plan is the lead orchestrator.

Use Grok 4.7 Extra High for:

- protocol architecture;
- subprocess security;
- manifest and schema decisions;
- failure taxonomy;
- calibration design;
- provenance review;
- conflict resolution;
- independent final verification.

Delegate parallel read-only investigation and controlled implementation to specialist agents.

### **Agent 1: Candidate-protocol specialist**

Owns:

- protocol framing;
- protocol versioning;
- request and response schemas;
- canonical JSON;
- standard-input and standard-output behavior;
- successful, unavailable, and rejected states;
- provider-neutral core fields.

### **Agent 2: Subprocess-security specialist**

Owns:

- direct executable invocation;
- shell avoidance;
- timeout enforcement;
- output limits;
- standard-error limits;
- environment allowlist;
- working-directory boundary;
- child termination;
- failure classification;
- platform-limit documentation.

### **Agent 3: Candidate-manifest and provenance specialist**

Owns:

- candidate-manifest schema;
- deterministic fixture manifests;
- implementation and configuration digests;
- entry-point validation;
- source and license fields;
- prohibited-use declarations;
- review status;
- fixture provenance record.

### **Agent 4: Deterministic-fixture specialist**

Owns:

1. conforming fixture;
2. unsupported-claim fixture;
3. prompt-injection-following fixture;
4. cross-tenant-leaking fixture;
5. timeout fixture;
6. malformed-output fixture;
7. excessive-output fixture;
8. nonzero-exit fixture.

Fixtures must be deterministic and must not be described as models.

### **Agent 5: Result and comparison specialist**

Owns:

- candidate-execution result records;
- stable experiment identity;
- immutable result paths;
- overwrite refusal;
- comparison schema;
- stable comparison behavior;
- result-retention policy.

### **Agent 6: Calibration specialist**

Owns:

- calibration records;
- fixture-to-gate mapping;
- threshold-boundary checks;
- evaluator sensitivity;
- false-positive and false-negative analysis;
- no-silent-gate-change rule.

### **Agent 7: Independent-verification specialist**

Runs after implementation.

Must not own:

- protocol schemas;
- manifest implementation;
- subprocess runner;
- fixture implementation;
- result storage;
- comparison;
- calibration.

### **Coordination rules**

The parent agent must:

- run read-only investigations in parallel;
- reconcile one architecture before edits;
- assign exclusive file ownership;
- prevent overlapping edits;
- sequence schemas before implementation;
- sequence protocol before fixtures;
- sequence candidate execution before comparison;
- sequence evaluation before calibration;
- integrate centrally;
- commission a fresh independent reviewer.

## **Ordered Execution Plan**

Cursor Plan must create one to-do for every task and execute them in order.

### **Task 1: Verify the Intelligence Track 2 Baseline**

#### **Allowed files or subsystem**

Read-only repository state, schemas, corpus, baseline, evaluator, workflow, documentation, CLI, and tests.

#### **Required behavior**

Confirm every assumed repository-state item.

Map:

- current CLI conventions;
- schema-loading conventions;
- canonical JSON behavior;
- experiment-manifest behavior;
- evaluation-result behavior;
- network guard;
- sensitive-data checks;
- logging behavior;
- promotion-gate representation;
- current workflow commands;
- exact file ownership for Tasks 2 through 8.

#### **Tests**

Run safe Git and repository inspection commands plus existing locked validation commands where necessary.

#### **Done condition**

The baseline is proven, no stop condition exists, and the parent agent has assigned exclusive file ownership.

### **Task 2: Define the Candidate Protocol and Closed Schemas**

#### **Allowed files or subsystem**

Candidate-protocol documentation, schema files, schema loader, examples, and focused tests.

#### **Required behavior**

Create closed, versioned JSON Schemas for:

1. candidate manifest;
2. candidate request;
3. candidate response;
4. candidate execution result;
5. calibration record;
6. comparison result.

The candidate request must contain:

- schema version;
- protocol version;
- request ID;
- case ID;
- authorized synthetic organization ID;
- validated Finding-explanation input;
- execution constraints;
- expected response-schema version.

The candidate response must contain:

- schema version;
- protocol version;
- request ID;
- candidate ID;
- candidate version;
- status;
- validated Finding-explanation output for success;
- structured failure or refusal information when applicable;
- no authoritative state-mutation fields;
- no provider-specific fields in the core protocol.

The execution-result schema must distinguish:

- success;
- candidate rejection;
- candidate unavailable;
- timeout;
- malformed output;
- multiple outputs;
- schema-invalid output;
- output limit exceeded;
- standard-error limit exceeded;
- nonzero exit;
- protocol mismatch;
- request-ID mismatch;
- candidate-identity mismatch;
- network-policy failure;
- internal harness failure.

#### **Tests**

Prove:

- valid examples pass;
- unknown properties fail;
- missing fields fail;
- protocol mismatch fails;
- response request ID must match;
- candidate identity must match the manifest;
- state-mutation fields fail;
- malformed and multiple outputs fail;
- provider-specific fields in the core protocol fail;
- every schema has a stable ID and explicit version.

#### **Done condition**

The protocol is closed, versioned, provider-neutral, and incapable of authorizing PatchPilot state mutation.

### **Task 3: Implement Candidate Manifests and Provenance**

#### **Allowed files or subsystem**

Manifest loader, manifest validation, fixture manifests, provenance record, and focused tests.

#### **Required behavior**

Implement:

- canonical manifest serialization;
- stable manifest digest;
- stable implementation digest;
- stable configuration digest;
- entry-point validation;
- executable allowlist;
- repository-contained relative paths;
- license field;
- source field;
- candidate kind;
- determinism declaration;
- network declaration;
- data-retention declaration;
- permitted use;
- prohibited use;
- review status;
- protocol compatibility.

Reject:

- path traversal;
- absolute paths outside the repository;
- sibling-repository paths;
- shell strings;
- ambiguous executable commands;
- missing license;
- missing provenance;
- unsupported protocol versions;
- provider credentials;
- unreviewed network requirements;
- candidate kinds not authorized by this Session.

#### **Tests**

Prove:

- valid fixture manifests pass;
- manifest digest is stable;
- traversal fails;
- external absolute path fails;
- sibling path fails;
- shell interpolation fails;
- missing provenance fails;
- missing license fails;
- unsupported protocol fails;
- real-model or provider claims fail under the authorized candidate-kind vocabulary.

#### **Done condition**

Every committed executable candidate has a validated, reproducible, provenance-bound manifest.

### **Task 4: Implement the Bounded Candidate Runner**

#### **Allowed files or subsystem**

Candidate runner, protocol transport, failure taxonomy, process controls, network guard integration, and tests.

#### **Required behavior**

Run one candidate invocation through a subprocess boundary.

Use:

- direct argument arrays;
- no shell;
- canonical request JSON on standard input;
- one response JSON on standard output;
- bounded wall-clock time;
- bounded stdout;
- bounded stderr;
- minimal environment;
- repository-contained working directory;
- stable failure categories;
- child termination on timeout;
- zero automatic retries;
- no inherited secrets;
- no writes outside explicitly permitted paths.

Default limits:

- 15-second wall-clock timeout;
- 64 KiB maximum standard output;
- 16 KiB maximum standard error;
- one process per case;
- zero retries.

These values are evaluation limits, not production service-level objectives.

The runner must avoid loading candidate code into the evaluator process.

#### **Tests**

Prove:

- successful invocation;
- timeout;
- nonzero exit;
- malformed JSON;
- multiple response objects;
- oversized stdout;
- oversized stderr;
- protocol mismatch;
- response-ID mismatch;
- candidate-identity mismatch;
- schema-invalid response;
- environment minimization;
- shell metacharacters remain inert;
- repository working-directory confinement;
- attempted network access fails where observable;
- input remains unchanged;
- failure records do not expose complete prompt contents by default.

#### **Done condition**

The runner executes deterministic fixtures reproducibly and classifies failures without weakening the offline boundary.

### **Task 5: Add Deterministic Candidate Fixtures**

#### **Allowed files or subsystem**

Fixture executables, manifests, fixture provenance, and focused tests.

#### **Required behavior**

Create these fixtures:

1. **Conforming fixture**  
  

   - emits supported claims only;
   - uses authorized citations;
   - refuses when required;
   - ignores embedded prompt injection;
   - excludes cross-tenant negative controls;
   - contains no state mutation.
2. **Unsupported-claim fixture**  
  

   - remains schema-valid;
   - deliberately emits unsupported claims;
   - fails unsupported-claim gates.
3. **Prompt-injection-following fixture**  
  

   - deliberately follows embedded malicious instructions;
   - fails prompt-injection gates.
4. **Cross-tenant-leaking fixture**  
  

   - deliberately emits a negative-control tenant fact;
   - fails the cross-tenant invariant.
5. **Timeout fixture**  
  

   - exceeds the authorized timeout.
6. **Malformed-output fixture**  
  

   - emits invalid JSON or an invalid response frame.
7. **Excessive-output fixture**  
  

   - exceeds the output limit.
8. **Nonzero-exit fixture**  
  

   - exits with a stable nonzero code.

Fixtures must:

- use no model or ML terminology suggesting trained intelligence;
- use no network;
- use no secrets;
- use no environment-dependent behavior;
- remain original repository code;
- have explicit provenance;
- produce stable results.

#### **Tests**

Prove:

- conforming fixture passes intended harness gates;
- every unsafe fixture fails its intended gate;
- every operational fixture returns the intended execution category;
- fixtures do not cause unrelated failures;
- fixture outputs are byte-stable where applicable;
- fixture manifests and digests are stable.

#### **Done condition**

The harness demonstrates sensitivity to conforming, unsafe, leaking, malformed, and unavailable candidate behavior.

### **Task 6: Implement Candidate Evaluation and Durable Results**

#### **Allowed files or subsystem**

Evaluator integration, result store, experiment manifests, CLI, comparison, and tests.

#### **Required behavior**

Add CLI commands equivalent to:

- candidate manifest validation;
- one-case candidate execution;
- complete candidate evaluation;
- result validation;
- candidate comparison;
- calibration generation.

Complete evaluation must:

- validate the candidate manifest;
- validate requests and responses;
- execute one child process per case;
- preserve per-case execution outcomes;
- calculate existing metrics;
- distinguish execution failure from quality failure;
- preserve unmeasured metrics;
- record every required identity and digest;
- write artifacts only to an explicit output directory;
- refuse overwrite by default;
- use a stable path derived from experiment identity;
- emit canonical JSON;
- keep productionReady: false.

Result artifacts must not contain:

- environment dumps;
- credentials;
- complete unauthorized context;
- cross-tenant controls outside failure evidence;
- unnecessary full input or output bodies.

Candidate comparison must:

- require compatible corpus and metric definitions;
- retain candidate identities;
- report incomparable results explicitly;
- avoid ranking candidates when identity or corpus compatibility fails;
- use deterministic ordering;
- avoid declaring a production winner.

#### **Tests**

Prove:

- conforming complete evaluation;
- every faulty-fixture evaluation;
- stable experiment ID;
- stable result paths;
- overwrite rejection;
- canonical result stability;
- compatible comparison;
- incompatible comparison rejection;
- missing result handling;
- invalid manifest rejection;
- partial execution failure handling;
- no production-readiness claim.

#### **Done condition**

The repository can evaluate, persist, validate, and compare deterministic candidates reproducibly.

### **Task 7: Implement Calibration Protocol**

#### **Allowed files or subsystem**

Calibration module, calibration schema integration, CLI, architecture document, and tests.

#### **Required behavior**

Generate a calibration record from deterministic fixtures.

The process must:

- verify every invariant gate detects its intended failure;
- verify percentage metrics detect faulty outputs;
- test exact threshold boundaries;
- identify metrics insufficiently exercised by 24 cases;
- identify corpus imbalance;
- identify evaluator blind spots;
- record potential false positives;
- record potential false negatives;
- propose future adjustments without adopting them;
- preserve current gates unchanged;
- keep productionReady: false;
- identify prerequisites for a future real offline candidate.

The calibration record must not authorize:

- a model;
- a provider;
- shadow mode;
- production composition;
- a gate change.

#### **Tests**

Prove:

- expected fixture-to-gate mapping;
- invariant sensitivity;
- percentage-boundary behavior;
- zero-denominator handling;
- unmeasured behavior;
- stable calibration record;
- no silent threshold modification;
- no production-ready outcome.

#### **Done condition**

The repository contains a reproducible evaluator-calibration protocol without pretending fixtures prove real-model quality.

### **Task 8: Documentation, CI, and Independent Verification**

#### **Allowed files or subsystem**

README, architecture documents, provenance documents, SECURITY, AGENTS, CONTRIBUTING, validation workflow, complete repository diff.

#### **Required behavior**

Document:

- candidate protocol;
- manifest contract;
- subprocess boundary;
- platform limitations;
- fixture purpose;
- result layout;
- overwrite behavior;
- comparison semantics;
- calibration semantics;
- offline requirements;
- commands;
- no-production-composition boundary;
- Intelligence Track 4 prerequisites.

Update protected validation CI to run:

- uv sync --frozen;
- Ruff format;
- Ruff lint;
- mypy;
- pytest;
- corpus validation;
- baseline evaluation;
- candidate-manifest validation;
- conforming candidate evaluation;
- faulty-fixture checks;
- calibration validation.

Do not upload complete candidate requests or responses as workflow artifacts.

Assign final verification to a fresh agent that did not own protocol, runner, fixtures, result store, comparison, or calibration.

#### **Tests**

Run every command in the Verification section.

#### **Done condition**

The candidate boundary is documented, reproducible, protected by CI, independently verified, and ready for Principal Architect review.

## **Out of Scope**

Intelligence Track 3 must not:

- modify patchpilot;
- modify neural-from-scratch;
- inspect local sibling-repository files;
- add a real model;
- download weights;
- use a model hub;
- add PyTorch;
- add Transformers;
- add TensorFlow;
- add JAX;
- add llama.cpp;
- add hosted-provider SDKs;
- add API keys;
- add hosted inference;
- add real local-model inference;
- add embeddings;
- add a vector database;
- add RAG;
- add fine-tuning;
- add LoRA;
- add preference optimization;
- add autonomous agents;
- add tool execution;
- use tenant data;
- use customer data;
- use real SBOMs;
- use raw advisory payloads;
- create a PatchPilot API route;
- create a PatchPilot UI;
- create a production service;
- add a database;
- publish a Python package;
- create a release;
- deploy;
- claim real-model quality;
- claim production readiness.

## **Stop Conditions**

Stop and report if:

1. The spec-only commit parent does not equal origin/main.
2. The working tree contains unrelated changes.
3. Intelligence Track 2 is not merged.
4. Corpus count or taxonomy differs without accepted authority.
5. Corpus digest differs without an accepted corpus revision.
6. Review status does not authorize offline-candidate evaluation.
7. A real-model dependency appears necessary.
8. Network access appears necessary for evaluation.
9. Tenant or customer data appears necessary.
10. A subprocess boundary cannot avoid shell execution.
11. Candidate execution requires unrestricted environment inheritance.
12. Candidate execution requires paths outside this repository.
13. A protocol field would grant authoritative PatchPilot mutation.
14. Result persistence requires a database.
15. Calibration requires silently changing gates.
16. A fixture cannot remain deterministic.
17. A security claim would exceed actual process isolation.
18. A new dependency is required without a clear license and security disposition.
19. Work cannot fit in one pull-request-sized branch.
20. Either sibling repository is accessed locally or appears in the change set.

On a stop condition:

- make no speculative workaround;
- do not weaken security or provenance;
- do not broaden scope;
- cite the conflict;
- identify the smallest required decision;
- return the conflict for Principal Architect review.

## **Verification**

Pass requires:

- uv sync --frozen;
- uv run ruff format --check .;
- uv run ruff check .;
- uv run mypy src tests;
- uv run pytest;
- uv run patchpilot-evals corpus-validation;
- uv run patchpilot-evals baseline-evaluation;
- candidate-manifest validation for every committed fixture;
- conforming-candidate complete evaluation;
- unsupported-claim fixture evaluation;
- prompt-injection fixture evaluation;
- cross-tenant fixture evaluation;
- timeout fixture execution;
- malformed-output fixture execution;
- excessive-output fixture execution;
- nonzero-exit fixture execution;
- candidate-comparison validation;
- calibration-record generation and validation;
- schema validation for every committed JSON file;
- manifest and digest validation;
- network-guard tests;
- environment-minimization tests;
- timeout and output-limit tests;
- cross-tenant failure tests;
- prompt-injection failure tests;
- unsupported-claim failure tests;
- deterministic-replay tests;
- result-overwrite tests;
- documentation and relative-link checks;
- license and provenance checks;
- workflow validation;
- git diff --check;
- git status --short --branch.

Also confirm:

- no real model was downloaded or executed;
- no provider or model hub was contacted;
- no tenant or customer data was used;
- no sibling repository was accessed;
- no PatchPilot production integration was created;
- no package was published;
- no release or deployment occurred;
- productionReady remains false.

Recommended Conventional Commit:

feat(evals): add offline candidate protocol

Do not create the commit automatically.

## **Handoff Requirements**

Return one consolidated handoff containing:

1. Outcome
2. Base commit, branch, and working-tree state
3. Multi-agent execution summary
4. Intelligence Track 2 baseline
5. Candidate protocol
6. Candidate schemas
7. Candidate manifest and provenance
8. Subprocess isolation
9. Isolation limits
10. Failure taxonomy
11. Deterministic fixtures
12. Candidate evaluation
13. Durable result records
14. Comparison behavior
15. Calibration protocol
16. Calibration findings
17. Security and offline controls
18. Files changed
19. Dependency and license impact
20. Every verification command and actual result
21. CI workflow changes
22. Independent verification findings
23. Scope compliance
24. Unresolved decisions
25. Residual risks
26. Proposed Conventional Commit
27. Proposed pull-request title and summary
28. Recommended Intelligence Track 4 prerequisites

Final verdict:

- OFFLINE CANDIDATE PROTOCOL READY FOR PRINCIPAL REVIEW
- OFFLINE CANDIDATE PROTOCOL READY WITH DOCUMENTED RESIDUALS
- OFFLINE CANDIDATE PROTOCOL NOT READY
- BLOCKED BY UNRESOLVED AUTHORITY

Explicitly confirm:

- no real model was downloaded or executed;
- no provider or model hub was contacted;
- no tenant or customer data was used;
- no sibling repository was accessed or modified;
- no PatchPilot production integration was created;
- no automatic commit or push occurred;
- no pull request was created automatically;
- no package was published;
- no release or deployment occurred;
- productionReady remains false.

End with exactly one:

INTELLIGENCE TRACK 3 READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT

or:

INTELLIGENCE TRACK 3 BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW