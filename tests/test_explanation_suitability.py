"""Explanation suitability stays unresolved without measured-quality claims."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.explanation_suitability import (
    SuitabilityError,
    decide_explanation_suitability,
    load_explanation_suitability,
    suitability_outcome,
    validate_explanation_suitability,
)
from patchpilot_intelligence_evals.schemas import repo_root

_RECORD = "candidates/authorization/finalist-explanation-suitability.json"


def test_safety_gap_stays_unresolved() -> None:
    document = load_explanation_suitability()
    finalist = document["finalists"][0]
    assert finalist["suitabilityOutcome"] == "unresolved"
    assert document["measuredQualityClaimed"] is False
    topics = {item["topic"]: item["status"] for item in finalist["assessments"]}
    assert topics["safetyLimitations"] == "not-stated"
    assert topics["instructionFollowing"] == "supported"
    opened = dict(topics)
    opened["safetyLimitations"] = "stated"
    opened["citationIdReproduction"] = "supported"
    opened["refusalAndUncertainty"] = "supported"
    assert suitability_outcome(opened) == "suitable-for-offline-evaluation"
    assert suitability_outcome({**topics, "instructionFollowing": "unsupported"}) == "unsuitable"


def test_quality_claim_and_outcome_mismatch_fail() -> None:
    before = (repo_root() / _RECORD).read_bytes()
    claimed = json.loads(json.dumps(decide_explanation_suitability()))
    claimed["finalists"][0]["evidence"][0]["claim"] = (
        "The card states a measured hallucination rate for this checkpoint."
    )
    with pytest.raises(SuitabilityError) as quality_error:
        validate_explanation_suitability(claimed)
    assert quality_error.value.code == "quality-claim"
    mismatched = json.loads(json.dumps(decide_explanation_suitability()))
    mismatched["finalists"][0]["suitabilityOutcome"] = "suitable-for-offline-evaluation"
    with pytest.raises(SuitabilityError) as outcome_error:
        validate_explanation_suitability(mismatched)
    assert outcome_error.value.code == "outcome"
    assert (repo_root() / _RECORD).read_bytes() == before


def test_explanation_suitability_validation_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["finalist-explanation-suitability-validation"])
    payload = json.loads(buffer.getvalue())
    assert code == 0
    assert payload["suitabilityOutcome"] == "unresolved"
    assert payload["measuredQualityClaimed"] is False
    assert payload["productionReady"] is False
