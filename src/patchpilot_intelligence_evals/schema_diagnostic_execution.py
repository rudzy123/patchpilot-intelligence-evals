"""Serial six-run diagnostic. Synthetic tests pass a launcher double."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_inference import (
    Launcher,
    assert_no_gold,
    child_indexes,
    classify_execution,
    launch_child,
    measurement_limits,
)
from patchpilot_intelligence_evals.corpus import (
    canonical_dumps,
    load_cases,
    sha256_text,
    to_candidate_input,
)
from patchpilot_intelligence_evals.corpus_continuation_plan import (
    PROFILE_ID,
    continuation_stop,
    measured_continue,
    response_schema_digest,
)
from patchpilot_intelligence_evals.diagnostic_case_selection import PLANNED_RUNS
from patchpilot_intelligence_evals.evaluator import repository_commit
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
from patchpilot_intelligence_evals.output_extraction import extract_envelope
from patchpilot_intelligence_evals.protocol import (
    MAX_STDERR_BYTES,
    MAX_STDOUT_BYTES,
    build_request,
    classify_response,
    parse_candidate_stdout,
)
from patchpilot_intelligence_evals.response_diagnostics import diagnose_response, generation_facts
from patchpilot_intelligence_evals.result_store import ResultStoreError, write_canonical
from patchpilot_intelligence_evals.schema_diagnostic_attribution import (
    attribution_chain,
    extracted_field_names,
)
from patchpilot_intelligence_evals.schema_diagnostic_closeout import build_closeout
from patchpilot_intelligence_evals.schema_diagnostic_plan import (
    artifact_pins,
    identity_fields,
    prepare_diagnostic_root,
    require_schema_diagnostic_approval,
)
from patchpilot_intelligence_evals.schema_diagnostic_preflight import (
    run_schema_diagnostic_preflight,
)
from patchpilot_intelligence_evals.schema_diagnostic_summary import (
    build_summary,
    placeholder_result,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError, repo_root
from patchpilot_intelligence_evals.track11_readiness import recommend

_RUN_TEMPLATE = Path("candidates/templates/schema-diagnostic-run-template.json")
Probe = Callable[[Path], str]


def build_run_template() -> dict[str, Any]:
    """Committed run record. No candidate bytes are stored."""
    return digest_document(_run_body(_plan()), "schema-diagnostic-run", "identityDigest")


def load_run_template() -> dict[str, Any]:
    """Load the committed run template and require it to match the builder."""
    loaded = json.loads((repo_root() / _RUN_TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_run_template():
        raise MeasurementError("record-drift")
    return loaded


def execute_diagnostic(
    *,
    approval: str,
    runtime_root: Path,
    model_root: Path,
    result_root: Path,
    indexes: dict[str, int] | None = None,
    launcher: Launcher = execute_hardened,
    executed: bool = False,
    bind: bool = True,
    probe: Probe | None = None,
) -> dict[str, Any]:
    """Run one sealed repetition of each selected case. There are zero retries."""
    plan = require_schema_diagnostic_approval(approval)
    _require_identities(plan)
    root = prepare_diagnostic_root(result_root)
    if bind:
        from patchpilot_intelligence_evals.measurement_plan import bind_verified_roots

        bind_verified_roots(runtime_root, model_root)
        header_indexes = child_indexes(read_verified_header(runtime_root))
    elif indexes is None:
        raise MeasurementError("unverified-dependency")
    else:
        header_indexes = indexes
    preflight = run_schema_diagnostic_preflight(
        runtime_root,
        model_root,
        root,
        bind=bind,
        probe=probe,
    )
    _write(root, "preflight.json", preflight, "schema-diagnostic-preflight")
    if preflight["preflightStatus"] == "failed" or (
        bind and preflight["preflightStatus"] != "passed"
    ):
        cause = (
            "compatibility-failure"
            if preflight["templateStatus"] == "failed"
            else "precheck-failed"
        )
        return _finish(root, plan, [], cause, executed, preflight)
    template = prompt_template()
    runtime_dir = runtime_root / "verified" / RUNTIME_ATTEMPT
    model_dir = model_root / "verified" / CANDIDATE_ATTEMPT
    loaded = {str(case["caseId"]): case for case in load_cases()}
    sealed_rows: list[dict[str, Any]] = []
    stop: str | None = None
    for planned in plan["runs"]:
        if stop is not None:
            break
        case_id = str(planned["caseId"])
        case = loaded.get(case_id)
        if case is None or str(case["category"]) != planned["category"]:
            raise MeasurementError("corpus-mismatch")
        request = build_request(case, plan["planDigest"])
        hidden = to_candidate_input(case)
        assert_no_gold(hidden)
        config = _config(plan, header_indexes, template, request)
        try:
            result, sampler = launch_child(
                config,
                runtime_dir=runtime_dir,
                model_dir=model_dir,
                limits=measurement_limits(plan),
                launcher=launcher,
                schema_diagnostic_approval=approval if launcher is execute_hardened else None,
            )
        except MeasurementError as exc:
            stop = exc.code
            break
        try:
            record, outcome = _seal_one(
                root=root,
                plan=plan,
                planned=planned,
                request=request,
                result=result,
                sampler=sampler,
                executed=executed,
            )
        except MeasurementError as exc:
            if exc.code == "unclassified-launch":
                sealed_rows.append(_unclassified_row(planned))
                stop = "unclassified-launch"
                break
            if continuation_stop(exc.code):
                stop = exc.code
                break
            raise
        sealed_rows.append(_result_row(record))
        if continuation_stop(outcome) or not measured_continue(outcome):
            stop = outcome
            break
    return _finish(root, plan, sealed_rows, stop, executed, preflight)


def _plan() -> dict[str, Any]:
    from patchpilot_intelligence_evals.schema_diagnostic_plan import load_schema_diagnostic_plan

    return load_schema_diagnostic_plan()


def _finish(
    root: Path,
    plan: dict[str, Any],
    sealed_rows: list[dict[str, Any]],
    stop: str | None,
    executed: bool,
    preflight: dict[str, Any],
) -> dict[str, Any]:
    del executed
    by_id = {str(row["runId"]): row for row in sealed_rows}
    rows = [
        by_id[str(planned["runId"])]
        if str(planned["runId"]) in by_id
        else placeholder_result(planned)
        for planned in plan["runs"]
    ]
    summary = build_summary(plan, rows, stop)
    cleanup = "not-performed"
    if sealed_rows:
        cleanup = "failed" if stop == "cleanup-failure" else "reaped"
    if stop == "raw-output-unretained":
        retention = "partial"
    elif sealed_rows:
        retention = "retained"
    else:
        retention = "not-performed"
    closeout = build_closeout(plan, summary, stop, cleanup=cleanup, retention=retention)
    readiness = recommend(closeout, summary)
    _write(root, "summary.json", summary, "schema-diagnostic-summary")
    _write(root, "closeout.json", closeout, "schema-diagnostic-closeout")
    _write(root, "track11-readiness.json", readiness, "track11-readiness")
    return summary


def _seal_one(
    *,
    root: Path,
    plan: dict[str, Any],
    planned: dict[str, Any],
    request: dict[str, Any],
    result: ExecutionResult,
    sampler: Any,
    executed: bool,
) -> tuple[dict[str, Any], str]:
    classified = classify_execution(result, sampler, cold_warm=False)
    if getattr(sampler, "blocked_classification", None) == "infrastructure-failure":
        classified["exitClassification"] = "isolation-failure"
    stdout = result.stdout
    limit = _limit_status(result.exit_classification)
    run_id = str(planned["runId"])
    raw = _retain_bytes(
        root, run_id=run_id, stdout=stdout, stderr=result.stderr, limit_status=limit
    )
    try:
        extraction = extract_envelope(stdout)
        side = generation_facts(result.generation_diagnostic)
        diagnosed = diagnose_response(extraction, side)
        outcome, _parsed = _outcome(classified, stdout, request)
        merged = {
            **diagnosed,
            "extractedDigest": extraction["extractedDigest"],
            "extractionStatus": extraction["extractionStatus"],
        }
        authority = attribute_failure(outcome, raw, merged)
        chain = attribution_chain(
            exit_classification=outcome,
            raw=raw,
            diagnostic=merged,
            side_names=side.get("innerFieldNames")
            if isinstance(side.get("innerFieldNames"), list)
            else None,
            extracted_names=extracted_field_names(extraction.get("parsed")),
        )
        record = digest_document(
            _run_body(
                plan,
                executed=executed,
                planned=planned,
                request=request,
                raw=raw,
                extraction=extraction,
                diagnosed=diagnosed,
                classified=classified,
                sampler=sampler,
                outcome=outcome,
                authority=authority,
                chain=chain,
            ),
            "schema-diagnostic-run",
            "identityDigest",
        )
    except (MeasurementError, ResultStoreError, SchemaValidationError, OSError):
        if not stdout:
            raise
        _write_unclassified(root, plan, planned, raw, executed)
        raise MeasurementError("unclassified-launch") from None
    _write_extracted(root, run_id, extraction)
    _write(root, f"runs/{run_id}/run.json", record, "schema-diagnostic-run")
    return record, outcome


def _require_identities(plan: dict[str, Any]) -> None:
    if plan["corpusDigest"] != CORPUS_DIGEST or len(plan["runs"]) != PLANNED_RUNS:
        raise MeasurementError("corpus-mismatch")
    if prompt_template() == "" or plan["promptTemplateDigest"] != PROMPT_TEMPLATE_DIGEST:
        raise MeasurementError("prompt-mismatch")
    if plan["responseSchema"]["digest"] != response_schema_digest():
        raise MeasurementError("response-schema-mismatch")
    if plan["caseCount"] != PLANNED_RUNS or plan["repetitionsPerCase"] != 1:
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
        "phase": "schema-diagnostic",
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
    executed: bool = False,
    planned: dict[str, Any] | None = None,
    request: dict[str, Any] | None = None,
    raw: dict[str, Any] | None = None,
    extraction: dict[str, Any] | None = None,
    diagnosed: dict[str, Any] | None = None,
    classified: dict[str, Any] | None = None,
    sampler: Any = None,
    outcome: str = "not-executed",
    authority: str | None = None,
    chain: dict[str, Any] | None = None,
    record_kind: str = "run",
) -> dict[str, Any]:
    observed = executed and outcome != "not-executed"
    memory = {} if classified is None else classified["coldMemory"]
    timing = {} if classified is None else classified["coldTiming"]
    facts = diagnosed or _empty_diagnostic()
    generation_observed = bool(facts["generationObserved"])
    extracted = extraction or {
        "extractedBytes": 0,
        "extractedDigest": None,
        "extractionStatus": "not-performed",
    }
    retained = raw or {}
    links = chain or _empty_chain()
    case_id = "not-executed" if planned is None else str(planned["caseId"])
    category = "not-executed" if planned is None else str(planned["category"])
    run_id = "not-executed" if planned is None else str(planned["runId"])
    if outcome in {"success", "not-executed"}:
        stop: str | None = None
    else:
        stop = outcome
    eligibility = "not-executed"
    if observed or raw is not None:
        eligibility = (
            "qualifying" if links["qualifyingCandidateOutputSchemaFailure"] else "not-qualifying"
        )
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        **_limits(plan),
        "adapterFallback": bool(facts["adapterFallback"]),
        "adapterInnerFieldComparison": links["adapterInnerFieldComparison"],
        "adapterInnerFieldMutation": links["adapterInnerFieldMutation"],
        "adapterTruncated": bool(facts["adapterTruncated"]),
        "blockingInfrastructureExplanation": links["blockingInfrastructureExplanation"],
        "blockingSecurityExplanation": links["blockingSecurityExplanation"],
        "caseId": case_id,
        "category": category,
        "childState": _child_state(sampler, observed),
        "cleanupStatus": "not-performed" if classified is None else classified["cleanup"],
        "cgroupCurrentBytes": memory.get("cgroupCurrentBytes"),
        "cgroupPeakBytes": memory.get("cgroupPeakBytes"),
        "decoding": dict(plan["decoding"]),
        "evidenceIdFindings": list(facts["evidenceIdFindings"]),
        "exitClassification": outcome,
        "extractedBytes": int(extracted["extractedBytes"]),
        "extractedDigest": extracted["extractedDigest"],
        "extractionAuthorityEstablished": links["extractionAuthorityEstablished"],
        "extractionStatus": extracted["extractionStatus"],
        "failureAuthority": authority,
        "generationObserved": generation_observed,
        "generationSeconds": timing.get("generationSeconds"),
        "inputDigest": None if request is None else sha256_text(canonical_dumps(request)),
        "intendedResponseSchemaApplied": links["intendedResponseSchemaApplied"],
        "jsonParseAuthorityEstablished": links["jsonParseAuthorityEstablished"],
        "loadSeconds": timing.get("loadSeconds"),
        "measurementCompleted": observed and outcome == "success",
        "measurementPerformed": observed,
        "missingRequired": list(facts["missingRequired"]),
        "modelSessionCreated": observed,
        "networkResult": "not-performed" if classified is None else classified["networkResult"],
        "oomEvents": memory.get("oomEvents"),
        "outputLimitExceeded": links["outputLimitExceeded"],
        "outputLimitStatus": retained.get("outputLimitStatus", "not-retained"),
        "parseStatus": facts["parseStatus"],
        "postExitScope": _post_exit(sampler),
        "processCleanup": "not-performed" if classified is None else classified["cleanup"],
        "processRssBytes": memory.get("processRssBytes"),
        "processTreeRssBytes": memory.get("processTreeRssBytes"),
        "profileId": PROFILE_ID,
        "qualifyingCandidateOutputSchemaFailure": links["qualifyingCandidateOutputSchemaFailure"],
        "rawOutputRetained": links["rawOutputRetained"],
        "realModelExecuted": observed and generation_observed,
        "recordKind": record_kind,
        "repetition": 1,
        "repositoryCommit": "not-executed" if not observed else repository_commit(),
        "responseFailureAuthority": links["responseFailureAuthority"],
        "runId": run_id,
        "runInvoked": observed,
        "schemaStatus": facts["schemaStatus"],
        "stderrBytes": int(retained.get("stderrBytes", 0)),
        "stderrDigest": retained.get("stderrDigest"),
        "stderrTruncated": bool(retained.get("stderrTruncated", False)),
        "stdoutBytes": int(retained.get("stdoutBytes", 0)),
        "stdoutDigest": retained.get("stdoutDigest"),
        "stdoutTruncated": bool(retained.get("stdoutTruncated", False)),
        "stopCause": stop,
        "telemetryStatus": _telemetry(memory, observed=classified is not None),
        "thresholdEligibility": eligibility,
        "timestamp": "not-executed" if not observed else utc_timestamp(),
        "trailingBytes": int(facts["trailingBytes"]),
        "truncated": links["truncated"],
        "unexpectedFields": list(facts["unexpectedFields"]),
        "utf8": bool(facts["utf8"]),
        "virtualAddressBytes": memory.get("virtualAddressBytes"),
        "wallSeconds": timing.get("wallSeconds"),
    }


def _empty_diagnostic() -> dict[str, Any]:
    return {
        "adapterFallback": False,
        "adapterTruncated": False,
        "evidenceIdFindings": [],
        "generationObserved": False,
        "missingRequired": [],
        "parseStatus": "not-performed",
        "schemaStatus": "not-performed",
        "trailingBytes": 0,
        "unexpectedFields": [],
        "utf8": False,
    }


def _empty_chain() -> dict[str, Any]:
    return {
        "adapterInnerFieldComparison": "not-performed",
        "adapterInnerFieldMutation": None,
        "blockingInfrastructureExplanation": False,
        "blockingSecurityExplanation": False,
        "extractionAuthorityEstablished": False,
        "intendedResponseSchemaApplied": False,
        "jsonParseAuthorityEstablished": False,
        "outputLimitExceeded": False,
        "qualifyingCandidateOutputSchemaFailure": False,
        "rawOutputRetained": False,
        "responseFailureAuthority": None,
        "truncated": False,
    }


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


def _result_row(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "caseId": record["caseId"],
        "category": record["category"],
        "exitClassification": record["exitClassification"],
        "missingRequired": list(record["missingRequired"]),
        "qualifyingCandidateOutputSchemaFailure": record["qualifyingCandidateOutputSchemaFailure"],
        "repetition": 1,
        "responseFailureAuthority": record["responseFailureAuthority"],
        "runId": record["runId"],
        "schemaStatus": record["schemaStatus"],
        "sealed": True,
        "unexpectedFields": list(record["unexpectedFields"]),
    }


def _unclassified_row(planned: dict[str, Any]) -> dict[str, Any]:
    row = placeholder_result(planned)
    row["exitClassification"] = "unclassified-launch"
    row["responseFailureAuthority"] = "measurement-infrastructure"
    row["schemaStatus"] = "not-performed"
    row["sealed"] = True
    return row


def _retain_bytes(
    root: Path,
    *,
    run_id: str,
    stdout: bytes,
    stderr: bytes,
    limit_status: str,
) -> dict[str, Any]:
    if len(stdout) > MAX_STDOUT_BYTES or len(stderr) > MAX_STDERR_BYTES:
        raise MeasurementError("excessive-output")
    if limit_status not in {"within-limit", "stdout-limit-exceeded", "stderr-limit-exceeded"}:
        raise MeasurementError("raw-output-unretained")
    run_dir = root / "runs" / run_id
    if run_dir.exists():
        raise MeasurementError("result-root-reuse")
    runs = root / "runs"
    try:
        if not runs.exists():
            runs.mkdir(mode=0o700)
        os.chmod(runs, 0o700)
        run_dir.mkdir(mode=0o700)
        os.chmod(run_dir, 0o700)
        stdout_path = run_dir / "stdout.bin"
        stderr_path = run_dir / "stderr.bin"
        stdout_path.write_bytes(stdout)
        stderr_path.write_bytes(stderr)
        os.chmod(stdout_path, 0o400)
        os.chmod(stderr_path, 0o400)
    except OSError as exc:
        raise MeasurementError("raw-output-unretained") from exc
    return {
        "outputLimitStatus": limit_status,
        "retentionStatus": "retained",
        "stderrBytes": len(stderr),
        "stderrDigest": hashlib.sha256(stderr).hexdigest(),
        "stderrTruncated": limit_status == "stderr-limit-exceeded",
        "stdoutBytes": len(stdout),
        "stdoutDigest": hashlib.sha256(stdout).hexdigest(),
        "stdoutTruncated": limit_status == "stdout-limit-exceeded",
    }


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
    path.write_bytes(canonical_dumps(explanation).encode("utf-8"))
    path.chmod(0o400)


def _write_unclassified(
    root: Path,
    plan: dict[str, Any],
    planned: dict[str, Any],
    raw: dict[str, Any],
    executed: bool,
) -> None:
    chain = _empty_chain()
    chain["rawOutputRetained"] = True
    chain["blockingInfrastructureExplanation"] = True
    chain["responseFailureAuthority"] = "measurement-infrastructure"
    record = digest_document(
        _run_body(
            plan,
            executed=executed,
            planned=planned,
            raw=raw,
            outcome="unclassified-launch",
            authority="measurement-infrastructure",
            chain=chain,
            record_kind="unclassified-launch",
        ),
        "schema-diagnostic-run",
        "identityDigest",
    )
    _write(root, f"runs/{planned['runId']}/run.json", record, "schema-diagnostic-run")


def _limit_status(exit_classification: str) -> str:
    if exit_classification == "output-limit-exceeded":
        return "stdout-limit-exceeded"
    if exit_classification == "stderr-limit-exceeded":
        return "stderr-limit-exceeded"
    return "within-limit"


def _child_state(sampler: Any, observed: bool) -> str:
    if sampler is None:
        return "not-observed"
    state = str(getattr(sampler, "child_state", "not-observed"))
    if state in {"active", "exited"}:
        return state
    return "exited" if observed else "not-observed"


def _post_exit(sampler: Any) -> str:
    if sampler is None:
        return "not-observed"
    disposition = str(getattr(sampler, "disposition", "pending"))
    if disposition == "post-exit-scope-removed":
        return "removed"
    if getattr(sampler, "last_complete", None) is not None:
        return "retained"
    return "not-observed"


def _telemetry(memory: dict[str, Any], *, observed: bool) -> str:
    if not observed:
        return "not-executed"
    if not memory:
        return "not-observed"
    return str(memory.get("telemetry", "not-observed"))


def _write(root: Path, relative: str, document: dict[str, Any], schema_name: str) -> None:
    try:
        write_canonical(relative, document, schema_name=schema_name, root=root)
    except ResultStoreError as exc:
        raise MeasurementError("result-root-reuse") from exc
    (root / relative).chmod(0o400)
