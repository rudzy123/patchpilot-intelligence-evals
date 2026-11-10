"""In-process file boundary for a candidate child.

The child working directory is a temporary runtime that contains only the
copied fixture files. This hook rejects lexical paths for the corpus, prior
result artifacts, and sibling repository names before the real open runs.
It is not a mount namespace, seccomp profile, or operating-system sandbox.
A private system call or a nested executable is outside this control.
"""

from __future__ import annotations

import builtins
import errno
import io
import os
import pathlib
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.schemas import repo_root

_SIBLING_PARTS = frozenset({"patchpilot", "neural-from-scratch"})
_RESULT_NAMES = frozenset(
    {
        "calibration-record.json",
        "candidate-execution-result.json",
        "experiment-manifest.json",
    }
)


class _BoundaryState:
    def __init__(self) -> None:
        self.runtime: Path | None = None
        self.open: Callable[..., Any] | None = None
        self.io_open: Callable[..., Any] | None = None
        self.os_open: Callable[..., Any] | None = None
        self.listdir: Callable[..., Any] | None = None
        self.scandir: Callable[..., Any] | None = None
        self.path_methods: dict[str, Any] = {}


_STATE = _BoundaryState()


def _normalized(path: str | os.PathLike[str], runtime: Path) -> Path:
    text = os.fspath(path)
    if not os.path.isabs(text):
        text = os.path.join(str(runtime), text)
    return Path(os.path.normpath(text))


def _within(path: Path, root: Path) -> bool:
    return path == root or root in path.parents


def _allowed_roots() -> tuple[Path, ...]:
    import patchpilot_intelligence_evals

    package = Path(os.path.normpath(patchpilot_intelligence_evals.__file__)).parent
    stdlib = Path(os.path.normpath(os.__file__)).parent
    prefixes = [package, stdlib]
    for prefix in (sys.prefix, sys.base_prefix, sys.exec_prefix):
        prefixes.append(Path(os.path.normpath(prefix)))
    return tuple(prefixes)


def classify_candidate_path(path: str | os.PathLike[str], *, runtime: Path) -> str:
    """Return ``allow`` or ``deny`` without opening the path."""
    normalized = _normalized(path, runtime)
    if any(part in _SIBLING_PARTS for part in normalized.parts):
        return "deny"
    runtime_root = Path(os.path.normpath(str(runtime)))
    if _within(normalized, runtime_root):
        return "allow"
    repo = Path(os.path.normpath(str(repo_root())))
    for name in ("corpus", "build"):
        if _within(normalized, repo / name):
            return "deny"
    artifact = normalized.name
    if artifact in _RESULT_NAMES or (
        artifact.startswith("comparison-") and artifact.endswith(".json")
    ):
        return "deny"
    for root in _allowed_roots():
        if _within(normalized, root):
            return "allow"
    return "deny"


def _assign(module: Any, name: str, value: Any) -> None:
    setattr(module, name, value)


def _reject(path: str | os.PathLike[str]) -> None:
    runtime = _STATE.runtime
    if runtime is None:
        raise PermissionError(errno.EACCES, "candidate-boundary")
    if classify_candidate_path(path, runtime=runtime) == "deny":
        raise PermissionError(errno.EACCES, "candidate-boundary")


def _open(file: Any, *args: Any, **kwargs: Any) -> Any:
    if not isinstance(file, int):
        _reject(file)
    original = _STATE.open
    if original is None:
        raise PermissionError(errno.EACCES, "candidate-boundary")
    return original(file, *args, **kwargs)


def _io_open(file: Any, *args: Any, **kwargs: Any) -> Any:
    if not isinstance(file, int):
        _reject(file)
    original = _STATE.io_open
    if original is None:
        raise PermissionError(errno.EACCES, "candidate-boundary")
    return original(file, *args, **kwargs)


def _os_open(
    path: str | os.PathLike[str],
    flags: int,
    mode: int = 0o777,
    *,
    dir_fd: int | None = None,
) -> int:
    if dir_fd is not None:
        raise PermissionError(errno.EACCES, "candidate-boundary")
    _reject(path)
    original = _STATE.os_open
    if original is None:
        raise PermissionError(errno.EACCES, "candidate-boundary")
    return int(original(path, flags, mode))


def _listdir(path: str | os.PathLike[str] | None = None) -> list[str]:
    if path is not None:
        _reject(path)
    original = _STATE.listdir
    if original is None:
        raise PermissionError(errno.EACCES, "candidate-boundary")
    return list(original(path))


def _scandir(path: str | os.PathLike[str] | None = None) -> Any:
    if path is not None:
        _reject(path)
    original = _STATE.scandir
    if original is None:
        raise PermissionError(errno.EACCES, "candidate-boundary")
    return original(path)


def install_candidate_boundary(runtime: Path) -> None:
    """Install the file hook for one child. The runtime directory stays readable."""
    if _STATE.runtime is not None:
        return
    _STATE.runtime = runtime
    _STATE.open = builtins.open
    _STATE.io_open = io.open
    _STATE.os_open = os.open
    _STATE.listdir = os.listdir
    _STATE.scandir = os.scandir
    builtins.open = _open
    io.open = _io_open
    _assign(os, "open", _os_open)
    _assign(os, "listdir", _listdir)
    _assign(os, "scandir", _scandir)
    for name in ("glob", "rglob", "iterdir"):
        original = getattr(pathlib.Path, name)
        _STATE.path_methods[name] = original

        def wrapped(self: pathlib.Path, *args: Any, original: Any = original, **kwargs: Any) -> Any:
            _reject(self)
            return original(self, *args, **kwargs)

        setattr(pathlib.Path, name, wrapped)


def restore_candidate_boundary() -> None:
    """Restore the process openers. The child exits after the script returns."""
    if _STATE.open is not None:
        builtins.open = _STATE.open
    if _STATE.io_open is not None:
        io.open = _STATE.io_open
    if _STATE.os_open is not None:
        _assign(os, "open", _STATE.os_open)
    if _STATE.listdir is not None:
        _assign(os, "listdir", _STATE.listdir)
    if _STATE.scandir is not None:
        _assign(os, "scandir", _STATE.scandir)
    for name, original in _STATE.path_methods.items():
        setattr(pathlib.Path, name, original)
    _STATE.path_methods = {}
    _STATE.runtime = None
