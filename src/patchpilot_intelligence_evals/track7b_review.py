"""Principal Architect review of Track 7B. Approval does not start measurement."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.candidate_discovery import (
    LFM_MODEL_ID,
    contains_private_marker,
)
from patchpilot_intelligence_evals.explanation_suitability import (
    decide_explanation_suitability,
    rejects_quality_claim,
)
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.measurement_authorization import decide_measurement_authorization
from patchpilot_intelligence_evals.memory_budget import decide_memory_budget
from patchpilot_intelligence_evals.memory_evidence import decide_memory_evidence
from patchpilot_intelligence_evals.memory_model import (
    BYTES_PER_FP32,
    CATEGORY_IDS,
    LOGICAL_PARAMETER_BYTES,
    PARAMETER_COUNT,
    decide_memory_model,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.suitability_contract import SAFETY_CRITICAL
from patchpilot_intelligence_evals.suitability_evidence import decide_suitability_evidence
from patchpilot_intelligence_evals.track7_selection import decide_track7_selection
from patchpilot_intelligence_evals.track7a_review import decide_track7a_review
from patchpilot_intelligence_evals.track8_authorization import decide_track8_authorization
from patchpilot_intelligence_evals.track8b_readiness import decide_track8b_readiness

_RECORD = Path("candidates/authorization/track7b-implementation-review.json")
_SCOPE = (
    "This approval accepts the Track 7B evidence closure and authorizes a future "
    "narrowly controlled measurement Session in principle with documented residuals. "
    "Track 8B is ready only for a separately specified and reviewed controlled "
    "measurement Session. This review does not authorize operators or Cursor to begin "
    "acquisition, installation, or execution. A later Session must separately authorize "
    "runtime staging, artifact acquisition, digest verification, atomic promotion, "
    "hardened execution, measurement commands, stop conditions, result handling, and cleanup."
)
_SUPPORTED = (
    "instruction-following",
    "structured-output",
    "english-language",
    "context-capacity",
)
_EMPIRICAL = (
    "bounded-generation",
    "deterministic-fact-separation",
    "evidence-id-reproduction",
    "missing-evidence-reporting",
    "uncertainty-expression",
    "unsupported-request-refusal",
    "embedded-instruction-resistance",
    "state-mutation-avoidance",
    "cross-tenant-nondisclosure",
    "schema-compatibility",
)
_COMPONENTS: tuple[tuple[str, str, str, str], ...] = (
    (
        "memory-model-contract",
        "memoryModelContract",
        "approved",
        "The memory-model contract is approved.",
    ),
    (
        "official-memory-evidence",
        "officialMemoryEvidence",
        "approved",
        "The official memory-evidence review is approved.",
    ),
    (
        "envelope-4096",
        "envelope4096",
        "unresolved",
        "The 4096-token FP32 resident envelope remains unresolved.",
    ),
    (
        "envelope-8192",
        "envelope8192",
        "unresolved",
        "The 8192-token FP32 resident envelope remains unresolved.",
    ),
    (
        "explanation-suitability-contract",
        "explanationSuitabilityContract",
        "approved",
        "The explanation-suitability contract is approved.",
    ),
    (
        "official-suitability-screening",
        "suitabilityScreening",
        "eligible-for-controlled-evaluation",
        "Official suitability screening is eligible for controlled evaluation.",
    ),
    (
        "measured-behavioral-quality",
        "measuredBehavioralQuality",
        "not-established",
        "Measured behavioral quality is not established.",
    ),
    (
        "controlled-measurement",
        "controlledMeasurement",
        "authorized-in-principle-with-documented-residuals",
        "Controlled measurement is authorized in principle with documented residuals.",
    ),
)
_RESIDUALS: tuple[tuple[str, str], ...] = (
    (
        "resident-upper-bounds-unavailable",
        "Resident upper bounds remain unavailable for both context sizes.",
    ),
    ("safety-margin-unset", "The safety margin remains unset."),
    ("graph-not-parsed", "The ONNX graph has not been parsed."),
    ("local-digests-empty", "Local artifact digests are empty."),
    (
        "runtime-and-allocator-overhead-unmeasured",
        "ONNX Runtime resident process and allocator overhead are unmeasured.",
    ),
    (
        "architecture-state-and-activation-unresolved",
        "Architecture-state and activation bounds are unresolved.",
    ),
    ("behavioral-metrics-unmeasured", "Behavioral metrics are unmeasured."),
    (
        "knowledge-intensive-task-caveat",
        "The official knowledge-intensive-task caveat remains applicable.",
    ),
    ("installation-not-authorized", "Runtime installation remains unauthorized."),
    ("candidate-artifacts-unacquired", "Candidate artifacts remain unacquired."),
    (
        "adapter-executable-state-unavailable",
        "The adapter executable state remains unavailable.",
    ),
)
_LATER: tuple[str, ...] = (
    "runtime staging",
    "artifact acquisition",
    "digest verification",
    "atomic promotion",
    "hardened execution",
    "measurement commands",
    "stop conditions",
    "result handling",
    "cleanup",
)
_NOT_AUTHORIZED: tuple[str, ...] = (
    "candidate selection",
    "Track 8 acquisition",
    "runtime installation",
    "model, tokenizer, configuration, or ONNX acquisition",
    "conversion",
    "quantization",
    "inference in this Session",
    "execution in this Session",
    "evaluation-gate changes",
    "shadow mode",
    "PatchPilot production composition",
    "starting measurement from this review",
)
_DIGEST_FIELDS = (
    "locallyObservedRuntimeDigests",
    "locallyObservedModelDigests",
    "locallyObservedTokenizerDigests",
    "locallyObservedConfigurationDigests",
    "locallyObservedOnnxArtifactDigests",
    "locallyObservedArtifactDigests",
)


class Track7BReviewError(ValueError):
    """A Track 7B review check failed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def decide_track7b_review() -> dict[str, Any]:
    """Build the accepted evidence review and seal its digest."""
    document: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "runtimeInstallationStatus": "not-installed",
        "acquisitionStatus": "not-acquired",
        "conversionStatus": "not-performed",
        "executionStatus": "not-executed",
        "measurementPerformed": False,
        "reviewStatus": "accepted-by-principal-systems-architect",
        "reviewDate": "2026-11-12",
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "decision": (
            "track 7b evidence closure approved and measurement authorized "
            "in principle with residuals"
        ),
        "authorizedScope": _SCOPE,
        "finalistModelId": LFM_MODEL_ID,
        "parameterCount": PARAMETER_COUNT,
        "bytesPerFp32Parameter": BYTES_PER_FP32,
        "logicalFp32ProductBytes": LOGICAL_PARAMETER_BYTES,
        "logicalProductIncludedInPeak": False,
        "processMemoryCeilingBytes": MEMORY_CAP,
        "ceilingUnchanged": True,
        "candidateDecision": "no-selection",
        "selectionOutcome": "no-selection",
        "weightedScore": None,
        "qualifyingCandidateCount": 0,
        "acquisitionAuthorization": "not-authorized",
        "installationAuthorized": False,
        "executionAuthorized": False,
        "calibrationApprovalStatus": "not-approved",
        "storageDecision": "unchanged",
        "track8aReadinessOutcome": "not-ready",
        "track8bReadiness": "ready-for-controlled-measurement",
        "unresolvedResidentCategories": list(CATEGORY_IDS),
        "supportedInPrinciple": list(_SUPPORTED),
        "empiricalEvaluationRequired": list(_EMPIRICAL),
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
        "laterSessionMustAuthorize": list(_LATER),
        "notAuthorized": list(_NOT_AUTHORIZED),
    }
    for field in _DIGEST_FIELDS:
        document[field] = []
    for _component_id, field, disposition, _statement in _COMPONENTS:
        document[field] = disposition
    document["reviewDigest"] = review_digest(document)
    return validate_track7b_review(document)


def validate_track7b_review(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the review and require the live Track 7B outcomes."""
    validate("track7b-implementation-review", document)
    if contains_private_marker(document) or rejects_quality_claim(document):
        raise Track7BReviewError("quality-claim")
    if document["reviewDigest"] != review_digest(document):
        raise Track7BReviewError("review-digest")
    if (
        document["processMemoryCeilingBytes"] != MEMORY_CAP
        or document["ceilingUnchanged"] is not True
    ):
        raise Track7BReviewError("ceiling")
    if document["logicalProductIncludedInPeak"] is not False:
        raise Track7BReviewError("parameter-product")
    if document["logicalFp32ProductBytes"] != LOGICAL_PARAMETER_BYTES:
        raise Track7BReviewError("parameter-product")
    if document["parameterCount"] != PARAMETER_COUNT or document["bytesPerFp32Parameter"] != 4:
        raise Track7BReviewError("parameter-product")
    for field in _DIGEST_FIELDS:
        if document[field] != []:
            raise Track7BReviewError("local-digest")
    observed = [
        (item["componentId"], item["disposition"], item["statement"])
        for item in document["componentReviews"]
    ]
    expected = [
        (component_id, disposition, statement)
        for component_id, _field, disposition, statement in _COMPONENTS
    ]
    if observed != expected:
        raise Track7BReviewError("components")
    for _component_id, field, disposition, _statement in _COMPONENTS:
        if document[field] != disposition:
            raise Track7BReviewError(field)
    residuals = [(item["residualId"], item["statement"]) for item in document["acceptedResiduals"]]
    if residuals != list(_RESIDUALS):
        raise Track7BReviewError("residuals")
    if tuple(document["notAuthorized"]) != _NOT_AUTHORIZED:
        raise Track7BReviewError("not-authorized")
    if tuple(document["laterSessionMustAuthorize"]) != _LATER:
        raise Track7BReviewError("later-session")
    if tuple(document["unresolvedResidentCategories"]) != CATEGORY_IDS:
        raise Track7BReviewError("categories")
    if tuple(document["supportedInPrinciple"]) != _SUPPORTED:
        raise Track7BReviewError("supported")
    if tuple(document["empiricalEvaluationRequired"]) != _EMPIRICAL:
        raise Track7BReviewError("empirical")
    if set(_EMPIRICAL) != set(SAFETY_CRITICAL) | {"bounded-generation"}:
        raise Track7BReviewError("empirical")
    _require_live_outcomes(document)
    return document


def load_track7b_review(root: Path | None = None) -> dict[str, Any]:
    """Load the review and require it to match the sealed record."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise Track7BReviewError("record-type")
    document = validate_track7b_review(loaded)
    if document != decide_track7b_review():
        raise Track7BReviewError("review-drift")
    return document


def _require_live_outcomes(document: dict[str, Any]) -> None:
    model = decide_memory_model()
    evidence = decide_memory_evidence()
    budget = decide_memory_budget()
    suitability = decide_suitability_evidence()
    measurement = decide_measurement_authorization()
    readiness = decide_track8b_readiness()
    selection = decide_track7_selection()
    authorization = decide_track8_authorization()
    prior = decide_track7a_review()
    legacy = decide_explanation_suitability()["finalists"][0]["suitabilityOutcome"]
    product = model["parameterRepresentation"]
    if (
        product["parameterCount"] != PARAMETER_COUNT
        or product["bytesPerParameter"] != BYTES_PER_FP32
        or product["logicalProductBytes"] != LOGICAL_PARAMETER_BYTES
        or product["logicalProductIncludedInPeak"] is not False
    ):
        raise Track7BReviewError("parameter-product")
    if model["ceilingBytes"] != MEMORY_CAP:
        raise Track7BReviewError("ceiling")
    if evidence["graphParsed"] is not False:
        raise Track7BReviewError("graph")
    _require_unresolved_categories(evidence["categories"])
    contexts = [envelope["contextTokens"] for envelope in budget["envelopes"]]
    if contexts != [4096, 8192]:
        raise Track7BReviewError("envelope")
    for envelope in budget["envelopes"]:
        _require_unresolved_envelope(envelope)
    if suitability["screeningOutcome"] != "eligible-for-controlled-evaluation":
        raise Track7BReviewError("screening")
    if suitability["measuredQualityClaimed"] is not False:
        raise Track7BReviewError("quality-claim")
    _require_capability_split(suitability["capabilities"])
    if measurement["authorizationOutcome"] != "authorized-with-documented-residuals":
        raise Track7BReviewError("measurement")
    if measurement["measurementPerformed"] is not False or measurement["installationAuthorized"]:
        raise Track7BReviewError("measurement")
    if readiness["readinessOutcome"] != "ready-for-controlled-measurement":
        raise Track7BReviewError("readiness")
    if readiness["acquisitionAuthorization"] != "not-authorized":
        raise Track7BReviewError("acquisition")
    if (
        selection["selectionOutcome"] != "no-selection"
        or selection["qualifyingCandidateCount"] != 0
        or selection["candidates"][0]["weightedScore"] is not None
    ):
        raise Track7BReviewError("selection")
    if authorization["authorizationOutcome"] != "not-authorized":
        raise Track7BReviewError("acquisition")
    if authorization["installationAuthorized"] is not False:
        raise Track7BReviewError("installation")
    if (
        prior["storageOnlyBlocker"] != "resolved"
        or prior["atomicPromotion"] != "approved-with-documented-residuals"
        or prior["copyPromotion"] != "failed"
        or prior["peakMemoryBasis"] != "unknown-fp32"
        or prior["explanationSuitability"] != "unresolved"
    ):
        raise Track7BReviewError("storage")
    if legacy != "unresolved":
        raise Track7BReviewError("legacy-suitability")
    if document["finalistModelId"] != LFM_MODEL_ID:
        raise Track7BReviewError("identity")
    if document["calibrationApprovalStatus"] != "not-approved":
        raise Track7BReviewError("calibration")
    if document["storageDecision"] != "unchanged":
        raise Track7BReviewError("storage")
    _require_disabled(measurement)
    _require_disabled(readiness)


def _require_unresolved_categories(rows: list[dict[str, Any]]) -> None:
    if [row["categoryId"] for row in rows] != list(CATEGORY_IDS):
        raise Track7BReviewError("categories")
    for row in rows:
        if row["evidenceStatus"] != "unresolved":
            raise Track7BReviewError("categories")
        if row["upperBoundBytes"] is not None or row["lowerBoundBytes"] is not None:
            raise Track7BReviewError("zero-fill")
        if row["upperBoundBytes"] == 0 or row["lowerBoundBytes"] == 0:
            raise Track7BReviewError("zero-fill")
        if row["logicalBytesIncludedInPeak"] is not False:
            raise Track7BReviewError("parameter-product")


def _require_unresolved_envelope(envelope: dict[str, Any]) -> None:
    if envelope["classification"] != "unresolved" or envelope["upperBoundBytes"] is not None:
        raise Track7BReviewError("envelope")
    if envelope["lowerBoundBytes"] is not None or envelope["ceilingBytes"] != MEMORY_CAP:
        raise Track7BReviewError("envelope")
    if envelope["ceilingComparison"] != "unresolved":
        raise Track7BReviewError("envelope")
    if envelope["unresolvedCategoryIds"] != list(CATEGORY_IDS):
        raise Track7BReviewError("categories")
    _require_unresolved_categories(envelope["categories"])
    static = envelope["categories"][0]
    if static["logicalBytes"] != LOGICAL_PARAMETER_BYTES:
        raise Track7BReviewError("parameter-product")


def _require_capability_split(rows: list[dict[str, Any]]) -> None:
    supported = [row["capabilityId"] for row in rows if row["result"] == "supported-in-principle"]
    empirical = [
        row["capabilityId"] for row in rows if row["result"] == "requires-empirical-evaluation"
    ]
    if tuple(supported) != _SUPPORTED or tuple(empirical) != _EMPIRICAL:
        raise Track7BReviewError("capabilities")
    for row in rows:
        if row["capabilityId"] in _EMPIRICAL and row["empiricalEvaluationRequired"] is not True:
            raise Track7BReviewError("empirical")
        if row["disqualifyingLimitation"] is not False:
            raise Track7BReviewError("disqualifier")


def _require_disabled(document: dict[str, Any]) -> None:
    if document["locallyObservedArtifactDigests"] != []:
        raise Track7BReviewError("local-digest")
    if (
        document["acquisitionStatus"] != "not-acquired"
        or document["runtimeInstallationStatus"] != "not-installed"
        or document["conversionStatus"] != "not-performed"
        or document["executionStatus"] != "not-executed"
        or document["realModelExecuted"] is not False
        or document["productionReady"] is not False
        or document["measurementPerformed"] is not False
        or document["selectionOutcome"] != "no-selection"
        or document["weightedScore"] is not None
        or document["qualifyingCandidateCount"] != 0
    ):
        raise Track7BReviewError("disabled")
