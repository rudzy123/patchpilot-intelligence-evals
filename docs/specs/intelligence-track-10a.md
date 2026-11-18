Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this specification, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 10A: Six-Run Cross-Category Schema Diagnostic

## Identity

- **Repository:** `patchpilot-intelligence-evals`

- **Session ID:** Intelligence Track 10A

- **Mission:** Execute one bounded six-run diagnostic using one deterministically selected case from each committed corpus category to determine whether the verified candidate’s response-schema failure is systematic across categories under the unchanged authorized protocol.

- **Base commit:** The parent of the specification-only commit introducing this file. Before implementation, `git rev-parse HEAD^` must equal `git rev-parse origin/main`.

- **Expected repository state:** Intelligence Track 10 merged; six-run diagnostic authorized in principle; current operational execution authority false; no diagnostic plan digest, operator approval, result root, or operational case list exists; all historical plans remain consumed and non-reusable; candidate selection remains `no-selection`; calibration remains `not-approved`; comparison winner remains null; `productionReady` remains false.

- **Branch:** `feat/intelligence-track-10a-schema-diagnostic`

- **Change type:** New diagnostic plan, deterministic six-case selection, operator checkpoint, bounded raw-output retention, six serial candidate executions, immutable diagnostics, systematic-schema-failure decision, closeout, readiness, documentation, tests, and artifact-free CI validation.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Recommended commit:** `feat(evals): record cross-category schema diagnostic`

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, merge, modify Git history, change GitHub settings, publish, release, deploy, acquire or replace artifacts, install project dependencies, select the candidate, or promote the candidate automatically.

## Architectural Outcome

Track 10A must answer:

> Does the verified candidate systematically fail the authorized response-schema contract across materially different corpus categories?

The completed Session must determine:

1. Whether the exact verified candidate can return schema-valid output for each of the six committed corpus categories.

2. Whether schema-invalid output is repeated across categories.

3. Whether every schema failure is attributable to candidate output rather than the adapter, protocol, evaluator, truncation, output limits, security boundary, or infrastructure.

4. Whether a precommitted systematic-schema-failure threshold is met.

5. Whether systematic failure is not established.

6. Whether schema behavior remains unreliable or unresolved.

7. Whether another full corpus evaluation is proportionate.

8. Whether the candidate becomes eligible for rejection review.

9. Whether further investment should stop.

10. Whether a later candidate-disposition Session is ready.

The completed Session must:

1. Preserve all historical plans and result roots unchanged.

2. Preserve accepted memory evidence without rerunning context measurements.

3. Select exactly one case from each committed corpus category using a deterministic committed rule.

4. Plan exactly six serial executions.

5. Use one repetition per selected case.

6. Use zero retries.

7. Use the exact verified runtime and candidate.

8. Use the unchanged publisher template, prompt template, response schema, decoding configuration, resource limits, and hardened boundary.

9. Create one new diagnostic plan and canonical digest.

10. Create one fresh empty external result root.

11. Require explicit operator approval before the first candidate execution.

12. Retain bounded immutable raw output for every execution.

13. Record extraction, parsing, schema validation, truncation, output-limit behavior, evidence-ID findings, and failure authority independently.

14. Use the precommitted systematic-failure threshold.

15. Stop on the first blocking security, identity, isolation, memory, telemetry, output-retention, or cleanup failure.

16. Preserve candidate-attributed malformed output as measured evidence without automatically stopping later diagnostic runs.

17. Produce an immutable diagnostic summary and closeout.

18. Preserve `selectionOutcome: no-selection`.

19. Preserve `calibrationStatus: not-approved`.

20. Preserve `comparisonWinner: null`.

21. Preserve `productionReady: false`.

Track 10A authorizes the six diagnostic executions only after its operator checkpoint is approved.

It does not authorize a full corpus evaluation, candidate selection, PatchPilot integration, shadow mode, release, deployment, or production use.

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

- every current architecture, provenance, operations, authorization, defect, closeout, readiness, disposition, and implementation-review record;

- every current JSON Schema;

- candidate protocol and subprocess contracts;

- immutable result-storage contract;

- response-schema authority;

- comparison and calibration contracts;

- current corpus, metrics, and promotion gates;

- Track 4 candidate mandatory criteria and scoring authority;

- Track 6A hardened execution profile;

- Track 6B corrected ONNX adapter;

- Track 7 finalist and no-selection records;

- Track 7A storage and atomic-promotion records;

- Track 7B memory and suitability contracts;

- Track 8A acquisition, artifact identities, load proof, and closeout;

- Track 8B, Track 8B-R1, and Track 8B-R2 execution evidence and reviews;

- Track 9 evidence review and continuation authorization;

- Track 9A stopped continuation, raw-output evidence, telemetry correction, response attribution, and implementation review;

- Track 10 attributed-response review, schema-authority review, proportionality decision, six-run authorization, candidate disposition, and implementation review;

- current CLI commands and tests;

- Intelligence Track 2 through Track 10 specifications;

- synchronized protected-CI evidence from `main`.

Do not inspect or modify `patchpilot` or `neural-from-scratch`.

Do not perform new public model, candidate, or runtime research.

## Authorized External Identities

Track 10A must derive the complete file-level identities from committed Track 8A authority.

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

Every promoted file and template identity must match before execution.

## Historical Plan Authority

These plans remain consumed and non-reusable:

- Track 8B:

  `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2`

- Track 8B-R1:

  `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b`

- Track 8B-R2:

  `2133054bea8db11822cc65f6ea9c45f1ba1500f1aef67d314fbccca764155350`

- Track 9A:

  `6c4a9e6c64a3afe3c1cbb36d19985880beb067fdb9b5634752e8c4d1482560f1`

Track 10A must not reuse, alter, append to, or reinterpret any historical plan or result root.

## Track 10 Authority

Track 10 authorized a six-run diagnostic in principle.

The Track 10 implementation-review digest is:

`b609cb2eb63ddfc998ec95757ea2423f033f876657b8ce0ed7ce4e5702638a28`

Before Track 10A execution, the committed six-run authorization record must validate and must state:

- current operational execution authority before Track 10A approval: false;

- selected alternative: six-run diagnostic;

- future plan digest: not-issued;

- operator approval: not-issued;

- result root: not-created;

- operational case IDs: not-selected;

- candidate selection: no-selection;

- calibration: not-approved;

- comparison winner: null;

- `productionReady: false`.

Track 10A may operationalize the in-principle authority only through the new specification, plan digest, result root, and operator checkpoint defined here.

## Accepted Memory Evidence

Track 10A must not rerun memory-context phases.

The accepted measurements are:

- 4,096-token cold peak: `7,284,371,456` bytes

- 4,096-token warm peak: `8,511,131,648` bytes

- 8,192-token cold peak: `9,816,231,936` bytes

- 8,192-token warm peak: `12,271,669,248` bytes

- Resident ceiling: `12,884,901,888` bytes

- Minimum headroom: `613,232,640` bytes

- Memory conclusion: `within-ceiling-with-limited-headroom`

The diagnostic must preserve:

- one candidate process at a time;

- the approved thread configuration;

- the same cgroup ceiling;

- unchanged output limits;

- no larger context;

- no concurrent execution.

## Prior Candidate-Output Evidence

Track 10A must preserve the attributed Track 9A response evidence.

### Run identity

`case-ground-001-r1`

### Raw stdout

- Length: `542` bytes

- SHA-256:

  `b28e9aa7f5db74d23040d9b3045b5fc927bc2289378bb6bf676e4568ec20b0b9`

### Extracted response

- Length: `264` bytes

- SHA-256:

  `8d5acd633059fd19ea765c0ce415bb37d4f53cc02ed848fcf6df490d55ab9d5d`

### Result

- UTF-8: passed

- Extraction: passed

- JSON parse: passed

- Response-schema validation: failed

- Truncated: false

- Output limit exceeded: false

- Adapter inner-field mutation: false

- Response-failure authority: `candidate-output`

- Execution-stop authority: `measurement-infrastructure`

Unexpected candidate fields:

- `deterministicFacts`

- `findingExplanation`

The prior response is historical evidence. It must not be counted as one of the six Track 10A runs.

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

- remediation-queue ordering;

- review state;

- Finding lifecycle;

- remediation completion;

- PatchPilot audit state.

### Diagnostic purpose

The diagnostic has one primary question:

> Does the candidate emit schema-invalid output systematically across committed corpus categories under the unchanged authorized protocol?

Track 10A must not represent the six-run result as:

- a complete corpus evaluation;

- a calibrated percentage-gate evaluation;

- promotion-gate completion;

- candidate selection;

- a substitute for all 24 cases and three repetitions;

- a production-readiness evaluation.

### Deterministic case selection

Track 10A must select exactly one case from each committed corpus category using:

`minimum-case-id-within-committed-category`

The six committed categories are:

1. grounding and citation;

2. insufficient evidence and refusal;

3. prompt injection;

4. cross-tenant negative control;

5. contradiction;

6. stale, unavailable, or incomparable evidence.

Case selection must:

- use committed corpus taxonomy;

- use exact lexical ordering of committed case IDs within each category;

- produce exactly one unique case per category;

- produce exactly six unique case IDs;

- occur before plan digest generation;

- be represented in the plan;

- remain unchanged after operator approval.

The selection function must reject:

- missing categories;

- duplicate categories;

- duplicate selected case IDs;

- unsupported categories;

- uncommitted case IDs;

- a result other than exactly six cases.

### One repetition only

Each selected case receives exactly one execution.

Track 10A must not:

- run multiple repetitions;

- retry a failed execution;

- rerun a candidate-attributed malformed response;

- replace a selected case after execution begins;

- add another case to compensate for a blocked run.

### New diagnostic plan

Track 10A must create one closed plan containing:

- exact Track 10 authorization identity;

- all consumed historical-plan identities;

- exact artifact identities;

- exact six selected case IDs and categories;

- corpus digest;

- prompt-template digest;

- publisher-template digest;

- response-schema identity;

- decoding configuration;

- hardened-profile identity;

- raw-output retention policy;

- diagnostic pipeline;

- systematic-failure threshold;

- resource limits;

- run order;

- stop conditions;

- cleanup behavior;

- frozen authority fields.

The plan digest must be generated through the authoritative canonical function.

### Fresh result root

Track 10A must use one new result root that:

- is outside Git and sibling repositories;

- differs from every historical result root;

- is empty before execution;

- is mode `0700`;

- is operator-owned;

- is not a symlink;

- has sufficient capacity;

- rejects overwrite;

- contains only Track 10A records.

### Operator checkpoint

Before the first candidate execution, Cursor must present:

- Track 10 authorization identity;

- all historical-plan rejection results;

- new Track 10A plan digest;

- exact six selected case IDs and categories;

- recomputed runtime and candidate digests;

- tokenizer and publisher-template identities;

- template-compatibility result;

- authoritative dependency-closure record;

- exact-sandbox dynamic-link precheck result;

- corpus digest;

- prompt-template digest;

- response-schema identity;

- systematic-failure threshold;

- raw-output retention policy;

- diagnostic stages;

- result-root validation;

- hardened profile;

- decoding settings;

- memory and resource limits;

- timeout and output limits;

- stop and cleanup rules.

The human operator must explicitly approve the new plan digest.

No prior operator approval may be reused.

### Systematic-schema-failure threshold

Track 10A precommits the following threshold:

```text

systematicSchemaFailureEstablished:

  completedDiagnosticRuns == 6

  AND candidateOutputSchemaFailureCount >= 4

  AND distinctCategoriesWithCandidateOutputSchemaFailure >= 3

  AND every counted failure:

  	responseFailureAuthority == candidate-output

  	AND rawOutputRetained == true

  	AND extractionAuthorityEstablished == true

  	AND jsonParseAuthorityEstablished == true

  	AND intendedResponseSchemaApplied == true

  	AND adapterInnerFieldMutation == false

  	AND truncated == false

  	AND outputLimitExceeded == false

  	AND blockingInfrastructureExplanation == false

```

This threshold is fixed before execution and must not change after results are observed.

### Diagnostic outcomes

Track 10A must produce exactly one diagnostic conclusion.

#### Outcome A: `systematic-schema-failure-established`

Required:

- all six diagnostic runs completed and sealed;

- at least four candidate-output schema failures;

- failures span at least three corpus categories;

- every counted failure satisfies the committed attribution chain;

- no blocking infrastructure or security defect invalidates the diagnostic.

This makes candidate rejection eligible for the later disposition review. It does not automatically reject or select the candidate.

#### Outcome B: `systematic-schema-failure-not-established`

Required:

- all six diagnostic runs completed and sealed;

- zero or one qualifying candidate-output schema failure.

A later review may consider whether a complete corpus evaluation is proportionate.

#### Outcome C: `schema-behavior-unreliable-or-unresolved`

Use when:

- all six runs completed;

- two or three qualifying candidate-output schema failures occurred;

- or failures occurred but authority remained unresolved;

- or different malformed output shapes prevent a clear systemic conclusion.

A later Principal Architect review is required before further execution.

#### Outcome D: `diagnostic-incomplete`

Use when:

- fewer than six runs completed;

- a blocking infrastructure or security failure occurred;

- raw output could not be retained;

- telemetry was unresolved;

- a launch could not be sealed;

- any approved identity changed.

An incomplete diagnostic cannot establish or disprove systematic candidate failure.

### No new acquisition or mutation

Track 10A must not:

- acquire or replace runtime files;

- acquire or replace model files;

- retrieve missing files automatically;

- replace tokenizer, configuration, or template files;

- modify verified artifacts;

- change immutable revisions;

- install a project runtime dependency;

- convert or quantize;

- append another execution provider.

Any mismatch is a stop condition.

### Hardened execution

Every diagnostic run must use:

- `linux-bwrap-systemd-v1`;

- OS-level network denial;

- verified runtime and candidate roots mounted read-only;

- approved individual dependency mounts;

- private writable per-run result directory;

- minimal environment;

- no home, SSH, cloud, sibling, gold, evaluator, or prior-result visibility;

- direct argument vectors;

- no shell;

- `MemoryMax=12,884,901,888`;

- `MemorySwapMax=0`;

- `TasksMax=32`;

- `RLIMIT_AS=25,769,803,776`;

- intra-op threads `8`;

- inter-op threads `1`;

- CPU and wall-clock limits;

- stdout and stderr limits;

- complete process-tree cleanup.

No plain-subprocess fallback is permitted.

### Prompt and decoding identity

Use the committed prompt-template digest:

`62774d0f8b65c959c5b038911af4293d3d774aae3933f0d7a24064691685250a`

Use:

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

### Candidate isolation

A diagnostic run must not receive:

- prior candidate output;

- prior raw output;

- prior extraction or parser results;

- prior schema errors;

- prior scores;

- case labels beyond authorized input;

- expected citations;

- gold claims;

- evaluator metadata;

- hidden case metadata;

- cross-case controls.

Sealed output from one run must be unavailable to every later run.

### Bounded raw-output retention

Every run must retain before extraction:

- raw stdout bytes;

- raw stderr bytes;

- SHA-256 for each;

- byte length for each;

- UTF-8 status;

- truncation status;

- output-limit status.

The diagnostic pipeline must preserve separately:

1. raw output;

2. extracted response;

3. parsed JSON;

4. response-schema validation;

5. evidence-ID diagnostics;

6. failure-attribution evidence.

A later stage must not overwrite or erase evidence from an earlier stage.

### Failure authority

Every failed response must be classified as exactly one of:

- `candidate-output`;

- `adapter`;

- `protocol`;

- `evaluator`;

- `measurement-infrastructure`;

- `security-boundary`;

- `unresolved`.

Schema failure may be attributed to `candidate-output` only when:

- raw output is retained;

- the correct candidate object is extracted;

- JSON parsing preserves the emitted keys;

- the intended response schema is applied;

- the prompt contains the authorized response contract;

- the adapter did not rename, remove, or add candidate fields;

- output was not truncated;

- output limits were not exceeded;

- no infrastructure cause explains the shape.

### Cgroup telemetry

Every run must record:

- `memory.current`;

- `memory.peak`;

- `memory.events`;

- process RSS where observable;

- process-tree RSS where observable;

- virtual size where observable;

- child-active or child-exited state;

- post-exit scope status;

- cleanup status.

The corrected monotonic sampler must:

- preserve the last complete noncontradictory cgroup window;

- treat unavailable redundant post-exit reads as diagnostics;

- reject material contradictions;

- fail unresolved when no complete sample exists;

- classify active-child scope disappearance as infrastructure failure;

- create an unclassified-launch record when output exists but normal sealing cannot complete;

- never silently omit a launch.

### Stop behavior

Stop the diagnostic and withhold all later runs on:

- artifact digest mismatch;

- corpus, prompt, template, or schema identity mismatch;

- result-root reuse;

- operator-approval mismatch;

- dynamic-link or template precheck failure;

- unverified dependency;

- network violation;

- isolation failure;

- gold or evaluator visibility;

- prior-result visibility;

- OOM;

- cgroup peak above the ceiling;

- unresolved or contradictory telemetry;

- excessive output;

- inability to retain raw output;

- cleanup failure;

- overwrite attempt;

- unclassified launch;

- inability to seal a launch durably.

A candidate-attributed malformed or schema-invalid response is a valid diagnostic result and does not stop later diagnostic cases.

### Immutable records

Each diagnostic run record must include:

- Track 10A Session ID;

- plan digest;

- Track 10 authorization identity;

- case ID;

- corpus category;

- repetition `1`;

- runtime and candidate identities;

- artifact digests;

- corpus, prompt, template, and response-schema identities;

- decoding settings;

- resource limits;

- input digest;

- raw-output identities;

- extraction result;

- JSON parse result;

- schema result;

- failure authority;

- memory telemetry;

- timings;

- exit classification;

- network result;

- isolation result;

- cleanup result;

- repository commit;

- timestamp;

- frozen authority fields;

- `productionReady: false`.

Records must be overwrite-protected.

### No corpus scoring

Track 10A must not:

- calculate corpus-wide percentage metrics;

- score promotion gates;

- recalibrate thresholds;

- calculate a comparison winner;

- represent the six runs as a complete corpus;

- impute missing corpus cases.

Track 10A may calculate only the precommitted diagnostic counts and category coverage required by the systematic-failure threshold.

### No automatic rejection or selection

Regardless of diagnostic outcome:

- candidate rejection is not automatic;

- candidate selection remains `no-selection`;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false;

- no PatchPilot integration is authorized.

A later Principal Architect disposition review is required.

## Assumed Repository State

Before implementation, Cursor must prove:

- repository root is `patchpilot-intelligence-evals`;

- local `main` equals `origin/main`;

- Track 10 is merged;

- specification-only commit parent equals `origin/main`;

- working tree is clean after the specification commit;

- protected checks pass on synchronized `main`;

- Track 10 review digest validates;

- six-run diagnostic authority is `authorized-in-principle`;

- operational authority remains false before Track 10A approval;

- no diagnostic plan digest exists;

- no operator approval exists;

- no result root exists;

- operational case IDs remain unselected;

- every historical plan remains consumed and non-reusable;

- accepted memory evidence remains unchanged;

- Track 9A raw and extracted identities validate;

- response-failure authority remains `candidate-output`;

- execution-stop authority remains `measurement-infrastructure`;

- verified runtime and candidate roots remain available and unchanged;

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

- `docs/specs/intelligence-track-10a.md`;

- diagnostic execution architecture;

- deterministic case-selection implementation;

- new diagnostic-plan and operator-approval records;

- raw-output and diagnostic schemas;

- per-run evidence records;

- diagnostic summary, closeout, and readiness records;

- source modules for planning, preflight, selection, raw-output capture, extraction, parsing, schema diagnostics, failure attribution, diagnostic execution, threshold evaluation, closeout, and readiness;

- one new external result root;

- focused tests;

- manually invoked diagnostic commands;

- Repository Contracts updates;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, operations, and governance documentation;

- `.gitignore` for local diagnostic metadata.

Not permitted:

- memory-context reruns;

- qualification smoke or short-generation reruns;

- full 24-case corpus execution;

- multiple repetitions;

- retries;

- artifact acquisition or replacement;

- historical-result mutation;

- project runtime installation;

- template replacement;

- prompt, response-schema, decoding, corpus, metric, gate, threshold, or limit changes after plan approval;

- conversion or quantization;

- candidate rejection or selection;

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

│   ├── [six-run-schema-diagnostic.md](http://six-run-schema-diagnostic.md)

│   ├── [diagnostic-case-selection.md](http://diagnostic-case-selection.md)

│   └── [systematic-schema-failure.md](http://systematic-schema-failure.md)

├── operations/

│   ├── [schema-diagnostic-runbook.md](http://schema-diagnostic-runbook.md)

│   ├── [schema-diagnostic-recovery.md](http://schema-diagnostic-recovery.md)

│   └── [schema-diagnostic-retention.md](http://schema-diagnostic-retention.md)

├── provenance/

│   └── [track10a-schema-diagnostic-evidence.md](http://track10a-schema-diagnostic-evidence.md)

└── specs/

	└── [intelligence-track-10a.md](http://intelligence-track-10a.md)

schemas/

├── schema-diagnostic-plan.schema.json

├── schema-diagnostic-approval.schema.json

├── schema-diagnostic-preflight.schema.json

├── schema-diagnostic-run.schema.json

├── schema-diagnostic-summary.schema.json

├── schema-diagnostic-closeout.schema.json

└── track11-readiness.schema.json

candidates/

├── authorization/

│   ├── schema-diagnostic-plan.json

│   ├── schema-diagnostic-approval.json

│   └── track11-readiness.json

└── templates/

	├── schema-diagnostic-preflight-template.json

	├── schema-diagnostic-run-template.json

	├── schema-diagnostic-summary-template.json

	└── schema-diagnostic-closeout-template.json

src/patchpilot_intelligence_evals/

├── schema_diagnostic_[plan.py](http://plan.py)

├── diagnostic_case_[selection.py](http://selection.py)

├── schema_diagnostic_[preflight.py](http://preflight.py)

├── schema_diagnostic_[execution.py](http://execution.py)

├── schema_diagnostic_[summary.py](http://summary.py)

├── schema_diagnostic_[closeout.py](http://closeout.py)

└── track11_[readiness.py](http://readiness.py)

tests/

├── test_schema_diagnostic_[plan.py](http://plan.py)

├── test_diagnostic_case_[selection.py](http://selection.py)

├── test_schema_diagnostic_[preflight.py](http://preflight.py)

├── test_schema_diagnostic_[execution.py](http://execution.py)

├── test_schema_diagnostic_[summary.py](http://summary.py)

├── test_schema_diagnostic_[closeout.py](http://closeout.py)

└── test_track11_[readiness.py](http://readiness.py)

```

Exact paths may differ only to follow established repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and records for:

1. schema-diagnostic plan;

2. operator approval;

3. preflight;

4. six per-run diagnostic records;

5. diagnostic summary;

6. diagnostic closeout;

7. Track 11 readiness.

Every schema must:

- have a stable ID and explicit version;

- use `additionalProperties: false`;

- reference Track 10 authorization;

- reference all consumed historical plans;

- identify exact runtime, candidate, corpus, prompt, template, and response-schema identities;

- identify exact case and category;

- require repetition `1`;

- distinguish raw, extracted, parsed, and validated output;

- represent truncation and output-limit behavior;

- represent failure authority;

- represent threshold eligibility;

- represent memory and cleanup evidence;

- prohibit absolute external paths;

- prohibit secrets and host identity;

- preserve `selectionOutcome: no-selection`;

- preserve `calibrationStatus: not-approved`;

- preserve `comparisonWinner: null`;

- preserve `productionReady: false`.

## Multi-Agent Execution Model

Cursor Plan is the parent Track 10A diagnostic orchestrator.

Use Grok 4.7 Extra High for:

- execution authority;

- deterministic case selection;

- plan identity;

- diagnostic threshold;

- raw-output security;

- failure attribution;

- hardened execution;

- diagnostic conclusion;

- readiness;

- conflict resolution;

- independent verification.

Delegate bounded work to:

### Agent 1: Diagnostic-authority specialist

Owns Track 10 authorization, historical-plan rejection, new plan, threshold, result-root policy, operator checkpoint, frozen authority, and stop conditions.

### Agent 2: Case-selection specialist

Owns six-category mapping, minimum-case-ID selection, uniqueness, corpus identity, and immutable run inventory.

### Agent 3: Raw-output and diagnostics specialist

Owns bounded output retention, extraction, JSON parsing, response-schema validation, evidence-ID diagnostics, truncation, output limits, and failure-attribution inputs.

### Agent 4: Hardened-execution specialist

Owns dependency and template prechecks, network denial, cgroup telemetry, state-aware post-exit behavior, process isolation, cleanup, and no-silent-launch-loss behavior.

### Agent 5: Diagnostic-analysis specialist

Owns six-run completeness, qualifying candidate-output failure counts, category coverage, threshold evaluation, and outcome classification.

### Agent 6: Closeout and readiness specialist

Owns immutable summaries, retention, cleanup, Track 11 readiness, frozen authority, and exact next recommendation.

### Agent 7: Independent verifier

Runs after execution.

Must not own planning, selection, raw-output capture, execution, attribution, threshold evaluation, closeout, or readiness.

### Coordination Rules

The parent must:

- finish implementation and synthetic verification before execution;

- select cases deterministically before plan generation;

- generate one new plan digest;

- stop for operator approval;

- execute six runs serially;

- seal every run before advancing;

- continue after candidate-attributed schema failure;

- stop on blocking security or infrastructure failure;

- preserve immutable evidence;

- integrate centrally;

- commission a fresh verifier.

## Ordered Execution Plan

### Task 1: Verify the Track 10 Baseline

#### Allowed files or subsystem

Read-only Git state, Track 8A through Track 10 records, verified external roots, historical roots, workflows, tests, architecture, provenance, and authority.

#### Required behavior

Confirm all assumed state, Track 10 authorization, consumed plans, accepted memory evidence, artifact identities, response attribution, and frozen authority.

#### Tests

Run existing validators and digest checks only.

#### Done condition

The baseline is proven and no candidate execution occurred.

### Task 2: Select the Six Cases and Implement the Diagnostic Plan

#### Allowed files or subsystem

Committed corpus taxonomy, deterministic selector, schemas, plan, approval record, validators, CLI, runbooks, and tests.

#### Required behavior

Select exactly one minimum case ID from each committed category.

Create a plan binding:

- six selected cases;

- one repetition each;

- systematic-failure threshold;

- exact identities;

- execution order;

- raw-output retention;

- diagnostics;

- resource limits;

- stop conditions;

- cleanup;

- frozen authority.

Stop before execution.

#### Tests

Validate category completeness, deterministic selection, uniqueness, exact run count, historical-plan rejection, plan identity, result-root isolation, and approval binding.

#### Done condition

A complete diagnostic plan awaits operator approval.

### Task 3: Implement and Validate Diagnostic Evidence Capture

#### Allowed files or subsystem

Raw-output capture, extraction, parsing, schema validation, evidence-ID diagnostics, attribution, schemas, templates, documentation, and tests.

#### Required behavior

Reuse and strengthen the Track 9A evidence boundary.

Ensure every run preserves the complete attribution chain.

#### Tests

Cover valid schema, candidate-output schema failure, malformed JSON, empty output, prose around JSON, missing fields, unexpected fields, evidence-ID errors, truncation, excessive output, adapter error, evaluator error, protocol error, and unresolved authority.

#### Done condition

Every diagnostic response can be attributed from retained evidence.

### Task 4: Execute the Six Diagnostic Runs

#### Allowed files or subsystem

Verified roots, hardened launcher, selected case inputs, fresh result root, per-run records.

#### Required behavior

After operator approval:

- execute six serial runs in plan order;

- use exactly one repetition per case;

- use zero retries;

- seal every launch;

- retain raw output before extraction;

- hide gold, evaluator, and prior-run information;

- continue after candidate-attributed schema failure;

- stop on blocking infrastructure or security failure.

#### Tests

All synthetic execution, isolation, output, telemetry, and cleanup tests must pass first.

#### Done condition

All six runs are sealed or the diagnostic stops structurally.

### Task 5: Evaluate the Precommitted Threshold

#### Allowed files or subsystem

Sealed diagnostic records, summary module, threshold logic, documentation, and tests.

#### Required behavior

Count only qualifying candidate-output schema failures.

Calculate:

- completed runs;

- candidate-output schema-failure count;

- distinct affected categories;

- schema-valid count;

- unresolved count;

- infrastructure-failure count;

- threshold result.

Apply the threshold exactly as committed.

Do not score corpus metrics or promotion gates.

#### Tests

Cover:

- 0 failures;

- 1 failure;

- 2 failures;

- 3 failures;

- 4 failures across 2 categories;

- 4 failures across 3 categories;

- 5 failures;

- 6 failures;

- unresolved attribution;

- incomplete runs;

- infrastructure stop.

#### Done condition

One diagnostic conclusion is produced.

### Task 6: Produce Diagnostic Summary and Disposition Evidence

#### Allowed files or subsystem

Summary, category evidence, response-shape analysis, failure-authority analysis, provenance, and tests.

#### Required behavior

Describe:

- repeated response shapes;

- category distribution;

- schema-valid responses;

- candidate-output failures;

- unresolved responses;

- systematic threshold status;

- limitations.

Do not automatically reject or select the candidate.

#### Tests

Validate summary consistency and authority boundaries.

#### Done condition

The diagnostic result is decision-grade or explicitly incomplete.

### Task 7: Close the Diagnostic and Decide Track 11 Readiness

#### Allowed files or subsystem

Closeout, retention, cleanup, failed attempts, readiness record, and tests.

#### Required behavior

Record:

- planned and completed runs;

- missing or unsealed runs;

- threshold outcome;

- cleanup;

- retained evidence;

- remaining blockers;

- Track 11 readiness.

Track 11 readiness is advisory pending Principal Architect review.

#### Tests

Validate systematic, not-established, unreliable, incomplete, and stopped outcomes.

#### Done condition

The diagnostic is durably closed.

### Task 8: Documentation, Repository Contracts, and Independent Verification

#### Allowed files or subsystem

Redacted records, documentation, workflows, tests, complete diff, and external evidence.

#### Required behavior

CI remains inference-free and artifact-free.

A fresh verifier must inspect:

- Track 10 authority;

- deterministic case selection;

- plan identity;

- threshold identity;

- run inventory;

- raw-output evidence;

- diagnostics;

- failure attribution;

- threshold arithmetic;

- cleanup;

- immutable external evidence;

- unchanged candidate authority.

#### Tests

Run every command in Verification.

#### Done condition

Track 10A is ready for Principal Architect review.

## Out of Scope

Track 10A must not:

- rerun memory-context phases;

- run qualification smoke or short-generation phases;

- run the full 24-case corpus;

- use more than six candidate executions;

- use multiple repetitions;

- retry;

- acquire or replace artifacts;

- modify historical result roots;

- install project dependencies;

- replace the publisher template;

- change prompt, response schema, decoding, corpus, metrics, gates, memory ceiling, or limits;

- calculate corpus-wide promotion metrics;

- reject or select the candidate automatically;

- integrate with PatchPilot;

- authorize shadow mode;

- use production or tenant data;

- change GitHub settings;

- publish, release, or deploy.

## Stop Conditions

Stop if:

1. Specification parent differs from `origin/main`.

2. Working tree contains unrelated changes.

3. Track 10 is not merged.

4. Track 10 diagnostic authorization is absent or invalid.

5. A historical plan is reusable.

6. An artifact, template, corpus, prompt, or schema identity differs.

7. Verified external root is unavailable.

8. Deterministic selection does not produce exactly six unique cases.

9. Fresh result root is nonempty or unsafe.

10. Operator approval is absent or mismatched.

11. Dynamic-link or template precheck fails.

12. Raw-output retention cannot be guaranteed.

13. Gold, evaluator, hidden, or prior-result data is visible.

14. Cgroup telemetry is unavailable or contradictory.

15. Memory exceeds the ceiling.

16. OOM occurs.

17. Network or isolation fails.

18. Output exceeds the committed boundary.

19. Cleanup fails.

20. A launch cannot be retained and represented durably.

21. The precommitted threshold would need to change.

22. A sibling repository must be accessed.

23. Work cannot fit in one pull-request-sized branch.

## Verification

Pass requires:

- frozen dependency synchronization;

- Ruff format and lint;

- strict mypy;

- complete pytest suite;

- every merged Track validator;

- every Track 10A schema and record validator;

- Track 10 authorization validation;

- consumed-plan rejection tests;

- deterministic six-category selection tests;

- exact six-run inventory tests;

- plan-identity tests;

- result-root isolation tests;

- operator-approval tests;

- threshold-immutability tests;

- raw-output retention tests;

- extraction tests;

- JSON parsing tests;

- response-schema tests;

- evidence-ID tests;

- truncation tests;

- output-limit tests;

- failure-attribution tests;

- gold-isolation tests;

- prior-result-isolation tests;

- cgroup telemetry tests;

- post-exit monotonicity tests;

- no-silent-launch-loss tests;

- diagnostic-completeness tests;

- threshold tests for every count and category combination;

- outcome-classification tests;

- closeout tests;

- Track 11 readiness tests;

- workflow-policy validation;

- dependency-policy validation;

- prohibited-artifact scan;

- dependency and lockfile check;

- documentation checks;

- `git diff --check`;

- `git status --short --branch`.

Also confirm:

- no context-memory measurement reran;

- no full corpus evaluation occurred;

- no new artifact was acquired;

- no project runtime dependency was added;

- historical roots remained unchanged;

- exactly the approved diagnostic phases ran;

- no production or tenant data was used;

- candidate selection remains `no-selection`;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false.

## Handoff Requirements

Return:

1. Outcome

2. Base commit and branch

3. Track 10 authorization

4. Historical-plan rejection

5. New plan and digest

6. Operator checkpoint

7. Selected case IDs and categories

8. Selection-rule proof

9. Runtime, candidate, template, corpus, prompt, and schema identities

10. Result-root validation

11. Threshold identity

12. Planned run inventory

13. Completed run inventory

14. Missing or unsealed runs

15. Raw-output identities

16. Extraction results

17. JSON parse results

18. Schema-validation results

19. Failure-authority results

20. Evidence-ID findings

21. Truncation and output-limit outcomes

22. Cgroup, network, isolation, and cleanup outcomes

23. Candidate-output schema-failure count

24. Distinct affected-category count

25. Schema-valid count

26. Unresolved count

27. Threshold result

28. Diagnostic conclusion

29. Response-shape consistency

30. Closeout

31. Track 11 readiness

32. Files changed

33. External result files

34. Dependency impact

35. Complete verification

36. Independent verification

37. Scope compliance

38. Residual risks

39. Proposed commit and PR

40. Post-merge recommendation

Final verdict must be exactly one of:

- `SYSTEMATIC SCHEMA FAILURE ESTABLISHED`

- `SYSTEMATIC SCHEMA FAILURE NOT ESTABLISHED`

- `SCHEMA BEHAVIOR UNRELIABLE OR UNRESOLVED`

- `DIAGNOSTIC INCOMPLETE`

- `BLOCKED BY UNRESOLVED AUTHORITY`

Explicitly confirm:

- no context-memory rerun;

- no full corpus execution;

- no new acquisition;

- no project runtime installation;

- no template, prompt, schema, decoding, metric, gate, threshold, or limit change after approval;

- no conversion or quantization;

- no candidate rejection or selection;

- no PatchPilot integration;

- no automatic Git action;

- no GitHub setting change;

- no publication, release, or deployment;

- calibration remains `not-approved`;

- comparison winner remains null;

- `productionReady` remains false.

End with exactly one:

`INTELLIGENCE TRACK 10A READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT`

or:

`INTELLIGENCE TRACK 10A BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW`