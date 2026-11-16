"""Context memory conclusions. Smoke evidence cannot establish eligibility."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.measurement_retry_closeout import (
    build_closeout,
    context_memory_conclusion,
    load_closeout_template,
)

_SMOKE_PEAK = 46_288_896


def test_empty_required_phase_set_is_unavailable() -> None:
    conclusion = context_memory_conclusion(
        {"one-token-smoke": _phase(_SMOKE_PEAK)},
        required=(),
    )
    assert conclusion == "unavailable"


def test_absent_context_records_are_unavailable() -> None:
    assert context_memory_conclusion({}) == "unavailable"
    assert context_memory_conclusion({"context-4096": None, "context-8192": None}) == (
        "unavailable"
    )


def test_smoke_result_does_not_establish_context_eligibility() -> None:
    conclusion = context_memory_conclusion({"one-token-smoke": _phase(_SMOKE_PEAK)})
    assert conclusion == "unavailable"


def test_only_4096_or_withheld_8192_is_unavailable() -> None:
    partial = {"context-4096": _phase(1024), "context-8192": None}
    assert context_memory_conclusion(partial) == "unavailable"
    assert context_memory_conclusion({"context-4096": _phase(1024)}) == "unavailable"


def test_complete_phases_within_ceiling_are_accepted() -> None:
    records = {"context-4096": _phase(1024), "context-8192": _phase(2048)}
    assert context_memory_conclusion(records) == "within-ceiling"


def test_exact_ceiling_is_within_ceiling() -> None:
    records = {
        "context-4096": _phase(MEMORY_CAP),
        "context-8192": _phase(MEMORY_CAP),
    }
    assert context_memory_conclusion(records) == "within-ceiling"


def test_one_byte_above_ceiling_is_exceeded() -> None:
    records = {
        "context-4096": _phase(MEMORY_CAP),
        "context-8192": _phase(MEMORY_CAP + 1),
    }
    assert context_memory_conclusion(records) == "exceeded"


def test_missing_peak_is_unresolved() -> None:
    cold = _window(1024)
    cold["cgroupPeakBytes"] = None
    records = {
        "context-4096": _phase(1024, cold=cold),
        "context-8192": _phase(1024),
    }
    assert context_memory_conclusion(records) == "unresolved"


def test_contradictory_telemetry_is_unresolved() -> None:
    cold = _window(1024, current=1025)
    records = {
        "context-4096": _phase(1024, cold=cold),
        "context-8192": _phase(1024),
    }
    assert context_memory_conclusion(records) == "unresolved"


def test_oom_is_a_measured_failure() -> None:
    records = {
        "context-4096": _phase(1024, cold=_window(1024, oom=1)),
        "context-8192": _phase(1024),
    }
    assert context_memory_conclusion(records) == "oom"


def test_cleanup_failure_is_unavailable() -> None:
    records = {
        "context-4096": _phase(1024, process_cleanup="failed"),
        "context-8192": _phase(1024),
    }
    assert context_memory_conclusion(records) == "unavailable"


def test_closeout_ignores_smoke_and_empty_context(tmp_path: Path) -> None:
    root = tmp_path / "result"
    root.mkdir()
    (root / "one-token-smoke.json").write_text(
        json.dumps(
            {
                "exitClassification": "inference-failure",
                "processCleanup": "reaped",
                "runInvoked": False,
                "modelSessionCreated": False,
                "realModelExecuted": False,
                "coldMemory": _window(_SMOKE_PEAK),
            }
        ),
        encoding="utf-8",
    )
    document = build_closeout(root)
    assert document["memoryConclusion"] == "unavailable"
    assert load_closeout_template()["memoryConclusion"] == "unavailable"


def _phase(
    peak: int,
    *,
    cold: dict[str, Any] | None = None,
    warm: dict[str, Any] | None = None,
    process_cleanup: str = "reaped",
) -> dict[str, Any]:
    return {
        "exitClassification": "success",
        "networkResult": "denied",
        "processCleanup": process_cleanup,
        "coldMemory": _window(peak) if cold is None else cold,
        "warmMemory": _window(peak) if warm is None else warm,
    }


def _window(peak: int, *, current: int = 0, oom: int = 0) -> dict[str, Any]:
    return {
        "cgroupCurrentBytes": current,
        "cgroupPeakBytes": peak,
        "memoryEvents": {"high": 0, "low": 0, "max": 0, "oom": oom, "oomKill": oom},
        "oomEvents": oom,
        "telemetry": "complete",
    }
