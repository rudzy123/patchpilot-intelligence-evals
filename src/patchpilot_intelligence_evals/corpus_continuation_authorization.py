"""Track 9 corpus-continuation authorization. No plan digest is issued."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.corpus import CASE_IDS
from patchpilot_intelligence_evals.inference_retry_plan import load_inference_plan
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.protocol import MAX_STDOUT_BYTES
from patchpilot_intelligence_evals.track8b_r2_records import load_stopped_track9
from patchpilot_intelligence_evals.track9_review import (
    CHAT_TEMPLATE_SHA256,
    CORPUS_DIGEST,
    DEPENDENCY_CLOSURE_DIGEST,
    DYNAMIC_LINK_PRECHECK_DIGEST,
    PROMPT_TEMPLATE_DIGEST,
    TOKENIZER_SHA256,
    common,
    load_record,
    seal,
)

SCHEMA_NAME = "corpus-continuation-authorization"
_RECORD = "candidates/authorization/corpus-continuation-authorization.json"
CASE_COUNT = 24
REPETITIONS = 3
PLANNED_RUNS = 72
STOP_CONDITIONS = (
    "cleanup-failure",
    "digest-mismatch",
    "excessive-output",
    "isolation-failure",
    "memory-ceiling",
    "network-violation",
    "oom",
    "telemetry-unresolved",
)
_OMITTED = ("context-4096", "context-8192")
_RAW_TRUE = (
    "associatedWithCaseAndRepetition",
    "boundedByStdoutLimit",
    "classifyFailureAuthority",
    "digestIdentified",
    "distinguishesRawFromParsed",
    "externalDuringExecution",
    "immutable",
    "recordOutputLimit",
    "recordParseErrors",
    "recordSchemaErrors",
    "recordTruncation",
)


def _phase(plan: dict[str, Any], name: str) -> dict[str, Any]:
    matches = [row for row in plan["phases"] if row["phase"] == name]
    if len(matches) != 1:
        raise MeasurementError("continuation-boundary")
    found = matches[0]
    if not isinstance(found, dict):
        raise MeasurementError("continuation-boundary")
    return found


def _raw_output(authorized: bool) -> dict[str, Any]:
    retained = authorized
    return {
        "associatedWithCaseAndRepetition": retained,
        "availableToCandidate": False,
        "availableToLaterRuns": False,
        "boundedByStdoutLimit": retained,
        "classifyFailureAuthority": retained,
        "digestIdentified": retained,
        "distinguishesRawFromParsed": retained,
        "externalDuringExecution": retained,
        "freeOfGold": True,
        "hostIdentityExcluded": True,
        "immutable": retained,
        "recordOutputLimit": retained,
        "recordParseErrors": retained,
        "recordSchemaErrors": retained,
        "recordTruncation": retained,
        "redaction": "synthetic-data-rules",
        "status": "required" if authorized else "withheld",
    }


def require_raw_output(block: dict[str, Any], *, authorized: bool) -> None:
    """Raw output stays bounded, hidden, and digest-identified when authorized."""
    if block["availableToCandidate"] is not False or block["availableToLaterRuns"] is not False:
        raise MeasurementError("raw-output-retention")
    if block["freeOfGold"] is not True or block["hostIdentityExcluded"] is not True:
        raise MeasurementError("raw-output-retention")
    if block["redaction"] != "synthetic-data-rules":
        raise MeasurementError("raw-output-retention")
    if authorized:
        if block["status"] != "required":
            raise MeasurementError("raw-output-retention")
        for name in _RAW_TRUE:
            if block[name] is not True:
                raise MeasurementError("raw-output-retention")
        return
    if block["status"] != "withheld":
        raise MeasurementError("raw-output-retention")
    for name in _RAW_TRUE:
        if block[name] is not False:
            raise MeasurementError("raw-output-retention")


def require_continuation(document: dict[str, Any]) -> None:
    """Authorize a future corpus-only Session, or withhold it, without issuing a plan."""
    if document["futurePlanDigest"] != "not-issued" or document["r3Plan"] != "not-issued":
        raise MeasurementError("plan-issued")
    if document["currentExecutionAuthority"] is not False:
        raise MeasurementError("execution-authorized")
    if document["operatorApproval"] != "not-issued":
        raise MeasurementError("approval-issued")
    if document["resultRootState"] != "not-created":
        raise MeasurementError("result-root-created")
    if document["containsExecutionInstructions"] is not False:
        raise MeasurementError("execution-instructions")
    for name in (
        "artifactsUnchanged",
        "gatesUnchanged",
        "metricsUnchanged",
        "promptsUnchanged",
        "responseSchemaUnchanged",
    ):
        if document[name] is not True:
            raise MeasurementError("continuation-boundary")
    if document["repeatContext4096"] is not False or document["repeatContext8192"] is not False:
        raise MeasurementError("continuation-boundary")
    if tuple(document["omittedPhases"]) != _OMITTED:
        raise MeasurementError("continuation-boundary")
    if document["stdoutLimitBytes"] != MAX_STDOUT_BYTES:
        raise MeasurementError("continuation-boundary")
    status = document["authorizationStatus"]
    authorized = status == "authorized-in-principle"
    if status not in {"authorized-in-principle", "withheld"}:
        raise MeasurementError("continuation-boundary")
    if authorized:
        if document["withheldReason"] != "not-applicable":
            raise MeasurementError("continuation-boundary")
        if (document["caseCount"], document["repetitionsPerCase"], document["plannedRuns"]) != (
            CASE_COUNT,
            REPETITIONS,
            PLANNED_RUNS,
        ):
            raise MeasurementError("continuation-boundary")
        if document["reuseAcceptedMemoryEvidence"] is not True:
            raise MeasurementError("continuation-boundary")
        if document["hardenedExecution"] != "required":
            raise MeasurementError("continuation-boundary")
        if document["goldIsolation"] != "mandatory":
            raise MeasurementError("continuation-boundary")
        if document["futureSpecification"] != "mandatory":
            raise MeasurementError("continuation-boundary")
        if document["futureOperatorCheckpoint"] != "mandatory":
            raise MeasurementError("continuation-boundary")
        if tuple(document["stopConditions"]) != STOP_CONDITIONS:
            raise MeasurementError("continuation-boundary")
    else:
        if document["withheldReason"] == "not-applicable":
            raise MeasurementError("continuation-boundary")
        if document["caseCount"] != 0 or document["plannedRuns"] != 0:
            raise MeasurementError("continuation-boundary")
        if document["repetitionsPerCase"] != 0:
            raise MeasurementError("continuation-boundary")
        if document["reuseAcceptedMemoryEvidence"] is not False:
            raise MeasurementError("continuation-boundary")
        if document["hardenedExecution"] != "not-authorized":
            raise MeasurementError("continuation-boundary")
        if document["stopConditions"] != []:
            raise MeasurementError("continuation-boundary")
    if document["caseCount"] * document["repetitionsPerCase"] != document["plannedRuns"]:
        raise MeasurementError("continuation-boundary")
    require_raw_output(document["rawOutputRetention"], authorized=authorized)


def build_continuation(status: str, withheld_reason: str) -> dict[str, Any]:
    """Build one authorization or withholding record. Neither record issues a plan."""
    if len(CASE_IDS) != CASE_COUNT:
        raise MeasurementError("continuation-boundary")
    plan = load_inference_plan()
    corpus = _phase(plan, "corpus-evaluation")
    context_4096 = _phase(plan, "context-4096")
    context_8192 = _phase(plan, "context-8192")
    if corpus["repetitions"] != REPETITIONS or corpus["stdoutBytes"] != MAX_STDOUT_BYTES:
        raise MeasurementError("continuation-boundary")
    if corpus["batchSize"] != 1 or corpus["maxNewTokens"] != 256:
        raise MeasurementError("continuation-boundary")
    if context_4096["inputTokens"] != 4096 or context_8192["inputTokens"] != 8192:
        raise MeasurementError("continuation-boundary")
    if plan["promptTemplateDigest"] != PROMPT_TEMPLATE_DIGEST:
        raise MeasurementError("continuation-boundary")
    if plan["corpusDigest"] != CORPUS_DIGEST:
        raise MeasurementError("continuation-boundary")
    if plan["chatTemplateSha256"] != CHAT_TEMPLATE_SHA256:
        raise MeasurementError("continuation-boundary")
    readiness = load_stopped_track9()
    if readiness["dependencyClosureDigest"] != DEPENDENCY_CLOSURE_DIGEST:
        raise MeasurementError("record-drift")
    if readiness["dynamicLinkPrecheckDigest"] != DYNAMIC_LINK_PRECHECK_DIGEST:
        raise MeasurementError("record-drift")
    authorized = status == "authorized-in-principle"
    document = {
        **common(),
        "artifactsUnchanged": True,
        "authorizationStatus": status,
        "batchSize": 1,
        "caseCount": CASE_COUNT if authorized else 0,
        "chatTemplateDigest": CHAT_TEMPLATE_SHA256,
        "corpusDigest": CORPUS_DIGEST,
        "dependencyClosureDigest": DEPENDENCY_CLOSURE_DIGEST,
        "dynamicLinkPrecheckDigest": DYNAMIC_LINK_PRECHECK_DIGEST,
        "futureOperatorCheckpoint": "mandatory" if authorized else "not-required",
        "futureSpecification": "mandatory" if authorized else "not-required",
        "gatesUnchanged": True,
        "goldIsolation": "mandatory" if authorized else "not-applicable",
        "hardenedExecution": "required" if authorized else "not-authorized",
        "maxNewTokens": 256,
        "metricsUnchanged": True,
        "omittedPhases": list(_OMITTED),
        "operatorApproval": "not-issued",
        "plannedRuns": PLANNED_RUNS if authorized else 0,
        "promptTemplateDigest": PROMPT_TEMPLATE_DIGEST,
        "promptsUnchanged": True,
        "rawOutputRetention": _raw_output(authorized),
        "repeatContext4096": False,
        "repeatContext8192": False,
        "repetitionsPerCase": REPETITIONS if authorized else 0,
        "responseSchemaUnchanged": True,
        "resultRootState": "not-created",
        "reuseAcceptedMemoryEvidence": authorized,
        "stdoutLimitBytes": MAX_STDOUT_BYTES,
        "stopConditions": list(STOP_CONDITIONS) if authorized else [],
        "tokenizerDigest": TOKENIZER_SHA256,
        "withheldReason": withheld_reason,
    }
    require_continuation(document)
    return seal(document, SCHEMA_NAME)


def build_corpus_continuation_authorization() -> dict[str, Any]:
    """Authorize the future corpus-only Session in principle."""
    return build_continuation("authorized-in-principle", "not-applicable")


def build_withheld_continuation(reason: str = "proportionality-stop") -> dict[str, Any]:
    """Build an uncommitted withholding record for the closed negative path."""
    if reason == "not-applicable":
        raise MeasurementError("continuation-boundary")
    return build_continuation("withheld", reason)


def load_corpus_continuation_authorization() -> dict[str, Any]:
    """Return the committed in-principle authorization."""
    return load_record(_RECORD, build_corpus_continuation_authorization)
