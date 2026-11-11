# Candidate pre-screen

The pre-screen admits at most eight families and advances at most four. A family advances only when every screen below passes. The machine record is [candidate-discovery.json](../../candidates/authorization/candidate-discovery.json).

A different organization, size, quantized suffix, or revision of `gemma-3`, `olmo-2`, `qwen2.5`, or `smollm2` stays a prior checkpoint. Qwen3 and SmolLM3 do not carry those family tokens, so they are screened as later families.

The parameter band is 500,000,000 through 3,200,000,000 inclusive. That is the session reading of approximately 0.5B to 3B. A publisher-named 3B model inside that ceiling can pass the parameter screen. 3.8B-class listings fail it.

Discovery context must be an integer of at least 4,096. Finalist context fit still uses the existing envelope: official context must be an integer of at least 8,192. A shorter official context can be discovered and then fail hardware fit.

The listed artifact for discovery is the official graph plus its external data. It must be an integer at or below 8,589,934,592 bytes. Unknown size fails. Finalist footprint accounting is stricter and is described in [direct-onnx-selection.md](direct-onnx-selection.md).

Other advance requirements are an instruction-capable official card, an official non-quantized ONNX path, no required conversion, no required quantization, no required remote code, no automatic retrieval, no hosted API, no mandatory telemetry, CPU-only plausibility, and weight terms other than `absent`. Card-named licenses stay in discovery. Instrument depth is finalist work.

`LiquidAI/LFM2.5-1.2B-Instruct` advances. Its safetensors listing reports 1,170,340,608 parameters, the card states 32,768 tokens of context, and the FP32 graph plus external data lists 4,714,268,170 bytes.

`HuggingFaceTB/SmolLM3-3B` is a later family with its own card, revision, and architecture name. It is excluded because the non-quantized ONNX pair lists 12,334,174,552 bytes.

`Qwen/Qwen3-1.7B` and `ibm-granite/granite-3.3-2b-instruct` have no publisher ONNX graph in the pinned tree. `mistralai/Ministral-3-3B-Instruct-2512` lists 3,849,090,048 parameters, including FP8 weights, and its context was not established. `microsoft/Phi-4-mini-instruct` lists 3,836,021,760 parameters, requires remote code, and publishes int4 ONNX variants. `tiiuae/Falcon3-1B-Instruct` and `swiss-ai/Apertus-v1.1-0.5B-Instruct` are served as ONNX by onnx-community conversions. Apertus acceptable-use text also calls for periodic retrieval of an external filter.

The method and baseline are in [candidate-landscape-refresh.md](candidate-landscape-refresh.md).
