"""Runtime records. No runtime is installed and no model is executed."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.runtime_authorization import (
    CRITERIA,
    decide,
    load_assessment,
    load_authorization,
)
from patchpilot_intelligence_evals.schemas import error_paths


def _pass_runtime(assessment: dict[str, Any], runtime_id: str) -> None:
    runtimes = assessment["runtimes"]
    assert isinstance(runtimes, list)
    for runtime in runtimes:
        assert isinstance(runtime, dict)
        if runtime["runtimeId"] == runtime_id:
            runtime["criteria"] = {name: "pass" for name in CRITERIA}
            runtime["disqualifiers"] = []


def test_committed_runtime_decision_is_no_runtime(capsys: pytest.CaptureFixture[str]) -> None:
    assessment = load_assessment()
    authorization = load_authorization()
    assert len(assessment["runtimes"]) == 3
    assert assessment["installedDuringSession"] is False
    assert authorization["authorizationOutcome"] == "no-runtime"
    assert authorization["runtimeId"] is None
    assert authorization["versionTag"] is None
    assert authorization["immutableRevision"] is None
    assert authorization["locallyObservedArtifactDigests"] == []
    assert authorization["productionReady"] is False
    assert authorization["acquisitionStatus"] == "not-acquired"
    assert authorization["executionStatus"] == "not-executed"
    assert [item["runtimeId"] for item in authorization["disqualifiers"]] == [
        "llama-cpp",
        "onnxruntime",
        "transformers",
    ]
    for runtime in assessment["runtimes"]:
        assert "fail" in runtime["criteria"].values()
    assert main(["runtime-assessment-validation"]) == 0
    assert main(["runtime-authorization-validation"]) == 0
    captured = capsys.readouterr().out.strip().splitlines()
    assert json.loads(captured[0])["status"] == "ok"
    assert json.loads(captured[1])["authorizationOutcome"] == "no-runtime"


def test_one_passing_runtime_is_the_only_authorized_outcome() -> None:
    assessment = deepcopy(load_assessment())
    _pass_runtime(assessment, "llama-cpp")
    decision = decide(assessment)
    assert decision["authorizationOutcome"] == "authorized"
    assert decision["runtimeId"] == "llama-cpp"
    assert decision["installedDuringSession"] is False
    assert decision["acquisitionStatus"] == "not-acquired"
    assert "llama-cpp" not in {item["runtimeId"] for item in decision["disqualifiers"]}


def test_two_passing_runtimes_remain_no_runtime() -> None:
    assessment = deepcopy(load_assessment())
    _pass_runtime(assessment, "llama-cpp")
    _pass_runtime(assessment, "onnxruntime")
    decision = decide(assessment)
    assert decision["authorizationOutcome"] == "no-runtime"
    assert decision["runtimeId"] is None


def test_assessment_rejects_a_fourth_runtime() -> None:
    assessment = load_assessment()
    assessment["runtimes"].append(deepcopy(assessment["runtimes"][0]))
    assert error_paths("runtime-assessment", assessment)
