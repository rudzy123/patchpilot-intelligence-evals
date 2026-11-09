"""Replay ignores the result timestamp, latency, and process memory."""

from __future__ import annotations

import logging
from typing import Any

from patchpilot_intelligence_evals.corpus import canonical_dumps, load_cases
from patchpilot_intelligence_evals.evaluator import evaluate_baseline


def _stable(result: dict[str, Any]) -> dict[str, Any]:
    clone = dict(result)
    clone["executedAt"] = "stripped"
    global_metrics = dict(clone["global"])
    global_metrics["latency"] = {"status": "stripped"}
    global_metrics["peakProcessMemory"] = {"status": "stripped"}
    clone["global"] = global_metrics
    by_category = {}
    for name, block in clone["byCategory"].items():
        metrics = dict(block)
        metrics["latency"] = {"status": "stripped"}
        by_category[name] = metrics
    clone["byCategory"] = by_category
    per_case = []
    for item in clone["perCase"]:
        metrics = dict(item["metrics"])
        metrics["latency"] = {"status": "stripped"}
        per_case.append({**item, "metrics": metrics})
    clone["perCase"] = per_case
    return clone


def test_logs_keep_identifiers_and_omit_request_text(caplog: Any) -> None:
    caplog.set_level(logging.INFO, logger="patchpilot_intelligence_evals")
    evaluate_baseline()
    request = next(
        case["assistanceRequest"] for case in load_cases() if case["caseId"] == "case-ground-001"
    )
    assert "case_id=case-ground-001" in caplog.text
    assert request not in caplog.text
    assert "INJECT-NORTH-0002" not in caplog.text


def test_baseline_evaluation_replays_without_the_clock() -> None:
    first = evaluate_baseline()
    second = evaluate_baseline()
    assert first["productionReady"] is False
    assert first["purpose"] == "harness-validation"
    assert first["resultDistinctions"]["candidatePerformance"] == "not-measured"
    assert canonical_dumps(_stable(first)) == canonical_dumps(_stable(second))
    assert all(gate["status"] == "pass" for gate in first["gates"].values())
