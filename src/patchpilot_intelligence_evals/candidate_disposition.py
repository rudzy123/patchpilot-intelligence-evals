"""Track 9 candidate disposition. Continuation is not selection."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.proportionality_decision import SELECTED_ALTERNATIVE
from patchpilot_intelligence_evals.track9_review import common, load_record, seal

SCHEMA_NAME = "candidate-disposition"
_RECORD = "candidates/authorization/candidate-disposition.json"
PAIRS = {
    "corpus-only-continuation-authorized-in-principle": (
        "evaluation-incomplete-continuation-authorized-in-principle"
    ),
    "candidate-rejected": "candidate-rejected",
    "narrow-forensic-session-required": "further-forensics-required",
    "further-investment-stopped": "further-investment-stopped",
    "blocked-by-unresolved-authority": "blocked-by-unresolved-authority",
}
_ALTERNATIVES = {
    "corpus-only-continuation-authorized-in-principle": SELECTED_ALTERNATIVE,
    "candidate-rejected": "reject-now",
    "narrow-forensic-session-required": "narrow-forensics",
    "further-investment-stopped": "stop-investment",
    "blocked-by-unresolved-authority": "none",
}
_FALSE_AUTHORITY = (
    "authorizesCalibration",
    "authorizesCandidateSelection",
    "authorizesCurrentExecution",
    "authorizesPatchPilotIntegration",
    "authorizesProduction",
    "authorizesShadowMode",
)


def require_disposition(document: dict[str, Any]) -> None:
    """Keep selection, calibration, comparison, and production frozen."""
    track9 = document["track9Disposition"]
    if track9 not in PAIRS:
        raise MeasurementError("contradictory-authority")
    if document["candidateDisposition"] != PAIRS[track9]:
        raise MeasurementError("contradictory-authority")
    if document["selectedAlternative"] != _ALTERNATIVES[track9]:
        raise MeasurementError("contradictory-authority")
    if document["selectionOutcome"] != "no-selection":
        raise MeasurementError("contradictory-authority")
    if document["calibrationStatus"] != "not-approved":
        raise MeasurementError("contradictory-authority")
    if document["comparisonWinner"] is not None:
        raise MeasurementError("contradictory-authority")
    if document["productionReady"] is not False:
        raise MeasurementError("contradictory-authority")
    if document["continuationIsNotSelection"] is not True:
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


def build_disposition(track9: str) -> dict[str, Any]:
    """Build one consistent disposition. The committed file uses the continuation pair."""
    document = {
        **common(),
        "authorizesCalibration": False,
        "authorizesCandidateSelection": False,
        "authorizesCurrentExecution": False,
        "authorizesPatchPilotIntegration": False,
        "authorizesProduction": False,
        "authorizesShadowMode": False,
        "candidateDisposition": PAIRS[track9],
        "continuationIsNotSelection": True,
        "operatorApproval": "not-issued",
        "resultRootState": "not-created",
        "selectedAlternative": _ALTERNATIVES[track9],
        "track9Disposition": track9,
    }
    require_disposition(document)
    return seal(document, SCHEMA_NAME)


def build_candidate_disposition() -> dict[str, Any]:
    """Record the in-principle continuation without selecting the candidate."""
    return build_disposition("corpus-only-continuation-authorized-in-principle")


def load_candidate_disposition() -> dict[str, Any]:
    """Return the committed candidate disposition."""
    return load_record(_RECORD, build_candidate_disposition)
