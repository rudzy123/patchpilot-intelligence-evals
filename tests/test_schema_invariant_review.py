"""Schema-invariant authority tests."""

import pytest

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.metrics import COUNT_METRICS
from patchpilot_intelligence_evals.schema_invariant_review import (
    SCHEMA_NAME,
    build_schema_invariant_body,
    build_schema_invariant_review,
    load_schema_invariant_review,
    require_schema_invariant,
)
from patchpilot_intelligence_evals.schemas import validate


def test_one_schema_failure_does_not_reject_the_candidate() -> None:
    document = load_schema_invariant_review()
    assert document == build_schema_invariant_review()
    assert document["perRunValidityRequirement"] is True
    assert document["responseSchemaIsInvariantGate"] is False
    assert document["oneInvalidRunIsInvariantFailure"] is False
    assert document["oneInvalidRunRejectsCandidate"] is False
    assert document["rejectionCurrentlySupported"] is False
    assert document["mandatoryFailureSupported"] is False
    assert document["mandatoryCriteriaIncludeSchemaConformance"] is False
    assert set(document["invariantGateNames"]) == set(COUNT_METRICS)
    assert "outputSchemaValidity" not in document["invariantGateNames"]
    assert document["percentageGateKind"] == "proposed-percentage"
    assert document["percentageGateName"] == "outputSchemaValidity"
    assert document["percentageRule"] == "exactly-100"
    assert document["percentageStatusOnThisRun"] == "unmeasured"
    assert document["oneRunCanFailPercentageGate"] is False
    assert document["fullResultSetRequiredForPercentage"] is True
    assert document["repetitionsRequiredForConsistency"] == 3
    assert document["observedRepetitions"] == 1
    assert document["oneRepetitionEstablishesConsistency"] is False
    assert document["executionContinuationCriterion"] == "measured-continue"
    assert document["responseSchemaIsCandidateSelectionCriterion"] is False
    assert document["schemaValidCountsAsMutationOnCandidatePath"] is False
    assert document["majorityThreshold"] == "deferred-to-future-diagnostic-specification"
    assert document["additionalEvidenceRequired"] == "six-category-one-repetition-diagnostic"
    assert document["evaluatedCaseInclusion"] == "unresolved-does-not-support-rejection"


def test_supported_rejection_flag_is_rejected() -> None:
    document = build_schema_invariant_body()
    document["rejectionCurrentlySupported"] = True
    with pytest.raises(MeasurementError) as caught:
        require_schema_invariant(document)
    assert caught.value.code == "unsupported-rejection"


def test_single_run_invariant_claim_is_rejected() -> None:
    document = build_schema_invariant_body()
    document["oneInvalidRunIsInvariantFailure"] = True
    with pytest.raises(MeasurementError) as caught:
        require_schema_invariant(document)
    assert caught.value.code == "unsupported-rejection"


def test_percentage_failure_on_one_run_is_rejected() -> None:
    document = build_schema_invariant_body()
    document["percentageStatusOnThisRun"] = "fail"
    with pytest.raises(MeasurementError) as caught:
        require_schema_invariant(document)
    assert caught.value.code == "percentage-gate"


def test_repetition_consistency_claim_is_rejected() -> None:
    document = build_schema_invariant_body()
    document["oneRepetitionEstablishesConsistency"] = True
    with pytest.raises(MeasurementError) as caught:
        require_schema_invariant(document)
    assert caught.value.code == "repetition-authority"


def test_schema_accepts_other_dispositions_and_authority_rejects_them() -> None:
    document = build_schema_invariant_body()
    document["track10Disposition"] = "candidate-rejected"
    document["candidateDisposition"] = "candidate-rejected"
    document["selectedAlternative"] = "reject-now"
    document["identityDigest"] = "0" * 64
    validate(SCHEMA_NAME, document)
    with pytest.raises(MeasurementError) as caught:
        require_schema_invariant(document)
    assert caught.value.code == "contradictory-authority"
