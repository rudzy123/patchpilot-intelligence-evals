"""Resource limits and process-tree cleanup."""

from __future__ import annotations

import os
import subprocess
import threading
import time

import pytest

from patchpilot_intelligence_evals.hardened_execution import (
    ExecutionResult,
    execute_hardened,
    host_supports_boundary,
)
from patchpilot_intelligence_evals.resource_controls import DEFAULT_LIMITS, probe_limits
from patchpilot_intelligence_evals.schemas import repo_root

_FIXTURE = repo_root() / "tests" / "sandbox_fixtures" / "resource_probe.py"


def _require_boundary() -> None:
    if not host_supports_boundary():
        pytest.skip("unsupported-capability")


def test_default_limits_name_address_space_separately_from_memory() -> None:
    assert DEFAULT_LIMITS.memory_max_bytes == 268435456
    assert DEFAULT_LIMITS.address_space_bytes == 2147483648
    assert DEFAULT_LIMITS.tasks_max == 32
    assert probe_limits("memory").memory_max_bytes < DEFAULT_LIMITS.memory_max_bytes
    assert probe_limits("address-space").address_space_bytes < DEFAULT_LIMITS.address_space_bytes


@pytest.mark.parametrize(
    ("mode", "kind", "classification", "stdout"),
    [
        ("file-size", "file-size", "success", b"FILESIZE\n"),
        ("open-files", "open-files", "success", b"NOFILE\n"),
        ("tasks", "tasks", "success", b"TASKS\n"),
        ("memory", "memory", "signal-killed", b""),
        ("stdout", "stdout", "output-limit-exceeded", b""),
        ("stderr", "stderr", "stderr-limit-exceeded", b""),
        ("wall", "wall", "timeout", b""),
    ],
)
def test_one_limit_has_a_stable_classification(
    mode: str,
    kind: str,
    classification: str,
    stdout: bytes,
) -> None:
    _require_boundary()
    result = execute_hardened(_FIXTURE, (mode,), limits=probe_limits(kind))
    assert result.exit_classification == classification
    assert result.stdout == stdout
    assert result.attempts == 1
    assert result.cleanup == "reaped"


def test_cpu_limit_kills_before_the_wall_clock() -> None:
    _require_boundary()
    started = time.monotonic()
    result = execute_hardened(_FIXTURE, ("cpu",), limits=probe_limits("cpu"))
    elapsed = time.monotonic() - started
    assert result.exit_classification == "signal-killed"
    assert elapsed < probe_limits("cpu").wall_clock_seconds
    assert result.attempts == 1


def test_process_tree_is_reaped() -> None:
    _require_boundary()
    token = "patchpilot-tree-" + os.urandom(4).hex()
    holder: dict[str, ExecutionResult] = {}

    def run() -> None:
        holder["result"] = execute_hardened(_FIXTURE, ("tree", token), limits=probe_limits("tree"))

    thread = threading.Thread(target=run)
    thread.start()
    seen = False
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline and thread.is_alive():
        if token in _process_args():
            seen = True
            break
        time.sleep(0.05)
    thread.join()
    result = holder["result"]
    assert seen is True
    assert token not in _process_args()
    assert result.cleanup == "reaped"
    assert result.attempts == 1


def _process_args() -> str:
    completed = subprocess.run(
        ["ps", "-eo", "args"],
        check=False,
        shell=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout
