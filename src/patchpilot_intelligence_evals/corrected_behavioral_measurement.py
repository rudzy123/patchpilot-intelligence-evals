"""Conditional 24-case evaluation. Gold stays off the child."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.behavioral_measurement import (
    _CONTINUE,
    _capability_rows,
    _protocol_outcome,
)
from patchpilot_intelligence_evals.candidate_inference import (
    Launcher,
    assert_no_gold,
    child_indexes,
)
from patchpilot_intelligence_evals.comparison import compare_results
from patchpilot_intelligence_evals.corpus import (
    canonical_dumps,
    load_cases,
    sha256_text,
    to_candidate_input,
)
from patchpilot_intelligence_evals.corrected_candidate_inference import launch_retry, phase_limits
from patchpilot_intelligence_evals.evaluator import GATE_NAMES, repository_commit
from patchpilot_intelligence_evals.hardened_execution import execute_hardened
from patchpilot_intelligence_evals.measurement_plan import (
    CANDIDATE_ATTEMPT,
    HARNESS_CANDIDATE_ID,
    PROTOCOL_CANDIDATE_VERSION,
    RUNTIME_ATTEMPT,
    MeasurementError,
    digest_document,
    prompt_template,
    read_verified_header,
)
from patchpilot_intelligence_evals.measurement_retry_plan import (
    load_retry_plan,
    phase_by_name,
    require_retry_approval,
    session_stop,
)
from patchpilot_intelligence_evals.measurement_retry_preflight import (
    PHASE_FILES,
    require_prior,
    utc_timestamp,
    write_new,
)
from patchpilot_intelligence_evals.metrics import (
    METRIC_NAMES,
    add_metrics,
    gate_from_metric,
    measure,
    score_case,
)
from patchpilot_intelligence_evals.protocol import build_request
from patchpilot_intelligence_evals.result_store import write_canonical
from patchpilot_intelligence_evals.schemas import repo_root

_RUN = Path("candidates/templates/retry-behavioral-run-template.json")
_SUMMARY = Path("candidates/templates/retry-behavioral-summary-template.json")


def build_run_template() -> dict[str, Any]:
    """Committed per-run record. It has not been executed."""
    plan = load_retry_plan()
    return digest_document(
        _run_body(plan, executed=False), "retry-behavioral-run", "identityDigest"
    )


def build_summary_template() -> dict[str, Any]:
    """Committed summary. Comparison has no winner and calibration stays unapproved."""
    plan = load_retry_plan()
    return digest_document(
        _summary_body(plan, [], [], [], executed=False, completed=False),
        "retry-behavioral-run",
        "identityDigest",
    )


def load_run_template() -> dict[str, Any]:
    """Load the committed run template and require it to match the builder."""
    return _load(_RUN, build_run_template)


def load_summary_template() -> dict[str, Any]:
    """Load the committed summary template and require it to match the builder."""
    return _load(_SUMMARY, build_summary_template)


def execute_corpus(
    *,
    approval: str,
    runtime_root: Path,
    model_root: Path,
    result_root: Path,
    indexes: dict[str, int] | None = None,
    launcher: Launcher = execute_hardened,
    executed: bool = False,
    bind: bool = True,
) -> dict[str, Any]:
    """Run three repetitions per case after every memory phase passed."""
    plan = require_retry_approval(approval)
    require_prior(result_root, "corpus-evaluation")
    phase = phase_by_name(plan, "corpus-evaluation")
    if bind:
        from patchpilot_intelligence_evals.measurement_plan import bind_verified_roots

        bind_verified_roots(runtime_root, model_root)
    if indexes is not None:
        header_indexes = indexes
    elif bind:
        header_indexes = child_indexes(read_verified_header(runtime_root))
    else:
        raise MeasurementError("unverified-dependency")
    template = prompt_template()
    runtime_dir = runtime_root / "verified" / RUNTIME_ATTEMPT
    model_dir = model_root / "verified" / CANDIDATE_ATTEMPT
    blocks: list[dict[str, Any]] = []
    agreements: list[bool] = []
    missing_matches: list[bool] = []
    stop: str | None = None
    for case in load_cases():
        if stop is not None:
            break
        case_id = str(case["caseId"])
        request = build_request(case, plan["planDigest"])
        hidden = to_candidate_input(case)
        assert_no_gold(hidden)
        digests: list[str] = []
        first_output: dict[str, Any] | None = None
        first_ok = False
        for repetition in range(1, int(phase["repetitions"]) + 1):
            config = _config(plan, phase, header_indexes, template, request)
            classified, run_invoked, session_created = launch_retry(
                config,
                approval=approval,
                runtime_dir=runtime_dir,
                model_dir=model_dir,
                limits=phase_limits(phase),
                launcher=launcher,
                executed=executed,
            )
            stdout = classified.get("stdout", b"")
            if not isinstance(stdout, bytes):
                stdout = b""
            outcome, parsed = _protocol_outcome(classified, stdout, request)
            if outcome == "success" and parsed is not None:
                explanation = parsed["findingExplanationOutput"]
                digests.append(sha256_text(canonical_dumps(explanation)))
                if repetition == 1:
                    first_output = explanation
                    first_ok = True
            record = _run_record(
                plan,
                case_id,
                repetition,
                request,
                classified,
                outcome,
                executed,
                run_invoked,
                session_created,
            )
            write_canonical(
                f"runs/{case_id}-r{repetition}.json",
                record,
                schema_name="retry-behavioral-run",
                root=result_root,
            )
            if session_stop(outcome):
                stop = outcome
                break
            if outcome not in _CONTINUE and outcome != "success":
                stop = outcome
                break
        if stop is None and first_ok and first_output is not None:
            replay = len(digests) == int(phase["repetitions"]) and len(set(digests)) == 1
            agreements.append(replay)
            blocks.append(
                score_case(
                    case,
                    first_output,
                    schema_valid=True,
                    replay_match=replay,
                    log_text=f"case_id={case_id} metric=outputSchemaValidity status=pass",
                )
            )
            missing_matches.append(
                list(first_output.get("missingEvidence", [])) == list(case["missingEvidence"])
            )
        elif stop is None:
            blocks.append({name: measure(0, 0) for name in METRIC_NAMES})
    summary = _summary_body(
        plan,
        blocks,
        agreements,
        missing_matches,
        executed=executed,
        completed=stop is None,
    )
    sealed = digest_document(summary, "retry-behavioral-run", "identityDigest")
    write_new(result_root, PHASE_FILES["corpus-evaluation"], sealed)
    if stop is not None:
        raise MeasurementError(stop)
    return sealed


def _config(
    plan: dict[str, Any],
    phase: dict[str, Any],
    indexes: dict[str, int],
    template: str,
    request: dict[str, Any],
) -> dict[str, Any]:
    config = {
        "coldWarm": False,
        "eosTokenId": int(plan["eosTokenId"]),
        "generationBudgetSeconds": int(phase["generationBudgetSeconds"]),
        "harnessCandidateId": HARNESS_CANDIDATE_ID,
        "indexes": indexes,
        "inputTokenCount": None,
        "interOpThreads": int(plan["interOpThreads"]),
        "intraOpThreads": int(plan["intraOpThreads"]),
        "maxNewTokens": int(phase["maxNewTokens"]),
        "phase": "corpus-evaluation",
        "prompt": "",
        "promptConstruction": "protocol-request",
        "promptTemplate": template,
        "protocolCandidateVersion": PROTOCOL_CANDIDATE_VERSION,
        "repeatedTokenId": int(plan["repeatedTokenId"]),
        "request": request,
    }
    assert_no_gold(config)
    return config


def _run_body(plan: dict[str, Any], *, executed: bool) -> dict[str, Any]:
    return _authority_body(plan, executed=executed, completed=False) | {
        "caseId": "not-executed",
        "exitClassification": "not-executed",
        "networkResult": "not-performed",
        "outputDigest": None,
        "processCleanup": "not-performed",
        "recordKind": "run",
        "repetition": 0,
        "requestDigest": None,
        "stopCause": None,
    }


def _run_record(
    plan: dict[str, Any],
    case_id: str,
    repetition: int,
    request: dict[str, Any],
    classified: dict[str, Any],
    outcome: str,
    executed: bool,
    run_invoked: bool,
    session_created: bool,
) -> dict[str, Any]:
    success = outcome == "success"
    return digest_document(
        _authority_body(
            plan,
            executed=executed,
            completed=True,
            run_invoked=run_invoked,
            session_created=session_created,
            real_model_executed=executed and success and run_invoked,
        )
        | {
            "caseId": case_id,
            "exitClassification": outcome,
            "networkResult": classified["networkResult"],
            "outputDigest": classified["outputDigest"] if success else None,
            "processCleanup": classified["cleanup"],
            "recordKind": "run",
            "repetition": repetition,
            "requestDigest": sha256_text(canonical_dumps(request)),
            "stopCause": None if success else outcome,
        },
        "retry-behavioral-run",
        "identityDigest",
    )


def _summary_body(
    plan: dict[str, Any],
    blocks: list[dict[str, Any]],
    agreements: list[bool],
    missing_matches: list[bool],
    *,
    executed: bool,
    completed: bool,
) -> dict[str, Any]:
    combined = add_metrics(blocks) if blocks else {name: measure(0, 0) for name in METRIC_NAMES}
    gates = {name: gate_from_metric(name, combined[name]) for name in GATE_NAMES}
    comparison = compare_results(
        {
            "candidateId": HARNESS_CANDIDATE_ID,
            "candidateManifestDigest": plan["planDigest"],
            "candidateVersion": PROTOCOL_CANDIDATE_VERSION,
            "complete": completed,
            "corpusDigest": plan["corpusDigest"],
            "corpusVersion": "1.0.0",
            "experimentId": plan["planDigest"],
            "protocolVersion": "1.0.0",
        },
        None,
    )
    if comparison["winner"] is not None:
        raise MeasurementError("comparison")
    if not completed:
        agreement: str | None = "not-executed"
    elif not agreements:
        agreement = None
    elif all(agreements):
        agreement = "agree"
    else:
        agreement = "disagree"
    reached = completed and executed
    return _authority_body(plan, executed=executed and completed, completed=completed) | {
        "capabilities": _capability_rows(
            gates,
            {"missing": missing_matches},
            reached=reached,
            metrics=combined if reached else None,
        ),
        "comparisonStatus": "not-executed" if not completed else "missing-right",
        "comparisonWinner": None,
        "gates": [
            {
                "denominator": int(gates[name]["denominator"]),
                "kind": gates[name]["kind"],
                "name": name,
                "numerator": int(gates[name]["numerator"]),
                "status": gates[name]["status"],
            }
            for name in GATE_NAMES
        ]
        if completed
        else [],
        "gatesUnchanged": True,
        "metrics": [
            {
                "denominator": int(combined[name]["denominator"]),
                "name": name,
                "numerator": int(combined[name]["numerator"]),
                "status": combined[name]["status"],
            }
            for name in METRIC_NAMES
        ]
        if completed
        else [],
        "percentageGatesCalibrated": False,
        "recordKind": "summary",
        "ungatedCanonicalAgreement": agreement,
    }


def _authority_body(
    plan: dict[str, Any],
    *,
    executed: bool,
    completed: bool,
    run_invoked: bool = False,
    session_created: bool = False,
    real_model_executed: bool = False,
) -> dict[str, Any]:
    return {
        "calibrationStatus": "not-approved",
        "installationAuthorized": False,
        "measurementCompleted": executed and completed,
        "measurementPerformed": executed,
        "modelSessionCreated": executed and session_created,
        "planDigest": plan["planDigest"],
        "priorPlanDigest": plan["priorPlanDigest"],
        "productionReady": False,
        "realModelExecuted": real_model_executed,
        "repositoryCommit": repository_commit() if executed else "not-executed",
        "resultRootClass": plan["resultRootClass"],
        "runInvoked": executed and run_invoked,
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
        "sessionId": plan["sessionId"],
        "timestamp": utc_timestamp() if executed else "not-executed",
    }


def _load(relative: Path, builder: Any) -> dict[str, Any]:
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != builder():
        raise MeasurementError("record-drift")
    return loaded
