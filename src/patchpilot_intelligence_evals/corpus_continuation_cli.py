"""Track 9A commands. Validators read committed records. Execute stays outside CI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.bounded_raw_output import load_raw_template
from patchpilot_intelligence_evals.corpus_continuation import (
    execute_continuation,
    load_diagnostic_template,
    load_run_template,
    load_summary_template,
)
from patchpilot_intelligence_evals.corpus_continuation_closeout import load_closeout_template
from patchpilot_intelligence_evals.corpus_continuation_plan import (
    FRESH_RESULT_ROOT,
    PLANNED_RUNS,
    load_corpus_approval,
    load_corpus_plan,
)
from patchpilot_intelligence_evals.corpus_continuation_preflight import (
    load_preflight_template,
    run_continuation_preflight,
)
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.track9a_records import (
    load_corrected_interpretation,
    load_plan_disposition,
    load_proportionality_review,
    load_schema_forensics,
    load_stopped_attempt,
    load_telemetry_defect,
    load_track9a_review,
    load_track10_not_ready,
)
from patchpilot_intelligence_evals.track10_readiness import load_track10_template

VALIDATION = (
    "corpus-continuation-plan-validation",
    "corpus-continuation-approval-validation",
    "corpus-continuation-preflight-validation",
    "bounded-raw-output-validation",
    "run-diagnostics-validation",
    "corpus-continuation-run-validation",
    "corpus-continuation-summary-validation",
    "corpus-continuation-closeout-validation",
    "track10-readiness-validation",
    "track9a-stopped-attempt-validation",
    "track9a-telemetry-finalization-defect-validation",
    "track9a-schema-forensics-validation",
    "track9a-corrected-interpretation-validation",
    "track9a-plan-disposition-validation",
    "track9a-proportionality-review-validation",
    "track9a-track10-not-ready-validation",
    "track9a-implementation-review-validation",
)
EXECUTE = frozenset({"corpus-continuation-execute", "corpus-continuation-preflight"})


def register(commands: Any) -> None:
    """Add Track 9A validators and the manual corpus commands."""
    for name in VALIDATION:
        commands.add_parser(name)
    preflight = commands.add_parser("corpus-continuation-preflight")
    _roots(preflight, approval=False)
    execute = commands.add_parser("corpus-continuation-execute")
    _roots(execute, approval=True)


def handle(command: str, args: argparse.Namespace) -> dict[str, Any]:
    """Validate one committed record or run one manual command."""
    if command == "corpus-continuation-plan-validation":
        plan = load_corpus_plan()
        return _ok(
            executionStatus=plan["executionStatus"],
            planDigest=plan["planDigest"],
            plannedRuns=plan["plannedRuns"],
            runInvoked=plan["runInvoked"],
        )
    if command == "corpus-continuation-approval-validation":
        approval = load_corpus_approval()
        return _ok(approvalStatus=approval["approvalStatus"], planDigest=approval["planDigest"])
    if command == "corpus-continuation-preflight-validation":
        document = load_preflight_template()
        return _ok(
            modelSessionCreated=document["modelSessionCreated"],
            preflightStatus=document["preflightStatus"],
            runInvoked=document["runInvoked"],
        )
    if command == "bounded-raw-output-validation":
        document = load_raw_template()
        return _ok(recordKind=document["recordKind"], retentionStatus=document["retentionStatus"])
    if command == "run-diagnostics-validation":
        document = load_diagnostic_template()
        return _ok(parseStatus=document["parseStatus"], schemaStatus=document["schemaStatus"])
    if command == "corpus-continuation-run-validation":
        document = load_run_template()
        return _ok(
            exitClassification=document["exitClassification"], runInvoked=document["runInvoked"]
        )
    if command == "corpus-continuation-summary-validation":
        document = load_summary_template()
        return _ok(
            comparisonWinner=document["comparisonWinner"],
            completeness=document["completeness"],
            plannedRuns=document["plannedRuns"],
        )
    if command == "corpus-continuation-closeout-validation":
        document = load_closeout_template()
        return _ok(blocker=document["blocker"], closeoutState=document["closeoutState"])
    if command == "track10-readiness-validation":
        document = load_track10_template()
        return _ok(readinessOutcome=document["readinessOutcome"], verdict=document["verdict"])
    if command == "track9a-stopped-attempt-validation":
        document = load_stopped_attempt()
        return _ok(
            attemptOutcome=document["attemptOutcome"],
            completedRuns=document["completedRuns"],
            missingRuns=document["missingRuns"],
            stopCause=document["stopCause"],
        )
    if command == "track9a-telemetry-finalization-defect-validation":
        document = load_telemetry_defect()
        return _ok(correctedDisposition=document["correctedDisposition"], defect=document["defect"])
    if command == "track9a-schema-forensics-validation":
        document = load_schema_forensics()
        return _ok(
            executionStopAuthority=document["executionStopAuthority"],
            responseFailureAuthority=document["responseFailureAuthority"],
        )
    if command == "track9a-corrected-interpretation-validation":
        document = load_corrected_interpretation()
        return _ok(
            behavioralConclusion=document["behavioralConclusion"],
            candidateMetricsProduced=document["candidateMetricsProduced"],
        )
    if command == "track9a-plan-disposition-validation":
        document = load_plan_disposition()
        return _ok(
            planDisposition=document["planDisposition"],
            replacementPlanDigest=document["replacementPlanDigest"],
            reusable=document["reusable"],
        )
    if command == "track9a-proportionality-review-validation":
        document = load_proportionality_review()
        return _ok(
            authorizesAnotherRun=document["authorizesAnotherRun"],
            proportionalityRecommendation=document["proportionalityRecommendation"],
        )
    if command == "track9a-track10-not-ready-validation":
        document = load_track10_not_ready()
        return _ok(readinessOutcome=document["readinessOutcome"], verdict=document["verdict"])
    if command == "track9a-implementation-review-validation":
        document = load_track9a_review()
        return _ok(
            planDisposition=document["planDisposition"], reviewStatus=document["reviewStatus"]
        )
    if command == "corpus-continuation-preflight":
        return _preflight(args)
    if command == "corpus-continuation-execute":
        return _execute(args)
    raise KeyError(command)


def _preflight(args: argparse.Namespace) -> dict[str, Any]:
    root = _root(args.result_root)
    document = run_continuation_preflight(
        Path(args.runtime_cache),
        Path(args.model_cache),
        root,
        bind=True,
    )
    return _ok(
        dynamicLinkStatus=document["dynamicLinkStatus"],
        modelSessionCreated=document["modelSessionCreated"],
        planDigest=document["planDigest"],
        preflightStatus=document["preflightStatus"],
        runInvoked=document["runInvoked"],
        templateStatus=document["templateStatus"],
    )


def _execute(args: argparse.Namespace) -> dict[str, Any]:
    root = _root(args.result_root)
    summary = execute_continuation(
        approval=str(args.operator_approval),
        runtime_root=Path(args.runtime_cache),
        model_root=Path(args.model_cache),
        result_root=root,
        bind=True,
        executed=True,
    )
    ready = json.loads((root / "track10-readiness.json").read_text(encoding="utf-8"))
    status = "ok" if summary["completeness"] == "complete" else "stopped"
    return _ok(
        calibrationStatus=summary["calibrationStatus"],
        comparisonWinner=summary["comparisonWinner"],
        completeness=summary["completeness"],
        completedRuns=summary["completedRuns"],
        missingRuns=summary["missingRuns"],
        planDigest=summary["planDigest"],
        plannedRuns=PLANNED_RUNS,
        readinessOutcome=ready["readinessOutcome"],
        status=status,
        stopCause=ready["stopCause"],
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
