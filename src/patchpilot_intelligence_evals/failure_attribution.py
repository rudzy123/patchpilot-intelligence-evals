"""One failure authority for a sealed run, cited from retained diagnostics."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.corpus_continuation_plan import FAILURE_AUTHORITIES

_SECURITY = frozenset({"gold-visible", "isolation-failure", "network-violation"})
_INFRASTRUCTURE = frozenset(
    {
        "approval-required",
        "cleanup-failure",
        "compatibility-failure",
        "corpus-mismatch",
        "digest-mismatch",
        "evaluator-failure",
        "memory-ceiling",
        "oom",
        "plan-consumed",
        "precheck-failed",
        "prompt-mismatch",
        "raw-output-unretained",
        "response-schema-mismatch",
        "result-root-reuse",
        "telemetry-unresolved",
        "unclassified-launch",
        "unverified-dependency",
    }
)
_ADAPTER_EXIT = frozenset(
    {
        "inference-failure",
        "model-load-failure",
        "runtime-startup-failure",
        "tokenizer-failure",
    }
)


def attribute_failure(
    exit_classification: str,
    raw: dict[str, Any],
    diagnostic: dict[str, Any],
) -> str | None:
    """Classify a failed run. A successful run has no failure authority."""
    if exit_classification in {"success", "not-executed"}:
        return None
    if exit_classification in _SECURITY:
        return _known("security-boundary")
    if exit_classification in _INFRASTRUCTURE:
        return _known("measurement-infrastructure")
    if exit_classification == "excessive-output":
        if raw.get("retentionStatus") == "retained":
            return _known("protocol")
        return _known("measurement-infrastructure")
    if exit_classification in _ADAPTER_EXIT:
        return _known("adapter")
    if exit_classification in {"malformed-response", "schema-failure"}:
        return _content_authority(exit_classification, raw, diagnostic)
    if exit_classification == "timeout":
        if raw.get("retentionStatus") == "retained":
            return _known("candidate-output")
        return _known("unresolved")
    if exit_classification == "nonzero-exit":
        return _known("unresolved")
    return _known("unresolved")


def _content_authority(
    exit_classification: str,
    raw: dict[str, Any],
    diagnostic: dict[str, Any],
) -> str:
    if raw.get("retentionStatus") != "retained":
        return _known("unresolved")
    extraction = diagnostic.get("extractionStatus")
    parse_status = diagnostic.get("parseStatus")
    if extraction in {None, "not-performed"} or parse_status in {None, "not-performed"}:
        return _known("unresolved")
    if diagnostic.get("generationObserved") is not True:
        return _known("unresolved")
    if (
        diagnostic.get("adapterFallback") is True
        or diagnostic.get("adapterTruncated") is True
        or int(diagnostic.get("trailingBytes") or 0) > 0
    ):
        return _known("adapter")
    if (
        exit_classification == "schema-failure"
        and diagnostic.get("schemaStatus") == "not-performed"
    ):
        return _known("unresolved")
    return _known("candidate-output")


def _known(value: str) -> str:
    if value not in FAILURE_AUTHORITIES:
        return "unresolved"
    return value
