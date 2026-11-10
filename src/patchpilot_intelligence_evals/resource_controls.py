"""Resource limits for the hardened boundary.

``RLIMIT_AS`` is virtual address space. Resident memory is ``MemoryMax`` on a
systemd user scope. ``RLIMIT_NPROC`` is per-user and is not the process-count
control. ``TasksMax`` is that control.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceLimits:
    """Limits applied to one hardened launch. Zero retries are implicit."""

    memory_max_bytes: int
    tasks_max: int
    cpu_seconds: int
    address_space_bytes: int
    file_size_bytes: int
    open_files: int
    wall_clock_seconds: float
    stdout_bytes: int
    stderr_bytes: int


DEFAULT_LIMITS = ResourceLimits(
    memory_max_bytes=268435456,
    tasks_max=32,
    cpu_seconds=5,
    address_space_bytes=2147483648,
    file_size_bytes=1048576,
    open_files=128,
    wall_clock_seconds=15,
    stdout_bytes=65536,
    stderr_bytes=16384,
)


def probe_limits(kind: str) -> ResourceLimits:
    """Return limits that exceed one control and leave the others at defaults."""
    if kind == "memory":
        return _replace(memory_max_bytes=67108864)
    if kind == "tasks":
        return _replace(tasks_max=8, wall_clock_seconds=8)
    if kind == "cpu":
        return _replace(cpu_seconds=1, wall_clock_seconds=8)
    if kind == "address-space":
        return _replace(memory_max_bytes=1073741824, address_space_bytes=268435456)
    if kind == "file-size":
        return _replace(file_size_bytes=0)
    if kind == "open-files":
        return _replace(open_files=32)
    if kind == "wall":
        return _replace(wall_clock_seconds=1)
    if kind == "stdout":
        return _replace(stdout_bytes=1024, wall_clock_seconds=8)
    if kind == "stderr":
        return _replace(stderr_bytes=1024, wall_clock_seconds=8)
    if kind == "tree":
        return _replace(wall_clock_seconds=8)
    raise ValueError(kind)


def systemd_properties(limits: ResourceLimits) -> list[str]:
    """Return systemd-run property arguments. Values are decimal byte counts."""
    return [
        "-p",
        f"MemoryMax={limits.memory_max_bytes}",
        "-p",
        "MemorySwapMax=0",
        "-p",
        f"TasksMax={limits.tasks_max}",
    ]


def prlimit_arguments(limits: ResourceLimits) -> list[str]:
    """Return prlimit arguments. ``--as`` is address space, not resident memory."""
    return [
        "/usr/bin/prlimit",
        f"--cpu={limits.cpu_seconds}",
        f"--as={limits.address_space_bytes}",
        f"--fsize={limits.file_size_bytes}",
        f"--nofile={limits.open_files}",
        "--",
    ]


def _replace(**changes: int | float) -> ResourceLimits:
    return ResourceLimits(
        memory_max_bytes=int(changes.get("memory_max_bytes", DEFAULT_LIMITS.memory_max_bytes)),
        tasks_max=int(changes.get("tasks_max", DEFAULT_LIMITS.tasks_max)),
        cpu_seconds=int(changes.get("cpu_seconds", DEFAULT_LIMITS.cpu_seconds)),
        address_space_bytes=int(
            changes.get("address_space_bytes", DEFAULT_LIMITS.address_space_bytes)
        ),
        file_size_bytes=int(changes.get("file_size_bytes", DEFAULT_LIMITS.file_size_bytes)),
        open_files=int(changes.get("open_files", DEFAULT_LIMITS.open_files)),
        wall_clock_seconds=float(
            changes.get("wall_clock_seconds", DEFAULT_LIMITS.wall_clock_seconds)
        ),
        stdout_bytes=int(changes.get("stdout_bytes", DEFAULT_LIMITS.stdout_bytes)),
        stderr_bytes=int(changes.get("stderr_bytes", DEFAULT_LIMITS.stderr_bytes)),
    )
