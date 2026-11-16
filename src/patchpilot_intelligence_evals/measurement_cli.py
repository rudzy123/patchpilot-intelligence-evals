"""Track 8B commands. Validators read committed records. Execute stays outside CI."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.behavioral_measurement import (
    build_run_template,
    build_summary_template,
    execute_corpus,
)
from patchpilot_intelligence_evals.context_measurement import (
    PHASE_FILES,
    build_context_template,
    build_smoke_template,
    execute_phase,
    run_preflight,
)
from patchpilot_intelligence_evals.measurement_closeout import (
    build_closeout,
    load_closeout_template,
)
from patchpilot_intelligence_evals.measurement_plan import (
    MeasurementError,
    load_measurement_plan,
    load_operator_approval,
)
from patchpilot_intelligence_evals.schemas import validate
from patchpilot_intelligence_evals.track8b_records import (
    load_plan_disposition,
    load_preflight_template,
    load_stopped_attempt,
    load_stopped_closeout,
    load_template_defect,
    load_track8b_review,
)
from patchpilot_intelligence_evals.track9_readiness import (
    load_track9_readiness,
    recommend,
)

VALIDATION = (
    "measurement-plan-validation",
    "measurement-operator-approval-validation",
    "smoke-execution-validation",
    "context-memory-measurement-validation",
    "candidate-behavioral-run-validation",
    "candidate-behavioral-summary-validation",
    "measurement-closeout-validation",
    "track8b-preflight-validation",
    "track8b-stopped-attempt-validation",
    "track8b-plan-disposition-validation",
    "track8b-template-compatibility-defect-validation",
    "track8b-review-validation",
    "track9-readiness-validation",
)
EXECUTE = frozenset(
    {
        "measurement-context",
        "measurement-corpus",
        "measurement-execute",
        "measurement-preflight",
        "measurement-short-generation",
        "measurement-smoke",
    }
)
_PHASES = (
    "one-token-smoke",
    "short-generation",
    "context-4096",
    "context-8192",
)


def register(commands: Any) -> None:
    """Add Track 8B subcommands."""
    for name in VALIDATION:
        commands.add_parser(name)
    preflight = commands.add_parser("measurement-preflight")
    _roots(preflight, approval=False)
    for name in (
        "measurement-execute",
        "measurement-smoke",
        "measurement-short-generation",
        "measurement-corpus",
    ):
        _roots(commands.add_parser(name), approval=True)
    context = commands.add_parser("measurement-context")
    _roots(context, approval=True)
    context.add_argument("--tokens", required=True, choices=("4096", "8192"))


def handle(command: str, args: argparse.Namespace) -> dict[str, Any]:
    """Run one Track 8B command and return a path-free summary."""
    if command == "measurement-plan-validation":
        plan = load_measurement_plan()
        return _ok(planDigest=plan["planDigest"], executionStatus=plan["executionStatus"])
    if command == "measurement-operator-approval-validation":
        approval = load_operator_approval()
        return _ok(approvalStatus=approval["approvalStatus"], planDigest=approval["planDigest"])
    if command == "smoke-execution-validation":
        document = build_smoke_template()
        validate("smoke-execution", document)
        return _ok(phase=document["phase"], realModelExecuted=False)
    if command == "context-memory-measurement-validation":
        document = build_context_template()
        validate("context-memory-measurement", document)
        return _ok(phase=document["phase"], realModelExecuted=False)
    if command == "candidate-behavioral-run-validation":
        document = build_run_template()
        validate("candidate-behavioral-run", document)
        return _ok(exitClassification=document["exitClassification"])
    if command == "candidate-behavioral-summary-validation":
        document = build_summary_template()
        validate("candidate-behavioral-summary", document)
        return _ok(comparisonWinner=document["comparisonWinner"])
    if command == "measurement-closeout-validation":
        document = load_closeout_template()
        observed = load_stopped_closeout()
        return _ok(
            closeoutState=document["closeoutState"],
            observedCloseoutState=observed["closeoutState"],
        )
    if command == "track8b-preflight-validation":
        document = load_preflight_template()
        return _ok(
            calibrationStatus=document["calibrationStatus"],
            measurementPerformed=document["measurementPerformed"],
            preflightStatus=document["status"],
            runInvoked=document["runInvoked"],
        )
    if command == "track8b-stopped-attempt-validation":
        document = load_stopped_attempt()
        return _ok(
            runInvoked=document["runInvoked"],
            sessionCreated=document["sessionCreated"],
            stopCause=document["stopCause"],
            track9Readiness=document["track9Readiness"],
        )
    if command == "track8b-plan-disposition-validation":
        document = load_plan_disposition()
        return _ok(
            planDisposition=document["planDisposition"],
            replacementPlanDigest=document["replacementPlanDigest"],
            reusable=document["reusable"],
        )
    if command == "track8b-template-compatibility-defect-validation":
        document = load_template_defect()
        return _ok(
            defectStatus=document["status"],
            failureBeforeSession=document["failureBeforeSession"],
            templateBytesChanged=document["templateBytesChanged"],
        )
    if command == "track8b-review-validation":
        document = load_track8b_review()
        return _ok(
            reviewDigest=document["reviewDigest"],
            reviewStatus=document["reviewStatus"],
            track9Readiness=document["track9Readiness"],
        )
    if command == "track9-readiness-validation":
        document = load_track9_readiness()
        return _ok(readinessOutcome=document["readinessOutcome"], verdict=document["verdict"])
    if command == "measurement-preflight":
        document = run_preflight(
            _path(args.runtime_cache), _path(args.model_cache), _path(args.result_root)
        )
        return _ok(
            archiveAttemptId=document["archiveAttemptId"],
            candidateAttemptId=document["candidateAttemptId"],
            candidateClass=document["candidateClass"],
            planDigest=document["planDigest"],
            runtimeAttemptId=document["runtimeAttemptId"],
            runtimeClass=document["runtimeClass"],
        )
    return _execute(command, args)


def _execute(command: str, args: argparse.Namespace) -> dict[str, Any]:
    runtime = _path(args.runtime_cache)
    model = _path(args.model_cache)
    result = _path(args.result_root)
    approval = str(args.operator_approval)
    if command == "measurement-execute":
        return _execute_all(approval, runtime, model, result)
    if command == "measurement-smoke":
        document = execute_phase(
            "one-token-smoke",
            approval=approval,
            runtime_root=runtime,
            model_root=model,
            result_root=result,
        )
        return _phase_summary(document)
    if command == "measurement-short-generation":
        document = execute_phase(
            "short-generation",
            approval=approval,
            runtime_root=runtime,
            model_root=model,
            result_root=result,
        )
        return _phase_summary(document)
    if command == "measurement-context":
        phase = "context-4096" if args.tokens == "4096" else "context-8192"
        document = execute_phase(
            phase,
            approval=approval,
            runtime_root=runtime,
            model_root=model,
            result_root=result,
        )
        return _phase_summary(document)
    if command == "measurement-corpus":
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
    if not (result / PHASE_FILES["preflight"]).is_file():
        run_preflight(runtime, model, result)
    stop: str | None = None
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
        try:
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
    _write(result, "closeout.json", closeout)
    _write(result, "track9-readiness.json", readiness)
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
    import json

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


def _write(root: Path, name: str, document: dict[str, Any]) -> None:
    from patchpilot_intelligence_evals.corpus import canonical_dumps

    destination = root / name
    if destination.exists():
        raise MeasurementError("overwrite")
    destination.write_text(canonical_dumps(document) + "\n", encoding="utf-8")


def _ok(**fields: object) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "calibrationStatus": "not-approved",
        "productionReady": False,
        "selectionOutcome": "no-selection",
        "status": "ok",
    }
    payload.update(fields)
    return payload
