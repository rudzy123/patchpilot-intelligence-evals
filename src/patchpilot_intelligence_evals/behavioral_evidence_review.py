"""Track 9 behavioral-evidence review. Incomplete evidence is not scored."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.track9_review import (
    BEHAVIOR_SOURCE_DIGEST,
    FORENSICS_SOURCE_DIGEST,
    common,
    load_record,
    seal,
)

SCHEMA_NAME = "behavioral-evidence-review"
_RECORD = "candidates/authorization/behavioral-evidence-review.json"
SEALED_CASE_IDS = (
    "case-contra-001",
    "case-contra-002",
    "case-contra-003",
    "case-ground-001",
    "case-ground-002",
)
_AUTHORITIES = frozenset({"adapter", "candidate-output", "evaluator", "protocol", "unresolved"})


def score_corpus(document: Mapping[str, Any]) -> None:
    """Scoring stays closed until the corpus, raw output, and authority are complete."""
    if document["behavioralMeasurementCompleted"] is not True:
        raise MeasurementError("incomplete-evidence")
    if document["casesWithoutResults"] != 0:
        raise MeasurementError("incomplete-evidence")
    if document["candidateMetricsProduced"] is not True:
        raise MeasurementError("incomplete-evidence")
    if document["scoringPermitted"] is not True:
        raise MeasurementError("incomplete-evidence")


def impute_cases(document: Mapping[str, Any], outcome: str) -> None:
    """Missing cases are neither passes nor failures."""
    if outcome in {"pass", "fail"}:
        raise MeasurementError("imputation-prohibited")
    if document["casesWithoutResults"] != 0 or document["imputationPermitted"] is not False:
        raise MeasurementError("imputation-prohibited")
    raise MeasurementError("imputation-prohibited")


def assign_failure_authority(authority: str) -> None:
    """The sealed runs stay unresolved. Another authority is not assigned."""
    if authority not in _AUTHORITIES or authority != "unresolved":
        raise MeasurementError("unresolved-authority")


def require_behavior(document: Mapping[str, Any]) -> None:
    """Refuse a candidate-quality conclusion from the partial corpus."""
    if document["schemaFailuresObserved"] != 15:
        raise MeasurementError("incomplete-evidence")
    if document["completeCaseGroups"] != 5 or document["sealedRepetitions"] != 3:
        raise MeasurementError("incomplete-evidence")
    if document["unsealedLaunches"] != 1 or document["casesWithoutResults"] != 19:
        raise MeasurementError("incomplete-evidence")
    if document["corpusCaseCount"] != 24:
        raise MeasurementError("incomplete-evidence")
    if document["completeCaseGroups"] + document["casesWithoutResults"] != 24:
        raise MeasurementError("incomplete-evidence")
    if tuple(document["sealedCaseIds"]) != SEALED_CASE_IDS:
        raise MeasurementError("incomplete-evidence")
    if document["schemaFailureAuthority"] != "unresolved":
        raise MeasurementError("unresolved-authority")
    if document["candidateCharacterizedAsSchemaNoncompliant"] is not False:
        raise MeasurementError("unresolved-authority")
    for name in (
        "candidateQualityConclusion",
        "empiricalCapabilityConclusions",
        "schemaComplianceConclusion",
    ):
        if document[name] != "unavailable":
            raise MeasurementError("incomplete-evidence")
    if document["behavioralConclusion"] != "partial-inconclusive":
        raise MeasurementError("incomplete-evidence")
    if document["missingCasesTreatedAsPasses"] or document["missingCasesTreatedAsFailures"]:
        raise MeasurementError("imputation-prohibited")
    if document["rawOutputRetained"] or document["parseErrorsRetained"]:
        raise MeasurementError("incomplete-evidence")
    if document["schemaErrorsRetained"] is not False:
        raise MeasurementError("incomplete-evidence")


def build_behavioral_evidence_review() -> dict[str, Any]:
    """Record the partial corpus without scoring it."""
    document = {
        **common(),
        "behavioralConclusion": "partial-inconclusive",
        "behavioralMeasurementAttempted": True,
        "behavioralMeasurementCompleted": False,
        "candidateCharacterizedAsSchemaNoncompliant": False,
        "candidateEvaluatedCompletely": False,
        "candidateMetricsProduced": False,
        "candidateQualityConclusion": "unavailable",
        "casesWithoutResults": 19,
        "comparisonStatus": "not-executed",
        "completeCaseGroups": 5,
        "corpusCaseCount": 24,
        "correctionBlocker": "raw-output-not-retained",
        "empiricalCapabilityConclusions": "unavailable",
        "imputationPermitted": False,
        "missingCasesTreatedAsFailures": False,
        "missingCasesTreatedAsPasses": False,
        "parseErrorsRetained": False,
        "percentageGatesCalibrated": False,
        "rawOutputRetained": False,
        "schemaComplianceConclusion": "unavailable",
        "schemaErrorsRetained": False,
        "schemaFailureAuthority": "unresolved",
        "schemaFailuresObserved": 15,
        "scoringPermitted": False,
        "sealedCaseIds": list(SEALED_CASE_IDS),
        "sealedRepetitions": 3,
        "sourceBehaviorDigest": BEHAVIOR_SOURCE_DIGEST,
        "sourceForensicsDigest": FORENSICS_SOURCE_DIGEST,
        "summaryStop": "telemetry-unresolved",
        "unsealedLaunches": 1,
    }
    require_behavior(document)
    return seal(document, SCHEMA_NAME)


def load_behavioral_evidence_review() -> dict[str, Any]:
    """Return the committed behavioral review."""
    return load_record(_RECORD, build_behavioral_evidence_review)
