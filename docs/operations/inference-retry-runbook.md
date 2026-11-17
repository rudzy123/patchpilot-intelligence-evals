# Inference retry runbook

Validators read committed records and do not create a session. The boundary is [hardened-inference-retry.md](../architecture/hardened-inference-retry.md).

`inference-retry-preflight` recomputes promoted digests and writes the preflight and template-compatibility records. It does not require the operator digest and it does not call Run. `inference-retry-precheck` uses the same bubblewrap and systemd scope as measurement, loads the verified runtime library, resolves `OrtGetApiBase`, and exits without a model session.

`inference-retry-execute`, `inference-retry-smoke`, `inference-retry-short-generation`, `inference-retry-context`, and `inference-retry-corpus` require `--operator-approval`, `--runtime-cache`, `--model-cache`, and `--result-root`. The context command also requires `--tokens` `4096` or `8192`. The R2 digest `2133054bea8db11822cc65f6ea9c45f1ba1500f1aef67d314fbccca764155350` is consumed and raises `plan-consumed`. The earlier digests `8280ec639abd60edad7d49c1129d691822c17be06d7ef15aa2fcb5425bdbf0a2` and `572fc9da2bf5c3d378a56764672617849d317df293fdbc29d85b40e70ae27d2b` also raise `plan-consumed`. No replacement or R3 digest is issued. Any other digest raises `approval-required`.

The result root is a new empty directory under `/var/tmp`, mode `0700`, class `inference-retry-result`. It is distinct from the Track 8A caches and from `/var/tmp/patchpilot-evals-track8b-approved-8280ec63`, `/var/tmp/patchpilot-evals-track8b-checkpoint`, and `/var/tmp/patchpilot-evals-track8b-r1-572fc9da`. Those historical roots stay untouched.

`inference-retry-execute` checks the operator digest, then runs preflight, template compatibility, the dynamic-link precheck, one-token smoke, short generation, 4,096 tokens, 8,192 tokens, and the corpus. A failed phase writes the failure, closeout, and advisory Track 9 record. Later phases stay withheld. 8,192 tokens run only after 4,096 tokens pass. The corpus runs only after 8,192 tokens pass.

These execute commands are absent from `validate.yml`. Repository Contracts runs only the validation commands. `installationAuthorized` stays false. `selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false.
