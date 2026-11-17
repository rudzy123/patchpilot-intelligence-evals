"""Track 10 readiness stays advisory and does not select a candidate."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.corpus_continuation_plan import load_corpus_plan
from patchpilot_intelligence_evals.evaluator import GATE_NAMES
from patchpilot_intelligence_evals.metrics import COUNT_METRICS
from patchpilot_intelligence_evals.track10_readiness import load_track10_template, recommend

_READY = "TRACK 10 CANDIDATE DISPOSITION REVIEW READY"
_RESIDUALS = "TRACK 10 CANDIDATE DISPOSITION REVIEW READY WITH DOCUMENTED RESIDUALS"
_NOT_READY = "TRACK 10 CANDIDATE DISPOSITION REVIEW NOT READY"
_BLOCKED = "BLOCKED BY UNRESOLVED AUTHORITY"


def test_committed_readiness_is_not_executed() -> None:
    document = load_track10_template()
    assert document["readinessOutcome"] == "not-ready"
    assert document["verdict"] == _NOT_READY
    assert document["reason"] == "not-executed"
    assert document["measurementPerformed"] is False
    assert document["realModelExecuted"] is False
    assert document["comparisonWinner"] is None
    assert document["productionReady"] is False


def test_ready_residual_not_ready_and_blocked_outcomes() -> None:
    ready = recommend(_closeout("closed", None), _summary("pass", "consistent"))
    residual = recommend(_closeout("closed", None), _summary("unmeasured", "consistent"))
    inconsistent = recommend(_closeout("closed", None), _summary("pass", "inconsistent"))
    failed = recommend(_closeout("closed", None), _summary("fail", "consistent"))
    stopped = recommend(_closeout("stopped", "excessive-output"), _summary("pass", "consistent"))
    blocked = recommend(_closeout("stopped", "gold-visible"), _summary("pass", "consistent"))
    drifted = _closeout("closed", None)
    drifted["productionReady"] = True
    authority = recommend(drifted, _summary("pass", "consistent"))
    assert ready["verdict"] == _READY
    assert residual["verdict"] == _RESIDUALS
    assert inconsistent["verdict"] == _RESIDUALS
    assert failed["verdict"] == _NOT_READY
    assert failed["reason"] == "invariant-gate"
    assert stopped["verdict"] == _NOT_READY
    assert blocked["verdict"] == _BLOCKED
    assert authority["verdict"] == _BLOCKED
    for document in (ready, residual, inconsistent, failed, stopped, blocked, authority):
        assert document["comparisonWinner"] is None
        assert document["productionReady"] is False
        assert document["selectionOutcome"] == "no-selection"
        assert document["calibrationStatus"] == "not-approved"


def _closeout(state: str, stop: str | None) -> dict[str, Any]:
    plan = load_corpus_plan()
    return {
        "calibrationStatus": "not-approved",
        "cleanup": "reaped",
        "closeoutState": state,
        "comparisonWinner": None,
        "completedRuns": 72,
        "installationAuthorized": False,
        "measurementPerformed": True,
        "planDigest": plan["planDigest"],
        "productionReady": False,
        "realModelExecuted": False,
        "retention": "retained",
        "selectionOutcome": "no-selection",
        "stopCause": stop,
    }


def _summary(status: str, consistency: str) -> dict[str, Any]:
    plan = load_corpus_plan()
    gates = []
    for name in GATE_NAMES:
        kind = "invariant" if name in COUNT_METRICS else "proposed-percentage"
        gate_status = "fail" if status == "fail" and kind == "invariant" else status
        if status == "fail" and kind != "invariant":
            gate_status = "pass"
        gates.append(
            {
                "denominator": 1,
                "gate": name,
                "kind": kind,
                "numerator": 0 if gate_status == "fail" else 1,
                "status": gate_status,
            }
        )
    return {
        "calibrationStatus": "not-approved",
        "comparisonWinner": None,
        "failureAuthorityCounts": {"unresolved": 0},
        "gates": gates,
        "gatesUnchanged": True,
        "installationAuthorized": False,
        "percentageGatesCalibrated": False,
        "planDigest": plan["planDigest"],
        "productionReady": False,
        "repetitionConsistency": consistency,
        "selectionOutcome": "no-selection",
    }
