"""Track 9 recommendation for the inference retry. It does not select a candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.inference_retry_plan import load_inference_plan
from patchpilot_intelligence_evals.measurement_plan import MeasurementError, digest_document
from patchpilot_intelligence_evals.schemas import repo_root

_RECORD = Path("candidates/authorization/inference-retry-track9-readiness.json")
_READY = "TRACK 9 EVALUATION REVIEW READY"
_RESIDUALS = "TRACK 9 EVALUATION REVIEW READY WITH DOCUMENTED RESIDUALS"
_NOT_READY = "TRACK 9 EVALUATION REVIEW NOT READY"
_BLOCKED = "BLOCKED BY UNRESOLVED AUTHORITY"
_AUTHORITY = frozenset(
    {
        "approval-required",
        "compatibility-failure",
        "digest-mismatch",
        "gold-visible",
        "insufficient-capacity",
        "isolation-failure",
        "missing-root",
        "plan-consumed",
        "result-root-reuse",
        "unverified-dependency",
    }
)


def build_track9_template() -> dict[str, Any]:
    """Committed recommendation before any inference-retry phase runs."""
    plan = load_inference_plan()
    return digest_document(
        {
            **_flags(False, False),
            **_links(plan, "not-executed"),
            "planDigest": plan["planDigest"],
            "priorPlanDigest": plan["priorPlanDigest"],
            "readinessOutcome": "not-ready",
            "reason": "measurement-not-performed",
            "sessionId": plan["sessionId"],
            "verdict": _NOT_READY,
        },
        "inference-retry-track9-readiness",
        "identityDigest",
    )


def load_track9_template() -> dict[str, Any]:
    """Load the committed recommendation and require it to match the builder."""
    loaded = json.loads((repo_root() / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_track9_template():
        raise MeasurementError("record-drift")
    return loaded


def recommend(closeout: dict[str, Any], summary: dict[str, Any] | None) -> dict[str, Any]:
    """Choose one Track 9 verdict. The verdict stays advisory."""
    plan = load_inference_plan()
    if (
        closeout.get("planDigest") != plan["planDigest"]
        or closeout.get("productionReady") is not False
        or closeout.get("selectionOutcome") != "no-selection"
        or closeout.get("calibrationStatus") != "not-approved"
        or closeout.get("comparisonWinner") is not None
        or closeout.get("furtherRetryAssumed") is not False
    ):
        outcome, verdict, reason = "blocked", _BLOCKED, "unresolved-authority"
    else:
        outcome, verdict, reason = _from_phases(closeout, summary)
    performed = closeout.get("closeoutState") != "not-closed"
    precheck = closeout.get("dynamicLinkPrecheckDigest")
    digest = precheck if isinstance(precheck, str) else "not-executed"
    return digest_document(
        {
            **_flags(bool(performed), bool(closeout.get("realModelExecuted"))),
            **_links(plan, digest),
            "planDigest": plan["planDigest"],
            "priorPlanDigest": plan["priorPlanDigest"],
            "readinessOutcome": outcome,
            "reason": reason,
            "sessionId": plan["sessionId"],
            "verdict": verdict,
        },
        "inference-retry-track9-readiness",
        "identityDigest",
    )


def _links(plan: dict[str, Any], precheck_digest: str) -> dict[str, str]:
    return {
        "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
        "dependencyClosureDigest": plan["dependencyClosureDigest"],
        "dynamicLinkPrecheckDigest": precheck_digest,
    }


def _flags(performed: bool, executed: bool) -> dict[str, Any]:
    return {
        "calibrationStatus": "not-approved",
        "installationAuthorized": False,
        "measurementPerformed": performed,
        "productionReady": False,
        "realModelExecuted": executed,
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
    }


def _from_phases(
    closeout: dict[str, Any],
    summary: dict[str, Any] | None,
) -> tuple[str, str, str]:
    stop = closeout.get("stopCause")
    if isinstance(stop, str) and stop in _AUTHORITY:
        return "blocked", _BLOCKED, stop
    phases = closeout.get("phases")
    if not isinstance(phases, list) or any(item.get("status") != "passed" for item in phases):
        reason = stop if isinstance(stop, str) else "measurement-not-performed"
        if closeout.get("closeoutState") == "stopped":
            reason = stop if isinstance(stop, str) else "phase-stopped"
        return "not-ready", _NOT_READY, reason[:80]
    if summary is None or summary.get("gatesUnchanged") is not True:
        return "not-ready", _NOT_READY, "summary-missing"
    if (
        summary.get("comparisonWinner") is not None
        or summary.get("calibrationStatus") != "not-approved"
        or summary.get("productionReady") is not False
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
