"""The Track 7A review approves the storage model and withholds acquisition."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.track7a_review import (
    Track7AReviewError,
    load_track7a_review,
    validate_track7a_review,
)

_RECORD = "candidates/authorization/track7a-implementation-review.json"


def test_review_seals_the_storage_decision() -> None:
    review = load_track7a_review()
    assert review["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert review["reviewDate"] == "2026-11-12"
    assert review["reviewAuthority"] == "PatchPilot Principal Systems Architect"
    assert review["artifactStoragePolicy"] == "approved"
    assert review["verificationSealing"] == "approved"
    assert review["mutationDetection"] == "approved"
    assert review["atomicPromotion"] == "approved-with-documented-residuals"
    assert review["copyPromotion"] == "failed"
    assert review["crossFilesystemPromotion"] == "ineligible"
    assert review["copyFallback"] == "prohibited"
    assert review["ceilingUnchanged"] is True
    assert review["artifactCapBytes"] == 8_589_934_592
    assert review["logicalInventoryBytes"] == 4_717_588_977
    assert review["verificationWorkingOverheadBytes"] == 1_228_800
    assert review["runtimeStagingListedBytes"] == 11_413_655
    assert review["copyPromotionPeakBytes"] == 9_447_820_409
    assert review["copyPromotionExcessBytes"] == 857_885_817
    assert review["atomicPromotionPeakBytes"] == 4_730_231_432
    assert review["atomicPromotionHeadroomBytes"] == 3_859_703_160
    assert review["storageOnlyBlocker"] == "resolved"
    assert review["candidateDecision"] == "no-selection"
    assert review["track8Authorization"] == "not-authorized"
    assert review["selectionOutcome"] == "no-selection"
    assert review["authorizationOutcome"] == "not-authorized"
    assert review["weightedScore"] is None
    assert review["qualifyingCandidateCount"] == 0
    assert review["peakMemoryBasis"] == "unknown-fp32"
    assert review["explanationSuitability"] == "unresolved"
    assert review["readinessOutcome"] == "not-ready"
    assert review["runtimeInstallationStatus"] == "not-installed"
    assert review["acquisitionStatus"] == "not-acquired"
    assert review["conversionStatus"] == "not-performed"
    assert review["executionStatus"] == "not-executed"
    assert review["realModelExecuted"] is False
    assert review["productionReady"] is False
    assert review["locallyObservedArtifactDigests"] == []
    assert review["reviewDigest"] == review_digest(review)
    assert [item["residualId"] for item in review["acceptedResiduals"]] == [
        "one-proven-filesystem",
        "cross-device-ineligible",
        "no-copy-and-delete-fallback",
        "post-rename-recovery-proof",
        "inconsistent-verified-evidence",
        "verified-mutation-without-kernel-immutability",
        "transient-acquisition-overhead-unknown",
        "no-real-model-artifact",
        "fp32-peak-memory-unresolved",
        "explanation-suitability-unresolved",
    ]


def test_digest_mutation_fails_closed() -> None:
    before = (repo_root() / _RECORD).read_bytes()
    mutated = json.loads(json.dumps(load_track7a_review()))
    mutated["reviewDigest"] = "0" * 64
    with pytest.raises(Track7AReviewError) as caught:
        validate_track7a_review(mutated)
    assert caught.value.code == "review-digest"
    assert (repo_root() / _RECORD).read_bytes() == before


def test_track7a_review_validation_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["track7a-review-validation"])
    payload = json.loads(buffer.getvalue())
    assert code == 0
    assert payload["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert payload["storageOnlyBlocker"] == "resolved"
    assert payload["candidateDecision"] == "no-selection"
    assert payload["track8Authorization"] == "not-authorized"
    assert payload["reviewDigest"] == load_track7a_review()["reviewDigest"]
    assert payload["productionReady"] is False
