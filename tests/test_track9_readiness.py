"""Track 9 stays a recommendation with ready and not-ready outcomes."""

from __future__ import annotations

from patchpilot_intelligence_evals.measurement_closeout import build_closeout_template
from patchpilot_intelligence_evals.measurement_plan import PHASE_ORDER
from patchpilot_intelligence_evals.track9_readiness import load_track9_readiness, recommend


def _closeout(status: str, stop: str | None) -> dict[str, object]:
    template = build_closeout_template()
    return {
        "closeoutState": "closed" if status == "passed" else "stopped",
        "phases": [{"phase": phase, "status": status} for phase in PHASE_ORDER],
        "planDigest": template["planDigest"],
        "productionReady": False,
        "realModelExecuted": status == "passed",
        "stopCause": stop,
    }


def _summary(gate_status: str, kind: str = "proposed-percentage") -> dict[str, object]:
    return {
        "calibrationStatus": "not-approved",
        "comparisonWinner": None,
        "gates": [
            {
                "denominator": 1,
                "kind": kind,
                "name": "outputSchemaValidity",
                "numerator": 1 if gate_status == "pass" else 0,
                "status": gate_status,
            }
        ],
        "gatesUnchanged": True,
        "ungatedCanonicalAgreement": "agree",
    }


def test_committed_record_is_not_ready() -> None:
    document = load_track9_readiness()
    assert document["verdict"] == "TRACK 9 EVALUATION REVIEW NOT READY"
    assert document["reason"] == "measurement-not-performed"
    assert document["measurementPerformed"] is False
    assert document["selectionOutcome"] == "no-selection"
    assert document["productionReady"] is False


def test_ready_and_not_ready_recommendations() -> None:
    ready = recommend(_closeout("passed", None), _summary("pass"))
    assert ready["verdict"] == "TRACK 9 EVALUATION REVIEW READY"
    assert ready["selectionOutcome"] == "no-selection"
    residual = recommend(_closeout("passed", None), _summary("fail"))
    assert residual["readinessOutcome"] == "ready-with-documented-residuals"
    invariant = recommend(_closeout("passed", None), _summary("fail", "invariant"))
    assert invariant["verdict"] == "TRACK 9 EVALUATION REVIEW NOT READY"
    stopped = recommend(_closeout("failed", "oom"), None)
    assert stopped["verdict"] == "TRACK 9 EVALUATION REVIEW NOT READY"
    blocked = recommend(_closeout("failed", "digest-mismatch"), None)
    assert blocked["verdict"] == "BLOCKED BY UNRESOLVED AUTHORITY"
