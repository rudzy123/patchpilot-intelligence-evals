"""Track 9 stays advisory before measurement."""

from __future__ import annotations

from patchpilot_intelligence_evals.inference_retry_track9 import (
    build_track9_template,
    load_track9_template,
)


def test_track9_template_is_not_ready() -> None:
    document = load_track9_template()
    assert document == build_track9_template()
    assert document["readinessOutcome"] == "not-ready"
    assert document["reason"] == "measurement-not-performed"
    assert document["verdict"] == "TRACK 9 EVALUATION REVIEW NOT READY"
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert document["selectionOutcome"] == "no-selection"
    assert document["calibrationStatus"] == "not-approved"
