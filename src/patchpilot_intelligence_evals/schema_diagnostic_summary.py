"""Threshold evaluation for the six-run diagnostic. This module does not score the corpus."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.diagnostic_case_selection import PLANNED_RUNS
from patchpilot_intelligence_evals.measurement_plan import MeasurementError, digest_document
from patchpilot_intelligence_evals.schema_diagnostic_plan import (
    artifact_pins,
    identity_fields,
    load_schema_diagnostic_plan,
    systematic_threshold,
)
from patchpilot_intelligence_evals.schemas import repo_root

_TEMPLATE = Path("candidates/templates/schema-diagnostic-summary-template.json")
AUTHORITY_BLOCKS = frozenset(
    {
        "approval-required",
        "compatibility-failure",
        "corpus-mismatch",
        "digest-mismatch",
        "gold-visible",
        "isolation-failure",
        "network-violation",
        "plan-consumed",
        "prompt-mismatch",
        "raw-output-unretained",
        "response-schema-mismatch",
        "result-root-reuse",
        "unverified-dependency",
    }
)
CONCLUSIONS = (
    "not-executed",
    "systematic-schema-failure-established",
    "systematic-schema-failure-not-established",
    "schema-behavior-unreliable-or-unresolved",
    "diagnostic-incomplete",
    "blocked-by-unresolved-authority",
)


def placeholder_result(planned: dict[str, Any]) -> dict[str, Any]:
    """One planned run that has not been sealed."""
    return {
        "caseId": planned["caseId"],
        "category": planned["category"],
        "exitClassification": "not-executed",
        "missingRequired": [],
        "qualifyingCandidateOutputSchemaFailure": False,
        "repetition": 1,
        "responseFailureAuthority": None,
        "runId": planned["runId"],
        "schemaStatus": "not-performed",
        "sealed": False,
        "unexpectedFields": [],
    }


def classify_diagnostic(
    rows: list[dict[str, Any]],
    stop: str | None,
    *,
    planned: int = PLANNED_RUNS,
) -> dict[str, Any]:
    """Apply the precommitted threshold. Percentage gates are not calculated."""
    if len(rows) != planned:
        raise MeasurementError("run-inventory")
    sealed = [row for row in rows if row.get("sealed") is True]
    qualifying = [
        row for row in sealed if row.get("qualifyingCandidateOutputSchemaFailure") is True
    ]
    categories = {str(row["category"]) for row in qualifying}
    unresolved = [row for row in sealed if row.get("responseFailureAuthority") == "unresolved"]
    schema_valid = sum(1 for row in sealed if row.get("schemaStatus") == "valid")
    infrastructure = sum(
        1 for row in sealed if row.get("responseFailureAuthority") == "measurement-infrastructure"
    )
    threshold = systematic_threshold()
    count = len(qualifying)
    distinct = len(categories)
    met = bool(
        stop is None
        and len(sealed) == int(threshold["requiredCompletedRuns"])
        and count >= int(threshold["minimumQualifyingFailures"])
        and distinct >= int(threshold["minimumDistinctCategories"])
    )
    if len(qualifying) < 2:
        shape = "not-applicable" if sealed else "not-executed"
    else:
        shapes = {
            (tuple(row["unexpectedFields"]), tuple(row["missingRequired"])) for row in qualifying
        }
        shape = "consistent" if len(shapes) == 1 else "divergent"
    if stop in AUTHORITY_BLOCKS:
        conclusion = "blocked-by-unresolved-authority"
        met = False
    elif stop is not None or len(sealed) < planned:
        conclusion = "diagnostic-incomplete"
        met = False
    elif met:
        conclusion = "systematic-schema-failure-established"
    elif count <= 1 and not unresolved:
        conclusion = "systematic-schema-failure-not-established"
    else:
        conclusion = "schema-behavior-unreliable-or-unresolved"
    if conclusion not in CONCLUSIONS:
        raise MeasurementError("record-drift")
    return {
        "candidateOutputSchemaFailureCount": count,
        "completedRuns": len(sealed),
        "diagnosticConclusion": conclusion,
        "distinctCategoryCount": distinct,
        "infrastructureFailureCount": infrastructure,
        "missingRuns": planned - len(sealed),
        "responseShapeConsistency": shape,
        "schemaValidCount": schema_valid,
        "thresholdMet": met,
        "unresolvedCount": len(unresolved),
    }


def build_summary_template() -> dict[str, Any]:
    """Committed summary before any diagnostic run."""
    plan = load_schema_diagnostic_plan()
    rows = [placeholder_result(run) for run in plan["runs"]]
    return digest_document(
        _body(
            plan,
            rows=rows,
            conclusion="not-executed",
            stop=None,
            threshold_met=False,
            shape="not-executed",
            completed=0,
            missing=PLANNED_RUNS,
            failures=0,
            categories=0,
            schema_valid=0,
            unresolved=0,
            infrastructure=0,
        ),
        "schema-diagnostic-summary",
        "identityDigest",
    )


def load_summary_template() -> dict[str, Any]:
    """Load the committed summary and require it to match the builder."""
    loaded = json.loads((repo_root() / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_summary_template():
        raise MeasurementError("record-drift")
    return loaded


def build_summary(
    plan: dict[str, Any],
    rows: list[dict[str, Any]],
    stop: str | None,
) -> dict[str, Any]:
    """Seal one conclusion from the six-run inventory."""
    decision = classify_diagnostic(rows, stop)
    return digest_document(
        _body(
            plan,
            rows=rows,
            conclusion=str(decision["diagnosticConclusion"]),
            stop=stop,
            threshold_met=bool(decision["thresholdMet"]),
            shape=str(decision["responseShapeConsistency"]),
            completed=int(decision["completedRuns"]),
            missing=int(decision["missingRuns"]),
            failures=int(decision["candidateOutputSchemaFailureCount"]),
            categories=int(decision["distinctCategoryCount"]),
            schema_valid=int(decision["schemaValidCount"]),
            unresolved=int(decision["unresolvedCount"]),
            infrastructure=int(decision["infrastructureFailureCount"]),
        ),
        "schema-diagnostic-summary",
        "identityDigest",
    )


def _body(
    plan: dict[str, Any],
    *,
    rows: list[dict[str, Any]],
    conclusion: str,
    stop: str | None,
    threshold_met: bool,
    shape: str,
    completed: int,
    missing: int,
    failures: int,
    categories: int,
    schema_valid: int,
    unresolved: int,
    infrastructure: int,
) -> dict[str, Any]:
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        "automaticCandidateRejection": False,
        "automaticCandidateSelection": False,
        "candidateOutputSchemaFailureCount": failures,
        "completedRuns": completed,
        "diagnosticConclusion": conclusion,
        "distinctCategoryCount": categories,
        "infrastructureFailureCount": infrastructure,
        "missingRuns": missing,
        "percentageMetrics": False,
        "plannedRuns": PLANNED_RUNS,
        "promotionGateAttempt": False,
        "representsCompleteCorpus": False,
        "responseShapeConsistency": shape,
        "runResults": rows,
        "schemaValidCount": schema_valid,
        "stopCause": stop,
        "systematicThreshold": plan["systematicThreshold"],
        "thresholdMet": threshold_met,
        "unresolvedCount": unresolved,
    }
