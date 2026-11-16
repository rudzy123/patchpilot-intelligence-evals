# Corrected measurement recovery

A failed phase is kept. The ceiling is not raised, and the phase is not retried by the harness. The stop causes are `approval-required`, `cleanup-failure`, `compatibility-failure`, `digest-mismatch`, `excessive-output`, `gold-visible`, `insufficient-capacity`, `isolation-failure`, `memory-ceiling`, `missing-root`, `network-violation`, `oom`, `plan-consumed`, `prior-phase-failed`, `result-root-reuse`, `telemetry-unresolved`, and `unverified-dependency`.

Any of those causes stops the current phase and every later phase. Closeout marks the later phases `withheld`. The consumed Track 8B plan cannot be supplied as a replacement. The retry plan digest is consumed as well, and `replacementPlanDigest` stays `not-issued`. A later real execution needs a new Session or explicitly reviewed retry authority, a new plan digest, a fresh empty result root, and a new operator checkpoint.

The operator inspects the external result root, removes nothing that a later review still needs, and leaves the historical Track 8B result root unchanged. Overwrite of an existing result file is refused. Recovery does not download, replace, or relocate the promoted runtime, model, tokenizer, ONNX, external-data, or publisher-template bytes.

`RLIMIT_AS` is address space. Cgroup `MemoryMax` is the resident-memory control. Recovery reads `memory.current`, `memory.peak`, and `memory.events` separately from process RSS, process-tree RSS, and virtual size. A missing counter, a current value above the recorded peak, or an out-of-memory event is a stop, not a cue to raise `12884901888`.
