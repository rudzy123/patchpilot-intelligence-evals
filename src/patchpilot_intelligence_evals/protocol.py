"""Provider-neutral candidate request and response framing.

Track 2 remains authoritative for the finding-explanation input and output
schemas, metric formulas, and promotion gates. This module only frames one
canonical JSON request and one canonical JSON response. It does not score
quality and it does not grant PatchPilot state authority.
"""

from __future__ import annotations

import json
from typing import Any

from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text, to_candidate_input
from patchpilot_intelligence_evals.schemas import SchemaValidationError, validate

PROTOCOL_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"
PURPOSE = "candidate-performance"
EVALUATOR_VERSION = "0.0.0"
PROMPT_IDENTITY = "candidate-protocol-1.0.0"
TIMEOUT_SECONDS = 15
MAX_STDOUT_BYTES = 65536
MAX_STDERR_BYTES = 16384
RETRIES = 0
EXPLANATION_KIND = "future-candidate"

EXECUTION_OUTCOMES: tuple[str, ...] = (
    "internal-harness-failure",
    "timeout",
    "output-limit-exceeded",
    "stderr-limit-exceeded",
    "network-policy-failure",
    "nonzero-exit",
    "malformed-output",
    "multiple-outputs",
    "schema-invalid-output",
    "protocol-mismatch",
    "request-id-mismatch",
    "candidate-identity-mismatch",
    "candidate-rejection",
    "candidate-unavailable",
    "success",
)

FAILURE_OUTCOMES: tuple[str, ...] = tuple(
    outcome for outcome in EXECUTION_OUTCOMES if outcome != "success"
)

_HIDDEN_INPUT_FIELDS: frozenset[str] = frozenset(
    {
        "negativeControls",
        "goldSupportedClaims",
        "prohibitedClaims",
        "expectedCitations",
        "expectedRefusal",
        "expectedUncertainty",
        "expectedSafetyWarnings",
        "expectedRemediationSuggestions",
        "category",
        "promptInjection",
        "decisiveEvidenceIds",
    }
)


class ProtocolError(ValueError):
    """A candidate frame failed a closed protocol check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def execution_constraints() -> dict[str, int]:
    return {
        "timeoutSeconds": TIMEOUT_SECONDS,
        "maxStdoutBytes": MAX_STDOUT_BYTES,
        "maxStderrBytes": MAX_STDERR_BYTES,
        "retries": RETRIES,
    }


def request_id(case_id: str, manifest_digest: str) -> str:
    """Stable request identity. It does not include the assistance text."""
    return sha256_text(
        canonical_dumps(
            {
                "caseId": case_id,
                "candidateManifestDigest": manifest_digest,
                "protocolVersion": PROTOCOL_VERSION,
            }
        )
    )


def experiment_id(*, manifest_digest: str, corpus_digest: str) -> str:
    """Content address of one candidate experiment.

    Timestamp, commit, operating system, and Python version are excluded so
    the same candidate and corpus keep the same path.
    """
    return sha256_text(
        canonical_dumps(
            {
                "protocolVersion": PROTOCOL_VERSION,
                "candidateManifestDigest": manifest_digest,
                "corpusDigest": corpus_digest,
                "evaluatorVersion": EVALUATOR_VERSION,
                "purpose": PURPOSE,
            }
        )
    )


def build_request(case: dict[str, Any], manifest_digest: str) -> dict[str, Any]:
    """Build one request. The case mapping and its hidden labels are not copied."""
    finding_input = to_candidate_input(case)
    request = {
        "schemaVersion": SCHEMA_VERSION,
        "protocolVersion": PROTOCOL_VERSION,
        "requestId": request_id(str(case["caseId"]), manifest_digest),
        "caseId": str(case["caseId"]),
        "authorizedOrganizationId": str(case["authorizedOrganizationId"]),
        "findingExplanationInput": finding_input,
        "executionConstraints": execution_constraints(),
        "expectedResponseSchemaVersion": SCHEMA_VERSION,
    }
    validate_request(request)
    return request


def validate_request(request: dict[str, Any]) -> None:
    """Validate the envelope and the Track 2 finding-explanation input."""
    validate("candidate-request", request)
    finding_input = request["findingExplanationInput"]
    if not isinstance(finding_input, dict):
        raise ProtocolError("input-type")
    hidden = _HIDDEN_INPUT_FIELDS.intersection(finding_input)
    if hidden:
        raise ProtocolError("hidden-label")
    validate("finding-explanation-input", finding_input)
    if request["authorizedOrganizationId"] != finding_input["authorizedOrganizationId"]:
        raise ProtocolError("organization-mismatch")
    payload = dict(finding_input)
    digest = str(payload.pop("inputDigest"))
    if sha256_text(canonical_dumps(payload)) != digest:
        raise ProtocolError("input-digest")


def parse_candidate_stdout(stdout: bytes) -> tuple[str, dict[str, Any] | None]:
    """Return a parse outcome and, for one canonical object, that object.

    Exactly one canonical JSON object is accepted. A trailing newline, a second
    value, or non-canonical whitespace fails closed. The returned outcome is
    `parsed`, `malformed-output`, or `multiple-outputs`.
    """
    try:
        text = stdout.decode("utf-8")
    except UnicodeDecodeError:
        return "malformed-output", None
    if text == "":
        return "malformed-output", None
    try:
        parsed, end = json.JSONDecoder().raw_decode(text)
    except json.JSONDecodeError:
        return "malformed-output", None
    if text[end:] != "":
        return "multiple-outputs", None
    if not isinstance(parsed, dict):
        return "malformed-output", None
    if canonical_dumps(parsed) != text:
        return "malformed-output", None
    return "parsed", parsed


def classify_response(
    parsed: dict[str, Any],
    *,
    request_id_value: str,
    candidate_id: str,
    candidate_version: str,
) -> str:
    """Classify one parsed response object. This does not score quality.

    Field mismatches that the schema also rejects are reported as the more
    specific protocol outcome when the field is present.
    """
    if "protocolVersion" in parsed and parsed["protocolVersion"] != PROTOCOL_VERSION:
        return "protocol-mismatch"
    if "requestId" in parsed and parsed["requestId"] != request_id_value:
        return "request-id-mismatch"
    if "candidateId" in parsed and parsed["candidateId"] != candidate_id:
        return "candidate-identity-mismatch"
    if "candidateVersion" in parsed and parsed["candidateVersion"] != candidate_version:
        return "candidate-identity-mismatch"
    try:
        validate("candidate-response", parsed)
    except SchemaValidationError:
        return "schema-invalid-output"
    status = str(parsed["status"])
    if status == "rejected":
        return "candidate-rejection"
    if status == "unavailable":
        return "candidate-unavailable"
    output = parsed["findingExplanationOutput"]
    try:
        validate("finding-explanation-output", output)
    except SchemaValidationError:
        return "schema-invalid-output"
    candidate = output["candidate"]
    if (
        candidate["kind"] != EXPLANATION_KIND
        or candidate["name"] != candidate_id
        or candidate["version"] != candidate_version
    ):
        return "candidate-identity-mismatch"
    return "success"
