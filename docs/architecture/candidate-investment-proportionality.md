# Candidate investment proportionality

The proportionality record is [diagnostic-proportionality.json](../../candidates/authorization/diagnostic-proportionality.json). The stop record is [investment-stop-decision.json](../../candidates/authorization/investment-stop-decision.json).

Track 10 compares five alternatives with closed categories. Rejecting the candidate now is ineligible because no supported mandatory failure exists. Protocol forensics are ineligible because the adapter, prompt, parser, and evaluator behavior are already proven. A full 72-run continuation can produce complete metrics later and is not selected now; its cost category is `full-corpus`, and another infrastructure failure would repeat a corpus loss. Stopping further investment is an eligible program decision, not a candidate-quality verdict, and it is not selected. The selected alternative is one six-run diagnostic. Its evidence value is `decision-grade-for-schema-behavior` and its cost category is `six-run`. That diagnostic precedes any full rerun.

Memory remains `within-ceiling-with-limited-headroom`. The limited headroom is not a rejection basis. Security risk stays unchanged. `qualityVerdict` stays false on every alternative.

`selectionOutcome` stays `no-selection`. `calibrationStatus` stays `not-approved`. `comparisonWinner` stays null. `productionReady` stays false.
