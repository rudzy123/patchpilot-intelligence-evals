"""Track 9 candidate-disposition tests."""

import pytest

from patchpilot_intelligence_evals.candidate_disposition import (
    PAIRS,
    build_candidate_disposition,
    build_disposition,
    load_candidate_disposition,
    require_disposition,
)
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schemas import SchemaValidationError, validate


def test_committed_disposition_authorizes_continuation_without_selection() -> None:
    document = load_candidate_disposition()
    assert document == build_candidate_disposition()
    assert document["track9Disposition"] == "corpus-only-continuation-authorized-in-principle"
    assert (
        document["candidateDisposition"]
        == "evaluation-incomplete-continuation-authorized-in-principle"
    )
    assert document["selectedAlternative"] == "clean-24-case-corpus-only-rerun"
    assert document["continuationIsNotSelection"] is True
    assert document["selectionOutcome"] == "no-selection"
    assert document["calibrationStatus"] == "not-approved"
    assert document["comparisonWinner"] is None
    assert document["productionReady"] is False
    assert document["authorizesCandidateSelection"] is False
    assert document["authorizesCalibration"] is False
    assert document["authorizesProduction"] is False
    assert document["authorizesShadowMode"] is False
    assert document["authorizesPatchPilotIntegration"] is False
    assert document["authorizesCurrentExecution"] is False
    assert document["futurePlanDigest"] == "not-issued"
    assert document["operatorApproval"] == "not-issued"
    assert document["resultRootState"] == "not-created"


def test_every_disposition_pair_stays_frozen() -> None:
    for track9, candidate in PAIRS.items():
        document = build_disposition(track9)
        assert document["candidateDisposition"] == candidate
        assert document["selectionOutcome"] == "no-selection"
        assert document["comparisonWinner"] is None
        assert document["productionReady"] is False
        assert document["continuationIsNotSelection"] is True


def test_contradictory_authority_is_rejected() -> None:
    document = build_candidate_disposition()
    document["candidateDisposition"] = "candidate-rejected"
    validate("candidate-disposition", document)
    with pytest.raises(MeasurementError) as caught:
        require_disposition(document)
    assert caught.value.code == "contradictory-authority"


def test_schema_rejects_production_ready() -> None:
    document = build_candidate_disposition()
    document["productionReady"] = True
    with pytest.raises(SchemaValidationError):
        validate("candidate-disposition", document)
