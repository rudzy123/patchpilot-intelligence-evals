"""OS network denial and minimal environment."""

from __future__ import annotations

import json
import shutil
import socket
import subprocess
import tempfile
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.hardened_execution import (
    execute_hardened,
    host_supports_boundary,
)
from patchpilot_intelligence_evals.network_policy import (
    ALLOWED_ENVIRONMENT,
    DENIED_ENVIRONMENT_NAMES,
    environment_is_minimal,
)
from patchpilot_intelligence_evals.schemas import repo_root

_FIXTURE = repo_root() / "tests" / "sandbox_fixtures" / "net_probe.py"


def _require_boundary() -> None:
    if not host_supports_boundary():
        pytest.skip("unsupported-capability")


def test_environment_allowlist_rejects_credentials() -> None:
    assert environment_is_minimal(["PATH", "LANG", "PWD"])
    assert environment_is_minimal(sorted(ALLOWED_ENVIRONMENT)) is True
    assert environment_is_minimal(["PATH", "HOME"]) is False
    assert "AWS_SECRET_ACCESS_KEY" in DENIED_ENVIRONMENT_NAMES
    assert "SSH_AUTH_SOCK" in DENIED_ENVIRONMENT_NAMES


def test_hardened_network_and_environment_are_denied(monkeypatch: pytest.MonkeyPatch) -> None:
    _require_boundary()
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "synthetic-secret")
    monkeypatch.setenv("SSH_AUTH_SOCK", "/tmp/patchpilot-agent.sock")
    monkeypatch.setenv("HTTP_PROXY", "http://example.invalid:9")
    monkeypatch.setenv("HOME", "/tmp/patchpilot-not-home")
    root = Path(tempfile.mkdtemp(prefix="patchpilot-net-", dir="/tmp"))
    config = root / "config"
    config.mkdir()
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    sock_dir = Path(tempfile.mkdtemp(prefix="patchpilot-sock-", dir="/tmp"))
    sock_path = sock_dir / "h.sock"
    unix_listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    unix_listener.bind(str(sock_path))
    unix_listener.listen(1)
    try:
        (config / "request.json").write_text(
            json.dumps({"port": listener.getsockname()[1], "unixSocket": str(sock_path)}),
            encoding="utf-8",
        )
        result = execute_hardened(_FIXTURE, config_dir=config)
    finally:
        listener.close()
        unix_listener.close()
        sock_path.unlink(missing_ok=True)
        sock_dir.rmdir()
        shutil.rmtree(root, ignore_errors=True)
    assert result.exit_classification == "success"
    assert b"synthetic-secret" not in result.stdout
    report = json.loads(result.stdout)
    assert set(report["env"]) <= ALLOWED_ENVIRONMENT
    for name in DENIED_ENVIRONMENT_NAMES:
        assert name not in report["env"]
    assert report["ipv4"] != "reached"
    assert report["ipv6"] != "reached"
    assert report["dns"] != "reached"
    assert report["loopback"] != "reached"
    assert report["unix"] != "reached"
    assert report["localLoopback"] == "ConnectionRefusedError"


def test_host_loopback_is_reachable_without_a_network_namespace() -> None:
    _require_boundary()
    if shutil.which("bwrap") is None or not Path("/usr/bin/python3").is_file():
        pytest.skip("unsupported-capability")
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    argv = [
        "bwrap",
        "--unshare-user",
        "--die-with-parent",
        "--clearenv",
        "--setenv",
        "PATH",
        "/usr/bin",
        "--ro-bind",
        "/usr",
        "/usr",
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--tmpfs",
        "/tmp",
    ]
    for directory in ("/lib", "/lib64"):
        if Path(directory).is_dir():
            argv.extend(["--ro-bind", directory, directory])
    argv.extend(
        [
            "--",
            "/usr/bin/python3",
            "-c",
            "import socket,sys; s=socket.socket(); s.settimeout(0.5); "
            "s.connect(('127.0.0.1', int(sys.argv[1]))); print('REACHED')",
            str(port),
        ]
    )
    try:
        completed = subprocess.run(
            argv,
            check=False,
            shell=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    finally:
        listener.close()
    assert completed.returncode == 0
    assert completed.stdout.strip() == "REACHED"
