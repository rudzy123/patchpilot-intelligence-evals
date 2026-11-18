"""Track 10 review validators. They read committed records and do not call Run."""

from __future__ import annotations

import argparse
from typing import Any

from patchpilot_intelligence_evals.attributed_response_review import load_attributed_response
from patchpilot_intelligence_evals.diagnostic_proportionality import load_diagnostic_proportionality
from patchpilot_intelligence_evals.investment_stop_decision import load_investment_stop
from patchpilot_intelligence_evals.schema_invariant_review import load_schema_invariant_review
from patchpilot_intelligence_evals.six_run_diagnostic_authorization import (
    load_six_run_authorization,
)
from patchpilot_intelligence_evals.track10_candidate_disposition import load_track10_disposition
from patchpilot_intelligence_evals.track10_implementation_review import (
    load_track10_implementation_review,
)

VALIDATION = (
    "attributed-response-evidence-validation",
    "schema-invariant-review-validation",
    "diagnostic-proportionality-validation",
    "six-run-diagnostic-authorization-validation",
    "investment-stop-decision-validation",
    "track10-candidate-disposition-validation",
    "track10-implementation-review-validation",
)


def register(commands: Any) -> None:
    """Add the Track 10 review validators. There is no execute command."""
    for name in VALIDATION:
        commands.add_parser(name)


def handle(command: str, _args: argparse.Namespace) -> dict[str, Any]:
    """Validate one committed Track 10 record and return a path-free summary."""
    if command == "attributed-response-evidence-validation":
        document = load_attributed_response()
        return _ok(
            executionStopAuthority=document["executionStopAuthority"],
            responseFailureAuthority=document["responseFailureAuthority"],
            schemaStatus=document["schemaStatus"],
        )
    if command == "schema-invariant-review-validation":
        document = load_schema_invariant_review()
        return _ok(
            oneInvalidRunRejectsCandidate=document["oneInvalidRunRejectsCandidate"],
            rejectionCurrentlySupported=document["rejectionCurrentlySupported"],
        )
    if command == "diagnostic-proportionality-validation":
        document = load_diagnostic_proportionality()
        return _ok(selectedAlternative=document["selectedAlternative"])
    if command == "six-run-diagnostic-authorization-validation":
        document = load_six_run_authorization()
        return _ok(
            authorizationStatus=document["authorizationStatus"],
            futurePlanDigest=document["futurePlanDigest"],
            plannedDiagnosticRuns=document["plannedDiagnosticRuns"],
        )
    if command == "investment-stop-decision-validation":
        document = load_investment_stop()
        return _ok(
            recommendation=document["recommendation"],
            stopSelected=document["stopSelected"],
        )
    if command == "track10-candidate-disposition-validation":
        document = load_track10_disposition()
        return _ok(
            candidateDisposition=document["candidateDisposition"],
            track10Disposition=document["track10Disposition"],
        )
    if command == "track10-implementation-review-validation":
        document = load_track10_implementation_review()
        return _ok(
            reviewDigest=document["reviewDigest"],
            reviewStatus=document["reviewStatus"],
            sixRunDiagnostic=document["sixRunDiagnostic"],
        )
    raise KeyError(command)


def _ok(**fields: object) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "calibrationStatus": "not-approved",
        "comparisonWinner": None,
        "productionReady": False,
        "selectionOutcome": "no-selection",
        "status": "ok",
    }
    payload.update(fields)
    return payload
