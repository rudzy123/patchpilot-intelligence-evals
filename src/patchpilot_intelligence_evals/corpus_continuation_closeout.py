"""Close a corpus continuation without changing selection or production readiness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.corpus_continuation_plan import (
    PHASE_ORDER,
    PLANNED_RUNS,
    artifact_pins,
    identity_fields,
    load_corpus_plan,
)
from patchpilot_intelligence_evals.measurement_plan import MeasurementError, digest_document
from patchpilot_intelligence_evals.schemas import repo_root

_TEMPLATE = Path("candidates/templates/corpus-continuation-closeout-template.json")


def build_closeout_template() -> dict[str, Any]:
    """Committed closeout. No run has been sealed."""
    plan = load_corpus_plan()
    return digest_document(
        _body(
            plan,
            state="not-closed",
            stop=None,
            completed=0,
            authorities={},
            gates=_unmeasured_gates(),
            cleanup="not-performed",
            retention="not-performed",
            blocker="operator-approval",
            phases=_phases("not-executed"),
            performed=False,
            completed_measurement=False,
            invoked=False,
            executed=False,
        ),
        "corpus-continuation-closeout",
        "identityDigest",
    )


def load_closeout_template() -> dict[str, Any]:
    """Load the committed closeout and require it to match the builder."""
    loaded = json.loads((repo_root() / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_closeout_template():
        raise MeasurementError("record-drift")
    return loaded


def build_closeout(
    summary: dict[str, Any],
    stop: str | None,
    preflight: dict[str, Any] | None,
) -> dict[str, Any]:
    """Seal planned, missing, authority, gate, memory, cleanup, and retention facts."""
    plan = load_corpus_plan()
    if summary.get("planDigest") != plan["planDigest"]:
        raise MeasurementError("digest-mismatch")
    completed = int(summary["completedRuns"])
    state = _state(summary, stop)
    cleanup = "failed" if stop == "cleanup-failure" else "reaped" if completed else "not-performed"
    retention = (
        "failed"
        if stop == "raw-output-unretained"
        else "retained"
        if completed
        else "not-performed"
    )
    if state == "closed":
        blocker = "principal-architect-review"
    elif state == "stopped":
        blocker = stop if isinstance(stop, str) else "incomplete"
    else:
        blocker = "operator-approval"
    counts = summary.get("failureAuthorityCounts")
    authorities = counts if isinstance(counts, dict) else {}
    gates = summary.get("gates")
    return digest_document(
        _body(
            plan,
            state=state,
            stop=stop,
            completed=completed,
            authorities=authorities,
            gates=list(gates) if isinstance(gates, list) else [],
            cleanup=cleanup,
            retention=retention,
            blocker=blocker,
            phases=_live_phases(preflight, state, stop),
            performed=bool(summary.get("measurementPerformed")),
            completed_measurement=state == "closed",
            invoked=bool(summary.get("runInvoked")),
            executed=bool(summary.get("realModelExecuted")),
        ),
        "corpus-continuation-closeout",
        "identityDigest",
    )


def _body(
    plan: dict[str, Any],
    *,
    state: str,
    stop: str | None,
    completed: int,
    authorities: dict[str, Any],
    gates: list[Any],
    cleanup: str,
    retention: str,
    blocker: str,
    phases: list[dict[str, str]],
    performed: bool,
    completed_measurement: bool,
    invoked: bool,
    executed: bool,
) -> dict[str, Any]:
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        "blocker": blocker,
        "cleanup": cleanup,
        "closeoutState": state,
        "completedRuns": completed,
        "failureAuthorityCounts": _counts(authorities),
        "gates": gates,
        "measurementCompleted": completed_measurement,
        "measurementPerformed": performed,
        "memoryResidual": _memory(plan),
        "missingRuns": PLANNED_RUNS - completed,
        "modelSessionCreated": invoked,
        "phases": phases,
        "plannedRuns": PLANNED_RUNS,
        "realModelExecuted": executed,
        "recordKind": "closeout",
        "residuals": [] if stop is None else [stop],
        "retention": retention,
        "runInvoked": invoked,
        "stopCause": stop,
    }


def _state(summary: dict[str, Any], stop: str | None) -> str:
    if summary.get("completeness") == "not-executed" and stop is None:
        return "not-closed"
    if stop is None and summary.get("completeness") == "complete":
        return "closed"
    return "stopped"


def _counts(authorities: dict[str, Any]) -> dict[str, int]:
    from patchpilot_intelligence_evals.corpus_continuation_plan import FAILURE_AUTHORITIES

    return {name: int(authorities.get(name, 0)) for name in FAILURE_AUTHORITIES}


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


def _phases(status: str) -> list[dict[str, str]]:
    return [{"phase": phase, "status": status} for phase in PHASE_ORDER]


def _live_phases(
    preflight: dict[str, Any] | None,
    state: str,
    stop: str | None,
) -> list[dict[str, str]]:
    if preflight is None:
        return _phases("not-executed")
    template = _check_status(str(preflight.get("templateStatus")))
    link = _check_status(str(preflight.get("dynamicLinkStatus")))
    preflight_status = _check_status(str(preflight.get("preflightStatus")))
    if state == "closed":
        corpus = "passed"
    elif preflight_status == "failed":
        corpus = "withheld"
    elif stop is None:
        corpus = "not-executed"
    else:
        corpus = "failed"
    return [
        {"phase": "preflight", "status": preflight_status},
        {"phase": "template-compatibility", "status": template},
        {"phase": "dynamic-link-precheck", "status": link},
        {"phase": "corpus-evaluation", "status": corpus},
    ]


def _check_status(value: str) -> str:
    if value in {"passed", "supported"}:
        return "passed"
    if value in {"failed", "unavailable"}:
        return "failed"
    return "not-executed"


def _unmeasured_gates() -> list[dict[str, Any]]:
    from patchpilot_intelligence_evals.evaluator import GATE_NAMES
    from patchpilot_intelligence_evals.metrics import gate_from_metric, measure

    rows: list[dict[str, Any]] = []
    for name in GATE_NAMES:
        gate = gate_from_metric(name, measure(0, 0))
        rows.append(
            {
                "denominator": gate["denominator"],
                "gate": name,
                "kind": gate["kind"],
                "numerator": gate["numerator"],
                "status": gate["status"],
            }
        )
    return rows
