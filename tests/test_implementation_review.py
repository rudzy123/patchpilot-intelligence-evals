"""The Track 5 review accepts the boundary and keeps acquisition withheld."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.acquisition_authorization import load_track6_authorization
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.evidence_closure import load_closure
from patchpilot_intelligence_evals.implementation_review import (
    ReviewError,
    load_review,
    validate_review,
)
from patchpilot_intelligence_evals.runtime_authorization import load_authorization


def test_review_accepts_fail_closed_outcomes(capsys: pytest.CaptureFixture[str]) -> None:
    review = load_review()
    assert review["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert review["reviewDate"] == "2026-11-10"
    assert review["reviewAuthority"] == "PatchPilot Principal Systems Architect"
    assert review["runtimeDecision"] == "no-runtime"
    assert review["candidateDecision"] == "no-selection"
    assert review["track6Authorization"] == "not-authorized"
    assert review["acquisitionStatus"] == "not-acquired"
    assert review["executionStatus"] == "not-executed"
    assert review["productionReady"] is False
    assert review["locallyObservedArtifactDigests"] == []
    assert [item["disposition"] for item in review["componentReviews"]] == [
        "approved",
        "approved",
        "approved-with-documented-limitations",
    ]
    assert [item["prerequisiteId"] for item in review["unmetPrerequisites"]] == [
        "one-qualifying-candidate",
        "one-authorized-runtime",
        "isolation-without-acquisition-blocker",
        "immutable-revision-and-source",
        "tokenizer-provenance",
        "weight-license-and-commercial-use",
        "redistribution-unnecessary",
    ]
    assert [item["prerequisiteId"] for item in review["passingPrerequisites"]] == [
        "cache-and-verification",
        "hardware-fit",
        "no-gate-change",
    ]
    assert load_authorization()["authorizationOutcome"] == "no-runtime"
    assert load_closure()["selectionOutcome"] == "no-selection"
    assert load_track6_authorization()["authorizationOutcome"] == "not-authorized"
    assert main(["track5-review-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert summary["track6Authorization"] == "not-authorized"
    assert summary["productionReady"] is False


def test_review_rejects_a_digest_that_was_not_sealed() -> None:
    document = load_review()
    document["reviewDigest"] = "0" * 64
    with pytest.raises(ReviewError, match="review-digest"):
        validate_review(document)
