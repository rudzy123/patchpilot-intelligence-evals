"""Corpus-only plan identity, consumed-plan rejection, and the fresh result root."""

from __future__ import annotations

from pathlib import Path

import pytest

from patchpilot_intelligence_evals.candidate_inference import launch_child, measurement_limits
from patchpilot_intelligence_evals.corpus_continuation_plan import (
    FRESH_RESULT_ROOT,
    PLANNED_RUNS,
    STOP_CONDITIONS,
    historical_rejections,
    load_corpus_approval,
    load_corpus_plan,
    prepare_continuation_root,
    require_corpus_approval,
    run_inventory,
)
from patchpilot_intelligence_evals.hardened_execution import execute_hardened
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.schemas import TRACK9A_SCHEMA_NAMES, load_schema
from patchpilot_intelligence_evals.track8b_records import APPROVED_PLAN_DIGEST


def test_plan_is_separate_from_consumed_digests() -> None:
    plan = load_corpus_plan()
    approval = load_corpus_approval()
    consumed = {row["planDigest"] for row in plan["consumedPlans"]}
    assert plan["planDigest"] not in consumed
    assert APPROVED_PLAN_DIGEST in consumed
    assert len(consumed) == 3
    assert approval["planDigest"] == plan["planDigest"]
    assert approval["approvalStatus"] == "not-approved"
    assert plan["executionStatus"] == "not-executed"
    assert plan["runInvoked"] is False
    assert plan["currentExecutionAuthority"] is False
    assert plan["selectionOutcome"] == "no-selection"
    assert plan["calibrationStatus"] == "not-approved"
    assert plan["comparisonWinner"] is None
    assert plan["productionReady"] is False
    assert plan["installationAuthorized"] is False
    assert plan["plannedRuns"] == PLANNED_RUNS
    assert len(plan["runs"]) == PLANNED_RUNS
    assert run_inventory() == plan["runs"]
    assert plan["acceptedMemory"]["remeasured"] is False
    assert FRESH_RESULT_ROOT.name == "patchpilot-evals-track9a-corpus"


def test_historical_plans_are_consumed() -> None:
    rows = historical_rejections()
    assert [row["result"] for row in rows] == ["plan-consumed", "plan-consumed", "plan-consumed"]
    with pytest.raises(MeasurementError) as caught:
        require_corpus_approval(APPROVED_PLAN_DIGEST)
    assert caught.value.code == "plan-consumed"
    with pytest.raises(MeasurementError) as caught:
        require_corpus_approval("a" * 64)
    assert caught.value.code == "approval-required"
    with pytest.raises(MeasurementError) as caught:
        require_corpus_approval(load_corpus_plan()["planDigest"])
    assert caught.value.code == "plan-consumed"


def test_stop_tuple_matches_the_plan_schema() -> None:
    schema = load_schema("corpus-continuation-plan")
    assert schema["properties"]["stopConditions"]["const"] == list(STOP_CONDITIONS)
    assert len(STOP_CONDITIONS) == 21


def test_track9a_schemas_are_closed() -> None:
    for name in TRACK9A_SCHEMA_NAMES:
        document = load_schema(name)
        assert document["additionalProperties"] is False
        assert document["$id"] == f"urn:patchpilot-intelligence-evals:schema:{name}:v1"


def test_historical_result_root_is_not_created(tmp_path: Path) -> None:
    historical = Path("/var/tmp/patchpilot-evals-track8b-r2")
    with pytest.raises(MeasurementError) as caught:
        prepare_continuation_root(historical)
    assert caught.value.code == "result-root-reuse"
    named = tmp_path / "track8b-r1-copy"
    with pytest.raises(MeasurementError) as caught:
        prepare_continuation_root(named)
    assert caught.value.code == "result-root-reuse"
    assert not named.exists()


def test_fresh_root_is_owner_only(tmp_path: Path) -> None:
    root = prepare_continuation_root(tmp_path / "fresh-corpus")
    assert root.is_dir()
    assert root.stat().st_mode & 0o077 == 0
    (root / "preflight.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(MeasurementError) as caught:
        prepare_continuation_root(root)
    assert caught.value.code == "result-root-reuse"


def test_real_launcher_refuses_a_consumed_plan(tmp_path: Path) -> None:
    with pytest.raises(MeasurementError) as caught:
        launch_child(
            {"phase": "corpus-evaluation"},
            runtime_dir=tmp_path / "runtime",
            model_dir=tmp_path / "model",
            limits=measurement_limits(load_corpus_plan()),
            launcher=execute_hardened,
            continuation_approval=APPROVED_PLAN_DIGEST,
        )
    assert caught.value.code == "plan-consumed"
