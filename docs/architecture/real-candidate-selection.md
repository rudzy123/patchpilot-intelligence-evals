# Real candidate selection

Track 4 selects at most one small offline candidate for a later Finding Explanation Assistant evaluation. A checkpoint that fails any mandatory criterion is disqualified. Disqualified checkpoints do not receive a weighted score.

The mandatory criteria are:

- explicit weight-use license
- clear commercial-use position
- clear redistribution position
- immutable official revision
- no remote-code requirement
- fully offline runtime support
- tokenizer provenance
- artifact digest capability
- fit within the local resource envelope
- compatibility with the current bounded subprocess evaluation
- no mandatory telemetry
- no tenant-data requirement
- official model card
- documented limitations
- no PatchPilot production dependency

An unresolved conflict in weight use, tokenizer licensing, commercial use, remote code, or immutable artifact identity disqualifies the checkpoint. A model card is not a license. A permissive code license does not license weights or a tokenizer. The more restrictive reading controls when sources conflict.

Eligible checkpoints would be scored on a 100-point scale:

- license, weight-use clarity, and provenance: 25
- security, remote-code avoidance, and offline isolation: 20
- local hardware and memory fit: 20
- Finding Explanation Assistant evaluation suitability: 20
- model-card completeness and limitation disclosure: 10
- runtime maturity and reproducibility: 5

Tie-breaking order, used only after every mandatory criterion passes, is: clearer weight and tokenizer licensing; no custom or remote code; lower estimated peak memory; smaller artifact size; stronger immutable artifact identity; better model-card disclosure; more mature offline runtime support. Leaderboard position, popularity, download count, and benchmark prestige are excluded.

This track applies the rubric and does not apply the scores. All five shortlisted checkpoints fail at least one mandatory criterion, including compatibility with the current subprocess boundary described in [subprocess-isolation.md](subprocess-isolation.md) and [candidate-protocol.md](candidate-protocol.md). The manifest accepts only a deterministic test double. The child can open files in its temporary runtime, this package, the standard library, and the interpreter prefixes. An external weight cache is denied, and the timeout ceiling remains 15 seconds. No runtime is authorized.

The evidence register is [candidate-shortlist.md](../provenance/candidate-shortlist.md). The authorization record in [selected-candidate-authorization.md](../provenance/selected-candidate-authorization.md) is `accepted-by-principal-systems-architect` on 2026-11-10 for the no-selection record only. Promotion gates in [promotion-gates.md](promotion-gates.md) are unchanged. `productionReady` remains false.
