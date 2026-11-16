"""Corpus evaluation stays behind the memory phases and hides gold."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.cgroup_memory import ScopeSampler
from patchpilot_intelligence_evals.corrected_behavioral_measurement import execute_corpus
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.measurement_plan import MeasurementError
from patchpilot_intelligence_evals.measurement_retry_closeout import build_closeout
from patchpilot_intelligence_evals.measurement_retry_plan import load_retry_plan
from patchpilot_intelligence_evals.retry_track9_readiness import recommend


def test_corpus_is_withheld_without_8192(tmp_path: Path) -> None:
    root = tmp_path / "result"
    root.mkdir()
    root.chmod(0o700)
    with pytest.raises(MeasurementError) as caught:
        execute_corpus(
            approval=load_retry_plan()["planDigest"],
            runtime_root=tmp_path / "runtime",
            model_root=tmp_path / "model",
            result_root=root,
            indexes={"api_version": 1},
            executed=False,
            bind=False,
        )
    assert caught.value.code == "prior-phase-failed"


def test_summary_has_no_winner_and_track9_stays_advisory(tmp_path: Path) -> None:
    root = tmp_path / "result"
    root.mkdir()
    root.chmod(0o700)
    for name, document in (
        ("preflight.json", {"status": "ok", "runInvoked": False}),
        (
            "template-compatibility.json",
            {
                "compatibility": "supported",
                "renderedDigest": (
                    "5c61ee0b595fa4c5b295feb233b312c38b779f7840f3f39c82aef51da9061e5d"
                ),
                "runInvoked": False,
                "sessionCreated": False,
            },
        ),
    ):
        (root / name).write_text(json.dumps(document), encoding="utf-8")
    for phase in ("one-token-smoke", "short-generation", "context-4096", "context-8192"):
        (root / f"{phase}.json").write_text(
            json.dumps({"exitClassification": "success", "stopCause": None}),
            encoding="utf-8",
        )

    def launch(fixture: Path, arguments: tuple[str, ...], **kwargs: object) -> ExecutionResult:
        observer = kwargs["observer"]
        assert isinstance(observer, ScopeSampler)
        observer.samples.append(
            {
                "cgroupCurrentBytes": 4,
                "cgroupPeakBytes": 8,
                "memoryEvents": {"high": 0, "low": 0, "max": 0, "oom": 0, "oomKill": 0},
                "oomEvents": 0,
                "phase": "cold",
                "processRssBytes": 1,
                "processTreeRssBytes": 1,
                "virtualAddressBytes": 9,
            }
        )
        report = {
            "inputTokenCount": 4,
            "network": {"dns": "gaierror", "ipv4": "OSError"},
            "newTokenCount": 0,
            "outputDigest": None,
            "status": "ok",
            "wallSeconds": 0.1,
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

    summary = execute_corpus(
        approval=load_retry_plan()["planDigest"],
        runtime_root=tmp_path / "runtime",
        model_root=tmp_path / "model",
        result_root=root,
        indexes={"api_version": 1},
        launcher=launch,
        executed=False,
        bind=False,
    )
    assert summary["comparisonWinner"] is None
    assert summary["calibrationStatus"] == "not-approved"
    assert summary["productionReady"] is False
    assert summary["selectionOutcome"] == "no-selection"
    assert summary["gatesUnchanged"] is True
    assert summary["percentageGatesCalibrated"] is False
    closeout = build_closeout(root)
    readiness = recommend(closeout, summary)
    assert closeout["comparisonWinner"] is None
    assert readiness["productionReady"] is False
    assert readiness["selectionOutcome"] == "no-selection"
    assert readiness["verdict"] in {
        "TRACK 9 EVALUATION REVIEW NOT READY",
        "TRACK 9 EVALUATION REVIEW READY WITH DOCUMENTED RESIDUALS",
        "TRACK 9 EVALUATION REVIEW READY",
        "BLOCKED BY UNRESOLVED AUTHORITY",
    }


def test_not_ready_template_and_blocked_authority() -> None:
    from patchpilot_intelligence_evals.retry_track9_readiness import build_track9_template

    template = build_track9_template()
    assert template["verdict"] == "TRACK 9 EVALUATION REVIEW NOT READY"
    assert template["measurementPerformed"] is False
    blocked = recommend(
        {
            "planDigest": "0" * 64,
            "productionReady": False,
            "selectionOutcome": "no-selection",
            "calibrationStatus": "not-approved",
            "closeoutState": "stopped",
            "realModelExecuted": False,
        },
        None,
    )
    assert blocked["verdict"] == "BLOCKED BY UNRESOLVED AUTHORITY"
    assert blocked["productionReady"] is False
