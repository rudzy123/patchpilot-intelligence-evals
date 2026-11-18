"""Attributed response evidence tests."""

import pytest

from patchpilot_intelligence_evals.attributed_response_review import (
    MISSING_REQUIRED,
    SCHEMA_NAME,
    UNEXPECTED,
    build_attributed_response,
    build_attributed_response_body,
    load_attributed_response,
    require_attributed_response,
)
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schemas import SchemaValidationError, validate
from patchpilot_intelligence_evals.track9a_records import (
    EXTRACTED_DIGEST,
    STDOUT_DIGEST,
    load_schema_forensics,
)
from patchpilot_intelligence_evals.track10_review import seal


def test_committed_response_matches_forensics_identity() -> None:
    document = load_attributed_response()
    forensics = load_schema_forensics()
    assert document == build_attributed_response()
    assert document["stdoutDigest"] == STDOUT_DIGEST == forensics["stdoutDigest"]
    assert document["stdoutBytes"] == 542 == forensics["stdoutBytes"]
    assert document["extractedDigest"] == EXTRACTED_DIGEST == forensics["extractedDigest"]
    assert document["extractedBytes"] == 264 == forensics["extractedBytes"]
    assert document["parseStatus"] == "parsed"
    assert document["schemaStatus"] == "invalid"
    assert document["stdoutTruncated"] is False
    assert document["outputLimitStatus"] == "within-limit"
    assert tuple(document["missingRequiredFields"]) == MISSING_REQUIRED
    assert document["missingRequiredFields"] == forensics["missingRequiredFields"]
    assert tuple(document["unexpectedFields"]) == UNEXPECTED
    assert document["unexpectedFields"] == forensics["unexpectedFields"]
    assert document["responseFailureAuthority"] == "candidate-output"
    assert document["executionStopAuthority"] == "measurement-infrastructure"
    assert document["executionStopCause"] == "telemetry-unresolved"
    assert document["authoritiesConflated"] is False
    assert document["responseEvidenceClass"] == "candidate-evidence"
    assert document["stopEvidenceClass"] == "measurement-infrastructure-evidence"
    assert document["adapterWrappedEnvelope"] is True
    assert document["adapterRenamedFields"] is False
    assert document["adapterRemovedFields"] is False
    assert document["adapterAddedInnerFields"] is False
    assert document["innerObjectUnchanged"] is True
    assert document["promptContractPresent"] is True
    assert document["evaluatorAppliedIntendedSchema"] is True
    assert document["candidateMetricsProduced"] is False
    assert document["futurePlanDigest"] == "not-issued"
    assert document["operatorApproval"] == "not-issued"
    assert document["resultRootState"] == "not-created"


def test_changed_output_identity_is_rejected() -> None:
    document = build_attributed_response_body()
    document["stdoutDigest"] = "0" * 64
    with pytest.raises(MeasurementError) as caught:
        require_attributed_response(document)
    assert caught.value.code == "stdout-identity"


def test_conflating_authorities_is_rejected() -> None:
    document = build_attributed_response_body()
    document["authoritiesConflated"] = True
    with pytest.raises(MeasurementError) as caught:
        require_attributed_response(document)
    assert caught.value.code == "authority-conflated"


def test_host_path_is_rejected() -> None:
    document = build_attributed_response_body()
    document["runId"] = "/home/example"
    with pytest.raises(MeasurementError) as caught:
        seal(document, SCHEMA_NAME)
    assert caught.value.code == "identity"


def test_schema_rejects_extra_field() -> None:
    document = build_attributed_response()
    document["explanationText"] = "hidden"
    with pytest.raises(SchemaValidationError):
        validate(SCHEMA_NAME, document)
