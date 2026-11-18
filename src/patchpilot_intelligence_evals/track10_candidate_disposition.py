"""Track 10 candidate disposition. A future diagnostic is not selection."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.track10_review import (
    DECISION_ALTERNATIVES,
    SELECTED_TRACK,
    common,
    decision_for,
    load_record,
    require_authority_separation,
    require_frozen,
    require_no_operational,
    seal,
)

SCHEMA_NAME = "track10-candidate-disposition"
_RECORD = "candidates/authorization/track10-candidate-disposition.json"
_FALSE_AUTHORITY = (
    "authorizesCalibration",
    "authorizesCandidateSelection",
    "authorizesCurrentExecution",
    "authorizesPatchPilotIntegration",
    "authorizesProduction",
    "authorizesShadowMode",
)


def require_disposition(document: dict[str, Any]) -> None:
    """Keep one consistent pair and frozen authority."""
    require_frozen(document)
    require_no_operational(document)
    require_authority_separation(document)
    track = document["track10Disposition"]
    expected = decision_for(track)
    if document["candidateDisposition"] != expected["candidateDisposition"]:
        raise MeasurementError("contradictory-authority")
    if document["selectedAlternative"] != expected["selectedAlternative"]:
        raise MeasurementError("contradictory-authority")
    if tuple(document["decisionAlternatives"]) != DECISION_ALTERNATIVES:
        raise MeasurementError("contradictory-authority")
    if document["mandatoryFailureSupported"] is not False:
        raise MeasurementError("unsupported-rejection")
    expected_precedence = track == SELECTED_TRACK
    if document["sixRunPrecedesFullRerun"] is not expected_precedence:
        raise MeasurementError("contradictory-authority")
    in_principle = track == SELECTED_TRACK
    if document["authorizesFutureDiagnosticInPrinciple"] is not in_principle:
        raise MeasurementError("contradictory-authority")
    if document["diagnosticIsNotSelection"] is not True:
        raise MeasurementError("contradictory-authority")
    if document["diagnosticIsNotCompleteEvaluation"] is not True:
        raise MeasurementError("contradictory-authority")
    if document["diagnosticIsNotPromotion"] is not True:
        raise MeasurementError("contradictory-authority")
    if document["diagnosticIsNotCalibration"] is not True:
        raise MeasurementError("contradictory-authority")
    for name in _FALSE_AUTHORITY:
        if document[name] is not False:
            raise MeasurementError("contradictory-authority")
    if document["operatorApproval"] != "not-issued":
        raise MeasurementError("approval-issued")
    if document["resultRootState"] != "not-created":
        raise MeasurementError("result-root-created")
    if document["futurePlanDigest"] != "not-issued":
        raise MeasurementError("plan-issued")


def build_disposition_body(track: str) -> dict[str, Any]:
    """Build one disposition body. Rejection stays unsupported."""
    document = {
        **common(),
        **decision_for(track),
        "authorizesCalibration": False,
        "authorizesCandidateSelection": False,
        "authorizesCurrentExecution": False,
        "authorizesFutureDiagnosticInPrinciple": track == SELECTED_TRACK,
        "authorizesPatchPilotIntegration": False,
        "authorizesProduction": False,
        "authorizesShadowMode": False,
        "diagnosticIsNotCalibration": True,
        "diagnosticIsNotCompleteEvaluation": True,
        "diagnosticIsNotPromotion": True,
        "diagnosticIsNotSelection": True,
        "mandatoryFailureSupported": False,
        "operatorApproval": "not-issued",
        "resultRootState": "not-created",
        "sixRunPrecedesFullRerun": track == SELECTED_TRACK,
    }
    require_disposition(document)
    return document


def build_disposition(track: str) -> dict[str, Any]:
    """Seal one consistent disposition."""
    return seal(build_disposition_body(track), SCHEMA_NAME)


def build_track10_disposition() -> dict[str, Any]:
    """Record the in-principle six-run diagnostic without selecting the candidate."""
    return build_disposition(SELECTED_TRACK)


def load_track10_disposition() -> dict[str, Any]:
    """Return the committed Track 10 disposition."""
    return load_record(_RECORD, build_track10_disposition)
