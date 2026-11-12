"""Track 8B readiness. A measurement recommendation does not authorize acquisition."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    contains_private_marker,
)
from patchpilot_intelligence_evals.measurement_authorization import (
    classify_measurement,
    decide_measurement_authorization,
)
from patchpilot_intelligence_evals.memory_model import RETRIEVED_ON
from patchpilot_intelligence_evals.schemas import repo_root, validate

_RECORD = Path("candidates/authorization/track8b-readiness.json")


class Track8BReadinessError(ValueError):
    """A Track 8B readiness record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_track8b_readiness() -> dict[str, Any]:
    """Record measurement readiness while Track 8 acquisition stays not authorized."""
    authorization = decide_measurement_authorization()
    decision = classify_measurement(_facts_from(authorization))
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
        "readinessOutcome": decision["readinessOutcome"],
        "verdict": authorization["verdict"],
        "measurementAuthorization": authorization["authorizationOutcome"],
        "measurementReason": authorization["reason"],
        "measurementPerformed": False,
        "installationAuthorized": False,
        "quantizationApproved": False,
        "selectionOutcome": "no-selection",
        "selectedModelId": None,
        "weightedScore": None,
        "qualifyingCandidateCount": 0,
        "acquisitionAuthorization": "not-authorized",
        "track8aReadinessOutcome": "not-ready",
        "storageBlocker": "resolved",
        "memoryClassifications": authorization["memoryClassifications"],
        "suitabilityScreening": authorization["suitabilityScreening"],
    }
    return validate_track8b_readiness(document)


def validate_track8b_readiness(document: dict[str, Any]) -> dict[str, Any]:
    """Validate readiness against the measurement decision and the disabled states."""
    validate("track8b-readiness", document)
    if contains_private_marker(document):
        raise Track8BReadinessError("identity")
    if (
        document["locallyObservedArtifactDigests"] != []
        or document["measurementPerformed"] is not False
    ):
        raise Track8BReadinessError("measurement")
    if (
        document["installationAuthorized"] is not False
        or document["realModelExecuted"] is not False
    ):
        raise Track8BReadinessError("disabled")
    if document["productionReady"] is not False or document["acquisitionStatus"] != "not-acquired":
        raise Track8BReadinessError("disabled")
    if (
        document["executionStatus"] != "not-executed"
        or document["conversionStatus"] != "not-performed"
    ):
        raise Track8BReadinessError("disabled")
    if document["selectionOutcome"] != "no-selection" or document["weightedScore"] is not None:
        raise Track8BReadinessError("selection")
    if document["qualifyingCandidateCount"] != 0 or document["selectedModelId"] is not None:
        raise Track8BReadinessError("selection")
    if document["acquisitionAuthorization"] != "not-authorized":
        raise Track8BReadinessError("authorization")
    if (
        document["track8aReadinessOutcome"] != "not-ready"
        or document["storageBlocker"] != "resolved"
    ):
        raise Track8BReadinessError("storage")
    authorization = decide_measurement_authorization()
    if document["measurementAuthorization"] != authorization["authorizationOutcome"]:
        raise Track8BReadinessError("outcome")
    if document["verdict"] != authorization["verdict"]:
        raise Track8BReadinessError("outcome")
    if document["memoryClassifications"] != authorization["memoryClassifications"]:
        raise Track8BReadinessError("memory")
    if document["suitabilityScreening"] != authorization["suitabilityScreening"]:
        raise Track8BReadinessError("suitability")
    expected = classify_measurement(_facts_from(authorization))
    if document["readinessOutcome"] != expected["readinessOutcome"]:
        raise Track8BReadinessError("readiness")
    return document


def load_track8b_readiness(root: Path | None = None) -> dict[str, Any]:
    """Load the committed readiness record and require it to match the decision."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise Track8BReadinessError("record-type")
    document = validate_track8b_readiness(loaded)
    if document != decide_track8b_readiness():
        raise Track8BReadinessError("record-drift")
    return document


def _facts_from(authorization: Mapping[str, Any]) -> dict[str, bool]:
    """Rebuild the committed facts. Synthetic paths call classify_measurement directly."""
    classifications = authorization["memoryClassifications"]
    screening = authorization["suitabilityScreening"]
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
        "residualsPresent": bool(authorization["residuals"]),
    }
