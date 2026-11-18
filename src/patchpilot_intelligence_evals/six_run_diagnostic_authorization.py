"""Six-run diagnostic boundary. Authorization in principle does not create a plan."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.corpus import load_cases
from patchpilot_intelligence_evals.corpus_continuation_plan import load_corpus_plan
from patchpilot_intelligence_evals.evaluator import CATEGORIES
from patchpilot_intelligence_evals.measurement_plan import CHAT_TEMPLATE_SHA256, MeasurementError
from patchpilot_intelligence_evals.protocol import (
    MAX_STDERR_BYTES,
    MAX_STDOUT_BYTES,
    TIMEOUT_SECONDS,
)
from patchpilot_intelligence_evals.track10_review import (
    SELECTED_TRACK,
    common,
    decision_for,
    load_record,
    require_authority_separation,
    require_frozen,
    require_no_operational,
    seal,
)

SCHEMA_NAME = "six-run-diagnostic-authorization"
_RECORD = "candidates/authorization/six-run-diagnostic-authorization.json"
REPRESENTATIVE_RULE = "minimum-case-id-within-committed-category"
DIAGNOSTIC_RUNS = 6
REPETITIONS = 1
DECODING: dict[str, Any] = {
    "method": "greedy-argmax",
    "repetitionPenalty": 1,
    "seed": 0,
    "seedControl": "unused",
    "seedSupport": False,
    "temperature": 0,
    "topK": 1,
    "topP": 1,
}
REQUIRED_DIAGNOSTICS: tuple[str, ...] = (
    "extraction",
    "parse",
    "schema",
    "truncation",
    "output-limit",
    "evidence-id",
    "failure-authority",
)
SYSTEMATIC_PRECONDITIONS: tuple[str, ...] = (
    "complete-diagnostic-result-set",
    "raw-output-and-diagnostics-for-every-run",
    "candidate-output-authority-proven",
    "no-explaining-defect",
)
THRESHOLD = "deferred-to-future-diagnostic-specification"


def representative_cases() -> dict[str, str]:
    """Return the minimum case id in each committed category.

    The result is a review oracle. It is not written into the authorization record.
    """
    chosen: dict[str, str] = {}
    for case in load_cases():
        category = str(case["category"])
        case_id = str(case["caseId"])
        current = chosen.get(category)
        if current is None or case_id < current:
            chosen[category] = case_id
    if set(chosen) != set(CATEGORIES):
        raise MeasurementError("category-coverage")
    return {category: chosen[category] for category in CATEGORIES}


def _categories(authorized: bool) -> list[dict[str, Any]]:
    if not authorized:
        return []
    return [
        {
            "caseId": "not-selected",
            "category": category,
            "repetitionCount": REPETITIONS,
            "representativeCaseRule": REPRESENTATIVE_RULE,
        }
        for category in CATEGORIES
    ]


def require_six_run(document: dict[str, Any]) -> None:
    """Bound a future diagnostic without selecting cases or issuing a plan."""
    require_frozen(document)
    require_no_operational(document)
    require_authority_separation(document)
    if document["decoding"] != DECODING:
        raise MeasurementError("decoding")
    if document["decoding"] != load_corpus_plan()["decoding"]:
        raise MeasurementError("decoding")
    if document["chatTemplateDigest"] != CHAT_TEMPLATE_SHA256:
        raise MeasurementError("publisher-template")
    if document["operationalCaseIds"] != "not-selected":
        raise MeasurementError("operational-case")
    if document["automaticCandidateSelection"] is not False:
        raise MeasurementError("automatic-selection")
    if document["memoryRerun"] is not False or document["contextMemoryRerun"] is not False:
        raise MeasurementError("memory-rerun")
    if document["plannedCorpusRuns"] != 72:
        raise MeasurementError("corpus-count")
    if document["systematicThreshold"] != THRESHOLD:
        raise MeasurementError("hidden-threshold")
    if document["representsCompleteCorpus"] is not False:
        raise MeasurementError("diagnostic-scope")
    if document["producesPercentageMetrics"] is not False:
        raise MeasurementError("diagnostic-scope")
    if document["promotionGateAttempt"] is not False:
        raise MeasurementError("diagnostic-scope")
    if document["calibrationRun"] is not False or document["candidateSelectionRun"] is not False:
        raise MeasurementError("diagnostic-scope")
    if document["maxNewTokens"] != 256:
        raise MeasurementError("output-limit")
    if document["stdoutLimitBytes"] != MAX_STDOUT_BYTES:
        raise MeasurementError("output-limit")
    if document["stderrLimitBytes"] != MAX_STDERR_BYTES:
        raise MeasurementError("output-limit")
    if document["timeoutSeconds"] != TIMEOUT_SECONDS:
        raise MeasurementError("output-limit")
    status = document["authorizationStatus"]
    authorized = status == "authorized-in-principle"
    if status not in {"authorized-in-principle", "withheld"}:
        raise MeasurementError("authorization-status")
    if document["authorizesFutureSession"] is not authorized:
        raise MeasurementError("authorization-status")
    if authorized:
        if document["withheldReason"] != "not-applicable":
            raise MeasurementError("withheld-reason")
        if document["track10Disposition"] != SELECTED_TRACK:
            raise MeasurementError("contradictory-authority")
        if document["selectedAlternative"] != "six-run-diagnostic":
            raise MeasurementError("contradictory-authority")
        if document["plannedDiagnosticRuns"] != DIAGNOSTIC_RUNS:
            raise MeasurementError("diagnostic-count")
        if document["repetitionsPerSelectedCase"] != REPETITIONS:
            raise MeasurementError("diagnostic-count")
        if document["futureSpecification"] != "mandatory":
            raise MeasurementError("future-specification")
        if document["goldIsolation"] != "mandatory":
            raise MeasurementError("gold-isolation")
        if document["hardenedBoundary"] != "required":
            raise MeasurementError("hardened-boundary")
        if document["rawOutputRetention"] != "bounded-immutable":
            raise MeasurementError("raw-output")
        if tuple(document["requiredDiagnostics"]) != REQUIRED_DIAGNOSTICS:
            raise MeasurementError("diagnostics")
        if tuple(document["systematicPreconditions"]) != SYSTEMATIC_PRECONDITIONS:
            raise MeasurementError("systematic-preconditions")
        rows = document["categories"]
        if [row["category"] for row in rows] != list(CATEGORIES):
            raise MeasurementError("category-coverage")
        if any(row["caseId"] != "not-selected" for row in rows):
            raise MeasurementError("operational-case")
        if any(row["repetitionCount"] != 1 for row in rows):
            raise MeasurementError("diagnostic-count")
        if any(row["representativeCaseRule"] != REPRESENTATIVE_RULE for row in rows):
            raise MeasurementError("case-rule")
    else:
        if document["withheldReason"] == "not-applicable":
            raise MeasurementError("withheld-reason")
        if document["track10Disposition"] == SELECTED_TRACK:
            raise MeasurementError("contradictory-authority")
        if document["plannedDiagnosticRuns"] != 0 or document["repetitionsPerSelectedCase"] != 0:
            raise MeasurementError("diagnostic-count")
        if document["categories"] != []:
            raise MeasurementError("category-coverage")
        if document["requiredDiagnostics"] != [] or document["systematicPreconditions"] != []:
            raise MeasurementError("diagnostics")
        if document["futureSpecification"] != "not-required":
            raise MeasurementError("future-specification")
        if document["goldIsolation"] != "not-applicable":
            raise MeasurementError("gold-isolation")
        if document["hardenedBoundary"] != "not-authorized":
            raise MeasurementError("hardened-boundary")
        if document["rawOutputRetention"] != "not-authorized":
            raise MeasurementError("raw-output")
    runs = document["plannedDiagnosticRuns"]
    repetitions = document["repetitionsPerSelectedCase"]
    if len(document["categories"]) * repetitions != runs:
        raise MeasurementError("diagnostic-count")


def build_six_run_body(status: str, withheld_reason: str) -> dict[str, Any]:
    """Build one authorization or withholding body. Neither body issues a plan."""
    authorized = status == "authorized-in-principle"
    track = SELECTED_TRACK if authorized else "further-investment-stopped"
    document = {
        **common(),
        **decision_for(track),
        "authorizationStatus": status,
        "authorizesFutureSession": authorized,
        "automaticCandidateSelection": False,
        "calibrationRun": False,
        "candidateSelectionRun": False,
        "categories": _categories(authorized),
        "contextMemoryRerun": False,
        "decoding": dict(DECODING),
        "decodingUnchanged": True,
        "freshResultRootRequired": True,
        "futureSpecification": "mandatory" if authorized else "not-required",
        "goldIsolation": "mandatory" if authorized else "not-applicable",
        "hardenedBoundary": "required" if authorized else "not-authorized",
        "limitsUnchanged": True,
        "maxNewTokens": 256,
        "memoryRerun": False,
        "newOperatorApprovalRequired": True,
        "newPlanDigestRequired": True,
        "operationalCaseIds": "not-selected",
        "plannedDiagnosticRuns": DIAGNOSTIC_RUNS if authorized else 0,
        "producesPercentageMetrics": False,
        "promotionGateAttempt": False,
        "promptsUnchanged": True,
        "publisherTemplateUnchanged": True,
        "rawOutputRetention": "bounded-immutable" if authorized else "not-authorized",
        "repetitionsPerSelectedCase": REPETITIONS if authorized else 0,
        "representsCompleteCorpus": False,
        "requiredDiagnostics": list(REQUIRED_DIAGNOSTICS) if authorized else [],
        "responseSchemaUnchanged": True,
        "reuseAcceptedMemoryEvidence": authorized,
        "stderrLimitBytes": MAX_STDERR_BYTES,
        "stdoutLimitBytes": MAX_STDOUT_BYTES,
        "systematicPreconditions": list(SYSTEMATIC_PRECONDITIONS) if authorized else [],
        "systematicThreshold": THRESHOLD,
        "timeoutSeconds": TIMEOUT_SECONDS,
        "withheldReason": withheld_reason,
    }
    require_six_run(document)
    return document


def build_six_run_authorization() -> dict[str, Any]:
    """Seal the committed in-principle six-run authorization."""
    body = build_six_run_body("authorized-in-principle", "not-applicable")
    return seal(body, SCHEMA_NAME)


def build_withheld_six_run(reason: str = "not-selected") -> dict[str, Any]:
    """Build an uncommitted withholding record for the closed negative path."""
    if reason == "not-applicable":
        raise MeasurementError("withheld-reason")
    return seal(build_six_run_body("withheld", reason), SCHEMA_NAME)


def load_six_run_authorization() -> dict[str, Any]:
    """Return the committed in-principle six-run authorization."""
    return load_record(_RECORD, build_six_run_authorization)
