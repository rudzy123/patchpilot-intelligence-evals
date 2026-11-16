"""Offline-load attestation. The child is not launched."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.hardened_load_proof import (
    LOAD_LIMITS,
    LoadProofError,
    attestation_from_result,
    load_attestation_template,
    not_performed_attestation,
    proof_arguments,
    proof_is_generation_free,
)
from patchpilot_intelligence_evals.offline_load_main import _indexes

_HEADER = """
#define ORT_API_VERSION 21
ORT_LOGGING_LEVEL_ERROR = 3
struct OrtApi {
ORT_API_STATUS(ORT_API_CALL *CreateEnv)();
ORT_API_STATUS(ORT_API_CALL *CreateSession)();
ORT_API_STATUS(ORT_API_CALL *CreateSessionOptions)();
ORT_API_STATUS(ORT_API_CALL *DisableTelemetryEvents)();
ORT_API_STATUS(ORT_API_CALL *GetErrorMessage)();
ORT_API_STATUS(ORT_API_CALL *ReleaseEnv)();
ORT_API_STATUS(ORT_API_CALL *ReleaseSession)();
ORT_API_STATUS(ORT_API_CALL *ReleaseSessionOptions)();
ORT_API_STATUS(ORT_API_CALL *SessionGetInputCount)();
ORT_API_STATUS(ORT_API_CALL *SessionGetOutputCount)();
};
"""


def test_attestation_template_is_not_performed() -> None:
    document = load_attestation_template()
    assert document == not_performed_attestation()
    assert document["loadStatus"] == "not-performed"
    assert document["inferencePerformed"] is False
    assert document["realModelExecuted"] is False
    assert document["measurementPerformed"] is False
    assert document["memoryCeilingBytes"] == 12_884_901_888
    assert LOAD_LIMITS.memory_max_bytes == 12_884_901_888
    assert LOAD_LIMITS.address_space_bytes == 12_884_901_888


def test_child_source_does_not_generate() -> None:
    assert proof_is_generation_free()
    arguments = proof_arguments(_HEADER)
    assert all(not item.startswith("run=") for item in arguments)
    assert _indexes(["run=1"]) is None
    assert _indexes(list(arguments)) is not None


def test_attestation_keeps_inference_false() -> None:
    report = {
        "corpusExecuted": False,
        "generationTokens": 0,
        "inferencePerformed": False,
        "inputCount": 2,
        "loadStatus": "loaded",
        "network": {
            "dns": "gaierror",
            "ipv4": "OSError",
            "localLoopback": "ConnectionRefusedError",
        },
        "outputCount": 1,
        "residentBytes": 4096,
        "tokenizerInitialized": True,
    }
    result = ExecutionResult(
        exit_classification="success",
        return_code=0,
        stdout=b"",
        stderr=b"",
        cleanup="reaped",
        attempts=1,
        report=json.dumps(report).encode("utf-8"),
        argv=("bwrap", "--unshare-net"),
    )
    document = attestation_from_result(result)
    assert document["loadStatus"] == "loaded"
    assert document["inferencePerformed"] is False
    assert document["generationPerformed"] is False
    assert document["corpusExecuted"] is False
    assert document["realModelExecuted"] is False
    assert document["measurementPerformed"] is False
    assert document["networkDenial"] == "denied"
    assert document["processCleanup"] == "reaped"
    report["generationTokens"] = 1
    result = ExecutionResult(
        exit_classification="success",
        return_code=0,
        stdout=b"",
        stderr=b"",
        cleanup="reaped",
        attempts=1,
        report=json.dumps(report).encode("utf-8"),
        argv=("bwrap", "--unshare-net"),
    )
    with pytest.raises(LoadProofError) as caught:
        attestation_from_result(result)
    assert caught.value.code == "generation"
