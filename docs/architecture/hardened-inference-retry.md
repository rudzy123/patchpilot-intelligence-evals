# Hardened inference retry

Track 8B-R2 uses the verified ONNX Runtime and candidate artifacts, the shared runtime dependency closure, and `linux-bwrap-systemd-v1`. The exact-sandbox dynamic-link precheck loads `libonnxruntime.so.1.31.1`, resolves `OrtGetApiBase`, and exits. It does not create a model session and it does not call Run.

Both earlier plan digests stay consumed. The R2 plan digest `2133054bea8db11822cc65f6ea9c45f1ba1500f1aef67d314fbccca764155350` is consumed and is not reusable. `replacementPlanDigest` stays `not-issued` and no R3 digest is issued. Another Run requires a new plan and a new operator checkpoint. Approved dependencies are mounted individually and read-only. Provider libraries and broad host library directories stay unmounted.

Resident memory authority remains cgroup `memory.current`, `memory.peak`, and `memory.events`. `RLIMIT_AS` is address space. A context-memory conclusion of `within-ceiling` requires complete cgroup peak evidence for both the 4,096-token phase and the 8,192-token phase. A scope that disappears after the child exits can be recorded as `post-exit-scope-removed` when a complete sample already exists. A scope that disappears while the child is active is an infrastructure failure. Smoke evidence does not establish the context conclusion. A peak above the ceiling is `exceeded`.

The 24-case metrics and gates stay unchanged. `comparisonWinner` stays null. Calibration stays `not-approved`. Selection stays `no-selection`. `productionReady` stays false. `furtherRetryAssumed` stays false. An infrastructure stop records `proportionalityRecommendation` `review-required` and does not authorize another retry.
