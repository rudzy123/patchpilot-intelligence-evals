# Candidate disposition authority

The Track 9 disposition is [candidate-disposition.json](../../candidates/authorization/candidate-disposition.json). The session disposition is `corpus-only-continuation-authorized-in-principle`. The candidate disposition is `evaluation-incomplete-continuation-authorized-in-principle`.

Continuation is not selection. `selectionOutcome` stays `no-selection`. Calibration stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false. Shadow mode, PatchPilot integration, and execution in this Session stay unauthorized.

Comparison still requires a complete result under one identity, as described in [result-retention.md](result-retention.md). The partial corpus is not scored, and missing cases are not imputed.

The proportionality record is [proportionality-decision.json](../../candidates/authorization/proportionality-decision.json). Rejecting the candidate now is withheld because no supported mandatory failure exists. A remaining-19 continuation would not be one comparable result. Narrow forensics cannot recover the missing raw output. Stopping further investment remains a valid proportionality choice and is not selected. The selected continuation is one clean 24-case corpus-only rerun, bounded in [corpus-continuation-boundary.md](corpus-continuation-boundary.md).

Principal Architect review on 2026-11-17 accepts this disposition. The acceptance record is [track9-implementation-review.md](../provenance/track9-implementation-review.md). Acceptance does not create a plan, a plan digest, an operator approval, or a result root.
