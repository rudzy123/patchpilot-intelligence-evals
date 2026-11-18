"""Six-run diagnostic boundary tests."""

import pytest

from patchpilot_intelligence_evals.corpus import load_cases
from patchpilot_intelligence_evals.evaluator import CATEGORIES
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.six_run_diagnostic_authorization import (
    build_six_run_authorization,
    build_six_run_body,
    build_withheld_six_run,
    load_six_run_authorization,
    representative_cases,
    require_six_run,
)


def test_authorization_is_in_principle_only() -> None:
    document = load_six_run_authorization()
    assert document == build_six_run_authorization()
    assert document["authorizationStatus"] == "authorized-in-principle"
    assert document["authorizesFutureSession"] is True
    assert document["plannedDiagnosticRuns"] == 6
    assert document["repetitionsPerSelectedCase"] == 1
    assert document["plannedCorpusRuns"] == 72
    assert document["operationalCaseIds"] == "not-selected"
    assert document["futurePlanDigest"] == "not-issued"
    assert document["operatorApproval"] == "not-issued"
    assert document["resultRootState"] == "not-created"
    assert document["automaticCandidateSelection"] is False
    assert document["memoryRerun"] is False
    assert document["contextMemoryRerun"] is False
    assert document["rawOutputRetention"] == "bounded-immutable"
    assert document["goldIsolation"] == "mandatory"
    assert document["systematicThreshold"] == "deferred-to-future-diagnostic-specification"
    assert document["representsCompleteCorpus"] is False
    assert document["producesPercentageMetrics"] is False
    assert document["promotionGateAttempt"] is False
    assert document["currentExecutionAuthority"] is False
    assert [row["category"] for row in document["categories"]] == list(CATEGORIES)
    assert {row["caseId"] for row in document["categories"]} == {"not-selected"}
    assert {row["repetitionCount"] for row in document["categories"]} == {1}


def test_representative_rule_covers_each_category_without_entering_the_record() -> None:
    chosen = representative_cases()
    expected: dict[str, str] = {}
    for case in load_cases():
        category = str(case["category"])
        case_id = str(case["caseId"])
        current = expected.get(category)
        if current is None or case_id < current:
            expected[category] = case_id
    assert chosen == {category: expected[category] for category in CATEGORIES}
    assert chosen == {
        "grounding-citation": "case-ground-001",
        "insufficient-evidence-refusal": "case-refuse-001",
        "prompt-injection": "case-inject-001",
        "cross-tenant-negative-control": "case-tenant-001",
        "contradiction": "case-contra-001",
        "stale-unavailable-incomparable": "case-stale-001",
    }
    text = load_six_run_authorization().__repr__()
    for case_id in (
        "case-refuse-001",
        "case-inject-001",
        "case-tenant-001",
        "case-contra-001",
        "case-stale-001",
    ):
        assert case_id not in text


def test_withheld_authorization_is_not_committed() -> None:
    withheld = build_withheld_six_run()
    assert withheld["authorizationStatus"] == "withheld"
    assert withheld["authorizesFutureSession"] is False
    assert withheld["plannedDiagnosticRuns"] == 0
    assert withheld["categories"] == []
    assert withheld["futurePlanDigest"] == "not-issued"
    assert withheld["operationalCaseIds"] == "not-selected"
    assert withheld != load_six_run_authorization()
    with pytest.raises(MeasurementError) as caught:
        build_withheld_six_run("not-applicable")
    assert caught.value.code == "withheld-reason"


def test_operational_case_selection_is_rejected() -> None:
    document = build_six_run_body("authorized-in-principle", "not-applicable")
    document["categories"][0]["caseId"] = "case-ground-001"
    with pytest.raises(MeasurementError) as caught:
        require_six_run(document)
    assert caught.value.code == "operational-case"


def test_issued_plan_is_rejected() -> None:
    document = build_six_run_body("authorized-in-principle", "not-applicable")
    document["futurePlanDigest"] = "a" * 64
    with pytest.raises(MeasurementError) as caught:
        require_six_run(document)
    assert caught.value.code == "plan-issued"
