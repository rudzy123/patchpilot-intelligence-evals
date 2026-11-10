# Candidate protocol

Track 2 remains authoritative for the finding-explanation schemas, metric formulas, promotion gates, corpus, and `productionReady: false`. Track 3 adds a provider-neutral way to run a deterministic test double beside that harness.

One invocation sends one canonical UTF-8 JSON request on standard input and accepts one canonical UTF-8 JSON response on standard output. There is no shell, no stream, no interactive session, and no retry. A trailing extra JSON value or non-canonical whitespace fails closed.

The request carries the protocol version `1.0.0`, a request id, the case id, the authorized synthetic organization id, the Track 2 finding-explanation input, and the execution limits. It does not carry gold claims, expected citations, expected refusal, category, or negative controls. The child working directory contains only the copied fixture files. The fixture reads that request on standard input.

A response status is `success`, `unavailable`, or `rejected`. Success includes a Track 2 finding-explanation output. The explanation candidate kind stays `future-candidate` because that is the closed Track 2 vocabulary. The candidate manifest uses `deterministic-test-double` and must not claim to be a model or a hosted provider.

The harness classifies execution before it scores quality. Quality scoring uses the existing Track 2 metrics and only runs after `success`. A timeout, malformed body, oversized body, or nonzero exit stays unmeasured and does not increment the state-mutation gate.

No response field can assign affectedness, priority, Finding state, queue rank, or remediation completion. Those names fail the closed schema.
