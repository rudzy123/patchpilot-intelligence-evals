Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.
# Intelligence Track 4: First Offline Candidate Selection and Evaluation Authorization
## Identity
- Repository: patchpilot-intelligence-evals
- Session ID: Intelligence Track 4
- Mission: Select and authorize one small offline candidate for a future Finding Explanation Assistant evaluation, establish its licensing and provenance record, fix the acquisition and isolation procedure, define the exact experiment, and determine whether candidate acquisition may proceed in Intelligence Track 5.
- Base commit: The parent of the spec-only commit introducing this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.
- Expected repository state: Intelligence Track 3 merged with a provider-neutral candidate protocol, bounded subprocess execution, deterministic fixtures, immutable result records, candidate comparison, calibration, and protected validation CI.
- Branch prefix: docs/intelligence-track-4-candidate-selection
- Change type: Architecture, research evidence, provenance records, closed authorization schemas, schema-validation tests, and documentation only. No model acquisition or inference.
- Commit policy: One Conventional Commit after Principal Architect review.
- Automatic Git actions: Cursor must not commit, push, create a pull request, create a tag, publish a release, deploy, modify Git history, change GitHub repository settings, or acquire model or tokenizer artifacts.
## Architectural Outcome
Intelligence Track 4 must answer one question:
> Which single small offline candidate, if any, is suitable for the first controlled PatchPilot Finding Explanation Assistant evaluation?
The Session must produce a complete authorization package containing:
1. Candidate-selection criteria.
2. A documented shortlist of no more than five candidates.
3. One recommended candidate or an explicit no-selection verdict.
4. Model-card and source verification.
5. License and redistribution analysis.
6. Weight and tokenizer provenance requirements.
7. A non-sensitive local hardware profile.
8. A fixed hardware and memory budget.
9. An offline acquisition procedure.
10. Cryptographic identity and artifact-inventory requirements.
11. Runtime and subprocess-isolation design.
12. Prompt and output contract.
13. Exact future evaluation experiment.
14. Security and privacy review.
15. Stop conditions for acquisition and execution.
16. Intelligence Track 5 acceptance criteria.
This Session does not acquire or execute a candidate.
## Strategic Boundary
PatchPilot remains deterministic and authoritative.
A future evaluated candidate may assist with:
- explaining stored Finding facts;
- explaining Product Match Evidence;
- explaining deterministic P1-P4 factor contributions;
- identifying missing evidence;
- organizing authorized citations;
- drafting non-authoritative remediation guidance;
- refusing when evidence is insufficient.
A candidate must never become authoritative over:
- tenant identity;
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
- remediation-queue rank;
- human priority review;
- Finding lifecycle;
- remediation completion;
- audit records.
Model output remains evaluation data.
No model output may enter PatchPilot production during this Session.
## Governing Authority
Before research or editing, Cursor must reread:
- all repository AGENTS.md files;
- README.md;
- SECURITY.md;
- CONTRIBUTING.md;
- NOTICE;
- LICENSE;
- .gitignore;
- pyproject.toml;
- uv.lock;
- the protected validation workflow;
- all documents under docs/architecture;
- all documents under docs/provenance;
- all current JSON Schemas;
- corpus manifest and corpus policy;
- promotion-gate documentation;
- candidate-protocol documentation;
- subprocess-isolation documentation;
- calibration documentation;
- result-retention documentation;
- candidate manifests and fixture provenance;
- candidate comparison behavior;
- existing CLI commands;
- existing tests;
- Intelligence Track 2 and Track 3 specifications;
- merged Intelligence Track 3 implementation evidence.
Do not inspect local files in patchpilot or neural-from-scratch.
Public, read-only research is permitted for:
- official candidate repositories;
- official model cards;
- official license and terms pages;
- official tokenizer documentation;
- official runtime documentation;
- official artifact manifests;
- published technical reports;
- original model authors or organizations;
- official security advisories affecting the proposed runtime or artifact format.
Prefer primary sources.
Do not rely on an unverified model-directory listing, repost, mirror, benchmark leaderboard, blog, forum, or social-media claim as the sole authority for selection.
## Invariants
### One candidate only
The Session may recommend at most one candidate for Intelligence Track 5.
A shortlist may be analyzed, but the final outcome must be exactly one of:
- one candidate recommended for controlled acquisition;
- no candidate currently satisfies the requirements.
Do not authorize multiple downloads or a broad model benchmark.
### Small offline candidate
The recommended candidate must be suitable for local, offline, evaluation-only use.
The target class is:
- open-weight or source-available under documented terms;
- text-generation capable;
- instruction-following capable or reasonably promptable for structured explanation;
- small enough for bounded local evaluation;
- no mandatory hosted API;
- no mandatory telemetry;
- no remote-code requirement;
- no proprietary runtime requirement.
Preferred parameter range:
- approximately 0.5 billion to 3 billion parameters.
A candidate above 3 billion parameters requires explicit justification based on local hardware, memory, storage, runtime, latency, and expected evaluation benefit.
### Mandatory licensing and provenance
The candidate must have:
- identifiable authorship or organizational ownership;
- an official source repository;
- an official model card;
- explicit model-weight terms;
- explicit code-license terms where code is required;
- explicit tokenizer provenance;
- documented commercial-use status;
- documented redistribution rights or restrictions;
- documented modification or quantization rights;
- documented attribution requirements;
- documented acceptable-use restrictions;
- an immutable official revision;
- a verifiable artifact inventory.
Do not assume that:
- a public repository means open weights;
- a permissive source-code license applies to model weights;
- Apache-2.0 code guarantees Apache-2.0 weights;
- a community conversion inherits an upstream license automatically;
- a downloadable artifact may be redistributed;
- a model card is legally equivalent to a license.
License or provenance uncertainty is a stop condition.
### Artifact identity
The authorization package must define:
- official model ID;
- organization or author;
- exact immutable revision or commit;
- official source URL;
- model-card URL;
- license URL;
- tokenizer source;
- configuration source;
- expected artifact inventory;
- expected file names;
- expected file sizes where published;
- expected upstream digests where available;
- locally computed SHA-256 requirement after acquisition;
- conversion or quantization provenance where applicable;
- runtime compatibility;
- prohibited mirrors;
- prohibited unverified conversions.
A floating branch such as main is not sufficient as the final artifact identity.
### Runtime neutrality
Intelligence Track 4 may recommend one runtime for Intelligence Track 5, but the candidate protocol remains provider-neutral.
The runtime must:
- support fully offline execution after acquisition;
- avoid remote code;
- avoid trust_remote_code;
- avoid mandatory telemetry;
- permit explicit telemetry disablement where telemetry exists;
- support local artifact paths;
- support deterministic generation settings where practical;
- fit the approved hardware budget;
- run behind the existing subprocess boundary;
- remain outside PatchPilot production dependencies;
- have explicit license and security dispositions.
Runtime libraries must not be added during Intelligence Track 4.
### Local hardware budget
Cursor may inspect the current evaluation machine only through non-sensitive local system commands.
The hardware record may contain:
- operating-system family and version;
- CPU architecture;
- logical CPU count;
- total system memory;
- available storage;
- GPU availability;
- GPU model;
- GPU memory where available;
- supported runtime capabilities.
The hardware record must not contain:
- usernames;
- hostnames;
- IP addresses;
- MAC addresses;
- serial numbers;
- device IDs;
- filesystem paths containing usernames;
- environment variables;
- credentials;
- license keys.
Initial preferred limits:
- model artifacts at or below 8 GiB;
- estimated peak process memory at or below 12 GiB;
- evaluation context at or below 8,192 tokens unless the model supports less;
- generated output at or below 1,200 words and existing protocol output limits;
- one real-candidate process at a time;
- zero concurrent real-model invocations;
- no mandatory GPU requirement unless the inspected machine supports it reliably;
- at least twice the expected artifact size available for acquisition, quarantine, and verification;
- sufficient additional space for runtime caches and evaluation results.
If the local machine cannot support the candidate safely, return no-selection or recommend a smaller candidate.
### Synthetic-only evaluation
Future evaluation remains synthetic-only.
A candidate may receive only:
- the approved synthetic Finding Explanation input;
- deterministic PatchPilot conclusions represented by existing schemas;
- authorized synthetic evidence;
- approved prompt instructions;
- generation constraints.
A candidate must not receive:
- gold claims;
- expected citations;
- refusal labels;
- category labels;
- prompt-injection labels;
- cross-tenant negative controls;
- prior candidate outputs;
- prior evaluation outcomes;
- tenant data;
- customer data;
- production data;
- credentials;
- environment dumps;
- unrelated local source code.
### Offline execution and remote-code prohibition
After acquisition, evaluation must use:
- local artifact paths only;
- disabled or blocked outbound network access;
- no provider API;
- no model-hub access;
- no automatic tokenizer retrieval;
- no automatic configuration retrieval;
- no telemetry;
- no automatic updates;
- no arbitrary code from model repositories;
- no trust_remote_code.
The candidate must not require custom remote code.
### No production composition
Intelligence Track 4 must not add:
- model weights;
- tokenizer files;
- model configuration files;
- runtime libraries;
- real-model inference;
- production prompts;
- PatchPilot APIs;
- PatchPilot web UI;
- database state;
- tenant data;
- shadow mode;
- generated product content;
- production composition.
### No gate changes
Current invariant and percentage gates remain unchanged.
The Session may identify calibration concerns, but it must not change:
- metric definitions;
- corpus taxonomy;
- invariant gates;
- percentage thresholds;
- promotion status.
Any future gate change requires explicit Principal Architect approval.
## Assumed Repository State
Before editing, Cursor must prove:
- workspace root and Git root are patchpilot-intelligence-evals;
- local main equals origin/main;
- Intelligence Track 3 is merged;
- the spec-only commit parent equals origin/main;
- the working tree is clean after the spec-only commit;
- repository license is Apache-2.0;
- Python requirement remains &gt;=3.12,&lt;3.13;
- uv.lock exists and validates;
- protected validation CI exists and passes on synchronized main;
- exactly 24 synthetic cases exist;
- the approved corpus digest remains authoritative unless synchronized main proves an authorized revision;
- candidate protocol version remains 1.0.0 unless synchronized main proves an authorized revision;
- eight deterministic fixture manifests exist;
- fixture review statuses record Principal Architect approval for harness evaluation;
- candidate execution occurs through the bounded subprocess protocol;
- no fixture reads gold corpus records;
- result artifacts are immutable and overwrite-protected;
- comparison selects no production winner;
- calibration remains not approved;
- productionReady remains false;
- no real-model dependency exists;
- no model weight or tokenizer artifact exists;
- no provider SDK exists;
- no tenant or customer data exists;
- no PatchPilot production integration exists;
- no sibling repository is nested in this Git tree.
If a material assumption is false, stop and report the conflict.
## Allowed Change Surface
Permitted:
- docs/specs/intelligence-track-4.md;
- candidate-selection criteria;
- candidate-shortlist record;
- selected-candidate authorization record;
- license and provenance review;
- non-sensitive local hardware record;
- acquisition protocol;
- artifact-manifest template;
- runtime-selection record;
- first-real-candidate experiment plan;
- prompt contract;
- security review;
- model-card review;
- threat-model additions;
- promotion-gate interpretation;
- README and architecture-index updates;
- closed JSON Schemas required for Track 4 structured records;
- schema-validation tests;
- CLI validation commands only if needed to validate Track 4 records;
- existing validation workflow only if needed to validate committed Track 4 records.
Not permitted:
- model artifacts;
- tokenizer artifacts;
- model configuration artifacts;
- inference-runtime dependencies;
- model-framework dependencies;
- candidate execution;
- model download;
- provider access for inference;
- PatchPilot product integration;
- sibling-repository modification;
- deployment.
## Required Documentation Outputs
The final repository must include the conceptual equivalent of:
```text
docs/
├── architecture/
│   ├── real-candidate-selection.md
│   ├── real-candidate-acquisition.md
│   ├── real-candidate-isolation.md
│   └── real-candidate-evaluation-plan.md
├── provenance/
│   ├── candidate-shortlist.md
│   └── selected-candidate-authorization.md
└── specs/
	└── intelligence-track-4.md
candidates/
└── authorization/
	├── candidate-shortlist.json
	├── first-real-candidate.json
	├── evaluation-hardware-profile.json
	├── acquisition-manifest-template.json
	└── first-real-candidate-experiment.json
schemas/
├── candidate-shortlist.schema.json
├── real-candidate-authorization.schema.json
├── evaluation-hardware-profile.schema.json
├── candidate-acquisition-manifest.schema.json
└── real-candidate-experiment-plan.schema.json
Exact names may change only to follow established repository conventions.
Do not create a candidate manifest that falsely implies artifacts were already acquired.
Required Structured Records
Intelligence Track 4 must create closed, versioned JSON Schemas and validated records for:
candidate shortlist;
selected-candidate authorization;
non-sensitive local hardware profile;
acquisition-manifest template;
real-candidate experiment plan.
Required schema files:
schemas/candidate-shortlist.schema.json;
schemas/real-candidate-authorization.schema.json;
schemas/evaluation-hardware-profile.schema.json;
schemas/candidate-acquisition-manifest.schema.json;
schemas/real-candidate-experiment-plan.schema.json.
Required records:
candidates/authorization/candidate-shortlist.json;
candidates/authorization/first-real-candidate.json;
candidates/authorization/evaluation-hardware-profile.json;
candidates/authorization/acquisition-manifest-template.json;
candidates/authorization/first-real-candidate-experiment.json.
Every schema must:
have a stable schema identifier;
have an explicit schema version;
use additionalProperties: false;
distinguish expected values from observed values;
distinguish selected candidates from rejected candidates;
support an explicit no-selection outcome;
prohibit credentials, tokens, tenant identifiers, hostnames, IP addresses, device identifiers, and environment values;
preserve productionReady: false.
The selected-candidate authorization record must contain:
acquisitionStatus: "not-acquired";
executionStatus: "not-executed";
productionReady: false;
an empty list of locally observed artifact digests;
the expected immutable upstream revision;
official source, model-card, license, and tokenizer references;
Principal Architect review status;
explicit prohibited uses;
explicit Track 5 stop conditions.
Expected artifact values must not be represented as locally verified values.
Local SHA-256 values remain unavailable until Intelligence Track 5.
Multi-Agent Execution Model
Cursor Plan is the lead candidate-selection orchestrator.
Use Grok 4.7 Extra High for:
candidate selection;
license interpretation;
provenance decisions;
hardware-fit analysis;
runtime selection;
security decisions;
supply-chain controls;
experiment design;
conflict resolution;
independent final verification.
Delegate parallel read-only investigation to specialist agents.
Agent 1: Candidate-landscape specialist
Builds a shortlist of no more than five candidates.
Evaluates:
parameter count;
context length;
instruction capability;
likely local resource fit;
official support;
documentation quality;
immutable revision availability;
evaluation suitability.
Agent 2: License and provenance specialist
Verifies:
weight license;
code license;
tokenizer license;
commercial use;
redistribution;
modification;
quantization rights;
attribution;
acceptable-use restrictions;
official source;
immutable revision;
artifact provenance.
Agent 3: Runtime and hardware specialist
Inspects the non-sensitive local hardware profile and evaluates:
memory;
storage;
CPU;
GPU;
candidate artifact size;
estimated peak memory;
runtime compatibility;
expected latency;
context budget;
quantization requirements.
Agent 4: Security and isolation specialist
Evaluates:
remote-code requirements;
tokenizer code;
serialization format;
model-loading risk;
telemetry;
network behavior;
subprocess compatibility;
filesystem isolation;
artifact scanning;
quarantine;
safe acquisition;
supply-chain controls.
Agent 5: Evaluation-plan specialist
Defines:
prompt contract;
deterministic inference settings;
generation limits;
candidate-response handling;
one-process-per-case behavior;
experiment manifest;
failure boundaries;
metrics;
repetitions;
result interpretation;
comparison restrictions.
Agent 6: Model-card specialist
Evaluates:
intended use;
prohibited use;
limitations;
training-data disclosure;
benchmark claims;
safety notes;
language support;
model-card completeness;
security-explanation suitability.
Agent 7: Independent final-verification specialist
Runs after primary records are written.
Must not own:
shortlist;
license decision;
candidate authorization;
runtime decision;
security decision;
acquisition procedure;
experiment plan.
Coordination rules
The parent agent must:
run specialist research in parallel;
use primary evidence;
document missing evidence;
reconcile exactly one recommendation or no-selection;
assign exclusive ownership to each document and structured record;
prevent overlapping edits;
stop when license or provenance remains ambiguous;
commission independent final verification.
Ordered Execution Plan
Cursor Plan must create one to-do per task and execute tasks in order.
Task 1: Verify the Intelligence Track 3 Baseline
Allowed files or subsystem
Read-only repository state, protocol, manifests, runner, schemas, fixtures, evaluation, calibration, CI, and documentation.
Required behavior
Confirm every assumed repository-state item.
Record:
corpus identity;
protocol identity;
existing subprocess limits;
current candidate boundary;
current promotion gates;
calibration status;
current schema-registration conventions;
required documentation ownership;
exact files authorized for Tasks 2 through 8.
Tests
Run safe Git and existing locked validation commands where required.
Done condition
The Track 3 baseline is proven, no stop condition exists, and exclusive file ownership is assigned.
Task 2: Define Candidate-Selection Criteria
Allowed files or subsystem
Candidate-selection architecture, scoring rules, disqualifiers, and schema requirements.
Required behavior
Define mandatory criteria.
Mandatory criteria must include:
explicit weight-use license;
clear commercial-use position;
clear redistribution position;
immutable official source revision;
no remote-code requirement;
fully offline runtime support;
tokenizer provenance;
artifact digest capability;
fit within approved local resources;
compatibility with bounded subprocess evaluation;
no mandatory telemetry;
no tenant-data requirement;
official model card;
documented limitations;
no PatchPilot production dependency.
Candidates that fail any mandatory criterion are disqualified and must not receive a weighted score.
Candidates passing all mandatory criteria must be scored on a 100-point scale:
license, weight-use clarity, and provenance: 25 points;
security, remote-code avoidance, and offline isolation: 20 points;
local hardware and memory fit: 20 points;
Finding Explanation Assistant evaluation suitability: 20 points;
model-card completeness and limitation disclosure: 10 points;
runtime maturity and reproducibility: 5 points.
Each score must cite primary evidence.
Tie-breaking order:
clearer weight and tokenizer licensing;
no custom or remote code;
lower estimated peak memory;
smaller artifact size;
stronger immutable artifact identity;
better model-card disclosure;
more mature offline runtime support.
Leaderboard position, popularity, download count, and benchmark prestige are not tie-breakers.
Tests
Run schema, documentation, arithmetic, and consistency checks.
Done condition
Candidate selection is reproducible, evidence-backed, and independent of popularity.
Task 3: Inspect Local Hardware and Fix the Resource Budget
Allowed files or subsystem
Non-sensitive system inspection and hardware-profile documentation.
Required behavior
Record only:
operating-system family and version;
CPU architecture;
logical CPU count;
total memory;
available storage;
GPU availability;
GPU model and memory where available;
supported runtime capabilities.
Do not record hostnames, usernames, IP addresses, MAC addresses, serial numbers, device IDs, or environment values.
Define:
maximum candidate artifact size;
maximum estimated peak process memory;
maximum context length;
maximum generated tokens or words;
process concurrency;
timeout;
allowed quantization;
required free storage;
CPU fallback behavior;
GPU requirements, if any.
Tests
Validate the hardware record and scan for prohibited identifiers.
Done condition
The resource envelope is explicit and can reject candidates that do not fit.
Task 4: Research and Evaluate the Candidate Shortlist
Allowed files or subsystem
Public primary-source research, shortlist documentation, shortlist JSON record, and evidence references.
Required behavior
Analyze no more than five candidates.
For each candidate record:
official model ID;
author or organization;
parameter count;
architecture family;
context length;
official source;
immutable revision availability;
weight license;
code license;
commercial-use position;
redistribution position;
modification or quantization conditions;
tokenizer provenance;
artifact formats;
expected artifact size;
available runtimes;
remote-code requirement;
telemetry behavior;
likely hardware fit;
model-card completeness;
security concerns;
evaluation strengths;
evaluation weaknesses;
mandatory-criterion status;
disqualifiers;
weighted score when eligible;
evidence sources.
For every external source, record:
descriptive source name;
exact URL;
publisher or model owner;
retrieval date in ISO 8601 format;
which claim the source supports;
whether the source is authoritative, secondary, or unresolved.
License conclusions must cite the official license or terms page.
Model-card conclusions must cite the official model card.
Immutable revision claims must cite the official repository revision.
Hardware estimates must distinguish:
publisher-provided values;
runtime-documentation estimates;
calculated estimates;
unknown values.
Do not copy complete model cards or license terms into the repository. Use concise summaries and links.
If sources conflict, record the conflict and use the more restrictive interpretation.
An unresolved conflict in weight use, tokenizer licensing, commercial use, remote code, or immutable identity disqualifies the candidate.
Do not download model or tokenizer artifacts.
Tests
Validate the shortlist schema, scoring arithmetic, evidence references, links, and mandatory-criterion decisions.
Done condition
The shortlist contains sufficient primary evidence to support one selection or a no-selection result.
Task 5: Select One Candidate or Return No-Selection
Allowed files or subsystem
Selected-candidate authorization document and structured authorization record.
Required behavior
Choose exactly one candidate only if every mandatory criterion passes.
The authorization record must state:
candidate identity;
approved source;
immutable revision;
weight-license disposition;
code-license disposition;
tokenizer provenance;
commercial-use disposition;
redistribution disposition;
approved artifact format;
approved tokenizer source;
approved runtime;
approved quantization, if any;
expected artifact inventory;
expected artifact sizes where known;
acquisition status;
execution status;
locally verified digest list;
evaluation-only authorization;
prohibited uses;
hardware fit;
security conditions;
Track 5 stop conditions;
productionReady: false;
Principal Architect review status.
Required initial states:
acquisitionStatus: "not-acquired";
executionStatus: "not-executed";
productionReady: false;
locally observed artifact digests: empty.
If no candidate qualifies:
create an explicit no-selection record;
identify the blockers;
do not invent a selected candidate;
stop before acquisition and experiment authorization tasks that require a candidate.
Tests
Validate the structured authorization record against the closed schema.
Done condition
One candidate is selected with complete evidence, or a truthful no-selection decision is recorded.
Task 6: Define Offline Acquisition and Artifact Verification
Allowed files or subsystem
Acquisition architecture, acquisition-manifest schema, template record, supply-chain controls, and security documentation.
Required behavior
Define a future operator procedure that:
Acquires artifacts only from the approved official source.
Pins the approved immutable revision.
Uses an empty quarantine directory.
Disables automatic execution and remote code.
Records source URLs.
Records expected and observed filenames separately.
Records expected and observed file sizes separately.
Computes SHA-256 for every acquired artifact.
Validates artifact types.
Scans for unexpected executable content.
Verifies tokenizer and configuration provenance.
Produces a local artifact manifest.
Rejects unexpected files.
Moves only verified artifacts into the approved local cache.
Tests offline loading after acquisition.
Prevents network fallback.
Records acquisition date and operator role.
Prohibits committing weights to Git.
Prohibits uploading weights as CI artifacts.
Prohibits redistribution unless explicitly authorized.
Define failure, rejection, cleanup, quarantine-retention, and retry behavior.
No acquisition occurs during Intelligence Track 4.
Tests
Validate the closed acquisition-manifest schema and unpopulated template record.
Confirm:
no observed digest is present;
no observed artifact falsely appears acquired;
no credential or local path is embedded;
acquisition status remains not acquired.
Done condition
Intelligence Track 5 can acquire the candidate without making new licensing, provenance, or security decisions during download.
Task 7: Define the First Real-Candidate Experiment
Allowed files or subsystem
Experiment-plan schema, structured experiment record, prompt contract, runtime plan, and evaluation documentation.
Required behavior
Define the exact Intelligence Track 5 experiment.
Specify:
selected candidate;
selected runtime;
selected quantization;
corpus version and digest;
candidate-protocol version;
candidate-manifest version;
prompt-template identity;
prompt-template digest requirement;
decoding settings;
seed behavior;
temperature;
top-p;
top-k where supported;
repetition count;
context limit;
generation limit;
timeout;
stdout and stderr limits;
hardware profile;
offline network policy;
one-process-at-a-time policy;
result directory;
experiment identity;
failure handling;
evaluator metrics;
invariant gates;
percentage gates;
no-winner rule;
no-production-readiness rule.
Require at least three repetitions per case when deterministic replay is measured, unless the selected runtime cannot provide meaningful seed control.
If deterministic replay is unavailable, define an alternate consistency metric without changing existing promotion gates.
Define the prompt so the candidate:
receives authorized evidence only;
distinguishes deterministic PatchPilot conclusions from generated explanation;
cites evidence IDs;
reports missing evidence;
qualifies uncertainty;
refuses unsupported requests;
ignores instructions embedded in evidence;
does not claim state mutation;
does not expose hidden evaluation labels;
does not receive gold claims or cross-tenant controls.
Do not execute the experiment during this Session.
Tests
Validate the experiment-plan schema and structured record.
Confirm:
execution status remains not executed;
no local artifact digest is fabricated;
no gate changes occur;
production readiness remains false;
no gold-label field is included in the prompt contract.
Done condition
Intelligence Track 5 has one bounded and reproducible experiment requiring no unresolved architecture decision.
Task 8: Independent Verification and Track 5 Recommendation
Allowed files or subsystem
Complete Track 4 documentation, schemas, records, references, and repository diff.
Required behavior
A fresh agent must verify:
all mandatory candidate evidence comes from authoritative sources;
scoring is correct;
disqualified candidates are not scored;
the selected candidate passes all mandatory criteria;
license conclusions are supportable;
immutable revision is fixed;
tokenizer provenance is clear;
no remote code is required;
hardware budget is credible;
runtime is offline-capable;
acquisition has not occurred;
experiment is reproducible;
prompt excludes gold labels;
no threshold changed;
productionReady remains false;
no sibling repository was accessed;
no model, tokenizer, or configuration artifact entered the repository;
all five schemas and five records validate.
Tests
Run every command in the Verification section.
Done condition
The independent reviewer confirms that Intelligence Track 5 acquisition may proceed or returns a release-blocking selection defect.
Out of Scope
Intelligence Track 4 must not:
download model weights;
download tokenizer artifacts;
download model configurations;
execute a real model;
install an inference runtime;
add a model framework;
modify uv.lock for inference;
contact a hosted inference provider;
use API keys;
use tenant data;
use customer data;
use production data;
modify patchpilot;
modify neural-from-scratch;
inspect local sibling repositories;
add embeddings;
add a vector database;
add RAG;
add fine-tuning;
add LoRA;
add preference optimization;
implement shadow mode;
implement PatchPilot APIs or UI;
create production composition;
change evaluation gates;
publish a model;
redistribute model weights;
create a release;
deploy.
Stop Conditions
Stop and report if:
The spec-only commit parent differs from origin/main.
The working tree contains unrelated changes.
Intelligence Track 3 is not merged.
Protected Track 3 validation is failing.
A real candidate artifact already exists in the repository.
A candidate requires remote code.
Weight licensing is unclear.
Commercial-use terms are unclear.
Redistribution terms are unclear when redistribution is required.
Tokenizer provenance is unclear.
No immutable official revision is available.
The candidate exceeds the local hardware budget.
The candidate requires a hosted provider.
The candidate requires network access during evaluation.
The candidate requires tenant or production data.
The candidate cannot use the provider-neutral subprocess protocol.
Runtime licensing or security remains unresolved.
Acquisition requires an unverified mirror.
Experiment design would expose gold labels.
Experiment design would change current gates.
A sibling repository must be inspected locally.
A model, tokenizer, or configuration artifact is downloaded.
A runtime dependency or lockfile change appears necessary.
A structured record cannot be represented through a closed schema.
The work cannot fit in one documentation-oriented pull request.
On a stop condition:
do not choose the candidate;
do not download artifacts;
do not weaken criteria;
record the exact blocker;
cite the governing evidence;
recommend the smallest next decision.
Verification
Pass requires:
uv sync --frozen;
uv run ruff format --check .;
uv run ruff check .;
uv run mypy src tests;
uv run pytest;
uv run patchpilot-evals corpus-validation;
uv run patchpilot-evals baseline-evaluation;
validation of all five Intelligence Track 4 schemas;
validation of all five Intelligence Track 4 structured records;
confirmation of exactly one selected candidate or one explicit no-selection result;
confirmation that every candidate either passes all mandatory criteria or is explicitly disqualified;
confirmation that disqualified candidates have no weighted score;
confirmation that weighted scores total no more than 100;
confirmation that every scored claim has a recorded source;
confirmation that the selected candidate has no unresolved mandatory criterion;
confirmation that acquisitionStatus remains not-acquired;
confirmation that executionStatus remains not-executed;
confirmation that locally observed artifact digests remain empty;
confirmation that productionReady remains false;
acquisition-manifest template validation;
experiment-plan validation;
documentation and relative-link checks;
license and provenance checks;
workflow validation;
secret-pattern scan;
prohibited-hardware-identifier scan;
prohibited-artifact scan;
scan for model weights, tokenizer artifacts, and model configurations;
confirmation that no inference-runtime dependency was added;
confirmation that uv.lock did not change;
git diff --check;
git status --short --branch.
Also confirm:
no model or tokenizer was downloaded;
no model was executed;
no inference provider was contacted;
no runtime dependency was added;
no tenant, customer, or production data was used;
no sibling repository was accessed or modified;
no PatchPilot production integration was created;
no release or deployment occurred;
current gates are unchanged;
productionReady remains false.
Recommended Conventional Commit:
docs(evals): authorize first offline candidate
Do not create the commit automatically.
Handoff Requirements
Return one consolidated handoff containing:
Outcome
Base commit, branch, and working-tree state
Multi-agent execution summary
Intelligence Track 3 baseline
Candidate-selection criteria
Mandatory-criterion results
Scoring model
Local hardware budget
Candidate shortlist
Primary evidence reviewed
License and use-rights analysis
Selected candidate or no-selection decision
Immutable candidate identity
Tokenizer provenance
Runtime recommendation
Expected artifact inventory
Offline acquisition procedure
Supply-chain controls
First real-candidate experiment plan
Prompt contract
Security and isolation requirements
Structured schemas and records
Files changed
Dependency and lockfile impact
Every verification command and actual result
Independent verification findings
Scope compliance
Unresolved decisions
Residual risks
Exact Intelligence Track 5 authorization recommendation
Proposed Conventional Commit
Proposed pull-request title and summary
Intelligence Track 5 prerequisites
Final verdict:
FIRST OFFLINE CANDIDATE AUTHORIZED FOR CONTROLLED ACQUISITION
FIRST OFFLINE CANDIDATE AUTHORIZED WITH DOCUMENTED RESIDUALS
NO CANDIDATE AUTHORIZED
BLOCKED BY UNRESOLVED AUTHORITY
Explicitly confirm:
no model, tokenizer, or configuration artifact was downloaded;
no real model was executed;
no inference provider was contacted;
no model-runtime dependency was added;
no tenant, customer, or production data was used;
no sibling repository was accessed or modified;
no PatchPilot production integration was created;
no automatic commit or push occurred;
no pull request was created automatically;
no release or deployment occurred;
acquisitionStatus remains not-acquired;
executionStatus remains not-executed;
productionReady remains false.
End with exactly one:
INTELLIGENCE TRACK 4 READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT
or:
INTELLIGENCE TRACK 4 BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW
