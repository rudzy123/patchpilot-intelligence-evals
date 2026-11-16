# Behavioral evaluation execution

The 24-case protocol starts only after the context phases pass. Each request is built with `to_candidate_input()` and `build_request()`. `validate_request()` remains the gold barrier. One case and one repetition use one hardened process. Each case has three repetitions because argmax replay is deterministic.

The prompt template digest is `62774d0f8b65c959c5b038911af4293d3d774aae3933f0d7a24064691685250a`. Load time is recorded outside the existing 15-second generation budget. Stdout is 65536 bytes, stderr is 16384 bytes, and retries stay zero. Process wall clock is 900 seconds and the CPU limit is 600 seconds.

Results use the immutable result writer and refuse overwrite. Execution failures stay apart from evaluator failures: startup, load, tokenizer, inference, timeout, out of memory, malformed response, schema, output limit, nonzero exit, isolation, network, cleanup, and evaluator failure. A schema, malformed, or timeout outcome continues with the other cases. The session stops on out of memory, network failure, isolation failure, cleanup failure, a digest mismatch, a peak above the ceiling, or missing telemetry.

Gold fields are not mounted. The durable record stores an output digest and metric numerators. It does not store assistance text or explanation bodies. Metrics and gates are the existing functions, unchanged. Comparison keeps `winner` null. Calibration stays `not-approved`.
