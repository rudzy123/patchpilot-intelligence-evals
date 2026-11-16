"""Sealed measurement plan and operator checkpoint."""

from __future__ import annotations

import pytest

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.candidate_inference import measurement_limits
from patchpilot_intelligence_evals.hardened_load_proof import proof_is_generation_free
from patchpilot_intelligence_evals.measurement_plan import (
    ADDRESS_SPACE_BYTES,
    MeasurementError,
    load_measurement_plan,
    load_operator_approval,
    phase_by_name,
    require_operator_approval,
)
from patchpilot_intelligence_evals.schemas import TRACK8B_SCHEMA_NAMES, load_schema


def test_plan_and_approval_match_builders() -> None:
    plan = load_measurement_plan()
    approval = load_operator_approval()
    assert approval["planDigest"] == plan["planDigest"]
    assert approval["approvalStatus"] == "not-approved"
    assert plan["executionStatus"] == "not-executed"
    assert plan["measurementAuthorization"] == "not-authorized"
    assert plan["productionReady"] is False
    assert plan["selectionOutcome"] == "no-selection"
    assert plan["installationAuthorized"] is False
    assert [item["phase"] for item in plan["phases"]] == [
        "preflight",
        "one-token-smoke",
        "short-generation",
        "context-4096",
        "context-8192",
        "corpus-evaluation",
    ]


def test_wrong_approval_digest_is_rejected() -> None:
    with pytest.raises(MeasurementError) as caught:
        require_operator_approval("0" * 64)
    assert caught.value.code == "approval-required"


def test_address_space_is_not_the_resident_ceiling() -> None:
    plan = load_measurement_plan()
    phase = phase_by_name(plan, "context-4096")
    limits = measurement_limits(phase)
    assert plan["memoryMaxBytes"] == MEMORY_CAP
    assert plan["addressSpaceBytes"] == ADDRESS_SPACE_BYTES
    assert limits.memory_max_bytes == MEMORY_CAP
    assert limits.address_space_bytes == ADDRESS_SPACE_BYTES
    assert limits.address_space_bytes == MEMORY_CAP * 2
    assert limits.address_space_bytes != limits.memory_max_bytes


def test_track8b_schemas_are_closed() -> None:
    for name in TRACK8B_SCHEMA_NAMES:
        document = load_schema(name)
        assert document["additionalProperties"] is False
        assert document["$id"] == f"urn:patchpilot-intelligence-evals:schema:{name}:v1"


def test_offline_load_child_stays_generation_free() -> None:
    assert proof_is_generation_free() is True
