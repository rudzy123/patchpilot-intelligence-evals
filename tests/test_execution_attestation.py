"""Attestations and Track 6B readiness fail closed."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from patchpilot_intelligence_evals.execution_attestation import (
    REQUIRED_CONTROLS,
    AttestationError,
    build_attestation,
    decide_readiness,
    load_attestation,
    load_profile,
    load_readiness,
    repository_commit,
    validate_attestation,
)
from patchpilot_intelligence_evals.runtime_security import load_authorization
from patchpilot_intelligence_evals.schemas import SchemaValidationError


def test_committed_attestation_is_closed() -> None:
    document = load_attestation()
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert document["attempts"] == 1
    assert document["exitClassification"] == "success"
    assert document["networkTestResult"] == "passed"
    assert document["filesystemVisibilityResult"] == "passed"
    assert document["processTreeCleanupResult"] == "reaped"
    assert document["runtimeAuthorizationId"] == "onnxruntime@v1.31.1"
    assert "/home/" not in str(document)
    validate_attestation(document)


def test_readiness_matches_profile_and_runtime() -> None:
    readiness = load_readiness()
    assert readiness["readiness"] == "ready"
    assert readiness["verdict"] == ("TRACK 6B HARDENED ACQUISITION READY WITH DOCUMENTED RESIDUALS")
    assert readiness["selectionOutcome"] == "no-selection"
    assert readiness["acquisitionStatus"] == "not-acquired"
    assert readiness["executionStatus"] == "not-executed"
    assert readiness["blockers"] == []
    assert readiness["localModelArtifactDigests"] == []
    assert "sandbox-local-loopback" in readiness["residualIds"]
    assert "candidate-format-gap" in readiness["residualIds"]
    assert readiness["installationAuthorized"] is False


def test_missing_control_is_not_ready() -> None:
    profile = load_profile()
    for control in profile["controls"]:
        if control["controlId"] == "no-outbound-network":
            control["disposition"] = "failed"
    readiness = decide_readiness(profile, load_authorization())
    assert readiness["readiness"] == "not-ready"
    assert "no-outbound-network" in readiness["blockers"]
    assert readiness["verdict"] == "TRACK 6B HARDENED ACQUISITION NOT READY"


def test_no_runtime_blocks_readiness() -> None:
    authorization = load_authorization()
    authorization["authorizationOutcome"] = "no-runtime"
    authorization["runtimeId"] = None
    authorization["versionTag"] = None
    authorization["immutableRevision"] = None
    authorization["artifactFormat"] = None
    readiness = decide_readiness(load_profile(), authorization)
    assert readiness["readiness"] == "not-ready"
    assert "runtime-authorization" in readiness["blockers"]


def test_attestation_rejects_identity_and_retries() -> None:
    document = load_attestation()
    document["attempts"] = 2
    with pytest.raises(SchemaValidationError):
        validate_attestation(document)
    identified = load_attestation()
    identified["unsupportedControlIds"] = [*identified["unsupportedControlIds"], "/home/operator"]
    with pytest.raises(AttestationError) as identified_error:
        validate_attestation(identified)
    assert identified_error.value.code == "identity"
    rebuilt = build_attestation(
        profile=load_profile(),
        authorization=load_authorization(),
        fixture_name="fs-visibility",
        fixture_bytes=b"synthetic",
        input_bytes=b"{}",
        stdout=b"ok",
        exit_classification="success",
        network_result="passed",
        filesystem_result="passed",
        cleanup_result="reaped",
        executed_at=datetime(2026, 11, 10, 17, 45, tzinfo=UTC),
        repository_commit=repository_commit(),
    )
    assert rebuilt["outputDigest"] != load_attestation()["outputDigest"]
    assert set(REQUIRED_CONTROLS).issubset(set(rebuilt["enforcedControlIds"]))
