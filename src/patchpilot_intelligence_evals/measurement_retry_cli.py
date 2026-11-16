"""Track 8B-R1 commands. Validators read committed records. Execute stays outside CI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.corrected_behavioral_measurement import (
    build_run_template,
    build_summary_template,
    execute_corpus,
    load_run_template,
    load_summary_template,
)
from patchpilot_intelligence_evals.corrected_context_measurement import (
    build_context_template,
    build_smoke_template,
    execute_phase,
    load_context_template,
    load_smoke_template,
)
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.measurement_retry_closeout import (
    build_closeout,
    load_closeout_template,
)
from patchpilot_intelligence_evals.measurement_retry_plan import (
    load_retry_approval,
    load_retry_plan,
    require_open_retry_plan,
    require_retry_approval,
    validate_retry_result_root,
)
from patchpilot_intelligence_evals.measurement_retry_preflight import (
    PHASE_FILES,
    load_compatibility_template,
    load_preflight_template,
    run_compatibility,
    run_preflight,
    write_new,
)
from patchpilot_intelligence_evals.retry_track9_readiness import (
    load_track9_template,
    recommend,
)
from patchpilot_intelligence_evals.track8b_r1_records import (
    load_corrected_closeout,
    load_dependency_defect,
    load_memory_defect,
    load_retry_disposition,
    load_stopped_attempt,
    load_stopped_track9,
    load_track8b_r1_review,
)

VALIDATION = (
    "measurement-retry-plan-validation",
    "measurement-retry-approval-validation",
    "measurement-retry-preflight-validation",
    "template-compatibility-result-validation",
    "retry-smoke-execution-validation",
    "retry-context-memory-validation",
    "retry-behavioral-run-validation",
    "retry-closeout-validation",
    "retry-track9-readiness-validation",
    "track8b-r1-stopped-attempt-validation",
    "track8b-r1-dependency-mount-defect-validation",
    "track8b-r1-memory-conclusion-defect-validation",
    "track8b-r1-corrected-closeout-validation",
    "track8b-r1-plan-disposition-validation",
    "track8b-r1-stopped-track9-validation",
    "track8b-r1-review-validation",
)
EXECUTE = frozenset(
    {
        "measurement-retry-context",
        "measurement-retry-corpus",
        "measurement-retry-execute",
        "measurement-retry-preflight",
        "measurement-retry-short-generation",
        "measurement-retry-smoke",
    }
)


def _record_summaries() -> dict[str, Any]:
    """Path-free summaries for the durable correction records."""
    attempt = load_stopped_attempt()
    dependency = load_dependency_defect()
    memory = load_memory_defect()
    closeout = load_corrected_closeout()
    disposition = load_retry_disposition()
    readiness = load_stopped_track9()
    review = load_track8b_r1_review()
    return {
        "track8b-r1-stopped-attempt-validation": {
            "attemptOutcome": attempt["attemptOutcome"],
            "failureCategory": attempt["failureCategory"],
            "runInvoked": attempt["runInvoked"],
        },
        "track8b-r1-dependency-mount-defect-validation": {
            "defectStatus": dependency["status"],
            "modelSessionCreated": dependency["modelSessionCreated"],
            "providerMounted": dependency["providerMounted"],
        },
        "track8b-r1-memory-conclusion-defect-validation": {
            "correctedConclusion": memory["correctedConclusion"],
            "smokeEvidenceRole": memory["smokeEvidenceRole"],
        },
        "track8b-r1-corrected-closeout-validation": {
            "memoryConclusion": closeout["memoryConclusion"],
            "track9Readiness": closeout["track9Readiness"],
        },
        "track8b-r1-plan-disposition-validation": {
            "planDisposition": disposition["planDisposition"],
            "replacementPlanDigest": disposition["replacementPlanDigest"],
            "reusable": disposition["reusable"],
        },
        "track8b-r1-stopped-track9-validation": {
            "readinessOutcome": readiness["readinessOutcome"],
            "verdict": readiness["verdict"],
        },
        "track8b-r1-review-validation": {
            "memoryConclusion": review["memoryConclusion"],
            "reviewStatus": review["reviewStatus"],
        },
    }


_PHASES = (
    "one-token-smoke",
    "short-generation",
    "context-4096",
    "context-8192",
)


def register(commands: Any) -> None:
    """Add Track 8B-R1 subcommands."""
    for name in VALIDATION:
        commands.add_parser(name)
    preflight = commands.add_parser("measurement-retry-preflight")
    _roots(preflight, approval=False)
    for name in (
        "measurement-retry-execute",
        "measurement-retry-smoke",
        "measurement-retry-short-generation",
        "measurement-retry-corpus",
    ):
        _roots(commands.add_parser(name), approval=True)
    context = commands.add_parser("measurement-retry-context")
    _roots(context, approval=True)
    context.add_argument("--tokens", required=True, choices=("4096", "8192"))


def handle(command: str, args: argparse.Namespace) -> dict[str, Any]:
    """Run one retry command and return a path-free summary."""
    if command == "measurement-retry-plan-validation":
        plan = load_retry_plan()
        return _ok(
            executionStatus=plan["executionStatus"],
            planDigest=plan["planDigest"],
            priorPlanDigest=plan["priorPlanDigest"],
        )
    if command == "measurement-retry-approval-validation":
        approval = load_retry_approval()
        return _ok(approvalStatus=approval["approvalStatus"], planDigest=approval["planDigest"])
    if command == "measurement-retry-preflight-validation":
        document = load_preflight_template()
        return _ok(preflightStatus=document["status"], runInvoked=document["runInvoked"])
    if command == "template-compatibility-result-validation":
        document = load_compatibility_template()
        return _ok(
            compatibility=document["compatibility"],
            runInvoked=document["runInvoked"],
            sessionCreated=document["sessionCreated"],
        )
    if command == "retry-smoke-execution-validation":
        document = load_smoke_template()
        build_smoke_template()
        return _ok(phase=document["phase"], realModelExecuted=False)
    if command == "retry-context-memory-validation":
        document = load_context_template()
        build_context_template()
        return _ok(phase=document["phase"], realModelExecuted=False)
    if command == "retry-behavioral-run-validation":
        document = load_run_template()
        summary = load_summary_template()
        build_run_template()
        build_summary_template()
        return _ok(
            comparisonWinner=summary["comparisonWinner"],
            exitClassification=document["exitClassification"],
        )
    if command == "retry-closeout-validation":
        document = load_closeout_template()
        return _ok(closeoutState=document["closeoutState"])
    if command == "retry-track9-readiness-validation":
        document = load_track9_template()
        return _ok(readinessOutcome=document["readinessOutcome"], verdict=document["verdict"])
    summaries = _record_summaries()
    if command in summaries:
        return _ok(**summaries[command])
    if command == "measurement-retry-preflight":
        require_open_retry_plan()
        document = run_preflight(
            _path(args.runtime_cache), _path(args.model_cache), _path(args.result_root)
        )
        return _ok(planDigest=document["planDigest"], runInvoked=document["runInvoked"])
    return _execute(command, args)


def _execute(command: str, args: argparse.Namespace) -> dict[str, Any]:
    require_open_retry_plan()
    runtime = _path(args.runtime_cache)
    model = _path(args.model_cache)
    result = _path(args.result_root)
    approval = str(args.operator_approval)
    if command == "measurement-retry-execute":
        return _execute_all(approval, runtime, model, result)
    if command == "measurement-retry-smoke":
        return _phase_summary(
            execute_phase(
                "one-token-smoke",
                approval=approval,
                runtime_root=runtime,
                model_root=model,
                result_root=result,
                executed=True,
            )
        )
    if command == "measurement-retry-short-generation":
        return _phase_summary(
            execute_phase(
                "short-generation",
                approval=approval,
                runtime_root=runtime,
                model_root=model,
                result_root=result,
                executed=True,
            )
        )
    if command == "measurement-retry-context":
        phase = "context-4096" if args.tokens == "4096" else "context-8192"
        return _phase_summary(
            execute_phase(
                phase,
                approval=approval,
                runtime_root=runtime,
                model_root=model,
                result_root=result,
                executed=True,
            )
        )
    if command == "measurement-retry-corpus":
        document = execute_corpus(
            approval=approval,
            runtime_root=runtime,
            model_root=model,
            result_root=result,
            executed=True,
        )
        return _ok(comparisonWinner=None, realModelExecuted=document["realModelExecuted"])
    raise MeasurementError("phase")


def _execute_all(approval: str, runtime: Path, model: Path, result: Path) -> dict[str, Any]:
    require_retry_approval(approval)
    if (result / PHASE_FILES["preflight"]).is_file():
        validate_retry_result_root(result, resume=True)
    else:
        run_preflight(runtime, model, result)
    if not (result / PHASE_FILES["template-compatibility"]).is_file():
        run_compatibility(model, result)
    stop: str | None = None
    try:
        for phase in _PHASES:
            document = execute_phase(
                phase,
                approval=approval,
                runtime_root=runtime,
                model_root=model,
                result_root=result,
                executed=True,
            )
            if document.get("exitClassification") != "success":
                stop = str(document.get("stopCause") or document["exitClassification"])
                break
        else:
            execute_corpus(
                approval=approval,
                runtime_root=runtime,
                model_root=model,
                result_root=result,
                executed=True,
            )
    except MeasurementError as exc:
        stop = exc.code
    closeout = build_closeout(result)
    summary = _optional_summary(result)
    readiness = recommend(closeout, summary)
    write_new(result, "closeout.json", closeout)
    write_new(result, "track9-readiness.json", readiness)
    status = "ok" if stop is None and readiness["readinessOutcome"] != "blocked" else "stopped"
    return {
        "calibrationStatus": "not-approved",
        "planDigest": closeout["planDigest"],
        "productionReady": False,
        "readinessOutcome": readiness["readinessOutcome"],
        "selectionOutcome": "no-selection",
        "status": status,
        "stopCause": stop,
        "verdict": readiness["verdict"],
    }


def _optional_summary(result: Path) -> dict[str, Any] | None:
    path = result / PHASE_FILES["corpus-evaluation"]
    if not path.is_file():
        return None
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    return loaded


def _phase_summary(document: dict[str, Any]) -> dict[str, Any]:
    status = "ok" if document.get("exitClassification") == "success" else "stopped"
    return {
        "exitClassification": document.get("exitClassification"),
        "phase": document.get("phase"),
        "productionReady": False,
        "selectionOutcome": "no-selection",
        "status": status,
        "stopCause": document.get("stopCause"),
    }


def _roots(parser: argparse.ArgumentParser, *, approval: bool) -> None:
    parser.add_argument("--runtime-cache", required=True)
    parser.add_argument("--model-cache", required=True)
    parser.add_argument("--result-root", required=True)
    if approval:
        parser.add_argument("--operator-approval", required=True)


def _path(value: str) -> Path:
    return Path(value)


def _ok(**fields: object) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "calibrationStatus": "not-approved",
        "productionReady": False,
        "selectionOutcome": "no-selection",
        "status": "ok",
    }
    payload.update(fields)
    return payload
