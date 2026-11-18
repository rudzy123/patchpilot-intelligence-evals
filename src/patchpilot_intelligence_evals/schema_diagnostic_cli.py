"""Track 10A commands. Validators read committed records. Execute stays outside CI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.diagnostic_case_selection import PLANNED_RUNS
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schema_diagnostic_closeout import load_closeout_template
from patchpilot_intelligence_evals.schema_diagnostic_execution import (
    execute_diagnostic,
    load_run_template,
)
from patchpilot_intelligence_evals.schema_diagnostic_plan import (
    FRESH_RESULT_ROOT,
    diagnostic_rejections,
    load_schema_diagnostic_approval,
    load_schema_diagnostic_plan,
    prepare_diagnostic_root,
)
from patchpilot_intelligence_evals.schema_diagnostic_preflight import (
    load_preflight_template,
    run_schema_diagnostic_preflight,
)
from patchpilot_intelligence_evals.schema_diagnostic_summary import load_summary_template
from patchpilot_intelligence_evals.track10a_implementation_review import (
    load_track10a_implementation_review,
)
from patchpilot_intelligence_evals.track11_readiness import load_track11_template

VALIDATION = (
    "schema-diagnostic-plan-validation",
    "schema-diagnostic-approval-validation",
    "schema-diagnostic-preflight-validation",
    "schema-diagnostic-run-validation",
    "schema-diagnostic-summary-validation",
    "schema-diagnostic-closeout-validation",
    "track11-readiness-validation",
    "track10a-implementation-review-validation",
)
EXECUTE = frozenset({"schema-diagnostic-execute", "schema-diagnostic-preflight"})


def register(commands: Any) -> None:
    """Add Track 10A validators and the manual diagnostic commands."""
    for name in VALIDATION:
        commands.add_parser(name)
    preflight = commands.add_parser("schema-diagnostic-preflight")
    _roots(preflight, approval=False)
    execute = commands.add_parser("schema-diagnostic-execute")
    _roots(execute, approval=True)


def handle(command: str, args: argparse.Namespace) -> dict[str, Any]:
    """Validate one committed record or run one manual command."""
    if command == "schema-diagnostic-plan-validation":
        plan = load_schema_diagnostic_plan()
        return _ok(
            executionStatus=plan["executionStatus"],
            planDigest=plan["planDigest"],
            plannedRuns=plan["plannedRuns"],
            runInvoked=plan["runInvoked"],
        )
    if command == "schema-diagnostic-approval-validation":
        approval = load_schema_diagnostic_approval()
        return _ok(approvalStatus=approval["approvalStatus"], planDigest=approval["planDigest"])
    if command == "schema-diagnostic-preflight-validation":
        document = load_preflight_template()
        return _ok(
            modelSessionCreated=document["modelSessionCreated"],
            preflightStatus=document["preflightStatus"],
            runInvoked=document["runInvoked"],
        )
    if command == "schema-diagnostic-run-validation":
        document = load_run_template()
        return _ok(
            exitClassification=document["exitClassification"], runInvoked=document["runInvoked"]
        )
    if command == "schema-diagnostic-summary-validation":
        document = load_summary_template()
        return _ok(
            diagnosticConclusion=document["diagnosticConclusion"],
            plannedRuns=document["plannedRuns"],
            thresholdMet=document["thresholdMet"],
        )
    if command == "schema-diagnostic-closeout-validation":
        document = load_closeout_template()
        return _ok(blocker=document["blocker"], closeoutState=document["closeoutState"])
    if command == "track11-readiness-validation":
        document = load_track11_template()
        return _ok(readinessOutcome=document["readinessOutcome"], verdict=document["verdict"])
    if command == "track10a-implementation-review-validation":
        document = load_track10a_implementation_review()
        return _ok(
            diagnosticConclusion=document["diagnosticConclusion"],
            realModelExecuted=document["realModelExecuted"],
            reviewDigest=document["reviewDigest"],
            reviewStatus=document["reviewStatus"],
        )
    if command == "schema-diagnostic-preflight":
        return _preflight(args)
    if command == "schema-diagnostic-execute":
        return _execute(args)
    raise KeyError(command)


def _preflight(args: argparse.Namespace) -> dict[str, Any]:
    root = prepare_diagnostic_root(_root(args.result_root))
    document = run_schema_diagnostic_preflight(
        Path(args.runtime_cache),
        Path(args.model_cache),
        root,
        bind=True,
    )
    rejections = diagnostic_rejections()
    return _ok(
        dynamicLinkStatus=document["dynamicLinkStatus"],
        historicalPlanRejections=len(rejections),
        modelSessionCreated=document["modelSessionCreated"],
        planDigest=document["planDigest"],
        preflightStatus=document["preflightStatus"],
        runInvoked=document["runInvoked"],
        templateStatus=document["templateStatus"],
    )


def _execute(args: argparse.Namespace) -> dict[str, Any]:
    root = _root(args.result_root)
    summary = execute_diagnostic(
        approval=str(args.operator_approval),
        runtime_root=Path(args.runtime_cache),
        model_root=Path(args.model_cache),
        result_root=root,
        bind=True,
        executed=True,
    )
    ready = json.loads((root / "track11-readiness.json").read_text(encoding="utf-8"))
    status = "ok" if summary["diagnosticConclusion"].endswith("established") else "stopped"
    if summary["diagnosticConclusion"] == "systematic-schema-failure-not-established":
        status = "ok"
    return _ok(
        calibrationStatus=summary["calibrationStatus"],
        candidateOutputSchemaFailureCount=summary["candidateOutputSchemaFailureCount"],
        comparisonWinner=summary["comparisonWinner"],
        completedRuns=summary["completedRuns"],
        diagnosticConclusion=summary["diagnosticConclusion"],
        distinctCategoryCount=summary["distinctCategoryCount"],
        missingRuns=summary["missingRuns"],
        planDigest=summary["planDigest"],
        plannedRuns=PLANNED_RUNS,
        readinessOutcome=ready["readinessOutcome"],
        status=status,
        stopCause=ready["stopCause"],
        thresholdMet=summary["thresholdMet"],
        verdict=ready["verdict"],
    )


def _root(value: str) -> Path:
    path = Path(value)
    if path != FRESH_RESULT_ROOT:
        raise MeasurementError("result-root-reuse")
    return path


def _roots(parser: argparse.ArgumentParser, *, approval: bool) -> None:
    parser.add_argument("--runtime-cache", required=True)
    parser.add_argument("--model-cache", required=True)
    parser.add_argument("--result-root", required=True)
    if approval:
        parser.add_argument("--operator-approval", required=True)


def _ok(**fields: object) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "calibrationStatus": "not-approved",
        "comparisonWinner": None,
        "productionReady": False,
        "selectionOutcome": "no-selection",
        "status": "ok",
    }
    payload.update(fields)
    return payload
