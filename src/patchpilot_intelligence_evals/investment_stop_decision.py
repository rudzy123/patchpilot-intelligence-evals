"""Investment-stop decision. Stopping would be a program choice, and it is not selected."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.track10_review import (
    SELECTED_TRACK,
    common,
    decision_for,
    load_record,
    require_session_decision,
    seal,
)

SCHEMA_NAME = "investment-stop-decision"
_RECORD = "candidates/authorization/investment-stop-decision.json"


def require_investment_stop(document: dict[str, Any]) -> None:
    """Keep the stop unselected and outside any candidate-quality verdict."""
    require_session_decision(document)
    if document["stopSelected"] is not False:
        raise MeasurementError("stop-selected")
    if document["stopIsQualityVerdict"] is not False:
        raise MeasurementError("quality-verdict")
    if document["candidateFailureIndependentlyProven"] is not False:
        raise MeasurementError("unsupported-rejection")
    if document["memoryIsRejectionBasis"] is not False:
        raise MeasurementError("memory-rejection")
    if document["recommendation"] != "continue-only-six-run-in-principle":
        raise MeasurementError("recommendation")
    if document["expectedSixRunEvidenceValue"] != "decision-grade-for-schema-behavior":
        raise MeasurementError("evidence-value")
    if document["opportunityCostOfStopping"] != "forgoes-narrow-schema-question":
        raise MeasurementError("opportunity-cost")
    if document["anotherInfrastructureFailureConsequence"] != "little-new-candidate-evidence":
        raise MeasurementError("failure-consequence")
    if document["memoryHeadroom"] != "limited-ceiling-passed":
        raise MeasurementError("memory-headroom")
    if document["candidateRole"] != "non-authoritative-explanation-assistant":
        raise MeasurementError("candidate-role")
    if document["infrastructureMaturity"] != "telemetry-corrected-with-historical-stops":
        raise MeasurementError("infrastructure-maturity")
    if document["sixRunResourceCost"] != "six-run":
        raise MeasurementError("resource-cost")
    if document["fullCorpusResourceCost"] != "full-corpus":
        raise MeasurementError("resource-cost")


def build_investment_stop_body() -> dict[str, Any]:
    """Build the unsigned investment-stop body."""
    document = {
        **common(),
        **decision_for(SELECTED_TRACK),
        "anotherInfrastructureFailureConsequence": "little-new-candidate-evidence",
        "candidateFailureIndependentlyProven": False,
        "candidateRole": "non-authoritative-explanation-assistant",
        "expectedSixRunEvidenceValue": "decision-grade-for-schema-behavior",
        "fullCorpusResourceCost": "full-corpus",
        "infrastructureMaturity": "telemetry-corrected-with-historical-stops",
        "memoryHeadroom": "limited-ceiling-passed",
        "memoryIsRejectionBasis": False,
        "opportunityCostOfStopping": "forgoes-narrow-schema-question",
        "recommendation": "continue-only-six-run-in-principle",
        "sixRunResourceCost": "six-run",
        "stopIsQualityVerdict": False,
        "stopSelected": False,
    }
    require_investment_stop(document)
    return document


def build_investment_stop() -> dict[str, Any]:
    """Seal the committed investment-stop record."""
    return seal(build_investment_stop_body(), SCHEMA_NAME)


def load_investment_stop() -> dict[str, Any]:
    """Return the committed investment-stop record."""
    return load_record(_RECORD, build_investment_stop)
