"""Principal Architect review of Track 7A. Approval does not authorize acquisition."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import ARTIFACT_CAP
from patchpilot_intelligence_evals.candidate_discovery import LFM_MODEL_ID
from patchpilot_intelligence_evals.explanation_suitability import decide_explanation_suitability
from patchpilot_intelligence_evals.finalist_budget import decide_finalist_budget
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.storage_budget import decide_storage_policy
from patchpilot_intelligence_evals.track7_selection import decide_track7_selection
from patchpilot_intelligence_evals.track8_authorization import decide_track8_authorization
from patchpilot_intelligence_evals.track8a_readiness import decide_track8a_readiness

_RECORD = Path("candidates/authorization/track7a-implementation-review.json")
_LOGICAL = 4_717_588_977
_OVERHEAD = 1_228_800
_RUNTIME = 11_413_655
_COPY_PEAK = 9_447_820_409
_COPY_EXCESS = 857_885_817
_ATOMIC_PEAK = 4_730_231_432
_ATOMIC_HEADROOM = 3_859_703_160
_COMPONENTS: tuple[tuple[str, str, str, str], ...] = (
    (
        "artifact-storage-policy",
        "artifactStoragePolicy",
        "approved",
        "Artifact storage policy is approved.",
    ),
    (
        "verification-sealing",
        "verificationSealing",
        "approved",
        "Verification sealing is approved.",
    ),
    (
        "mutation-detection",
        "mutationDetection",
        "approved",
        "Mutation detection is approved.",
    ),
    (
        "same-filesystem-atomic-promotion",
        "atomicPromotion",
        "approved-with-documented-residuals",
        "Same-filesystem atomic promotion is approved with documented residuals.",
    ),
    (
        "copy-promotion",
        "copyPromotion",
        "failed",
        "Copy promotion failed for the Track 7 finalist.",
    ),
    (
        "cross-filesystem-promotion",
        "crossFilesystemPromotion",
        "ineligible",
        "Cross-filesystem promotion is ineligible.",
    ),
    (
        "copy-fallback",
        "copyFallback",
        "prohibited",
        "Copy fallback is prohibited.",
    ),
)
_RESIDUALS: tuple[tuple[str, str], ...] = (
    (
        "one-proven-filesystem",
        "Atomic promotion is supported only on one proven filesystem.",
    ),
    (
        "cross-device-ineligible",
        "Cross-device promotion remains ineligible.",
    ),
    (
        "no-copy-and-delete-fallback",
        "There is no copy-and-delete fallback.",
    ),
    (
        "post-rename-recovery-proof",
        "Interruption after rename may require explicit recovery proof.",
    ),
    (
        "inconsistent-verified-evidence",
        "A verified directory with inconsistent journal or seal evidence remains indeterminate.",
    ),
    (
        "verified-mutation-without-kernel-immutability",
        (
            "Repository policy detects verified-state mutation but does not claim "
            "kernel-enforced immutability."
        ),
    ),
    (
        "transient-acquisition-overhead-unknown",
        "Transient acquisition overhead remains unknown.",
    ),
    (
        "no-real-model-artifact",
        "No real model artifact has exercised the state machine.",
    ),
    (
        "fp32-peak-memory-unresolved",
        "FP32 peak process memory remains unresolved.",
    ),
    (
        "explanation-suitability-unresolved",
        "Explanation suitability remains unresolved.",
    ),
)
_NOT_AUTHORIZED: tuple[str, ...] = (
    "candidate selection",
    "Track 8 acquisition",
    "runtime installation",
    "model, tokenizer, configuration, or ONNX acquisition",
    "conversion",
    "quantization",
    "inference",
    "evaluation-gate changes",
    "shadow mode",
    "PatchPilot production composition",
)


class Track7AReviewError(ValueError):
    """A Track 7A review check failed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_track7a_review() -> dict[str, Any]:
    """Build the accepted storage review and seal its digest."""
    document: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "reviewStatus": "accepted-by-principal-systems-architect",
        "reviewDate": "2026-11-12",
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "decision": "track 7a storage model approved and acquisition withheld",
        "authorizedScope": (
            "This approval accepts the Track 7A storage model and same-filesystem "
            "atomic promotion with documented residuals."
        ),
        "finalistModelId": LFM_MODEL_ID,
        "ceilingUnchanged": True,
        "storageOnlyBlocker": "resolved",
        "candidateDecision": "no-selection",
        "track8Authorization": "not-authorized",
        "selectionOutcome": "no-selection",
        "authorizationOutcome": "not-authorized",
        "weightedScore": None,
        "qualifyingCandidateCount": 0,
        "logicalInventoryBytes": _LOGICAL,
        "verificationWorkingOverheadBytes": _OVERHEAD,
        "runtimeStagingListedBytes": _RUNTIME,
        "copyPromotionPeakBytes": _COPY_PEAK,
        "copyPromotionExcessBytes": _COPY_EXCESS,
        "atomicPromotionPeakBytes": _ATOMIC_PEAK,
        "atomicPromotionHeadroomBytes": _ATOMIC_HEADROOM,
        "artifactCapBytes": ARTIFACT_CAP,
        "peakMemoryBasis": "unknown-fp32",
        "explanationSuitability": "unresolved",
        "readinessOutcome": "not-ready",
        "installationAuthorized": False,
        "conversionAuthorized": False,
        "quantizationApproved": False,
        "componentReviews": [
            {
                "componentId": component_id,
                "disposition": disposition,
                "statement": statement,
            }
            for component_id, _field, disposition, statement in _COMPONENTS
        ],
        "acceptedResiduals": [
            {"residualId": residual_id, "statement": statement}
            for residual_id, statement in _RESIDUALS
        ],
        "notAuthorized": list(_NOT_AUTHORIZED),
        "locallyObservedArtifactDigests": [],
    }
    for _component_id, field, disposition, _statement in _COMPONENTS:
        document[field] = disposition
    document["reviewDigest"] = review_digest(document)
    return validate_track7a_review(document)


def validate_track7a_review(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the review and require the live storage and authorization outcomes."""
    validate("track7a-implementation-review", document)
    if document["reviewDigest"] != review_digest(document):
        raise Track7AReviewError("review-digest")
    if document["locallyObservedArtifactDigests"] != []:
        raise Track7AReviewError("local-digest")
    if document["artifactCapBytes"] != ARTIFACT_CAP or document["ceilingUnchanged"] is not True:
        raise Track7AReviewError("ceiling")
    observed = [
        (item["componentId"], item["disposition"], item["statement"])
        for item in document["componentReviews"]
    ]
    expected = [
        (component_id, disposition, statement)
        for component_id, _field, disposition, statement in _COMPONENTS
    ]
    if observed != expected:
        raise Track7AReviewError("components")
    for component_id, field, disposition, _statement in _COMPONENTS:
        if document[field] != disposition:
            raise Track7AReviewError(component_id)
    observed_residuals = [
        (item["residualId"], item["statement"]) for item in document["acceptedResiduals"]
    ]
    if observed_residuals != list(_RESIDUALS):
        raise Track7AReviewError("residuals")
    if tuple(document["notAuthorized"]) != _NOT_AUTHORIZED:
        raise Track7AReviewError("not-authorized")
    _require_live_outcomes(document)
    return document


def load_track7a_review(root: Path | None = None) -> dict[str, Any]:
    """Load the review and require it to match the sealed record."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise Track7AReviewError("record-type")
    document = validate_track7a_review(loaded)
    if document != decide_track7a_review():
        raise Track7AReviewError("review-drift")
    return document


def _require_live_outcomes(document: dict[str, Any]) -> None:
    policy = decide_storage_policy()
    readiness = decide_track8a_readiness()
    selection = decide_track7_selection()
    authorization = decide_track8_authorization()
    finalist = decide_finalist_budget()["finalists"][0]
    suitability = decide_explanation_suitability()["finalists"][0]["suitabilityOutcome"]
    if policy["artifactCapBytes"] != ARTIFACT_CAP:
        raise Track7AReviewError("ceiling")
    if policy["logicalInventoryBytes"] != _LOGICAL:
        raise Track7AReviewError("arithmetic")
    if policy["verificationWorkingOverheadBytes"] != _OVERHEAD:
        raise Track7AReviewError("arithmetic")
    if policy["runtimeStagingListedBytes"] != _RUNTIME:
        raise Track7AReviewError("arithmetic")
    if (
        policy["copyPromotionPeakBytes"] != _COPY_PEAK
        or policy["copyPromotionOverBytes"] != _COPY_EXCESS
    ):
        raise Track7AReviewError("arithmetic")
    if (
        policy["atomicPromotionPeakBytes"] != _ATOMIC_PEAK
        or policy["atomicPromotionUnderBytes"] != _ATOMIC_HEADROOM
    ):
        raise Track7AReviewError("arithmetic")
    if policy["copyPromotionStorageOutcome"] != "fail":
        raise Track7AReviewError("copy-promotion")
    if policy["atomicPromotionStorageOutcome"] != "pass":
        raise Track7AReviewError("atomic-promotion")
    if (
        policy["crossFilesystemStorageOutcome"] != "ineligible"
        or policy["copyFallback"] != "prohibited"
    ):
        raise Track7AReviewError("cross-filesystem")
    if policy["transientAcquisitionOverheadBytes"] is not None:
        raise Track7AReviewError("acquisition")
    if document["copyPromotionExcessBytes"] != _COPY_EXCESS:
        raise Track7AReviewError("arithmetic")
    if document["atomicPromotionHeadroomBytes"] != _ATOMIC_HEADROOM:
        raise Track7AReviewError("arithmetic")
    if readiness["readinessOutcome"] != "not-ready" or readiness["storageBlocker"] != "resolved":
        raise Track7AReviewError("readiness")
    if readiness["authorizationOutcome"] != "not-authorized":
        raise Track7AReviewError("authorization")
    if (
        selection["selectionOutcome"] != "no-selection"
        or selection["qualifyingCandidateCount"] != 0
    ):
        raise Track7AReviewError("selection")
    if selection["candidates"][0]["weightedScore"] is not None:
        raise Track7AReviewError("selection")
    if authorization["authorizationOutcome"] != "not-authorized":
        raise Track7AReviewError("authorization")
    if authorization["installationAuthorized"] is not False:
        raise Track7AReviewError("authorization")
    if finalist["peakMemoryBasis"] != "unknown-fp32" or finalist["peakMemoryBytes"] is not None:
        raise Track7AReviewError("memory")
    if suitability != "unresolved":
        raise Track7AReviewError("suitability")
    if document["finalistModelId"] != LFM_MODEL_ID:
        raise Track7AReviewError("identity")
    if document["storageOnlyBlocker"] != "resolved":
        raise Track7AReviewError("storage-blocker")
