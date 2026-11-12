"""Measurement authorization paths. Disabled states stay disabled on every path."""

from __future__ import annotations

from patchpilot_intelligence_evals.measurement_authorization import (
    classify_measurement,
    load_measurement_authorization,
)


def _facts(**overrides: bool) -> dict[str, bool]:
    facts = {
        "memoryClosed": False,
        "suitabilityClosed": False,
        "disqualifierPresent": False,
        "materialUnknown": True,
        "storageOnlyPass": True,
        "hardenedExecutionApproved": True,
        "runtimeIdentityAuthorized": True,
        "adapterIdentityFixed": True,
        "artifactIdentityFixed": True,
        "residualsPresent": True,
    }
    facts.update(overrides)
    return facts


def test_committed_measurement_keeps_acquisition_disabled() -> None:
    document = load_measurement_authorization()
    assert document["authorizationOutcome"] == "authorized-with-documented-residuals"
    assert document["reason"] == "measurement-required"
    assert document["verdict"] == (
        "TRACK 8B CONTROLLED MEASUREMENT AUTHORIZED WITH DOCUMENTED RESIDUALS"
    )
    assert document["measurementPerformed"] is False
    assert document["installationAuthorized"] is False
    assert document["acquisitionStatus"] == "not-acquired"
    assert document["executionStatus"] == "not-executed"
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert document["locallyObservedArtifactDigests"] == []
    assert document["selectionOutcome"] == "no-selection"
    assert document["weightedScore"] is None
    assert document["qualifyingCandidateCount"] == 0
    assert document["acquisitionAuthorization"] == "not-authorized"
    assert document["memoryClassifications"] == ["unresolved", "unresolved"]
    assert document["suitabilityScreening"] == "eligible-for-controlled-evaluation"


def test_authorization_paths() -> None:
    closed = classify_measurement(
        _facts(
            memoryClosed=True, suitabilityClosed=True, materialUnknown=False, residualsPresent=False
        )
    )
    assert closed["authorizationOutcome"] == "not-authorized"
    assert closed["reason"] == "evidence-closed"
    assert closed["selectionOutcome"] == "no-selection"
    justified = classify_measurement(_facts(residualsPresent=False))
    assert justified["authorizationOutcome"] == "authorized"
    assert justified["verdict"] == "TRACK 8B CONTROLLED MEASUREMENT AUTHORIZED"
    disqualified = classify_measurement(_facts(disqualifierPresent=True))
    assert disqualified["authorizationOutcome"] == "not-authorized"
    assert disqualified["reason"] == "disqualified"
    withheld = classify_measurement(_facts(storageOnlyPass=False))
    assert withheld["reason"] == "prerequisite-failed"
    unjustified = classify_measurement(_facts(materialUnknown=False))
    assert unjustified["authorizationOutcome"] == "not-authorized"
    assert unjustified["reason"] == "unresolved-without-justification"
    assert unjustified["selectionOutcome"] == "no-selection"
    blocked = classify_measurement(_facts(artifactIdentityFixed=False))
    assert blocked["authorizationOutcome"] == "blocked-by-unresolved-authority"
    assert blocked["verdict"] == "BLOCKED BY UNRESOLVED AUTHORITY"
