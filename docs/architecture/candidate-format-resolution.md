# Candidate format resolution

The authorized runtime format is ONNX. The five Track 4 families remain safetensors candidates, and selection stays `no-selection`. The official revision listings were read on 2026-11-10. Listing digests are upstream identities. `locallyObservedArtifactDigests` stays empty. No weight file was downloaded.

`Qwen/Qwen2.5-1.5B-Instruct` at `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` lists safetensors, a LICENSE file, and tokenizer files. It lists no ONNX file. Closure still fails `documented-limitations` and `bounded-subprocess-compatibility`.

`Qwen/Qwen2.5-3B-Instruct` at `aa8e72537993ba99e69dfaafa59ed015b17504d1` lists two safetensors shards and a LICENSE file. It lists no ONNX file. Closure still fails `documented-limitations` and `bounded-subprocess-compatibility`. The Qwen Research License is not conversion authority. That disqualifier is recorded on the conversion plan.

`HuggingFaceTB/SmolLM2-1.7B-Instruct` at `31b70e2e869a7173562077fd711b654946d38674` publishes an `onnx/` tree at the official revision. Those files are a hosted conversion, and this session did not inspect the graph. The tree sums to 19246095294 bytes. `onnx/model.onnx_data` plus `onnx/model_fp16.onnx_data` is 8944754688 bytes, above the 8589934592-byte artifact cap. `onnx/model_quantized.onnx` and `onnx/model_uint8.onnx` share one upstream listing digest and one byte count; both paths are recorded because the official tree lists both. Quantized variants are not approved. Weight license and tokenizer provenance remain failed. `bounded-subprocess-compatibility` stays failed. The hosted conversion does not qualify.

`allenai/OLMo-2-0425-1B-Instruct` at `48d788eca847d4d7548f375ad03d3c9312f6139e` lists safetensors and tokenizer files. It lists no LICENSE file and no ONNX file. Weight license and tokenizer provenance stay unresolved.

`google/gemma-3-1b-it` at `dcc83ea841ab6100d6b47a070329e1ba4cf78752` lists safetensors and tokenizer files. It lists no LICENSE file and no ONNX file. The safetensors listing digest was redacted and is not stored. The offline grant, tokenizer grant, and digest stay unresolved.

No family passes every mandatory criterion. The hardened launcher does not clear `bounded-subprocess-compatibility`. `resolutionOutcome` is `no-path`. `directOnnxQualified` is false. Installation, acquisition, conversion, and execution stay closed.

The command is `candidate-format-resolution-validation`. The conversion decision is in [onnx-conversion-boundary.md](onnx-conversion-boundary.md).
