"""Hardened launcher fail-closed behavior."""

from __future__ import annotations

import json
import shutil
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.cli import main
from patchpilot_intelligence_evals.hardened_execution import (
    HardenedExecutionError,
    build_argv,
    command_uses_shell,
    execute_hardened,
    host_supports_boundary,
)
from patchpilot_intelligence_evals.resource_controls import DEFAULT_LIMITS
from patchpilot_intelligence_evals.schemas import repo_root

_FIXTURE = repo_root() / "tests" / "sandbox_fixtures" / "resource_probe.py"


def test_non_linux_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "darwin")
    with pytest.raises(HardenedExecutionError) as caught:
        execute_hardened(_FIXTURE, ("ok",))
    assert caught.value.code == "unsupported-platform"


def test_missing_bubblewrap_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda _name: None)
    with pytest.raises(HardenedExecutionError) as caught:
        execute_hardened(_FIXTURE, ("ok",))
    assert caught.value.code == "unsupported-capability"


def test_launch_vector_has_no_shell() -> None:
    argv = build_argv(
        unit="patchpilot-h0123456789abcdef",
        mounts=(),
        limits=DEFAULT_LIMITS,
        arguments=("ok",),
    )
    assert command_uses_shell(argv) is False
    assert "--unshare-net" in argv
    assert "--clearenv" in argv
    assert "sh" not in {Path(item).name for item in argv}
    assert argv[0] == "systemd-run"
    joined = " ".join(argv)
    assert "/home/" not in joined
    assert "shell=False" not in joined


def test_cli_fixture_execution_opens_the_host_listener() -> None:
    if not host_supports_boundary():
        pytest.skip("unsupported-capability")
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(["hardened-fixture-execution"])
    assert code == 0
    summary = json.loads(buffer.getvalue())
    assert summary["status"] == "ok"
    assert summary["filesystemPassed"] is True
    assert summary["networkPassed"] is True
    assert summary["realModelExecuted"] is False
    assert summary["productionReady"] is False
