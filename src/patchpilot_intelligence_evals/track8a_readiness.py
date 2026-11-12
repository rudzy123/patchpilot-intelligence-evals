"""Track 8A storage readiness. A storage pass does not select or authorize a candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import ARTIFACT_CAP, MEMORY_CAP
from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    contains_private_marker,
)
from patchpilot_intelligence_evals.candidate_eligibility import RETRIEVED_ON
from patchpilot_intelligence_evals.explanation_suitability import decide_explanation_suitability
from patchpilot_intelligence_evals.finalist_budget import decide_finalist_budget
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.storage_budget import decide_storage_policy
from patchpilot_intelligence_evals.track7_selection import decide_track7_selection
from patchpilot_intelligence_evals.track8_authorization import decide_track8_authorization

_RECALCULATION = Path("candidates/authorization/artifact-budget-recalculation.json")
_READINESS = Path("candidates/authorization/track8a-storage-readiness.json")
_VERDICT = "TRACK 8A STORAGE RECALCULATED ACQUISITION NOT AUTHORIZED"


class Track8AReadinessError(ValueError):
    """A Track 8A record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_budget_recalculation() -> dict[str, Any]:
    """Recalculate the finalist under the three storage models."""
    policy = decide_storage_policy()
    preserved = _preserved()
    document = {
        "schemaVersion": "1.0.0",
        **_disabled(),
        "retrievedOn": RETRIEVED_ON,
        "finalistModelId": LFM_MODEL_ID,
        "artifactCapBytes": ARTIFACT_CAP,
        "memoryCapBytes": MEMORY_CAP,
        "logicalInventoryBytes": policy["logicalInventoryBytes"],
        "legacyCopyFootprintBytes": policy["legacyCopyFootprintBytes"],
        "verificationWorkingOverheadBytes": policy["verificationWorkingOverheadBytes"],
        "runtimeStagingListedBytes": policy["runtimeStagingListedBytes"],
        "allocatedBytesGovernCeiling": False,
        "sparseAllocatedBytesGovernCeiling": False,
        "transientAcquisitionAuthorized": False,
        "transientAcquisitionOverheadBytes": None,
        "copyPromotionPeakBytes": policy["copyPromotionPeakBytes"],
        "copyStorageOnlyEligibility": policy["copyPromotionStorageOutcome"],
        "copyStorageBlocker": "still-failed",
        "atomicPromotionPeakBytes": policy["atomicPromotionPeakBytes"],
        "atomicStorageOnlyEligibility": policy["atomicPromotionStorageOutcome"],
        "atomicStorageBlocker": "resolved",
        "crossFilesystemPeakBytes": None,
        "crossFilesystemStorageOnlyEligibility": "ineligible",
        "crossFilesystemStorageBlocker": "ineligible",
        "memoryEligibility": "fail",
        "explanationSuitabilityEligibility": "unresolved",
        "candidateSelectionEligibility": "fail",
        "acquisitionAuthorization": "not-authorized",
        **preserved,
    }
    return validate_budget_recalculation(document)


def decide_track8a_readiness() -> dict[str, Any]:
    """Record storage recalculation while acquisition stays not authorized."""
    recalculation = decide_budget_recalculation()
    document = {
        "schemaVersion": "1.0.0",
        **_disabled(),
        "retrievedOn": RETRIEVED_ON,
        "readinessOutcome": "not-ready",
        "verdict": _VERDICT,
        "finalistModelId": LFM_MODEL_ID,
        "artifactCapBytes": ARTIFACT_CAP,
        "storageBlocker": recalculation["atomicStorageBlocker"],
        "copyPromotionStorageBlocker": recalculation["copyStorageBlocker"],
        "atomicPromotionStorageBlocker": recalculation["atomicStorageBlocker"],
        "crossFilesystemStorageBlocker": recalculation["crossFilesystemStorageBlocker"],
        "storageOnlyEligibility": recalculation["atomicStorageOnlyEligibility"],
        "memoryEligibility": "fail",
        "explanationSuitabilityEligibility": "unresolved",
        "candidateSelectionEligibility": "fail",
        "acquisitionAuthorization": "not-authorized",
        "transientAcquisitionAuthorized": False,
        "transientAcquisitionOverheadBytes": None,
        "installationAuthorized": False,
        "conversionAuthorized": False,
        "quantizationApproved": False,
        **_preserved(),
    }
    return validate_track8a_readiness(document)


def validate_budget_recalculation(document: dict[str, Any]) -> dict[str, Any]:
    """Validate one recalculation against the storage policy and Track 7 records."""
    validate("artifact-budget-recalculation", document)
    _require_common(document)
    policy = decide_storage_policy()
    if document["logicalInventoryBytes"] != policy["logicalInventoryBytes"]:
        raise Track8AReadinessError("arithmetic")
    if document["copyPromotionPeakBytes"] != policy["copyPromotionPeakBytes"]:
        raise Track8AReadinessError("arithmetic")
    if document["atomicPromotionPeakBytes"] != policy["atomicPromotionPeakBytes"]:
        raise Track8AReadinessError("arithmetic")
    if document["copyStorageOnlyEligibility"] != "fail":
        raise Track8AReadinessError("outcome")
    if document["atomicStorageOnlyEligibility"] != "pass":
        raise Track8AReadinessError("outcome")
    if document["crossFilesystemStorageOnlyEligibility"] != "ineligible":
        raise Track8AReadinessError("outcome")
    if document["memoryEligibility"] != "fail":
        raise Track8AReadinessError("memory")
    if document["candidateSelectionEligibility"] != "fail":
        raise Track8AReadinessError("selection")
    if document["acquisitionAuthorization"] != "not-authorized":
        raise Track8AReadinessError("authorization")
    return document


def validate_track8a_readiness(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the Track 8A readiness record. Acquisition stays withheld."""
    validate("track8a-storage-readiness", document)
    _require_common(document)
    if document["readinessOutcome"] != "not-ready" or document["verdict"] != _VERDICT:
        raise Track8AReadinessError("verdict")
    if document["storageBlocker"] != "resolved":
        raise Track8AReadinessError("outcome")
    if document["copyPromotionStorageBlocker"] != "still-failed":
        raise Track8AReadinessError("outcome")
    if document["crossFilesystemStorageBlocker"] != "ineligible":
        raise Track8AReadinessError("outcome")
    if document["authorizationOutcome"] != "not-authorized":
        raise Track8AReadinessError("authorization")
    if (
        document["installationAuthorized"] is not False
        or document["conversionAuthorized"] is not False
    ):
        raise Track8AReadinessError("authorization")
    if document["quantizationApproved"] is not False:
        raise Track8AReadinessError("authorization")
    if document["storageOnlyEligibility"] != "pass":
        raise Track8AReadinessError("outcome")
    if document["candidateSelectionEligibility"] != "fail":
        raise Track8AReadinessError("selection")
    return document


def load_budget_recalculation(root: Path | None = None) -> dict[str, Any]:
    """Load the committed recalculation and require it to match the decision."""
    return _load(_RECALCULATION, validate_budget_recalculation, decide_budget_recalculation, root)


def load_track8a_readiness(root: Path | None = None) -> dict[str, Any]:
    """Load the committed readiness record and require it to match the decision."""
    return _load(_READINESS, validate_track8a_readiness, decide_track8a_readiness, root)


def _preserved() -> dict[str, Any]:
    selection = decide_track7_selection()
    authorization = decide_track8_authorization()
    suitability = decide_explanation_suitability()["finalists"][0]["suitabilityOutcome"]
    finalist = decide_finalist_budget()["finalists"][0]
    if (
        selection["selectionOutcome"] != "no-selection"
        or selection["qualifyingCandidateCount"] != 0
    ):
        raise Track8AReadinessError("selection")
    if selection["candidates"][0]["weightedScore"] is not None:
        raise Track8AReadinessError("selection")
    if authorization["authorizationOutcome"] != "not-authorized":
        raise Track8AReadinessError("authorization")
    if suitability != "unresolved" or finalist["peakMemoryBasis"] != "unknown-fp32":
        raise Track8AReadinessError("memory")
    if finalist["peakMemoryBytes"] is not None:
        raise Track8AReadinessError("memory")
    return {
        "selectionOutcome": "no-selection",
        "selectedModelId": None,
        "authorizationOutcome": "not-authorized",
        "weightedScore": None,
        "qualifyingCandidateCount": 0,
        "peakMemoryBasis": "unknown-fp32",
        "peakMemoryBytes": None,
        "explanationSuitability": "unresolved",
    }


def _require_common(document: dict[str, Any]) -> None:
    if contains_private_marker(document):
        raise Track8AReadinessError("identity")
    if document["locallyObservedArtifactDigests"] != []:
        raise Track8AReadinessError("local-digest")
    if document["artifactCapBytes"] != ARTIFACT_CAP:
        raise Track8AReadinessError("cap")
    preserved = _preserved()
    for key, value in preserved.items():
        if document[key] != value:
            raise Track8AReadinessError("preserved")
    if document["explanationSuitabilityEligibility"] != "unresolved":
        raise Track8AReadinessError("suitability")
    if document["transientAcquisitionOverheadBytes"] is not None:
        raise Track8AReadinessError("acquisition")


def _disabled() -> dict[str, Any]:
    return {
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "locallyObservedArtifactDigests": [],
    }


def _load(
    relative: Path,
    validator: Any,
    decider: Any,
    root: Path | None,
) -> dict[str, Any]:
    base = root if root is not None else repo_root()
    loaded = json.loads((base / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise Track8AReadinessError("record-type")
    document: dict[str, Any] = validator(loaded)
    if document != decider():
        raise Track8AReadinessError("record-drift")
    return document
