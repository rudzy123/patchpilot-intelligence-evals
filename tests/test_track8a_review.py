"""Track 8A evidence and review stay redacted and sealed."""

from __future__ import annotations

from patchpilot_intelligence_evals.acquisition_plan import load_acquisition_plan
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.track8_authorization import load_track8_authorization
from patchpilot_intelligence_evals.track8a_evidence import (
    build_acquisition_evidence,
    load_acquisition_evidence,
    provider_disposition,
)
from patchpilot_intelligence_evals.track8a_review import decide_track8a_review, load_track8a_review


def test_evidence_records_the_observed_acquisition() -> None:
    document = load_acquisition_evidence()
    assert document == build_acquisition_evidence()
    assert document["providerSharedLibraryDisposition"] == provider_disposition()
    assert document["providerSharedLibraryDisposition"] == (
        "not required for the authorized CPU-only path"
    )
    assert document["operatorApproval"] == "accepted"
    assert document["measurementPerformed"] is False
    assert document["inferencePerformed"] is False
    assert document["generationPerformed"] is False
    assert document["corpusExecuted"] is False
    assert document["longContextMeasurementPerformed"] is False
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert document["selectionOutcome"] == "no-selection"
    assert document["track8bMeasurementAuthorization"] == "not-authorized"
    assert document["copyFallbackUsed"] is False
    assert document["sameFilesystemPromotion"] is True
    assert document["gitTrackedArtifact"] is False
    assert document["storageReclaimedBytes"] == 31_938_441
    assert len(document["runtimeFiles"]) == 4
    assert len(document["candidateFiles"]) == 11
    assert all(item["executableEligibility"] is False for item in document["attemptDecisions"])
    assert all(item["verifiedStateEligibility"] is False for item in document["attemptDecisions"])
    promoted = [
        item["attemptId"]
        for item in document["retainedIdentities"]
        if item["verifiedStateEligibility"] is True
    ]
    assert promoted == ["rp-c2fe1c88f694fc1e", "cd-20b7ceee37a62cba"]
    archive = document["runtimeArchive"]
    assert archive["fileName"] == "onnxruntime-linux-x64-1.31.1.tgz"
    assert archive["logicalBytes"] == 11_413_655
    assert archive["localSha256"] == archive["upstreamSha256"]


def test_historical_records_stay_unauthorized() -> None:
    plan = load_acquisition_plan()
    authorization = load_track8_authorization()
    assert plan["acquisitionStatus"] == "not-acquired"
    assert plan["operatorApproval"] == "required"
    assert authorization["authorizationOutcome"] == "not-authorized"
    assert authorization["acquisitionStatus"] == "not-acquired"


def test_review_digest_seals_the_evidence() -> None:
    review = load_track8a_review()
    evidence = load_acquisition_evidence()
    assert review == decide_track8a_review()
    assert review["reviewDigest"] == review_digest(review)
    assert review["evidenceIdentityDigest"] == evidence["identityDigest"]
    assert review["runtimeFiles"] == evidence["runtimeFiles"]
    assert review["candidateFiles"] == evidence["candidateFiles"]
    assert review["reviewDate"] == "2026-11-16"
    assert review["reviewAuthority"] == "PatchPilot Principal Systems Architect"
    assert review["track8bMeasurementAuthorization"] == "not-authorized"
    assert review["measurementPerformed"] is False
    assert review["realModelExecuted"] is False
    assert review["productionReady"] is False
    assert "/" not in review["planDigest"]
