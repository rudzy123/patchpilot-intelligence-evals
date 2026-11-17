"""Serial 24-case continuation. Synthetic tests pass a launcher double."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.behavioral_measurement import _capability_rows
from patchpilot_intelligence_evals.bounded_raw_output import retain_bounded_output
from patchpilot_intelligence_evals.candidate_inference import (
    Launcher,
    assert_no_gold,
    child_indexes,
    classify_execution,
    launch_child,
    measurement_limits,
)
from patchpilot_intelligence_evals.cgroup_memory import ScopeSampler
from patchpilot_intelligence_evals.comparison import compare_results
from patchpilot_intelligence_evals.corpus import (
    CASE_IDS,
    canonical_dumps,
    load_cases,
    sha256_text,
    to_candidate_input,
)
from patchpilot_intelligence_evals.corpus_continuation_plan import (
    CASE_COUNT,
    PLANNED_RUNS,
    PROFILE_ID,
    REPETITIONS,
    artifact_pins,
    continuation_stop,
    identity_fields,
    load_corpus_plan,
    measured_continue,
    prepare_continuation_root,
    require_corpus_approval,
    response_schema_digest,
)
from patchpilot_intelligence_evals.corpus_continuation_preflight import run_continuation_preflight
from patchpilot_intelligence_evals.evaluator import GATE_NAMES, repository_commit
from patchpilot_intelligence_evals.failure_attribution import attribute_failure
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult, execute_hardened
from patchpilot_intelligence_evals.measurement_plan import (
    CANDIDATE_ATTEMPT,
    CORPUS_DIGEST,
    HARNESS_CANDIDATE_ID,
    PROMPT_TEMPLATE_DIGEST,
    PROTOCOL_CANDIDATE_VERSION,
    RUNTIME_ATTEMPT,
    MeasurementError,
    digest_document,
    prompt_template,
    read_verified_header,
)
from patchpilot_intelligence_evals.measurement_retry_preflight import utc_timestamp
from patchpilot_intelligence_evals.metrics import (
    METRIC_NAMES,
    add_metrics,
    gate_from_metric,
    measure,
    score_case,
)
from patchpilot_intelligence_evals.output_extraction import extract_envelope
from patchpilot_intelligence_evals.protocol import (
    build_request,
    classify_response,
    parse_candidate_stdout,
)
from patchpilot_intelligence_evals.response_diagnostics import diagnose_response, generation_facts
from patchpilot_intelligence_evals.result_store import ResultStoreError, write_canonical
from patchpilot_intelligence_evals.schemas import SchemaValidationError, repo_root

_RUN_TEMPLATE = Path("candidates/templates/corpus-continuation-run-template.json")
_DIAGNOSTIC_TEMPLATE = Path("candidates/templates/run-diagnostics-template.json")
_SUMMARY_TEMPLATE = Path("candidates/templates/corpus-continuation-summary-template.json")


def build_run_template() -> dict[str, Any]:
    """Committed run record. It has not been executed."""
    plan = load_corpus_plan()
    return digest_document(
        _run_body(plan, executed=False), "corpus-continuation-run", "identityDigest"
    )


def load_run_template() -> dict[str, Any]:
    """Load the committed run template and require it to match the builder."""
    return _load(_RUN_TEMPLATE, build_run_template)


def build_diagnostic_template() -> dict[str, Any]:
    """Committed diagnostic record. No candidate output is included."""
    plan = load_corpus_plan()
    return digest_document(_diagnostic_body(plan), "run-diagnostics", "identityDigest")


def load_diagnostic_template() -> dict[str, Any]:
    """Load the committed diagnostic template and require it to match the builder."""
    return _load(_DIAGNOSTIC_TEMPLATE, build_diagnostic_template)


def build_summary_template() -> dict[str, Any]:
    """Committed summary. Metrics stay unmeasured until a sealed corpus exists."""
    plan = load_corpus_plan()
    empty = {name: measure(0, 0) for name in METRIC_NAMES}
    return digest_document(
        _summary_body(
            plan,
            metrics=empty,
            gates={name: gate_from_metric(name, empty[name]) for name in GATE_NAMES},
            capabilities=_empirical(_capability_rows({}, {}, reached=False, metrics=empty)),
            agreements=[],
            authorities=[],
            completed=0,
            missing=PLANNED_RUNS,
            completeness="not-executed",
            reached=False,
        ),
        "corpus-continuation-summary",
        "identityDigest",
    )


def load_summary_template() -> dict[str, Any]:
    """Load the committed summary template and require it to match the builder."""
    return _load(_SUMMARY_TEMPLATE, build_summary_template)


def execute_continuation(
    *,
    approval: str,
    runtime_root: Path,
    model_root: Path,
    result_root: Path,
    indexes: dict[str, int] | None = None,
    launcher: Launcher = execute_hardened,
    executed: bool = False,
    bind: bool = True,
    probe: Callable[[Path], str] | None = None,
) -> dict[str, Any]:
    """Run three sealed repetitions per case. There are zero retries."""
    plan = require_corpus_approval(approval)
    _require_identities(plan)
    root = prepare_continuation_root(result_root)
    if bind:
        from patchpilot_intelligence_evals.measurement_plan import bind_verified_roots

        bind_verified_roots(runtime_root, model_root)
        header_indexes = child_indexes(read_verified_header(runtime_root))
    elif indexes is None:
        raise MeasurementError("unverified-dependency")
    else:
        header_indexes = indexes
    preflight = run_continuation_preflight(
        runtime_root,
        model_root,
        root,
        bind=bind,
        probe=probe,
    )
    _write(root, "preflight.json", preflight, "corpus-continuation-preflight")
    if preflight["preflightStatus"] == "failed" or (
        bind and preflight["preflightStatus"] != "passed"
    ):
        cause = (
            "compatibility-failure"
            if preflight["templateStatus"] == "failed"
            else "precheck-failed"
        )
        return _finish(root, plan, [], [], [], 0, cause, executed, preflight=preflight)
    template = prompt_template()
    runtime_dir = runtime_root / "verified" / RUNTIME_ATTEMPT
    model_dir = model_root / "verified" / CANDIDATE_ATTEMPT
    blocks: list[dict[str, Any]] = []
    agreements: list[bool] = []
    missing_matches: list[bool] = []
    authorities: list[str | None] = []
    completed = 0
    stop: str | None = None
    loaded = {str(case["caseId"]): case for case in load_cases()}
    if set(loaded) != set(CASE_IDS) or len(loaded) != CASE_COUNT:
        raise MeasurementError("corpus-mismatch")
    for case_id in CASE_IDS:
        if stop is not None:
            break
        case = loaded[case_id]
        request = build_request(case, plan["planDigest"])
        hidden = to_candidate_input(case)
        assert_no_gold(hidden)
        digests: list[str] = []
        first_output: dict[str, Any] | None = None
        first_ok = False
        for repetition in range(1, REPETITIONS + 1):
            if stop is not None:
                break
            config = _config(plan, header_indexes, template, request)
            try:
                result, sampler = launch_child(
                    config,
                    runtime_dir=runtime_dir,
                    model_dir=model_dir,
                    limits=measurement_limits(plan),
                    launcher=launcher,
                    continuation_approval=approval if launcher is execute_hardened else None,
                )
            except MeasurementError as exc:
                stop = str(exc)
                break
            try:
                sealed, outcome, parsed = _seal_one(
                    root=root,
                    plan=plan,
                    case=case,
                    case_id=case_id,
                    repetition=repetition,
                    request=request,
                    result=result,
                    sampler=sampler,
                    executed=executed,
                )
            except MeasurementError as exc:
                if exc.code == "unclassified-launch":
                    authorities.append("measurement-infrastructure")
                    completed += 1
                    stop = "unclassified-launch"
                    break
                if continuation_stop(exc.code):
                    stop = exc.code
                    break
                raise
            authorities.append(sealed["failureAuthority"])
            completed += 1
            if outcome == "success" and parsed is not None:
                explanation = parsed["findingExplanationOutput"]
                digests.append(sha256_text(canonical_dumps(explanation)))
                if repetition == 1:
                    first_output = explanation
                    first_ok = True
            if continuation_stop(outcome):
                stop = outcome
                break
            if not measured_continue(outcome):
                stop = outcome
                break
        if stop is None and first_ok and first_output is not None:
            replay = len(digests) == REPETITIONS and len(set(digests)) == 1
            agreements.append(replay)
            blocks.append(
                score_case(
                    case,
                    first_output,
                    schema_valid=True,
                    replay_match=replay,
                    log_text=f"case_id={case_id}",
                )
            )
            missing_matches.append(
                list(first_output.get("missingEvidence", [])) == list(case["missingEvidence"])
            )
        elif stop is None:
            blocks.append({name: measure(0, 0) for name in METRIC_NAMES})
    return _finish(
        root,
        plan,
        blocks,
        agreements,
        authorities,
        completed,
        stop,
        executed,
        missing_matches,
        preflight,
    )


def _seal_one(
    *,
    root: Path,
    plan: dict[str, Any],
    case: dict[str, Any],
    case_id: str,
    repetition: int,
    request: dict[str, Any],
    result: ExecutionResult,
    sampler: ScopeSampler,
    executed: bool,
) -> tuple[dict[str, Any], str, dict[str, Any] | None]:
    classified = classify_execution(result, sampler, cold_warm=False)
    if getattr(sampler, "blocked_classification", None) == "infrastructure-failure":
        classified["exitClassification"] = "isolation-failure"
    stdout = result.stdout
    limit = _limit_status(result.exit_classification)
    run_id = f"{case_id}-r{repetition}"
    raw = retain_bounded_output(
        root,
        case_id=case_id,
        repetition=repetition,
        run_id=run_id,
        stdout=stdout,
        stderr=result.stderr,
        limit_status=limit,
    )
    try:
        extraction = extract_envelope(stdout)
        side = generation_facts(result.generation_diagnostic)
        diagnosed = diagnose_response(extraction, side)
        outcome, parsed = _outcome(classified, stdout, request)
        merged = {**diagnosed, "extractionStatus": extraction["extractionStatus"]}
        authority = attribute_failure(outcome, raw, merged)
        diagnostic = digest_document(
            _diagnostic_body(
                plan,
                case_id=case_id,
                repetition=repetition,
                run_id=run_id,
                extraction=extraction,
                diagnosed=diagnosed,
                authority=authority,
                raw=raw,
            ),
            "run-diagnostics",
            "identityDigest",
        )
        record = digest_document(
            _run_body(
                plan,
                executed=executed,
                case_id=case_id,
                repetition=repetition,
                run_id=run_id,
                request=request,
                raw=raw,
                diagnostic=diagnostic,
                classified=classified,
                sampler=sampler,
                outcome=outcome,
                authority=authority,
                success=outcome == "success",
            ),
            "corpus-continuation-run",
            "identityDigest",
        )
    except (MeasurementError, ResultStoreError, SchemaValidationError, OSError):
        if not stdout:
            raise
        _write_unclassified(root, plan, case_id, repetition, executed)
        raise MeasurementError("unclassified-launch") from None
    _write_extracted(root, run_id, extraction)
    _write(root, f"runs/{run_id}/diagnostics.json", diagnostic, "run-diagnostics")
    _write(root, f"runs/{run_id}/run.json", record, "corpus-continuation-run")
    del case
    return record, outcome, parsed


def _finish(
    root: Path,
    plan: dict[str, Any],
    blocks: list[dict[str, Any]],
    agreements: list[bool],
    authorities: list[str | None],
    completed: int,
    stop: str | None,
    executed: bool,
    missing_matches: list[bool] | None = None,
    preflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from patchpilot_intelligence_evals.corpus_continuation_closeout import build_closeout
    from patchpilot_intelligence_evals.track10_readiness import recommend

    metrics = add_metrics(blocks) if blocks else {name: measure(0, 0) for name in METRIC_NAMES}
    gates = {name: gate_from_metric(name, metrics[name]) for name in GATE_NAMES}
    reached = stop is None and completed == PLANNED_RUNS
    capabilities = _empirical(
        _capability_rows(
            gates,
            {"missing": list(missing_matches or [])},
            reached=reached,
            metrics=metrics,
        )
    )
    summary = digest_document(
        _summary_body(
            plan,
            metrics=metrics,
            gates=gates,
            capabilities=capabilities,
            agreements=agreements,
            authorities=authorities,
            completed=completed,
            missing=PLANNED_RUNS - completed,
            completeness="complete" if reached else "incomplete",
            reached=reached,
            executed=executed,
        ),
        "corpus-continuation-summary",
        "identityDigest",
    )
    closeout = build_closeout(summary, stop, preflight)
    readiness = recommend(closeout, summary)
    _write(root, "summary.json", summary, "corpus-continuation-summary")
    _write(root, "closeout.json", closeout, "corpus-continuation-closeout")
    _write(root, "track10-readiness.json", readiness, "track10-readiness")
    return summary


def _require_identities(plan: dict[str, Any]) -> None:
    if plan["corpusDigest"] != CORPUS_DIGEST or len(plan["runs"]) != PLANNED_RUNS:
        raise MeasurementError("corpus-mismatch")
    if prompt_template() == "":
        raise MeasurementError("prompt-mismatch")
    if plan["promptTemplateDigest"] != PROMPT_TEMPLATE_DIGEST:
        raise MeasurementError("prompt-mismatch")
    if plan["responseSchema"]["digest"] != response_schema_digest():
        raise MeasurementError("response-schema-mismatch")
    if plan["caseCount"] != CASE_COUNT:
        raise MeasurementError("corpus-mismatch")


def _config(
    plan: dict[str, Any],
    indexes: dict[str, int],
    template: str,
    request: dict[str, Any],
) -> dict[str, Any]:
    config = {
        "coldWarm": False,
        "eosTokenId": int(plan["eosTokenId"]),
        "generationBudgetSeconds": int(plan["generationBudgetSeconds"]),
        "harnessCandidateId": HARNESS_CANDIDATE_ID,
        "indexes": indexes,
        "inputTokenCount": None,
        "interOpThreads": int(plan["interOpThreads"]),
        "intraOpThreads": int(plan["intraOpThreads"]),
        "maxNewTokens": int(plan["maxNewTokens"]),
        "phase": "corpus-evaluation",
        "prompt": "",
        "promptConstruction": "protocol-request",
        "promptTemplate": template,
        "protocolCandidateVersion": PROTOCOL_CANDIDATE_VERSION,
        "repeatedTokenId": 574,
        "request": request,
    }
    assert_no_gold(config)
    return config


def _outcome(
    classified: dict[str, Any],
    stdout: bytes,
    request: dict[str, Any],
) -> tuple[str, dict[str, Any] | None]:
    if classified["exitClassification"] != "success":
        return str(classified["exitClassification"]), None
    outcome, parsed = parse_candidate_stdout(stdout)
    if outcome != "parsed" or parsed is None:
        return "malformed-response", None
    status = classify_response(
        parsed,
        request_id_value=str(request["requestId"]),
        candidate_id=HARNESS_CANDIDATE_ID,
        candidate_version=PROTOCOL_CANDIDATE_VERSION,
    )
    if status == "success":
        return "success", parsed
    if status == "schema-invalid-output":
        return "schema-failure", parsed
    return "malformed-response", parsed


def _run_body(
    plan: dict[str, Any],
    *,
    executed: bool,
    case_id: str = "not-executed",
    repetition: int = 0,
    run_id: str = "not-executed",
    request: dict[str, Any] | None = None,
    raw: dict[str, Any] | None = None,
    diagnostic: dict[str, Any] | None = None,
    classified: dict[str, Any] | None = None,
    sampler: ScopeSampler | None = None,
    outcome: str = "not-executed",
    authority: str | None = None,
    success: bool = False,
    record_kind: str = "run",
    failure_evidence: str | None = None,
) -> dict[str, Any]:
    memory = {} if classified is None else classified["coldMemory"]
    timing = {} if classified is None else classified["coldTiming"]
    observed = executed and outcome != "not-executed"
    if failure_evidence is not None:
        evidence = failure_evidence
    elif diagnostic is None:
        evidence = "not-executed"
    else:
        evidence = str(diagnostic["failureEvidence"])
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        **_limits(plan),
        "caseId": case_id,
        "childState": _child_state(sampler, observed),
        "cleanupStatus": "not-performed" if classified is None else classified["cleanup"],
        "decoding": dict(plan["decoding"]),
        "exitClassification": outcome,
        "extractedDigest": None if diagnostic is None else diagnostic["extractedDigest"],
        "extractionStatus": "not-performed"
        if diagnostic is None
        else diagnostic["extractionStatus"],
        "failureAuthority": authority,
        "failureEvidence": evidence,
        "inputDigest": None if request is None else sha256_text(canonical_dumps(request)),
        "measurementCompleted": observed and success,
        "measurementPerformed": observed,
        "modelSessionCreated": observed,
        "networkResult": "not-performed" if classified is None else classified["networkResult"],
        "outputLimitStatus": "not-retained" if raw is None else raw["outputLimitStatus"],
        "parseStatus": "not-performed" if diagnostic is None else diagnostic["parseStatus"],
        "postExitScope": _post_exit(sampler),
        "processCleanup": "not-performed" if classified is None else classified["cleanup"],
        "profileId": PROFILE_ID,
        "realModelExecuted": executed and success,
        "recordKind": record_kind,
        "repetition": repetition,
        "repositoryCommit": "not-executed" if not observed else repository_commit(),
        "runId": run_id,
        "runInvoked": observed,
        "runtimeAttemptId": plan["runtimeAttemptId"],
        "schemaStatus": "not-performed" if diagnostic is None else diagnostic["schemaStatus"],
        "stderrBytes": 0 if raw is None else raw["stderrBytes"],
        "stderrDigest": None if raw is None else raw["stderrDigest"],
        "stdoutBytes": 0 if raw is None else raw["stdoutBytes"],
        "stdoutDigest": None if raw is None else raw["stdoutDigest"],
        "stopCause": None if outcome in {"success", "not-executed"} else outcome,
        "telemetryStatus": _telemetry(memory),
        "timestamp": "not-executed" if not observed else utc_timestamp(),
        "cgroupCurrentBytes": memory.get("cgroupCurrentBytes"),
        "cgroupPeakBytes": memory.get("cgroupPeakBytes"),
        "generationSeconds": timing.get("generationSeconds"),
        "loadSeconds": timing.get("loadSeconds"),
        "oomEvents": memory.get("oomEvents"),
        "processRssBytes": memory.get("processRssBytes"),
        "processTreeRssBytes": memory.get("processTreeRssBytes"),
        "virtualAddressBytes": memory.get("virtualAddressBytes"),
        "wallSeconds": timing.get("wallSeconds"),
    }


def _diagnostic_body(
    plan: dict[str, Any],
    *,
    case_id: str = "not-executed",
    repetition: int = 0,
    run_id: str = "not-executed",
    extraction: dict[str, Any] | None = None,
    diagnosed: dict[str, Any] | None = None,
    authority: str | None = None,
    raw: dict[str, Any] | None = None,
) -> dict[str, Any]:
    extracted = extraction or {
        "extractedBytes": 0,
        "extractedDigest": None,
        "extractionStatus": "not-performed",
    }
    facts = diagnosed or {
        "adapterFallback": False,
        "adapterTruncated": False,
        "evidenceIdFindings": [],
        "generationObserved": False,
        "missingRequired": [],
        "parseCategory": "not-performed",
        "parseColumn": None,
        "parseLine": None,
        "parsePosition": None,
        "parseStatus": "not-performed",
        "schemaStatus": "not-performed",
        "trailingBytes": 0,
        "unexpectedFields": [],
        "utf8": False,
    }
    evidence = "not-executed" if extraction is None else _evidence_code(authority, facts)
    limited = raw or {}
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        "adapterFallback": facts["adapterFallback"],
        "adapterTruncated": facts["adapterTruncated"],
        "caseId": case_id,
        "cleanupEvidence": "not-observed",
        "evidenceIdFindings": list(facts["evidenceIdFindings"]),
        "extractedBytes": extracted["extractedBytes"],
        "extractedDigest": extracted["extractedDigest"],
        "extractionStatus": extracted["extractionStatus"],
        "failureAuthority": authority,
        "failureEvidence": evidence,
        "generationObserved": facts["generationObserved"],
        "memoryEvidence": "not-observed",
        "missingRequired": list(facts["missingRequired"]),
        "outputLimitStatus": limited.get("outputLimitStatus", "not-retained"),
        "parseCategory": facts["parseCategory"],
        "parseColumn": facts["parseColumn"],
        "parseLine": facts["parseLine"],
        "parsePosition": facts["parsePosition"],
        "parseStatus": facts["parseStatus"],
        "recordKind": "diagnostics",
        "repetition": repetition,
        "runId": run_id,
        "schemaStatus": facts["schemaStatus"],
        "stderrTruncated": bool(limited.get("stderrTruncated", False)),
        "stdoutTruncated": bool(limited.get("stdoutTruncated", False)),
        "trailingBytes": facts["trailingBytes"],
        "unexpectedFields": list(facts["unexpectedFields"]),
        "utf8": facts["utf8"],
    }


def _summary_body(
    plan: dict[str, Any],
    *,
    metrics: dict[str, Any],
    gates: dict[str, Any],
    capabilities: list[dict[str, Any]],
    agreements: list[bool],
    authorities: list[str | None],
    completed: int,
    missing: int,
    completeness: str,
    reached: bool,
    executed: bool = False,
) -> dict[str, Any]:
    comparison = _comparison(plan, reached)
    if not agreements:
        consistency = "not-executed" if completeness == "not-executed" else "unmeasured"
    elif all(agreements):
        consistency = "consistent"
    else:
        consistency = "inconsistent"
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        "calibrationInterpretation": "not-approved",
        "capabilities": capabilities,
        "comparisonReason": comparison["reason"] if reached else "not-executed",
        "comparisonStatus": comparison["status"] if reached else "not-executed",
        "completeness": completeness,
        "completedRuns": completed,
        "failureAuthorityCounts": _authority_counts(authorities),
        "gates": [_gate_row(name, gates[name]) for name in GATE_NAMES],
        "gatesUnchanged": True,
        "measurementPerformed": executed and completed > 0,
        "metrics": [_metric_row(name, metrics[name]) for name in METRIC_NAMES],
        "missingRuns": missing,
        "percentageGatesCalibrated": False,
        "plannedRuns": PLANNED_RUNS,
        "realModelExecuted": executed and completed > 0,
        "recordKind": "summary",
        "repetitionConsistency": consistency,
        "runInvoked": executed and completed > 0,
    }


def _comparison(plan: dict[str, Any], reached: bool) -> dict[str, Any]:
    if not reached:
        return compare_results(None, None)
    manifest = json.loads((repo_root() / "corpus" / "manifest.json").read_text(encoding="utf-8"))
    left = {
        "candidateId": HARNESS_CANDIDATE_ID,
        "candidateManifestDigest": plan["planDigest"],
        "candidateVersion": PROTOCOL_CANDIDATE_VERSION,
        "corpusDigest": CORPUS_DIGEST,
        "corpusVersion": str(manifest["corpusVersion"]),
        "experimentId": plan["planDigest"],
        "protocolVersion": "1.0.0",
    }
    return compare_results(left, None)


def _limits(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "addressSpaceBytes": plan["addressSpaceBytes"],
        "cpuSeconds": plan["cpuSeconds"],
        "generationBudgetSeconds": plan["generationBudgetSeconds"],
        "maxNewTokens": plan["maxNewTokens"],
        "memoryMaxBytes": plan["memoryMaxBytes"],
        "memorySwapMaxBytes": plan["memorySwapMaxBytes"],
        "stderrLimitBytes": plan["stderrBytes"],
        "stdoutLimitBytes": plan["stdoutBytes"],
        "tasksMax": plan["tasksMax"],
        "wallClockSeconds": plan["wallClockSeconds"],
    }


def _gate_row(name: str, gate: dict[str, Any]) -> dict[str, Any]:
    return {
        "denominator": gate["denominator"],
        "gate": name,
        "kind": gate["kind"],
        "numerator": gate["numerator"],
        "status": gate["status"],
    }


def _metric_row(name: str, metric: dict[str, Any]) -> dict[str, Any]:
    return {
        "denominator": metric["denominator"],
        "name": name,
        "numerator": metric["numerator"],
        "status": metric["status"],
        "value": metric["value"],
    }


def _authority_counts(authorities: list[str | None]) -> dict[str, int]:
    from patchpilot_intelligence_evals.corpus_continuation_plan import FAILURE_AUTHORITIES

    counts = {name: 0 for name in FAILURE_AUTHORITIES}
    for item in authorities:
        if isinstance(item, str) and item in counts:
            counts[item] += 1
    return counts


def _evidence_code(authority: str | None, facts: dict[str, Any]) -> str:
    if authority is None:
        return "not-a-failure"
    if authority == "candidate-output":
        return "candidate-output-retained"
    if authority == "adapter":
        return "adapter-rewrite" if facts.get("adapterFallback") else "adapter-behavior"
    return authority


def _limit_status(exit_classification: str) -> str:
    if exit_classification == "output-limit-exceeded":
        return "stdout-limit-exceeded"
    if exit_classification == "stderr-limit-exceeded":
        return "stderr-limit-exceeded"
    return "within-limit"


def _child_state(sampler: ScopeSampler | None, observed: bool) -> str:
    if sampler is None:
        return "not-observed"
    state = str(getattr(sampler, "child_state", "not-observed"))
    if state in {"active", "exited"}:
        return state
    return "exited" if observed else "not-observed"


def _post_exit(sampler: ScopeSampler | None) -> str:
    if sampler is None:
        return "not-observed"
    disposition = str(getattr(sampler, "disposition", "pending"))
    if disposition == "post-exit-scope-removed":
        return "removed"
    if getattr(sampler, "last_complete", None) is not None:
        return "retained"
    return "not-observed"


def _write_extracted(root: Path, run_id: str, extraction: dict[str, Any]) -> None:
    parsed = extraction.get("parsed")
    if not isinstance(parsed, dict):
        return
    explanation = parsed.get("findingExplanationOutput")
    if not isinstance(explanation, dict):
        return
    path = root / "runs" / run_id / "extracted.bin"
    if path.exists():
        raise MeasurementError("result-root-reuse")
    payload = canonical_dumps(explanation).encode("utf-8")
    path.write_bytes(payload)
    path.chmod(0o400)


def _write_unclassified(
    root: Path,
    plan: dict[str, Any],
    case_id: str,
    repetition: int,
    executed: bool,
) -> None:
    record = digest_document(
        _run_body(
            plan,
            executed=executed,
            case_id=case_id,
            repetition=repetition,
            run_id=f"{case_id}-r{repetition}",
            outcome="unclassified-launch",
            authority="measurement-infrastructure",
            record_kind="unclassified-launch",
            failure_evidence="unclassified-launch",
        ),
        "corpus-continuation-run",
        "identityDigest",
    )
    record_path = f"runs/{case_id}-r{repetition}/run.json"
    _write(root, record_path, record, "corpus-continuation-run")


def _empirical(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row["priorEvidence"] == "empirical"]


def _telemetry(memory: dict[str, Any]) -> str:
    if not memory:
        return "not-executed"
    return str(memory.get("telemetry", "not-observed"))


def _write(root: Path, relative: str, document: dict[str, Any], schema_name: str) -> None:
    try:
        write_canonical(relative, document, schema_name=schema_name, root=root)
    except ResultStoreError as exc:
        raise MeasurementError("result-root-reuse") from exc
    (root / relative).chmod(0o400)


def _load(relative: Path, builder: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != builder():
        raise MeasurementError("record-drift")
    return loaded
