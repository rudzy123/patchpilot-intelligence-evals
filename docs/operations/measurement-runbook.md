# Measurement runbook

Validators read committed records. They do not create a session.

`measurement-preflight` recomputes the promoted runtime and candidate digests and checks the verified-root classes. It does not require the operator digest and it does not call session Run. `measurement-execute`, `measurement-smoke`, `measurement-short-generation`, `measurement-context`, and `measurement-corpus` require `--operator-approval` equal to the measurement-plan digest. They also require `--runtime-cache`, `--model-cache`, and `--result-root`. Those roots stay outside this repository, outside home directories, and outside the sibling repositories.

`measurement-execute` runs the phases serially and refuses a later phase after a failed record. The real launcher also refuses the consumed 2026-11-16 plan before Run. Another Run requires a new plan and a new operator approval. The 8,192-token phase is conditional on the 4,096-token record. The corpus is conditional on the 8,192-token record. Raw outputs stay in the external result root. Redacted records omit cache paths, host identity, assistance text, and explanation bodies.

These execute commands are absent from `.github/workflows/validate.yml`. Repository Contracts runs only the validation commands. `installationAuthorized` stays false. Historical authorization records stay `not-authorized`.
