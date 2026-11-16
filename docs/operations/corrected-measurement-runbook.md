# Corrected measurement runbook

Validators read committed retry records. They do not create a session. The boundary is [corrected-controlled-measurement.md](../architecture/corrected-controlled-measurement.md).

`measurement-retry-preflight` recomputes the promoted runtime and candidate digests and checks the verified-root classes. It does not require the operator digest and it does not call session Run. It writes `preflight.json` and `template-compatibility.json` under the result root.

`measurement-retry-execute`, `measurement-retry-smoke`, `measurement-retry-short-generation`, `measurement-retry-context`, and `measurement-retry-corpus` require `--operator-approval`, `--runtime-cache`, `--model-cache`, and `--result-root`. The context command also requires `--tokens` `4096` or `8192`. The retry plan digest `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b` is consumed. These commands refuse it before Run.

The result root is a new empty directory under `/var/tmp`, mode `0700`, class `measurement-retry-result`. It is distinct from `/var/tmp/patchpilot-evals-track8a/runtime-cache`, `/var/tmp/patchpilot-evals-track8a/model-cache`, `/var/tmp/patchpilot-evals-track8b-approved-8280ec63`, and `/var/tmp/patchpilot-evals-track8b-checkpoint`. Those historical roots stay read-only or untouched. A non-empty root, a reused historical root, or a root that contains another plan digest is refused before Run.

`measurement-retry-execute` checks the operator digest before preflight. It then runs preflight, template compatibility, one-token smoke, short generation, the 4,096-token phase, the 8,192-token phase, and the corpus, in that order. A failed or unresolved prerequisite writes the failure, the closeout, and the advisory Track 9 record, then returns. Later phases stay withheld.

Supplying the consumed digest `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2` raises `plan-consumed`. Supplying the consumed retry digest `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b` also raises `plan-consumed`. Any other digest raises `approval-required`. No replacement plan digest is issued. Another real execution requires a new Session or explicitly reviewed retry authority, a new plan digest, a fresh empty result root, and a new operator checkpoint.

These execute commands are absent from `.github/workflows/validate.yml`. Repository Contracts runs only the validation commands. `installationAuthorized` stays false. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `productionReady` stays false.
