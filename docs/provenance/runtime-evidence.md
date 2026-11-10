# Runtime evidence

Track 6A reuses the official facts already recorded for Track 5 on 2026-11-10. No project page, source archive, wheel, or model file was retrieved again. No runtime was installed. The closed assessment is [runtime-security-assessment.json](../../candidates/authorization/runtime-security-assessment.json).

`llama-cpp` is ggml-org/llama.cpp tag `v0.9.0` at `cd959bae99ff4bed22bef2604f45241c09bbb8c8`, MIT, artifact format GGUF. The Track 6A checklist fails `cpu-only` and `advisories-reviewed`. The recorded advisory identifiers stay in the assessment. Advisory bodies are not copied here.

`onnxruntime` is microsoft/onnxruntime tag `v1.31.1` at `6af1a932e2286d5c58166085d24c68783033edee`, MIT, artifact format ONNX. The recorded evidence supports CPU execution, offline local paths, a telemetry disable path, deterministic settings, and subprocess launch. No advisory identifier was recorded for this pin. Every Track 6A criterion passes.

`transformers` is huggingface/transformers tag `v5.22.2` at `6d195c6262a0ac2ef44f7b9a308617562286ff45`, Apache-2.0, artifact format safetensors. The Track 6A checklist fails `cpu-only`, `no-remote-code-required`, and `advisories-reviewed`. Official loading can execute repository Python when remote code is trusted. The recorded advisory identifiers have unknown affected ranges.

The Track 5 safetensors requirement remains the approved candidate format. ONNX authorization leaves `candidateFormatGap` true. That gap is recorded in [runtime-authorization-v2.json](../../candidates/authorization/runtime-authorization-v2.json). It does not change the Track 5 `no-runtime` decision in [runtime-selection.md](../architecture/runtime-selection.md).
