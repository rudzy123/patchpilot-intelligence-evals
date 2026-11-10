# Runtime selection

Track 5 assesses three offline runtimes and authorizes at most one. None was installed. The records are [runtime-assessment.json](../../candidates/authorization/runtime-assessment.json) and [runtime-authorization.json](../../candidates/authorization/runtime-authorization.json). Retrieval date: 2026-11-10.

The approved model format for this boundary is publisher safetensors with no conversion and no quantization. A missing or conflicting fact fails that criterion. The product repository was not inspected. None of these runtimes is added to this repository.

`llama-cpp` is ggml-org/llama.cpp tag `v0.9.0` at `cd959bae99ff4bed22bef2604f45241c09bbb8c8`, MIT. It fails because inference consumes GGUF rather than safetensors, because explicit Linux x86_64 support was not established from the retrieved CPU text, and because three GGUF parsing advisories have no identified patched version.

`onnxruntime` is microsoft/onnxruntime tag `v1.31.1` at `6af1a932e2286d5c58166085d24c68783033edee`, MIT. CPU execution is documented. It fails because sessions load ONNX or ORT graphs, not safetensors, and because the retrieved API does not bound token context or generated output.

`transformers` is huggingface/transformers tag `v5.22.2` at `6d195c6262a0ac2ef44f7b9a308617562286ff45`, Apache-2.0. It can load local safetensors. It fails because official loading documentation executes repository Python when remote code is trusted, because explicit Linux x86_64 support was not established, and because three deserialization advisories have unknown affected ranges.

The decision is `no-runtime`. No version is pinned for later acquisition. `acquisitionStatus` stays `not-acquired`, `executionStatus` stays `not-executed`, and `productionReady` stays false. Advisory identifiers are recorded without advisory bodies.

Principal Systems Architect review on 2026-11-10 accepts this no-runtime decision. It does not authorize a runtime. The acceptance record is [track5-implementation-review.md](../provenance/track5-implementation-review.md).
