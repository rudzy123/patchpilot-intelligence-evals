# Selected candidate authorization

Outcome: no candidate is authorized.

Review status is `accepted-by-principal-systems-architect`.

Recorded acceptance:

- review date: 2026-11-10
- review authority: PatchPilot Principal Systems Architect
- decision: no candidate authorized

The no-selection decision is approved because:

1. The current candidate protocol authorizes deterministic test doubles but does not yet represent or stage real-model artifacts.
2. The current runner denies the required external weight-cache boundary.
3. The current 15-second limit has not been justified for real-model startup.
4. Every reviewed candidate has at least one independent mandatory licensing, provenance, model-card, tokenizer, digest, commercial-use, or remote-control blocker.

This approval authorizes the no-selection record only. It does not authorize any candidate, model or tokenizer acquisition, a runtime dependency, quantization, real-model execution, changes to current evaluation gates, shadow mode, or PatchPilot production composition.

`selectionOutcome` is `no-selection`. `acquisitionStatus` remains `not-acquired`. `executionStatus` remains `not-executed`. `productionReady` remains false. Locally observed artifact digests remain empty. The approved model, revision, source, model card, license, tokenizer, runtime, and quantization are unset.

The blockers are the shortlist in [candidate-shortlist.md](candidate-shortlist.md) and the current harness boundary. Every reviewed checkpoint fails at least one mandatory criterion. The candidate manifest accepts only a deterministic test double. The child path boundary denies an external weight cache. This track cannot raise the 15-second timeout. No runtime is authorized.

Prohibited uses are production decisions; tenant, customer, or production data; finding, priority, queue, or remediation authority; weight redistribution; `trust_remote_code`; and hosted inference.

Track 5 stops before acquisition or execution. It also stops before any gate change and before any claim that this record approves production use. A later track can score a checkpoint only after the manifest identity, weight-cache denial, and timeout ceiling have an accepted revision, and after the missing license, tokenizer, limitations, and digest evidence named in the authorization record is closed.

The acquisition template that withholds download permission is [real-candidate-acquisition.md](../architecture/real-candidate-acquisition.md). The experiment that is not authorized to run is [real-candidate-evaluation-plan.md](../architecture/real-candidate-evaluation-plan.md). Isolation limits are in [real-candidate-isolation.md](../architecture/real-candidate-isolation.md).

The proposed commit subject for later review is `docs(evals): record no offline candidate authorization`. The specification's example subject would say a candidate had been authorized. That subject does not match this record.
