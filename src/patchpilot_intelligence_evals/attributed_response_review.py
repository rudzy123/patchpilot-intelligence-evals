"""Attributed Track 9A response evidence. This record does not call Run."""

from __future__ import annotations

from typing import Any

from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.track9a_records import (
    EXTRACTED_DIGEST,
    STDERR_DIGEST,
    STDOUT_DIGEST,
)
from patchpilot_intelligence_evals.track10_review import (
    DIAGNOSTIC_DIGEST,
    EXTRACTED_BYTES,
    SELECTED_TRACK,
    STDOUT_BYTES,
    common,
    decision_for,
    load_record,
    require_session_decision,
    seal,
)

SCHEMA_NAME = "attributed-response-evidence"
_RECORD = "candidates/authorization/attributed-response-evidence.json"
ENVELOPE_SCHEMA_ID = "urn:patchpilot-intelligence-evals:schema:candidate-response:v1"
EXPLANATION_SCHEMA_ID = "urn:patchpilot-intelligence-evals:schema:finding-explanation-output:v1"
MISSING_REQUIRED: tuple[str, ...] = (
    "schemaVersion",
    "candidate",
    "authorizedOrganizationId",
    "findingId",
    "refused",
    "refusalReason",
    "preservedDeterministicFacts",
    "sourceFacts",
    "supportedClaims",
    "remediationSuggestions",
    "uncertainty",
    "citations",
    "safetyWarnings",
    "explanationText",
    "nonAuthoritative",
)
UNEXPECTED: tuple[str, ...] = ("deterministicFacts", "findingExplanation")


def require_attributed_response(document: dict[str, Any]) -> None:
    """Require the sealed response chain and separated stop authority."""
    require_session_decision(document)
    if document["stdoutDigest"] != STDOUT_DIGEST or document["stdoutBytes"] != STDOUT_BYTES:
        raise MeasurementError("stdout-identity")
    if (
        document["extractedDigest"] != EXTRACTED_DIGEST
        or document["extractedBytes"] != EXTRACTED_BYTES
    ):
        raise MeasurementError("extracted-identity")
    if document["stderrDigest"] != STDERR_DIGEST or document["stderrBytes"] != 0:
        raise MeasurementError("stderr-identity")
    if document["diagnosticIdentityDigest"] != DIAGNOSTIC_DIGEST:
        raise MeasurementError("diagnostic-identity")
    if document["parseStatus"] != "parsed" or document["utf8"] is not True:
        raise MeasurementError("parse-status")
    if document["schemaStatus"] != "invalid":
        raise MeasurementError("schema-status")
    if document["stdoutTruncated"] is not False or document["stderrTruncated"] is not False:
        raise MeasurementError("truncation")
    if document["outputLimitStatus"] != "within-limit":
        raise MeasurementError("output-limit")
    if tuple(document["missingRequiredFields"]) != MISSING_REQUIRED:
        raise MeasurementError("missing-fields")
    if tuple(document["unexpectedFields"]) != UNEXPECTED:
        raise MeasurementError("unexpected-fields")
    if document["adapterWrappedEnvelope"] is not True:
        raise MeasurementError("adapter-preservation")
    if document["adapterRenamedFields"] is not False:
        raise MeasurementError("adapter-preservation")
    if document["adapterRemovedFields"] is not False:
        raise MeasurementError("adapter-preservation")
    if document["adapterAddedInnerFields"] is not False:
        raise MeasurementError("adapter-preservation")
    if document["innerObjectUnchanged"] is not True:
        raise MeasurementError("adapter-preservation")
    if document["jsonKeysPreserved"] is not True:
        raise MeasurementError("adapter-preservation")
    if document["extractionPreservedObject"] is not True:
        raise MeasurementError("adapter-preservation")
    if document["adapterFallback"] is not False or document["adapterTruncated"] is not False:
        raise MeasurementError("adapter-preservation")
    if document["promptContractPresent"] is not True:
        raise MeasurementError("prompt-contract")
    if document["evaluatorAppliedIntendedSchema"] is not True:
        raise MeasurementError("evaluator-schema")
    if document["envelopeSchemaId"] != ENVELOPE_SCHEMA_ID:
        raise MeasurementError("evaluator-schema")
    if document["explanationSchemaId"] != EXPLANATION_SCHEMA_ID:
        raise MeasurementError("evaluator-schema")
    if document["responseEvidenceClass"] != "candidate-evidence":
        raise MeasurementError("evidence-class")
    if document["stopEvidenceClass"] != "measurement-infrastructure-evidence":
        raise MeasurementError("evidence-class")
    if document["evidenceCompleteness"] != "single-run-attributed":
        raise MeasurementError("evidence-completeness")


def build_attributed_response_body() -> dict[str, Any]:
    """Build the unsigned attributed-response body."""
    document = {
        **common(),
        **decision_for(SELECTED_TRACK),
        "adapterAddedInnerFields": False,
        "adapterFallback": False,
        "adapterRemovedFields": False,
        "adapterRenamedFields": False,
        "adapterTruncated": False,
        "adapterWrappedEnvelope": True,
        "envelopeSchemaId": ENVELOPE_SCHEMA_ID,
        "evaluatorAppliedIntendedSchema": True,
        "explanationSchemaId": EXPLANATION_SCHEMA_ID,
        "extractionPreservedObject": True,
        "generationObserved": True,
        "innerObjectUnchanged": True,
        "jsonKeysPreserved": True,
        "missingRequiredFields": list(MISSING_REQUIRED),
        "promptContainsFindingExplanation": False,
        "promptContractPresent": True,
        "responseEvidenceClass": "candidate-evidence",
        "stderrBytes": 0,
        "stderrDigest": STDERR_DIGEST,
        "stderrTruncated": False,
        "stopEvidenceClass": "measurement-infrastructure-evidence",
        "unexpectedFields": list(UNEXPECTED),
        "utf8": True,
    }
    require_attributed_response(document)
    return document


def build_attributed_response() -> dict[str, Any]:
    """Seal the committed attributed-response record."""
    return seal(build_attributed_response_body(), SCHEMA_NAME)


def load_attributed_response() -> dict[str, Any]:
    """Return the committed attributed-response record."""
    return load_record(_RECORD, build_attributed_response)
