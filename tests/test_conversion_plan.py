"""Conversion stays unauthorized. No toolchain is installed."""

from __future__ import annotations

import json

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.conversion_equivalence import ATOL, RTOL
from patchpilot_intelligence_evals.conversion_plan import (
    decide_conversion_plan,
    load_conversion_plan,
)


def test_three_toolchains_stay_unauthorized(capsys: pytest.CaptureFixture[str]) -> None:
    document = load_conversion_plan()
    assert document == decide_conversion_plan()
    assert document["authorizationOutcome"] == "not-authorized"
    assert document["conversionStatus"] == "not-performed"
    assert document["offlineClosed"] is False
    assert document["equivalenceMeasured"] is False
    assert document["equivalence"]["atol"] == ATOL == "0.0001"
    assert document["equivalence"]["rtol"] == RTOL == "0.001"
    assert document["equivalence"]["convertedProvenance"] == "locally-converted"
    assert document["equivalence"]["publisherProvided"] is False
    assert document["equivalence"]["opsetDisposition"] == "unresolved"
    assert document["locallyObservedArtifactDigests"] == []
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    text = json.dumps(document)
    assert "https://" not in text
    assert "/home/" not in text
    identities = [item["toolchainId"] for item in document["toolchains"]]
    assert identities == ["optimum-onnx", "onnxruntime-genai", "pytorch-onnx-exporter"]
    for item in document["toolchains"]:
        assert item["authorizationOutcome"] == "not-authorized"
        assert "sources-not-independently-eligible" in item["disqualifiers"]
    optimum = document["toolchains"][0]
    assert optimum["immutableRevision"] == "d2328e386a81b0970a458a7570a38b131414edc6"
    assert optimum["licenseName"] == "Apache-2.0"
    assert "export-defaults-not-offline-closed" in optimum["disqualifiers"]
    genai = document["toolchains"][1]
    assert genai["versionTag"] == "v0.19.0"
    assert genai["licenseName"] == "MIT"
    assert "architecture-support-unresolved" in genai["disqualifiers"]
    exporter = document["toolchains"][2]
    assert exporter["versionTag"] == "unresolved"
    assert exporter["immutableRevision"] is None
    assert exporter["licenseName"] == "unresolved"
    assert main(["onnx-conversion-plan-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["authorizationOutcome"] == "not-authorized"
    assert summary["equivalenceMeasured"] is False
    assert summary["productionReady"] is False
