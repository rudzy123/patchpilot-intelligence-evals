"""Advisory Track 10 readiness. This record does not select a candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.corpus_continuation_plan import (
    PLANNED_RUNS,
    artifact_pins,
    identity_fields,
    load_corpus_plan,
)
from patchpilot_intelligence_evals.measurement_plan import MeasurementError, digest_document
from patchpilot_intelligence_evals.schemas import repo_root

_RECORD = Path("candidates/authorization/track10-readiness.json")
_READY = "TRACK 10 CANDIDATE DISPOSITION REVIEW READY"
_RESIDUALS = "TRACK 10 CANDIDATE DISPOSITION REVIEW READY WITH DOCUMENTED RESIDUALS"
_NOT_READY = "TRACK 10 CANDIDATE DISPOSITION REVIEW NOT READY"
_BLOCKED = "BLOCKED BY UNRESOLVED AUTHORITY"
_AUTHORITY = frozenset(
    {
        "approval-required",
        "compatibility-failure",
        "corpus-mismatch",
        "digest-mismatch",
        "gold-visible",
        "isolation-failure",
        "network-violation",
        "plan-consumed",
        "prompt-mismatch",
        "raw-output-unretained",
        "response-schema-mismatch",
        "result-root-reuse",
        "unverified-dependency",
    }
)


def build_track10_template() -> dict[str, Any]:
    """Committed readiness before any corpus run. The verdict stays not ready."""
    plan = load_corpus_plan()
    return digest_document(
        _body(
            plan,
            outcome="not-ready",
            verdict=_NOT_READY,
            reason="not-executed",
            state="not-closed",
            stop=None,
            completed=0,
            performed=False,
            executed=False,
            cleanup="not-performed",
            retention="not-performed",
        ),
        "track10-readiness",
        "identityDigest",
    )


def load_track10_template() -> dict[str, Any]:
    """Load the committed readiness record and require it to match the builder."""
    loaded = json.loads((repo_root() / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_track10_template():
        raise MeasurementError("record-drift")
    return loaded


def recommend(closeout: dict[str, Any], summary: dict[str, Any] | None) -> dict[str, Any]:
    """Choose one advisory verdict from a sealed closeout."""
    plan = load_corpus_plan()
    outcome, verdict, reason = _decision(closeout, summary, plan)
    return digest_document(
        _body(
            plan,
            outcome=outcome,
            verdict=verdict,
            reason=reason,
            state=str(closeout.get("closeoutState", "not-closed")),
            stop=closeout.get("stopCause") if isinstance(closeout.get("stopCause"), str) else None,
            completed=int(closeout.get("completedRuns", 0)),
            performed=bool(closeout.get("measurementPerformed")),
            executed=bool(closeout.get("realModelExecuted")),
            cleanup=str(closeout.get("cleanup", "not-performed")),
            retention=str(closeout.get("retention", "not-performed")),
        ),
        "track10-readiness",
        "identityDigest",
    )


def _decision(
    closeout: dict[str, Any],
    summary: dict[str, Any] | None,
    plan: dict[str, Any],
) -> tuple[str, str, str]:
    if _drift(closeout, plan) or (summary is not None and _drift(summary, plan)):
        return "blocked", _BLOCKED, "unresolved-authority"
    stop = closeout.get("stopCause")
    if isinstance(stop, str) and stop in _AUTHORITY:
        return "blocked", _BLOCKED, stop
    if closeout.get("closeoutState") != "closed" or summary is None:
        reason = stop if isinstance(stop, str) else "not-executed"
        return "not-ready", _NOT_READY, reason[:80]
    if (
        summary.get("gatesUnchanged") is not True
        or summary.get("percentageGatesCalibrated") is not False
    ):
        return "blocked", _BLOCKED, "unresolved-authority"
    gates = summary.get("gates")
    if not isinstance(gates, list) or not gates:
        return "not-ready", _NOT_READY, "summary-missing"
    if any(item.get("kind") == "invariant" and item.get("status") == "fail" for item in gates):
        return "not-ready", _NOT_READY, "invariant-gate"
    inconsistent = summary.get("repetitionConsistency") == "inconsistent"
    if any(item.get("status") != "pass" for item in gates) or inconsistent:
        return "ready-with-documented-residuals", _RESIDUALS, "percentage-or-consistency"
    counts = summary.get("failureAuthorityCounts")
    if isinstance(counts, dict) and int(counts.get("unresolved", 0)) > 0:
        return "ready-with-documented-residuals", _RESIDUALS, "unresolved-failure"
    return "ready", _READY, "gates-passed"


def _drift(document: dict[str, Any], plan: dict[str, Any]) -> bool:
    return any(
        (
            document.get("planDigest") != plan["planDigest"],
            document.get("productionReady") is not False,
            document.get("selectionOutcome") != "no-selection",
            document.get("calibrationStatus") != "not-approved",
            document.get("comparisonWinner") is not None,
            document.get("installationAuthorized") is not False,
        )
    )


def _body(
    plan: dict[str, Any],
    *,
    outcome: str,
    verdict: str,
    reason: str,
    state: str,
    stop: str | None,
    completed: int,
    performed: bool,
    executed: bool,
    cleanup: str,
    retention: str,
) -> dict[str, Any]:
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        "cleanup": cleanup,
        "closeoutState": state,
        "completedRuns": completed,
        "measurementPerformed": performed,
        "memoryResidual": _memory(plan),
        "missingRuns": PLANNED_RUNS - completed,
        "plannedRuns": PLANNED_RUNS,
        "readinessOutcome": outcome,
        "realModelExecuted": executed,
        "reason": reason,
        "recordKind": "readiness",
        "retention": retention,
        "runInvoked": performed,
        "stopCause": stop,
        "verdict": verdict,
    }


def _memory(plan: dict[str, Any]) -> dict[str, Any]:
    memory = plan["acceptedMemory"]
    return {
        "ceilingBytes": memory["ceilingBytes"],
        "conclusion": memory["conclusion"],
        "minimumHeadroomBytes": memory["minimumHeadroomBytes"],
        "remeasured": False,
        "reviewDigest": memory["reviewDigest"],
        "sourceDigest": memory["sourceDigest"],
    }
