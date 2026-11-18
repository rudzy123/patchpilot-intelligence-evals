"""Track 10A attribution chain. Track 9A failure authority stays unchanged."""

from __future__ import annotations

from typing import Any

_SECURITY = frozenset({"gold-visible", "isolation-failure", "network-violation"})
_INFRASTRUCTURE = frozenset(
    {
        "approval-required",
        "cleanup-failure",
        "compatibility-failure",
        "corpus-mismatch",
        "digest-mismatch",
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
_AUTHORITIES = frozenset(
    {
        "adapter",
        "candidate-output",
        "evaluator",
        "measurement-infrastructure",
        "protocol",
        "security-boundary",
        "unresolved",
    }
)


def extracted_field_names(parsed: object) -> list[str] | None:
    """Return sorted explanation keys. Values are not copied."""
    if not isinstance(parsed, dict):
        return None
    explanation = parsed.get("findingExplanationOutput")
    if not isinstance(explanation, dict):
        return None
    return sorted(str(key) for key in explanation)


def attribution_chain(
    *,
    exit_classification: str,
    raw: dict[str, Any],
    diagnostic: dict[str, Any],
    side_names: list[str] | None,
    extracted_names: list[str] | None,
) -> dict[str, Any]:
    """Return the chain used by the precommitted threshold."""
    raw_retained = raw.get("retentionStatus") == "retained"
    truncated = bool(raw.get("stdoutTruncated")) or bool(raw.get("stderrTruncated"))
    limit_status = str(raw.get("outputLimitStatus", "not-retained"))
    output_limit = limit_status != "within-limit"
    extraction_ok = (
        diagnostic.get("extractionStatus") == "extracted"
        and diagnostic.get("extractedDigest") is not None
    )
    parse_ok = diagnostic.get("parseStatus") == "parsed"
    schema_status = str(diagnostic.get("schemaStatus", "not-performed"))
    schema_applied = schema_status in {"valid", "invalid"}
    if side_names is None or extracted_names is None:
        comparison = "unresolved"
        mutation: bool | None = None
    elif side_names == extracted_names:
        comparison = "matched"
        mutation = False
    else:
        comparison = "mutated"
        mutation = True
    adapter_signal = (
        exit_classification in _ADAPTER_EXIT
        or diagnostic.get("adapterFallback") is True
        or diagnostic.get("adapterTruncated") is True
        or int(diagnostic.get("trailingBytes") or 0) > 0
        or mutation is True
    )
    blocking_security = exit_classification in _SECURITY
    blocking_infrastructure = exit_classification in _INFRASTRUCTURE
    if blocking_security:
        authority = "security-boundary"
    elif exit_classification == "evaluator-failure":
        authority = "evaluator"
    elif blocking_infrastructure:
        authority = "measurement-infrastructure"
    elif exit_classification == "excessive-output" or output_limit:
        authority = "protocol"
    elif adapter_signal:
        authority = "adapter"
    elif (
        schema_status == "invalid"
        and raw_retained
        and extraction_ok
        and parse_ok
        and schema_applied
        and mutation is False
        and not truncated
        and not output_limit
    ):
        authority = "candidate-output"
    elif schema_status == "valid" and exit_classification == "success":
        authority = None
    else:
        authority = "unresolved"
    if authority is not None and authority not in _AUTHORITIES:
        authority = "unresolved"
    qualifying = bool(
        authority == "candidate-output"
        and schema_status == "invalid"
        and raw_retained
        and extraction_ok
        and parse_ok
        and schema_applied
        and mutation is False
        and comparison == "matched"
        and not truncated
        and not output_limit
        and not blocking_infrastructure
        and not blocking_security
    )
    return {
        "adapterInnerFieldComparison": comparison,
        "adapterInnerFieldMutation": mutation,
        "blockingInfrastructureExplanation": blocking_infrastructure,
        "blockingSecurityExplanation": blocking_security,
        "extractionAuthorityEstablished": extraction_ok,
        "intendedResponseSchemaApplied": schema_applied,
        "jsonParseAuthorityEstablished": parse_ok,
        "outputLimitExceeded": output_limit,
        "qualifyingCandidateOutputSchemaFailure": qualifying,
        "rawOutputRetained": raw_retained,
        "responseFailureAuthority": authority,
        "truncated": truncated,
    }
