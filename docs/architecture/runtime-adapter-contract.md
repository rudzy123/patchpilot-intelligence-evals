# Runtime adapter contract

The adapter id is `patchpilot-onnxruntime-adapter` version `1.0.0`. It speaks candidate protocol `1.0.0` and accepts only runtime `onnxruntime` `v1.31.1`. The hardened profile `linux-bwrap-systemd-v1` version `1.0.0` is required. There is no shell and no fallback launcher.

Three artifact classes stay separate.

A source-model artifact may be safetensors. Its only role is input to a separately authorized future conversion. Execution of a safetensors path is prohibited. The adapter rejects that path with `source-model-rejected`.

An executable runtime-model artifact is a verified ONNX graph file plus every verified ONNX external-data file that graph requires. An unverified ONNX inventory is `unverified-model`. A missing required external-data file is `missing-external-data`. An external-data file that is not part of the verified inventory is `unexpected-external-data`. This check compares names, sizes, and SHA-256 values. It does not inspect an ONNX graph and it does not execute one.

The current real-candidate outcome is `format-unavailable` because no qualifying ONNX artifact exists. That outcome is a stable candidate response with status `unavailable`. It does not accept a safetensors path in place of the missing ONNX artifact.

The synthetic fixture `synthetic_runtime_adapter.py` validates protocol and failure behavior. It is not a model artifact. The launcher does not mount a model directory for it. Offline mode is required. The child receives `ORT_DISABLE_TELEMETRY=1` through the hardened launcher's allowlist. Automatic retrieval, automatic conversion, and fallback execution are prohibited. One request produces one response. The fixture answers `unavailable` and does not load a model.

The command is `runtime-adapter-contract-validation`. `runtimeInstalled`, `realModelExecuted`, and `productionReady` stay false.
