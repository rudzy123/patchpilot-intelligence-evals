"""Close a retry session without changing selection or production readiness."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.cgroup_memory import contradictory_resident
from patchpilot_intelligence_evals.measurement_plan import MeasurementError, digest_document
from patchpilot_intelligence_evals.measurement_retry_plan import (
    PHASE_ORDER,
    load_retry_plan,
    session_stop,
)
from patchpilot_intelligence_evals.measurement_retry_preflight import PHASE_FILES, passed
from patchpilot_intelligence_evals.schemas import repo_root

_TEMPLATE = Path("candidates/templates/retry-closeout-template.json")
REQUIRED_CONTEXT_PHASES = ("context-4096", "context-8192")


def build_closeout_template() -> dict[str, Any]:
    """Committed closeout. No phase has run."""
    plan = load_retry_plan()
    return digest_document(
        _body(plan, _empty_phases(), None, "not-performed", False),
        "retry-closeout",
        "identityDigest",
    )


def load_closeout_template() -> dict[str, Any]:
    """Load the committed closeout and require it to match the builder."""
    loaded = json.loads((repo_root() / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != build_closeout_template():
        raise MeasurementError("record-drift")
    return loaded


def build_closeout(result_root: Path) -> dict[str, Any]:
    """Summarize external phase files. A measured stop stays reviewable."""
    plan = load_retry_plan()
    phases: list[dict[str, str]] = []
    stop: str | None = None
    cleanup = "reaped"
    executed = False
    run_invoked = False
    session_created = False
    failed = False
    for phase in PHASE_ORDER:
        status, phase_stop, phase_cleanup, phase_executed, flags = _phase_status(result_root, phase)
        if status == "not-executed" and failed:
            status = "withheld"
        phases.append({"phase": phase, "status": status})
        if status == "failed":
            failed = True
            if stop is None:
                stop = phase_stop
        if phase_cleanup == "failed":
            cleanup = "failed"
        executed = executed or phase_executed
        run_invoked = run_invoked or flags[0]
        session_created = session_created or flags[1]
    if not any(item["status"] != "not-executed" for item in phases):
        state = "not-closed"
        cleanup = "not-performed"
    elif stop is None and all(item["status"] == "passed" for item in phases):
        state = "closed"
    else:
        state = "stopped"
    document = _body(plan, phases, stop, cleanup, executed)
    document["closeoutState"] = state
    document["measurementPerformed"] = state != "not-closed"
    document["measurementCompleted"] = state in {"closed", "stopped"}
    document["runInvoked"] = run_invoked
    document["modelSessionCreated"] = session_created
    document["realModelExecuted"] = executed
    document["memoryConclusion"] = context_memory_conclusion(_context_records(result_root))
    document["behavioralConclusion"] = _behavioral_conclusion(phases)
    if stop is not None:
        document["residuals"] = [stop[:80]]
    return digest_document(document, "retry-closeout", "identityDigest")


def _body(
    plan: dict[str, Any],
    phases: list[dict[str, str]],
    stop: str | None,
    cleanup: str,
    executed: bool,
) -> dict[str, Any]:
    return {
        "behavioralConclusion": "not-measured",
        "calibrationRemainedNotApproved": True,
        "calibrationStatus": "not-approved",
        "cleanup": cleanup,
        "closeoutState": "not-closed",
        "comparisonWinner": None,
        "installationAuthorized": False,
        "measurementCompleted": False,
        "measurementPerformed": False,
        "memoryConclusion": "unavailable",
        "modelSessionCreated": False,
        "phases": phases,
        "planDigest": plan["planDigest"],
        "priorPlanDigest": plan["priorPlanDigest"],
        "productionReady": False,
        "realModelExecuted": executed,
        "residuals": [],
        "resultRootClass": plan["resultRootClass"],
        "runInvoked": False,
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
        "sessionId": plan["sessionId"],
        "stopCause": stop,
    }


def _empty_phases() -> list[dict[str, str]]:
    return [{"phase": phase, "status": "not-executed"} for phase in PHASE_ORDER]


def _phase_status(
    result_root: Path, phase: str
) -> tuple[str, str | None, str, bool, tuple[bool, bool]]:
    path = result_root / PHASE_FILES[phase]
    if not path.is_file() or path.is_symlink():
        return "not-executed", None, "not-performed", False, (False, False)
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise MeasurementError("record-type")
    flags = (bool(document.get("runInvoked")), bool(document.get("modelSessionCreated")))
    if phase == "preflight":
        ok = passed(phase, document)
        return (
            "passed" if ok else "failed",
            None if ok else "missing-root",
            "reaped",
            False,
            flags,
        )
    if phase == "template-compatibility":
        ok = passed(phase, document)
        cause = None if ok else str(document.get("compatibility") or "compatibility-failure")
        return ("passed" if ok else "failed", cause, "reaped", False, flags)
    if phase == "corpus-evaluation":
        finished = (
            document.get("recordKind") == "summary"
            and document.get("ungatedCanonicalAgreement") != "not-executed"
        )
        stop = None if finished else _corpus_stop(result_root)
        return (
            "passed" if finished else "failed",
            stop,
            "reaped",
            bool(document.get("realModelExecuted")),
            flags,
        )
    classification = str(document.get("exitClassification", "not-executed"))
    if classification == "not-executed":
        return "not-executed", None, "not-performed", False, flags
    if classification == "success":
        return (
            "passed",
            None,
            str(document.get("processCleanup", "reaped")),
            bool(document.get("realModelExecuted")),
            flags,
        )
    return (
        "failed",
        classification,
        str(document.get("processCleanup", "failed")),
        bool(document.get("realModelExecuted")),
        flags,
    )


def context_memory_conclusion(
    records: Mapping[str, dict[str, Any] | None],
    *,
    required: tuple[str, ...] = REQUIRED_CONTEXT_PHASES,
) -> str:
    """Conclude context memory. An empty required set cannot be within-ceiling."""
    if not required:
        return "unavailable"
    issues = [
        _phase_memory_issue(records.get(phase))
        for phase in required
        if records.get(phase) is not None
    ]
    if not issues:
        return "unavailable"
    if "oom" in issues:
        return "oom"
    if "unresolved" in issues:
        return "unresolved"
    if "exceeded" in issues:
        return "exceeded"
    if len(issues) != len(required) or any(item != "ok" for item in issues):
        return "unavailable"
    return "within-ceiling"


def _context_records(result_root: Path) -> dict[str, dict[str, Any] | None]:
    found: dict[str, dict[str, Any] | None] = {}
    for phase in REQUIRED_CONTEXT_PHASES:
        path = result_root / PHASE_FILES[phase]
        if not path.is_file() or path.is_symlink():
            found[phase] = None
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise MeasurementError("record-type")
        found[phase] = document
    return found


def _phase_memory_issue(record: dict[str, Any] | None) -> str:
    if record is None:
        return "unavailable"
    if record.get("exitClassification") == "oom" or record.get("stopCause") == "oom":
        return "oom"
    issues = [_window_issue(record.get("coldMemory")), _window_issue(record.get("warmMemory"))]
    if "oom" in issues:
        return "oom"
    if "unresolved" in issues:
        return "unresolved"
    if "exceeded" in issues:
        return "exceeded"
    if record.get("exitClassification") != "success":
        return "unavailable"
    if record.get("processCleanup") != "reaped" or record.get("networkResult") != "denied":
        return "unavailable"
    return "ok"


def _window_issue(memory: object) -> str | None:
    if not isinstance(memory, dict):
        return "unresolved"
    if _oom(memory):
        return "oom"
    if memory.get("telemetry") == "exceeded":
        return "exceeded"
    peak = memory.get("cgroupPeakBytes")
    current = memory.get("cgroupCurrentBytes")
    complete = (
        isinstance(peak, int)
        and isinstance(current, int)
        and memory.get("telemetry") == "complete"
        and not contradictory_resident(memory)
    )
    if not complete:
        return "unresolved"
    if isinstance(peak, int) and peak > MEMORY_CAP:
        return "exceeded"
    return None


def _oom(memory: Mapping[str, Any]) -> bool:
    if memory.get("telemetry") == "oom":
        return True
    oom_events = memory.get("oomEvents")
    if isinstance(oom_events, int) and oom_events > 0:
        return True
    events = memory.get("memoryEvents")
    if not isinstance(events, dict):
        return False
    for key in ("oom", "oomKill"):
        count = events.get(key)
        if isinstance(count, int) and count > 0:
            return True
    return False


def _behavioral_conclusion(phases: list[dict[str, str]]) -> str:
    corpus = next(item for item in phases if item["phase"] == "corpus-evaluation")
    if corpus["status"] == "passed":
        return "measured"
    if corpus["status"] == "withheld":
        return "withheld"
    if corpus["status"] == "failed":
        return "measured"
    return "not-measured"


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
