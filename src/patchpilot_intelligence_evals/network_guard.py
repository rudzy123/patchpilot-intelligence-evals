"""In-process network and path boundaries.

The socket hooks are not an operating-system sandbox, seccomp profile,
network namespace, or firewall. Code that opens a socket before the hook,
calls the private _socket module, or starts another process is outside
this control.
"""

from __future__ import annotations

import socket
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from urllib import request as urllib_request

ALLOWED_ENV_VARS: frozenset[str] = frozenset(
    {
        "FORCE_COLOR",
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "NO_COLOR",
        "PATH",
        "PYTEST_ADDOPTS",
        "PYTEST_CURRENT_TEST",
        "PYTHONDONTWRITEBYTECODE",
        "PYTHONNOUSERSITE",
        "PYTHONPATH",
        "TEMP",
        "TMP",
        "TMPDIR",
        "TZ",
        "UV_CACHE_DIR",
        "UV_NO_CACHE",
        "UV_PROJECT_ENVIRONMENT",
        "VIRTUAL_ENV",
    }
)


class NetworkProhibited(RuntimeError):
    """An evaluation path tried to use a patched network entry point."""


class BoundaryError(ValueError):
    """A path escaped the repository or an environment read was not allowed."""


class _GuardState:
    def __init__(self) -> None:
        self.depth = 0
        self.socket_cls: Any = None
        self.create_connection: Any = None
        self.getaddrinfo: Any = None
        self.urlopen: Any = None


_STATE = _GuardState()


def _blocked(*_args: object, **_kwargs: object) -> Any:
    raise NetworkProhibited("offline evaluation blocked network access")


def _assign(module: Any, name: str, value: Any) -> None:
    setattr(module, name, value)


@contextmanager
def network_guard() -> Iterator[None]:
    """Fail closed on socket, DNS, and urllib entry points while entered."""
    if _STATE.depth == 0:
        _STATE.socket_cls = socket.socket
        _STATE.create_connection = socket.create_connection
        _STATE.getaddrinfo = socket.getaddrinfo
        _STATE.urlopen = urllib_request.urlopen
        _assign(socket, "socket", _blocked)
        _assign(socket, "create_connection", _blocked)
        _assign(socket, "getaddrinfo", _blocked)
        _assign(urllib_request, "urlopen", _blocked)
    _STATE.depth += 1
    try:
        yield
    finally:
        _STATE.depth -= 1
        if _STATE.depth == 0:
            _assign(socket, "socket", _STATE.socket_cls)
            _assign(socket, "create_connection", _STATE.create_connection)
            _assign(socket, "getaddrinfo", _STATE.getaddrinfo)
            _assign(urllib_request, "urlopen", _STATE.urlopen)


def read_allowed_env(name: str) -> str | None:
    """Read one tooling variable. This does not hide the process environment."""
    import os

    if name not in ALLOWED_ENV_VARS:
        raise BoundaryError("environment variable is not in the tooling allowlist")
    return os.environ.get(name)


def assert_inside_repository(relative_path: str, repo_root: Path) -> None:
    """Reject paths that leave the repo root without resolving sibling paths."""
    if relative_path.startswith("/") or relative_path.startswith("\\"):
        raise BoundaryError("absolute paths are outside the repository boundary")
    parts: list[str] = []
    for part in Path(relative_path).parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if not parts:
                raise BoundaryError("path escapes the repository root")
            parts.pop()
            continue
        parts.append(part)
    candidate = repo_root.joinpath(*parts)
    try:
        candidate.relative_to(repo_root)
    except ValueError as exc:
        raise BoundaryError("path escapes the repository root") from exc
