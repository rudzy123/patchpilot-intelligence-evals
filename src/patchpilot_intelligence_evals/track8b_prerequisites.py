"""Track 8B prerequisite decision. Measurement stays unperformed."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.track8a_evidence import (
    build_acquisition_evidence,
    provider_disposition,
)

_RECORD = Path("candidates/authorization/track8b-measurement-prerequisites.json")
_BLOCKING: dict[str, bool] = {
    "artifactMismatch": False,
    "atomicPromotionPassed": False,
    "configurationVerified": False,
    "executionDependencyOutsideVerifiedRuntime": True,
    "hardenedLoadPassed": False,
    "localDigestsPresent": False,
    "modelVerified": False,
    "networkDenialPassed": False,
    "projectDependencyChanged": False,
    "providerSharedLibraryBlocking": True,
    "runtimeVerified": False,
    "supersededPayloadClosed": False,
    "tokenizerVerified": False,
}
_SEALED: dict[str, bool] = {
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


class PrerequisiteError(ValueError):
    """A prerequisite record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def digest_document(document: dict[str, Any]) -> dict[str, Any]:
    """Attach the identity digest and validate the prerequisite record."""
    payload = {key: value for key, value in document.items() if key != "identityDigest"}
    payload["identityDigest"] = sha256_text(canonical_dumps(payload))
    reject_sensitive(payload)
    validate("track8b-measurement-prerequisites", payload)
    return payload


def decide_prerequisites(evidence: dict[str, bool] | None = None) -> dict[str, Any]:
    """Decide readiness. A pass still leaves memory residuals and performs no measurement."""
    flags = dict(_BLOCKING)
    if evidence is not None:
        flags.update(evidence)
    required = (
        "runtimeVerified",
        "modelVerified",
        "tokenizerVerified",
        "configurationVerified",
        "localDigestsPresent",
        "atomicPromotionPassed",
        "hardenedLoadPassed",
        "networkDenialPassed",
        "supersededPayloadClosed",
    )
    ready = all(flags[name] is True for name in required)
    ready = ready and flags["artifactMismatch"] is False
    ready = ready and flags["projectDependencyChanged"] is False
    ready = ready and flags["providerSharedLibraryBlocking"] is False
    ready = ready and flags["executionDependencyOutsideVerifiedRuntime"] is False
    if ready:
        outcome = "ready-with-documented-residuals"
        verdict = "TRACK 8B CONTROLLED MEASUREMENT READY WITH DOCUMENTED RESIDUALS"
    else:
        outcome = "not-ready"
        verdict = "TRACK 8B CONTROLLED MEASUREMENT NOT READY"
    return digest_document(
        {
            "artifactMismatch": flags["artifactMismatch"],
            "atomicPromotionPassed": flags["atomicPromotionPassed"],
            "calibrationStatus": "not-approved",
            "configurationVerified": flags["configurationVerified"],
            "executionDependencyOutsideVerifiedRuntime": flags[
                "executionDependencyOutsideVerifiedRuntime"
            ],
            "hardenedLoadPassed": flags["hardenedLoadPassed"],
            "installationAuthorized": False,
            "localDigestsPresent": flags["localDigestsPresent"],
            "measurementAuthorization": "not-authorized",
            "measurementPerformed": False,
            "modelVerified": flags["modelVerified"],
            "networkDenialPassed": flags["networkDenialPassed"],
            "productionReady": False,
            "projectDependencyChanged": flags["projectDependencyChanged"],
            "providerSharedLibraryBlocking": flags["providerSharedLibraryBlocking"],
            "quantizationApproved": False,
            "readinessOutcome": outcome,
            "realModelExecuted": False,
            "runtimeVerified": flags["runtimeVerified"],
            "schemaVersion": "1.0.0",
            "selectionOutcome": "no-selection",
            "supersededPayloadClosed": flags["supersededPayloadClosed"],
            "tokenizerVerified": flags["tokenizerVerified"],
            "verdict": verdict,
        }
    )


def sealed_prerequisites() -> dict[str, Any]:
    """Seal the evidence-backed prerequisite decision. Measurement stays unauthorized."""
    evidence = build_acquisition_evidence()
    if evidence["providerSharedLibraryDisposition"] != provider_disposition():
        raise PrerequisiteError("provider-library")
    if evidence["track8bMeasurementAuthorization"] != "not-authorized":
        raise PrerequisiteError("authorization")
    if any(
        item["executableEligibility"] or item["verifiedStateEligibility"]
        for item in evidence["attemptDecisions"]
    ):
        raise PrerequisiteError("cleanup")
    promoted = [
        item for item in evidence["retainedIdentities"] if item["verifiedStateEligibility"] is True
    ]
    if [item["attemptClass"] for item in promoted] != ["verified-runtime", "verified-candidate"]:
        raise PrerequisiteError("cleanup")
    return decide_prerequisites(_SEALED)


def load_measurement_prerequisites(root: Path | None = None) -> dict[str, Any]:
    """Load the committed prerequisite record and require the sealed decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise PrerequisiteError("record-type")
    validate("track8b-measurement-prerequisites", loaded)
    if loaded != sealed_prerequisites():
        raise PrerequisiteError("record-drift")
    return loaded
