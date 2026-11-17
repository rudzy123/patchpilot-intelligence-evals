"""Close an inference retry without changing selection or production readiness."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.inference_retry_plan import PHASE_ORDER, load_inference_plan
from patchpilot_intelligence_evals.inference_retry_preflight import PHASE_FILES, passed
from patchpilot_intelligence_evals.measurement_plan import MeasurementError, digest_document
from patchpilot_intelligence_evals.measurement_retry_closeout import context_memory_conclusion
from patchpilot_intelligence_evals.schemas import repo_root

_TEMPLATE = Path("candidates/templates/inference-retry-closeout-template.json")
REQUIRED_CONTEXT_PHASES = ("context-4096", "context-8192")
_INFRASTRUCTURE = frozenset(
    {
        "cleanup-failure",
        "isolation-failure",
        "network-violation",
        "precheck-failed",
        "telemetry-unresolved",
        "unverified-dependency",
    }
)


def build_closeout_template() -> dict[str, Any]:
    """Committed closeout. No phase has run."""
    plan = load_inference_plan()
    return digest_document(
        _body(plan, _empty_phases(), None, "not-performed", False, "not-executed"),
        "inference-retry-closeout",
        "identityDigest",
    )


def load_closeout_template() -> dict[str, Any]:
    """Load the committed closeout and require it to match the builder."""
    loaded = json.loads((repo_root() / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_closeout_template():
        raise MeasurementError("record-drift")
    return loaded


def build_closeout(result_root: Path) -> dict[str, Any]:
    """Summarize external phase files. A measured stop stays reviewable."""
    plan = load_inference_plan()
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
    document = _body(plan, phases, stop, cleanup, executed, _precheck_digest(result_root))
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
    return digest_document(document, "inference-retry-closeout", "identityDigest")


def _body(
    plan: dict[str, Any],
    phases: list[dict[str, str]],
    stop: str | None,
    cleanup: str,
    executed: bool,
    precheck_digest: str,
) -> dict[str, Any]:
    recommendation, rationale = _proportionality(stop)
    return {
        "behavioralConclusion": "not-measured",
        "calibrationRemainedNotApproved": True,
        "calibrationStatus": "not-approved",
        "cleanup": cleanup,
        "closeoutState": "not-closed",
        "comparisonWinner": None,
        "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
        "dependencyClosureDigest": plan["dependencyClosureDigest"],
        "dynamicLinkPrecheckDigest": precheck_digest,
        "furtherRetryAssumed": False,
        "installationAuthorized": False,
        "measurementCompleted": False,
        "measurementPerformed": False,
        "memoryConclusion": "unavailable",
        "modelSessionCreated": False,
        "phases": phases,
        "planDigest": plan["planDigest"],
        "priorPlanDigest": plan["priorPlanDigest"],
        "productionReady": False,
        "proportionalityRecommendation": recommendation,
        "proportionalityRationale": rationale,
        "realModelExecuted": executed,
        "residuals": [],
        "resultRootClass": plan["resultRootClass"],
        "runInvoked": False,
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
        "sessionId": plan["sessionId"],
        "stopCause": stop,
    }


def _proportionality(stop: str | None) -> tuple[str, str]:
    if stop in _INFRASTRUCTURE:
        return "review-required", "infrastructure-defect-requires-review"
    return "not-applicable", "not-applicable"


def _precheck_digest(result_root: Path) -> str:
    path = result_root / PHASE_FILES["dynamic-link-precheck"]
    if not path.is_file() or path.is_symlink():
        return "not-executed"
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise MeasurementError("record-type")
    digest = document.get("identityDigest")
    if not isinstance(digest, str):
        return "not-executed"
    return digest


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
    if phase in {"preflight", "template-compatibility", "dynamic-link-precheck"}:
        ok = passed(phase, document)
        cause = None if ok else _pre_run_cause(phase, document)
        return ("passed" if ok else "failed", cause, "reaped", False, flags)
    if phase == "corpus-evaluation":
        cause = document.get("stopCause")
        finished = (
            document.get("recordKind") == "summary"
            and document.get("ungatedCanonicalAgreement") != "not-executed"
            and cause is None
        )
        if finished:
            stop = None
        elif isinstance(cause, str) and cause:
            stop = cause
        else:
            stop = "prior-phase-failed"
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


def _pre_run_cause(phase: str, document: dict[str, Any]) -> str:
    if phase == "dynamic-link-precheck":
        return str(document.get("stopCause") or "precheck-failed")
    if phase == "template-compatibility":
        return str(document.get("compatibility") or "compatibility-failure")
    return "missing-root"


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


def _behavioral_conclusion(phases: list[dict[str, str]]) -> str:
    corpus = next(item for item in phases if item["phase"] == "corpus-evaluation")
    if corpus["status"] == "passed":
        return "measured"
    if corpus["status"] == "withheld":
        return "withheld"
    if corpus["status"] == "failed":
        return "measured"
    return "not-measured"
