"""The Track 7B review approves the evidence closure and withholds execution."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.track7b_review import (
    Track7BReviewError,
    load_track7b_review,
    validate_track7b_review,
)

_RECORD = "candidates/authorization/track7b-implementation-review.json"


def test_review_seals_the_evidence_decision() -> None:
    review = load_track7b_review()
    assert review["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert review["reviewDate"] == "2026-11-12"
    assert review["reviewAuthority"] == "PatchPilot Principal Systems Architect"
    assert review["memoryModelContract"] == "approved"
    assert review["officialMemoryEvidence"] == "approved"
    assert review["envelope4096"] == "unresolved"
    assert review["envelope8192"] == "unresolved"
    assert review["processMemoryCeilingBytes"] == 12_884_901_888
    assert review["ceilingUnchanged"] is True
    assert review["explanationSuitabilityContract"] == "approved"
    assert review["suitabilityScreening"] == "eligible-for-controlled-evaluation"
    assert review["measuredBehavioralQuality"] == "not-established"
    assert review["controlledMeasurement"] == "authorized-in-principle-with-documented-residuals"
    assert review["parameterCount"] == 1_170_340_608
    assert review["bytesPerFp32Parameter"] == 4
    assert review["logicalFp32ProductBytes"] == 4_681_362_432
    assert review["logicalProductIncludedInPeak"] is False
    assert review["candidateDecision"] == "no-selection"
    assert review["selectionOutcome"] == "no-selection"
    assert review["weightedScore"] is None
    assert review["qualifyingCandidateCount"] == 0
    assert review["acquisitionAuthorization"] == "not-authorized"
    assert review["installationAuthorized"] is False
    assert review["executionAuthorized"] is False
    assert review["measurementPerformed"] is False
    assert review["runtimeInstallationStatus"] == "not-installed"
    assert review["acquisitionStatus"] == "not-acquired"
    assert review["conversionStatus"] == "not-performed"
    assert review["executionStatus"] == "not-executed"
    assert review["realModelExecuted"] is False
    assert review["productionReady"] is False
    assert review["calibrationApprovalStatus"] == "not-approved"
    assert review["storageDecision"] == "unchanged"
    assert review["track8bReadiness"] == "ready-for-controlled-measurement"
    assert review["locallyObservedRuntimeDigests"] == []
    assert review["locallyObservedModelDigests"] == []
    assert review["locallyObservedTokenizerDigests"] == []
    assert review["locallyObservedConfigurationDigests"] == []
    assert review["locallyObservedOnnxArtifactDigests"] == []
    assert review["locallyObservedArtifactDigests"] == []
    assert review["reviewDigest"] == review_digest(review)
    assert len(review["unresolvedResidentCategories"]) == 10
    assert review["supportedInPrinciple"] == [
        "instruction-following",
        "structured-output",
        "english-language",
        "context-capacity",
    ]
    assert "starting measurement from this review" in review["notAuthorized"]


def test_digest_mutation_fails_closed() -> None:
    before = (repo_root() / _RECORD).read_bytes()
    mutated = json.loads(json.dumps(load_track7b_review()))
    mutated["reviewDigest"] = "0" * 64
    with pytest.raises(Track7BReviewError) as caught:
        validate_track7b_review(mutated)
    assert caught.value.code == "review-digest"
    assert (repo_root() / _RECORD).read_bytes() == before


def test_track7b_review_validation_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["track7b-review-validation"])
    payload = json.loads(buffer.getvalue())
    assert code == 0
    assert payload["reviewStatus"] == "accepted-by-principal-systems-architect"
    assert payload["controlledMeasurement"] == "authorized-in-principle-with-documented-residuals"
    assert payload["selectionOutcome"] == "no-selection"
    assert payload["reviewDigest"] == load_track7b_review()["reviewDigest"]
    assert payload["productionReady"] is False
