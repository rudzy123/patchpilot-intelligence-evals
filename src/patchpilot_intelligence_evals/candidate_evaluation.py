"""Evaluate a deterministic test double through the candidate protocol.

Execution failure is not a quality failure. Unscored cases stay unmeasured
and do not increment state-mutation gates. productionReady stays false.
"""

from __future__ import annotations

import logging
import platform
import time
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_manifest import validate_manifest
from patchpilot_intelligence_evals.candidate_runner import Invocation, invoke_candidate
from patchpilot_intelligence_evals.corpus import (
    canonical_dumps,
    load_cases,
    sha256_text,
    validate_corpus,
)
from patchpilot_intelligence_evals.evaluator import CATEGORIES, GATE_NAMES, repository_commit
from patchpilot_intelligence_evals.metrics import (
    METRIC_NAMES,
    add_metrics,
    gate_from_metric,
    measure,
    score_case,
)
from patchpilot_intelligence_evals.protocol import (
    EVALUATOR_VERSION,
    PROMPT_IDENTITY,
    PURPOSE,
    TIMEOUT_SECONDS,
    build_request,
    execution_constraints,
    experiment_id,
)
from patchpilot_intelligence_evals.result_store import (
    ResultStoreError,
    experiment_manifest_for,
    prepare_execution_write,
    write_execution_result,
)
from patchpilot_intelligence_evals.schemas import repo_root

LOGGER = logging.getLogger("patchpilot_intelligence_evals")
Invoker = Callable[..., Invocation]


def _log_case(case_id: str, metric: str, status: str) -> str:
    message = "case_id=%s metric=%s status=%s"
    LOGGER.info(message, case_id, metric, status)
    return message % (case_id, metric, status)


def _unscored_metrics() -> dict[str, Any]:
    return {name: measure(0, 0) for name in METRIC_NAMES}


def _peak_memory_kb() -> dict[str, Any]:
    try:
        import resource
    except ImportError:
        return measure(0, 0)
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if usage < 0:
        return measure(0, 0)
    return measure(int(usage), 1, as_count=True)


def _software() -> tuple[str, str, str]:
    system = platform.platform()
    if len(system) > 200:
        system = system[:200]
    return platform.python_version(), system, version("jsonschema")


def _assert_no_case_text(result: dict[str, Any], cases: Sequence[dict[str, Any]]) -> None:
    text = canonical_dumps(result)
    if "explanationText" in text or "assistanceRequest" in text:
        raise ResultStoreError("prompt-in-result")
    for case in cases:
        prompt = str(case["assistanceRequest"])
        if prompt and prompt in text:
            raise ResultStoreError("prompt-in-result")


def evaluate_candidate(
    manifest: dict[str, Any],
    *,
    output_dir: str | None = None,
    output_root: Path | None = None,
    case_ids: tuple[str, ...] | None = None,
    timeout_seconds: float = TIMEOUT_SECONDS,
    invoker: Invoker = invoke_candidate,
) -> dict[str, Any]:
    """Run one child process per selected case. A full run uses every corpus case.

    ``case_ids`` limits a focused run and marks it incomplete. The recorded
    protocol timeout stays 15 seconds. Tests may pass a shorter kill timer.
    """
    root = repo_root()
    artifact_root = output_root if output_root is not None else root
    validate_manifest(manifest, root=root)
    summary = validate_corpus()
    selected = load_cases()
    if case_ids is not None:
        wanted = set(case_ids)
        selected = [case for case in selected if str(case["caseId"]) in wanted]
        if len(selected) != len(wanted):
            raise ResultStoreError("unknown-case")
    manifest_digest = str(manifest["manifestDigest"])
    corpus_digest = str(summary["corpusDigest"])
    identity = experiment_id(manifest_digest=manifest_digest, corpus_digest=corpus_digest)
    if output_dir is not None:
        prepare_execution_write(output_dir, identity, root=artifact_root)
    per_case: list[dict[str, Any]] = []
    for case in selected:
        case_id = str(case["caseId"])
        request = build_request(case, manifest_digest)
        started = time.perf_counter()
        first = invoker(manifest, request, timeout_seconds=timeout_seconds, root=root)
        elapsed_us = int((time.perf_counter() - started) * 1_000_000)
        if first.outcome == "success" and first.parsed is not None:
            second = invoker(manifest, request, timeout_seconds=timeout_seconds, root=root)
            first_output = first.parsed["findingExplanationOutput"]
            replay_match = (
                second.outcome == "success"
                and second.parsed is not None
                and canonical_dumps(first_output)
                == canonical_dumps(second.parsed["findingExplanationOutput"])
            )
            log_line = _log_case(case_id, "outputSchemaValidity", "pass")
            metrics = score_case(
                case,
                first_output,
                schema_valid=True,
                replay_match=replay_match,
                log_text=log_line,
            )
            metrics["latency"] = measure(elapsed_us, 1)
            quality_scored = True
        else:
            _log_case(case_id, "executionOutcome", first.outcome)
            metrics = _unscored_metrics()
            quality_scored = False
        per_case.append(
            {
                "caseId": case_id,
                "category": str(case["category"]),
                "executionOutcome": first.outcome,
                "inputDigest": request["findingExplanationInput"]["inputDigest"],
                "outputDigest": first.output_digest,
                "qualityScored": quality_scored,
                "metrics": metrics,
            }
        )
    grouped = {
        category: [item["metrics"] for item in per_case if item["category"] == category]
        for category in CATEGORIES
    }
    by_category = {category: add_metrics(grouped[category]) for category in CATEGORIES}
    global_metrics = add_metrics([item["metrics"] for item in per_case])
    global_metrics["peakProcessMemory"] = _peak_memory_kb()
    gates = {name: gate_from_metric(name, global_metrics[name]) for name in GATE_NAMES}
    for name in METRIC_NAMES:
        if name == "peakProcessMemory":
            continue
        _log_case("global", name, str(global_metrics[name]["status"]))
    python_version, operating_system, jsonschema_version = _software()
    result: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "protocolVersion": "1.0.0",
        "purpose": PURPOSE,
        "productionReady": False,
        "resultDistinctions": {
            "harnessCorrectness": "reported",
            "baselinePerformance": "not-measured",
            "candidatePerformance": "reported",
            "promotionGateStatus": "reported",
            "executionFailures": "distinguished-from-quality-failures",
            "incompleteMetrics": "distinguished-by-unmeasured-status",
        },
        "repositoryCommit": repository_commit(),
        "corpusVersion": "1.0.0",
        "corpusDigest": corpus_digest,
        "candidateManifestDigest": manifest_digest,
        "candidateId": str(manifest["candidateId"]),
        "candidateVersion": str(manifest["candidateVersion"]),
        "candidateKind": "deterministic-test-double",
        "experimentId": identity,
        "evaluatorVersion": EVALUATOR_VERSION,
        "pythonVersion": python_version,
        "operatingSystem": operating_system,
        "jsonschemaVersion": jsonschema_version,
        "executedAt": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "deterministicSettings": {"canonicalJson": "sort_keys_separators_utf8_no_newline"},
        "promptIdentity": PROMPT_IDENTITY,
        "executionConstraints": execution_constraints(),
        "complete": case_ids is None,
        "caseCount": len(per_case),
        "perCase": per_case,
        "byCategory": by_category,
        "global": global_metrics,
        "gates": gates,
        "unmeasuredMetrics": sorted(
            name for name in METRIC_NAMES if global_metrics[name]["status"] == "unmeasured"
        ),
        "executionFailureCategories": sorted(
            {
                str(item["executionOutcome"])
                for item in per_case
                if item["executionOutcome"] != "success"
            }
        ),
    }
    result["experimentManifestDigest"] = sha256_manifest(result)
    _assert_no_case_text(result, selected)
    if output_dir is not None:
        write_execution_result(output_dir, result, root=artifact_root)
    return result


def sha256_manifest(result: dict[str, Any]) -> str:
    return sha256_text(canonical_dumps(experiment_manifest_for(result)))
