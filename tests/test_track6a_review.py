"""The Track 6A review accepts the boundary and keeps acquisition withheld."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.acquisition_authorization import load_track6_authorization
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.evidence_closure import load_closure
from patchpilot_intelligence_evals.implementation_review import load_review as load_track5_review
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.runtime_security import load_authorization
from patchpilot_intelligence_evals.track6a_review import (
    Track6AReviewError,
    load_review,
    validate_review,
)


def test_review_accepts_the_hardened_boundary(capsys: pytest.CaptureFixture[str]) -> None:
    review = load_review()
    assert review["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert review["reviewDate"] == "2026-11-10"
    assert review["reviewAuthority"] == "PatchPilot Principal Systems Architect"
    assert review["decision"] == "hardened execution boundary approved with documented residuals"
    assert review["profileId"] == "linux-bwrap-systemd-v1"
    assert review["profileVersion"] == "1.0.0"
    assert review["runtimeId"] == "onnxruntime"
    assert review["versionTag"] == "v1.31.1"
    assert review["installationAuthorized"] is False
    assert review["installedDuringSession"] is False
    assert review["candidateFormatGap"] is True
    assert review["candidateDecision"] == "no-selection"
    assert review["track6Authorization"] == "not-authorized"
    assert review["acquisitionStatus"] == "not-acquired"
    assert review["executionStatus"] == "not-executed"
    assert review["realModelExecuted"] is False
    assert review["productionReady"] is False
    assert review["locallyObservedArtifactDigests"] == []
    assert review["reviewDigest"] == review_digest(review)
    assert "next controlled architectural Session" in review["readinessMeaning"]
    assert review["notAuthorized"] == [
        "runtime installation",
        "model or tokenizer acquisition",
        "model conversion",
        "candidate selection",
        "real inference",
        "evaluation-gate changes",
        "shadow mode",
        "PatchPilot production composition",
    ]
    assert [item["controlId"] for item in review["acceptedControls"][:7]] == [
        "user-namespace",
        "mount-namespace",
        "pid-namespace",
        "network-namespace",
        "ipc-namespace",
        "uts-namespace",
        "cgroup-namespace",
    ]
    assert review["acceptedControls"][-1]["controlId"] == "no-shell"
    assert "candidate-format-gap" in [item["residualId"] for item in review["acceptedResiduals"]]
    assert load_authorization()["installationAuthorized"] is False
    assert load_authorization()["installedDuringSession"] is False
    assert load_closure()["selectionOutcome"] == "no-selection"
    assert load_track6_authorization()["authorizationOutcome"] == "not-authorized"
    assert load_track5_review()["runtimeDecision"] == "no-runtime"
    assert load_track5_review()["track6Authorization"] == "not-authorized"
    assert main(["track6a-review-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert summary["installationAuthorized"] is False
    assert summary["candidateDecision"] == "no-selection"
    assert summary["track6Authorization"] == "not-authorized"
    assert summary["realModelExecuted"] is False
    assert summary["productionReady"] is False


def test_review_rejects_a_digest_that_was_not_sealed() -> None:
    document = load_review()
    document["reviewDigest"] = "0" * 64
    with pytest.raises(Track6AReviewError, match="review-digest"):
        validate_review(document)
