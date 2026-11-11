"""Finalist license applicability, revision pins, and null scores."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.finalist_eligibility import (
    FinalistEligibilityError,
    decide_finalist_eligibility,
    load_finalist_eligibility,
    validate_finalist_eligibility,
)
from patchpilot_intelligence_evals.schemas import repo_root

_RECORD = "candidates/authorization/finalist-eligibility.json"


def _bytes() -> bytes:
    return (repo_root() / _RECORD).read_bytes()


def test_finalist_fails_only_local_resource_fit() -> None:
    document = load_finalist_eligibility()
    finalist = document["finalists"][0]
    assert document["finalistCount"] == 1
    assert finalist["commercialGrant"] == "restricted"
    assert finalist["commercialUseResult"] == "pass"
    assert finalist["weightedScore"] is None
    assert finalist["categoryScores"] is None
    assert finalist["scoringEligible"] is False
    assert finalist["disqualifiers"] == ["local-resource-fit"]
    assert finalist["unresolvedConflict"] is True
    assert document["productionReady"] is False
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["executionStatus"] == "not-executed"
    assert document["realModelExecuted"] is False


def test_inapplicable_license_and_revision_fail_closed() -> None:
    before = _bytes()
    scored = json.loads(json.dumps(decide_finalist_eligibility()))
    scored["finalists"][0]["weightedScore"] = 10
    with pytest.raises(FinalistEligibilityError) as score_error:
        validate_finalist_eligibility(scored)
    assert score_error.value.code == "weighted-score"
    assumed = json.loads(json.dumps(decide_finalist_eligibility()))
    assumed["finalists"][0]["licenseInstrument"] = "assumed-from-model-license"
    with pytest.raises(FinalistEligibilityError) as license_error:
        validate_finalist_eligibility(assumed)
    assert license_error.value.code == "mandatory-criteria"
    shifted = json.loads(json.dumps(decide_finalist_eligibility()))
    shifted["finalists"][0]["evidence"][0]["immutableRevision"] = "b" * 40
    with pytest.raises(FinalistEligibilityError) as revision_error:
        validate_finalist_eligibility(shifted)
    assert revision_error.value.code == "revision"
    assert _bytes() == before


def test_finalist_eligibility_validation_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["finalist-eligibility-validation"])
    payload = json.loads(buffer.getvalue())
    assert code == 0
    assert payload["finalistCount"] == 1
    assert payload["weightedScore"] is None
    assert payload["mandatoryStatus"] == "fail"
    assert payload["productionReady"] is False
