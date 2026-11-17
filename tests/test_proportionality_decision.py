"""Track 9 proportionality tests."""

import pytest

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.proportionality_decision import (
    SELECTED_ALTERNATIVE,
    build_proportionality_decision,
    load_proportionality_decision,
    reject_contract_change,
    require_proportionality,
)
from patchpilot_intelligence_evals.schemas import SchemaValidationError, validate


def test_clean_rerun_is_the_only_selected_alternative() -> None:
    document = load_proportionality_decision()
    assert document == build_proportionality_decision()
    assert document["selectedAlternative"] == SELECTED_ALTERNATIVE
    assert document["proportionalityJudgment"] == "proportionate"
    assert document["mandatoryFailureSupported"] is False
    assert document["contractChangesPermitted"] is False
    selected = [row for row in document["alternatives"] if row["selected"]]
    assert [row["alternativeId"] for row in selected] == [SELECTED_ALTERNATIVE]
    by_id = {row["alternativeId"]: row for row in document["alternatives"]}
    assert by_id["reject-now"]["disqualifiers"] == ["absence-of-evidence-is-not-mandatory-failure"]
    assert by_id["reject-now"]["eligible"] is False
    assert by_id["remaining-19"]["estimatedRuns"] == 57
    assert by_id["remaining-19"]["comparability"] == "mixed-incomparable"
    assert by_id["remaining-19"]["disqualifiers"] == ["comparison-requires-complete-uniform-result"]
    assert by_id[SELECTED_ALTERNATIVE]["estimatedRuns"] == 72
    assert by_id[SELECTED_ALTERNATIVE]["comparability"] == "uniform"
    assert by_id[SELECTED_ALTERNATIVE]["resourceCost"] == "bounded-corpus-only"
    assert by_id[SELECTED_ALTERNATIVE]["executionScope"] == "corpus-24"
    assert by_id[SELECTED_ALTERNATIVE]["disqualifiers"] == []
    assert by_id["narrow-forensics"]["disqualifiers"] == ["raw-output-not-recoverable-by-analysis"]
    assert by_id["narrow-forensics"]["executionScope"] == "analysis-only"
    assert by_id["stop-investment"]["eligible"] is True
    assert by_id["stop-investment"]["selected"] is False
    assert by_id["stop-investment"]["qualityVerdict"] is False
    assert by_id["stop-investment"]["estimatedRuns"] == 0
    assert document["comparisonWinner"] is None
    assert document["productionReady"] is False


def test_changed_contract_is_rejected() -> None:
    flags = {
        "artifactsUnchanged": True,
        "gatesUnchanged": True,
        "metricsUnchanged": True,
        "promptsUnchanged": True,
        "responseSchemaUnchanged": True,
    }
    reject_contract_change(flags)
    for name in flags:
        changed = dict(flags)
        changed[name] = False
        with pytest.raises(MeasurementError) as caught:
            reject_contract_change(changed)
        assert caught.value.code == "continuation-boundary"


def test_a_second_selected_alternative_is_rejected() -> None:
    document = build_proportionality_decision()
    document["alternatives"][0]["selected"] = True
    with pytest.raises(MeasurementError) as caught:
        require_proportionality(document)
    assert caught.value.code == "proportionality-selection"


def test_schema_rejects_an_unlisted_run_count() -> None:
    document = build_proportionality_decision()
    document["alternatives"][2]["estimatedRuns"] = 19
    with pytest.raises(SchemaValidationError):
        validate("proportionality-decision", document)
