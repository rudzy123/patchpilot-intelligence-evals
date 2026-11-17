"""Inference launch uses the R2 approval channel."""

from __future__ import annotations

from pathlib import Path

import pytest

from patchpilot_intelligence_evals.candidate_inference import Launcher
from patchpilot_intelligence_evals.corrected_candidate_inference import repeated_token_ids
from patchpilot_intelligence_evals.hardened_candidate_inference import launch_inference
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.inference_retry_plan import load_inference_plan
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.resource_controls import ResourceLimits


def test_repeated_token_counts_are_exact() -> None:
    assert repeated_token_ids(574, 4096) == [574] * 4096
    assert repeated_token_ids(574, 8192) == [574] * 8192
    with pytest.raises(MeasurementError) as exc:
        repeated_token_ids(574, 100)
    assert exc.value.code == "inference-failure"


def test_consumed_digest_does_not_launch(tmp_path: Path) -> None:
    plan = load_inference_plan()
    seen: dict[str, object] = {}

    def launcher(*_args: object, **_kwargs: object) -> ExecutionResult:
        seen["called"] = True
        return ExecutionResult("success", 0, b"", b"", "reaped", 1, b"{}", ())

    with pytest.raises(MeasurementError) as exc:
        launch_inference(
            {"coldWarm": False},
            approval=plan["planDigest"],
            runtime_dir=tmp_path,
            model_dir=tmp_path,
            result_root=tmp_path,
            limits=ResourceLimits(1, 1, 1, 1, 1, 1, 1.0, 1, 1),
            launcher=launcher,
            executed=True,
        )
    assert exc.value.code == "plan-consumed"
    assert seen == {}


def test_launcher_type_accepts_the_wrapper() -> None:
    assert isinstance(launch_inference, object)
    assert Launcher is not None
