# Finalist suitability evidence

Retrieved on 2026-11-12. Evidence is the pinned Liquid AI card, the Liquid AI model page, and the pinned ONNX card. No benchmark score is used. No grounding, refusal, citation, uncertainty, prompt-injection, tenant-isolation, or hallucination rate is marked proven.

Screening outcome is `eligible-for-controlled-evaluation`. `measuredQualityClaimed` stays false. `realModelExecuted` stays false.

## Supported in principle

- `instruction-following`. The card describes an instruction-tuned model. Empirical evaluation on the English 24-case corpus is still required.
- `structured-output`. The card describes JSON tool calls. `outputSchemaValidity` is still required.
- `english-language`. The card lists English among the supported languages. Pass authority is the official statement.
- `context-capacity`. The published context length is `32768` tokens, which covers the `8192` evaluation cap. Memory fit is a separate record. Pass authority is the official statement.

## Empirical evaluation required

These capabilities stay `requires-empirical-evaluation`. The card does not state the behavior, and a general recommendation is not a measurement:

- `bounded-generation`, against the `400` character and `1200` word output bounds
- `deterministic-fact-separation`, metric `affectednessOrPriorityChange`
- `evidence-id-reproduction`, metric `citationValidity`
- `missing-evidence-reporting`, against the existing `missingEvidence` output array
- `uncertainty-expression`, metric `correctUncertainty`
- `unsupported-request-refusal`, metric `correctRefusal`
- `embedded-instruction-resistance`, metric `promptInjectionResistance`
- `state-mutation-avoidance`, metric `unauthorizedStateMutation`
- `cross-tenant-nondisclosure`, metric `crossTenantDisclosure`
- `schema-compatibility`, metric `outputSchemaValidity`

The card limitation that knowledge-intensive tasks are not recommended is a caveat. It is not a prohibition of evidence-bounded explanation, so `disqualifyingLimitation` stays false on every capability.

Sources:

https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct/blob/b9d816ab510f9a28dca37cb182e9da8b0226e13c/README.md

https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct-ONNX/blob/10f72e70abf67ac0fd7ebf15bc5854726891d864/README.md

https://docs.liquid.ai/lfm/models/lfm25-1.2b-instruct

The contract is [explanation-suitability-contract.md](../architecture/explanation-suitability-contract.md). The committed evidence record is [explanation-suitability-evidence.json](../../candidates/authorization/explanation-suitability-evidence.json). The earlier Track 7 suitability record is unchanged.
