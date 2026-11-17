"""Host cgroup samples. Virtual size is not the resident ceiling."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.candidate_inference import classify_execution
from patchpilot_intelligence_evals.cgroup_memory import (
    ScopeSampler,
    classify_memory,
    contradictory_resident,
    parse_events,
    parse_memory_events,
    parse_status,
    read_cgroup_dir,
    resolve_scope_observation,
    retry_window,
    sample_complete,
    window,
)
from patchpilot_intelligence_evals.hardened_execution import ExecutionResult
from patchpilot_intelligence_evals.measurement_plan import ADDRESS_SPACE_BYTES
from patchpilot_intelligence_evals.measurement_retry_closeout import context_memory_conclusion


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


def test_events_enxio_is_reported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from patchpilot_intelligence_evals.cgroup_memory import CgroupReadError

    (tmp_path / "memory.events").write_text("oom 0\n", encoding="utf-8")

    def unavailable(self: Path, *args: object, **kwargs: object) -> str:
        raise OSError(19, "No such device")

    monkeypatch.setattr(Path, "read_text", unavailable)
    with pytest.raises(CgroupReadError) as exc:
        read_cgroup_dir(tmp_path, rss=1, tree=2, virtual=3)
    assert exc.value.errno == 19


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


def _complete(current: int = 4, peak: int = 8) -> dict[str, Any]:
    return {
        "cgroupCurrentBytes": current,
        "cgroupPeakBytes": peak,
        "oomEvents": 0,
        "processRssBytes": 1,
        "processTreeRssBytes": 2,
        "telemetry": "complete",
        "virtualAddressBytes": 9,
    }


def test_scope_present_through_final_sample() -> None:
    sample = _complete()
    decision = resolve_scope_observation(
        child_state="exited", read_error=None, sample=sample, last_complete=None
    )
    assert decision["disposition"] == "present"
    assert decision["append"] == sample
    assert decision["classification"] is None


def test_scope_disappears_immediately_after_child_exit() -> None:
    decision = resolve_scope_observation(
        child_state="exited",
        read_error="disappeared",
        sample=None,
        last_complete=_complete(),
    )
    assert decision["disposition"] == "post-exit-scope-removed"
    assert decision["append"] is None
    assert decision["classification"] is None
    assert decision["retain"]["cgroupPeakBytes"] == 8


def test_events_enxio_after_complete_sample_is_post_exit() -> None:
    decision = resolve_scope_observation(
        child_state="exited", read_error="enxio", sample=None, last_complete=_complete()
    )
    assert decision["disposition"] == "post-exit-scope-removed"
    assert decision["classification"] is None


def test_current_disappearance_after_child_exit_keeps_peak() -> None:
    sample = _complete()
    sample["cgroupCurrentBytes"] = None
    sample["telemetry"] = "unresolved"
    decision = resolve_scope_observation(
        child_state="exited", read_error=None, sample=sample, last_complete=_complete()
    )
    assert decision["disposition"] == "post-exit-scope-removed"
    assert decision["append"] is None


def test_scope_disappearance_before_any_complete_sample_is_unresolved() -> None:
    decision = resolve_scope_observation(
        child_state="exited", read_error="enxio", sample=None, last_complete=None
    )
    assert decision["disposition"] == "unresolved"
    assert decision["classification"] == "telemetry-unresolved"
    assert decision["append"]["telemetry"] == "unresolved"


def test_scope_disappearance_while_child_is_active_is_infrastructure() -> None:
    decision = resolve_scope_observation(
        child_state="active", read_error="enxio", sample=None, last_complete=_complete()
    )
    assert decision["disposition"] == "disappeared-while-active"
    assert decision["classification"] == "infrastructure-failure"
    assert decision["append"] is None


def test_active_contradiction_stays_unresolved_after_a_later_read(tmp_path: Path) -> None:
    sampler = ScopeSampler()
    sampler.child_state = "active"
    sampler._observe(read_error=None, sample=_complete(current=4, peak=8), results=tmp_path)
    sampler._observe(read_error=None, sample=_complete(current=9, peak=8), results=tmp_path)
    assert sampler.blocked_classification == "telemetry-unresolved"
    sampler.child_state = "exited"
    sampler._observe(read_error="enxio", sample=None, results=tmp_path)
    assert sampler.blocked_classification == "telemetry-unresolved"
    reduced = window(sampler.samples, frozenset({"cold", "unmarked"}))
    assert reduced["telemetry"] == "unresolved"
    assert reduced["cgroupCurrentBytes"] == 9
    assert reduced["cgroupPeakBytes"] == 8
    result = ExecutionResult("success", 0, b"{}", b"", "reaped", 1, b"", ())
    assert classify_execution(result, sampler, cold_warm=False)["exitClassification"] == (
        "telemetry-unresolved"
    )


def test_contradictory_final_telemetry_is_unresolved() -> None:
    sample = _complete(current=9, peak=8)
    decision = resolve_scope_observation(
        child_state="exited", read_error=None, sample=sample, last_complete=_complete()
    )
    assert decision["classification"] == "telemetry-unresolved"
    assert decision["append"] == sample


def test_post_exit_removal_does_not_weaken_a_complete_peak() -> None:
    retained = _complete(current=4, peak=8)
    retained["memoryEvents"] = {"high": 0, "low": 0, "max": 0, "oom": 0, "oomKill": 0}
    retained["phase"] = "cold"
    decision = resolve_scope_observation(
        child_state="exited", read_error="enxio", sample=None, last_complete=retained
    )
    assert decision["append"] is None
    reduced = retry_window([retained], frozenset({"cold"}))
    assert reduced["telemetry"] == "complete"
    assert reduced["cgroupPeakBytes"] == 8
    missing = {"exitClassification": "success", "coldMemory": {"telemetry": "unresolved"}}
    assert context_memory_conclusion({"context-4096": missing, "context-8192": missing}) != (
        "within-ceiling"
    )


def test_sampler_retains_the_last_complete_sample(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scope = tmp_path / "patchpilot-habc.scope"
    scope.mkdir()
    (scope / "memory.current").write_text("4\n", encoding="utf-8")
    (scope / "memory.peak").write_text("8\n", encoding="utf-8")
    (scope / "memory.events").write_text("oom 0\noom_kill 0\n", encoding="utf-8")
    (scope / "cgroup.procs").write_text("", encoding="utf-8")
    monkeypatch.setattr(
        "patchpilot_intelligence_evals.cgroup_memory.cgroup_directory",
        lambda _pid: scope,
    )
    sampler = ScopeSampler()
    results = tmp_path / "results"
    results.mkdir()
    sampler(10, "patchpilot-habc", results)

    def boom(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise OSError(19, "No such device")

    monkeypatch.setattr(
        "patchpilot_intelligence_evals.cgroup_memory.read_cgroup_dir",
        boom,
    )
    sampler(0, "patchpilot-habc", results)
    assert sampler.disposition == "post-exit-scope-removed"
    assert sampler.blocked_classification is None
    assert len(sampler.samples) == 1
    assert sampler.last_complete is not None
    assert sampler.last_complete["cgroupPeakBytes"] == 8
    assert sampler.post_exit_reads == [{"effect": "diagnostic", "readError": "enxio"}]


def test_complete_window_keeps_a_successful_final_read() -> None:
    sealed = _complete(current=3_129_344, peak=5_709_541_376)
    sealed["phase"] = "cold"
    final = _complete(current=3_129_344, peak=5_709_541_376)
    final["phase"] = "cold"
    decision = resolve_scope_observation(
        child_state="exited", read_error=None, sample=final, last_complete=sealed
    )
    assert decision["classification"] is None
    assert decision["retain"]["cgroupPeakBytes"] == 5_709_541_376
    assert decision["retain"]["oomEvents"] == 0
    reduced = window([sealed, final], frozenset({"cold", "unmarked"}))
    assert reduced["telemetry"] == "complete"


def test_complete_window_records_enoent_without_downgrade() -> None:
    decision = resolve_scope_observation(
        child_state="exited", read_error="enoent", sample=None, last_complete=_complete()
    )
    assert decision["classification"] is None
    assert decision["disposition"] == "post-exit-scope-removed"
    assert decision["postExitRead"] == {"effect": "diagnostic", "readError": "enoent"}
    assert decision["retain"]["cgroupPeakBytes"] == 8


def test_complete_window_records_scope_removal_without_downgrade() -> None:
    decision = resolve_scope_observation(
        child_state="exited", read_error="disappeared", sample=None, last_complete=_complete()
    )
    assert decision["classification"] is None
    assert decision["retain"]["cgroupCurrentBytes"] == 4
    assert decision["retain"]["oomEvents"] == 0


def test_incomplete_post_exit_read_does_not_replace_a_sealed_window() -> None:
    sample = _complete()
    sample["cgroupPeakBytes"] = None
    sample["telemetry"] = "unresolved"
    sample["processRssBytes"] = None
    decision = resolve_scope_observation(
        child_state="exited", read_error=None, sample=sample, last_complete=_complete()
    )
    assert decision["classification"] is None
    assert decision["append"] is None
    assert decision["disposition"] == "post-exit-diagnostic"
    assert decision["retain"]["telemetry"] == "complete"


def test_rss_unavailable_does_not_make_cgroup_telemetry_incomplete() -> None:
    sample = _complete()
    sample["phase"] = "cold"
    sample["processRssBytes"] = None
    sample["processTreeRssBytes"] = None
    sample["virtualAddressBytes"] = None
    assert sample_complete(sample) is True
    reduced = window([sample], frozenset({"cold"}))
    assert reduced["telemetry"] == "complete"
    assert reduced["cgroupPeakBytes"] == 8
    assert reduced["processRssBytes"] is None
