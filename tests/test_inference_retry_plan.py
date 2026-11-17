"""Inference-retry plan identity, prior-plan rejection, and result-root rules."""

from __future__ import annotations

from pathlib import Path

import pytest

from patchpilot_intelligence_evals.candidate_inference import launch_child
from patchpilot_intelligence_evals.hardened_execution import execute_hardened
from patchpilot_intelligence_evals.inference_retry_plan import (
    CONSUMED_RETRY_PLAN_DIGEST,
    FRESH_RESULT_ROOT,
    PHASE_ORDER,
    load_inference_approval,
    load_inference_plan,
    phase_by_name,
    prepare_fresh_result_root,
    require_inference_retry_approval,
    validate_inference_result_root,
)
from patchpilot_intelligence_evals.measurement_plan import ADDRESS_SPACE_BYTES, MeasurementError
from patchpilot_intelligence_evals.measurement_retry_plan import PRIOR_PLAN_DIGEST
from patchpilot_intelligence_evals.resource_controls import ResourceLimits
from patchpilot_intelligence_evals.schemas import TRACK8B_R2_SCHEMA_NAMES, load_schema


def test_plan_keeps_both_consumed_digests() -> None:
    plan = load_inference_plan()
    approval = load_inference_approval()
    text = Path("docs/provenance/track8b-r2-measurement-evidence.md").read_text(encoding="utf-8")
    assert plan["planDigest"] in text
    assert plan["planDigest"] not in {PRIOR_PLAN_DIGEST, CONSUMED_RETRY_PLAN_DIGEST}
    assert plan["priorPlanDigest"] == PRIOR_PLAN_DIGEST
    assert plan["consumedRetryPlanDigest"] == CONSUMED_RETRY_PLAN_DIGEST
    assert plan["replacementPlanDigest"] == "not-issued"
    assert plan["executionStatus"] == "not-executed"
    assert plan["productionReady"] is False
    assert plan["selectionOutcome"] == "no-selection"
    assert plan["calibrationStatus"] == "not-approved"
    assert approval["approvalStatus"] == "not-approved"
    assert approval["planDigest"] == plan["planDigest"]
    assert [item["phase"] for item in plan["phases"]] == list(PHASE_ORDER)
    assert phase_by_name(plan, "one-token-smoke")["prerequisite"] == "dynamic-link-precheck"
    assert phase_by_name(plan, "context-8192")["prerequisite"] == "context-4096"
    assert phase_by_name(plan, "corpus-evaluation")["prerequisite"] == "context-8192"
    assert plan["addressSpaceBytes"] == ADDRESS_SPACE_BYTES
    assert FRESH_RESULT_ROOT.name == "patchpilot-evals-track8b-r2"


def test_consumed_digests_are_rejected() -> None:
    plan = load_inference_plan()
    with pytest.raises(MeasurementError) as prior:
        require_inference_retry_approval(PRIOR_PLAN_DIGEST)
    with pytest.raises(MeasurementError) as retry:
        require_inference_retry_approval(CONSUMED_RETRY_PLAN_DIGEST)
    with pytest.raises(MeasurementError) as other:
        require_inference_retry_approval("0" * 64)
    with pytest.raises(MeasurementError) as current:
        require_inference_retry_approval(plan["planDigest"])
    assert prior.value.code == "plan-consumed"
    assert retry.value.code == "plan-consumed"
    assert other.value.code == "approval-required"
    assert current.value.code == "plan-consumed"


def test_historical_and_open_result_roots(tmp_path: Path) -> None:
    historical = Path("/var/tmp/patchpilot-evals-track8b-r1-572fc9da")
    with pytest.raises(MeasurementError) as reused:
        validate_inference_result_root(historical, resume=False)
    assert reused.value.code == "result-root-reuse"
    root = tmp_path / "fresh-result"
    root.mkdir(mode=0o700)
    assert validate_inference_result_root(root, resume=False) == root.resolve()
    (root / "foreign.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(MeasurementError) as occupied:
        validate_inference_result_root(root, resume=False)
    assert occupied.value.code == "result-root-reuse"
    open_root = tmp_path / "open-result"
    open_root.mkdir(mode=0o755)
    with pytest.raises(MeasurementError) as mode:
        validate_inference_result_root(open_root, resume=False)
    assert mode.value.code == "missing-root"


def test_prepare_creates_an_owner_only_root(tmp_path: Path) -> None:
    root = tmp_path / "created-result"
    prepared = prepare_fresh_result_root(root)
    assert prepared.is_dir()
    assert prepared.stat().st_mode & 0o077 == 0


def test_schemas_reference_both_consumed_plans() -> None:
    for name in TRACK8B_R2_SCHEMA_NAMES:
        document = load_schema(name)
        assert document["additionalProperties"] is False
        properties = document["properties"]
        assert properties["productionReady"]["const"] is False
        assert properties["priorPlanDigest"]["const"] == PRIOR_PLAN_DIGEST
        assert properties["consumedRetryPlanDigest"]["const"] == CONSUMED_RETRY_PLAN_DIGEST


def test_real_launcher_refuses_consumed_digests_before_mounts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def mounted(*_args: object, **_kwargs: object) -> tuple[object, ...]:
        raise AssertionError("mounted")

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.candidate_inference.approved_runtime_mounts",
        mounted,
    )
    limits = ResourceLimits(1, 1, 1, 1, 1, 1, 1.0, 1, 1)
    for digest in (
        PRIOR_PLAN_DIGEST,
        CONSUMED_RETRY_PLAN_DIGEST,
        load_inference_plan()["planDigest"],
    ):
        with pytest.raises(MeasurementError) as exc:
            launch_child(
                {},
                runtime_dir=Path("/tmp"),
                model_dir=Path("/tmp"),
                limits=limits,
                launcher=execute_hardened,
                inference_retry_approval=digest,
            )
        assert exc.value.code == "plan-consumed"
