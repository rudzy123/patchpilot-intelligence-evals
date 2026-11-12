# Finalist memory evidence

Retrieved on 2026-11-12. The finalist is `LiquidAI/LFM2.5-1.2B-Instruct`, source revision `b9d816ab510f9a28dca37cb182e9da8b0226e13c`, ONNX revision `10f72e70abf67ac0fd7ebf15bc5854726891d864`. No graph, external-data file, tokenizer, or configuration was downloaded. `graphParsed` stays false. Every required resident category stays `unresolved`.

## Sources

- `lfm-card-shape` and `lfm-card-use`. Liquid AI model card at the pinned source revision. The card states about 1.17B parameters, 16 layers, context `32768`, vocabulary `65536`, English among the languages, instruction tuning, and JSON tool calls. It recommends agentic, extraction, and RAG uses and does not recommend knowledge-intensive tasks or programming. It does not state hidden size, head count, convolution width, or FP32 resident bytes.

  https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct/blob/b9d816ab510f9a28dca37cb182e9da8b0226e13c/README.md

- `lfm-card-memory`. The same card says the model runs under 1GB and lists 0.9GB NPU NexaML rows and a 719MB llama.cpp Q4_0 row. Units are decimal gigabytes. Conflict disposition is `restrictive-reading`. `byteBoundPermitted` is false. Those figures do not close an FP32 ONNX CPU envelope.

- `lfm-onnx-fp32` and `lfm-onnx-state`. Liquid AI ONNX card at the pinned ONNX revision. `model.onnx` is the FP32 graph and `model.onnx_data` files are FP32 weights. Q4, FP16, and Q8 size rows are other precisions. The quickstart names `past_key_values` and `past_conv` and does not state shapes, dtypes, or byte sizes.

  https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-ONNX/blob/10f72e70abf67ac0fd7ebf15bc5854726891d864/README.md

- `lfm-docs-overview`. Liquid AI documentation version `retrieved-2026-11-12`. The page states a dense instruction-tuned model, 32K context, and tool calling. It does not state hidden dimensions or FP32 resident memory.

  https://docs.liquid.ai/lfm/models/lfm25-1.2b-instruct

- `ort-session-defaults`. ONNX Runtime `v1.31.1` session header, revision `6af1a932e2286d5c58166085d24c68783033edee`. Defaults enable the memory pattern, memory reuse, and the CPU memory arena, and set graph optimization to the maximum level. The arena may preallocate. No byte bound for this model is stated.

  https://raw.githubusercontent.com/microsoft/onnxruntime/v1.31.1/onnxruntime/core/framework/session_options.h

- `ort-memory-page` and `ort-graph-opt`. ONNX Runtime documentation retrieved 2026-11-12. The memory page describes a shared arena and optional mimalloc and states no Linux resident bound for this model. The graph page says all optimization levels are enabled by default and describes constant folding and fusions. Neither page states a resident byte bound.

  https://onnxruntime.ai/docs/performance/tune-performance/memory.html

  https://onnxruntime.ai/docs/performance/model-optimizations/graph-optimizations.html

- `onnx-external-data`. ONNX external-data documentation, version `1.24.0`. Offsets should be page aligned so a runtime can map the file. The page does not require mapping and does not state a resident size.

  https://onnx.ai/onnx/repo-docs/ExternalData.html

- `fp32-logical-product`. Deterministic calculation: `1170340608 * 4 = 4681362432` logical bytes. Weight tying is not stated, so the product is not included in the peak.

- `margin-not-applied`. No official page states a safety-margin percentage or byte allowance for this FP32 CPU session. The margin stays unset.

Secondary runtime recipes are not used to close a dimension. The category dispositions are in [candidate-memory-budget.md](../architecture/candidate-memory-budget.md). The committed evidence record is [candidate-memory-evidence.json](../../candidates/authorization/candidate-memory-evidence.json).
