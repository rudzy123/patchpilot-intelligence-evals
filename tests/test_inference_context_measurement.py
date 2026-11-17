"""Context phases stay ordered and memory fields stay separate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.inference_context_measurement import (
    execute_phase,
    load_context_template,
    load_smoke_template,
)
from patchpilot_intelligence_evals.inference_retry_plan import load_inference_plan
from patchpilot_intelligence_evals.inference_retry_preflight import SYNTHETIC_RENDERED_DIGEST
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.measurement_retry_closeout import context_memory_conclusion


def test_templates_are_not_executed() -> None:
    smoke = load_smoke_template()
    context = load_context_template()
    assert smoke["phase"] == "not-executed"
    assert smoke["runInvoked"] is False
    assert context["phase"] == "not-executed"
    assert context["realModelExecuted"] is False
    assert "cgroupPeakBytes" in context["coldMemory"]
    assert "processRssBytes" in context["coldMemory"]
    assert "virtualAddressBytes" in context["coldMemory"]


def test_8192_waits_for_a_passing_4096(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    plan = load_inference_plan()
    monkeypatch.setattr(
        "patchpilot_intelligence_evals.inference_context_measurement.require_inference_retry_approval",
        lambda _supplied: plan,
    )
    _write(
        tmp_path / "template-compatibility.json",
        {
            "compatibility": "supported",
            "recordKind": "template-compatibility",
            "renderedDigest": SYNTHETIC_RENDERED_DIGEST,
            "runInvoked": False,
            "sessionCreated": False,
        },
    )
    _write(
        tmp_path / "context-4096.json",
        {"exitClassification": "oom", "stopCause": "oom"},
    )
    called = False

    def launcher(*_args: object, **_kwargs: object) -> ExecutionResult:
        nonlocal called
        called = True
        raise AssertionError("launched")

    with pytest.raises(MeasurementError) as exc:
        execute_phase(
            "context-8192",
            approval=plan["planDigest"],
            runtime_root=tmp_path,
            model_root=tmp_path,
            result_root=tmp_path,
            indexes={"api_version": 1},
            launcher=launcher,
            executed=True,
            bind=False,
        )
    assert exc.value.code == "prior-phase-failed"
    assert called is False


def test_empty_context_memory_is_unavailable() -> None:
    assert context_memory_conclusion({}) == "unavailable"
    assert context_memory_conclusion({"context-4096": None, "context-8192": None}) == "unavailable"


def _write(path: Path, document: dict[str, object]) -> None:
    path.write_text(json.dumps(document), encoding="utf-8")
