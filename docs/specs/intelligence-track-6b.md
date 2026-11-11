Execution contract for this session only. It authorizes only the work it names. It is subordinate to repository security rules, accepted architecture, licensing requirements, provenance controls, and committed repository state. If those disagree with this spec, stop and report the conflict. This file is not a checkpoint and is not an ADR.

# Intelligence Track 6B: Runtime Staging and Candidate-Format Resolution

## Identity

- **Repository:** patchpilot-intelligence-evals

- **Session ID:** Intelligence Track 6B

- **Mission:** Implement the operator-controlled staging, provenance verification, and hardened-boundary integration required for the authorized ONNX Runtime identity, and determine whether the safetensors-to-ONNX candidate-format gap can be resolved without acquiring model artifacts or weakening licensing, provenance, isolation, or deterministic PatchPilot authority.

- **Base commit:** The parent of the spec-only commit that introduces this file. Before implementation, git rev-parse HEAD^ must equal git rev-parse origin/main.

- **Expected repository state:** Intelligence Track 6A merged with an approved hardened execution boundary, onnxruntime v1.31.1 authorized as a future runtime identity, runtime installation not authorized, no candidate selected, model acquisition not authorized, and productionReady false.

- **Branch:** feat/intelligence-track-6b-runtime-staging

- **Change type:** Runtime-staging architecture and validation, supply-chain controls, synthetic adapter testing, candidate-format analysis, closed schemas, structured records, documentation, and CI enforcement. No runtime binary acquisition, model acquisition, conversion, or inference.

- **Commit policy:** One Conventional Commit after Principal Architect review.

- **Automatic Git actions:** Cursor must not commit, push, create a pull request, create a tag, publish a package, create a release, deploy, modify Git history, change GitHub settings, install the authorized runtime, download runtime binaries, acquire model artifacts, convert model artifacts, or execute real inference.

## Architectural Outcome

Intelligence Track 6B must answer:

> Can the authorized ONNX Runtime identity be staged and verified through an operator-controlled external-runtime process, and is there a legally, technically, and reproducibly acceptable path from an eligible model candidate to an ONNX artifact?

The completed repository must be able to:

1. Represent an externally staged inference runtime without installing it.

2. Validate a repository-external runtime staging root.

3. Represent runtime quarantine, verified, and rejected states.

4. Validate an expected runtime artifact inventory.

5. Verify runtime artifacts through local SHA-256 identities.

6. reject unexpected binaries, missing files, traversal, symlink escape, unapproved libraries, and digest mismatches.

7. distinguish runtime authorization from runtime installation.

8. describe a versioned runtime-adapter contract for the existing candidate subprocess protocol.

9. exercise that adapter contract using deterministic synthetic runtime fixtures only.

10. preserve the hardened execution profile from Track 6A.

11. establish the accepted model formats for the authorized runtime.

12. determine whether a direct official ONNX candidate exists among the five previously reviewed candidates.

13. assess whether safetensors-to-ONNX conversion may be legally and technically authorized.

14. identify the exact conversion toolchain, licenses, versions, provenance, determinism requirements, and artifact identities if conversion is potentially acceptable.

15. authorize one future direct-ONNX or conversion path, or record no format-resolution path.

16. preserve the approved no-selection outcome unless all candidate criteria pass independently.

17. produce a Track 6C acquisition recommendation or explicit withholding decision.

18. keep runtime installation, model acquisition, model conversion, inference, and production readiness disabled.

This is an implementation Session.

It authorizes schemas, validation modules, synthetic fixtures, CLI commands, tests, structured records, documentation, and CI enforcement.

It does not authorize downloading or executing the runtime or any model.

## Governing Authority

Before implementation, Cursor must reread:

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

- every document under docs/architecture;

- every document under docs/provenance;

- every current JSON Schema;

- every candidate and authorization record;

- candidate protocol and runner;

- real-candidate manifest boundary;

- external model-artifact cache;

- artifact-verification implementation;

- hardened execution implementation;

- sandbox capability report;

- Track 6A hardened execution profile;

- Track 6A execution attestation;

- Track 6A runtime assessment and runtime authorization;

- Track 6A implementation-review record;

- Track 6B readiness record;

- Track 4 and Track 5 candidate evidence;

- current candidate shortlist;

- current Track 6 acquisition authorization;

- existing CLI commands;

- existing tests;

- Intelligence Track 2 through Track 6A specifications;

- merged Track 6A implementation and protected-CI evidence.

Do not inspect local files in patchpilot or neural-from-scratch.

Public read-only research is permitted only for:

- official ONNX Runtime repositories and documentation;

- official ONNX specifications;

- official ONNX Runtime licenses and security advisories;

- official model repositories;

- official model cards;

- official model and tokenizer licenses;

- official conversion-tool repositories;

- official conversion-tool documentation;

- official immutable revisions;

- original publisher documentation.

Secondary sources may identify an issue but may not satisfy mandatory licensing, provenance, conversion, runtime, or candidate-eligibility requirements.

## Invariants

### Deterministic PatchPilot authority

No runtime, adapter, converter, candidate, or model may become authoritative over:

- tenant or organization identity;

- asset identity;

- package identity;

- Product Match Evidence;

- affectedness;

- Finding creation;

- KEV membership;

- policy facts;

- P1-P4 priority;

- escalation;

- remediation-queue order;

- review state;

- Finding lifecycle;

- remediation completion;

- PatchPilot audit state.

Every output remains an evaluation artifact.

### Runtime authorization is not installation authority

The Track 6A authorization of onnxruntime v1.31.1 means only that the runtime identity passed the recorded architecture review.

It does not authorize:

- package installation;

- binary download;

- container-image download;

- Python wheel download;

- library loading;

- runtime execution;

- model loading;

- inference;

- production use.

Track 6B must preserve installationAuthorized: false.

### No runtime or model acquisition

Track 6B must not:

- install ONNX Runtime;

- download ONNX Runtime binaries or wheels;

- download container images;

- download model weights;

- download tokenizers;

- download real model configurations;

- download conversion tools;

- convert model artifacts;

- execute a real runtime;

- execute a real model;

- contact a provider for inference;

- populate a persistent external runtime or model cache.

Only synthetic local test files may be used.

### Runtime staging outside Git

A future runtime must be staged outside the repository.

Implement logical runtime states:

1. quarantine

2. verified

3. rejected

The runtime staging root must:

- be supplied explicitly;

- resolve outside this repository;

- resolve outside known sibling repositories;

- reject traversal;

- reject symlink escape;

- reject identity-bearing paths in committed records;

- never be committed;

- never be uploaded by CI;

- never contain tenant or production data;

- remain distinct from the model-artifact cache;

- remain distinct from the output-result directory.

### Runtime artifact verification

Runtime verification must distinguish:

- expected runtime files;

- observed runtime files;

- expected sizes;

- observed sizes;

- expected upstream digests;

- locally computed digests;

- executable files;

- shared libraries;

- license and notice files;

- configuration;

- adapter files;

- unexpected files.

Verification must reject:

- missing files;

- unexpected files;

- digest mismatch;

- unsupported executable format;

- unapproved shared libraries;

- writable verified artifacts;

- symlink escape;

- version mismatch;

- license mismatch;

- unapproved telemetry configuration;

- runtime identity different from the authorization record.

Do not claim malware detection.

### Runtime-adapter boundary

Define one provider-neutral adapter contract for an externally staged runtime.

The adapter must:

- use direct argument arrays;

- avoid a shell;

- use canonical JSON for the PatchPilot evaluation protocol;

- accept only verified runtime identity;

- accept only verified model artifacts;

- run only through the hardened Track 6A launcher;

- receive local paths through ephemeral execution configuration;

- expose no provider credentials;

- support explicit offline mode;

- disable telemetry;

- prevent automatic model or tokenizer retrieval;

- record runtime and adapter identities;

- emit structured failure categories;

- preserve one request and one response per invocation;

- preserve productionReady: false.

The adapter implementation in Track 6B must use deterministic synthetic runtime fixtures only.

### Candidate-format resolution

The current state contains a format gap:

- authorized runtime format: ONNX;

- current candidate-contract format: safetensors;

- selected candidate: none.

Track 6B must evaluate two possible resolution paths.

#### Path A: Direct official ONNX artifact

A direct ONNX candidate may be considered only when:

- the artifact is published by the official model owner or an explicitly authorized official organization;

- immutable revision exists;

- model and tokenizer licensing are resolved;

- commercial use is resolved;

- redistribution requirements are resolved;

- artifact and tokenizer provenance are complete;

- expected digests are authoritative or locally computable after a later acquisition;

- no remote code is required;

- the candidate fits the hardware envelope;

- the candidate satisfies all existing mandatory criteria.

#### Path B: Reproducible local conversion

Conversion may be considered only when:

- the source model is independently eligible;

- source-weight license permits conversion;

- tokenizer license is resolved;

- output use and redistribution terms are resolved;

- conversion does not require remote code;

- exact conversion tool and immutable version are fixed;

- conversion-tool license is acceptable;

- conversion configuration is closed and versioned;

- opset and precision are fixed;

- dynamic and static axes are specified;

- external-data behavior is specified;

- input and output tensor contracts are fixed;

- conversion is deterministic or variation is explicitly characterized;

- source and converted digests remain distinct;

- converted output is not represented as publisher-provided;

- numerical-equivalence requirements are defined;

- conversion happens only in a later authorized Session.

Track 6B must not perform conversion.

### No candidate selection by format convenience

A candidate must not be selected merely because an ONNX artifact exists.

Candidate selection still requires every Track 4 mandatory criterion to pass.

No-selection remains authoritative unless candidate-specific licensing, tokenizer, model-card, revision, digest, commercial-use, and security requirements are resolved.

### Hardened execution remains mandatory

Any future runtime or conversion invocation must use the approved Track 6A boundary:

- bubblewrap;

- transient systemd user scope;

- minimal environment;

- read-only verified inputs;

- isolated writable output;

- no repository or home visibility;

- no SSH or cloud credentials;

- no outbound host network;

- cgroup memory and process limits;

- Linux resource limits;

- process-tree cleanup;

- no shell.

Track 6B must not add a weaker fallback.

### Synthetic-only tests

All adapter and staging tests must use deterministic synthetic runtime fixtures.

Tests must not contain:

- runtime binaries;

- real model files;

- tokenizer files;

- real ONNX graphs copied from external models;

- tenant data;

- production data;

- credentials.

A minimal synthetic data file created by repository code for schema and staging tests is permitted only if it is clearly marked as non-model test data.

### Conversion evidence is separate from execution evidence

Conversion authorization, model acquisition, runtime staging, runtime execution, and model evaluation are separate decisions.

A passing conversion-plan review does not prove:

- runtime installation;

- runtime safety;

- model quality;

- model eligibility;

- model equivalence;

- production readiness.

### No gate changes

Do not change:

- corpus cases;

- corpus taxonomy;

- corpus digest;

- evaluation metrics;

- invariant gates;

- percentage thresholds;

- calibration status;

- promotion status.

Calibration remains not-approved.

productionReady remains false.

## Assumed Repository State

Before implementation, Cursor must prove:

- workspace and Git root are patchpilot-intelligence-evals;

- local main equals origin/main;

- Intelligence Track 6A is merged;

- spec-only commit parent equals origin/main;

- working tree is clean after the spec-only commit;

- repository license remains Apache-2.0;

- Python remains &gt;=3.12,&lt;3.13;

- uv.lock exists and validates;

- protected CI passes on synchronized main;

- 213 or more tests pass on synchronized main;

- the 24-case corpus and approved digest are unchanged;

- candidate protocol remains version 1.0.0;

- Track 5 candidate selection remains no-selection;

- Track 6 acquisition remains not-authorized;

- Track 6A hardened profile is approved with residuals;

- hardened mechanism remains linux-bwrap-systemd-v1;

- runtime authorization v2 identifies onnxruntime v1.31.1;

- runtime installation remains unauthorized;

- candidate selection remains false;

- candidate format gap remains true;

- Track 6B readiness is ready with documented residuals;

- no model, tokenizer, ONNX artifact, runtime binary, wheel, or container image exists;

- no runtime dependency exists in pyproject.toml or uv.lock;

- no provider SDK exists;

- no tenant or customer data exists;

- no PatchPilot integration exists;

- no sibling repository is nested in the Git tree;

- realModelExecuted remains false;

- productionReady remains false.

If any material assumption is false, stop and report the conflict.

## Allowed Change Surface

Permitted:

- docs/specs/[intelligence-track-6b.md](http://intelligence-track-6b.md);

- runtime-staging architecture;

- runtime-verification architecture;

- adapter-contract documentation;

- candidate-format-resolution documentation;

- conversion-plan documentation;

- Track 6C readiness documentation;

- runtime staging, adapter, conversion, and readiness schemas;

- structured records;

- source modules for runtime-root validation, runtime-inventory validation, adapter-contract validation, synthetic adapter execution, format-resolution decisions, conversion-plan validation, and Track 6C readiness;

- deterministic synthetic fixtures;

- focused tests;

- CLI validation commands;

- safe CI updates;

- README, SECURITY, AGENTS, CONTRIBUTING, architecture, and provenance documentation;

- .gitignore only for generated synthetic outputs;

- pyproject.toml and uv.lock only if a non-runtime validation dependency is essential, licensed, and explicitly justified.

Not permitted:

- runtime download or installation;

- model, tokenizer, or configuration acquisition;

- model conversion;

- real runtime execution;

- real inference;

- candidate selection without complete evidence;

- corpus or gate changes;

- sibling-repository access;

- PatchPilot integration;

- privileged host changes;

- package publication;

- release;

- deployment.

## Required Repository Additions

The repository must include the conceptual equivalent of:

text</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">docs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── architecture/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [external-runtime-staging.md](http://external-runtime-staging.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [runtime-adapter-contract.md](http://runtime-adapter-contract.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [candidate-format-resolution.md](http://candidate-format-resolution.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [onnx-conversion-boundary.md](http://onnx-conversion-boundary.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [track6c-readiness.md](http://track6c-readiness.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── provenance/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── [runtime-staging-provenance.md](http://runtime-staging-provenance.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── [conversion-toolchain-evidence.md](http://conversion-toolchain-evidence.md)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">└── specs/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── [intelligence-track-6b.md](http://intelligence-track-6b.md)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">schemas/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── external-runtime-cache-policy.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── runtime-artifact-verification.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── runtime-adapter-contract.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── candidate-format-resolution.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── onnx-conversion-plan.schema.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">└── track6c-readiness.schema.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">candidates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── authorization/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── external-runtime-cache-policy.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── runtime-adapter-contract.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── candidate-format-resolution.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; ├── onnx-conversion-plan.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">│&nbsp;&nbsp; └── track6c-readiness.json</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">└── templates/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">&nbsp;&nbsp;&nbsp; └── runtime-artifact-verification-template.json</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">src/patchpilot_intelligence_evals/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── runtime_[cache.py](http://cache.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── runtime_artifact_[verification.py](http://verification.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── runtime_adapter_[contract.py](http://contract.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── synthetic_runtime_[adapter.py](http://adapter.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── candidate_format_[resolution.py](http://resolution.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── conversion_[plan.py](http://plan.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">└── track6c_[readiness.py](http://readiness.py)</span></div><div><span></span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">tests/</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── test_runtime_[cache.py](http://cache.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── test_runtime_artifact_[verification.py](http://verification.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── test_runtime_adapter_[contract.py](http://contract.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── test_synthetic_runtime_[adapter.py](http://adapter.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── test_candidate_format_[resolution.py](http://resolution.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">├── test_conversion_[plan.py](http://plan.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">└── test_track6c_[readiness.py](http://readiness.py)</span></div><div><span attribution="{&quot;id&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;name&quot;:&quot;Copilot&quot;,&quot;oid&quot;:&quot;E64C3D4F-5E12-4514-AD9B-893A6FAFD00C&quot;,&quot;timestamp&quot;:1794341400000,&quot;dataSource&quot;:0}">

Exact file names may differ only to follow existing repository conventions.

Do not create empty placeholders.

## Required Structured Records

Create closed, versioned schemas and validated records for:

1. external runtime-cache policy;

2. runtime artifact-verification template;

3. runtime-adapter contract;

4. candidate-format resolution;

5. ONNX conversion plan;

6. Track 6C readiness.

Every schema must:

- have a stable schema ID;

- declare an explicit version;

- use additionalProperties: false;

- separate expected and observed values;

- prohibit credentials and tenant identifiers;

- prohibit hostnames and IP addresses;

- prohibit identity-bearing local paths;

- prohibit claims that acquisition or installation occurred;

- preserve runtimeInstalled: false;

- preserve modelAcquired: false;

- preserve realModelExecuted: false;

- preserve productionReady: false;

- support explicit no-path and not-ready outcomes.

The Track 6C readiness record must preserve:

- selectionOutcome: "no-selection";

- runtimeInstallationStatus: "not-installed";

- acquisitionStatus: "not-acquired";

- conversionStatus: "not-performed";

- executionStatus: "not-executed";

- realModelExecuted: false;

- productionReady: false;

- empty observed runtime and model-artifact digest arrays.

## Multi-Agent Execution Model

Cursor Plan is the lead runtime-staging and format-resolution orchestrator.

Use Grok 4.7 Extra High for:

- runtime staging;

- runtime supply-chain review;

- adapter boundary;

- candidate-format analysis;

- conversion licensing and provenance;

- readiness decisions;

- conflict resolution;

- independent verification.

Delegate parallel read-only investigation and controlled implementation to these specialists.

### Agent 1: Runtime-staging specialist

Owns:

- external runtime states;

- runtime-root policy;

- runtime inventory;

- expected and observed runtime files;

- runtime digest validation;

- staging and rejection rules.

### Agent 2: Runtime-adapter specialist

Owns:

- adapter contract;

- hardened-launcher composition;

- canonical request and response behavior;

- offline and telemetry flags;

- failure categories;

- synthetic adapter fixture.

### Agent 3: Direct-ONNX candidate specialist

Revisits exactly the five existing candidate families for official revision-specific ONNX artifacts.

Owns:

- official source;

- format provenance;

- tokenizer compatibility;

- licensing;

- immutable revision;

- disqualifiers.

### Agent 4: Conversion-toolchain specialist

Assesses no more than three conversion toolchains.

Owns:

- official source;

- license;

- immutable version;

- supported model architectures;

- opset;

- precision;

- external-data handling;

- remote-code requirements;

- determinism;

- security advisories;

- output provenance.

### Agent 5: Conversion-equivalence specialist

Owns:

- tensor contracts;

- numerical-comparison plan;

- tolerance definitions;

- deterministic test fixtures;

- source-versus-converted identity;

- conversion-result evidence.

No conversion is performed.

### Agent 6: Track 6C readiness specialist

Owns:

- candidate-format outcome;

- runtime staging prerequisites;

- conversion-path authorization or withholding;

- unresolved blockers;

- Track 6C decision.

### Agent 7: Independent verification specialist

Runs after implementation.

Must not own:

- runtime cache;

- runtime verification;

- adapter contract;

- direct-ONNX analysis;

- conversion plan;

- readiness decision.

### Coordination Rules

The parent agent must:

- parallelize read-only research;

- synthesize one architecture before edits;

- assign exclusive file ownership;

- prevent overlap;

- preserve dependency order;

- stop on unresolved license or provenance;

- integrate centrally;

- use a fresh independent reviewer.

## Ordered Execution Plan

Cursor Plan must create one to-do per task and execute the tasks in order.

### Task 1: Verify Intelligence Track 6A Baseline

#### Allowed files or subsystem

Read-only Git state, Track 6A schemas, records, implementation, tests, workflow, and documentation.

#### Required behavior

Confirm all assumed-state items.

Record:

- Track 6A review identity;

- hardened profile identity;

- runtime authorization identity;

- format gap;

- no-selection state;

- no-acquisition state;

- exact file ownership for Tasks 2 through 8.

#### Tests

Run safe Git inspection and locked validation commands as needed.

#### Done condition

The baseline is proven and no stop condition exists.

### Task 2: Implement External Runtime Staging and Verification

#### Allowed files or subsystem

Runtime-cache schemas, records, validation modules, CLI, synthetic fixtures, and tests.

#### Required behavior

Implement:

- quarantine;

- verified;

- rejected.

Enforce:

- explicit external runtime root;

- no repository-contained root;

- no sibling root;

- no traversal;

- no symlink escape;

- no execution from quarantine;

- expected-versus-observed separation;

- filename validation;

- file-count validation;

- file-size validation;

- SHA-256 validation;

- runtime-version validation;

- license and notice validation;

- executable-format validation;

- shared-library allowlisting;

- unexpected-file rejection;

- immutable verified identity;

- rejected-state persistence;

- no Git tracking;

- no CI upload.

Use synthetic files only.

#### Tests

Prove all success and failure paths using temporary directories.

#### Done condition

The runtime staging boundary is executable without staging the real runtime.

### Task 3: Implement the Runtime-Adapter Contract

#### Allowed files or subsystem

Adapter schema, record, module, CLI, synthetic adapter fixture, and tests.

#### Required behavior

Define:

- adapter ID and version;

- supported runtime identity;

- local runtime path supplied at execution time;

- local verified model path;

- offline flags;

- telemetry-disabled flags;

- canonical request and response;

- direct argument vector;

- no shell;

- hardened-profile requirement;

- timeout and output limits;

- structured failure categories;

- runtime and adapter digest recording;

- no automatic retrieval;

- no automatic conversion;

- no fallback execution.

Execute only a deterministic synthetic adapter fixture through the hardened boundary.

#### Tests

Prove the contract and fail-closed behavior without ONNX Runtime.

#### Done condition

A future staged runtime has a closed integration contract without being installed.

### Task 4: Resolve Direct Official ONNX Availability

#### Allowed files or subsystem

Official primary-source research, format-resolution schemas and records, candidate evidence, and documentation.

#### Required behavior

Revisit exactly the five Track 4 candidate families.

For each, determine whether an official immutable ONNX artifact exists.

Record:

- publisher;

- official source;

- immutable revision;

- ONNX provenance;

- model license;

- tokenizer license and provenance;

- commercial-use status;

- redistribution status;

- artifact inventory;

- digest authority;

- remote-code requirement;

- hardware fit;

- mandatory blockers.

Do not download artifacts.

Do not consider unverified community conversions.

#### Tests

Validate format-resolution records and source evidence.

#### Done condition

One direct official ONNX path qualifies fully or all direct paths remain disqualified.

### Task 5: Assess the Safetensors-to-ONNX Conversion Path

#### Allowed files or subsystem

Official toolchain research, conversion schema, conversion record, provenance documentation, and validation tests.

#### Required behavior

Assess no more than three conversion toolchains.

For each, record:

- official source;

- immutable version;

- license;

- supported architectures;

- tokenizer handling;

- remote-code behavior;

- offline operation;

- opset support;

- precision support;

- external-data support;

- deterministic controls;

- known security advisories;

- output provenance behavior;

- disqualifiers.

Do not download tools or perform conversion.

#### Tests

Validate the conversion-plan schema and decision rules.

#### Done condition

One future conversion toolchain is authorized in principle or conversion remains not authorized.

### Task 6: Define Conversion Reproducibility and Equivalence

#### Allowed files or subsystem

Conversion architecture, equivalence plan, structured record, and deterministic validation tests.

#### Required behavior

Define:

- source-artifact identity;

- conversion configuration identity;

- toolchain identity;

- output-artifact identity;

- opset;

- precision;

- input signatures;

- output signatures;

- dynamic dimensions;

- external-data layout;

- random-seed handling;

- canonical conversion invocation;

- numerical equivalence metrics;

- absolute and relative tolerances;

- representative synthetic input strategy;

- failure thresholds;

- nondeterminism handling;

- provenance statements.

Do not run conversion.

#### Tests

Validate the plan and use purely synthetic numeric examples to test tolerance calculations.

#### Done condition

A future conversion can be evaluated reproducibly without confusing converted output with publisher-provided output.

### Task 7: Create or Withhold Track 6C Readiness

#### Allowed files or subsystem

Track 6C schema, record, readiness logic, documentation, and tests.

#### Required behavior

Track 6C may be marked ready only if:

- runtime staging boundary passes;

- adapter contract passes;

- one runtime identity remains authorized;

- one candidate path is legally and technically eligible;

- candidate immutable identity is fixed;

- tokenizer provenance is resolved;

- either a direct official ONNX artifact qualifies or a conversion path is authorized;

- hardened Track 6A profile remains required;

- no gate change is needed.

If any prerequisite fails:

- record readinessOutcome: "not-ready";

- list blockers;

- preserve no-selection;

- preserve runtime not installed;

- preserve no acquisition;

- preserve no conversion;

- preserve no execution.

#### Tests

Validate ready and not-ready scenarios.

#### Done condition

Track 6C has a durable readiness or withholding decision.

### Task 8: Documentation, CI, and Independent Verification

#### Allowed files or subsystem

README, SECURITY, AGENTS, CONTRIBUTING, architecture, provenance, workflow, and complete diff.

#### Required behavior

Document:

- runtime staging;

- runtime verification;

- adapter contract;

- candidate-format findings;

- conversion decision;

- equivalence plan;

- Track 6C outcome;

- residual risks;

- no-download boundary.

Update CI to run only synthetic and portable validations.

CI must not:

- download ONNX Runtime;

- download models;

- pull images;

- convert models;

- execute inference.

Assign a fresh independent verifier.

#### Tests

Run every command in the Verification section.

#### Done condition

The runtime-staging and format-resolution boundary is documented, tested, CI-enforced, independently verified, and ready for Principal Architect review.

## Out of Scope

Intelligence Track 6B must not:

- install or download ONNX Runtime;

- acquire model, tokenizer, or configuration artifacts;

- convert model artifacts;

- run real inference;

- select a candidate with unresolved criteria;

- modify the corpus or gates;

- modify sibling repositories;

- modify PatchPilot;

- use tenant or production data;

- add embeddings, RAG, fine-tuning, LoRA, or preference optimization;

- implement shadow mode;

- create production composition;

- publish a package;

- create a release;

- deploy.

## Stop Conditions

Stop and report if:

1. Spec-only commit parent differs from origin/main.

2. Working tree contains unrelated changes.

3. Track 6A is not merged.

4. Track 6A review is absent or invalid.

5. Runtime or model artifacts already exist.

6. Runtime verification requires downloading the runtime.

7. Direct ONNX eligibility depends on an unofficial conversion.

8. Conversion rights are unresolved.

9. Tokenizer licensing or provenance is unresolved for a proposed path.

10. A converter requires remote code.

11. A conversion tool must be installed in this Session.

12. Conversion determinism cannot be represented.

13. Hardened execution would require weakening Track 6A.

14. Candidate selection requires relaxing mandatory criteria.

15. Existing gates must change.

16. A sibling repository must be inspected.

17. Work cannot fit in one PR-sized branch.

On a stop condition:

- do not acquire a runtime or model;

- do not perform conversion;

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

- all existing Track 5 validations;

- all existing Track 6A validations;

- fixture, comparison, and calibration validation;

- every Track 6B schema validation;

- every Track 6B record validation;

- runtime-cache tests;

- runtime-inventory tests;

- runtime digest and size tests;

- runtime symlink and path tests;

- synthetic adapter tests;

- hardened-launcher integration tests using synthetic fixtures;

- direct-ONNX evidence validation;

- conversion-plan validation;

- conversion-equivalence arithmetic tests;

- Track 6C readiness tests;

- documentation and link checks;

- license and provenance checks;

- workflow validation;

- prohibited-artifact scan;

- runtime-binary scan;

- model-artifact scan;

- git diff --check;

- git status --short --branch.

Also confirm:

- no runtime was downloaded or installed;

- no model, tokenizer, or configuration was downloaded;

- no model conversion occurred;

- no real inference occurred;

- no candidate was selected unless all criteria passed;

- no sibling repository was accessed;

- no privileged host change occurred;

- no provider was contacted for inference;

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

feat(evals): add runtime staging boundary

Do not create the commit automatically.

## Handoff Requirements

Return one consolidated handoff containing:

1. Outcome

2. Base commit, branch, and working-tree state

3. Multi-agent execution summary

4. Track 6A baseline

5. Runtime-cache implementation

6. Runtime-verification behavior

7. Runtime-adapter contract

8. Synthetic adapter results

9. Direct official ONNX findings

10. Conversion-toolchain findings

11. Conversion authorization or withholding

12. Conversion reproducibility plan

13. Equivalence criteria

14. Candidate-format resolution

15. Track 6C readiness or withholding

16. Files changed

17. Dependency and lockfile impact

18. Every verification command and result

19. CI changes

20. Independent verification

21. Scope compliance

22. Unresolved decisions

23. Residual risks

24. Exact Track 6C recommendation

25. Proposed Conventional Commit

26. Proposed PR title and summary

27. Track 6C prerequisites

Final verdict must be exactly one of:

- TRACK 6C CONTROLLED STAGING READY

- TRACK 6C CONTROLLED STAGING READY WITH DOCUMENTED RESIDUALS

- TRACK 6C CONTROLLED STAGING NOT READY

- BLOCKED BY UNRESOLVED AUTHORITY

Explicitly confirm:

- no runtime binary, wheel, or image was downloaded;

- no runtime was installed;

- no model, tokenizer, or configuration was acquired;

- no conversion occurred;

- no inference occurred;

- no candidate was selected unless all mandatory criteria passed;

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

INTELLIGENCE TRACK 6B READY FOR PRINCIPAL ARCHITECT REVIEW BEFORE COMMIT

or:

INTELLIGENCE TRACK 6B BLOCKED PENDING PRINCIPAL ARCHITECT REVIEW