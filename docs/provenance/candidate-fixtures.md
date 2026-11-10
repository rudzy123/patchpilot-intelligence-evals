# Candidate fixture provenance

The eight candidate fixtures under `candidates/fixtures/` are original synthetic Apache-2.0 test doubles written for this repository. They are not models, model weights, or provider clients. No tenant, customer, production prompt, SBOM, advisory payload, or educational notebook content was copied into them.

Each fixture manifest records `candidateKind` as `deterministic-test-double`, license `Apache-2.0`, source `original-synthetic`, network policy `prohibited`, and review status `accepted-by-principal-systems-architect`. The corpus provenance sentence in [initial-corpus-provenance.md](initial-corpus-provenance.md) is unchanged.

Recorded acceptance:

- review date: 2026-11-09
- review authority: PatchPilot Principal Systems Architect
- approved scope: deterministic test-double design, stdin-only authorized-input behavior, fixture-local synthetic constants, offline subprocess execution, failure-taxonomy coverage, and evaluator/calibration sensitivity

This approval authorizes deterministic harness evaluation only. It does not authorize a real model, provider, model weights, model-quality claims, shadow mode, production composition, gate changes, affectedness, or priority authority.

Quality fixtures read only the canonical candidate request on standard input. They do not open corpus cases, gold claims, expected citations, refusal labels, category labels, prompt-injection labels, or negative controls. The conforming fixture restates authorized structured fields from that input. The unsupported-claim fixture adds the fixed sentence "Synthetic unsupported claim for harness sensitivity." The prompt-injection fixture copies `INJECT-` tokens that already appear in the authorized request text. The cross-tenant fixture emits its own declared marker `org-synthetic-fixture-forbidden` and does not read case canaries. A conforming run is harness behavior for an authorized input, not model quality.

Permitted use is offline harness evaluation in this repository. Prohibited uses are production decisions, model training, tenant analysis, provider execution, and PatchPilot state mutation.
