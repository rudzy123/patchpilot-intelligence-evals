"""Synthetic six-run execution. The launcher double does not call the runtime."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from patchpilot_intelligence_evals.baseline import run_baseline
from patchpilot_intelligence_evals.candidate_inference import GOLD_KEYS
from patchpilot_intelligence_evals.corpus import canonical_dumps, load_cases
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.measurement_plan import (
    HARNESS_CANDIDATE_ID,
    PROTOCOL_CANDIDATE_VERSION,
    MeasurementError,
)
from patchpilot_intelligence_evals.protocol import build_request
from patchpilot_intelligence_evals.schema_diagnostic_execution import (
    execute_diagnostic,
    load_run_template,
)
from patchpilot_intelligence_evals.schema_diagnostic_plan import load_schema_diagnostic_plan


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


def _selected_outputs(extra: dict[str, str] | None = None) -> dict[str, tuple[bytes, bytes]]:
    plan = load_schema_diagnostic_plan()
    selected = {row["caseId"] for row in plan["runs"]}
    outputs: dict[str, tuple[bytes, bytes]] = {}
    for case in load_cases():
        if case["caseId"] not in selected:
            continue
        request = build_request(case, plan["planDigest"])
        output = run_baseline(case)
        output["candidate"] = {
            "kind": "future-candidate",
            "name": HARNESS_CANDIDATE_ID,
            "version": PROTOCOL_CANDIDATE_VERSION,
        }
        output["explanationLabel"] = "generated-explanation"
        output["explanationText"] = "Synthetic diagnostic records authorized structured fields."
        if extra is not None:
            output.update(extra)
        envelope = {
            "candidateId": HARNESS_CANDIDATE_ID,
            "candidateVersion": PROTOCOL_CANDIDATE_VERSION,
            "findingExplanationOutput": output,
            "protocolVersion": "1.0.0",
            "requestId": request["requestId"],
            "schemaVersion": "1.0.0",
            "status": "success",
        }
        side = {
            "adapterFallback": False,
            "adapterTruncated": False,
            "innerFieldNames": sorted(output),
            "parseCategory": "parsed",
            "parseColumn": 0,
            "parseLine": 1,
            "parsePosition": 0,
            "trailingBytes": 0,
            "utf8": True,
        }
        outputs[str(request["requestId"])] = (
            canonical_dumps(envelope).encode("utf-8"),
            canonical_dumps(side).encode("utf-8"),
        )
    return outputs


def _run(
    tmp_path: Path,
    launcher: object,
    *,
    name: str,
    probe: object | None = None,
    executed: bool = False,
) -> tuple[dict[str, Any], Path]:
    plan = load_schema_diagnostic_plan()
    root = tmp_path / name
    summary = execute_diagnostic(
        approval=plan["planDigest"],
        runtime_root=tmp_path / "runtime",
        model_root=tmp_path / "model",
        result_root=root,
        indexes={"release_tensor_info": 1},
        launcher=launcher,  # type: ignore[arg-type]
        executed=executed,
        bind=False,
        probe=probe if probe is not None else (lambda _path: "passed"),  # type: ignore[arg-type]
    )
    return summary, root


def _flags(root: Path) -> dict[str, Any]:
    record = json.loads((root / "runs" / "case-ground-001-r1" / "run.json").read_text())
    return {
        "generationObserved": record["generationObserved"],
        "modelSessionCreated": record["modelSessionCreated"],
        "realModelExecuted": record["realModelExecuted"],
        "runInvoked": record["runInvoked"],
    }


def test_six_valid_runs_do_not_establish_systematic_failure(tmp_path: Path) -> None:
    outputs = _selected_outputs()
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
        stdout, side = outputs[config["request"]["requestId"]]
        return ExecutionResult("success", 0, stdout, b"", "reaped", 1, b"", (), side)

    summary, root = _run(tmp_path, launcher, name="valid-root")
    assert summary["diagnosticConclusion"] == "systematic-schema-failure-not-established"
    assert summary["completedRuns"] == 6
    assert summary["missingRuns"] == 0
    assert summary["candidateOutputSchemaFailureCount"] == 0
    assert summary["schemaValidCount"] == 6
    assert summary["thresholdMet"] is False
    assert summary["comparisonWinner"] is None
    assert summary["productionReady"] is False
    assert "Synthetic diagnostic records authorized structured fields." not in (
        root / "summary.json"
    ).read_text(encoding="utf-8")
    record = json.loads((root / "runs" / "case-ground-001-r1" / "run.json").read_text())
    assert record["schemaStatus"] == "valid"
    assert record["qualifyingCandidateOutputSchemaFailure"] is False
    assert record["adapterInnerFieldMutation"] is False
    assert (root / "runs" / "case-ground-001-r1" / "stdout.bin").stat().st_mode & 0o777 == 0o400
    assert all("valid-root" not in source for source in mounts)
    with pytest.raises(MeasurementError) as caught:
        execute_diagnostic(
            approval=load_schema_diagnostic_plan()["planDigest"],
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


def test_schema_failures_continue_and_can_meet_the_threshold(tmp_path: Path) -> None:
    outputs = _selected_outputs({"deterministicFacts": "hidden-value"})

    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        _observe(kwargs["observer"])
        config_dir = kwargs["config_dir"]
        config = json.loads((config_dir / "request.json").read_text(encoding="utf-8"))  # type: ignore[operator]
        stdout, side = outputs[config["request"]["requestId"]]
        return ExecutionResult("success", 0, stdout, b"", "reaped", 1, b"", (), side)

    summary, root = _run(tmp_path, launcher, name="invalid-root")
    assert summary["completedRuns"] == 6
    assert summary["candidateOutputSchemaFailureCount"] == 6
    assert summary["distinctCategoryCount"] == 6
    assert summary["thresholdMet"] is True
    assert summary["diagnosticConclusion"] == "systematic-schema-failure-established"
    assert summary["responseShapeConsistency"] == "consistent"
    assert _flags(root) == {
        "generationObserved": True,
        "modelSessionCreated": False,
        "realModelExecuted": False,
        "runInvoked": False,
    }
    assert "hidden-value" not in (root / "summary.json").read_text(encoding="utf-8")
    ready = json.loads((root / "track11-readiness.json").read_text(encoding="utf-8"))
    assert ready["readinessOutcome"] == "ready-for-disposition-review"
    assert ready["authorizesRejection"] is False
    assert ready["rejectionEligibleForReview"] is True
    assert ready["authorizesFullCorpus"] is False


def test_excessive_output_stops_and_keeps_raw_bytes(tmp_path: Path) -> None:
    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        _observe(kwargs["observer"])
        return ExecutionResult("output-limit-exceeded", 0, b"{}", b"", "reaped", 1, b"", ())

    summary, root = _run(tmp_path, launcher, name="limit-root")
    assert summary["completedRuns"] == 1
    assert summary["missingRuns"] == 5
    assert summary["diagnosticConclusion"] == "diagnostic-incomplete"
    assert (root / "runs" / "case-ground-001-r1" / "stdout.bin").read_bytes() == b"{}"
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
        "patchpilot_intelligence_evals.schema_diagnostic_execution.diagnose_response",
        _fail,
    )
    summary, root = _run(tmp_path, launcher, name="unclassified-root")
    assert summary["completedRuns"] == 1
    record = json.loads((root / "runs" / "case-ground-001-r1" / "run.json").read_text())
    assert record["recordKind"] == "unclassified-launch"
    assert (root / "runs" / "case-ground-001-r1" / "stdout.bin").read_bytes() == b"{}"
    assert summary["diagnosticConclusion"] == "diagnostic-incomplete"


def test_not_executed_template_stays_pre_execution() -> None:
    document = load_run_template()
    assert document["exitClassification"] == "not-executed"
    assert document["realModelExecuted"] is False
    assert document["runInvoked"] is False
    assert document["modelSessionCreated"] is False
    assert document["generationObserved"] is False


def test_observed_generation_sets_real_model_executed(tmp_path: Path) -> None:
    outputs = _selected_outputs({"deterministicFacts": "hidden-value"})

    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        _observe(kwargs["observer"])
        config_dir = kwargs["config_dir"]
        config = json.loads((config_dir / "request.json").read_text(encoding="utf-8"))  # type: ignore[operator]
        stdout, side = outputs[config["request"]["requestId"]]
        return ExecutionResult("success", 0, stdout, b"", "reaped", 1, b"", (), side)

    summary, root = _run(tmp_path, launcher, name="observed-root", executed=True)
    assert summary["diagnosticConclusion"] == "systematic-schema-failure-established"
    assert summary["thresholdMet"] is True
    assert _flags(root) == {
        "generationObserved": True,
        "modelSessionCreated": True,
        "realModelExecuted": True,
        "runInvoked": True,
    }
    assert "hidden-value" not in (root / "summary.json").read_text(encoding="utf-8")


def test_invoked_run_without_generation_is_not_real_model_execution(tmp_path: Path) -> None:
    outputs = _selected_outputs({"deterministicFacts": "hidden-value"})

    def launcher(*_args: object, **kwargs: object) -> ExecutionResult:
        _observe(kwargs["observer"])
        config_dir = kwargs["config_dir"]
        config = json.loads((config_dir / "request.json").read_text(encoding="utf-8"))  # type: ignore[operator]
        stdout, _side = outputs[config["request"]["requestId"]]
        return ExecutionResult("success", 0, stdout, b"", "reaped", 1, b"", ())

    _summary, root = _run(tmp_path, launcher, name="no-generation-root", executed=True)
    assert _flags(root) == {
        "generationObserved": False,
        "modelSessionCreated": True,
        "realModelExecuted": False,
        "runInvoked": True,
    }
