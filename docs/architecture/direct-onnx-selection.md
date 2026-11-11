# Direct ONNX selection

Track 7 qualifies a direct ONNX path only when the model owner publishes the graph for the exact family at an immutable revision, with a complete external-data inventory, normalized paths, no traversal, no symlink dependence, a consistent license, no remote-code requirement, and compatibility with the planned ONNX Runtime adapter. Community conversions, mirrors, local conversion, and unapproved quantization fail. `graphParsed` stays false.

The qualifying inventory is the FP32 set in [finalist-direct-onnx.json](../../candidates/authorization/finalist-direct-onnx.json) for `LiquidAI/LFM2.5-1.2B-Instruct-ONNX` revision `10f72e70abf67ac0fd7ebf15bc5854726891d864`. The pinned card maps `model.onnx` to `model.onnx_data`, `model.onnx_data_1`, and `model.onnx_data_2`. The selected inventory is 4,717,588,977 bytes. Reduced-precision and quantized files are recorded with `selected` false.

Verification overhead equals one extra copy of that inventory because promotion copies quarantine to verified. That is the restrictive reading of [external-artifact-cache.md](external-artifact-cache.md). Runtime staging allowance is the published size of `onnxruntime-linux-x64-1.31.1.tgz` at ONNX Runtime `v1.31.1`, 11,413,655 bytes. The footprint is 9,446,591,609 bytes, which is above the 8 GiB cap. Peak process memory for the FP32 ONNX inventory is unknown: published sub-1GB figures are tied to NPU and Q4_0 rows. `artifactFit` and `memoryFit` fail. Context fit passes at 32,768 tokens. Storage headroom passes. Hardware fit fails.

The publisher quickstart sets `trust_remote_code`. The pinned trees contain no custom Python module, so the flag is not a load requirement. Execution still prohibits remote code. The publisher documents an ONNX Runtime session and does not state an opset. Compatibility means the planned adapter contract. Verification has not been performed, and the runtime stays `not-installed`.

Safetensors remains a prohibited execution input. The budget record is [finalist-artifact-budget.json](../../candidates/authorization/finalist-artifact-budget.json).
