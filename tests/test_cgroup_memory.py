"""Host cgroup samples. Virtual size is not the resident ceiling."""

from __future__ import annotations

from pathlib import Path

import pytest

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.cgroup_memory import (
    ScopeSampler,
    classify_memory,
    contradictory_resident,
    parse_events,
    parse_memory_events,
    parse_status,
    read_cgroup_dir,
    retry_window,
    window,
)
from patchpilot_intelligence_evals.measurement_plan import ADDRESS_SPACE_BYTES


def test_status_and_events_parse_bytes() -> None:
    rss, virtual = parse_status("VmRSS:\t4 kB\nVmSize:\t8 kB\n")
    assert rss == 4096
    assert virtual == 8192
    assert parse_events("low 0\noom_kill 2\n") == 2


def test_missing_peak_is_unresolved(tmp_path: Path) -> None:
    (tmp_path / "memory.current").write_text("10\n", encoding="utf-8")
    (tmp_path / "memory.events").write_text("oom_kill 0\n", encoding="utf-8")
    memory = read_cgroup_dir(tmp_path, rss=1, tree=2, virtual=3)
    assert memory["telemetry"] == "unresolved"
    assert memory["cgroupPeakBytes"] is None
    assert memory["residentCeilingBytes"] == MEMORY_CAP
    assert memory["addressSpaceLimitBytes"] == ADDRESS_SPACE_BYTES


def test_peak_above_ceiling_is_exceeded(tmp_path: Path) -> None:
    (tmp_path / "memory.current").write_text("10\n", encoding="utf-8")
    (tmp_path / "memory.peak").write_text(f"{MEMORY_CAP + 1}\n", encoding="utf-8")
    (tmp_path / "memory.events").write_text("oom_kill 0\n", encoding="utf-8")
    memory = read_cgroup_dir(tmp_path, rss=1, tree=2, virtual=MEMORY_CAP * 4)
    assert memory["telemetry"] == "exceeded"
    assert memory["virtualAddressBytes"] == MEMORY_CAP * 4
    assert classify_memory(MEMORY_CAP, 0) == "complete"
    assert classify_memory(20, 1) == "oom"


def test_window_uses_resident_peak_only() -> None:
    samples = [
        {
            "phase": "cold",
            "cgroupCurrentBytes": 4,
            "cgroupPeakBytes": 8,
            "oomEvents": 0,
            "processRssBytes": 1,
            "processTreeRssBytes": 2,
            "virtualAddressBytes": 99,
        }
    ]
    memory = window(samples, frozenset({"cold"}))
    assert memory["telemetry"] == "complete"
    assert memory["cgroupPeakBytes"] == 8
    assert memory["virtualAddressBytes"] == 99
    assert window([], frozenset({"cold"}))["telemetry"] == "not-observed"


def test_sampler_records_only_the_named_scope(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    parent = tmp_path / "app-cursor.scope"
    scope = tmp_path / "patchpilot-habc.scope"
    for directory in (parent, scope):
        directory.mkdir()
        (directory / "memory.current").write_text("1\n", encoding="utf-8")
        (directory / "memory.peak").write_text("2\n", encoding="utf-8")
        (directory / "memory.events").write_text("oom_kill 0\n", encoding="utf-8")
        (directory / "cgroup.procs").write_text("", encoding="utf-8")
    located = iter((parent, scope))

    def fake_directory(_pid: int) -> Path:
        return next(located)

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.cgroup_memory.cgroup_directory",
        fake_directory,
    )
    sampler = ScopeSampler()
    results = tmp_path / "results"
    results.mkdir()
    sampler(10, "patchpilot-habc", results)
    sampler(10, "patchpilot-habc", results)
    assert sampler.directory == scope
    assert len(sampler.samples) == 1
    assert sampler.samples[0]["cgroupPeakBytes"] == 2


def test_memory_events_stay_separate_from_virtual_size() -> None:
    events = parse_memory_events("low 1\nhigh 2\nmax 3\noom 0\noom_kill 0\n")
    assert events == {"high": 2, "low": 1, "max": 3, "oom": 0, "oomKill": 0}
    sample = {
        "phase": "cold",
        "cgroupCurrentBytes": 4,
        "cgroupPeakBytes": 8,
        "oomEvents": 0,
        "processRssBytes": 1,
        "processTreeRssBytes": 2,
        "virtualAddressBytes": 99,
        "memoryEvents": events,
    }
    memory = retry_window([sample], frozenset({"cold"}))
    assert memory["telemetry"] == "complete"
    assert memory["cgroupPeakBytes"] == 8
    assert memory["processRssBytes"] == 1
    assert memory["virtualAddressBytes"] == 99
    assert memory["memoryEvents"]["oomKill"] == 0
    assert memory["addressSpaceLimitBytes"] != memory["residentCeilingBytes"]


def test_current_above_peak_is_contradictory() -> None:
    memory = {
        "cgroupCurrentBytes": 9,
        "cgroupPeakBytes": 8,
        "oomEvents": 0,
        "telemetry": "complete",
        "memoryEvents": {"high": 0, "low": 0, "max": 0, "oom": 0, "oomKill": 0},
    }
    assert contradictory_resident(memory) is True
    reduced = retry_window(
        [
            {
                "phase": "warm",
                "cgroupCurrentBytes": 9,
                "cgroupPeakBytes": 8,
                "oomEvents": 0,
                "processRssBytes": 1,
                "processTreeRssBytes": 1,
                "virtualAddressBytes": 3,
                "memoryEvents": memory["memoryEvents"],
            }
        ],
        frozenset({"warm"}),
    )
    assert reduced["telemetry"] == "unresolved"
