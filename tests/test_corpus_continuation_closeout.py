"""Closeout records planned, missing, cleanup, retention, and the memory residual."""

from __future__ import annotations

from patchpilot_intelligence_evals.corpus_continuation_closeout import load_closeout_template
from patchpilot_intelligence_evals.corpus_continuation_plan import PLANNED_RUNS, load_corpus_plan


def test_template_stays_not_closed() -> None:
    document = load_closeout_template()
    plan = load_corpus_plan()
    assert document["closeoutState"] == "not-closed"
    assert document["blocker"] == "operator-approval"
    assert document["plannedRuns"] == PLANNED_RUNS
    assert document["completedRuns"] == 0
    assert document["missingRuns"] == PLANNED_RUNS
    assert document["cleanup"] == "not-performed"
    assert document["retention"] == "not-performed"
    assert document["memoryResidual"]["remeasured"] is False
    assert document["memoryResidual"]["conclusion"] == plan["acceptedMemory"]["conclusion"]
    assert document["comparisonWinner"] is None
    assert document["productionReady"] is False
    assert document["selectionOutcome"] == "no-selection"
    assert document["calibrationStatus"] == "not-approved"
