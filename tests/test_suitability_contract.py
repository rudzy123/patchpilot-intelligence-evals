"""Suitability contract coverage tests."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.metrics import METRIC_NAMES
from patchpilot_intelligence_evals.suitability_contract import (
    CAPABILITY_IDS,
    SAFETY_CRITICAL,
    SuitabilityContractError,
    decide_suitability_contract,
    load_suitability_contract,
    validate_suitability_contract,
)


def test_contract_maps_existing_metrics_and_requires_empirical_safety() -> None:
    document = load_suitability_contract()
    rows = document["capabilities"]
    assert [row["capabilityId"] for row in rows] == list(CAPABILITY_IDS)
    assert len({row["capabilityId"] for row in rows}) == 14
    assert document["gatesUnchanged"] is True
    assert document["measuredQualityClaimed"] is False
    metrics = {row["metricName"] for row in rows if row["metricName"] is not None}
    assert metrics <= set(METRIC_NAMES)
    assert all(
        row["empiricalEvaluationRequired"] is True
        for row in rows
        if row["capabilityId"] in SAFETY_CRITICAL
    )
    english = next(row for row in rows if row["capabilityId"] == "english-language")
    assert english["metricName"] is None
    assert english["passAuthority"] == "official-statement"
    missing = next(row for row in rows if row["capabilityId"] == "missing-evidence-reporting")
    assert missing["metricName"] is None
    assert "insufficient-evidence-refusal" in missing["corpusCategories"]
    assert document == decide_suitability_contract()


def test_unknown_metric_and_waived_safety_fail() -> None:
    unknown = json.loads(json.dumps(decide_suitability_contract()))
    unknown["capabilities"][0]["metricName"] = "hallucinationRate"
    with pytest.raises(SuitabilityContractError) as metric:
        validate_suitability_contract(unknown)
    assert metric.value.code == "metric"
    waived = json.loads(json.dumps(decide_suitability_contract()))
    waived["capabilities"][5]["empiricalEvaluationRequired"] = False
    with pytest.raises(SuitabilityContractError) as empirical:
        validate_suitability_contract(waived)
    assert empirical.value.code == "empirical-required"
    claimed = json.loads(json.dumps(decide_suitability_contract()))
    claimed["capabilities"][0]["disqualifyingLimitationRule"] = (
        "The card states a measured hallucination rate for this capability."
    )
    with pytest.raises(SuitabilityContractError) as quality:
        validate_suitability_contract(claimed)
    assert quality.value.code == "quality-claim"
