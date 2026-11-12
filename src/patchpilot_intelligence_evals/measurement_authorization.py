"""Controlled-measurement authorization. This session does not acquire or execute a model."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    LFM_ONNX_REVISION,
    LFM_SOURCE_REVISION,
    contains_private_marker,
)
from patchpilot_intelligence_evals.memory_budget import decide_memory_budget
from patchpilot_intelligence_evals.memory_model import RETRIEVED_ON
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.suitability_evidence import decide_suitability_evidence

_RECORD = Path("candidates/authorization/controlled-measurement-authorization.json")
_RUNTIME_REVISION = "6af1a932e2286d5c58166085d24c68783033edee"
_FACT_KEYS = (
    "memoryClosed",
    "suitabilityClosed",
    "disqualifierPresent",
    "materialUnknown",
    "storageOnlyPass",
    "hardenedExecutionApproved",
    "runtimeIdentityAuthorized",
    "adapterIdentityFixed",
    "artifactIdentityFixed",
    "residualsPresent",
)
_VERDICTS = {
    "authorized": "TRACK 8B CONTROLLED MEASUREMENT AUTHORIZED",
    "authorized-with-documented-residuals": (
        "TRACK 8B CONTROLLED MEASUREMENT AUTHORIZED WITH DOCUMENTED RESIDUALS"
    ),
    "not-authorized": "TRACK 8B CONTROLLED MEASUREMENT NOT AUTHORIZED",
    "blocked-by-unresolved-authority": "BLOCKED BY UNRESOLVED AUTHORITY",
}


class MeasurementAuthorizationError(ValueError):
    """A measurement-authorization record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def classify_measurement(facts: Mapping[str, Any]) -> dict[str, str]:
    """Decide whether a future measurement session is justified. This one does not run it."""
    if set(facts) != set(_FACT_KEYS):
        raise MeasurementAuthorizationError("facts")
    if any(not isinstance(facts[key], bool) for key in _FACT_KEYS):
        raise MeasurementAuthorizationError("facts")
    if not facts["artifactIdentityFixed"] or not facts["runtimeIdentityAuthorized"]:
        outcome, reason = "blocked-by-unresolved-authority", "unresolved-authority"
    elif facts["disqualifierPresent"]:
        outcome, reason = "not-authorized", "disqualified"
    elif facts["memoryClosed"] and facts["suitabilityClosed"]:
        outcome, reason = "not-authorized", "evidence-closed"
    elif not facts["materialUnknown"]:
        outcome, reason = "not-authorized", "unresolved-without-justification"
    elif not (
        facts["storageOnlyPass"]
        and facts["hardenedExecutionApproved"]
        and facts["adapterIdentityFixed"]
    ):
        outcome, reason = "not-authorized", "prerequisite-failed"
    elif facts["residualsPresent"]:
        outcome, reason = "authorized-with-documented-residuals", "measurement-required"
    else:
        outcome, reason = "authorized", "measurement-required"
    readiness = (
        "ready-for-controlled-measurement" if outcome.startswith("authorized") else "not-ready"
    )
    return {
        "authorizationOutcome": outcome,
        "verdict": _VERDICTS[outcome],
        "reason": reason,
        "readinessOutcome": readiness,
        "selectionOutcome": "no-selection",
    }


def decide_measurement_authorization() -> dict[str, Any]:
    """Recommend a narrow future measurement and keep acquisition disabled."""
    decision = classify_measurement(_committed_facts())
    document = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "locallyObservedArtifactDigests": [],
        "retrievedOn": RETRIEVED_ON,
        "finalistModelId": LFM_MODEL_ID,
        "sourceRevision": LFM_SOURCE_REVISION,
        "onnxRevision": LFM_ONNX_REVISION,
        "runtimeId": "onnxruntime",
        "runtimeVersionTag": "v1.31.1",
        "runtimeRevision": _RUNTIME_REVISION,
        "adapterId": "patchpilot-onnxruntime-adapter",
        "adapterVersion": "1.0.0",
        "profileId": "linux-bwrap-systemd-v1",
        "profileVersion": "1.0.0",
        "installationAuthorized": False,
        "measurementPerformed": False,
        "quantizationApproved": False,
        "selectionOutcome": "no-selection",
        "weightedScore": None,
        "qualifyingCandidateCount": 0,
        "acquisitionAuthorization": "not-authorized",
        "authorizationOutcome": decision["authorizationOutcome"],
        "verdict": decision["verdict"],
        "reason": decision["reason"],
        "memoryClassifications": _memory_classifications(),
        "suitabilityScreening": decide_suitability_evidence()["screeningOutcome"],
        "scope": [
            "fp32-resident-peak-at-4096-tokens",
            "fp32-resident-peak-at-8192-tokens",
            "existing-synthetic-corpus-metrics",
        ],
        "stopConditions": [
            "ceiling-byte-exceeded",
            "official-disqualifier",
            "artifact-identity-drift",
            "graph-or-external-data-mismatch",
            "network-egress",
            "conversion-or-quantization",
            "production-use",
        ],
        "residuals": [
            "resident-upper-bound-unknown",
            "safety-margin-unset",
            "graph-not-parsed",
            "local-digests-empty",
            "behavioral-metrics-unmeasured",
            "knowledge-task-caveat",
            "installation-not-authorized",
            "adapter-executable-state-unavailable",
        ],
    }
    return validate_measurement_authorization(document)


def validate_measurement_authorization(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the decision and the disabled acquisition state."""
    validate("controlled-measurement-authorization", document)
    if contains_private_marker(document):
        raise MeasurementAuthorizationError("identity")
    if (
        document["locallyObservedArtifactDigests"] != []
        or document["measurementPerformed"] is not False
    ):
        raise MeasurementAuthorizationError("measurement")
    if (
        document["installationAuthorized"] is not False
        or document["acquisitionStatus"] != "not-acquired"
    ):
        raise MeasurementAuthorizationError("disabled")
    if document["selectionOutcome"] != "no-selection" or document["weightedScore"] is not None:
        raise MeasurementAuthorizationError("selection")
    if document["qualifyingCandidateCount"] != 0:
        raise MeasurementAuthorizationError("selection")
    if document["acquisitionAuthorization"] != "not-authorized":
        raise MeasurementAuthorizationError("authorization")
    expected = classify_measurement(_committed_facts())
    if document["authorizationOutcome"] != expected["authorizationOutcome"]:
        raise MeasurementAuthorizationError("outcome")
    if document["verdict"] != expected["verdict"] or document["reason"] != expected["reason"]:
        raise MeasurementAuthorizationError("outcome")
    if document["memoryClassifications"] != _memory_classifications():
        raise MeasurementAuthorizationError("memory")
    screening = decide_suitability_evidence()["screeningOutcome"]
    if document["suitabilityScreening"] != screening:
        raise MeasurementAuthorizationError("suitability")
    return document


def load_measurement_authorization(root: Path | None = None) -> dict[str, Any]:
    """Load the committed authorization and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementAuthorizationError("record-type")
    document = validate_measurement_authorization(loaded)
    if document != decide_measurement_authorization():
        raise MeasurementAuthorizationError("record-drift")
    return document


def _committed_facts() -> dict[str, bool]:
    classifications = _memory_classifications()
    screening = decide_suitability_evidence()["screeningOutcome"]
    memory_closed = classifications == ["proven-pass", "proven-pass"]
    suitability_closed = screening == "evidence-closed"
    return {
        "memoryClosed": memory_closed,
        "suitabilityClosed": suitability_closed,
        "disqualifierPresent": screening == "disqualified",
        "materialUnknown": not memory_closed or not suitability_closed,
        "storageOnlyPass": True,
        "hardenedExecutionApproved": True,
        "runtimeIdentityAuthorized": True,
        "adapterIdentityFixed": True,
        "artifactIdentityFixed": True,
        "residualsPresent": True,
    }


def _memory_classifications() -> list[str]:
    budget = decide_memory_budget()
    return [str(item["classification"]) for item in budget["envelopes"]]
