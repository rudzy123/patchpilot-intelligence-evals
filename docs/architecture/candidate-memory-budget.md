# Candidate memory budget

Track 7B records one resident-memory model for `LiquidAI/LFM2.5-1.2B-Instruct`. The process ceiling is `MEMORY_CAP`, `12884901888` bytes. A total that equals that ceiling can pass. One byte over fails. A missing required upper bound stays `unresolved`. The arithmetic does not store a partial sum as peak memory and does not replace an unknown category with zero.

Units are bytes. GiB conversion uses `1024**3` and is display-only. Decimal gigabytes, logical artifact size, resident set, virtual address space, allocator capacity, and `RLIMIT_AS` are separate domains. The harness metric `peakProcessMemory` remains Linux `ru_maxrss` kilobytes. The hardened profile `MemoryMax` of `268435456` bytes and `RLIMIT_AS` of `2147483648` bytes are launcher controls.

## Categories

Every envelope includes these categories, each with `includedInTotal` true and memory domain `resident`:

| Category | Formula |
| --- | --- |
| `static_parameter_memory` | `parameter_count * bytes_per_fp32_parameter` |
| `graph_and_initializer_overhead` | `resident_initializer_bytes_excluding_counted_parameter_payload` |
| `runtime_process_baseline` | `runtime_process_resident_bytes` |
| `allocator_and_optimization_overhead` | `arena_pattern_optimizer_and_thread_pool_resident_bytes` |
| `activation_memory` | `batch_size * sequence_tokens * activation_bytes_per_token` |
| `architecture_state_memory` | `attention_state_bytes + convolution_state_bytes` |
| `input_output_tensor_memory` | `input_id_bytes + mask_bytes + logits_bytes` |
| `tokenizer_and_configuration_memory` | `resident_tokenizer_bytes + resident_configuration_bytes` |
| `hardened_execution_overhead` | `launcher_ipc_and_attestation_resident_bytes` |
| `safety_margin` | `explicit_margin_bytes_after_complete_upper_bounds` |

Only `static_parameter_memory` may count the parameter payload. The committed parameter count is `1170340608`. Four bytes per parameter gives `4681362432` logical bytes. Weight tying is not stated, so that product is recorded as `logicalBytes` and is excluded from the peak. `safety_margin` stays unset until every other required upper bound is known. There is no hidden percentage.

## Envelopes

The committed record has two envelopes: batch size 1, one CPU process, FP32, no quantization, no speculative decoding, and no automatic batching. The context lengths are `4096` and `8192` tokens. Shared categories use the same inputs. Activation, architecture-state, and input-output inputs may differ by context, and only when official architecture inputs exist. Those widths are unpublished, so both envelopes stay:

- `upperBoundBytes`: null
- `lowerBoundBytes`: null
- `classification`: `unresolved`
- `ceilingComparison`: `unresolved`
- `bytesRelativeToCeiling`: null

All ten category identifiers remain unresolved. `measurementPerformed` stays false. `peakMemoryBasis` stays `unknown-fp32`.

The model, evidence, and budget records are [candidate-memory-model.json](../../candidates/authorization/candidate-memory-model.json), [candidate-memory-evidence.json](../../candidates/authorization/candidate-memory-evidence.json), and [candidate-memory-budget.json](../../candidates/authorization/candidate-memory-budget.json). Source notes are in [finalist-memory-evidence.md](../provenance/finalist-memory-evidence.md). Synthetic tests cover a complete model, a missing category, a duplicate, double counting, a unit mismatch, binary versus decimal units, signed overflow, an unknown upper bound, the exact ceiling, and one byte over. Those boundary cases use synthetic integers. The committed record does not invent byte totals.

This model does not reopen the Track 7A storage result in [artifact-budget-model.md](artifact-budget-model.md). Logical storage and resident process memory stay distinct.
