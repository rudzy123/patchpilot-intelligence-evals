"""Deterministic six-case selection. The selector does not execute a model."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.corpus import load_cases
from patchpilot_intelligence_evals.evaluator import CATEGORIES
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.six_run_diagnostic_authorization import representative_cases

SELECTION_RULE = "minimum-case-id-within-committed-category"
PLANNED_RUNS = 6


def select_diagnostic_cases() -> list[dict[str, Any]]:
    """Return one repetition of the minimum case id in each committed category."""
    chosen = representative_cases()
    if set(chosen) != set(CATEGORIES) or len(chosen) != len(CATEGORIES):
        raise MeasurementError("category-coverage")
    loaded = {str(case["caseId"]): str(case["category"]) for case in load_cases()}
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for category in CATEGORIES:
        case_id = chosen[category]
        if case_id in seen or loaded.get(case_id) != category:
            raise MeasurementError("category-coverage")
        seen.add(case_id)
        rows.append(
            {
                "caseId": case_id,
                "category": category,
                "repetition": 1,
                "runId": f"{case_id}-r1",
            }
        )
    if len(rows) != PLANNED_RUNS or len(seen) != PLANNED_RUNS:
        raise MeasurementError("category-coverage")
    return rows
