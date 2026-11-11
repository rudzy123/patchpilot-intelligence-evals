# Direct ONNX eligibility

No pinned family has a qualified direct official ONNX artifact.

`Qwen/Qwen2.5-1.5B-Instruct` and `Qwen/Qwen2.5-3B-Instruct` list no ONNX file. `onnx-community/Qwen2.5-1.5B-Instruct` and `tonythethompson/Qwen2.5-1.5B-Instruct-ONNX` are unofficial conversions.

`HuggingFaceTB/SmolLM2-1.7B-Instruct` hosts an `onnx/` tree in the official repository. That tree is an uploaded optimized conversion. The upstream listing sizes sum to 19246095294 bytes. `onnx/model.onnx` and `onnx/model.onnx_data` are adjacent names, and adjacency is not an official external-data relationship. `model_quantized.onnx` and `model_uint8.onnx` share one listing digest and one byte count. The graph was not parsed. Quantized siblings are not approved.

`allenai/OLMo-2-0425-1B-Instruct` lists no ONNX file. Its separate GGUF repository is not an ONNX artifact.

`google/gemma-3-1b-it` lists no ONNX file. `onnx-community/gemma-3-1b-it-ONNX` and `onnxruntime/Gemma-3-ONNX` are not Google publications of this checkpoint.

Listing SHA-256 values are upstream identities. `locallyObservedArtifactDigests` stays empty. The command is `direct-onnx-evidence-validation`.
