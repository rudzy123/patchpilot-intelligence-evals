"""Track 8A recalculation preserves every non-storage blocker."""

from __future__ import annotations

from patchpilot_intelligence_evals.artifact_budget import ARTIFACT_CAP
from patchpilot_intelligence_evals.finalist_budget import load_finalist_budget
from patchpilot_intelligence_evals.track7_selection import load_track7_selection
from patchpilot_intelligence_evals.track8_authorization import load_track8_authorization
from patchpilot_intelligence_evals.track8a_readiness import (
    load_budget_recalculation,
    load_track8a_readiness,
)


def test_recalculation_separates_storage_from_authorization() -> None:
    recalculation = load_budget_recalculation()
    readiness = load_track8a_readiness()
    assert recalculation["artifactCapBytes"] == ARTIFACT_CAP
    assert recalculation["copyStorageOnlyEligibility"] == "fail"
    assert recalculation["copyStorageBlocker"] == "still-failed"
    assert recalculation["atomicStorageOnlyEligibility"] == "pass"
    assert recalculation["atomicStorageBlocker"] == "resolved"
    assert recalculation["crossFilesystemStorageOnlyEligibility"] == "ineligible"
    assert recalculation["memoryEligibility"] == "fail"
    assert recalculation["explanationSuitability"] == "unresolved"
    assert recalculation["selectionOutcome"] == "no-selection"
    assert recalculation["weightedScore"] is None
    assert recalculation["qualifyingCandidateCount"] == 0
    assert recalculation["authorizationOutcome"] == "not-authorized"
    assert readiness["readinessOutcome"] == "not-ready"
    assert readiness["storageBlocker"] == "resolved"
    assert readiness["acquisitionAuthorization"] == "not-authorized"
    assert readiness["installationAuthorized"] is False
    assert readiness["conversionAuthorized"] is False
    assert readiness["quantizationApproved"] is False
    assert readiness["productionReady"] is False
    assert readiness["realModelExecuted"] is False
    assert readiness["runtimeInstallationStatus"] == "not-installed"
    assert readiness["acquisitionStatus"] == "not-acquired"
    assert readiness["conversionStatus"] == "not-performed"
    assert readiness["executionStatus"] == "not-executed"
    assert readiness["locallyObservedArtifactDigests"] == []
    assert load_track7_selection()["selectionOutcome"] == "no-selection"
    assert load_track8_authorization()["authorizationOutcome"] == "not-authorized"
    assert load_finalist_budget()["finalists"][0]["artifactFit"] == "fail"
    assert load_finalist_budget()["finalists"][0]["footprintBytes"] == 9446591609
