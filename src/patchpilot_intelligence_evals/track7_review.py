"""Principal Architect review of Track 7. Approval does not authorize acquisition."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import ARTIFACT_CAP
from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    decide_candidate_discovery,
)
from patchpilot_intelligence_evals.explanation_suitability import decide_explanation_suitability
from patchpilot_intelligence_evals.finalist_budget import decide_finalist_budget
from patchpilot_intelligence_evals.finalist_eligibility import decide_finalist_eligibility
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.track7_selection import decide_track7_selection
from patchpilot_intelligence_evals.track8_authorization import decide_track8_authorization

_RECORD = Path("candidates/authorization/track7-implementation-review.json")
_FOOTPRINT = 9_446_591_609
_EXCESS = _FOOTPRINT - ARTIFACT_CAP
_LIVE_BLOCKERS = (
    "artifact-footprint-exceeds-8gib",
    "explanation-suitability-unresolved",
    "local-resource-fit",
    "peak-memory-unknown",
    "unresolved-conflict",
)
_COMPONENTS: tuple[tuple[str, str, str], ...] = (
    (
        "candidate-landscape",
        "approved",
        "The Track 7 candidate landscape is approved.",
    ),
    (
        "candidate-selection",
        "approved",
        "Candidate selection remains no-selection.",
    ),
    (
        "track8-acquisition",
        "approved",
        "Track 8 acquisition remains not-authorized.",
    ),
)
_BLOCKERS: tuple[tuple[str, str], ...] = (
    (
        "footprint-exceeds-8gib",
        "The complete footprint exceeds 8 GiB by 856,657,017 bytes.",
    ),
    ("fp32-peak-memory-unknown", "FP32 peak memory is unknown."),
    (
        "explanation-suitability-unresolved",
        "Explanation suitability remains unresolved.",
    ),
    ("safety-limitations-unresolved", "Safety limitations remain unresolved."),
    (
        "mandatory-criteria-unmet",
        "No candidate passes all mandatory criteria.",
    ),
)
_NOT_AUTHORIZED: tuple[str, ...] = (
    "candidate selection",
    "runtime installation",
    "model acquisition",
    "tokenizer acquisition",
    "conversion",
    "quantization",
    "inference",
    "gate changes",
    "PatchPilot composition",
)


class Track7ReviewError(ValueError):
    """A Track 7 review check failed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_track7_review() -> dict[str, Any]:
    """Build the accepted fail-closed review and seal its digest."""
    document: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "reviewStatus": "accepted-by-principal-systems-architect",
        "reviewDate": "2026-11-11",
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "decision": "track 7 candidate landscape approved and acquisition withheld",
        "authorizedScope": "This approval accepts the Track 7 fail-closed landscape only.",
        "landscapeDisposition": "approved",
        "candidateDecision": "no-selection",
        "track8Authorization": "not-authorized",
        "discoveryCandidateCount": 8,
        "finalistCount": 1,
        "finalistModelId": LFM_MODEL_ID,
        "footprintBytes": _FOOTPRINT,
        "artifactCapBytes": ARTIFACT_CAP,
        "excessBytes": _EXCESS,
        "peakMemoryBytes": None,
        "weightedScore": None,
        "qualifyingCandidateCount": 0,
        "selectionOutcome": "no-selection",
        "componentReviews": [
            {
                "componentId": component_id,
                "disposition": disposition,
                "statement": statement,
            }
            for component_id, disposition, statement in _COMPONENTS
        ],
        "acceptedBlockers": [
            {"blockerId": blocker_id, "statement": statement} for blocker_id, statement in _BLOCKERS
        ],
        "notAuthorized": list(_NOT_AUTHORIZED),
        "locallyObservedArtifactDigests": [],
    }
    document["reviewDigest"] = review_digest(document)
    return validate_track7_review(document)


def validate_track7_review(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the review and require the live fail-closed outcomes."""
    validate("track7-implementation-review", document)
    if document["reviewDigest"] != review_digest(document):
        raise Track7ReviewError("review-digest")
    if document["locallyObservedArtifactDigests"] != []:
        raise Track7ReviewError("local-digest")
    if _EXCESS != 856_657_017 or document["excessBytes"] != _EXCESS:
        raise Track7ReviewError("excess")
    observed_components = [
        (item["componentId"], item["disposition"], item["statement"])
        for item in document["componentReviews"]
    ]
    if tuple(observed_components) != _COMPONENTS:
        raise Track7ReviewError("components")
    observed_blockers = [
        (item["blockerId"], item["statement"]) for item in document["acceptedBlockers"]
    ]
    if tuple(observed_blockers) != _BLOCKERS:
        raise Track7ReviewError("blockers")
    if tuple(document["notAuthorized"]) != _NOT_AUTHORIZED:
        raise Track7ReviewError("not-authorized")
    _require_live_outcomes(document)
    return document


def load_track7_review(root: Path | None = None) -> dict[str, Any]:
    """Load the review and require it to match the sealed record."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise Track7ReviewError("record-type")
    document = validate_track7_review(loaded)
    if document != decide_track7_review():
        raise Track7ReviewError("review-drift")
    return document


def _require_live_outcomes(document: dict[str, Any]) -> None:
    discovery = decide_candidate_discovery()
    eligibility = decide_finalist_eligibility()["finalists"][0]
    budget = decide_finalist_budget()
    finalist_budget = budget["finalists"][0]
    suitability = decide_explanation_suitability()["finalists"][0]
    selection = decide_track7_selection()
    authorization = decide_track8_authorization()
    if discovery["discoveryCandidateCount"] != 8 or discovery["finalistCount"] != 1:
        raise Track7ReviewError("discovery")
    if discovery["finalistModelIds"] != [LFM_MODEL_ID]:
        raise Track7ReviewError("discovery")
    if eligibility["weightedScore"] is not None or eligibility["mandatoryStatus"] != "fail":
        raise Track7ReviewError("eligibility")
    if (
        eligibility["disqualifiers"] != ["local-resource-fit"]
        or not eligibility["unresolvedConflict"]
    ):
        raise Track7ReviewError("eligibility")
    if (
        finalist_budget["footprintBytes"] != _FOOTPRINT
        or budget["artifactCapBytes"] != ARTIFACT_CAP
    ):
        raise Track7ReviewError("budget")
    if finalist_budget["peakMemoryBytes"] is not None or finalist_budget["hardwareFit"] != "fail":
        raise Track7ReviewError("budget")
    if suitability["suitabilityOutcome"] != "unresolved":
        raise Track7ReviewError("suitability")
    if selection["selectionOutcome"] != "no-selection" or selection["selectedModelId"] is not None:
        raise Track7ReviewError("selection")
    if (
        selection["qualifyingCandidateCount"] != 0
        or selection["candidates"][0]["weightedScore"] is not None
    ):
        raise Track7ReviewError("selection")
    if authorization["authorizationOutcome"] != "not-authorized":
        raise Track7ReviewError("authorization")
    if authorization["verdict"] != "TRACK 8 CONTROLLED ACQUISITION NOT AUTHORIZED":
        raise Track7ReviewError("authorization")
    if authorization["installationAuthorized"] is not False:
        raise Track7ReviewError("authorization")
    if tuple(authorization["blockers"]) != _LIVE_BLOCKERS:
        raise Track7ReviewError("authorization")
    if document["finalistModelId"] != LFM_MODEL_ID:
        raise Track7ReviewError("identity")
