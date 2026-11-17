"""Track 9 behavioral-review tests."""

import pytest

from patchpilot_intelligence_evals.behavioral_evidence_review import (
    assign_failure_authority,
    build_behavioral_evidence_review,
    impute_cases,
    load_behavioral_evidence_review,
    score_corpus,
)
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schemas import SchemaValidationError, validate
from patchpilot_intelligence_evals.track8b_r2_records import (
    load_behavioral_interpretation,
    load_cgroup_defect,
    load_schema_forensics,
)


def test_behavior_stays_partial_and_unscored() -> None:
    review = load_behavioral_evidence_review()
    behavior = load_behavioral_interpretation()
    forensics = load_schema_forensics()
    defect = load_cgroup_defect()
    assert review == build_behavioral_evidence_review()
    assert review["behavioralMeasurementAttempted"] is True
    assert (
        review["behavioralMeasurementCompleted"]
        is behavior["behavioralMeasurementCompleted"]
        is False
    )
    assert review["candidateMetricsProduced"] is False
    assert review["behavioralConclusion"] == "partial-inconclusive"
    assert review["schemaFailuresObserved"] == forensics["completedRunCount"] == 15
    assert review["schemaFailureAuthority"] == "unresolved"
    assert forensics["authorityCounts"]["unresolved"] == 15
    assert forensics["candidateCharacterizedAsSchemaNoncompliant"] is False
    assert review["candidateCharacterizedAsSchemaNoncompliant"] is False
    assert review["casesWithoutResults"] == 19
    assert review["completeCaseGroups"] == 5
    assert review["unsealedLaunches"] == 1
    assert defect["omittedLaunch"] is True
    assert defect["omittedLaunchSealed"] is False
    assert defect["stdoutRetained"] is False
    assert review["completeCaseGroups"] + review["casesWithoutResults"] == 24
    sealed = {row["caseId"] for row in forensics["runs"]}
    assert tuple(review["sealedCaseIds"]) == tuple(
        sorted(sealed, key=review["sealedCaseIds"].index)
    )
    assert review["candidateQualityConclusion"] == "unavailable"
    assert review["schemaComplianceConclusion"] == "unavailable"
    assert review["empiricalCapabilityConclusions"] == "unavailable"
    assert review["missingCasesTreatedAsPasses"] is False
    assert review["missingCasesTreatedAsFailures"] is False
    assert review["rawOutputRetained"] is False
    assert review["comparisonWinner"] is None
    assert review["comparisonStatus"] == "not-executed"
    assert review["productionReady"] is False


def test_incomplete_evidence_is_not_scored_or_imputed() -> None:
    document = load_behavioral_evidence_review()
    with pytest.raises(MeasurementError) as scored:
        score_corpus(document)
    assert scored.value.code == "incomplete-evidence"
    for outcome in ("pass", "fail"):
        with pytest.raises(MeasurementError) as imputed:
            impute_cases(document, outcome)
        assert imputed.value.code == "imputation-prohibited"


def test_failure_authority_stays_unresolved() -> None:
    assign_failure_authority("unresolved")
    for authority in ("candidate-output", "adapter", "evaluator", "protocol"):
        with pytest.raises(MeasurementError) as caught:
            assign_failure_authority(authority)
        assert caught.value.code == "unresolved-authority"
    document = build_behavioral_evidence_review()
    document["schemaFailureAuthority"] = "candidate-output"
    with pytest.raises(SchemaValidationError):
        validate("behavioral-evidence-review", document)
    document = build_behavioral_evidence_review()
    document["candidateCharacterizedAsSchemaNoncompliant"] = True
    with pytest.raises(SchemaValidationError):
        validate("behavioral-evidence-review", document)
