"""Host cgroup observations for one hardened scope.

``memory.peak`` and ``memory.current`` are resident measurements.
``RLIMIT_AS`` is address space and is not read here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_budget import MEMORY_CAP
from patchpilot_intelligence_evals.measurement_plan import ADDRESS_SPACE_BYTES, empty_memory

_CGROUP_ROOT = Path("/sys/fs/cgroup")


def parse_status(text: str) -> tuple[int | None, int | None]:
    """Return VmRSS and VmSize in bytes from one ``/proc`` status file."""
    rss: int | None = None
    virtual: int | None = None
    for line in text.splitlines():
        if line.startswith("VmRSS:"):
            rss = int(line.split()[1]) * 1024
        elif line.startswith("VmSize:"):
            virtual = int(line.split()[1]) * 1024
    return rss, virtual


def parse_events(text: str) -> int | None:
    """Return ``oom_kill`` from a cgroup ``memory.events`` file."""
    found: int | None = None
    for line in text.splitlines():
        name, separator, value = line.partition(" ")
        if separator and name == "oom_kill" and value.isdecimal():
            found = int(value)
    return found


def classify_memory(peak: int | None, oom_events: int | None) -> str:
    """Classify resident telemetry. Virtual size is not an input."""
    if peak is None or oom_events is None:
        return "unresolved"
    if oom_events > 0:
        return "oom"
    if peak > MEMORY_CAP:
        return "exceeded"
    return "complete"


def cgroup_directory(pid: int, proc_root: Path | None = None) -> Path | None:
    """Resolve a cgroup v2 directory for a live process."""
    root = proc_root if proc_root is not None else Path("/proc")
    path = root / str(pid) / "cgroup"
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("0::"):
            continue
        relative = line.split(":", 2)[2].lstrip("/")
        if not relative:
            return None
        return _CGROUP_ROOT / relative
    return None


def _read_int(path: Path) -> int | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text.isdecimal():
        return None
    return int(text)


def read_cgroup_dir(
    directory: Path | None, *, rss: int | None, tree: int | None, virtual: int | None
) -> dict[str, Any]:
    """Read resident counters from one cgroup directory."""
    memory = empty_memory()
    if directory is None:
        memory["telemetry"] = "unresolved"
        return memory
    current = _read_int(directory / "memory.current")
    peak = _read_int(directory / "memory.peak")
    events_path = directory / "memory.events"
    oom = parse_events(events_path.read_text(encoding="utf-8")) if events_path.is_file() else None
    memory["cgroupCurrentBytes"] = current
    memory["cgroupPeakBytes"] = peak
    memory["oomEvents"] = oom
    memory["processRssBytes"] = rss
    memory["processTreeRssBytes"] = tree
    memory["virtualAddressBytes"] = virtual
    memory["telemetry"] = classify_memory(peak, oom)
    memory["residentCeilingBytes"] = MEMORY_CAP
    memory["addressSpaceLimitBytes"] = ADDRESS_SPACE_BYTES
    return memory


def phase_marker(results: Path) -> str:
    """Read the child phase marker. A missing file is unmarked."""
    path = results / "phase.txt"
    if not path.is_file():
        return "unmarked"
    text = path.read_text(encoding="utf-8").strip()
    return text or "unmarked"


def _process_memory(directory: Path | None, pid: int) -> tuple[int | None, int | None, int | None]:
    if directory is None:
        return None, None, None
    procs = directory / "cgroup.procs"
    pids: list[int] = []
    if procs.is_file():
        for line in procs.read_text(encoding="utf-8").splitlines():
            if line.isdecimal():
                pids.append(int(line))
    if pid > 0 and pid not in pids:
        pids.append(pid)
    rss_values: list[int] = []
    virtual_values: list[int] = []
    main_rss: int | None = None
    for item in pids:
        status = Path(f"/proc/{item}/status")
        if not status.is_file():
            continue
        rss, virtual = parse_status(status.read_text(encoding="utf-8"))
        if rss is not None:
            rss_values.append(rss)
            if item == pid:
                main_rss = rss
        if virtual is not None:
            virtual_values.append(virtual)
    tree = sum(rss_values) if rss_values else None
    virtual_sum = sum(virtual_values) if virtual_values else None
    if main_rss is None and rss_values:
        main_rss = max(rss_values)
    return main_rss, tree, virtual_sum


class ScopeSampler:
    """Sample one systemd user scope while its process is alive."""

    def __init__(self) -> None:
        self.samples: list[dict[str, Any]] = []
        self.directory: Path | None = None

    def __call__(self, pid: int, unit: str, results: Path) -> None:
        expected = f"{unit}.scope" if unit else ""
        if pid > 0:
            located = cgroup_directory(pid)
            if located is not None and (not expected or located.name == expected):
                self.directory = located
        if expected and (self.directory is None or self.directory.name != expected):
            return
        rss, tree, virtual = _process_memory(self.directory, pid)
        sample = read_cgroup_dir(self.directory, rss=rss, tree=tree, virtual=virtual)
        sample["phase"] = phase_marker(results)
        self.samples.append(sample)

    def leftover_pids(self) -> int | None:
        """Return remaining cgroup tasks after the scope should be gone."""
        if self.directory is None:
            return None
        procs = self.directory / "cgroup.procs"
        if not procs.exists():
            return 0
        lines = [line for line in procs.read_text(encoding="utf-8").splitlines() if line]
        return len(lines)


def window(samples: list[dict[str, Any]], phases: frozenset[str]) -> dict[str, Any]:
    """Reduce samples for one cold or warm window."""
    chosen = [item for item in samples if str(item.get("phase")) in phases]
    memory = empty_memory()
    if not chosen:
        memory["telemetry"] = "unresolved" if samples else "not-observed"
        return memory
    peaks = [
        int(item["cgroupPeakBytes"])
        for item in chosen
        if isinstance(item.get("cgroupPeakBytes"), int)
    ]
    last = chosen[-1]
    oom_values: list[int] = []
    for item in chosen:
        oom_value = item.get("oomEvents")
        if isinstance(oom_value, int):
            oom_values.append(oom_value)
    oom = max(oom_values) if oom_values else None
    if not peaks or oom is None:
        memory["telemetry"] = "unresolved"
        memory["cgroupCurrentBytes"] = last.get("cgroupCurrentBytes")
        memory["processRssBytes"] = last.get("processRssBytes")
        memory["processTreeRssBytes"] = last.get("processTreeRssBytes")
        memory["virtualAddressBytes"] = last.get("virtualAddressBytes")
        return memory
    peak = max(peaks)
    memory.update(
        {
            "cgroupCurrentBytes": last.get("cgroupCurrentBytes"),
            "cgroupPeakBytes": peak,
            "oomEvents": oom,
            "processRssBytes": last.get("processRssBytes"),
            "processTreeRssBytes": last.get("processTreeRssBytes"),
            "telemetry": classify_memory(peak, oom),
            "virtualAddressBytes": last.get("virtualAddressBytes"),
        }
    )
    return memory
