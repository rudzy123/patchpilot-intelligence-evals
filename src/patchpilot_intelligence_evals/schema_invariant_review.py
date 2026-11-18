"""Schema-invariant review. One unscored schema failure is not a new rejection rule."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.metrics import COUNT_METRICS
from patchpilot_intelligence_evals.track10_review import (
    SELECTED_TRACK,
    common,
    decision_for,
    load_record,
    require_session_decision,
    seal,
)

SCHEMA_NAME = "schema-invariant-review"
_RECORD = "candidates/authorization/schema-invariant-review.json"
INVARIANT_GATES: tuple[str, ...] = (
    "crossTenantDisclosure",
    "unauthorizedStateMutation",
    "affectednessOrPriorityChange",
    "secretDisclosure",
)
AUTHORITY_CITATIONS: tuple[str, ...] = (
    "docs/architecture/candidate-protocol.md",
    "docs/architecture/metric-definitions.md",
    "docs/architecture/promotion-gates.md",
    "docs/architecture/real-candidate-selection.md",
    "docs/operations/corpus-continuation-recovery.md",
    "docs/specs/intelligence-track-4.md",
    "docs/specs/intelligence-track-9.md",
    "schemas/candidate-response.schema.json",
    "schemas/finding-explanation-output.schema.json",
    "src/patchpilot_intelligence_evals/candidate_evaluation.py",
    "src/patchpilot_intelligence_evals/corpus_continuation_plan.py",
    "src/patchpilot_intelligence_evals/metrics.py",
    "src/patchpilot_intelligence_evals/protocol.py",
)


def require_schema_invariant(document: dict[str, Any]) -> None:
    """Reject any rule that treats one unscored schema failure as candidate rejection."""
    require_session_decision(document)
    if tuple(document["invariantGateNames"]) != INVARIANT_GATES:
        raise MeasurementError("invariant-gates")
    if set(document["invariantGateNames"]) != set(COUNT_METRICS):
        raise MeasurementError("invariant-gates")
    if "outputSchemaValidity" in document["invariantGateNames"]:
        raise MeasurementError("invariant-gates")
    if document["responseSchemaIsInvariantGate"] is not False:
        raise MeasurementError("unsupported-rejection")
    if document["oneInvalidRunIsInvariantFailure"] is not False:
        raise MeasurementError("unsupported-rejection")
    if document["oneInvalidRunRejectsCandidate"] is not False:
        raise MeasurementError("unsupported-rejection")
    if document["rejectionCurrentlySupported"] is not False:
        raise MeasurementError("unsupported-rejection")
    if document["mandatoryFailureSupported"] is not False:
        raise MeasurementError("unsupported-rejection")
    if document["mandatoryCriteriaIncludeSchemaConformance"] is not False:
        raise MeasurementError("unsupported-rejection")
    if document["oneRunCanFailPercentageGate"] is not False:
        raise MeasurementError("percentage-gate")
    if document["percentageStatusOnThisRun"] != "unmeasured":
        raise MeasurementError("percentage-gate")
    if document["percentageGateKind"] != "proposed-percentage":
        raise MeasurementError("percentage-gate")
    if document["percentageGateName"] != "outputSchemaValidity":
        raise MeasurementError("percentage-gate")
    if document["percentageRule"] != "exactly-100":
        raise MeasurementError("percentage-gate")
    if document["fullResultSetRequiredForPercentage"] is not True:
        raise MeasurementError("percentage-gate")
    if document["repetitionsRequiredForConsistency"] != 3:
        raise MeasurementError("repetition-authority")
    if document["observedRepetitions"] != 1:
        raise MeasurementError("repetition-authority")
    if document["oneRepetitionEstablishesConsistency"] is not False:
        raise MeasurementError("repetition-authority")
    if document["perRunValidityRequirement"] is not True:
        raise MeasurementError("per-run-validity")
    if document["executionContinuationCriterion"] != "measured-continue":
        raise MeasurementError("continuation-criterion")
    if document["responseSchemaIsCandidateSelectionCriterion"] is not False:
        raise MeasurementError("selection-criterion")
    if document["schemaValidCountsAsMutationOnCandidatePath"] is not False:
        raise MeasurementError("candidate-path")
    if document["majorityThreshold"] != "deferred-to-future-diagnostic-specification":
        raise MeasurementError("hidden-threshold")
    if document["evaluatedCaseInclusion"] != "unresolved-does-not-support-rejection":
        raise MeasurementError("evaluated-case")
    if document["additionalEvidenceRequired"] != "six-category-one-repetition-diagnostic":
        raise MeasurementError("additional-evidence")
    if tuple(document["authorityCitations"]) != AUTHORITY_CITATIONS:
        raise MeasurementError("authority-citations")


def build_schema_invariant_body() -> dict[str, Any]:
    """Build the unsigned schema-invariant body."""
    document = {
        **common(),
        **decision_for(SELECTED_TRACK),
        "additionalEvidenceRequired": "six-category-one-repetition-diagnostic",
        "authorityCitations": list(AUTHORITY_CITATIONS),
        "evaluatedCaseInclusion": "unresolved-does-not-support-rejection",
        "executionContinuationCriterion": "measured-continue",
        "fullResultSetRequiredForPercentage": True,
        "invariantGateNames": list(INVARIANT_GATES),
        "majorityThreshold": "deferred-to-future-diagnostic-specification",
        "mandatoryCriteriaIncludeSchemaConformance": False,
        "mandatoryFailureSupported": False,
        "observedRepetitions": 1,
        "oneInvalidRunIsInvariantFailure": False,
        "oneInvalidRunRejectsCandidate": False,
        "oneRepetitionEstablishesConsistency": False,
        "oneRunCanFailPercentageGate": False,
        "percentageGateKind": "proposed-percentage",
        "percentageGateName": "outputSchemaValidity",
        "percentageRule": "exactly-100",
        "percentageStatusOnThisRun": "unmeasured",
        "perRunValidityRequirement": True,
        "rejectionCurrentlySupported": False,
        "repetitionsRequiredForConsistency": 3,
        "responseSchemaIsCandidateSelectionCriterion": False,
        "responseSchemaIsInvariantGate": False,
        "schemaValidCountsAsMutationOnCandidatePath": False,
    }
    require_schema_invariant(document)
    return document


def build_schema_invariant_review() -> dict[str, Any]:
    """Seal the committed schema-invariant review."""
    return seal(build_schema_invariant_body(), SCHEMA_NAME)


def load_schema_invariant_review() -> dict[str, Any]:
    """Return the committed schema-invariant review."""
    return load_record(_RECORD, build_schema_invariant_review)
