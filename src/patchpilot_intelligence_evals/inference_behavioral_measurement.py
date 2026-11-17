"""Conditional 24-case evaluation for the inference retry. Gold stays off the child."""

from __future__ import annotations

import hashlib
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
from patchpilot_intelligence_evals.corrected_candidate_inference import phase_limits
from patchpilot_intelligence_evals.evaluator import GATE_NAMES, repository_commit
from patchpilot_intelligence_evals.hardened_candidate_inference import launch_inference
from patchpilot_intelligence_evals.hardened_execution import execute_hardened
from patchpilot_intelligence_evals.inference_context_measurement import read_verified_header
from patchpilot_intelligence_evals.inference_retry_plan import (
    load_inference_plan,
    phase_by_name,
    require_inference_retry_approval,
    session_stop,
)
from patchpilot_intelligence_evals.inference_retry_preflight import (
    PHASE_FILES,
    load_phase,
    require_prior,
    utc_timestamp,
    write_new,
)
from patchpilot_intelligence_evals.measurement_plan import (
    CANDIDATE_ATTEMPT,
    HARNESS_CANDIDATE_ID,
    PROTOCOL_CANDIDATE_VERSION,
    RUNTIME_ATTEMPT,
    MeasurementError,
    digest_document,
    prompt_template,
)
from patchpilot_intelligence_evals.metrics import (
    METRIC_NAMES,
    add_metrics,
    gate_from_metric,
    measure,
    score_case,
)
from patchpilot_intelligence_evals.protocol import build_request
from patchpilot_intelligence_evals.result_store import ResultStoreError, write_canonical
from patchpilot_intelligence_evals.schemas import SchemaValidationError, repo_root

_RUN = Path("candidates/templates/inference-retry-behavioral-run-template.json")
_SUMMARY = Path("candidates/templates/inference-retry-behavioral-summary-template.json")


def build_run_template() -> dict[str, Any]:
    """Committed per-run record. It has not been executed."""
    plan = load_inference_plan()
    return digest_document(
        _run_body(plan, executed=False),
        "inference-retry-behavioral-run",
        "identityDigest",
    )


def build_summary_template() -> dict[str, Any]:
    """Committed summary. Comparison has no winner and calibration stays unapproved."""
    plan = load_inference_plan()
    return digest_document(
        _summary_body(plan, [], [], [], executed=False, completed=False),
        "inference-retry-behavioral-run",
        "identityDigest",
    )


def load_run_template() -> dict[str, Any]:
    """Load the committed run template and require it to match the builder."""
    return _load(_RUN, build_run_template)


def load_summary_template() -> dict[str, Any]:
    """Load the committed summary and require it to match the builder."""
    return _load(_SUMMARY, build_summary_template)


def seal_launch(root: Path, relative: str, record: dict[str, Any], schema_name: str) -> None:
    """Seal one run record. Failure leaves the caller holding the child output."""
    write_canonical(relative, record, schema_name=schema_name, root=root)


def preserve_unsealed_launch(
    *,
    root: Path,
    plan: dict[str, Any],
    case_id: str,
    repetition: int,
    stdout: bytes,
    executed: bool,
    run_invoked: bool,
    session_created: bool,
) -> None:
    """Persist an output digest when the run record cannot be sealed."""
    if not stdout:
        raise MeasurementError("missing-output")
    document = digest_document(
        _authority_body(
            plan,
            executed=executed,
            completed=False,
            run_invoked=run_invoked,
            session_created=session_created,
            real_model_executed=False,
            result_root=root,
        )
        | {
            "caseId": case_id,
            "outputByteCount": len(stdout),
            "outputDigest": hashlib.sha256(stdout).hexdigest(),
            "reason": "run-record-unsealable",
            "recordKind": "unclassified-launch",
            "repetition": repetition,
        },
        "inference-retry-unclassified-launch",
        "identityDigest",
    )
    (root / "runs").mkdir(parents=True, exist_ok=True)
    write_new(root, f"runs/{case_id}-r{repetition}-unclassified.json", document)


def record_sealed_or_orphan(
    *,
    root: Path,
    relative: str,
    record: dict[str, Any],
    schema_name: str,
    stdout: bytes,
    plan: dict[str, Any],
    case_id: str,
    repetition: int,
    executed: bool,
    run_invoked: bool,
    session_created: bool,
) -> str:
    """Seal a run, or retain an unclassified record when child output exists."""
    try:
        seal_launch(root, relative, record, schema_name)
    except (MeasurementError, ResultStoreError, SchemaValidationError, OSError):
        if not stdout:
            raise
        preserve_unsealed_launch(
            root=root,
            plan=plan,
            case_id=case_id,
            repetition=repetition,
            stdout=stdout,
            executed=executed,
            run_invoked=run_invoked,
            session_created=session_created,
        )
        return "unclassified"
    return "sealed"


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
    plan = require_inference_retry_approval(approval)
    require_prior(result_root, "corpus-evaluation")
    _require_contexts(result_root)
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
            classified, run_invoked, session_created = launch_inference(
                config,
                approval=approval,
                runtime_dir=runtime_dir,
                model_dir=model_dir,
                result_root=result_root,
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
            try:
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
                    result_root,
                )
            except (MeasurementError, ResultStoreError, SchemaValidationError, OSError):
                if not stdout:
                    raise
                preserve_unsealed_launch(
                    root=result_root,
                    plan=plan,
                    case_id=case_id,
                    repetition=repetition,
                    stdout=stdout,
                    executed=executed,
                    run_invoked=run_invoked,
                    session_created=session_created,
                )
                stop = "unclassified-launch"
                break
            sealed_as = record_sealed_or_orphan(
                root=result_root,
                relative=f"runs/{case_id}-r{repetition}.json",
                record=record,
                schema_name="inference-retry-behavioral-run",
                stdout=stdout,
                plan=plan,
                case_id=case_id,
                repetition=repetition,
                executed=executed,
                run_invoked=run_invoked,
                session_created=session_created,
            )
            if sealed_as == "unclassified":
                stop = "unclassified-launch"
                break
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
        result_root=result_root,
    )
    sealed = digest_document(summary, "inference-retry-behavioral-run", "identityDigest")
    write_new(result_root, PHASE_FILES["corpus-evaluation"], sealed)
    if stop is not None:
        raise MeasurementError(stop)
    return sealed


def record_corpus_stop(result_root: Path, stop: str) -> dict[str, Any]:
    """Seal an incomplete corpus. This does not launch another child."""
    plan = load_inference_plan()
    body = _summary_body(
        plan,
        [],
        [],
        [],
        executed=True,
        completed=False,
        result_root=result_root,
    )
    body["stopCause"] = stop
    sealed = digest_document(body, "inference-retry-behavioral-run", "identityDigest")
    write_new(result_root, PHASE_FILES["corpus-evaluation"], sealed)
    return sealed


def _require_contexts(result_root: Path) -> None:
    for phase_name in ("context-4096", "context-8192"):
        document = load_phase(result_root, phase_name)
        if document.get("exitClassification") != "success" or document.get("stopCause") is not None:
            raise MeasurementError("prior-phase-failed")


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


def _links(plan: dict[str, Any], result_root: Path | None) -> dict[str, str]:
    digest = "not-executed"
    if result_root is not None:
        document = load_phase(result_root, "dynamic-link-precheck")
        value = document.get("identityDigest")
        if not isinstance(value, str):
            raise MeasurementError("precheck-failed")
        digest = value
    return {
        "consumedRetryPlanDigest": plan["consumedRetryPlanDigest"],
        "dependencyClosureDigest": plan["dependencyClosureDigest"],
        "dynamicLinkPrecheckDigest": digest,
    }


def _run_body(plan: dict[str, Any], *, executed: bool) -> dict[str, Any]:
    return _authority_body(plan, executed=executed, completed=False, result_root=None) | {
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
    result_root: Path,
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
            result_root=result_root,
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
        "inference-retry-behavioral-run",
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
    result_root: Path | None = None,
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
    return _authority_body(
        plan,
        executed=executed,
        completed=completed,
        run_invoked=executed,
        session_created=executed,
        real_model_executed=executed,
        result_root=result_root,
    ) | {
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
    result_root: Path | None,
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
        **_links(plan, result_root),
    }


def _load(relative: Path, builder: Any) -> dict[str, Any]:
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != builder():
        raise MeasurementError("record-drift")
    return loaded
