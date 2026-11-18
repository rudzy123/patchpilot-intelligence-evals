"""Deterministic minimum-case selection across the six committed categories."""

from __future__ import annotations

import pytest

from patchpilot_intelligence_evals.diagnostic_case_selection import (
    PLANNED_RUNS,
    SELECTION_RULE,
    select_diagnostic_cases,
)
from patchpilot_intelligence_evals.evaluator import CATEGORIES
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.six_run_diagnostic_authorization import representative_cases


def test_selection_is_the_minimum_case_in_each_category() -> None:
    chosen = representative_cases()
    rows = select_diagnostic_cases()
    assert [row["category"] for row in rows] == list(CATEGORIES)
    assert [row["caseId"] for row in rows] == [chosen[category] for category in CATEGORIES]
    assert [row["runId"] for row in rows] == [f"{row['caseId']}-r1" for row in rows]
    assert {row["repetition"] for row in rows} == {1}
    assert len({row["caseId"] for row in rows}) == PLANNED_RUNS
    assert SELECTION_RULE == "minimum-case-id-within-committed-category"
    assert rows[0]["caseId"] == "case-ground-001"
    assert rows[1]["caseId"] == "case-refuse-001"
    assert rows[2]["caseId"] == "case-inject-001"
    assert rows[3]["caseId"] == "case-tenant-001"
    assert rows[4]["caseId"] == "case-contra-001"
    assert rows[5]["caseId"] == "case-stale-001"


def test_selection_rejects_a_duplicate_case(monkeypatch: pytest.MonkeyPatch) -> None:
    def _duplicate() -> dict[str, str]:
        chosen = representative_cases()
        first = next(iter(CATEGORIES))
        second = list(CATEGORIES)[1]
        chosen[second] = chosen[first]
        return chosen

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.diagnostic_case_selection.representative_cases",
        _duplicate,
    )
    with pytest.raises(MeasurementError) as caught:
        select_diagnostic_cases()
    assert caught.value.code == "category-coverage"


def test_selection_rejects_a_missing_category(monkeypatch: pytest.MonkeyPatch) -> None:
    def _short() -> dict[str, str]:
        chosen = representative_cases()
        del chosen[CATEGORIES[-1]]
        return chosen

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.diagnostic_case_selection.representative_cases",
        _short,
    )
    with pytest.raises(MeasurementError) as caught:
        select_diagnostic_cases()
    assert caught.value.code == "category-coverage"
