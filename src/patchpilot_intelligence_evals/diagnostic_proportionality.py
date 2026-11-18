"""Diagnostic proportionality. Closed categories only. This record does not call Run."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.track10_review import (
    DECISION_ALTERNATIVES,
    SELECTED_ALTERNATIVE,
    SELECTED_TRACK,
    common,
    decision_for,
    load_record,
    require_session_decision,
    seal,
)

SCHEMA_NAME = "diagnostic-proportionality"
_RECORD = "candidates/authorization/diagnostic-proportionality.json"


def _row(
    alternative_id: str,
    *,
    eligible: bool,
    selected: bool,
    estimated_runs: str,
    evidence_value: str,
    resource_cost: str,
    decision_value: str,
    infrastructure_risk: str,
    memory_fit: str,
    comparability: str,
    another_failure: str,
    disqualifier: str,
) -> dict[str, Any]:
    return {
        "alternativeId": alternative_id,
        "anotherFailureConsequence": another_failure,
        "comparability": comparability,
        "decisionValue": decision_value,
        "disqualifier": disqualifier,
        "eligible": eligible,
        "estimatedRuns": estimated_runs,
        "evidenceValue": evidence_value,
        "infrastructureRisk": infrastructure_risk,
        "memoryFit": memory_fit,
        "qualityVerdict": False,
        "resourceCost": resource_cost,
        "securityRisk": "unchanged",
        "selected": selected,
    }


def alternative_rows() -> list[dict[str, Any]]:
    """Return the five closed alternatives. Only the six-run row is selected."""
    return [
        _row(
            "reject-now",
            eligible=False,
            selected=False,
            estimated_runs="none",
            evidence_value="insufficient",
            resource_cost="none",
            decision_value="none",
            infrastructure_risk="none",
            memory_fit="not-applicable",
            comparability="not-applicable",
            another_failure="not-applicable",
            disqualifier="no-supported-mandatory-failure",
        ),
        _row(
            "six-run-diagnostic",
            eligible=True,
            selected=True,
            estimated_runs="six-run",
            evidence_value="decision-grade-for-schema-behavior",
            resource_cost="six-run",
            decision_value="decision-grade-for-schema-behavior",
            infrastructure_risk="residual",
            memory_fit="within-ceiling-limited-headroom",
            comparability="preserved-protocol",
            another_failure="little-new-candidate-evidence",
            disqualifier="none",
        ),
        _row(
            "full-72-run-continuation",
            eligible=True,
            selected=False,
            estimated_runs="full-corpus",
            evidence_value="complete-metrics-only",
            resource_cost="full-corpus",
            decision_value="promotion-metrics",
            infrastructure_risk="repeated-stop-history",
            memory_fit="within-ceiling-limited-headroom",
            comparability="preserved-protocol",
            another_failure="repeated-corpus-loss",
            disqualifier="disproportionate-to-narrow-uncertainty",
        ),
        _row(
            "protocol-forensics",
            eligible=False,
            selected=False,
            estimated_runs="none",
            evidence_value="insufficient",
            resource_cost="none",
            decision_value="none",
            infrastructure_risk="none",
            memory_fit="not-applicable",
            comparability="not-applicable",
            another_failure="not-applicable",
            disqualifier="adapter-prompt-parser-evaluator-already-proven",
        ),
        _row(
            "stop-investment",
            eligible=True,
            selected=False,
            estimated_runs="none",
            evidence_value="insufficient",
            resource_cost="none",
            decision_value="none",
            infrastructure_risk="repeated-stop-history",
            memory_fit="within-ceiling-limited-headroom",
            comparability="not-applicable",
            another_failure="little-new-candidate-evidence",
            disqualifier="none",
        ),
    ]


def require_proportionality(document: dict[str, Any]) -> None:
    """Require one selected alternative and no quality verdict."""
    require_session_decision(document)
    rows = document["alternatives"]
    if tuple(row["alternativeId"] for row in rows) != DECISION_ALTERNATIVES:
        raise MeasurementError("alternatives")
    selected = [row for row in rows if row["selected"] is True]
    if len(selected) != 1:
        raise MeasurementError("alternatives")
    if selected[0]["alternativeId"] != document["selectedAlternative"]:
        raise MeasurementError("alternatives")
    if selected[0]["alternativeId"] != SELECTED_ALTERNATIVE:
        raise MeasurementError("alternatives")
    if any(row["qualityVerdict"] is not False for row in rows):
        raise MeasurementError("quality-verdict")
    by_id = {row["alternativeId"]: row for row in rows}
    if by_id["reject-now"]["eligible"] is not False:
        raise MeasurementError("unsupported-rejection")
    if by_id["protocol-forensics"]["eligible"] is not False:
        raise MeasurementError("forensics-eligible")
    if by_id["full-72-run-continuation"]["selected"] is not False:
        raise MeasurementError("full-corpus-selected")
    if by_id["stop-investment"]["selected"] is not False:
        raise MeasurementError("stop-selected")
    if by_id["stop-investment"]["eligible"] is not True:
        raise MeasurementError("stop-eligibility")
    if document["mandatoryFailureSupported"] is not False:
        raise MeasurementError("unsupported-rejection")
    if document["sixRunPrecedesFullRerun"] is not True:
        raise MeasurementError("proportionality")
    if document["fullCorpusSelected"] is not False:
        raise MeasurementError("full-corpus-selected")
    if document["contractChangesPermitted"] is not False:
        raise MeasurementError("contract-change")
    if document["proportionalityJudgment"] != "six-run-proportionate":
        raise MeasurementError("proportionality")


def build_proportionality_body() -> dict[str, Any]:
    """Build the unsigned proportionality body."""
    document = {
        **common(),
        **decision_for(SELECTED_TRACK),
        "alternatives": alternative_rows(),
        "contractChangesPermitted": False,
        "fullCorpusSelected": False,
        "mandatoryFailureSupported": False,
        "proportionalityJudgment": "six-run-proportionate",
        "sixRunPrecedesFullRerun": True,
    }
    require_proportionality(document)
    return document


def build_diagnostic_proportionality() -> dict[str, Any]:
    """Seal the committed proportionality record."""
    return seal(build_proportionality_body(), SCHEMA_NAME)


def load_diagnostic_proportionality() -> dict[str, Any]:
    """Return the committed proportionality record."""
    return load_record(_RECORD, build_diagnostic_proportionality)
