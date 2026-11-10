"""Mount policy for the hardened boundary.

The interpreter and its libraries are copied under ``/tmp`` before they are
bound, so the sandbox mount table does not contain the operator home path.
"""

from __future__ import annotations

import atexit
import os
import shutil
import subprocess
from pathlib import Path
from typing import NamedTuple

_STAGE: Path | None = None


class FilesystemPolicyError(ValueError):
    """A mount request failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class Mount(NamedTuple):
    """One bubblewrap bind. ``source`` is a host path outside the home directory."""

    source: str
    destination: str
    read_only: bool


def bwrap_mount_arguments(mounts: tuple[Mount, ...] | list[Mount]) -> list[str]:
    """Return bubblewrap arguments for the approved mounts."""
    assert_mounts_safe(mounts)
    arguments: list[str] = []
    for mount in mounts:
        flag = "--ro-bind" if mount.read_only else "--bind"
        arguments.extend([flag, mount.source, mount.destination])
    arguments.extend(["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp"])
    return arguments


def assert_mounts_safe(mounts: tuple[Mount, ...] | list[Mount]) -> None:
    """Reject mounts that expose home, credentials, or the repository."""
    for mount in mounts:
        source = str(Path(mount.source).resolve())
        destination = mount.destination
        if _identity_path(source) or _identity_path(destination):
            raise FilesystemPolicyError("identity-path")
        if destination == "/home" or destination.startswith("/home/"):
            raise FilesystemPolicyError("home-destination")
        if destination == "/etc" or destination.startswith("/etc/"):
            raise FilesystemPolicyError("etc-destination")
        if Path(destination).name in {"patchpilot", "neural-from-scratch"}:
            raise FilesystemPolicyError("sibling-destination")


def runtime_mounts(executable: Path) -> tuple[Mount, ...]:
    """Return read-only binds for a staged interpreter and ``prlimit``."""
    stage = _interpreter_stage(executable.resolve())
    python = stage / "runtime" / "bin" / "python3"
    if not python.exists():
        raise FilesystemPolicyError("interpreter-missing")
    mounts = [Mount(str(stage / "runtime"), "/opt/runtime", True)]
    prlimit = shutil.which("prlimit")
    if prlimit is None:
        raise FilesystemPolicyError("prlimit-missing")
    mounts.extend(_library_mounts(Path(prlimit), stage, "prlimit"))
    prlimit_copy = stage / "prlimit" / "prlimit"
    mounts.append(Mount(str(prlimit_copy), "/usr/bin/prlimit", True))
    binary = Path(os.path.realpath(python))
    mounts.extend(_library_mounts(binary, stage, "python"))
    unique = _dedupe(tuple(mounts))
    assert_mounts_safe(unique)
    return unique


def sandbox_python() -> str:
    """Return the interpreter path inside the sandbox."""
    return "/opt/runtime/bin/python3"


def _interpreter_stage(executable: Path) -> Path:
    global _STAGE
    if _STAGE is not None and (_STAGE / "runtime" / "bin" / "python3").exists():
        return _STAGE
    prefix_text = subprocess.check_output(
        [str(executable), "-c", "import sys; print(sys.base_prefix)"],
        text=True,
        shell=False,
    ).strip()
    prefix = Path(prefix_text)
    stage = Path(os.path.join("/tmp", f"patchpilot-runtime-{os.getpid()}"))
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir()
    runtime = stage / "runtime"
    shutil.copytree(prefix, runtime, symlinks=True, ignore=_ignore_bytecode)
    _scrub(runtime, prefix)
    _STAGE = stage
    atexit.register(_cleanup)
    return stage


def _library_mounts(binary: Path, stage: Path, label: str) -> list[Mount]:
    mounts: list[Mount] = []
    directory = stage / label
    directory.mkdir(exist_ok=True)
    for index, library in enumerate(_ldd(binary)):
        if _identity_path(str(library)):
            raise FilesystemPolicyError("library-identity-path")
        copy = directory / f"{index}-{library.name}"
        shutil.copy2(library, copy)
        mounts.append(Mount(str(copy), str(library), True))
    if label == "prlimit":
        copy = directory / "prlimit"
        shutil.copy2(binary, copy)
    return mounts


def _ldd(binary: Path) -> list[Path]:
    completed = subprocess.run(
        ["ldd", str(binary)],
        check=False,
        shell=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise FilesystemPolicyError("ldd-failed")
    libraries: list[Path] = []
    for line in completed.stdout.splitlines():
        source = _ldd_path(line)
        if source is not None:
            libraries.append(source)
    return libraries


def _ldd_path(line: str) -> Path | None:
    if "=>" in line:
        part = line.split("=>", 1)[1].strip().split()
        if part and part[0].startswith("/"):
            return Path(part[0])
        return None
    stripped = line.strip().split()
    if stripped and stripped[0].startswith("/"):
        return Path(stripped[0])
    return None


def _scrub(runtime: Path, prefix: Path) -> None:
    needle = str(prefix).encode()
    home = str(Path.home()).encode()
    for path in runtime.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        data = path.read_bytes()
        if needle not in data and home not in data:
            continue
        if path.suffix != ".py":
            raise FilesystemPolicyError("runtime-identity-path")
        updated = data.replace(needle, b"/opt/runtime")
        if home in updated:
            raise FilesystemPolicyError("runtime-identity-path")
        path.write_bytes(updated)


def _ignore_bytecode(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name == "__pycache__" or name.endswith(".pyc")}


def _dedupe(mounts: tuple[Mount, ...]) -> tuple[Mount, ...]:
    seen: set[str] = set()
    chosen: list[Mount] = []
    for mount in mounts:
        if mount.destination in seen:
            continue
        seen.add(mount.destination)
        chosen.append(mount)
    return tuple(chosen)


def _identity_path(path: str) -> bool:
    return (
        "/home/" in path
        or path.startswith("/home")
        or "/Users/" in path
        or path.startswith("/Users")
    )


def _cleanup() -> None:
    if _STAGE is not None and _STAGE.exists():
        shutil.rmtree(_STAGE, ignore_errors=True)
