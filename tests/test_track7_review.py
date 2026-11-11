"""The Track 7 review approves the landscape and withholds acquisition."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.track7_review import (
    Track7ReviewError,
    load_track7_review,
    validate_track7_review,
)

_RECORD = "candidates/authorization/track7-implementation-review.json"


def test_review_seals_the_fail_closed_decision() -> None:
    review = load_track7_review()
    assert review["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert review["reviewDate"] == "2026-11-11"
    assert review["reviewAuthority"] == "PatchPilot Principal Systems Architect"
    assert review["landscapeDisposition"] == "approved"
    assert review["candidateDecision"] == "no-selection"
    assert review["track8Authorization"] == "not-authorized"
    assert review["selectionOutcome"] == "no-selection"
    assert review["weightedScore"] is None
    assert review["qualifyingCandidateCount"] == 0
    assert review["peakMemoryBytes"] is None
    assert review["footprintBytes"] == 9_446_591_609
    assert review["artifactCapBytes"] == 8_589_934_592
    assert review["excessBytes"] == 856_657_017
    assert review["reviewDigest"] == review_digest(review)
    assert review["productionReady"] is False
    assert review["locallyObservedArtifactDigests"] == []
    assert [item["blockerId"] for item in review["acceptedBlockers"]] == [
        "footprint-exceeds-8gib",
        "fp32-peak-memory-unknown",
        "explanation-suitability-unresolved",
        "safety-limitations-unresolved",
        "mandatory-criteria-unmet",
    ]


def test_digest_mutation_fails_closed() -> None:
    before = (repo_root() / _RECORD).read_bytes()
    mutated = json.loads(json.dumps(load_track7_review()))
    mutated["reviewDigest"] = "0" * 64
    with pytest.raises(Track7ReviewError) as caught:
        validate_track7_review(mutated)
    assert caught.value.code == "review-digest"
    assert (repo_root() / _RECORD).read_bytes() == before


def test_track7_review_validation_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["track7-review-validation"])
    payload = json.loads(buffer.getvalue())
    assert code == 0
    assert payload["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert payload["candidateDecision"] == "no-selection"
    assert payload["track8Authorization"] == "not-authorized"
    assert payload["productionReady"] is False
