"""Envelope tests for both context lengths and the 12 GiB ceiling."""

from __future__ import annotations

import json
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.corpus import canonical_dumps
from patchpilot_intelligence_evals.memory_budget import decide_memory_budget, load_memory_budget
from patchpilot_intelligence_evals.memory_model import (
    CATEGORY_IDS,
    LOGICAL_PARAMETER_BYTES,
    classify_peak,
)


def _row(
    category_id: str,
    upper: int | None,
    *,
    status: str = "deterministic-calculation",
) -> dict[str, Any]:
    return {
        "categoryId": category_id,
        "unit": "bytes",
        "memoryDomain": "resident",
        "includedInTotal": True,
        "countsParameterPayload": category_id == "static_parameter_memory",
        "evidenceStatus": "unresolved" if upper is None else status,
        "lowerBoundBytes": upper,
        "upperBoundBytes": upper,
    }


def _complete(total: int) -> list[dict[str, Any]]:
    base, remainder = divmod(total, len(CATEGORY_IDS))
    rows = []
    for index, category_id in enumerate(CATEGORY_IDS):
        share = base + (remainder if index == len(CATEGORY_IDS) - 1 else 0)
        rows.append(_row(category_id, share))
    return rows


def test_both_envelopes_stay_unresolved() -> None:
    document = load_memory_budget()
    assert document["measurementPerformed"] is False
    assert document["ceilingBytes"] == MEMORY_CAP
    assert document["realModelExecuted"] is False
    assert document["productionReady"] is False
    assert [item["contextTokens"] for item in document["envelopes"]] == [4096, 8192]
    for envelope in document["envelopes"]:
        assert envelope["classification"] == "unresolved"
        assert envelope["upperBoundBytes"] is None
        assert envelope["lowerBoundBytes"] is None
        assert envelope["ceilingComparison"] == "unresolved"
        assert envelope["bytesRelativeToCeiling"] is None
        assert envelope["unresolvedCategoryIds"] == list(CATEGORY_IDS)
        static = envelope["categories"][0]
        assert static["logicalBytes"] == LOGICAL_PARAMETER_BYTES
        assert static["upperBoundBytes"] is None
        assert static["logicalBytesIncludedInPeak"] is False
    short = document["envelopes"][0]["categories"][4]["inputs"]
    long = document["envelopes"][1]["categories"][4]["inputs"]
    assert "contextTokens=4096" in short
    assert "contextTokens=8192" in long
    assert canonical_dumps(document) == canonical_dumps(decide_memory_budget())


def test_synthetic_ceiling_paths() -> None:
    exact = classify_peak(_complete(MEMORY_CAP))
    assert exact["classification"] == "proven-pass"
    assert exact["upperBoundBytes"] == MEMORY_CAP
    over = classify_peak(_complete(MEMORY_CAP + 1))
    assert over["classification"] == "proven-fail"
    assert over["bytesRelativeToCeiling"] == 1
    missing = _complete(MEMORY_CAP)
    missing[-1] = _row("safety_margin", None)
    unresolved = classify_peak(missing)
    assert unresolved["classification"] == "unresolved"
    assert unresolved["upperBoundBytes"] is None
    again = classify_peak(_complete(MEMORY_CAP))
    assert json.dumps(exact, sort_keys=True) == json.dumps(again, sort_keys=True)
