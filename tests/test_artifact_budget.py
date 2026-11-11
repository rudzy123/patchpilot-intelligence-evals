"""Artifact budget boundaries and unknown-value failure."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.artifact_budget import (
    ARTIFACT_CAP,
    MEMORY_CAP,
    artifact_footprint,
    budget_fits,
    decide_artifact_budget,
    load_artifact_budget,
)
from patchpilot_intelligence_evals.cli import main


def test_committed_budgets_fail_closed(capsys: pytest.CaptureFixture[str]) -> None:
    document = load_artifact_budget()
    assert document == decide_artifact_budget()
    assert document["artifactCapBytes"] == 8589934592
    assert document["memoryCapBytes"] == 12884901888
    assert document["contextCapTokens"] == 8192
    assert all(item["hardwareFit"] == "fail" for item in document["families"])
    qwen, _, smol, olmo, gemma = document["families"]
    assert qwen["contextFit"] == "pass"
    assert gemma["contextFit"] == "pass"
    assert smol["contextFit"] == "fail"
    assert olmo["contextFit"] == "fail"
    assert smol["directoryExceedsCap"] is True
    assert smol["pairQualifies"] is False
    assert smol["footprintBytes"] is None
    assert main(["artifact-budget-validation"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["hardwarePassCount"] == 0


def test_exact_caps_pass_and_unknowns_fail() -> None:
    profile = json.loads(
        Path("candidates/authorization/evaluation-hardware-profile.json").read_text(
            encoding="utf-8"
        )
    )
    envelope = profile["resourceEnvelope"]
    assert envelope["maximumArtifactBytes"] == ARTIFACT_CAP
    assert envelope["maximumPeakProcessMemoryBytes"] == MEMORY_CAP
    exact = artifact_footprint(ARTIFACT_CAP - 30, [10, 20], 0, 0, 0)
    assert exact == ARTIFACT_CAP
    fits = budget_fits(exact, MEMORY_CAP, 8192, quantization_present=False)
    assert fits["artifactFit"] == "pass"
    assert fits["memoryFit"] == "pass"
    assert fits["hardwareFit"] == "pass"
    over = budget_fits(ARTIFACT_CAP + 1, MEMORY_CAP, 8192, quantization_present=False)
    assert over["artifactFit"] == "fail"
    memory = budget_fits(ARTIFACT_CAP, MEMORY_CAP + 1, 8192, quantization_present=False)
    assert memory["memoryFit"] == "fail"
    unknown = artifact_footprint(1, [2, None], 3, 4, 5)
    assert unknown is None
    assert budget_fits(unknown, None, None, quantization_present=False)["hardwareFit"] == "fail"
    summed = artifact_footprint(100, [20, 30], 5, 7, 8)
    assert summed == 170
    quantized = budget_fits(100, 100, 8192, quantization_present=True)
    assert quantized["artifactFit"] == "fail"
    assert quantized["hardwareFit"] == "fail"
