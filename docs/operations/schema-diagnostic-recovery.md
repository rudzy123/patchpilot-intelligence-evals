# Schema diagnostic recovery

Stop the diagnostic and do not start the next case when any of these occur:

- an artifact, corpus, prompt, template, or response-schema digest differs
- the result root is a historical root or is not empty at the start
- the operator approval digest differs from the plan digest
- dynamic-link or template preflight fails
- a dependency is unverified
- network denial or isolation fails
- gold, evaluator data, or a prior result is visible
- cgroup telemetry is missing or contradictory
- resident memory exceeds the ceiling or an OOM event is recorded
- raw output cannot be retained
- output exceeds the committed limit
- process-tree cleanup fails
- a launch cannot be sealed

A candidate-attributed malformed or schema-invalid response is retained and the next planned case may run. Do not retry a run, replace a selected case, or add a case to compensate for a stopped run.

Do not rewrite `/var/tmp/patchpilot-evals-track9a-corpus` or any earlier result root. Do not acquire or replace runtime, candidate, tokenizer, or template files. The committed approval stays `not-approved`.

The runbook is [schema-diagnostic-runbook.md](schema-diagnostic-runbook.md).
