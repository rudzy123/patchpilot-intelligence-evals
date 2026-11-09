"""Evaluate the deterministic baseline and build a result record.

The record is harness-validation evidence. It is not a model-quality claim
and it is not committed, because the timestamp is not stable.
"""

from __future__ import annotations

import logging
import platform
import time
from datetime import UTC, datetime
from importlib.metadata import version
from typing import Any

from patchpilot_intelligence_evals import __version__
from patchpilot_intelligence_evals.baseline import CANDIDATE, run_baseline
from patchpilot_intelligence_evals.corpus import (
    canonical_dumps,
    load_cases,
    sha256_text,
    validate_corpus,
)
from patchpilot_intelligence_evals.metrics import (
    METRIC_NAMES,
    add_metrics,
    gate_from_metric,
    measure,
    score_case,
)
from patchpilot_intelligence_evals.network_guard import network_guard
from patchpilot_intelligence_evals.schemas import (
    SCHEMA_IDS,
    SchemaValidationError,
    repo_root,
    validate,
)

LOGGER = logging.getLogger("patchpilot_intelligence_evals")

CATEGORIES: tuple[str, ...] = (
    "grounding-citation",
    "insufficient-evidence-refusal",
    "prompt-injection",
    "cross-tenant-negative-control",
    "contradiction",
    "stale-unavailable-incomparable",
)

GATE_NAMES: tuple[str, ...] = (
    "crossTenantDisclosure",
    "unauthorizedStateMutation",
    "affectednessOrPriorityChange",
    "secretDisclosure",
    "outputSchemaValidity",
    "citationValidity",
    "evidenceAttributionAccuracy",
    "unsupportedFactualClaims",
    "correctRefusal",
    "promptInjectionResistance",
)

PROMPT_IDENTITY = "none-deterministic-baseline"


def repository_commit() -> str:
    git_dir = repo_root() / ".git"
    head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
    if not head.startswith("ref: "):
        return head if len(head) == 40 else "unknown"
    ref = head.removeprefix("ref: ")
    ref_path = git_dir / ref
    if ref_path.is_file():
        value = ref_path.read_text(encoding="utf-8").strip()
        return value if len(value) == 40 else "unknown"
    packed = git_dir / "packed-refs"
    if packed.is_file():
        for line in packed.read_text(encoding="utf-8").splitlines():
            if line.startswith("#") or line.startswith("^"):
                continue
            if " " in line:
                commit, name = line.split(" ", 1)
                if name == ref and len(commit) == 40:
                    return commit
    return "unknown"


def _software_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "package": __version__,
        "jsonschema": version("jsonschema"),
    }


def _peak_memory_kb() -> dict[str, Any]:
    try:
        import resource
    except ImportError:
        return measure(0, 0)
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if usage < 0:
        return measure(0, 0)
    return measure(int(usage), 1, as_count=True)


def _log_case(case_id: str, metric: str, status: str) -> str:
    message = "case_id=%s metric=%s status=%s"
    LOGGER.info(message, case_id, metric, status)
    return message % (case_id, metric, status)


def experiment_manifest(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "experimentId": result["experimentId"],
        "purpose": result["purpose"],
        "productionReady": False,
        "corpusVersion": result["corpusVersion"],
        "corpusDigest": result["corpusDigest"],
        "candidate": result["candidate"],
        "softwareVersions": result["softwareVersions"],
        "deterministicSettings": result["deterministicSettings"],
        "promptIdentity": result["promptIdentity"],
        "schemaIds": list(SCHEMA_IDS),
    }


def evaluate_baseline() -> dict[str, Any]:
    """Run the baseline under the in-process network guard."""
    with network_guard():
        summary = validate_corpus()
        cases = load_cases()
        per_case: list[dict[str, Any]] = []
        for case in cases:
            case_id = str(case["caseId"])
            started = time.perf_counter()
            first = run_baseline(case)
            elapsed_us = int((time.perf_counter() - started) * 1_000_000)
            second = run_baseline(case)
            replay_match = canonical_dumps(first) == canonical_dumps(second)
            schema_valid = True
            try:
                validate("finding-explanation-output", first)
            except SchemaValidationError:
                schema_valid = False
            log_line = _log_case(
                case_id,
                "outputSchemaValidity",
                "pass" if schema_valid else "fail",
            )
            metrics = score_case(
                case,
                first,
                schema_valid=schema_valid,
                replay_match=replay_match,
                log_text=log_line,
            )
            metrics["latency"] = measure(elapsed_us, 1)
            per_case.append(
                {
                    "caseId": case_id,
                    "category": str(case["category"]),
                    "outputDigest": sha256_text(canonical_dumps(first)),
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
        for name in METRIC_NAMES:
            if name == "peakProcessMemory":
                continue
            _log_case("global", name, str(global_metrics[name]["status"]))
        gates = {name: gate_from_metric(name, global_metrics[name]) for name in GATE_NAMES}
        corpus_digest = str(summary["corpusDigest"])
        identity = f"{corpus_digest}:{CANDIDATE['name']}:{CANDIDATE['version']}"
        result: dict[str, Any] = {
            "schemaVersion": "1.0.0",
            "purpose": "harness-validation",
            "productionReady": False,
            "resultDistinctions": {
                "harnessCorrectness": "reported",
                "baselinePerformance": "reported-as-harness-validation-only",
                "candidatePerformance": "not-measured",
                "promotionGateStatus": "reported",
                "unavailableEvidence": "reported-per-case",
                "incompleteMetrics": "distinguished-by-unmeasured-status",
            },
            "repositoryCommit": repository_commit(),
            "corpusVersion": "1.0.0",
            "corpusDigest": corpus_digest,
            "candidate": dict(CANDIDATE),
            "softwareVersions": _software_versions(),
            "executedAt": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "deterministicSettings": {"canonicalJson": "sort_keys_separators_utf8_no_newline"},
            "promptIdentity": PROMPT_IDENTITY,
            "experimentId": sha256_text(identity),
            "perCase": per_case,
            "byCategory": by_category,
            "global": global_metrics,
            "gates": gates,
        }
        validate("evaluation-result", result)
        validate("experiment-manifest", experiment_manifest(result))
        return result
