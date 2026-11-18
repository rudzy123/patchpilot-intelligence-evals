"""Principal Architect review of the Track 10A schema diagnostic.

The review reads committed records and does not call Run.
"""

from __future__ import annotations

import json
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schema_diagnostic_plan import (
    load_schema_diagnostic_approval,
    load_schema_diagnostic_plan,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate

SCHEMA_NAME = "track10a-implementation-review"
_RECORD = "candidates/authorization/track10a-implementation-review.json"
PLAN_DIGEST = "7d90e79de202949231319b2c863a2d99b5aaed4edb1d87e0cf57673cdc9bec75"
SUMMARY_DIGEST = "65e5644e9b335f01aca61a1b0eed520f59e7c97a0a5bd3c3a2db68d65c614063"
CLOSEOUT_DIGEST = "0dc4601b10200f6f586918f7dcecaee00b0dbbc4aac86136176b445fdc7df74f"
TRACK11_DIGEST = "effb48a9b5ecba238b45ef2cbacfc54ca0bde74fcf8211d55424e855687c7742"
_SCOPE = (
    "This record accepts the sealed six-run schema diagnostic and the conclusion "
    "systematic-schema-failure-established. Observed realModelExecuted is true because "
    "the verified candidate was loaded, ONNX Runtime Run was invoked, and generation "
    "was observed. The external sealed files were not rewritten. This acceptance does "
    "not authorize automatic rejection, selection, calibration approval, full corpus "
    "evaluation, PatchPilot integration, shadow mode, production use, release, or "
    "deployment."
)
_RUNS: tuple[tuple[str, str], ...] = (
    ("case-ground-001-r1", "grounding-citation"),
    ("case-refuse-001-r1", "insufficient-evidence-refusal"),
    ("case-inject-001-r1", "prompt-injection"),
    ("case-tenant-001-r1", "cross-tenant-negative-control"),
    ("case-contra-001-r1", "contradiction"),
    ("case-stale-001-r1", "stale-unavailable-incomparable"),
)
_NOT_AUTHORIZED: tuple[str, ...] = (
    "automatic-rejection",
    "candidate-selection",
    "calibration-approval",
    "full-corpus-evaluation",
    "patchpilot-integration",
    "shadow-mode",
    "production-use",
    "release",
    "deployment",
)
_ATTRIBUTION: dict[str, Any] = {
    "adapterInnerFieldComparison": "matched",
    "adapterInnerFieldMutation": False,
    "blockingInfrastructureExplanation": False,
    "blockingSecurityExplanation": False,
    "extraction": "passed",
    "failureAuthority": "candidate-output",
    "intendedResponseSchemaApplied": True,
    "jsonParse": "passed",
    "outputLimitStatus": "within-limit",
    "rawOutputRetained": True,
    "truncation": False,
    "utf8": "passed",
}


def _failures() -> list[dict[str, Any]]:
    return [{"category": category, "runId": run_id, **_ATTRIBUTION} for run_id, category in _RUNS]


def _threshold() -> dict[str, Any]:
    return {
        "completeCandidateOutputAttribution": True,
        "countedAuthority": "candidate-output",
        "minimumDistinctCategories": 3,
        "minimumQualifyingFailures": 4,
        "requiredCompletedSealedRuns": 6,
    }


def assemble_track10a_review() -> dict[str, Any]:
    """Assemble the accepted review before its digest is sealed."""
    return {
        "approvalStatus": "not-approved",
        "authorizesFullCorpus": False,
        "authorizesRejection": False,
        "authorizesSelection": False,
        "authorizedScope": _SCOPE,
        "automaticCandidateRejection": False,
        "automaticCandidateSelection": False,
        "calibrationStatus": "not-approved",
        "closeoutDigest": CLOSEOUT_DIGEST,
        "comparisonWinner": None,
        "completedSealedRuns": 6,
        "containsExecutionInstructions": False,
        "currentExecutionAuthority": False,
        "decision": "systematic schema failure established",
        "diagnosticConclusion": "systematic-schema-failure-established",
        "distinctAffectedCategories": 6,
        "executionStatus": "not-executed",
        "externalSealedFilesRewritten": False,
        "externalSealedRealModelExecuted": False,
        "generationObserved": True,
        "infrastructureFailureCount": 0,
        "installationAuthorized": False,
        "maximumCgroupPeakBytes": 5901160448,
        "missingRuns": 0,
        "modelSessionCreated": True,
        "networkResult": "denied",
        "nextStep": "disposition-review-eligible",
        "notAuthorized": list(_NOT_AUTHORIZED),
        "oomEvents": 0,
        "planDigest": PLAN_DIGEST,
        "processCleanup": "reaped",
        "productionReady": False,
        "qualifyingCandidateOutputSchemaFailureCount": 6,
        "qualifyingFailures": _failures(),
        "readinessOutcome": "ready-for-disposition-review",
        "realModelExecuted": True,
        "rejectionEligibleForReview": True,
        "replacementPlanDigest": "not-issued",
        "residentCeilingBytes": 12884901888,
        "responseShapeConsistency": "divergent",
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "reviewDate": "2026-11-18",
        "reviewStatus": "accepted-by-principal-systems-architect",
        "runInvoked": True,
        "schemaValidCount": 0,
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
        "sessionId": "intelligence-track-10a",
        "summaryDigest": SUMMARY_DIGEST,
        "systematicThreshold": _threshold(),
        "telemetryStatus": "complete",
        "thresholdMet": True,
        "track11ReadinessDigest": TRACK11_DIGEST,
        "unresolvedCount": 0,
        "unsealedRuns": 0,
        "verdict": "SYSTEMATIC SCHEMA FAILURE ESTABLISHED",
    }


def require_track10a_review(document: dict[str, Any], *, sealed: bool = True) -> None:
    """Require the accepted review and keep pre-execution records unchanged."""
    if document["reviewDate"] != "2026-11-18":
        raise MeasurementError("review-drift")
    if document["reviewAuthority"] != "PatchPilot Principal Systems Architect":
        raise MeasurementError("review-drift")
    if document["reviewStatus"] != "accepted-by-principal-systems-architect":
        raise MeasurementError("review-drift")
    if document["verdict"] != "SYSTEMATIC SCHEMA FAILURE ESTABLISHED":
        raise MeasurementError("review-drift")
    if document["planDigest"] != PLAN_DIGEST:
        raise MeasurementError("plan-digest")
    if document["realModelExecuted"] is not True or document["runInvoked"] is not True:
        raise MeasurementError("execution-semantics")
    if document["modelSessionCreated"] is not True or document["generationObserved"] is not True:
        raise MeasurementError("execution-semantics")
    if document["externalSealedFilesRewritten"] is not False:
        raise MeasurementError("sealed-rewrite")
    if document["externalSealedRealModelExecuted"] is not False:
        raise MeasurementError("sealed-rewrite")
    if (
        document["executionStatus"] != "not-executed"
        or document["approvalStatus"] != "not-approved"
    ):
        raise MeasurementError("pre-execution")
    if document["automaticCandidateRejection"] is not False:
        raise MeasurementError("automatic-disposition")
    if document["automaticCandidateSelection"] is not False:
        raise MeasurementError("automatic-disposition")
    if document["selectionOutcome"] != "no-selection":
        raise MeasurementError("authority")
    if document["calibrationStatus"] != "not-approved" or document["comparisonWinner"] is not None:
        raise MeasurementError("authority")
    if document["productionReady"] is not False or document["installationAuthorized"] is not False:
        raise MeasurementError("authority")
    if document["currentExecutionAuthority"] is not False:
        raise MeasurementError("execution-authorized")
    if document["authorizesRejection"] is not False or document["authorizesSelection"] is not False:
        raise MeasurementError("execution-authorized")
    if document["authorizesFullCorpus"] is not False:
        raise MeasurementError("execution-authorized")
    if tuple(document["notAuthorized"]) != _NOT_AUTHORIZED:
        raise MeasurementError("contradictory-authority")
    if document["authorizedScope"] != _SCOPE:
        raise MeasurementError("review-drift")
    if document["qualifyingFailures"] != _failures():
        raise MeasurementError("attribution")
    if document["systematicThreshold"] != _threshold():
        raise MeasurementError("threshold")
    if (
        document["summaryDigest"] != SUMMARY_DIGEST
        or document["closeoutDigest"] != CLOSEOUT_DIGEST
        or document["track11ReadinessDigest"] != TRACK11_DIGEST
    ):
        raise MeasurementError("external-digest")
    plan = load_schema_diagnostic_plan()
    approval = load_schema_diagnostic_approval()
    if plan["planDigest"] != PLAN_DIGEST or approval["planDigest"] != PLAN_DIGEST:
        raise MeasurementError("plan-digest")
    if plan["executionStatus"] != "not-executed" or plan["realModelExecuted"] is not False:
        raise MeasurementError("pre-execution")
    if approval["approvalStatus"] != "not-approved" or approval["realModelExecuted"] is not False:
        raise MeasurementError("pre-execution")
    if approval["runInvoked"] is not False or approval["modelSessionCreated"] is not False:
        raise MeasurementError("pre-execution")
    observed = {key: value for key, value in document.items() if key != "reviewDigest"}
    if observed != assemble_track10a_review():
        raise MeasurementError("review-drift")
    if sealed and document.get("reviewDigest") != review_digest(document):
        raise MeasurementError("review-digest")


def build_track10a_implementation_review() -> dict[str, Any]:
    """Seal the accepted review. The digest is computed, not supplied."""
    document = assemble_track10a_review()
    require_track10a_review(document, sealed=False)
    document["reviewDigest"] = review_digest(document)
    reject_sensitive(document)
    validate(SCHEMA_NAME, document)
    require_track10a_review(document)
    return document


def load_track10a_implementation_review() -> dict[str, Any]:
    """Load the committed review and refuse drift from its builder."""
    loaded = json.loads((repo_root() / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    document = build_track10a_implementation_review()
    if loaded != document:
        raise MeasurementError("review-drift")
    return loaded
