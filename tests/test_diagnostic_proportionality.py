"""Diagnostic proportionality tests."""

import pytest

from patchpilot_intelligence_evals.diagnostic_proportionality import (
    SCHEMA_NAME,
    build_diagnostic_proportionality,
    build_proportionality_body,
    load_diagnostic_proportionality,
    require_proportionality,
)
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schemas import SchemaValidationError, validate
from patchpilot_intelligence_evals.track10_review import DECISION_ALTERNATIVES


def test_six_run_is_the_only_selected_alternative() -> None:
    document = load_diagnostic_proportionality()
    assert document == build_diagnostic_proportionality()
    assert tuple(row["alternativeId"] for row in document["alternatives"]) == DECISION_ALTERNATIVES
    selected = [row for row in document["alternatives"] if row["selected"] is True]
    assert len(selected) == 1
    assert selected[0]["alternativeId"] == "six-run-diagnostic"
    assert selected[0]["evidenceValue"] == "decision-grade-for-schema-behavior"
    assert selected[0]["resourceCost"] == "six-run"
    assert selected[0]["qualityVerdict"] is False
    by_id = {row["alternativeId"]: row for row in document["alternatives"]}
    assert by_id["reject-now"]["eligible"] is False
    assert by_id["reject-now"]["disqualifier"] == "no-supported-mandatory-failure"
    assert by_id["full-72-run-continuation"]["selected"] is False
    assert by_id["full-72-run-continuation"]["evidenceValue"] == "complete-metrics-only"
    assert by_id["full-72-run-continuation"]["resourceCost"] == "full-corpus"
    assert by_id["protocol-forensics"]["eligible"] is False
    assert by_id["stop-investment"]["eligible"] is True
    assert by_id["stop-investment"]["selected"] is False
    assert document["mandatoryFailureSupported"] is False
    assert document["sixRunPrecedesFullRerun"] is True
    assert document["fullCorpusSelected"] is False
    assert document["proportionalityJudgment"] == "six-run-proportionate"
    assert all(row["securityRisk"] == "unchanged" for row in document["alternatives"])


def test_two_selected_alternatives_are_rejected() -> None:
    document = build_proportionality_body()
    document["alternatives"][4]["selected"] = True
    with pytest.raises(MeasurementError) as caught:
        require_proportionality(document)
    assert caught.value.code == "alternatives"


def test_numeric_cost_claim_is_rejected() -> None:
    document = build_diagnostic_proportionality()
    document["wallClockHours"] = 12
    with pytest.raises(SchemaValidationError):
        validate(SCHEMA_NAME, document)
