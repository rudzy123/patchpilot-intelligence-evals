"""Closeout for one six-run diagnostic. It does not select a candidate."""

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
)
from patchpilot_intelligence_evals.schema_diagnostic_summary import build_summary_template
from patchpilot_intelligence_evals.schemas import repo_root

_TEMPLATE = Path("candidates/templates/schema-diagnostic-closeout-template.json")


def build_closeout_template() -> dict[str, Any]:
    """Committed closeout before execution."""
    plan = load_schema_diagnostic_plan()
    summary = build_summary_template()
    return digest_document(
        _body(
            plan,
            summary,
            state="not-closed",
            cleanup="not-performed",
            retention="not-performed",
            blocker="not-executed",
        ),
        "schema-diagnostic-closeout",
        "identityDigest",
    )


def load_closeout_template() -> dict[str, Any]:
    """Load the committed closeout and require it to match the builder."""
    loaded = json.loads((repo_root() / _TEMPLATE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict) or loaded != build_closeout_template():
        raise MeasurementError("record-drift")
    return loaded


def build_closeout(
    plan: dict[str, Any],
    summary: dict[str, Any],
    stop: str | None,
    *,
    cleanup: str,
    retention: str,
) -> dict[str, Any]:
    """Seal the diagnostic closeout from the summary."""
    conclusion = str(summary["diagnosticConclusion"])
    if conclusion == "not-executed":
        state = "not-closed"
        blocker = "not-executed"
    elif stop is None and int(summary["completedRuns"]) == PLANNED_RUNS:
        state = "closed"
        blocker = "none"
    else:
        state = "stopped"
        blocker = stop if stop is not None else "none"
    return digest_document(
        _body(plan, summary, state=state, cleanup=cleanup, retention=retention, blocker=blocker),
        "schema-diagnostic-closeout",
        "identityDigest",
    )


def _body(
    plan: dict[str, Any],
    summary: dict[str, Any],
    *,
    state: str,
    cleanup: str,
    retention: str,
    blocker: str,
) -> dict[str, Any]:
    return {
        **identity_fields(plan),
        **artifact_pins(plan),
        "automaticCandidateRejection": False,
        "automaticCandidateSelection": False,
        "blocker": blocker,
        "cleanup": cleanup,
        "closeoutState": state,
        "completedRuns": summary["completedRuns"],
        "diagnosticConclusion": summary["diagnosticConclusion"],
        "missingRuns": summary["missingRuns"],
        "percentageMetrics": False,
        "plannedRuns": PLANNED_RUNS,
        "promotionGateAttempt": False,
        "representsCompleteCorpus": False,
        "retention": retention,
        "stopCause": summary["stopCause"],
        "thresholdMet": summary["thresholdMet"],
    }
