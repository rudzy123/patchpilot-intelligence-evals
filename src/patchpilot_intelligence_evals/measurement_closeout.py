"""Close a measurement session without changing selection or production readiness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.context_measurement import PHASE_FILES
from patchpilot_intelligence_evals.measurement_plan import (
    PHASE_ORDER,
    MeasurementError,
    authority,
    digest_document,
    load_measurement_plan,
    session_stop,
)

_TEMPLATE = Path("candidates/templates/measurement-closeout-template.json")


def build_closeout_template() -> dict[str, Any]:
    """Committed closeout. No phase has run."""
    plan = load_measurement_plan()
    return digest_document(
        {
            **authority(),
            "cleanup": "not-performed",
            "closeoutState": "not-closed",
            "phases": [{"phase": phase, "status": "not-executed"} for phase in PHASE_ORDER],
            "planDigest": plan["planDigest"],
            "realModelExecuted": False,
            "retainedResultClass": "measurement-result",
            "stopCause": None,
        },
        "measurement-closeout",
        "identityDigest",
    )


def load_closeout_template() -> dict[str, Any]:
    """Load the committed template and require it to match the builder."""
    loaded = json.loads(_TEMPLATE.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != build_closeout_template():
        raise MeasurementError("record-drift")
    return loaded


def build_closeout(result_root: Path) -> dict[str, Any]:
    """Summarize external phase files. A measured stop stays reviewable."""
    plan = load_measurement_plan()
    phases: list[dict[str, str]] = []
    stop: str | None = None
    cleanup = "reaped"
    executed = False
    for phase in PHASE_ORDER:
        status, phase_stop, phase_cleanup, phase_executed = _phase_status(result_root, phase)
        phases.append({"phase": phase, "status": status})
        if phase_stop is not None and stop is None:
            stop = phase_stop
        if phase_cleanup == "failed":
            cleanup = "failed"
        executed = executed or phase_executed
    if not any(item["status"] != "not-executed" for item in phases):
        state = "not-closed"
        cleanup = "not-performed"
    elif stop is None and all(item["status"] == "passed" for item in phases):
        state = "closed"
    else:
        state = "stopped"
    return digest_document(
        {
            **authority(),
            "cleanup": cleanup,
            "closeoutState": state,
            "phases": phases,
            "planDigest": plan["planDigest"],
            "realModelExecuted": executed,
            "retainedResultClass": "measurement-result",
            "stopCause": stop,
        },
        "measurement-closeout",
        "identityDigest",
    )


def _phase_status(result_root: Path, phase: str) -> tuple[str, str | None, str, bool]:
    path = result_root / PHASE_FILES[phase]
    if not path.is_file() or path.is_symlink():
        return "not-executed", None, "not-performed", False
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise MeasurementError("record-type")
    if phase == "preflight":
        passed = document.get("status") == "ok"
        return (
            "passed" if passed else "failed",
            None if passed else "missing-root",
            "reaped",
            False,
        )
    if phase == "corpus-evaluation":
        finished = document.get("ungatedCanonicalAgreement") != "not-executed"
        stop = None if finished else _corpus_stop(result_root)
        return (
            "passed" if finished else "failed",
            stop,
            "reaped",
            bool(document.get("realModelExecuted")),
        )
    classification = str(document.get("exitClassification", "not-executed"))
    if classification == "not-executed":
        return "not-executed", None, "not-performed", False
    if classification == "success":
        return (
            "passed",
            None,
            str(document.get("processCleanup", "reaped")),
            bool(document.get("realModelExecuted")),
        )
    return (
        "failed",
        classification,
        str(document.get("processCleanup", "failed")),
        bool(document.get("realModelExecuted")),
    )


def _corpus_stop(result_root: Path) -> str:
    runs = result_root / "runs"
    if not runs.is_dir():
        return "prior-phase-failed"
    for path in sorted(runs.glob("*.json")):
        if path.is_symlink():
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(document, dict) and session_stop(str(document.get("stopCause"))):
            return str(document["stopCause"])
    return "prior-phase-failed"
