"""Shared dynamic-dependency closure for the verified ONNX Runtime library.

Track 8A offline load, Track 8B-R1 inference, and Track 8B-R2 inference use
this module. It does not create a model session and it does not call Run.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from secrets import token_hex

from patchpilot_intelligence_evals.filesystem_policy import Mount
from patchpilot_intelligence_evals.schemas import repo_root

LIBRARY_NAME = "libonnxruntime.so.1.31.1"
PROVIDER_LIBRARY = "libonnxruntime_providers_shared.so"
INTERPRETER_NAME = "ld-linux-x86-64.so.2"
APPROVED_BASENAMES = frozenset(
    {
        "libc.so.6",
        "libdl.so.2",
        "libgcc_s.so.1",
        "libm.so.6",
        "libpthread.so.0",
        "librt.so.1",
        "libstdc++.so.6",
    }
)
APPROVED_ROOTS = ("/lib/", "/lib64/", "/usr/lib/", "/usr/lib64/")


class ClosureError(ValueError):
    """A dependency closure failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class ResolvedDependency:
    """One resolved library. ``source`` stays out of committed records."""

    basename: str
    classification: str
    identity: str
    source: Path
    destination: str


def dependency_identity(classification: str, basename: str) -> str:
    """Stable identity from the classification and basename. No host path."""
    payload = f"{classification}:{basename}".encode()
    return hashlib.sha256(payload).hexdigest()


def public_dependency(item: ResolvedDependency) -> dict[str, str]:
    """Return the committable description. It has no host path."""
    return {
        "basename": item.basename,
        "classification": item.classification,
        "identity": item.identity,
    }


def closure_digest() -> str:
    """Digest the public closure. The digest covers no host path and no file bytes."""
    from patchpilot_intelligence_evals.corpus import canonical_dumps, sha256_text

    return sha256_text(canonical_dumps(approved_public_closure()))


def approved_public_closure() -> list[dict[str, str]]:
    """The accepted standard closure. Interpreter mounts stay in the policy."""
    rows = [
        {
            "basename": name,
            "classification": "standard-host-runtime",
            "identity": dependency_identity("standard-host-runtime", name),
        }
        for name in sorted(APPROVED_BASENAMES)
    ]
    rows.append(
        {
            "basename": INTERPRETER_NAME,
            "classification": "elf-interpreter",
            "identity": dependency_identity("elf-interpreter", INTERPRETER_NAME),
        }
    )
    return rows


def read_ldd(binary: Path) -> str:
    """Read the local dynamic closure. This does not fetch anything."""
    completed = subprocess.run(
        ["ldd", str(binary)],
        check=False,
        shell=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0 or "not found" in completed.stdout:
        raise ClosureError("unresolved-dependency")
    return completed.stdout


def parse_ldd(text: str) -> list[tuple[str, str | None]]:
    """Return basename and loader path. A missing path is unresolved."""
    found: list[tuple[str, str | None]] = []
    for line in text.splitlines():
        if "linux-vdso.so" in line:
            continue
        if "=>" in line:
            name, _separator, rest = line.strip().partition(" => ")
            token = rest.split()[0] if rest.split() else ""
            source = None if token in {"", "not"} else token
            found.append((Path(name).name, source))
            continue
        parts = line.strip().split()
        if parts and parts[0].startswith("/"):
            found.append((Path(parts[0]).name, parts[0]))
    return found


def inspect_dependency(
    name: str,
    source: str | None,
    *,
    roots: tuple[str, ...] = APPROVED_ROOTS,
) -> ResolvedDependency:
    """Classify one dependency and reject anything outside the approved closure."""
    if name == PROVIDER_LIBRARY or "providers" in name:
        raise ClosureError("unapproved-provider")
    if source is None:
        raise ClosureError("unresolved-dependency")
    path = Path(source)
    if not path.is_absolute():
        raise ClosureError("unapproved-root")
    _reject_location(path)
    if path.is_symlink() and not _under_roots(path.resolve(), roots):
        raise ClosureError("symlink-escape")
    resolved = path.resolve()
    if not _under_roots(resolved, roots) or not _under_roots(path, roots):
        raise ClosureError("unapproved-root")
    if path.is_dir() or resolved.is_dir():
        raise ClosureError("broad-directory")
    if not resolved.is_file():
        raise ClosureError("unresolved-dependency")
    if resolved.stat().st_mode & 0o022:
        raise ClosureError("writable-dependency")
    if name == INTERPRETER_NAME:
        classification = "elf-interpreter"
    elif name in APPROVED_BASENAMES:
        classification = "standard-host-runtime"
    else:
        raise ClosureError("closure-mismatch")
    return ResolvedDependency(
        basename=name,
        classification=classification,
        identity=dependency_identity(classification, name),
        source=resolved,
        destination=path.as_posix(),
    )


def resolve_runtime_dependencies(
    binary: Path,
    *,
    ldd_text: str | None = None,
    roots: tuple[str, ...] = APPROVED_ROOTS,
) -> tuple[ResolvedDependency, ...]:
    """Resolve the approved closure. A mismatch fails before a session exists."""
    if binary.name == PROVIDER_LIBRARY or "providers" in binary.name:
        raise ClosureError("unapproved-provider")
    if binary.name != LIBRARY_NAME:
        raise ClosureError("closure-mismatch")
    text = read_ldd(binary) if ldd_text is None else ldd_text
    resolved = tuple(
        inspect_dependency(name, source, roots=roots) for name, source in parse_ldd(text)
    )
    names = {item.basename for item in resolved if item.classification == "standard-host-runtime"}
    interpreters = [item for item in resolved if item.classification == "elf-interpreter"]
    if names != APPROVED_BASENAMES or len(interpreters) != 1:
        raise ClosureError("closure-mismatch")
    if interpreters[0].basename != INTERPRETER_NAME:
        raise ClosureError("closure-mismatch")
    return resolved


def approved_runtime_mounts(
    binary: Path,
    *,
    ldd_text: str | None = None,
    roots: tuple[str, ...] = APPROVED_ROOTS,
) -> tuple[Mount, ...]:
    """Mount each standard dependency read-only. The interpreter stays in policy."""
    resolved = resolve_runtime_dependencies(binary, ldd_text=ldd_text, roots=roots)
    stage = Path("/tmp") / f"patchpilot-deps-{os.getpid()}-{token_hex(4)}"
    stage.mkdir()
    mounts: list[Mount] = []
    for index, item in enumerate(resolved):
        if item.classification != "standard-host-runtime":
            continue
        copy = stage / f"{index}-{item.basename}"
        shutil.copy2(item.source, copy)
        destination = Path(item.destination)
        if copy.is_dir() or destination.is_dir() or destination.name != item.basename:
            raise ClosureError("broad-directory")
        mounts.append(Mount(str(copy), item.destination, True))
    if any(not mount.read_only or Path(mount.source).is_dir() for mount in mounts):
        raise ClosureError("broad-directory")
    if len(mounts) != len(APPROVED_BASENAMES):
        raise ClosureError("closure-mismatch")
    return tuple(mounts)


def _reject_location(path: Path) -> None:
    text = path.as_posix()
    parts = set(path.parts)
    if text.startswith("/home") or "/home/" in text or text.startswith("/Users"):
        raise ClosureError("home-dependency")
    try:
        path.resolve().relative_to(repo_root().resolve())
    except ValueError:
        pass
    else:
        raise ClosureError("repository-dependency")
    if ".venv" in parts or "site-packages" in parts:
        raise ClosureError("project-environment")
    if any("quarantine" in part for part in parts):
        raise ClosureError("quarantine-dependency")
    if any("transport" in part for part in parts):
        raise ClosureError("transport-attempt")


def _under_roots(path: Path, roots: tuple[str, ...]) -> bool:
    text = path.as_posix()
    for root in roots:
        prefix = root if root.endswith("/") else f"{root}/"
        if text == prefix.rstrip("/") or text.startswith(prefix):
            return True
    return False
