"""Track 10 implementation-review tests. The review does not call Run."""

import pytest

from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schemas import SchemaValidationError, validate
from patchpilot_intelligence_evals.track10_implementation_review import (
    SCHEMA_NAME,
    build_track10_implementation_review,
    load_track10_implementation_review,
    require_track10_review,
)

_STDOUT = "b28e9aa7f5db74d23040d9b3045b5fc927bc2289378bb6bf676e4568ec20b0b9"
_EXTRACTED = "8d5acd633059fd19ea765c0ce415bb37d4f53cc02ed848fcf6df490d55ab9d5d"


def test_committed_review_matches_the_sealed_builder() -> None:
    document = load_track10_implementation_review()
    assert document == build_track10_implementation_review()
    assert document["reviewDigest"] == review_digest(document)
    assert document["reviewDate"] == "2026-11-18"
    assert document["reviewAuthority"] == "PatchPilot Principal Systems Architect"
    assert document["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert document["sixRunDiagnostic"] == "authorized-in-principle"
    assert document["attributedResponseEvidence"] == "approved"
    assert document["schemaAuthorityReview"] == "approved"
    assert document["proportionalityAnalysis"] == "approved"
    assert document["currentExecutionAuthority"] is False
    assert document["futurePlanDigest"] == "not-issued"
    assert document["replacementPlanDigest"] == "not-issued"
    assert document["operatorApproval"] == "not-issued"
    assert document["resultRootState"] == "not-created"
    assert document["installationAuthorized"] is False
    assert document["selectionOutcome"] == "no-selection"
    assert document["calibrationStatus"] == "not-approved"
    assert document["comparisonWinner"] is None
    assert document["productionReady"] is False


def test_response_identities_stay_separated_from_the_stop() -> None:
    document = load_track10_implementation_review()
    evidence = document["responseEvidence"]
    assert evidence["runId"] == "case-ground-001-r1"
    assert (evidence["stdoutBytes"], evidence["stdoutDigest"]) == (542, _STDOUT)
    assert (evidence["extractedBytes"], evidence["extractedDigest"]) == (264, _EXTRACTED)
    assert evidence["jsonParse"] == "passed"
    assert evidence["responseSchemaValidation"] == "failed"
    assert evidence["truncation"] is False
    assert evidence["outputLimitExceeded"] is False
    assert evidence["adapterInnerFieldMutation"] is False
    assert evidence["unexpectedFields"] == ["deterministicFacts", "findingExplanation"]
    assert "schemaVersion" in evidence["missingRequiredFields"]
    assert "nonAuthoritative" in evidence["missingRequiredFields"]
    assert document["responseFailureAuthority"] == "candidate-output"
    assert document["executionStopAuthority"] == "measurement-infrastructure"
    assert document["executionStopCause"] == "telemetry-unresolved"
    assert document["authoritiesConflated"] is False


def test_one_response_does_not_support_rejection() -> None:
    document = load_track10_implementation_review()
    analysis = document["authorityAnalysis"]
    assert analysis["perRunResponseContract"] == "failed"
    assert analysis["invariantGateTriggered"] is False
    assert analysis["percentageGateName"] == "outputSchemaValidity"
    assert analysis["percentageGateKind"] == "proposed-percentage"
    assert analysis["percentageRule"] == "exactly-100"
    assert analysis["percentageStatus"] == "unmeasured"
    assert analysis["completeScoredResultRequired"] is True
    assert analysis["calibrationRequired"] is True
    assert analysis["repetitionsRequiredForConsistency"] == 3
    assert analysis["observedRepetitions"] == 1
    assert analysis["oneResponseSupportsCandidateRejection"] is False
    assert document["mandatoryFailureSupported"] is False
    assert document["candidateRejectionSupported"] is False


def test_exactly_one_alternative_is_selected() -> None:
    document = load_track10_implementation_review()
    selected = [row for row in document["alternativeDecisions"] if row["selected"]]
    assert [row["alternativeId"] for row in selected] == ["six-run-diagnostic"]
    assert document["selectedAlternative"] == "six-run-diagnostic"
    assert document["proportionalityJudgment"] == "six-run-proportionate"
    assert document["qualityVerdict"] is False
    assert document["sixRunPrecedesFullRerun"] is True
    assert document["investmentStopSelected"] is False
    decisions = {row["alternativeId"]: row["decision"] for row in document["alternativeDecisions"]}
    assert decisions == {
        "reject-now": "ineligible",
        "six-run-diagnostic": "selected",
        "full-72-run-continuation": "eligible",
        "protocol-forensics": "ineligible",
        "stop-investment": "permissible",
    }


def test_six_run_boundary_issues_no_plan_or_case_list() -> None:
    document = load_track10_implementation_review()
    boundary = document["diagnosticBoundary"]
    assert boundary["categoryCount"] == 6
    assert boundary["casesPerCategory"] == 1
    assert boundary["repetitionsPerCase"] == 1
    assert boundary["plannedDiagnosticRuns"] == 6
    assert boundary["representativeCaseRule"] == "minimum-case-id-within-committed-category"
    assert boundary["operationalCaseIds"] == "not-selected"
    assert boundary["runtimeAndCandidateUnchanged"] is True
    assert boundary["publisherTemplateUnchanged"] is True
    assert boundary["promptsUnchanged"] is True
    assert boundary["responseSchemaUnchanged"] is True
    assert boundary["decodingAndLimitsUnchanged"] is True
    assert boundary["hardenedBoundaryUnchanged"] is True
    assert boundary["reuseAcceptedMemoryEvidence"] is True
    assert boundary["contextMemoryRerun"] is False
    assert boundary["rawOutputRetention"] == "bounded-immutable"
    assert boundary["requiredDiagnostics"] == [
        "extraction",
        "parse",
        "schema",
        "truncation",
        "output-limit",
        "evidence-id",
        "failure-authority",
    ]
    assert boundary["futureSpecificationRequired"] is True
    assert boundary["newPlanDigestRequired"] is True
    assert boundary["freshEmptyResultRootRequired"] is True
    assert boundary["newOperatorApprovalRequired"] is True
    assert boundary["systematicThreshold"] == "deferred-to-future-diagnostic-specification"
    assert boundary["operationalThresholdIssued"] is False
    assert boundary["executionPlanIssued"] is False
    assert [row["reusable"] for row in document["consumedPlans"]] == [False, False, False, False]


def test_review_does_not_authorize_execution_or_selection() -> None:
    document = load_track10_implementation_review()
    assert document["notAuthorized"] == [
        "current-candidate-execution",
        "diagnostic-plan",
        "execution-plan-digest",
        "result-root",
        "operator-approval",
        "candidate-selection",
        "calibration-approval",
        "patchpilot-integration",
        "shadow-mode",
        "production-use",
        "release-or-deployment",
    ]


def test_second_selected_alternative_is_rejected() -> None:
    document = build_track10_implementation_review()
    document["alternativeDecisions"] = [dict(row) for row in document["alternativeDecisions"]]
    document["alternativeDecisions"][0]["selected"] = True
    with pytest.raises(MeasurementError) as caught:
        require_track10_review(document)
    assert caught.value.code == "proportionality-selection"


def test_hand_edited_digest_is_rejected() -> None:
    document = build_track10_implementation_review()
    document["reviewDigest"] = "0" * 64
    with pytest.raises(MeasurementError) as caught:
        require_track10_review(document)
    assert caught.value.code == "review-digest"


def test_schema_rejects_production_ready() -> None:
    document = build_track10_implementation_review()
    document["productionReady"] = True
    with pytest.raises(SchemaValidationError):
        validate(SCHEMA_NAME, document)
