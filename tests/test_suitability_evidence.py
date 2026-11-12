"""Suitability evidence tests. Official support is not measured behavior."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.suitability_contract import CAPABILITY_IDS, SAFETY_CRITICAL
from patchpilot_intelligence_evals.suitability_evidence import (
    SuitabilityEvidenceError,
    decide_suitability_evidence,
    load_suitability_evidence,
    screening_outcome,
    validate_suitability_evidence,
)


def test_screening_stays_empirical_and_unmeasured() -> None:
    document = load_suitability_evidence()
    assert document["screeningOutcome"] == "eligible-for-controlled-evaluation"
    assert document["measuredQualityClaimed"] is False
    assert document["realModelExecuted"] is False
    rows = document["capabilities"]
    assert [row["capabilityId"] for row in rows] == list(CAPABILITY_IDS)
    supported = {row["capabilityId"] for row in rows if row["result"] == "supported-in-principle"}
    assert supported == {
        "instruction-following",
        "structured-output",
        "english-language",
        "context-capacity",
    }
    for row in rows:
        if row["capabilityId"] in SAFETY_CRITICAL:
            assert row["result"] == "requires-empirical-evaluation"
            assert row["empiricalEvaluationRequired"] is True
            assert row["disqualifyingLimitation"] is False
    assert document == decide_suitability_evidence()


def test_quality_claim_and_disqualifier_fail_closed() -> None:
    claimed = json.loads(json.dumps(decide_suitability_evidence()))
    claimed["evidence"][0]["claim"] = (
        "The card states a measured hallucination rate for this model."
    )
    with pytest.raises(SuitabilityEvidenceError) as quality:
        validate_suitability_evidence(claimed)
    assert quality.value.code == "quality-claim"
    rows = json.loads(json.dumps(decide_suitability_evidence()["capabilities"]))
    rows[5]["result"] = "unsupported"
    rows[5]["disqualifyingLimitation"] = True
    assert screening_outcome(rows) == "disqualified"
