# Conversion toolchain evidence

Three official toolchains were assessed on 2026-11-10. None is authorized. No package was installed and no conversion was run. The decision record is [onnx-conversion-plan.json](../../candidates/authorization/onnx-conversion-plan.json).

`huggingface/optimum-onnx` tag `v0.1.0` resolves to commit `d2328e386a81b0970a458a7570a38b131414edc6`. The annotated tag is unsigned. Project metadata at that commit names Apache-2.0. It depends on `optimum` 2.1, `transformers` from 4.36 up to but not including 4.58, and `onnx`. Optional `onnxruntime` 1.18 or newer is not the authorized `v1.31.1` pin. No torch pin is published. The exporter source at that tag was not read in this session. The published export reference documents `revision` defaulting to `main`, `local_files_only` defaulting to false, and `trust_remote_code` defaulting to false. That reference is not a line-cited reading of the tag, so the export path stays not offline-closed. `trust_remote_code` must stay false.

`microsoft/onnxruntime-genai` tag `v0.19.0` is commit `d01b2441a72d4e3223415b9b08474c6e65fbc028`. The license file at that tag is MIT, with copyright held by Microsoft Corporation. Architecture support at that commit was not closed. The default-branch model builder is not the pin.

The PyTorch ONNX exporter is the underlying exporter, not a closed safetensors toolchain. `v0.1.0` does not publish an exact torch pin, so the exporter version and revision stay unresolved. Its license at a pinned commit was not read, so the license stays unresolved.

No source family is independently eligible. The Qwen Research License does not authorize acquisition or conversion. Weight-license and tokenizer gaps on OLMo, Gemma, and SmolLM2 remain. Converted output, if a later session authorizes it, is `locally-converted` and is not publisher-provided.
