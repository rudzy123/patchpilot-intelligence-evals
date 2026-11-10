"""Launch a synthetic fixture inside the hardened Linux boundary.

The launcher never falls back to an unscoped subprocess. It does not execute a
model and it does not retry.
"""

from __future__ import annotations

import json
import os
import selectors
import shutil
import signal
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from secrets import token_hex
from typing import Any, cast

from patchpilot_intelligence_evals.filesystem_policy import (
    FilesystemPolicyError,
    Mount,
    bwrap_mount_arguments,
    runtime_mounts,
    sandbox_python,
)
from patchpilot_intelligence_evals.network_policy import ALLOWED_ENVIRONMENT, namespace_arguments
from patchpilot_intelligence_evals.resource_controls import (
    DEFAULT_LIMITS,
    ResourceLimits,
    prlimit_arguments,
    systemd_properties,
)
from patchpilot_intelligence_evals.schemas import repo_root


class HardenedExecutionError(ValueError):
    """The hardened launch failed closed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class ExecutionResult:
    """One launch. Standard streams stay in memory and are not logged."""

    exit_classification: str
    return_code: int | None
    stdout: bytes
    stderr: bytes
    cleanup: str
    attempts: int
    report: bytes
    argv: tuple[str, ...]


def build_argv(
    *,
    unit: str,
    mounts: tuple[Mount, ...] | list[Mount],
    limits: ResourceLimits,
    arguments: tuple[str, ...],
) -> list[str]:
    """Return the systemd, bubblewrap, and prlimit argument vector."""
    argv = [
        "systemd-run",
        "--user",
        "--scope",
        "--collect",
        "--quiet",
        f"--unit={unit}",
        *systemd_properties(limits),
        "--",
        "bwrap",
        *namespace_arguments(),
        *bwrap_mount_arguments(mounts),
        "--",
        *prlimit_arguments(limits),
        sandbox_python(),
        "/fixture/main.py",
        *arguments,
    ]
    if command_uses_shell(argv):
        raise HardenedExecutionError("shell")
    return argv


def command_uses_shell(argv: list[str] | tuple[str, ...]) -> bool:
    """Return whether an argument vector invokes a shell."""
    shells = {"sh", "bash", "dash", "zsh", "fish"}
    return any(Path(item).name in shells or item == "-c" for item in argv)


def execute_hardened(
    fixture: Path,
    arguments: tuple[str, ...] = (),
    *,
    limits: ResourceLimits | None = None,
    artifact_dir: Path | None = None,
    config_dir: Path | None = None,
    executable: Path | None = None,
) -> ExecutionResult:
    """Run one fixture inside the boundary. ``attempts`` is always 1."""
    if not sys.platform.startswith("linux"):
        raise HardenedExecutionError("unsupported-platform")
    if shutil.which("bwrap") is None or shutil.which("systemd-run") is None:
        raise HardenedExecutionError("unsupported-capability")
    if shutil.which("systemctl") is None or shutil.which("prlimit") is None:
        raise HardenedExecutionError("unsupported-capability")
    chosen = limits if limits is not None else DEFAULT_LIMITS
    interpreter = executable if executable is not None else Path(sys.executable)
    try:
        mounts, work = _stage(fixture, artifact_dir, config_dir, interpreter)
    except FilesystemPolicyError as exc:
        raise HardenedExecutionError(exc.code) from None
    unit = f"patchpilot-h{token_hex(8)}"
    argv = build_argv(unit=unit, mounts=mounts, limits=chosen, arguments=arguments)
    proc = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        shell=False,
        start_new_session=True,
        close_fds=True,
    )
    limit, stdout, stderr = _capture(proc, chosen.wall_clock_seconds, chosen)
    cleanup = _reap(unit, proc)
    report = _read_report(work)
    shutil.rmtree(work, ignore_errors=True)
    return ExecutionResult(
        exit_classification=_classify(limit, proc.returncode),
        return_code=proc.returncode,
        stdout=stdout,
        stderr=stderr,
        cleanup=cleanup,
        attempts=1,
        report=report,
        argv=tuple(argv),
    )


def _stage(
    fixture: Path,
    artifact_dir: Path | None,
    config_dir: Path | None,
    executable: Path,
) -> tuple[tuple[Mount, ...], Path]:
    work = Path("/tmp") / f"patchpilot-run-{os.getpid()}-{token_hex(4)}"
    work.mkdir()
    fixture_dir = work / "fixture"
    fixture_dir.mkdir()
    shutil.copyfile(fixture, fixture_dir / "main.py")
    _copy_optional(artifact_dir, work / "artifacts")
    _copy_optional(config_dir, work / "config")
    (work / "results").mkdir()
    mounts = (
        *runtime_mounts(executable),
        Mount(str(work / "fixture"), "/fixture", True),
        Mount(str(work / "artifacts"), "/artifacts", True),
        Mount(str(work / "config"), "/config", True),
        Mount(str(work / "results"), "/results", False),
    )
    return mounts, work


def _copy_optional(source: Path | None, destination: Path) -> None:
    if source is None:
        destination.mkdir()
        return
    shutil.copytree(source, destination, symlinks=True)


def _read_report(work: Path) -> bytes:
    path = work / "results" / "report.json"
    if not path.is_file():
        return b""
    return path.read_bytes()


def _capture(
    proc: subprocess.Popen[bytes],
    timeout: float,
    limits: ResourceLimits,
) -> tuple[str | None, bytes, bytes]:
    stdout_pipe = proc.stdout
    stderr_pipe = proc.stderr
    if stdout_pipe is None or stderr_pipe is None:
        _reap_process(proc)
        return "internal-harness-failure", b"", b""
    selector = selectors.DefaultSelector()
    selector.register(stdout_pipe, selectors.EVENT_READ, "stdout")
    selector.register(stderr_pipe, selectors.EVENT_READ, "stderr")
    stdout = bytearray()
    stderr = bytearray()
    deadline = time.monotonic() + timeout
    limit: str | None = None
    try:
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                limit = "timeout"
                break
            events = selector.select(timeout=remaining)
            events.sort(key=lambda item: 0 if item[0].data == "stdout" else 1)
            for key, _mask in events:
                try:
                    chunk = os.read(key.fd, 8192)
                except OSError:
                    selector.unregister(key.fileobj)
                    continue
                if chunk == b"":
                    selector.unregister(key.fileobj)
                    continue
                if key.data == "stdout":
                    if len(stdout) + len(chunk) > limits.stdout_bytes:
                        limit = "output-limit-exceeded"
                        break
                    stdout.extend(chunk)
                elif len(stderr) + len(chunk) > limits.stderr_bytes:
                    limit = "stderr-limit-exceeded"
                    break
                else:
                    stderr.extend(chunk)
            if limit is not None:
                break
    finally:
        selector.close()
    if limit is not None:
        if not _reap_process(proc):
            return "internal-harness-failure", bytes(stdout), bytes(stderr)
        return limit, bytes(stdout), bytes(stderr)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if not _reap_process(proc):
            return "internal-harness-failure", bytes(stdout), bytes(stderr)
        return "timeout", bytes(stdout), bytes(stderr)
    return None, bytes(stdout), bytes(stderr)


def _reap(unit: str, proc: subprocess.Popen[bytes]) -> str:
    _kill_scope(unit)
    reaped = _reap_process(proc)
    if reaped and _scope_inactive(unit):
        return "reaped"
    return "failed"


def _reap_process(proc: subprocess.Popen[bytes]) -> bool:
    if proc.poll() is not None:
        return True
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        proc.kill()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        return False
    return proc.poll() is not None


def _kill_scope(unit: str) -> None:
    subprocess.run(
        [
            "systemctl",
            "--user",
            "kill",
            f"{unit}.scope",
            "--kill-whom=all",
            "--signal=SIGKILL",
        ],
        check=False,
        shell=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _scope_inactive(unit: str) -> bool:
    completed = subprocess.run(
        ["systemctl", "--user", "is-active", f"{unit}.scope"],
        check=False,
        shell=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip() in {"inactive", "failed", "unknown", ""}


def visibility_summary(executable: Path | None = None) -> dict[str, object]:
    """Run the synthetic visibility fixture and return statuses, not file contents."""
    if not host_supports_boundary():
        raise HardenedExecutionError("unsupported-capability")
    root = Path("/tmp") / f"patchpilot-visibility-{os.getpid()}-{token_hex(4)}"
    root.mkdir()
    try:
        artifact = root / "artifact"
        artifact.mkdir()
        (artifact / "marker").write_text("artifact-marker\n", encoding="utf-8")
        hidden = root / "hidden" / "gold"
        hidden.mkdir(parents=True)
        (hidden / "marker").write_text("hidden-marker\n", encoding="utf-8")
        (artifact / "escape").symlink_to(hidden / "marker")
        config = root / "config"
        config.mkdir()
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        sock_dir = Path("/tmp") / f"patchpilot-visibility-sock-{token_hex(4)}"
        sock_dir.mkdir()
        sock_path = sock_dir / "h.sock"
        unix_listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            unix_listener.bind(str(sock_path))
            unix_listener.listen(1)
            request = json.dumps({"port": listener.getsockname()[1], "unixSocket": str(sock_path)})
            (config / "request.json").write_text(request, encoding="utf-8")
            fixture = _fixture("fs_visibility.py")
            result = execute_hardened(
                fixture,
                artifact_dir=artifact,
                config_dir=config,
                executable=executable,
            )
        finally:
            listener.close()
            unix_listener.close()
            shutil.rmtree(sock_dir, ignore_errors=True)
        report = _load_report(result)
        filesystem_passed = _filesystem_passed(report)
        network_passed = _network_passed(report)
        passed = (
            filesystem_passed
            and network_passed
            and result.cleanup == "reaped"
            and result.exit_classification == "success"
        )
        return {
            "status": "ok" if passed else "fail",
            "exitClassification": result.exit_classification,
            "filesystemPassed": filesystem_passed,
            "networkPassed": network_passed,
            "cleanup": result.cleanup,
            "singleUidMap": report.get("singleUidMap") is True,
            "sandboxLocalLoopback": report.get("network", {}).get("localLoopback"),
            "realModelExecuted": False,
            "productionReady": False,
        }
    finally:
        shutil.rmtree(root, ignore_errors=True)


def host_supports_boundary() -> bool:
    """Return whether this host proved bubblewrap and a systemd user scope."""
    if not sys.platform.startswith("linux"):
        return False
    if shutil.which("bwrap") is None or shutil.which("systemd-run") is None:
        return False
    from patchpilot_intelligence_evals.sandbox_capabilities import probe_capabilities

    report = probe_capabilities()
    found = {str(item["probeId"]): str(item["disposition"]) for item in report["probes"]}
    return found.get("bubblewrap") == "enforced" and found.get("systemd-user-scope") == "enforced"


def _fixture(name: str) -> Path:
    return repo_root() / "tests" / "sandbox_fixtures" / name


def _load_report(result: ExecutionResult) -> dict[str, Any]:
    payload = result.report or result.stdout
    try:
        loaded = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise HardenedExecutionError("report") from exc
    if not isinstance(loaded, dict):
        raise HardenedExecutionError("report")
    return cast(dict[str, Any], loaded)


def _filesystem_passed(report: dict[str, Any]) -> bool:
    hidden = (
        "gold",
        "prior",
        "siblingPatchpilot",
        "siblingNeural",
        "home",
        "root",
        "ssh",
        "aws",
        "azure",
        "gcloud",
        "kube",
        "gitCredentials",
        "npm",
        "corpus",
        "etc",
        "homeInMounts",
        "symlinkEscaped",
    )
    visible = ("artifact", "config", "artifactWriteBlocked", "configWriteBlocked", "resultCreated")
    if any(report.get(name) is not False for name in hidden):
        return False
    if any(report.get(name) is not True for name in visible):
        return False
    env = report.get("env")
    return isinstance(env, list) and set(env) <= ALLOWED_ENVIRONMENT


def _network_passed(report: dict[str, Any]) -> bool:
    network = report.get("network")
    if not isinstance(network, dict):
        return False
    denied = ("ipv4", "ipv6", "dns", "loopback", "unix")
    if any(network.get(name) in {None, "reached"} for name in denied):
        return False
    return network.get("localLoopback") == "ConnectionRefusedError"


def _classify(limit: str | None, return_code: int | None) -> str:
    if limit in {"timeout", "output-limit-exceeded", "stderr-limit-exceeded"}:
        return str(limit)
    if limit == "internal-harness-failure":
        return "internal-harness-failure"
    if return_code == 0:
        return "success"
    if return_code is None:
        return "internal-harness-failure"
    if return_code < 0 or return_code >= 128:
        return "signal-killed"
    return "nonzero"
