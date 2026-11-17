# Contributing

Contributions to this repository must be original work for PatchPilot evaluation.

- Use synthetic identifiers only. Do not add tenant data, customer data, production prompts, raw SBOMs, or raw advisory payloads.
- Do not copy product source from the PatchPilot repository.
- Do not copy notebooks, modules, or datasets from `neural-from-scratch`.
- Do not add a model runtime, provider SDK, embedding stack, or vector database.
- Do not download model weights, tokenizer files, model configurations, or inference runtimes, and do not execute real inference.
- Do not commit weight files, tokenizer files, or an in-repository artifact cache. The ignore rules are defense in depth.
- A passing Track 5 validation command does not authorize Track 6 acquisition.
- A passing Track 6A validation command does not authorize acquisition, runtime installation, or model execution. Do not add a CI step that installs bubblewrap, Podman, Docker, or a model runtime.
- Track 6B readiness does not authorize runtime installation, model or tokenizer acquisition, model conversion, candidate selection, real inference, evaluation-gate changes, shadow mode, or PatchPilot production composition.
- A passing Track 6B validation command does not install ONNX Runtime, download a model, or convert a checkpoint. Track 6C readiness is `not-ready` and does not authorize installation, acquisition, conversion, or inference.
- Track 6D acquisition readiness is `not-ready` and does not authorize installation, acquisition, conversion, inference, or selection.
- Track 7 validation does not install a runtime, download a model, convert a checkpoint, or execute inference. Track 8 authorization is `not-authorized`. The Principal Architect review approves that outcome and does not authorize acquisition.
- Track 7A validation recalculates storage, checks the implementation review, and runs one temporary synthetic promotion. The 2026-11-12 review approves the storage model with documented residuals. It does not authorize acquisition, install a runtime, or execute inference. Track 8A readiness is `not-ready`.
- Track 7B validation reads committed memory, suitability, measurement, and implementation-review records. The 2026-11-12 review approves the evidence closure and authorizes a future measurement Session in principle with documented residuals. It does not authorize acquisition, runtime installation, conversion, quantization, inference, or selection. Track 8 acquisition stays `not-authorized`.
- Track 8A validation reads the committed acquisition plan, allowlist, redacted evidence, implementation review, and empty templates. It does not transfer, install a runtime, or execute a model. Do not add `acquire-runtime`, `acquire-candidate`, or `hardened-offline-load-proof` to a workflow. The 2026-11-16 review records one completed external transfer and does not authorize Track 8B measurement. An operator transfer writes outside this repository and does not change `pyproject.toml` or `uv.lock`.
- Track 8B validation reads the committed measurement plan, operator checkpoint, not-executed templates, stopped-attempt records, and Track 9 recommendation. It does not execute a model. Do not add `measurement-preflight`, `measurement-execute`, `measurement-smoke`, `measurement-short-generation`, `measurement-context`, or `measurement-corpus` to a workflow. The 2026-11-16 plan digest is consumed and is not reusable. Another Run requires a new plan and a new operator approval. Historical `measurementAuthorization` stays `not-authorized`. `installationAuthorized` stays false.
- Track 8B-R1 validation reads the committed retry plan, not-approved operator record, not-executed templates, stopped-attempt records, and advisory Track 9 recommendation. It does not execute a model. Do not add `measurement-retry-preflight`, `measurement-retry-execute`, `measurement-retry-smoke`, `measurement-retry-short-generation`, `measurement-retry-context`, or `measurement-retry-corpus` to a workflow. The retry plan digest is consumed and is not reusable. `replacementPlanDigest` stays `not-issued`. Another real execution requires a new plan digest and a new operator checkpoint. `installationAuthorized` stays false.
- Track 8B-R2 validation reads the committed inference-retry plan, not-approved operator record, not-executed templates, and the consumed-plan disposition. It does not execute a model. Do not add `inference-retry-preflight`, `inference-retry-precheck`, `inference-retry-execute`, `inference-retry-smoke`, `inference-retry-short-generation`, `inference-retry-context`, or `inference-retry-corpus` to a workflow. The R2 plan digest is consumed and is not reusable. No R3 digest is issued. `installationAuthorized` stays false.
- Candidate fixtures are deterministic test doubles. Do not describe them as models or give them network access.
- Do not put secrets in cases, tests, logs, or commits.
- Tests and evaluation commands must stay offline. Package installation is the only step that may use a package index.
- Keep JSON Schemas closed. Do not add fields that assign affectedness, priority, Finding state, queue rank, or remediation completion.
- Pin every external GitHub Action to a full commit SHA recorded in [docs/provenance/github-action-pins.md](docs/provenance/github-action-pins.md). Do not add `pull_request_target`, a write token, or a model or runtime download to a workflow.
- Required checks and the main ruleset procedure are in [docs/operations/required-checks.md](docs/operations/required-checks.md) and [docs/operations/main-ruleset-procedure.md](docs/operations/main-ruleset-procedure.md). Do not change repository rulesets from a pull request.
- Run the commands in [README.md](README.md) before asking for review.

Report accidental sensitive data through [SECURITY.md](SECURITY.md). Do not open a public issue that contains the data.
