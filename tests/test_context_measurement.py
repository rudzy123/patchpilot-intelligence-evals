"""Context phases stay behind their prerequisites and exact token counts."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.cgroup_memory import ScopeSampler
from patchpilot_intelligence_evals.context_measurement import (
    PHASE_FILES,
    execute_phase,
    withheld,
)
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.measurement_plan import (
    MeasurementError,
    load_measurement_plan,
)


def _passed(root: Path, phase: str, payload: dict[str, object]) -> None:
    (root / PHASE_FILES[phase]).write_text(json.dumps(payload), encoding="utf-8")


def _launcher(token_count: int) -> Callable[..., ExecutionResult]:
    def launch(fixture: Path, arguments: tuple[str, ...], **kwargs: object) -> ExecutionResult:
        observer = kwargs["observer"]
        assert isinstance(observer, ScopeSampler)
        samples = observer.samples
        samples.append(
            {
                "cgroupCurrentBytes": 4,
                "cgroupPeakBytes": 8,
                "oomEvents": 0,
                "phase": "cold",
                "processRssBytes": 1,
                "processTreeRssBytes": 1,
                "virtualAddressBytes": 9,
            }
        )
        samples.append(
            {
                "cgroupCurrentBytes": 4,
                "cgroupPeakBytes": 8,
                "oomEvents": 0,
                "phase": "warm",
                "processRssBytes": 1,
                "processTreeRssBytes": 1,
                "virtualAddressBytes": 9,
            }
        )
        report = {
            "coldGenerationSeconds": 0.1,
            "firstTokenSeconds": 0.1,
            "generationSeconds": 0.1,
            "inputTokenCount": token_count,
            "loadSeconds": 0.1,
            "network": {"dns": "gaierror", "ipv4": "OSError"},
            "newTokenCount": 1,
            "outputDigest": "ab" * 32,
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


def test_later_phase_is_withheld_until_the_prior_record_passes(tmp_path: Path) -> None:
    plan = load_measurement_plan()
    assert withheld("context-8192", tmp_path) is True
    _passed(tmp_path, "preflight", {"status": "ok", "realModelExecuted": False})
    _passed(tmp_path, "one-token-smoke", {"exitClassification": "success", "stopCause": None})
    _passed(tmp_path, "short-generation", {"exitClassification": "success", "stopCause": None})
    _passed(
        tmp_path, "context-4096", {"exitClassification": "telemetry-unresolved", "stopCause": "x"}
    )
    with pytest.raises(MeasurementError) as caught:
        execute_phase(
            "context-8192",
            approval=plan["planDigest"],
            runtime_root=tmp_path,
            model_root=tmp_path,
            result_root=tmp_path,
            indexes={"api_version": 1},
            launcher=_launcher(8192),
            bind=False,
        )
    assert caught.value.code == "prior-phase-failed"
    assert withheld("context-8192", tmp_path) is True


def test_context_records_the_exact_token_count(tmp_path: Path) -> None:
    plan = load_measurement_plan()
    _passed(tmp_path, "preflight", {"status": "ok", "realModelExecuted": False})
    _passed(tmp_path, "one-token-smoke", {"exitClassification": "success", "stopCause": None})
    _passed(tmp_path, "short-generation", {"exitClassification": "success", "stopCause": None})
    document = execute_phase(
        "context-4096",
        approval=plan["planDigest"],
        runtime_root=tmp_path,
        model_root=tmp_path,
        result_root=tmp_path,
        indexes={"api_version": 1},
        launcher=_launcher(4096),
        bind=False,
    )
    assert document["contextTokens"] == 4096
    assert document["exitClassification"] == "success"
    assert document["repeatedTokenId"] == 574
    mismatch = execute_phase(
        "context-8192",
        approval=plan["planDigest"],
        runtime_root=tmp_path,
        model_root=tmp_path,
        result_root=tmp_path,
        indexes={"api_version": 1},
        launcher=_launcher(3),
        bind=False,
    )
    assert mismatch["exitClassification"] == "inference-failure"
    assert mismatch["contextTokens"] == 8192
