"""Bounded child-process runner for one candidate invocation.

The runner uses an argument array and never a shell. It enforces a wall-clock
timeout, stdout and stderr caps, a minimal environment, and a temporary
working directory that contains only the copied fixture files. Killing the
child process group is not a container, cgroup, mount namespace, user
namespace, or operating-system network policy.
"""

from __future__ import annotations

import hashlib
import os
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.candidate_child import NETWORK_EXIT, NETWORK_STDERR
from patchpilot_intelligence_evals.candidate_manifest import validate_manifest
from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text
from patchpilot_intelligence_evals.protocol import (
    MAX_STDERR_BYTES,
    MAX_STDOUT_BYTES,
    TIMEOUT_SECONDS,
    ProtocolError,
    classify_response,
    parse_candidate_stdout,
    validate_request,
)
from patchpilot_intelligence_evals.schemas import repo_root

CHILD_ENV_KEYS: frozenset[str] = frozenset(
    {
        "LANG",
        "LC_ALL",
        "PATH",
        "PYTHONDONTWRITEBYTECODE",
        "PYTHONIOENCODING",
        "PYTHONUTF8",
    }
)


@dataclass(frozen=True)
class Invocation:
    """One child invocation.

    ``captured_stdout`` and ``captured_stderr`` stay in process memory so tests
    can see classification inputs. Durable results must not persist them.
    """

    outcome: str
    exit_code: int | None
    stdout_bytes: int
    stderr_bytes: int
    output_digest: str
    attempts: int
    parsed: dict[str, Any] | None
    captured_stdout: bytes
    captured_stderr: bytes

    def public_record(self) -> dict[str, Any]:
        """Failure or success identity without process text or prompt text."""
        return {
            "attempts": self.attempts,
            "executionOutcome": self.outcome,
            "exitCode": self.exit_code,
            "outputDigest": self.output_digest,
            "stderrBytes": self.stderr_bytes,
            "stdoutBytes": self.stdout_bytes,
        }


def child_environment() -> dict[str, str]:
    """Return the only variables the child receives. Secrets are not copied."""
    path = os.environ.get("PATH")
    lang = os.environ.get("LANG") or "C.UTF-8"
    env = {
        "LANG": lang,
        "LC_ALL": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
    }
    if path:
        env["PATH"] = path
    return env


def _terminate(proc: subprocess.Popen[bytes]) -> bool:
    """Stop the child process group. Return False when the process survives."""
    if proc.poll() is not None:
        return True
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        try:
            proc.kill()
        except (ProcessLookupError, PermissionError):
            return proc.poll() is not None
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            proc.kill()
        except (ProcessLookupError, PermissionError):
            return False
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            return False
    return proc.poll() is not None


def _write_stdin(proc: subprocess.Popen[bytes], payload: bytes) -> None:
    stdin = proc.stdin
    if stdin is None:
        return
    try:
        stdin.write(payload)
        stdin.close()
    except (BrokenPipeError, OSError):
        try:
            stdin.close()
        except OSError:
            return


def _capture(proc: subprocess.Popen[bytes], timeout: float) -> tuple[str | None, bytes, bytes]:
    stdout_pipe = proc.stdout
    stderr_pipe = proc.stderr
    if stdout_pipe is None or stderr_pipe is None:
        _terminate(proc)
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
                    if len(stdout) + len(chunk) > MAX_STDOUT_BYTES:
                        limit = "output-limit-exceeded"
                        break
                    stdout.extend(chunk)
                elif len(stderr) + len(chunk) > MAX_STDERR_BYTES:
                    limit = "stderr-limit-exceeded"
                    break
                else:
                    stderr.extend(chunk)
            if limit is not None:
                break
    finally:
        selector.close()
    if limit is not None:
        if not _terminate(proc):
            return "internal-harness-failure", bytes(stdout), bytes(stderr)
        return limit, bytes(stdout), bytes(stderr)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if not _terminate(proc):
            return "internal-harness-failure", bytes(stdout), bytes(stderr)
        return "timeout", bytes(stdout), bytes(stderr)
    return None, bytes(stdout), bytes(stderr)


def _digest(stdout: bytes, parsed: dict[str, Any] | None, outcome: str) -> str:
    if outcome == "success" and parsed is not None:
        return sha256_text(canonical_dumps(parsed["findingExplanationOutput"]))
    return hashlib.sha256(stdout).hexdigest()


def _invocation(
    *,
    outcome: str,
    proc: subprocess.Popen[bytes] | None,
    stdout: bytes,
    stderr: bytes,
    parsed: dict[str, Any] | None,
) -> Invocation:
    exit_code = None if proc is None else proc.returncode
    return Invocation(
        outcome=outcome,
        exit_code=exit_code,
        stdout_bytes=len(stdout),
        stderr_bytes=len(stderr),
        output_digest=_digest(stdout, parsed, outcome),
        attempts=1,
        parsed=parsed if outcome == "success" else None,
        captured_stdout=stdout,
        captured_stderr=stderr,
    )


def _stage_runtime(manifest: dict[str, Any], base: Path) -> Path:
    """Copy listed fixture files into an empty temporary directory."""
    implementation = manifest["implementation"]
    paths = [str(item) for item in implementation["implementationPaths"]]
    entry_point = str(implementation["entryPoint"])
    if entry_point not in paths:
        raise ProtocolError("runtime-input")
    runtime = Path(tempfile.mkdtemp(prefix="patchpilot-candidate-runtime-"))
    try:
        for relative in paths:
            source = base.joinpath(*Path(relative).parts)
            if source.is_symlink() or not source.is_file():
                raise ProtocolError("runtime-input")
            target = runtime.joinpath(*Path(relative).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    except Exception:
        shutil.rmtree(runtime, ignore_errors=True)
        raise
    return runtime


def invoke_candidate(
    manifest: dict[str, Any],
    request: dict[str, Any],
    *,
    timeout_seconds: float = TIMEOUT_SECONDS,
    root: Path | None = None,
) -> Invocation:
    """Run one child. There is no retry. The request mapping is not modified."""
    if not 0 < timeout_seconds <= TIMEOUT_SECONDS:
        raise ProtocolError("timeout-range")
    base = root if root is not None else repo_root()
    before = canonical_dumps(request)
    validate_manifest(manifest, root=base)
    validate_request(request)
    entry_point = str(manifest["implementation"]["entryPoint"])
    argv = [
        sys.executable,
        "-m",
        "patchpilot_intelligence_evals.candidate_child",
        entry_point,
    ]
    request_bytes = canonical_dumps(request).encode("utf-8")
    runtime = _stage_runtime(manifest, base)
    try:
        try:
            proc = subprocess.Popen(
                argv,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=runtime,
                env=child_environment(),
                shell=False,
                start_new_session=True,
                close_fds=True,
                bufsize=0,
            )
        except OSError:
            if canonical_dumps(request) != before:
                raise ProtocolError("request-mutated") from None
            return _invocation(
                outcome="internal-harness-failure",
                proc=None,
                stdout=b"",
                stderr=b"",
                parsed=None,
            )
        writer = threading.Thread(target=_write_stdin, args=(proc, request_bytes), daemon=True)
        writer.start()
        limit, stdout, stderr = _capture(proc, timeout_seconds)
        writer.join(timeout=1)
        if canonical_dumps(request) != before:
            _terminate(proc)
            raise ProtocolError("request-mutated")
        if limit is not None:
            return _invocation(outcome=limit, proc=proc, stdout=stdout, stderr=stderr, parsed=None)
        if (
            proc.returncode == NETWORK_EXIT
            and stderr.decode("utf-8", errors="replace") == NETWORK_STDERR
        ):
            return _invocation(
                outcome="network-policy-failure",
                proc=proc,
                stdout=stdout,
                stderr=stderr,
                parsed=None,
            )
        if proc.returncode not in (0, None):
            return _invocation(
                outcome="nonzero-exit",
                proc=proc,
                stdout=stdout,
                stderr=stderr,
                parsed=None,
            )
        parse_outcome, parsed = parse_candidate_stdout(stdout)
        if parse_outcome != "parsed" or parsed is None:
            return _invocation(
                outcome=parse_outcome,
                proc=proc,
                stdout=stdout,
                stderr=stderr,
                parsed=None,
            )
        outcome = classify_response(
            parsed,
            request_id_value=str(request["requestId"]),
            candidate_id=str(manifest["candidateId"]),
            candidate_version=str(manifest["candidateVersion"]),
        )
        return _invocation(
            outcome=outcome,
            proc=proc,
            stdout=stdout,
            stderr=stderr,
            parsed=parsed,
        )
    finally:
        shutil.rmtree(runtime, ignore_errors=True)
