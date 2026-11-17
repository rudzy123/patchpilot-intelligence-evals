"""Track 8B-R2 commands. Validators read committed records. Execute stays outside CI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.dynamic_link_precheck import (
    load_precheck_template,
    run_dynamic_link_precheck,
)
from patchpilot_intelligence_evals.inference_behavioral_measurement import (
    build_run_template,
    build_summary_template,
    execute_corpus,
    load_run_template,
    load_summary_template,
    record_corpus_stop,
)
from patchpilot_intelligence_evals.inference_context_measurement import (
    build_context_template,
    build_smoke_template,
    execute_phase,
    load_context_template,
    load_smoke_template,
)
from patchpilot_intelligence_evals.inference_retry_closeout import (
    build_closeout,
    load_closeout_template,
)
from patchpilot_intelligence_evals.inference_retry_plan import (
    load_inference_approval,
    load_inference_plan,
    prepare_fresh_result_root,
    require_inference_retry_approval,
    validate_inference_result_root,
)
from patchpilot_intelligence_evals.inference_retry_preflight import (
    PHASE_FILES,
    load_compatibility_template,
    load_phase,
    load_preflight_template,
    passed,
    run_compatibility,
    run_preflight,
    write_new,
)
from patchpilot_intelligence_evals.inference_retry_track9 import load_track9_template, recommend
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.track8b_r2_records import (
    load_behavioral_interpretation,
    load_cgroup_defect,
    load_memory_conclusion,
    load_plan_disposition,
    load_proportionality_review,
    load_schema_forensics,
    load_stopped_attempt,
    load_stopped_track9,
    load_track8b_r2_review,
)

VALIDATION = (
    "inference-retry-plan-validation",
    "inference-retry-approval-validation",
    "inference-retry-preflight-validation",
    "dynamic-link-precheck-validation",
    "inference-retry-smoke-validation",
    "inference-retry-context-memory-validation",
    "inference-retry-behavioral-run-validation",
    "inference-retry-closeout-validation",
    "inference-retry-track9-readiness-validation",
    "track8b-r2-stopped-attempt-validation",
    "track8b-r2-cgroup-sampling-defect-validation",
    "track8b-r2-schema-forensics-validation",
    "track8b-r2-behavioral-interpretation-validation",
    "track8b-r2-memory-conclusion-validation",
    "track8b-r2-plan-disposition-validation",
    "track8b-r2-proportionality-review-validation",
    "track8b-r2-stopped-track9-validation",
    "track8b-r2-review-validation",
)
EXECUTE = frozenset(
    {
        "inference-retry-context",
        "inference-retry-corpus",
        "inference-retry-execute",
        "inference-retry-precheck",
        "inference-retry-preflight",
        "inference-retry-short-generation",
        "inference-retry-smoke",
    }
)
_PHASES = (
    "one-token-smoke",
    "short-generation",
    "context-4096",
    "context-8192",
)


def register(commands: Any) -> None:
    """Add Track 8B-R2 subcommands."""
    for name in VALIDATION:
        commands.add_parser(name)
    for name in ("inference-retry-preflight", "inference-retry-precheck"):
        _roots(commands.add_parser(name), approval=False)
    for name in (
        "inference-retry-execute",
        "inference-retry-smoke",
        "inference-retry-short-generation",
        "inference-retry-corpus",
    ):
        _roots(commands.add_parser(name), approval=True)
    context = commands.add_parser("inference-retry-context")
    _roots(context, approval=True)
    context.add_argument("--tokens", required=True, choices=("4096", "8192"))


def handle(command: str, args: argparse.Namespace) -> dict[str, Any]:
    """Run one inference-retry command and return a path-free summary."""
    if command == "inference-retry-plan-validation":
        plan = load_inference_plan()
        return _ok(
            executionStatus=plan["executionStatus"],
            planDigest=plan["planDigest"],
            priorPlanDigest=plan["priorPlanDigest"],
            consumedRetryPlanDigest=plan["consumedRetryPlanDigest"],
        )
    if command == "inference-retry-approval-validation":
        approval = load_inference_approval()
        return _ok(approvalStatus=approval["approvalStatus"], planDigest=approval["planDigest"])
    if command == "inference-retry-preflight-validation":
        document = load_preflight_template()
        compatibility = load_compatibility_template()
        return _ok(
            compatibility=compatibility["compatibility"],
            preflightStatus=document["status"],
            runInvoked=document["runInvoked"],
            sessionCreated=compatibility["sessionCreated"],
        )
    if command == "dynamic-link-precheck-validation":
        document = load_precheck_template()
        return _ok(
            createSessionCalled=document["createSessionCalled"],
            runInvoked=document["runInvoked"],
            status=document["status"],
        )
    if command == "inference-retry-smoke-validation":
        document = load_smoke_template()
        build_smoke_template()
        return _ok(phase=document["phase"], realModelExecuted=False)
    if command == "inference-retry-context-memory-validation":
        document = load_context_template()
        build_context_template()
        return _ok(phase=document["phase"], realModelExecuted=False)
    if command == "inference-retry-behavioral-run-validation":
        document = load_run_template()
        summary = load_summary_template()
        build_run_template()
        build_summary_template()
        return _ok(
            comparisonWinner=summary["comparisonWinner"],
            exitClassification=document["exitClassification"],
        )
    if command == "inference-retry-closeout-validation":
        document = load_closeout_template()
        return _ok(
            closeoutState=document["closeoutState"],
            furtherRetryAssumed=document["furtherRetryAssumed"],
            proportionalityRecommendation=document["proportionalityRecommendation"],
        )
    if command == "inference-retry-track9-readiness-validation":
        document = load_track9_template()
        return _ok(readinessOutcome=document["readinessOutcome"], verdict=document["verdict"])
    if command == "track8b-r2-stopped-attempt-validation":
        document = load_stopped_attempt()
        return _ok(attemptOutcome=document["attemptOutcome"], stopCause=document["stopCause"])
    if command == "track8b-r2-cgroup-sampling-defect-validation":
        document = load_cgroup_defect()
        return _ok(correctedDisposition=document["correctedDisposition"], defect=document["defect"])
    if command == "track8b-r2-schema-forensics-validation":
        document = load_schema_forensics()
        return _ok(
            failureAuthority=document["runs"][0]["failureAuthority"],
            unresolved=document["authorityCounts"]["unresolved"],
        )
    if command == "track8b-r2-behavioral-interpretation-validation":
        document = load_behavioral_interpretation()
        return _ok(
            behavioralConclusion=document["behavioralConclusion"],
            candidateMetricsProduced=document["candidateMetricsProduced"],
        )
    if command == "track8b-r2-memory-conclusion-validation":
        document = load_memory_conclusion()
        return _ok(
            memoryConclusion=document["memoryConclusion"],
            minimumHeadroomBytes=document["minimumHeadroomBytes"],
        )
    if command == "track8b-r2-plan-disposition-validation":
        document = load_plan_disposition()
        return _ok(
            planDisposition=document["planDisposition"],
            r3Plan=document["r3Plan"],
            reusable=document["reusable"],
        )
    if command == "track8b-r2-proportionality-review-validation":
        document = load_proportionality_review()
        return _ok(
            authorizesRetry=document["authorizesRetry"],
            proportionalityRecommendation=document["proportionalityRecommendation"],
        )
    if command == "track8b-r2-stopped-track9-validation":
        document = load_stopped_track9()
        return _ok(readinessOutcome=document["readinessOutcome"], verdict=document["verdict"])
    if command == "track8b-r2-review-validation":
        document = load_track8b_r2_review()
        return _ok(
            memoryConclusion=document["memoryConclusion"],
            reviewStatus=document["reviewStatus"],
        )
    if command == "inference-retry-preflight":
        result = _path(args.result_root)
        if not result.exists():
            prepare_fresh_result_root(result)
        document = run_preflight(_path(args.runtime_cache), _path(args.model_cache), result)
        return _ok(planDigest=document["planDigest"], runInvoked=document["runInvoked"])
    if command == "inference-retry-precheck":
        root = _path(args.result_root)
        try:
            document = run_dynamic_link_precheck(_path(args.runtime_cache), root)
        except MeasurementError as exc:
            return _stopped(root, exc.code)
        return _ok(
            createSessionCalled=document["createSessionCalled"],
            planDigest=document["planDigest"],
            precheckStatus=document["status"],
            runInvoked=document["runInvoked"],
        )
    return _execute(command, args)


def _execute(command: str, args: argparse.Namespace) -> dict[str, Any]:
    runtime = _path(args.runtime_cache)
    model = _path(args.model_cache)
    result = _path(args.result_root)
    approval = str(args.operator_approval)
    require_inference_retry_approval(approval)
    if command == "inference-retry-execute":
        return _execute_all(approval, runtime, model, result)
    if command == "inference-retry-smoke":
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
    if command == "inference-retry-short-generation":
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
    if command == "inference-retry-context":
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
    if command == "inference-retry-corpus":
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
    stop: str | None = None
    try:
        _ensure_preflight(runtime, model, result)
        if not (result / PHASE_FILES["dynamic-link-precheck"]).is_file():
            run_dynamic_link_precheck(runtime, result)
        for phase in _PHASES:
            if _already_passed(result, phase):
                continue
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
            if not _already_passed(result, "corpus-evaluation"):
                execute_corpus(
                    approval=approval,
                    runtime_root=runtime,
                    model_root=model,
                    result_root=result,
                    executed=True,
                )
    except MeasurementError as exc:
        stop = exc.code
    except OSError:
        stop = "telemetry-unresolved"
        corpus = result / PHASE_FILES["corpus-evaluation"]
        if not corpus.exists() and (result / "runs").is_dir():
            record_corpus_stop(result, stop)
    closeout, readiness = _close(result)
    status = (
        "ok"
        if stop is None and readiness and readiness["readinessOutcome"] != "blocked"
        else "stopped"
    )
    payload: dict[str, Any] = {
        "calibrationStatus": "not-approved",
        "productionReady": False,
        "selectionOutcome": "no-selection",
        "status": status,
        "stopCause": stop,
    }
    if closeout is not None and readiness is not None:
        payload["planDigest"] = closeout["planDigest"]
        payload["readinessOutcome"] = readiness["readinessOutcome"]
        payload["verdict"] = readiness["verdict"]
    return payload


def _ensure_preflight(runtime: Path, model: Path, result: Path) -> None:
    if not (result / PHASE_FILES["preflight"]).is_file():
        if not result.exists():
            prepare_fresh_result_root(result)
        run_preflight(runtime, model, result)
        return
    validate_inference_result_root(result, resume=True)
    if not (result / PHASE_FILES["template-compatibility"]).is_file():
        run_compatibility(model, result)


def _already_passed(result: Path, phase: str) -> bool:
    path = result / PHASE_FILES[phase]
    if not path.is_file() or path.is_symlink():
        return False
    document = load_phase(result, phase)
    return passed(phase, document)


def _close(result: Path) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not result.is_dir():
        return None, None
    try:
        populated = any(result.iterdir())
        validate_inference_result_root(result, resume=populated)
    except MeasurementError:
        return None, None
    closeout = build_closeout(result)
    summary = _optional_summary(result)
    readiness = recommend(closeout, summary)
    write_new(result, "closeout.json", closeout)
    write_new(result, "track9-readiness.json", readiness)
    return closeout, readiness


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


def _stopped(result: Path, stop: str) -> dict[str, Any]:
    closeout, readiness = _close(result)
    payload: dict[str, Any] = {
        "calibrationStatus": "not-approved",
        "productionReady": False,
        "selectionOutcome": "no-selection",
        "status": "stopped",
        "stopCause": stop,
    }
    if closeout is not None and readiness is not None:
        payload["planDigest"] = closeout["planDigest"]
        payload["proportionalityRecommendation"] = closeout["proportionalityRecommendation"]
        payload["readinessOutcome"] = readiness["readinessOutcome"]
        payload["verdict"] = readiness["verdict"]
    return payload


def _ok(**fields: object) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "calibrationStatus": "not-approved",
        "productionReady": False,
        "selectionOutcome": "no-selection",
        "status": "ok",
    }
    payload.update(fields)
    return payload
