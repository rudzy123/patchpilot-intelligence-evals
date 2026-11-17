"""Track 9 proportionality decision. Categories stay closed. Run is not called."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.track9_review import common, load_record, seal

SCHEMA_NAME = "proportionality-decision"
_RECORD = "candidates/authorization/proportionality-decision.json"
SELECTED_ALTERNATIVE = "clean-24-case-corpus-only-rerun"
_UNCHANGED = (
    "artifactsUnchanged",
    "gatesUnchanged",
    "metricsUnchanged",
    "promptsUnchanged",
    "responseSchemaUnchanged",
)
_ALTERNATIVES: tuple[dict[str, Any], ...] = (
    {
        "alternativeId": "reject-now",
        "comparability": "not-applicable",
        "decisionValue": "none",
        "disqualifiers": ["absence-of-evidence-is-not-mandatory-failure"],
        "eligible": False,
        "estimatedRuns": 0,
        "evidenceValue": "insufficient",
        "executionScope": "none",
        "infrastructureRisk": "repeated-stop-history",
        "qualityVerdict": False,
        "resourceCost": "none",
        "securityRisk": "unchanged",
        "selected": False,
    },
    {
        "alternativeId": "remaining-19",
        "comparability": "mixed-incomparable",
        "decisionValue": "partial",
        "disqualifiers": ["comparison-requires-complete-uniform-result"],
        "eligible": False,
        "estimatedRuns": 57,
        "evidenceValue": "insufficient",
        "executionScope": "remaining-19",
        "infrastructureRisk": "repeated-stop-history",
        "qualityVerdict": False,
        "resourceCost": "mixed-corpus",
        "securityRisk": "unchanged",
        "selected": False,
    },
    {
        "alternativeId": SELECTED_ALTERNATIVE,
        "comparability": "uniform",
        "decisionValue": "decision-grade",
        "disqualifiers": [],
        "eligible": True,
        "estimatedRuns": 72,
        "evidenceValue": "decision-grade",
        "executionScope": "corpus-24",
        "infrastructureRisk": "residual",
        "qualityVerdict": False,
        "resourceCost": "bounded-corpus-only",
        "securityRisk": "unchanged",
        "selected": True,
    },
    {
        "alternativeId": "narrow-forensics",
        "comparability": "not-applicable",
        "decisionValue": "none",
        "disqualifiers": ["raw-output-not-recoverable-by-analysis"],
        "eligible": False,
        "estimatedRuns": 0,
        "evidenceValue": "insufficient",
        "executionScope": "analysis-only",
        "infrastructureRisk": "none",
        "qualityVerdict": False,
        "resourceCost": "none",
        "securityRisk": "unchanged",
        "selected": False,
    },
    {
        "alternativeId": "stop-investment",
        "comparability": "not-applicable",
        "decisionValue": "none",
        "disqualifiers": [],
        "eligible": True,
        "estimatedRuns": 0,
        "evidenceValue": "insufficient",
        "executionScope": "none",
        "infrastructureRisk": "repeated-stop-history",
        "qualityVerdict": False,
        "resourceCost": "none",
        "securityRisk": "unchanged",
        "selected": False,
    },
)


def alternatives() -> list[dict[str, Any]]:
    """Return the five closed alternatives in decision order."""
    return [dict(row) for row in _ALTERNATIVES]


def reject_contract_change(flags: dict[str, bool]) -> None:
    """A continuation that changes the corpus contract is refused."""
    for name in _UNCHANGED:
        if flags[name] is not True:
            raise MeasurementError("continuation-boundary")


def require_proportionality(document: dict[str, Any]) -> None:
    """Require one selected clean rerun and the recorded disqualifiers."""
    rows = document["alternatives"]
    if [row["alternativeId"] for row in rows] != [row["alternativeId"] for row in _ALTERNATIVES]:
        raise MeasurementError("proportionality-selection")
    selected = [row["alternativeId"] for row in rows if row["selected"]]
    if selected != [document["selectedAlternative"]]:
        raise MeasurementError("proportionality-selection")
    if document["selectedAlternative"] != SELECTED_ALTERNATIVE:
        raise MeasurementError("proportionality-selection")
    if document["mandatoryFailureSupported"] is not False:
        raise MeasurementError("proportionality-selection")
    if document["contractChangesPermitted"] is not False:
        raise MeasurementError("continuation-boundary")
    if document["proportionalityJudgment"] != "proportionate":
        raise MeasurementError("proportionality-selection")
    expected = {row["alternativeId"]: row for row in _ALTERNATIVES}
    for row in rows:
        source = expected[row["alternativeId"]]
        if row != source:
            raise MeasurementError("proportionality-selection")
    stop = expected["stop-investment"]
    if stop["eligible"] is not True or stop["selected"] is not False:
        raise MeasurementError("proportionality-selection")
    if stop["qualityVerdict"] is not False:
        raise MeasurementError("proportionality-selection")


def build_proportionality_decision() -> dict[str, Any]:
    """Select the clean 24-case rerun. Stopping stays eligible and unselected."""
    document = {
        **common(),
        "alternatives": alternatives(),
        "contractChangesPermitted": False,
        "mandatoryFailureSupported": False,
        "proportionalityJudgment": "proportionate",
        "selectedAlternative": SELECTED_ALTERNATIVE,
    }
    require_proportionality(document)
    return seal(document, SCHEMA_NAME)


def load_proportionality_decision() -> dict[str, Any]:
    """Return the committed proportionality decision."""
    return load_record(_RECORD, build_proportionality_decision)
