"""Track 8B prerequisites stay unmeasured and unauthorized."""

from __future__ import annotations

from patchpilot_intelligence_evals.track8b_prerequisites import (
    decide_prerequisites,
    load_measurement_prerequisites,
    sealed_prerequisites,
)


def test_committed_prerequisites_keep_memory_residuals() -> None:
    document = load_measurement_prerequisites()
    assert document == sealed_prerequisites()
    assert document["readinessOutcome"] == "ready-with-documented-residuals"
    assert document["verdict"] == "TRACK 8B CONTROLLED MEASUREMENT READY WITH DOCUMENTED RESIDUALS"
    assert document["measurementAuthorization"] == "not-authorized"
    assert document["measurementPerformed"] is False
    assert document["selectionOutcome"] == "no-selection"
    assert document["productionReady"] is False
    assert document["installationAuthorized"] is False
    assert document["providerSharedLibraryBlocking"] is False
    assert document["supersededPayloadClosed"] is True
    assert document["executionDependencyOutsideVerifiedRuntime"] is False


def test_missing_evidence_stays_not_ready() -> None:
    document = decide_prerequisites()
    assert document["readinessOutcome"] == "not-ready"
    assert document["measurementAuthorization"] == "not-authorized"
    assert document["measurementPerformed"] is False


def test_a_full_pass_keeps_memory_residuals() -> None:
    evidence = {
        "artifactMismatch": False,
        "atomicPromotionPassed": True,
        "configurationVerified": True,
        "executionDependencyOutsideVerifiedRuntime": False,
        "hardenedLoadPassed": True,
        "localDigestsPresent": True,
        "modelVerified": True,
        "networkDenialPassed": True,
        "projectDependencyChanged": False,
        "providerSharedLibraryBlocking": False,
        "runtimeVerified": True,
        "supersededPayloadClosed": True,
        "tokenizerVerified": True,
    }
    document = decide_prerequisites(evidence)
    assert document["readinessOutcome"] == "ready-with-documented-residuals"
    assert document["verdict"].endswith("READY WITH DOCUMENTED RESIDUALS")
    assert document["measurementPerformed"] is False
    assert document["measurementAuthorization"] == "not-authorized"
    assert document["realModelExecuted"] is False
    evidence["artifactMismatch"] = True
    blocked = decide_prerequisites(evidence)
    assert blocked["readinessOutcome"] == "not-ready"
    evidence["artifactMismatch"] = False
    evidence["providerSharedLibraryBlocking"] = True
    library_blocked = decide_prerequisites(evidence)
    assert library_blocked["readinessOutcome"] == "not-ready"
