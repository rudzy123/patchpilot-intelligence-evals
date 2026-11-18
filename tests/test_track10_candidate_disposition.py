"""Track 10 candidate-disposition tests."""

import json

import pytest

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schemas import SchemaValidationError, repo_root, validate
from patchpilot_intelligence_evals.track10_candidate_disposition import (
    SCHEMA_NAME,
    build_disposition,
    build_disposition_body,
    build_track10_disposition,
    load_track10_disposition,
    require_disposition,
)
from patchpilot_intelligence_evals.track10_review import PAIRS, TRACK_DISPOSITIONS


def test_committed_disposition_authorizes_six_run_without_selection() -> None:
    document = load_track10_disposition()
    assert document == build_track10_disposition()
    assert document["track10Disposition"] == "six-run-diagnostic-authorized-in-principle"
    assert (
        document["candidateDisposition"]
        == "evaluation-incomplete-six-run-diagnostic-authorized-in-principle"
    )
    assert document["selectedAlternative"] == "six-run-diagnostic"
    assert document["authorizesFutureDiagnosticInPrinciple"] is True
    assert document["sixRunPrecedesFullRerun"] is True
    assert document["diagnosticIsNotSelection"] is True
    assert document["diagnosticIsNotCompleteEvaluation"] is True
    assert document["diagnosticIsNotPromotion"] is True
    assert document["diagnosticIsNotCalibration"] is True
    assert document["selectionOutcome"] == "no-selection"
    assert document["calibrationStatus"] == "not-approved"
    assert document["comparisonWinner"] is None
    assert document["productionReady"] is False
    assert document["mandatoryFailureSupported"] is False
    assert document["authorizesCandidateSelection"] is False
    assert document["authorizesCurrentExecution"] is False
    assert document["futurePlanDigest"] == "not-issued"
    assert document["operatorApproval"] == "not-issued"
    assert document["resultRootState"] == "not-created"


def test_other_pairs_stay_frozen_and_are_not_committed() -> None:
    committed = load_track10_disposition()
    for track, candidate in PAIRS.items():
        document = build_disposition(track)
        assert document["candidateDisposition"] == candidate
        assert document["selectionOutcome"] == "no-selection"
        assert document["comparisonWinner"] is None
        assert document["productionReady"] is False
        assert document["mandatoryFailureSupported"] is False
        assert document["futurePlanDigest"] == "not-issued"
        if track != "six-run-diagnostic-authorized-in-principle":
            assert document != committed


def test_contradictory_pair_is_rejected() -> None:
    document = build_disposition_body("six-run-diagnostic-authorized-in-principle")
    document["candidateDisposition"] = "candidate-rejected"
    with pytest.raises(MeasurementError) as caught:
        require_disposition(document)
    assert caught.value.code == "contradictory-authority"


def test_schema_rejects_production_ready() -> None:
    document = build_track10_disposition()
    document["productionReady"] = True
    with pytest.raises(SchemaValidationError):
        validate(SCHEMA_NAME, document)


def test_schema_supports_every_disposition_value() -> None:
    document = build_track10_disposition()
    for track in TRACK_DISPOSITIONS:
        document["track10Disposition"] = track
        validate(SCHEMA_NAME, document)


def test_records_omit_execution_markers_and_host_paths() -> None:
    root = repo_root()
    names = (
        "attributed-response-evidence.json",
        "schema-invariant-review.json",
        "diagnostic-proportionality.json",
        "six-run-diagnostic-authorization.json",
        "investment-stop-decision.json",
        "track10-candidate-disposition.json",
    )
    for name in names:
        text = (root / "candidates" / "authorization" / name).read_text(encoding="utf-8")
        document = json.loads(text)
        assert document["futurePlanDigest"] == "not-issued"
        assert document["operatorApproval"] == "not-issued"
        assert document["resultRootState"] == "not-created"
        assert document["containsExecutionInstructions"] is False
        for marker in ("/home/", "/var/", "http://", "https://", "InferenceSession", "onnxruntime"):
            assert marker not in text
