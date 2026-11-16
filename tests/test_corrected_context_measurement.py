"""Compatibility precedes a session, and later phases wait on earlier records."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.cgroup_memory import ScopeSampler
from patchpilot_intelligence_evals.corrected_candidate_inference import repeated_token_ids
from patchpilot_intelligence_evals.corrected_context_measurement import execute_phase
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.measurement_retry_plan import load_retry_plan
from patchpilot_intelligence_evals.measurement_retry_preflight import (
    PHASE_FILES,
    run_preflight,
)
from patchpilot_intelligence_evals.template_compatibility import CHAT_TEMPLATE_SHA256

_EVENTS = {"high": 0, "low": 0, "max": 0, "oom": 0, "oomKill": 0}


def _prepare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, Path]:
    result = tmp_path / "result"
    result.mkdir()
    result.chmod(0o700)
    model = tmp_path / "model"
    destination = model / "verified" / "cd-20b7ceee37a62cba"
    destination.mkdir(parents=True)
    fixture = Path("tests/fixtures/verified-chat-template.jinja").read_text(encoding="utf-8")
    (destination / "chat_template.jinja").write_text(fixture, encoding="utf-8")
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    monkeypatch.setattr(
        "patchpilot_intelligence_evals.measurement_retry_preflight.bind_verified_roots",
        lambda *_args, **_kwargs: {
            "archiveAttemptId": "rt-e791f1518ae46ead",
            "candidateAttemptId": "cd-20b7ceee37a62cba",
            "runtimeAttemptId": "rp-c2fe1c88f694fc1e",
        },
    )
    return runtime, model, result


def _launcher(token_count: int, calls: list[str]) -> Callable[..., ExecutionResult]:
    def launch(fixture: Path, arguments: tuple[str, ...], **kwargs: object) -> ExecutionResult:
        observer = kwargs["observer"]
        assert isinstance(observer, ScopeSampler)
        calls.append("launch")
        for phase in ("cold", "warm"):
            observer.samples.append(
                {
                    "cgroupCurrentBytes": 4,
                    "cgroupPeakBytes": 8,
                    "memoryEvents": dict(_EVENTS),
                    "oomEvents": 0,
                    "phase": phase,
                    "processRssBytes": 1,
                    "processTreeRssBytes": 2,
                    "virtualAddressBytes": 99,
                }
            )
        report = {
            "coldGenerationSeconds": 0.1,
            "firstTokenSeconds": 0.1,
            "generationSeconds": 0.1,
            "inputTokenCount": token_count,
            "loadSeconds": 0.1,
            "modelSessionCreated": True,
            "network": {"dns": "gaierror", "ipv4": "OSError"},
            "newTokenCount": 1,
            "outputDigest": "ab" * 32,
            "runInvoked": True,
            "status": "ok",
            "wallSeconds": 0.2,
            "warmGenerationSeconds": 0.1,
        }
        return ExecutionResult(
            exit_classification="success",
            return_code=0,
            stdout=b"",
            stderr=b"",
            cleanup="reaped",
            attempts=1,
            report=json.dumps(report).encode("utf-8"),
            argv=(),
        )

    return launch


def test_repeated_token_counts_are_exact() -> None:
    assert repeated_token_ids(574, 4096) == [574] * 4096
    assert repeated_token_ids(574, 8192) == [574] * 8192
    with pytest.raises(MeasurementError) as caught:
        repeated_token_ids(574, 1024)
    assert caught.value.code == "inference-failure"


def test_compatibility_record_has_no_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime, model, result = _prepare(tmp_path, monkeypatch)
    preflight = run_preflight(runtime, model, result)
    document = json.loads((result / "template-compatibility.json").read_text(encoding="utf-8"))
    assert preflight["runInvoked"] is False
    assert preflight["modelSessionCreated"] is False
    assert document["compatibility"] == "supported"
    assert document["templateDigest"] == CHAT_TEMPLATE_SHA256
    assert document["renderedDigest"] == (
        "5c61ee0b595fa4c5b295feb233b312c38b779f7840f3f39c82aef51da9061e5d"
    )
    assert document["runInvoked"] is False
    assert document["sessionCreated"] is False
    assert "messages | length" not in (
        model / "verified/cd-20b7ceee37a62cba/chat_template.jinja"
    ).read_text(encoding="utf-8")


def test_smoke_and_short_generation_record_separate_memory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runtime, model, result = _prepare(tmp_path, monkeypatch)
    run_preflight(runtime, model, result)
    approval = load_retry_plan()["planDigest"]
    calls: list[str] = []
    smoke = execute_phase(
        "one-token-smoke",
        approval=approval,
        runtime_root=runtime,
        model_root=model,
        result_root=result,
        indexes={"api_version": 1},
        launcher=_launcher(4, calls),
        executed=False,
        bind=False,
    )
    short = execute_phase(
        "short-generation",
        approval=approval,
        runtime_root=runtime,
        model_root=model,
        result_root=result,
        indexes={"api_version": 1},
        launcher=_launcher(6, calls),
        executed=False,
        bind=False,
    )
    assert smoke["exitClassification"] == "success"
    assert smoke["realModelExecuted"] is False
    assert smoke["coldMemory"]["cgroupPeakBytes"] == 8
    assert smoke["coldMemory"]["processRssBytes"] == 1
    assert smoke["coldMemory"]["virtualAddressBytes"] == 99
    assert smoke["coldMemory"]["memoryEvents"]["oom"] == 0
    assert short["warmMemory"]["telemetry"] == "complete"
    assert short["warmTiming"]["generationSeconds"] == 0.1
    assert calls == ["launch", "launch"]


def test_8192_waits_for_4096(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runtime, model, result = _prepare(tmp_path, monkeypatch)
    run_preflight(runtime, model, result)
    approval = load_retry_plan()["planDigest"]
    calls: list[str] = []
    launcher = _launcher(4, calls)
    execute_phase(
        "one-token-smoke",
        approval=approval,
        runtime_root=runtime,
        model_root=model,
        result_root=result,
        indexes={"api_version": 1},
        launcher=launcher,
        executed=False,
        bind=False,
    )
    execute_phase(
        "short-generation",
        approval=approval,
        runtime_root=runtime,
        model_root=model,
        result_root=result,
        indexes={"api_version": 1},
        launcher=launcher,
        executed=False,
        bind=False,
    )
    (result / PHASE_FILES["context-4096"]).write_text(
        json.dumps({"exitClassification": "oom", "stopCause": "oom"}),
        encoding="utf-8",
    )
    with pytest.raises(MeasurementError) as caught:
        execute_phase(
            "context-8192",
            approval=approval,
            runtime_root=runtime,
            model_root=model,
            result_root=result,
            indexes={"api_version": 1},
            launcher=launcher,
            executed=False,
            bind=False,
        )
    assert caught.value.code == "prior-phase-failed"
    assert calls == ["launch", "launch"]


def test_context_token_count_must_match(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runtime, model, result = _prepare(tmp_path, monkeypatch)
    run_preflight(runtime, model, result)
    approval = load_retry_plan()["planDigest"]
    launcher = _launcher(4, [])
    execute_phase(
        "one-token-smoke",
        approval=approval,
        runtime_root=runtime,
        model_root=model,
        result_root=result,
        indexes={"api_version": 1},
        launcher=launcher,
        executed=False,
        bind=False,
    )
    execute_phase(
        "short-generation",
        approval=approval,
        runtime_root=runtime,
        model_root=model,
        result_root=result,
        indexes={"api_version": 1},
        launcher=launcher,
        executed=False,
        bind=False,
    )
    document = execute_phase(
        "context-4096",
        approval=approval,
        runtime_root=runtime,
        model_root=model,
        result_root=result,
        indexes={"api_version": 1},
        launcher=_launcher(3, []),
        executed=False,
        bind=False,
    )
    assert document["exitClassification"] == "inference-failure"
    assert document["contextTokens"] == 4096
    assert document["repeatedTokenId"] == 574
