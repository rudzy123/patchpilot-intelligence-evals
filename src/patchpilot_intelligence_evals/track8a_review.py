"""Principal Architect review of Track 8A. Approval does not start measurement."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_discovery import contains_private_marker
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.track8a_evidence import (
    EvidenceError,
    build_acquisition_evidence,
    provider_disposition,
)

_RECORD = Path("candidates/authorization/track8a-implementation-review.json")
_SCOPE = (
    "This approval accepts the Track 8A controlled acquisition, verification, "
    "same-filesystem atomic promotion, and hardened offline-load proof with documented "
    "residuals. It does not authorize Track 8B measurement, candidate selection, "
    "calibration, inference, generation, corpus execution, long-context measurement, or "
    "production use. Historical pre-Track-8A authorization records stay unchanged."
)
_COMPONENTS: tuple[tuple[str, str, str], ...] = (
    (
        "runtime-acquisition",
        "approved",
        "Runtime acquisition is acquired and verified.",
    ),
    (
        "candidate-acquisition",
        "approved",
        "Candidate acquisition is acquired and verified.",
    ),
    (
        "atomic-promotion",
        "approved",
        "Same-filesystem atomic promotion passed and copy fallback was not used.",
    ),
    (
        "hardened-offline-load",
        "approved",
        "The hardened offline load passed without inference or generation.",
    ),
    (
        "network-denial",
        "approved",
        "Operating-system network denial passed.",
    ),
    (
        "process-cleanup",
        "approved",
        "Process cleanup passed.",
    ),
    (
        "provider-shared-library",
        "not-required",
        "libonnxruntime_providers_shared.so is not required for the authorized CPU-only path.",
    ),
    (
        "superseded-attempt-cleanup",
        "closed",
        "Rejected and superseded payload handling is closed.",
    ),
    (
        "track8b-measurement",
        "not-authorized",
        "Track 8B measurement is not authorized.",
    ),
)
_RESIDUALS: tuple[tuple[str, str], ...] = (
    (
        "resident-envelopes-unresolved",
        "The 4096-token and 8192-token FP32 resident envelopes remain unresolved.",
    ),
    (
        "load-observation-is-not-resident-measurement",
        "The offline-load resident observation is not a weight-resident measurement.",
    ),
    ("behavioral-quality-unmeasured", "Behavioral quality remains unmeasured."),
    ("installation-not-authorized", "Runtime installation remains unauthorized."),
    (
        "historical-authorization-unchanged",
        "Historical pre-Track-8A authorization records stay not-authorized.",
    ),
    (
        "archive-retained-as-digest-evidence",
        (
            "The runtime archive remains quarantined digest evidence and is not an "
            "execution dependency."
        ),
    ),
)
_NOT_AUTHORIZED: tuple[str, ...] = (
    "Track 8B measurement",
    "candidate selection",
    "calibration approval",
    "inference",
    "generation",
    "corpus execution",
    "long-context measurement",
    "production use",
    "project dependency changes",
    "copy promotion",
)


class Track8AReviewError(ValueError):
    """A Track 8A review check failed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_track8a_review() -> dict[str, Any]:
    """Build the accepted acquisition review and seal its digest."""
    try:
        evidence = build_acquisition_evidence()
    except EvidenceError as exc:
        raise Track8AReviewError(exc.code) from exc
    if evidence["providerSharedLibraryDisposition"] != provider_disposition():
        raise Track8AReviewError("provider-library")
    if any(item["executableEligibility"] for item in evidence["attemptDecisions"]):
        raise Track8AReviewError("executable-eligibility")
    if any(item["verifiedStateEligibility"] for item in evidence["attemptDecisions"]):
        raise Track8AReviewError("verified-eligibility")
    document: dict[str, Any] = {
        "allowlistDigest": evidence["allowlistDigest"],
        "authorizedScope": _SCOPE,
        "calibrationApprovalStatus": "not-approved",
        "candidateAcquisition": evidence["candidateAcquisition"],
        "candidateAtomicPromotion": "passed",
        "candidateFiles": evidence["candidateFiles"],
        "copyFallbackUsed": False,
        "corpusExecuted": False,
        "decision": "track 8a controlled acquisition approved with documented residuals",
        "evidenceIdentityDigest": evidence["identityDigest"],
        "generationPerformed": False,
        "hardenedOfflineLoad": "passed",
        "inferencePerformed": False,
        "installationAuthorized": False,
        "longContextMeasurementPerformed": False,
        "measurementPerformed": False,
        "networkDenial": "passed",
        "operatorApproval": "accepted",
        "planDigest": evidence["planDigest"],
        "processCleanup": "passed",
        "productionReady": False,
        "providerSharedLibraryDisposition": provider_disposition(),
        "realModelExecuted": False,
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "reviewDate": "2026-11-16",
        "reviewStatus": "accepted-by-principal-systems-architect",
        "runtimeAcquisition": evidence["runtimeAcquisition"],
        "runtimeArchive": evidence["runtimeArchive"],
        "runtimeAtomicPromotion": "passed",
        "runtimeFiles": evidence["runtimeFiles"],
        "sameFilesystemPromotion": True,
        "schemaVersion": "1.0.0",
        "selectionOutcome": "no-selection",
        "track8bMeasurementAuthorization": "not-authorized",
        "acceptedResiduals": [
            {"residualId": residual_id, "statement": statement}
            for residual_id, statement in _RESIDUALS
        ],
        "componentReviews": [
            {"componentId": component_id, "disposition": disposition, "statement": statement}
            for component_id, disposition, statement in _COMPONENTS
        ],
        "notAuthorized": list(_NOT_AUTHORIZED),
    }
    document["reviewDigest"] = review_digest(document)
    return validate_track8a_review(document)


def validate_track8a_review(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the review and require the sealed evidence identity."""
    validate("track8a-implementation-review", document)
    if contains_private_marker(document):
        raise Track8AReviewError("identity")
    if document["reviewDigest"] != review_digest(document):
        raise Track8AReviewError("review-digest")
    evidence = build_acquisition_evidence()
    if document["evidenceIdentityDigest"] != evidence["identityDigest"]:
        raise Track8AReviewError("evidence-digest")
    if document["runtimeFiles"] != evidence["runtimeFiles"]:
        raise Track8AReviewError("runtime-digest")
    if document["candidateFiles"] != evidence["candidateFiles"]:
        raise Track8AReviewError("candidate-digest")
    if document["runtimeArchive"] != evidence["runtimeArchive"]:
        raise Track8AReviewError("runtime-digest")
    if document["providerSharedLibraryDisposition"] != provider_disposition():
        raise Track8AReviewError("provider-library")
    observed = [
        (item["componentId"], item["disposition"], item["statement"])
        for item in document["componentReviews"]
    ]
    if observed != list(_COMPONENTS):
        raise Track8AReviewError("components")
    residuals = [(item["residualId"], item["statement"]) for item in document["acceptedResiduals"]]
    if residuals != list(_RESIDUALS):
        raise Track8AReviewError("residuals")
    if list(document["notAuthorized"]) != list(_NOT_AUTHORIZED):
        raise Track8AReviewError("not-authorized")
    if document["authorizedScope"] != _SCOPE:
        raise Track8AReviewError("scope")
    return document


def load_track8a_review(root: Path | None = None) -> dict[str, Any]:
    """Load the committed review and require it to match the sealed record."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise Track8AReviewError("record-type")
    document = validate_track8a_review(loaded)
    if document != decide_track8a_review():
        raise Track8AReviewError("review-drift")
    return document
