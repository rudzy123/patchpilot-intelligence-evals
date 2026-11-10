"""Track 6A runtime authorization. No runtime is installed."""

from __future__ import annotations

from patchpilot_intelligence_evals.runtime_authorization import (
    load_authorization as load_track5_authorization,
)
from patchpilot_intelligence_evals.runtime_security import (
    decide,
    failing_criteria,
    load_assessment,
    load_authorization,
)


def test_track5_runtime_decision_remains_no_runtime() -> None:
    assert load_track5_authorization()["authorizationOutcome"] == "no-runtime"


def test_v2_authorizes_only_onnxruntime_without_installation() -> None:
    authorized = load_authorization()
    assert authorized["authorizationOutcome"] == "authorized"
    assert authorized["runtimeId"] == "onnxruntime"
    assert authorized["versionTag"] == "v1.31.1"
    assert authorized["immutableRevision"] == "6af1a932e2286d5c58166085d24c68783033edee"
    assert authorized["artifactFormat"] == "onnx"
    assert authorized["candidateFormatGap"] is True
    assert authorized["installedDuringSession"] is False
    assert authorized["installationAuthorized"] is False
    assert authorized["candidateSelected"] is False
    assert authorized["locallyObservedArtifactDigests"] == []
    assert authorized["acquisitionStatus"] == "not-acquired"
    assert authorized["executionStatus"] == "not-executed"
    assert authorized["productionReady"] is False
    assert authorized["realModelExecuted"] is False
    failed = {item["runtimeId"] for item in authorized["disqualifiers"]}
    assert failed == {"llama-cpp", "transformers"}


def test_two_passing_runtimes_are_not_authorized() -> None:
    assessment = load_assessment()
    for runtime in assessment["runtimes"]:
        if runtime["runtimeId"] != "llama-cpp":
            continue
        for name in runtime["criteria"]:
            runtime["criteria"][name] = "pass"
        runtime["disqualifiers"] = []
    decision = decide(assessment)
    assert decision["authorizationOutcome"] == "no-runtime"
    assert decision["runtimeId"] is None
    assert decision["installationAuthorized"] is False


def test_all_failing_runtimes_preserve_no_runtime() -> None:
    assessment = load_assessment()
    for runtime in assessment["runtimes"]:
        runtime["criteria"]["cpu-only"] = "fail"
        runtime["disqualifiers"] = failing_criteria(runtime)
    decision = decide(assessment)
    assert decision["authorizationOutcome"] == "no-runtime"
    assert {item["runtimeId"] for item in decision["disqualifiers"]} == {
        "llama-cpp",
        "onnxruntime",
        "transformers",
    }
