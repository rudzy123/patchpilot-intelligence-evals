"""Track 9 recommendation. It does not select a candidate or approve production."""

from __future__ import annotations

import json
from typing import Any

from patchpilot_intelligence_evals.measurement_plan import (
    MeasurementError,
    authority,
    digest_document,
    load_measurement_plan,
)

_RECORD = "candidates/authorization/track9-readiness.json"
_READY = "TRACK 9 EVALUATION REVIEW READY"
_RESIDUALS = "TRACK 9 EVALUATION REVIEW READY WITH DOCUMENTED RESIDUALS"
_NOT_READY = "TRACK 9 EVALUATION REVIEW NOT READY"
_BLOCKED = "BLOCKED BY UNRESOLVED AUTHORITY"
_AUTHORITY = frozenset(
    {
        "approval-required",
        "digest-mismatch",
        "gold-visible",
        "isolation-failure",
        "missing-root",
        "unverified-dependency",
    }
)


def build_track9_template() -> dict[str, Any]:
    """Committed recommendation before any measurement phase runs."""
    return digest_document(
        {
            **authority(),
            "measurementPerformed": False,
            "readinessOutcome": "not-ready",
            "realModelExecuted": False,
            "reason": "measurement-not-performed",
            "verdict": _NOT_READY,
        },
        "track9-readiness",
        "identityDigest",
    )


def load_track9_readiness() -> dict[str, Any]:
    """Load the committed recommendation and require it to match the builder."""
    from patchpilot_intelligence_evals.schemas import repo_root

    loaded = json.loads((repo_root() / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != build_track9_template():
        raise MeasurementError("record-drift")
    return loaded


def recommend(closeout: dict[str, Any], summary: dict[str, Any] | None) -> dict[str, Any]:
    """Choose one Track 9 verdict from a closeout and an optional summary."""
    plan = load_measurement_plan()
    if (
        closeout.get("planDigest") != plan["planDigest"]
        or closeout.get("productionReady") is not False
    ):
        outcome, verdict, reason = "blocked", _BLOCKED, "unresolved-authority"
    else:
        outcome, verdict, reason = _from_phases(closeout, summary)
    return digest_document(
        {
            **authority(),
            "measurementPerformed": closeout.get("closeoutState") != "not-closed",
            "readinessOutcome": outcome,
            "realModelExecuted": bool(closeout.get("realModelExecuted")),
            "reason": reason,
            "verdict": verdict,
        },
        "track9-readiness",
        "identityDigest",
    )


def _from_phases(
    closeout: dict[str, Any],
    summary: dict[str, Any] | None,
) -> tuple[str, str, str]:
    stop = closeout.get("stopCause")
    if isinstance(stop, str) and stop in _AUTHORITY:
        return "blocked", _BLOCKED, stop
    phases = closeout.get("phases")
    if not isinstance(phases, list) or any(item.get("status") != "passed" for item in phases):
        reason = stop if isinstance(stop, str) else "phase-stopped"
        return "not-ready", _NOT_READY, reason[:80]
    if summary is None or summary.get("gatesUnchanged") is not True:
        return "not-ready", _NOT_READY, "summary-missing"
    if (
        summary.get("comparisonWinner") is not None
        or summary.get("calibrationStatus") != "not-approved"
    ):
        return "blocked", _BLOCKED, "unresolved-authority"
    gates = summary.get("gates")
    if not isinstance(gates, list) or not gates:
        return "not-ready", _NOT_READY, "summary-missing"
    if any(item.get("kind") == "invariant" and item.get("status") == "fail" for item in gates):
        return "not-ready", _NOT_READY, "invariant-gate"
    if any(item.get("status") != "pass" for item in gates):
        return "ready-with-documented-residuals", _RESIDUALS, "percentage-or-consistency"
    if summary.get("ungatedCanonicalAgreement") == "disagree":
        return "ready-with-documented-residuals", _RESIDUALS, "consistency-residual"
    return "ready", _READY, "gates-passed"
