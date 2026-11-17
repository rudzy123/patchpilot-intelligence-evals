"""Synthetic corpus execution. The launcher double does not call the runtime."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from patchpilot_intelligence_evals.baseline import run_baseline
from patchpilot_intelligence_evals.candidate_inference import GOLD_KEYS
from patchpilot_intelligence_evals.corpus import canonical_dumps, load_cases
from patchpilot_intelligence_evals.corpus_continuation import execute_continuation
from patchpilot_intelligence_evals.corpus_continuation_plan import load_corpus_plan
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.measurement_plan import (
    HARNESS_CANDIDATE_ID,
    PROTOCOL_CANDIDATE_VERSION,
    MeasurementError,
)
from patchpilot_intelligence_evals.protocol import build_request


def _observe(observer: object) -> None:
    observer.samples.append(  # type: ignore[attr-defined]
        {
            "cgroupCurrentBytes": 512,
            "cgroupPeakBytes": 1024,
            "oomEvents": 0,
            "phase": "cold",
            "processRssBytes": 256,
            "processTreeRssBytes": 256,
            "virtualAddressBytes": 2048,
        }
    )
    observer.child_state = "exited"  # type: ignore[attr-defined]
    observer.last_complete = {"cgroupPeakBytes": 1024, "oomEvents": 0}  # type: ignore[attr-defined]
    observer.disposition = "post-exit-scope-removed"  # type: ignore[attr-defined]


def _run(
    tmp_path: Path,
    launcher: object,
    *,
    name: str,
    probe: object | None = None,
    monkeypatch: pytest.MonkeyPatch | None = None,
) -> tuple[dict[str, Any], Path]:
    if monkeypatch is not None:
        monkeypatch.setattr(
            "patchpilot_intelligence_evals.corpus_continuation.require_corpus_approval",
            lambda _supplied, root=None: load_corpus_plan(),
        )
    plan = load_corpus_plan()
    root = tmp_path / name
    summary = execute_continuation(
        approval=plan["planDigest"],
        runtime_root=tmp_path / "runtime",
        model_root=tmp_path / "model",
        result_root=root,
        indexes={"release_tensor_info": 1},
        launcher=launcher,  # type: ignore[arg-type]
        executed=False,
        bind=False,
        probe=probe if probe is not None else (lambda _path: "passed"),  # type: ignore[arg-type]
    )
    return summary, root


def _success_outputs() -> dict[str, bytes]:
    plan = load_corpus_plan()
    outputs: dict[str, bytes] = {}
    for case in load_cases():
        request = build_request(case, plan["planDigest"])
        output = run_baseline(case)
        output["candidate"] = {
            "kind": "future-candidate",
            "name": HARNESS_CANDIDATE_ID,
            "version": PROTOCOL_CANDIDATE_VERSION,
        }
        output["explanationLabel"] = "generated-explanation"
        output["explanationText"] = "Synthetic continuation records authorized structured fields."
        envelope = {
            "candidateId": HARNESS_CANDIDATE_ID,
            "candidateVersion": PROTOCOL_CANDIDATE_VERSION,
            "findingExplanationOutput": output,
            "protocolVersion": "1.0.0",
            "requestId": request["requestId"],
            "schemaVersion": "1.0.0",
            "status": "success",
        }
        outputs[str(request["requestId"])] = canonical_dumps(envelope).encode("utf-8")
    return outputs


def test_sealed_corpus_keeps_authority_and_hides_gold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    outputs = _success_outputs()
    mounts: list[str] = []

    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        _observe(kwargs["observer"])
        config_dir = kwargs["config_dir"]
        text = (config_dir / "request.json").read_text(encoding="utf-8")  # type: ignore[operator]
        for key in GOLD_KEYS:
            assert f'"{key}"' not in text
        config = json.loads(text)
        for mount in kwargs["extra_mounts"]:  # type: ignore[attr-defined]
            mounts.append(str(mount.source))
        return ExecutionResult(
            "success",
            0,
            outputs[config["request"]["requestId"]],
            b"",
            "reaped",
            1,
            b"",
            (),
        )

    summary, root = _run(tmp_path, launcher, name="complete-root", monkeypatch=monkeypatch)
    assert summary["completeness"] == "complete"
    assert summary["completedRuns"] == 72
    assert summary["missingRuns"] == 0
    assert summary["comparisonWinner"] is None
    assert summary["comparisonStatus"] == "missing-result"
    assert summary["comparisonReason"] == "missing-right"
    assert summary["calibrationInterpretation"] == "not-approved"
    assert summary["productionReady"] is False
    assert summary["repetitionConsistency"] == "consistent"
    assert summary["realModelExecuted"] is False
    assert len(summary["capabilities"]) == 10
    assert len(summary["gates"]) == 10
    assert len(summary["metrics"]) == 15
    record = json.loads((root / "runs" / "case-ground-001-r1" / "run.json").read_text())
    assert record["exitClassification"] == "success"
    assert record["failureAuthority"] is None
    assert record["cgroupPeakBytes"] == 1024
    assert record["cleanupStatus"] == "reaped"
    stored = root / "runs" / "case-ground-001-r1" / "stdout.bin"
    assert stored.stat().st_mode & 0o777 == 0o400
    assert "explanationText" not in (root / "summary.json").read_text(encoding="utf-8")
    assert all("complete-root" not in source for source in mounts)
    with pytest.raises(MeasurementError) as caught:
        execute_continuation(
            approval=load_corpus_plan()["planDigest"],
            runtime_root=tmp_path / "runtime",
            model_root=tmp_path / "model",
            result_root=root,
            indexes={"release_tensor_info": 1},
            launcher=launcher,
            executed=False,
            bind=False,
            probe=lambda _path: "passed",
        )
    assert caught.value.code == "result-root-reuse"


def test_excessive_output_stops_and_keeps_raw_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        _observe(kwargs["observer"])
        return ExecutionResult("output-limit-exceeded", 0, b"{}", b"", "reaped", 1, b"", ())

    summary, root = _run(tmp_path, launcher, name="stop-root", monkeypatch=monkeypatch)
    assert summary["completedRuns"] == 1
    assert summary["missingRuns"] == 71
    assert summary["failureAuthorityCounts"]["protocol"] == 1
    stored = root / "runs" / "case-ground-001-r1" / "stdout.bin"
    assert stored.read_bytes() == b"{}"
    closeout = json.loads((root / "closeout.json").read_text(encoding="utf-8"))
    assert closeout["closeoutState"] == "stopped"
    assert closeout["stopCause"] == "excessive-output"
    assert closeout["retention"] == "retained"


def test_unclassified_launch_keeps_the_raw_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        _observe(kwargs["observer"])
        return ExecutionResult("success", 0, b"{}", b"", "reaped", 1, b"", ())

    def _fail(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise OSError("seal")

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.corpus_continuation.diagnose_response",
        _fail,
    )
    summary, root = _run(tmp_path, launcher, name="unclassified-root", monkeypatch=monkeypatch)
    assert summary["completedRuns"] == 1
    record = json.loads((root / "runs" / "case-ground-001-r1" / "run.json").read_text())
    assert record["recordKind"] == "unclassified-launch"
    assert (root / "runs" / "case-ground-001-r1" / "stdout.bin").read_bytes() == b"{}"
    ready = json.loads((root / "track10-readiness.json").read_text(encoding="utf-8"))
    assert ready["verdict"] == "TRACK 10 CANDIDATE DISPOSITION REVIEW NOT READY"


def test_post_exit_read_does_not_drop_a_completed_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from patchpilot_intelligence_evals.cgroup_memory import resolve_scope_observation

    outputs = _success_outputs()
    launches: list[str] = []

    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        observer = kwargs["observer"]
        _observe(observer)
        sealed = {
            "cgroupCurrentBytes": 512,
            "cgroupPeakBytes": 1024,
            "oomEvents": 0,
            "telemetry": "complete",
        }
        decision = resolve_scope_observation(
            child_state="exited",
            read_error="enxio",
            sample=None,
            last_complete=sealed,
        )
        assert decision["classification"] is None
        config = json.loads((kwargs["config_dir"] / "request.json").read_text(encoding="utf-8"))  # type: ignore[operator]
        launches.append(str(config["request"]["requestId"]))
        return ExecutionResult(
            "success",
            0,
            outputs[config["request"]["requestId"]],
            b"",
            "reaped",
            1,
            b"",
            (),
        )

    summary, root = _run(tmp_path, launcher, name="advance-root", monkeypatch=monkeypatch)
    assert summary["completeness"] == "complete"
    assert summary["completedRuns"] == 72
    assert len(launches) == 72
    assert len(set(launches)) == 24
    assert (root / "runs" / "case-ground-001-r1" / "run.json").is_file()
    assert (root / "runs" / "case-ground-001-r2" / "run.json").is_file()
    assert (root / "runs" / "case-stale-003-r3" / "run.json").is_file()


def test_contradictory_telemetry_stops_before_the_next_case(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        observer = kwargs["observer"]
        _observe(observer)
        observer.blocked_classification = "telemetry-unresolved"  # type: ignore[attr-defined]
        return ExecutionResult("success", 0, b"{}", b"", "reaped", 1, b"", ())

    summary, root = _run(tmp_path, launcher, name="contradiction-root", monkeypatch=monkeypatch)
    assert summary["completedRuns"] == 1
    assert summary["missingRuns"] == 71
    record = json.loads((root / "runs" / "case-ground-001-r1" / "run.json").read_text())
    assert record["exitClassification"] == "telemetry-unresolved"
    assert record["recordKind"] == "run"
    assert (root / "runs" / "case-ground-001-r1" / "stdout.bin").read_bytes() == b"{}"
    assert not (root / "runs" / "case-ground-001-r2").exists()


def test_isolation_failure_stops_without_a_later_case(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        observer = kwargs["observer"]
        observer.blocked_classification = "infrastructure-failure"  # type: ignore[attr-defined]
        return ExecutionResult("success", 0, b"{}", b"", "reaped", 1, b"", ())

    summary, root = _run(tmp_path, launcher, name="isolation-root", monkeypatch=monkeypatch)
    assert summary["completedRuns"] == 1
    assert summary["failureAuthorityCounts"]["security-boundary"] == 1
    record = json.loads((root / "runs" / "case-ground-001-r1" / "run.json").read_text())
    assert record["exitClassification"] == "isolation-failure"
    assert not (root / "runs" / "case-ground-002-r1").exists()
