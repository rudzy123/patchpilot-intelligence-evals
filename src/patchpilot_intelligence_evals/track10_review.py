"""Shared Track 10 review identity. Building these records does not call Run."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Any

from patchpilot_intelligence_evals.candidate_discovery import LFM_MODEL_ID
from patchpilot_intelligence_evals.corpus_continuation_plan import response_schema_digest
from patchpilot_intelligence_evals.finalist_budget import RUNTIME_TAG
from patchpilot_intelligence_evals.inference_retry_plan import (
    CONSUMED_RETRY_PLAN_DIGEST as PLAN_R1,
)
from patchpilot_intelligence_evals.measurement_plan import (
    CANDIDATE_ATTEMPT,
    CHAT_TEMPLATE_SHA256,
    CORPUS_DIGEST,
    PROMPT_TEMPLATE_DIGEST,
    RUNTIME_ATTEMPT,
    MeasurementError,
    authority,
    digest_document,
)
from patchpilot_intelligence_evals.protocol import PROMPT_IDENTITY
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.track8b_r2_records import HEADROOM_BYTES
from patchpilot_intelligence_evals.track8b_r2_records import PLAN_DIGEST as PLAN_R2
from patchpilot_intelligence_evals.track8b_records import APPROVED_PLAN_DIGEST as PLAN_8B
from patchpilot_intelligence_evals.track9_review import MEMORY_SOURCE_DIGEST
from patchpilot_intelligence_evals.track9a_records import (
    EXTRACTED_DIGEST,
    STDOUT_DIGEST,
)
from patchpilot_intelligence_evals.track9a_records import PLAN_DIGEST as PLAN_9A

SESSION_ID = "intelligence-track-10"
NOT_ISSUED = "not-issued"
PRECISION = "FP32"
PROMPT_TEMPLATE_ID = "finding-explanation-1.0.0"
RESPONSE_SCHEMA_DIGEST = "15955301d2cd0e2f835b851e19d7f48a2664eb9df6f1f7f99d658926e8b46b91"
FORENSICS_DIGEST = "19786bdcfc186d665ee72e865d55652639da2aae47fb418e0ff46c4aa7e72021"
STOPPED_ATTEMPT_DIGEST = "9b24636d16d8fbe27a05982f76be39eab109f62fe3e921317efccffdc801d6e9"
DIAGNOSTIC_DIGEST = "f1aaa2a2288d04de90d5777e8fc5e87c1c74e8373d95f9a3b79202480233b6f9"
MEMORY_REVIEW_DIGEST = "47d8dc74f738d043a3fa58c40f936e3c9148ba88c45bb9e2cf1b23c0172796f2"
NOT_EXECUTED_READINESS_DIGEST = "80a24b19a39312de8dc82a973c7e79024dfdd32571e2662c42bd38724de491e0"
STOPPED_READINESS_DIGEST = "03e0795f15a8eac36c72218fc74da36363743aa4a4b4db46187c89e7356b172f"
RUN_ID = "case-ground-001-r1"
STDOUT_BYTES = 542
EXTRACTED_BYTES = 264
DECISION_ALTERNATIVES: tuple[str, ...] = (
    "reject-now",
    "six-run-diagnostic",
    "full-72-run-continuation",
    "protocol-forensics",
    "stop-investment",
)
TRACK_DISPOSITIONS: tuple[str, ...] = (
    "candidate-rejected",
    "six-run-diagnostic-authorized-in-principle",
    "full-corpus-continuation-authorized-in-principle",
    "further-investment-stopped",
    "blocked-by-unresolved-authority",
)
CANDIDATE_DISPOSITIONS: tuple[str, ...] = (
    "candidate-rejected",
    "evaluation-incomplete-six-run-diagnostic-authorized-in-principle",
    "full-corpus-continuation-authorized-in-principle",
    "further-investment-stopped",
    "blocked-by-unresolved-authority",
)
SELECTED_TRACK = "six-run-diagnostic-authorized-in-principle"
SELECTED_CANDIDATE = "evaluation-incomplete-six-run-diagnostic-authorized-in-principle"
SELECTED_ALTERNATIVE = "six-run-diagnostic"
PAIRS: dict[str, str] = {
    "six-run-diagnostic-authorized-in-principle": (
        "evaluation-incomplete-six-run-diagnostic-authorized-in-principle"
    ),
    "candidate-rejected": "candidate-rejected",
    "full-corpus-continuation-authorized-in-principle": (
        "full-corpus-continuation-authorized-in-principle"
    ),
    "further-investment-stopped": "further-investment-stopped",
    "blocked-by-unresolved-authority": "blocked-by-unresolved-authority",
}
ALTERNATIVE_FOR: dict[str, str] = {
    "six-run-diagnostic-authorized-in-principle": "six-run-diagnostic",
    "candidate-rejected": "reject-now",
    "full-corpus-continuation-authorized-in-principle": "full-72-run-continuation",
    "further-investment-stopped": "stop-investment",
    "blocked-by-unresolved-authority": "none",
}
_FORBIDDEN = ("/home/", "/var/", "http://", "https://", "InferenceSession", "onnxruntime")


def common() -> dict[str, Any]:
    """Identity and authority fields locked on every Track 10 record."""
    if response_schema_digest() != RESPONSE_SCHEMA_DIGEST:
        raise MeasurementError("response-schema-drift")
    if HEADROOM_BYTES != 613_232_640:
        raise MeasurementError("memory-evidence")
    return {
        **authority(),
        "authoritiesConflated": False,
        "behavioralConclusion": "partial-inconclusive",
        "candidateAttemptId": CANDIDATE_ATTEMPT,
        "candidateMetricsProduced": False,
        "candidateModelId": LFM_MODEL_ID,
        "candidatePrecision": PRECISION,
        "chatTemplateDigest": CHAT_TEMPLATE_SHA256,
        "comparisonWinner": None,
        "completedRuns": 1,
        "containsExecutionInstructions": False,
        "corpusDigest": CORPUS_DIGEST,
        "currentExecutionAuthority": False,
        "diagnosticIdentityDigest": DIAGNOSTIC_DIGEST,
        "evidenceCompleteness": "single-run-attributed",
        "executionStopAuthority": "measurement-infrastructure",
        "executionStopCause": "telemetry-unresolved",
        "extractedBytes": EXTRACTED_BYTES,
        "extractedDigest": EXTRACTED_DIGEST,
        "forensicsIdentityDigest": FORENSICS_DIGEST,
        "futurePlanDigest": NOT_ISSUED,
        "historicalPlansReusable": False,
        "memoryConclusion": "within-ceiling-with-limited-headroom",
        "memoryReviewDigest": MEMORY_REVIEW_DIGEST,
        "memorySourceDigest": MEMORY_SOURCE_DIGEST,
        "minimumHeadroomBytes": HEADROOM_BYTES,
        "missingRuns": 71,
        "notExecutedReadinessDigest": NOT_EXECUTED_READINESS_DIGEST,
        "operatorApproval": NOT_ISSUED,
        "outputLimitStatus": "within-limit",
        "parseStatus": "parsed",
        "plannedCorpusRuns": 72,
        "promptIdentity": PROMPT_IDENTITY,
        "promptTemplateDigest": PROMPT_TEMPLATE_DIGEST,
        "promptTemplateId": PROMPT_TEMPLATE_ID,
        "replacementPlanDigest": NOT_ISSUED,
        "responseFailureAuthority": "candidate-output",
        "responseSchemaDigest": RESPONSE_SCHEMA_DIGEST,
        "responseSchemaVersion": "1.0.0",
        "resultRootState": "not-created",
        "runId": RUN_ID,
        "runtimeAttemptId": RUNTIME_ATTEMPT,
        "runtimeVersionTag": RUNTIME_TAG,
        "schemaStatus": "invalid",
        "sessionId": SESSION_ID,
        "stdoutBytes": STDOUT_BYTES,
        "stdoutDigest": STDOUT_DIGEST,
        "stdoutTruncated": False,
        "stoppedAttemptDigest": STOPPED_ATTEMPT_DIGEST,
        "stoppedReadinessDigest": STOPPED_READINESS_DIGEST,
        "track8bPlanDigest": PLAN_8B,
        "track8bR1PlanDigest": PLAN_R1,
        "track8bR2PlanDigest": PLAN_R2,
        "track9aPlanDigest": PLAN_9A,
    }


def decision_for(track: str) -> dict[str, Any]:
    """One closed disposition triple. The committed records use the six-run pair."""
    if track not in PAIRS:
        raise MeasurementError("contradictory-authority")
    return {
        "candidateDisposition": PAIRS[track],
        "decisionAlternatives": list(DECISION_ALTERNATIVES),
        "selectedAlternative": ALTERNATIVE_FOR[track],
        "track10Disposition": track,
    }


def require_frozen(document: Mapping[str, Any]) -> None:
    """Keep selection, calibration, comparison, and production frozen."""
    if document["selectionOutcome"] != "no-selection":
        raise MeasurementError("contradictory-authority")
    if document["calibrationStatus"] != "not-approved":
        raise MeasurementError("contradictory-authority")
    if document["comparisonWinner"] is not None:
        raise MeasurementError("contradictory-authority")
    if document["productionReady"] is not False:
        raise MeasurementError("contradictory-authority")
    if document["installationAuthorized"] is not False:
        raise MeasurementError("contradictory-authority")
    if document["sessionId"] != SESSION_ID:
        raise MeasurementError("contradictory-authority")


def require_no_operational(document: Mapping[str, Any]) -> None:
    """Refuse a plan digest, operator approval, result root, or execution."""
    if document["futurePlanDigest"] != NOT_ISSUED:
        raise MeasurementError("plan-issued")
    if document["replacementPlanDigest"] != NOT_ISSUED:
        raise MeasurementError("plan-issued")
    if document["operatorApproval"] != NOT_ISSUED:
        raise MeasurementError("approval-issued")
    if document["resultRootState"] != "not-created":
        raise MeasurementError("result-root-created")
    if document["currentExecutionAuthority"] is not False:
        raise MeasurementError("execution-authorized")
    if document["containsExecutionInstructions"] is not False:
        raise MeasurementError("execution-instructions")
    if document["historicalPlansReusable"] is not False:
        raise MeasurementError("plan-reusable")


def require_authority_separation(document: Mapping[str, Any]) -> None:
    """Keep the candidate-output failure separate from the telemetry stop."""
    if document["authoritiesConflated"] is not False:
        raise MeasurementError("authority-conflated")
    if document["responseFailureAuthority"] != "candidate-output":
        raise MeasurementError("authority-separation")
    if document["executionStopAuthority"] != "measurement-infrastructure":
        raise MeasurementError("authority-separation")
    if document["executionStopCause"] != "telemetry-unresolved":
        raise MeasurementError("authority-separation")
    if document["candidateMetricsProduced"] is not False:
        raise MeasurementError("metrics-produced")
    if document["behavioralConclusion"] != "partial-inconclusive":
        raise MeasurementError("behavioral-conclusion")


def require_session_decision(document: Mapping[str, Any]) -> None:
    """Lock evidence records to the six-run conclusion."""
    require_frozen(document)
    require_no_operational(document)
    require_authority_separation(document)
    if document["track10Disposition"] != SELECTED_TRACK:
        raise MeasurementError("contradictory-authority")
    if document["candidateDisposition"] != SELECTED_CANDIDATE:
        raise MeasurementError("contradictory-authority")
    if document["selectedAlternative"] != SELECTED_ALTERNATIVE:
        raise MeasurementError("contradictory-authority")
    if tuple(document["decisionAlternatives"]) != DECISION_ALTERNATIVES:
        raise MeasurementError("contradictory-authority")


def reject_track10_text(document: Mapping[str, Any]) -> None:
    """Reject host paths, transfer URLs, and execution-runtime markers."""
    text = json.dumps(document)
    if any(marker in text for marker in _FORBIDDEN):
        raise MeasurementError("identity")
    if ".." in text:
        raise MeasurementError("identity")


def seal(document: dict[str, Any], schema_name: str) -> dict[str, Any]:
    """Digest one closed record. This does not create a plan or a result root."""
    reject_track10_text(document)
    return digest_document(document, schema_name, "identityDigest")


def load_record(relative: str, builder: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    """Load one committed record and refuse drift from its builder."""
    loaded = json.loads((repo_root() / relative).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise MeasurementError("record-type")
    if loaded != builder():
        raise MeasurementError("record-drift")
    return loaded
