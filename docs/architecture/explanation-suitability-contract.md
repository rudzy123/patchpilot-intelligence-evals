# Explanation suitability contract

Track 7B versions fourteen capabilities for evidence-bounded explanation. The contract maps each capability to an existing metric or to `metricName: null`. It adds no metric and does not edit a gate. `gatesUnchanged` stays true. `measuredQualityClaimed` stays false.

The disqualifying rule is the same for every capability: an official prohibition of evidence-bounded explanation disqualifies that capability. A published caveat that knowledge-intensive tasks are not recommended stays a caveat. It becomes a disqualifier only if the pinned card prohibits the approved use.

| Capability | Metric | Empirical evaluation | Pass authority |
| --- | --- | --- | --- |
| `instruction-following` | null | required | `empirical-harness` |
| `structured-output` | `outputSchemaValidity` | required | `empirical-harness` |
| `english-language` | null | not required | `official-statement` |
| `context-capacity` | null | not required | `official-statement` |
| `bounded-generation` | null | required | `empirical-harness` |
| `deterministic-fact-separation` | `affectednessOrPriorityChange` | required | `empirical-harness` |
| `evidence-id-reproduction` | `citationValidity` | required | `empirical-harness` |
| `missing-evidence-reporting` | null | required | `empirical-harness` |
| `uncertainty-expression` | `correctUncertainty` | required | `empirical-harness` |
| `unsupported-request-refusal` | `correctRefusal` | required | `empirical-harness` |
| `embedded-instruction-resistance` | `promptInjectionResistance` | required | `empirical-harness` |
| `state-mutation-avoidance` | `unauthorizedStateMutation` | required | `empirical-harness` |
| `cross-tenant-nondisclosure` | `crossTenantDisclosure` | required | `empirical-harness` |
| `schema-compatibility` | `outputSchemaValidity` | required | `empirical-harness` |

`deterministicReplayConsistency` is replay identity. `decisiveEvidenceOmission` counts omitted citation IDs. `evidenceAttributionAccuracy` remains a related reported gate. None of those three stands in for a capability that has no Track 2 metric.

Corpus categories stay the six taxonomy keys. `instruction-following`, `structured-output`, `bounded-generation`, `state-mutation-avoidance`, and `schema-compatibility` apply to every category. The others map to the category that already exercises that behavior: grounding and contradiction for fact separation, grounding for citation IDs, insufficient-evidence and stale evidence for missing-evidence reporting, contradiction plus those two for uncertainty, insufficient evidence for refusal, prompt injection for embedded instructions, and the cross-tenant negative control for nondisclosure.

English and context capacity may pass from an official statement. The published context length is `32768` tokens, which covers the evaluation cap of `8192`. Memory fit is a separate record. Safety-critical capabilities cannot waive empirical evaluation.

The committed contract is [explanation-suitability-contract.json](../../candidates/authorization/explanation-suitability-contract.json). The evidence mapping is [finalist-suitability-evidence.md](../provenance/finalist-suitability-evidence.md). Metric names stay those in [metric-definitions.md](metric-definitions.md). Promotion gates stay those in [promotion-gates.md](promotion-gates.md).
