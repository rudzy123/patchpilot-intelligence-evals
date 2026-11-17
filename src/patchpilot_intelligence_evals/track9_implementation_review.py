"""Principal Architect review of Track 9. Approval does not start execution."""

from __future__ import annotations

import json
from typing import Any

from patchpilot_intelligence_evals.acquisition_plan import reject_sensitive
from patchpilot_intelligence_evals.behavioral_evidence_review import (
    load_behavioral_evidence_review,
)
from patchpilot_intelligence_evals.candidate_disposition import load_candidate_disposition
from patchpilot_intelligence_evals.corpus_continuation_authorization import (
    load_corpus_continuation_authorization,
)
from patchpilot_intelligence_evals.evaluation_evidence_review import (
    load_evaluation_evidence_inventory,
)
from patchpilot_intelligence_evals.implementation_review import review_digest
from patchpilot_intelligence_evals.inference_retry_plan import CONSUMED_RETRY_PLAN_DIGEST
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.memory_evidence_review import load_memory_evidence_review
from patchpilot_intelligence_evals.proportionality_decision import (
    SELECTED_ALTERNATIVE,
    load_proportionality_decision,
)
from patchpilot_intelligence_evals.schemas import repo_root, validate
from patchpilot_intelligence_evals.track9_review import (
    CEILING_BYTES,
    COLD_4096_PEAK_BYTES,
    COLD_8192_PEAK_BYTES,
    HEADROOM_BYTES,
    PLAN_DIGEST,
    PRIOR_PLAN_DIGEST,
    WARM_4096_PEAK_BYTES,
    WARM_8192_PEAK_BYTES,
    common,
    reject_track9_text,
)

SCHEMA_NAME = "track9-implementation-review"
_RECORD = "candidates/authorization/track9-implementation-review.json"
_SCOPE = (
    "This approval accepts the Track 9 evidence review and authorizes one future "
    "clean 24-case corpus-only Session in principle. It does not authorize current "
    "execution, a measurement or execution plan, a plan digest, a result root, "
    "candidate selection, calibration approval, PatchPilot integration, shadow mode, "
    "production use, release, or deployment."
)
_ALTERNATIVES: tuple[dict[str, Any], ...] = (
    {
        "alternativeId": "reject-now",
        "decision": "withheld",
        "reason": "no-supported-mandatory-candidate-failure",
        "selected": False,
    },
    {
        "alternativeId": "remaining-19",
        "decision": "rejected",
        "reason": "not-one-uniform-comparable-result",
        "selected": False,
    },
    {
        "alternativeId": SELECTED_ALTERNATIVE,
        "decision": "selected",
        "reason": "uniform-complete-corpus",
        "selected": True,
    },
    {
        "alternativeId": "narrow-forensics",
        "decision": "rejected",
        "reason": "missing-raw-output-cannot-be-recovered",
        "selected": False,
    },
    {
        "alternativeId": "stop-investment",
        "decision": "permissible",
        "reason": "not-selected",
        "selected": False,
    },
)
_COMPONENTS: tuple[tuple[str, str, str], ...] = (
    ("evidence-inventory", "approved", "The evidence inventory is approved."),
    ("memory-evidence-review", "approved", "The memory evidence review is approved."),
    (
        "behavioral-evidence-review",
        "approved",
        "The behavioral evidence review is approved.",
    ),
    ("proportionality-analysis", "approved", "The proportionality analysis is approved."),
    (
        "corpus-only-continuation",
        "authorized-in-principle",
        "The corpus-only continuation is authorized in principle.",
    ),
)
_RESIDUALS: tuple[tuple[str, str], ...] = (
    ("limited-headroom", "The measured resident headroom is limited."),
    (
        "unresolved-schema-failure-authority",
        "Schema-failure authority remains unresolved.",
    ),
    (
        "partial-behavioral-evidence",
        "Behavioral evidence remains partial and is not scored.",
    ),
)
_NOT_AUTHORIZED: tuple[str, ...] = (
    "current-execution",
    "measurement-or-execution-plan",
    "plan-digest",
    "result-root",
    "candidate-selection",
    "calibration-approval",
    "patchpilot-integration",
    "shadow-mode",
    "production-use",
    "release-or-deployment",
)
_TRACK9 = "corpus-only-continuation-authorized-in-principle"
_CANDIDATE = "evaluation-incomplete-continuation-authorized-in-principle"


def _sources() -> dict[str, dict[str, Any]]:
    return {
        "behavioralEvidenceReview": load_behavioral_evidence_review(),
        "candidateDisposition": load_candidate_disposition(),
        "corpusContinuationAuthorization": load_corpus_continuation_authorization(),
        "evidenceInventory": load_evaluation_evidence_inventory(),
        "memoryEvidenceReview": load_memory_evidence_review(),
        "proportionalityDecision": load_proportionality_decision(),
    }


def _memory() -> dict[str, Any]:
    return {
        "ceilingBytes": CEILING_BYTES,
        "cold4096PeakBytes": COLD_4096_PEAK_BYTES,
        "cold8192PeakBytes": COLD_8192_PEAK_BYTES,
        "concurrency": "prohibited",
        "headroomAssessment": "limited",
        "largerContext": "not-authorized",
        "memoryGate": "passed",
        "minimumHeadroomBytes": HEADROOM_BYTES,
        "productionCapacity": "not-established",
        "warm4096PeakBytes": WARM_4096_PEAK_BYTES,
        "warm8192PeakBytes": WARM_8192_PEAK_BYTES,
    }


def _behavior() -> dict[str, Any]:
    return {
        "behavioralConclusion": "partial-inconclusive",
        "behavioralMeasurementAttempted": True,
        "behavioralMeasurementCompleted": False,
        "candidateEvaluatedCompletely": False,
        "candidateMetricsProduced": False,
        "completeCaseGroups": 5,
        "empiricalCapabilityConclusions": "unavailable",
        "missingCompleteCases": 19,
        "schemaComplianceConclusion": "unavailable",
        "schemaFailureAuthority": "unresolved",
        "sealedRunRecords": 15,
        "unsealedLaunchCount": 1,
    }


def _boundary() -> dict[str, Any]:
    return {
        "batchSize": 1,
        "caseCount": 24,
        "decodingConfigurationUnchanged": True,
        "diagnosticsRecordedSeparately": True,
        "failureAuthorityRecordedPerRun": True,
        "futureOperatorApproval": "not-issued",
        "futureOperatorApprovalRequired": True,
        "futurePlanDigest": "not-issued",
        "futurePlanRequired": True,
        "futureResultRoot": "not-created",
        "futureResultRootRequired": True,
        "futureSpecification": "required",
        "gatesUnchanged": True,
        "goldAndEvaluatorHidden": True,
        "maxNewTokens": 256,
        "metricsUnchanged": True,
        "plannedRuns": 72,
        "promptsUnchanged": True,
        "rawOutputRetention": "required",
        "repeatContext4096": False,
        "repeatContext8192": False,
        "repetitionsPerCase": 3,
        "responseSchemaUnchanged": True,
        "reuseAcceptedMemoryEvidence": True,
        "sameHardenedExecutionBoundary": True,
        "sameVerifiedRuntimeAndCandidate": True,
    }


def _plans() -> list[dict[str, Any]]:
    return [
        {"planDigest": PRIOR_PLAN_DIGEST, "reusable": False},
        {"planDigest": CONSUMED_RETRY_PLAN_DIGEST, "reusable": False},
        {"planDigest": PLAN_DIGEST, "reusable": False},
    ]


def assemble_track9_review() -> dict[str, Any]:
    """Assemble the approved review before its digest is sealed."""
    sources = _sources()
    document = {
        **common(),
        "acceptedResiduals": [
            {"residualId": residual_id, "statement": statement}
            for residual_id, statement in _RESIDUALS
        ],
        "alternativeDecisions": [dict(row) for row in _ALTERNATIVES],
        "authorizedScope": _SCOPE,
        "behavioralEvidence": _behavior(),
        "behavioralEvidenceReview": "approved",
        "candidateDisposition": _CANDIDATE,
        "componentReviews": [
            {"componentId": component_id, "disposition": disposition, "statement": statement}
            for component_id, disposition, statement in _COMPONENTS
        ],
        "consumedPlans": _plans(),
        "continuationBoundary": _boundary(),
        "corpusOnlyContinuation": "authorized-in-principle",
        "decision": "corpus-only continuation authorized in principle",
        "evidenceInventory": "approved",
        "memoryEvidence": _memory(),
        "memoryEvidenceReview": "approved",
        "notAuthorized": list(_NOT_AUTHORIZED),
        "operatorApproval": "not-issued",
        "proportionalityAnalysis": "approved",
        "proportionalityJudgment": "proportionate",
        "resultRootState": "not-created",
        "reviewAuthority": "PatchPilot Principal Systems Architect",
        "reviewDate": "2026-11-17",
        "reviewStatus": "accepted-by-principal-systems-architect",
        "selectedAlternative": SELECTED_ALTERNATIVE,
        "sourceDigests": {name: source["identityDigest"] for name, source in sources.items()},
        "track9Disposition": _TRACK9,
    }
    require_track9_review(document, sources=sources, sealed=False)
    return document


def require_track9_review(
    document: dict[str, Any],
    *,
    sources: dict[str, dict[str, Any]] | None = None,
    sealed: bool = True,
) -> None:
    """Require the approved review to match the six Track 9 decision records."""
    loaded = sources if sources is not None else _sources()
    _require_memory(document, loaded["memoryEvidenceReview"])
    _require_behavior(document, loaded["behavioralEvidenceReview"])
    _require_alternatives(document, loaded["proportionalityDecision"])
    _require_boundary(document, loaded["corpusContinuationAuthorization"])
    _require_disposition(document, loaded["candidateDisposition"])
    _require_inventory(loaded["evidenceInventory"])
    if document["sourceDigests"] != {
        name: source["identityDigest"] for name, source in loaded.items()
    }:
        raise MeasurementError("record-drift")
    if document["consumedPlans"] != _plans():
        raise MeasurementError("plan-issued")
    if tuple(document["notAuthorized"]) != _NOT_AUTHORIZED:
        raise MeasurementError("contradictory-authority")
    if document["evidenceInventory"] != "approved":
        raise MeasurementError("review-drift")
    if document["memoryEvidenceReview"] != "approved":
        raise MeasurementError("review-drift")
    if document["behavioralEvidenceReview"] != "approved":
        raise MeasurementError("review-drift")
    if document["proportionalityAnalysis"] != "approved":
        raise MeasurementError("review-drift")
    if document["reviewDate"] != "2026-11-17":
        raise MeasurementError("review-drift")
    if document["reviewAuthority"] != "PatchPilot Principal Systems Architect":
        raise MeasurementError("review-drift")
    if document["reviewStatus"] != "accepted-by-principal-systems-architect":
        raise MeasurementError("review-drift")
    if document["currentExecutionAuthority"] is not False:
        raise MeasurementError("execution-authorized")
    if document["futurePlanDigest"] != "not-issued" or document["operatorApproval"] != "not-issued":
        raise MeasurementError("plan-issued")
    if document["resultRootState"] != "not-created":
        raise MeasurementError("result-root-created")
    if document["selectionOutcome"] != "no-selection":
        raise MeasurementError("contradictory-authority")
    if document["calibrationStatus"] != "not-approved":
        raise MeasurementError("contradictory-authority")
    if document["comparisonWinner"] is not None or document["productionReady"] is not False:
        raise MeasurementError("contradictory-authority")
    observed = [
        (item["componentId"], item["disposition"], item["statement"])
        for item in document["componentReviews"]
    ]
    if observed != list(_COMPONENTS):
        raise MeasurementError("review-drift")
    residuals = [(item["residualId"], item["statement"]) for item in document["acceptedResiduals"]]
    if residuals != list(_RESIDUALS):
        raise MeasurementError("review-drift")
    if sealed and document["reviewDigest"] != review_digest(document):
        raise MeasurementError("review-digest")


def _require_memory(document: dict[str, Any], source: dict[str, Any]) -> None:
    memory = document["memoryEvidence"]
    if memory != _memory():
        raise MeasurementError("memory-scope")
    if memory["ceilingBytes"] - memory["warm8192PeakBytes"] != memory["minimumHeadroomBytes"]:
        raise MeasurementError("memory-arithmetic")
    peaks = (
        source["cold4096PeakBytes"],
        source["warm4096PeakBytes"],
        source["cold8192PeakBytes"],
        source["warm8192PeakBytes"],
        source["ceilingBytes"],
        source["minimumHeadroomBytes"],
    )
    expected = (
        memory["cold4096PeakBytes"],
        memory["warm4096PeakBytes"],
        memory["cold8192PeakBytes"],
        memory["warm8192PeakBytes"],
        memory["ceilingBytes"],
        memory["minimumHeadroomBytes"],
    )
    if peaks != expected:
        raise MeasurementError("memory-arithmetic")
    if source["memoryGate4096"] != "passed" or source["memoryGate8192"] != "passed":
        raise MeasurementError("memory-scope")
    if source["headroomAssessment"] != "limited" or source["concurrency"] != "prohibited":
        raise MeasurementError("memory-scope")
    if source["largerContext"] != "not-authorized":
        raise MeasurementError("memory-scope")
    if source["productionCapacity"] != "not-established":
        raise MeasurementError("memory-scope")


def _require_behavior(document: dict[str, Any], source: dict[str, Any]) -> None:
    behavior = document["behavioralEvidence"]
    if behavior != _behavior():
        raise MeasurementError("incomplete-evidence")
    if source["behavioralMeasurementAttempted"] is not True:
        raise MeasurementError("incomplete-evidence")
    if source["behavioralMeasurementCompleted"] is not False:
        raise MeasurementError("incomplete-evidence")
    if source["behavioralConclusion"] != "partial-inconclusive":
        raise MeasurementError("incomplete-evidence")
    if source["candidateMetricsProduced"] is not False:
        raise MeasurementError("incomplete-evidence")
    if source["candidateEvaluatedCompletely"] is not False:
        raise MeasurementError("incomplete-evidence")
    if source["schemaFailuresObserved"] != behavior["sealedRunRecords"]:
        raise MeasurementError("incomplete-evidence")
    if source["completeCaseGroups"] != behavior["completeCaseGroups"]:
        raise MeasurementError("incomplete-evidence")
    if source["casesWithoutResults"] != behavior["missingCompleteCases"]:
        raise MeasurementError("incomplete-evidence")
    if source["unsealedLaunches"] != behavior["unsealedLaunchCount"]:
        raise MeasurementError("incomplete-evidence")
    if source["schemaFailureAuthority"] != "unresolved":
        raise MeasurementError("unresolved-authority")
    if source["schemaComplianceConclusion"] != "unavailable":
        raise MeasurementError("incomplete-evidence")
    if source["empiricalCapabilityConclusions"] != "unavailable":
        raise MeasurementError("incomplete-evidence")
    if source["scoringPermitted"] is not False or source["imputationPermitted"] is not False:
        raise MeasurementError("incomplete-evidence")


def _require_alternatives(document: dict[str, Any], source: dict[str, Any]) -> None:
    rows = document["alternativeDecisions"]
    if rows != [dict(row) for row in _ALTERNATIVES]:
        raise MeasurementError("proportionality-selection")
    selected = [row["alternativeId"] for row in rows if row["selected"]]
    if (
        selected != [SELECTED_ALTERNATIVE]
        or document["selectedAlternative"] != SELECTED_ALTERNATIVE
    ):
        raise MeasurementError("proportionality-selection")
    if document["proportionalityJudgment"] != "proportionate":
        raise MeasurementError("proportionality-selection")
    if source["selectedAlternative"] != SELECTED_ALTERNATIVE:
        raise MeasurementError("proportionality-selection")
    if source["proportionalityJudgment"] != "proportionate":
        raise MeasurementError("proportionality-selection")
    if [row["alternativeId"] for row in source["alternatives"] if row["selected"]] != selected:
        raise MeasurementError("proportionality-selection")


def _require_boundary(document: dict[str, Any], source: dict[str, Any]) -> None:
    boundary = document["continuationBoundary"]
    if boundary != _boundary():
        raise MeasurementError("continuation-boundary")
    if document["corpusOnlyContinuation"] != "authorized-in-principle":
        raise MeasurementError("continuation-boundary")
    if source["authorizationStatus"] != "authorized-in-principle":
        raise MeasurementError("continuation-boundary")
    if (source["caseCount"], source["repetitionsPerCase"], source["plannedRuns"]) != (24, 3, 72):
        raise MeasurementError("continuation-boundary")
    if source["reuseAcceptedMemoryEvidence"] is not True:
        raise MeasurementError("continuation-boundary")
    if source["repeatContext4096"] is not False or source["repeatContext8192"] is not False:
        raise MeasurementError("continuation-boundary")
    for name in (
        "promptsUnchanged",
        "responseSchemaUnchanged",
        "metricsUnchanged",
        "gatesUnchanged",
        "artifactsUnchanged",
    ):
        if source[name] is not True:
            raise MeasurementError("continuation-boundary")
    if source["batchSize"] != 1 or source["maxNewTokens"] != 256:
        raise MeasurementError("continuation-boundary")
    if source["hardenedExecution"] != "required":
        raise MeasurementError("continuation-boundary")
    if source["futureSpecification"] != "mandatory":
        raise MeasurementError("continuation-boundary")
    if source["futurePlanDigest"] != "not-issued" or source["operatorApproval"] != "not-issued":
        raise MeasurementError("plan-issued")
    if source["resultRootState"] != "not-created":
        raise MeasurementError("result-root-created")
    raw = source["rawOutputRetention"]
    if raw["status"] != "required" or raw["availableToCandidate"] is not False:
        raise MeasurementError("raw-output-retention")
    if raw["availableToLaterRuns"] is not False or raw["freeOfGold"] is not True:
        raise MeasurementError("raw-output-retention")
    for name in (
        "recordParseErrors",
        "recordSchemaErrors",
        "recordTruncation",
        "recordOutputLimit",
        "classifyFailureAuthority",
    ):
        if raw[name] is not True:
            raise MeasurementError("raw-output-retention")
    if source["goldIsolation"] != "mandatory":
        raise MeasurementError("raw-output-retention")


def _require_disposition(document: dict[str, Any], source: dict[str, Any]) -> None:
    if document["track9Disposition"] != _TRACK9 or source["track9Disposition"] != _TRACK9:
        raise MeasurementError("contradictory-authority")
    if (
        document["candidateDisposition"] != _CANDIDATE
        or source["candidateDisposition"] != _CANDIDATE
    ):
        raise MeasurementError("contradictory-authority")
    if source["continuationIsNotSelection"] is not True:
        raise MeasurementError("contradictory-authority")
    if source["selectedAlternative"] != SELECTED_ALTERNATIVE:
        raise MeasurementError("contradictory-authority")


def _require_inventory(source: dict[str, Any]) -> None:
    candidate = {
        item["itemId"] for item in source["items"] if item["evidenceClass"] == "candidate-evidence"
    }
    if candidate != {"track8b-r2-accepted-memory", "track8b-r2-limited-headroom"}:
        raise MeasurementError("inventory-class")
    if (
        source["sealedRunFilesCommitted"] is not False
        or source["externalResultRootsRead"] is not False
    ):
        raise MeasurementError("inventory-incomplete")


def build_track9_implementation_review() -> dict[str, Any]:
    """Seal the approved review. The digest is computed, not supplied."""
    document = assemble_track9_review()
    document["reviewDigest"] = review_digest(document)
    reject_track9_text(document)
    reject_sensitive(document)
    validate(SCHEMA_NAME, document)
    require_track9_review(document)
    return document


def load_track9_implementation_review() -> dict[str, Any]:
    """Load the committed review and refuse drift from its builder."""
    loaded = json.loads((repo_root() / _RECORD).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    document = build_track9_implementation_review()
    if loaded != document:
        raise MeasurementError("review-drift")
    return loaded
