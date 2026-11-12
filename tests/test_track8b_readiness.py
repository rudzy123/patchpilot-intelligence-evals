"""Track 8B readiness preserves no-selection and disabled execution."""

from __future__ import annotations

from patchpilot_intelligence_evals.track8b_readiness import load_track8b_readiness


def test_track8b_readiness_authorizes_measurement_only() -> None:
    document = load_track8b_readiness()
    assert document["readinessOutcome"] == "ready-for-controlled-measurement"
    assert document["measurementAuthorization"] == "authorized-with-documented-residuals"
    assert document["verdict"] == (
        "TRACK 8B CONTROLLED MEASUREMENT AUTHORIZED WITH DOCUMENTED RESIDUALS"
    )
    assert document["measurementPerformed"] is False
    assert document["installationAuthorized"] is False
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["conversionStatus"] == "not-performed"
    assert document["executionStatus"] == "not-executed"
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert document["locallyObservedArtifactDigests"] == []
    assert document["selectionOutcome"] == "no-selection"
    assert document["selectedModelId"] is None
    assert document["weightedScore"] is None
    assert document["qualifyingCandidateCount"] == 0
    assert document["acquisitionAuthorization"] == "not-authorized"
    assert document["track8aReadinessOutcome"] == "not-ready"
    assert document["storageBlocker"] == "resolved"
    assert document["memoryClassifications"] == ["unresolved", "unresolved"]
    assert document["suitabilityScreening"] == "eligible-for-controlled-evaluation"
