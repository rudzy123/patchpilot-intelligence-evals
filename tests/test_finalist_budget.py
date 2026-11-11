"""Artifact-budget boundaries, unknown sizes, and execution compatibility."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO

import pytest

from patchpilot_intelligence_evals.artifact_budget import (
    ARTIFACT_CAP,
    CONTEXT_CAP,
    MEMORY_CAP,
    budget_fits,
)
from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.finalist_budget import (
    RUNTIME_LISTED_BYTES,
    FinalistBudgetError,
    decide_finalist_budget,
    load_finalist_budget,
    track7_footprint,
    validate_finalist_budget,
)
from patchpilot_intelligence_evals.schemas import repo_root

_RECORD = "candidates/authorization/finalist-artifact-budget.json"


def test_committed_footprint_fails_and_memory_is_unknown() -> None:
    document = load_finalist_budget()
    finalist = document["finalists"][0]
    assert finalist["inventoryBytes"] == 4_717_588_977
    assert finalist["footprintBytes"] == 9_446_591_609
    assert finalist["artifactFit"] == "fail"
    assert finalist["memoryFit"] == "fail"
    assert finalist["contextFit"] == "pass"
    assert finalist["storageHeadroom"] == "pass"
    assert finalist["hardwareFit"] == "fail"
    assert finalist["peakMemoryBytes"] is None
    assert finalist["executionOutcome"] == "pass"
    assert document["verificationPerformed"] is False
    assert document["quantizationApproved"] is False
    assert document["runtimeInstallationStatus"] == "not-installed"
    assert document["locallyObservedArtifactDigests"] == []


def test_cap_edges_unknown_sizes_and_incompatible_execution() -> None:
    inventory = (ARTIFACT_CAP - RUNTIME_LISTED_BYTES) // 2
    under = track7_footprint(inventory, [], 0, 0, 0, RUNTIME_LISTED_BYTES)
    over = track7_footprint(inventory + 1, [], 0, 0, 0, RUNTIME_LISTED_BYTES)
    assert under == ARTIFACT_CAP - 1
    assert over == ARTIFACT_CAP + 1
    assert track7_footprint(10, [20, 30], 5, 6, 7, 8) == (10 + 20 + 30 + 5 + 6 + 7) * 2 + 8
    assert track7_footprint(1, [None], 1, 1, 1, 1) is None
    assert track7_footprint(1, [1], 1, 1, 1, None) is None
    exact = budget_fits(ARTIFACT_CAP, MEMORY_CAP, CONTEXT_CAP, quantization_present=False)
    assert exact["artifactFit"] == "pass"
    assert exact["memoryFit"] == "pass"
    assert exact["contextFit"] == "pass"
    one_over = budget_fits(
        ARTIFACT_CAP + 1,
        MEMORY_CAP + 1,
        CONTEXT_CAP - 1,
        quantization_present=False,
    )
    assert one_over["artifactFit"] == "fail"
    assert one_over["memoryFit"] == "fail"
    assert one_over["contextFit"] == "fail"
    unknown = budget_fits(None, None, None, quantization_present=False)
    assert unknown["hardwareFit"] == "fail"
    short_context = budget_fits(100, 100, 4096, quantization_present=False)
    assert short_context["contextFit"] == "fail"
    before = (repo_root() / _RECORD).read_bytes()
    incompatible = json.loads(json.dumps(decide_finalist_budget()))
    incompatible["finalists"][0]["properties"][0]["result"] = "fail"
    with pytest.raises(FinalistBudgetError) as caught:
        validate_finalist_budget(incompatible)
    assert caught.value.code == "arithmetic"
    assert (repo_root() / _RECORD).read_bytes() == before


def test_finalist_artifact_budget_validation_command() -> None:
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["finalist-artifact-budget-validation"])
    payload = json.loads(buffer.getvalue())
    assert code == 0
    assert payload["hardwareFit"] == "fail"
    assert payload["executionOutcome"] == "pass"
    assert payload["footprintBytes"] == 9_446_591_609
    assert payload["productionReady"] is False
