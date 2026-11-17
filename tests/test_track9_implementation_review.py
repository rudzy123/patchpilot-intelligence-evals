"""Track 9 implementation-review tests. The review does not call Run."""

import pytest

from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schemas import SchemaValidationError, validate
from patchpilot_intelligence_evals.track9_implementation_review import (
    build_track9_implementation_review,
    load_track9_implementation_review,
    require_track9_review,
)
from patchpilot_intelligence_evals.track9_review import (
    CEILING_BYTES,
    HEADROOM_BYTES,
    WARM_8192_PEAK_BYTES,
)


def test_committed_review_matches_the_sealed_builder() -> None:
    document = load_track9_implementation_review()
    assert document == build_track9_implementation_review()
    assert document["reviewDigest"] == review_digest(document)
    assert document["reviewDate"] == "2026-11-17"
    assert document["reviewAuthority"] == "PatchPilot Principal Systems Architect"
    assert document["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert document["corpusOnlyContinuation"] == "authorized-in-principle"
    assert document["currentExecutionAuthority"] is False
    assert document["futurePlanDigest"] == "not-issued"
    assert document["operatorApproval"] == "not-issued"
    assert document["resultRootState"] == "not-created"
    assert document["selectionOutcome"] == "no-selection"
    assert document["calibrationStatus"] == "not-approved"
    assert document["comparisonWinner"] is None
    assert document["productionReady"] is False


def test_memory_arithmetic_and_limited_headroom_are_exact() -> None:
    memory = load_track9_implementation_review()["memoryEvidence"]
    assert memory["ceilingBytes"] == CEILING_BYTES
    assert memory["warm8192PeakBytes"] == WARM_8192_PEAK_BYTES
    assert memory["minimumHeadroomBytes"] == HEADROOM_BYTES
    assert memory["ceilingBytes"] - memory["warm8192PeakBytes"] == HEADROOM_BYTES
    assert memory["memoryGate"] == "passed"
    assert memory["headroomAssessment"] == "limited"
    assert memory["concurrency"] == "prohibited"
    assert memory["largerContext"] == "not-authorized"
    assert memory["productionCapacity"] == "not-established"


def test_behavioral_evidence_stays_unscored_and_unresolved() -> None:
    behavior = load_track9_implementation_review()["behavioralEvidence"]
    assert behavior["behavioralMeasurementAttempted"] is True
    assert behavior["behavioralMeasurementCompleted"] is False
    assert behavior["behavioralConclusion"] == "partial-inconclusive"
    assert behavior["candidateMetricsProduced"] is False
    assert behavior["candidateEvaluatedCompletely"] is False
    assert behavior["sealedRunRecords"] == 15
    assert behavior["completeCaseGroups"] == 5
    assert behavior["missingCompleteCases"] == 19
    assert behavior["unsealedLaunchCount"] == 1
    assert behavior["schemaFailureAuthority"] == "unresolved"
    assert behavior["schemaComplianceConclusion"] == "unavailable"
    assert behavior["empiricalCapabilityConclusions"] == "unavailable"


def test_exactly_one_alternative_is_selected() -> None:
    document = load_track9_implementation_review()
    selected = [row for row in document["alternativeDecisions"] if row["selected"]]
    assert [row["alternativeId"] for row in selected] == ["clean-24-case-corpus-only-rerun"]
    assert document["selectedAlternative"] == "clean-24-case-corpus-only-rerun"
    assert document["proportionalityJudgment"] == "proportionate"
    decisions = {row["alternativeId"]: row["decision"] for row in document["alternativeDecisions"]}
    assert decisions == {
        "reject-now": "withheld",
        "remaining-19": "rejected",
        "clean-24-case-corpus-only-rerun": "selected",
        "narrow-forensics": "rejected",
        "stop-investment": "permissible",
    }


def test_continuation_boundary_requires_a_future_plan() -> None:
    boundary = load_track9_implementation_review()["continuationBoundary"]
    assert (boundary["caseCount"], boundary["repetitionsPerCase"], boundary["plannedRuns"]) == (
        24,
        3,
        72,
    )
    assert boundary["reuseAcceptedMemoryEvidence"] is True
    assert boundary["repeatContext4096"] is False
    assert boundary["repeatContext8192"] is False
    assert boundary["rawOutputRetention"] == "required"
    assert boundary["futureSpecification"] == "required"
    assert boundary["futurePlanDigest"] == "not-issued"
    assert boundary["futurePlanRequired"] is True
    assert boundary["futureResultRoot"] == "not-created"
    assert boundary["futureOperatorApproval"] == "not-issued"
    assert boundary["goldAndEvaluatorHidden"] is True


def test_review_does_not_authorize_execution_or_selection() -> None:
    document = load_track9_implementation_review()
    assert document["notAuthorized"] == [
        "current-execution",
        "measurement-or-execution-plan",
        "plan-digest",
        "result-root",
        "candidate-selection",
        "calibration-approval",
        "patchpilot-integration",
        "shadow-mode",
        "production-use",
        "release-or-deployment",
    ]
    assert [row["reusable"] for row in document["consumedPlans"]] == [False, False, False]


def test_wrong_headroom_is_rejected() -> None:
    document = build_track9_implementation_review()
    document["memoryEvidence"] = dict(document["memoryEvidence"])
    document["memoryEvidence"]["minimumHeadroomBytes"] = 1
    with pytest.raises(MeasurementError) as caught:
        require_track9_review(document)
    assert caught.value.code == "memory-scope"


def test_second_selected_alternative_is_rejected() -> None:
    document = build_track9_implementation_review()
    document["alternativeDecisions"] = [dict(row) for row in document["alternativeDecisions"]]
    document["alternativeDecisions"][0]["selected"] = True
    with pytest.raises(MeasurementError) as caught:
        require_track9_review(document)
    assert caught.value.code == "proportionality-selection"


def test_schema_rejects_production_ready() -> None:
    document = build_track9_implementation_review()
    document["productionReady"] = True
    with pytest.raises(SchemaValidationError):
        validate("track9-implementation-review", document)
