# Measurement recovery

A failed phase is kept. The ceiling is not raised, and the phase is not retried by the harness. An out-of-memory event, a peak above `12884901888` bytes, missing `memory.peak`, a digest mismatch, an unverified dependency, a network reachability result, an isolation failure, an output-limit failure, or a cleanup failure stops every later phase.

The operator inspects the external result root, removes nothing that a later review still needs, and starts a new result root for a later session. Overwrite of an existing result file is refused. A new session still requires the measurement-plan digest. Recovery does not download, replace, or relocate the promoted artifacts.

`RLIMIT_AS` is not evidence that the resident ceiling held. Recovery uses the cgroup peak, cgroup current, RSS, and virtual size as separate fields.
