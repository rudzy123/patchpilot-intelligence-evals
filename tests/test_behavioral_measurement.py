"""Corpus measurement keeps gold off the child and stops on resident failure."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.behavioral_measurement import execute_corpus
from patchpilot_intelligence_evals.candidate_inference import GOLD_KEYS
from patchpilot_intelligence_evals.cgroup_memory import ScopeSampler
from patchpilot_intelligence_evals.context_measurement import PHASE_FILES
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.measurement_plan import (
    MeasurementError,
    load_measurement_plan,
)


def _launch(mode: str) -> tuple[Callable[..., ExecutionResult], list[dict[str, object]]]:
    seen: list[dict[str, object]] = []

    def launch(fixture: Path, arguments: tuple[str, ...], **kwargs: object) -> ExecutionResult:
        config_dir = kwargs["config_dir"]
        assert isinstance(config_dir, Path)
        config = json.loads((config_dir / "request.json").read_text(encoding="utf-8"))
        seen.append(config)
        observer = kwargs["observer"]
        assert isinstance(observer, ScopeSampler)
        peak = 10
        oom = 1 if mode == "oom" else 0
        if mode == "ceiling":
            peak = 12884901888 + 1
        samples = observer.samples
        samples.append(
            {
                "cgroupCurrentBytes": 1,
                "cgroupPeakBytes": None if mode == "missing" else peak,
                "oomEvents": oom,
                "phase": "cold",
                "processRssBytes": 1,
                "processTreeRssBytes": 1,
                "virtualAddressBytes": 4,
            }
        )
        report = {"network": {"dns": "gaierror", "ipv4": "OSError"}, "status": "ok"}
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

    return launch, seen


def test_corpus_is_withheld_and_gold_stays_unmounted(tmp_path: Path) -> None:
    plan = load_measurement_plan()
    with pytest.raises(MeasurementError) as caught:
        execute_corpus(
            approval=plan["planDigest"],
            runtime_root=tmp_path,
            model_root=tmp_path,
            result_root=tmp_path,
            indexes={"api_version": 1},
            launcher=_launch("ok")[0],
            bind=False,
        )
    assert caught.value.code == "prior-phase-failed"
    (tmp_path / PHASE_FILES["context-8192"]).write_text(
        json.dumps({"exitClassification": "success", "stopCause": None}),
        encoding="utf-8",
    )
    launcher, seen = _launch("ok")
    summary = execute_corpus(
        approval=plan["planDigest"],
        runtime_root=tmp_path,
        model_root=tmp_path,
        result_root=tmp_path,
        indexes={"api_version": 1},
        launcher=launcher,
        bind=False,
    )
    assert summary["comparisonWinner"] is None
    assert summary["calibrationStatus"] == "not-approved"
    assert summary["productionReady"] is False
    for config in seen:
        text = json.dumps(config)
        request = config["request"]
        assert isinstance(request, dict)
        assert GOLD_KEYS.isdisjoint(request)
        for key in GOLD_KEYS:
            assert f'"{key}"' not in text
    runs = list((tmp_path / "runs").glob("*.json"))
    assert len(runs) == 72


def test_resident_failures_stop_the_corpus(tmp_path: Path) -> None:
    plan = load_measurement_plan()
    (tmp_path / PHASE_FILES["context-8192"]).write_text(
        json.dumps({"exitClassification": "success", "stopCause": None}),
        encoding="utf-8",
    )
    for mode in ("oom", "ceiling", "missing"):
        root = tmp_path / mode
        root.mkdir()
        (root / PHASE_FILES["context-8192"]).write_text(
            json.dumps({"exitClassification": "success", "stopCause": None}),
            encoding="utf-8",
        )
        with pytest.raises(MeasurementError):
            execute_corpus(
                approval=plan["planDigest"],
                runtime_root=root,
                model_root=root,
                result_root=root,
                indexes={"api_version": 1},
                launcher=_launch(mode)[0],
                bind=False,
            )
        assert len(list((root / "runs").glob("*.json"))) == 1
