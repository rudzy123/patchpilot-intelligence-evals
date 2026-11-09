"""Metric arithmetic, including boundaries that do not appear in the corpus run."""

from __future__ import annotations

from copy import deepcopy

from patchpilot_intelligence_evals.baseline import run_baseline
from patchpilot_intelligence_evals.corpus import load_cases
from patchpilot_intelligence_evals.metrics import (
    at_least_95,
    at_most_2,
    exactly_100,
    gate_from_metric,
    invariant_status,
    measure,
    score_case,
)


def test_zero_denominator_is_unmeasured() -> None:
    assert measure(5, 0) == {
        "numerator": 0,
        "denominator": 0,
        "status": "unmeasured",
        "value": None,
    }
    assert at_least_95(0, 0) == "unmeasured"
    assert at_most_2(0, 0) == "unmeasured"
    assert exactly_100(0, 0) == "unmeasured"
    assert invariant_status(0, 0) == "unmeasured"


def test_percentage_boundaries() -> None:
    assert at_least_95(19, 20) == "pass"
    assert at_least_95(18, 19) == "fail"
    assert at_most_2(1, 50) == "pass"
    assert at_most_2(1, 49) == "fail"
    assert exactly_100(24, 24) == "pass"
    assert exactly_100(23, 24) == "fail"


def test_invariant_failure_is_distinct_from_a_percentage() -> None:
    assert invariant_status(0, 4) == "pass"
    assert invariant_status(1, 4) == "fail"
    changed = gate_from_metric(
        "affectednessOrPriorityChange",
        measure(1, 4, as_count=True),
    )
    assert changed["status"] == "fail"
    assert changed["kind"] == "invariant"


def test_changed_priority_and_unsupported_claim_are_counted() -> None:
    case = next(item for item in load_cases() if item["caseId"] == "case-ground-001")
    output = run_baseline(case)
    scored = score_case(
        case,
        output,
        schema_valid=True,
        replay_match=True,
        log_text="case_id=case-ground-001 metric=outputSchemaValidity status=pass",
    )
    assert scored["unsupportedFactualClaims"]["numerator"] == 0
    mutated = deepcopy(output)
    mutated["preservedDeterministicFacts"]["priority"] = "P1"
    mutated["supportedClaims"].append(
        {
            "claimId": "claim-synthetic-extra",
            "text": "The priority is changed to P1.",
            "evidenceIds": ["evidence-synthetic-ground-001"],
        }
    )
    failed = score_case(
        case,
        mutated,
        schema_valid=True,
        replay_match=True,
        log_text="case_id=case-ground-001 metric=outputSchemaValidity status=pass",
    )
    assert failed["affectednessOrPriorityChange"]["numerator"] == 1
    assert failed["unsupportedFactualClaims"]["numerator"] == 1
    assert failed["unauthorizedStateMutation"]["numerator"] == 1
