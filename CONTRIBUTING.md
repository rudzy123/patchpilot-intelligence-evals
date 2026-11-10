# Contributing

Contributions to this repository must be original work for PatchPilot evaluation.

- Use synthetic identifiers only. Do not add tenant data, customer data, production prompts, raw SBOMs, or raw advisory payloads.
- Do not copy product source from the PatchPilot repository.
- Do not copy notebooks, modules, or datasets from `neural-from-scratch`.
- Do not add a model runtime, provider SDK, embedding stack, or vector database.
- Candidate fixtures are deterministic test doubles. Do not describe them as models or give them network access.
- Do not put secrets in cases, tests, logs, or commits.
- Tests and evaluation commands must stay offline. Package installation is the only step that may use a package index.
- Keep JSON Schemas closed. Do not add fields that assign affectedness, priority, Finding state, queue rank, or remediation completion.
- Run the commands in [README.md](README.md) before asking for review.

Report accidental sensitive data through [SECURITY.md](SECURITY.md). Do not open a public issue that contains the data.
