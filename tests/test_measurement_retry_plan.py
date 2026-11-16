"""Retry plan identity, prior-plan rejection, and result-root rules."""

from __future__ import annotations

from pathlib import Path

import pytest

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.candidate_inference import launch_child, measurement_limits
from patchpilot_intelligence_evals.hardened_execution import execute_hardened
from patchpilot_intelligence_evals.measurement_plan import ADDRESS_SPACE_BYTES, MeasurementError
from patchpilot_intelligence_evals.measurement_retry_plan import (
    PRIOR_PLAN_DIGEST,
    RESULT_ROOT_CLASS,
    load_retry_approval,
    load_retry_plan,
    phase_by_name,
    reject_prior_plan,
    require_retry_approval,
    validate_retry_result_root,
)
from patchpilot_intelligence_evals.schemas import TRACK8B_R1_SCHEMA_NAMES, load_schema


def test_provenance_names_the_sealed_digest() -> None:
    plan = load_retry_plan()
    text = Path("docs/provenance/track8b-r1-measurement-evidence.md").read_text(encoding="utf-8")
    assert plan["planDigest"] in text
    assert plan["priorPlanDigest"] in text


def test_retry_plan_rejects_the_consumed_digest() -> None:
    plan = load_retry_plan()
    approval = load_retry_approval()
    assert plan["planDigest"] != PRIOR_PLAN_DIGEST
    assert plan["priorPlanDigest"] == PRIOR_PLAN_DIGEST
    assert plan["priorPlanDisposition"] == "consumed"
    assert plan["priorPlanReusable"] is False
    assert plan["replacementPlanDigest"] == "not-issued"
    assert plan["executionStatus"] == "not-executed"
    assert plan["measurementAuthorization"] == "not-authorized"
    assert approval["approvalStatus"] == "not-approved"
    assert approval["planDigest"] == plan["planDigest"]
    assert plan["productionReady"] is False
    assert plan["selectionOutcome"] == "no-selection"
    assert plan["calibrationStatus"] == "not-approved"
    assert plan["resultRootClass"] == RESULT_ROOT_CLASS
    with pytest.raises(MeasurementError) as caught:
        reject_prior_plan(PRIOR_PLAN_DIGEST)
    assert caught.value.code == "plan-consumed"
    with pytest.raises(MeasurementError) as caught:
        require_retry_approval("0" * 64)
    assert caught.value.code == "approval-required"


def test_phase_order_limits_and_prompts() -> None:
    plan = load_retry_plan()
    assert [item["phase"] for item in plan["phases"]] == [
        "preflight",
        "template-compatibility",
        "one-token-smoke",
        "short-generation",
        "context-4096",
        "context-8192",
        "corpus-evaluation",
    ]
    smoke = phase_by_name(plan, "one-token-smoke")
    short = phase_by_name(plan, "short-generation")
    context = phase_by_name(plan, "context-4096")
    longer = phase_by_name(plan, "context-8192")
    corpus = phase_by_name(plan, "corpus-evaluation")
    assert smoke["prerequisite"] == "template-compatibility"
    assert short["prerequisite"] == "one-token-smoke"
    assert context["prerequisite"] == "short-generation"
    assert longer["prerequisite"] == "context-4096"
    assert corpus["prerequisite"] == "context-8192"
    assert plan["smokePrompt"] == "Reply with one token."
    assert plan["shortPrompt"] == "Reply with the single word ready."
    assert smoke["maxNewTokens"] == 1
    assert short["maxNewTokens"] == 32
    assert short["coldWarm"] is True
    assert context["inputTokens"] == 4096
    assert longer["inputTokens"] == 8192
    assert longer["generationBudgetSeconds"] == 600
    assert corpus["repetitions"] == 3
    assert corpus["generationBudgetSeconds"] == 15
    assert plan["repeatedTokenId"] == 574
    assert plan["memoryMaxBytes"] == MEMORY_CAP
    assert plan["memorySwapMaxBytes"] == 0
    assert plan["addressSpaceBytes"] == ADDRESS_SPACE_BYTES
    assert plan["tasksMax"] == 32
    assert plan["profileId"] == "linux-bwrap-systemd-v1"
    assert plan["decoding"]["method"] == "greedy-argmax"
    assert plan["decoding"]["seedSupport"] is False
    limits = measurement_limits(context)
    assert limits.memory_max_bytes == MEMORY_CAP
    assert limits.address_space_bytes == ADDRESS_SPACE_BYTES
    assert limits.address_space_bytes != limits.memory_max_bytes


def test_retry_schemas_are_closed() -> None:
    for name in TRACK8B_R1_SCHEMA_NAMES:
        document = load_schema(name)
        assert document["additionalProperties"] is False
        assert document["$id"] == f"urn:patchpilot-intelligence-evals:schema:{name}:v1"


def test_historical_result_root_is_rejected() -> None:
    historical = Path("/var/tmp/patchpilot-evals-track8b-approved-8280ec63")
    with pytest.raises(MeasurementError) as caught:
        validate_retry_result_root(historical, resume=False)
    assert caught.value.code == "result-root-reuse"


def test_result_root_must_be_empty_and_owner_only(tmp_path: Path) -> None:
    root = tmp_path / "fresh"
    root.mkdir()
    root.chmod(0o700)
    assert validate_retry_result_root(root, resume=False) == root
    (root / "preflight.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(MeasurementError) as caught:
        validate_retry_result_root(root, resume=False)
    assert caught.value.code == "result-root-reuse"
    open_root = tmp_path / "open"
    open_root.mkdir()
    open_root.chmod(0o755)
    with pytest.raises(MeasurementError) as caught:
        validate_retry_result_root(open_root, resume=False)
    assert caught.value.code == "missing-root"


def test_real_launcher_still_refuses_the_consumed_plan() -> None:
    phase = phase_by_name(load_retry_plan(), "one-token-smoke")
    with pytest.raises(MeasurementError) as caught:
        launch_child(
            {"phase": "one-token-smoke"},
            runtime_dir=Path("/tmp/runtime"),
            model_dir=Path("/tmp/model"),
            limits=measurement_limits(phase),
            launcher=execute_hardened,
        )
    assert caught.value.code == "plan-consumed"
