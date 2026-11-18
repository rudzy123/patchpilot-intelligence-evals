"""Investment-stop decision tests."""

import pytest

from patchpilot_intelligence_evals.investment_stop_decision import (
    build_investment_stop,
    build_investment_stop_body,
    load_investment_stop,
    require_investment_stop,
)
from patchpilot_intelligence_evals.measurement_plan import MeasurementError


def test_stop_is_recorded_and_not_selected() -> None:
    document = load_investment_stop()
    assert document == build_investment_stop()
    assert document["stopSelected"] is False
    assert document["stopIsQualityVerdict"] is False
    assert document["candidateFailureIndependentlyProven"] is False
    assert document["memoryIsRejectionBasis"] is False
    assert document["memoryHeadroom"] == "limited-ceiling-passed"
    assert document["recommendation"] == "continue-only-six-run-in-principle"
    assert document["expectedSixRunEvidenceValue"] == "decision-grade-for-schema-behavior"
    assert document["opportunityCostOfStopping"] == "forgoes-narrow-schema-question"
    assert document["sixRunResourceCost"] == "six-run"
    assert document["fullCorpusResourceCost"] == "full-corpus"
    assert document["candidateRole"] == "non-authoritative-explanation-assistant"
    assert document["selectionOutcome"] == "no-selection"
    assert document["productionReady"] is False


def test_selecting_the_stop_is_rejected() -> None:
    document = build_investment_stop_body()
    document["stopSelected"] = True
    with pytest.raises(MeasurementError) as caught:
        require_investment_stop(document)
    assert caught.value.code == "stop-selected"


def test_quality_verdict_is_rejected() -> None:
    document = build_investment_stop_body()
    document["stopIsQualityVerdict"] = True
    with pytest.raises(MeasurementError) as caught:
        require_investment_stop(document)
    assert caught.value.code == "quality-verdict"


def test_unproven_candidate_failure_is_rejected() -> None:
    document = build_investment_stop_body()
    document["candidateFailureIndependentlyProven"] = True
    with pytest.raises(MeasurementError) as caught:
        require_investment_stop(document)
    assert caught.value.code == "unsupported-rejection"
