"""Explicit cleanup of one synthetic cache attempt.

Cleanup never follows a link, never deletes a verified identity, and never runs
in the background. A second call is already clean. A mid-delete failure stays a
failure.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.artifact_cache import validate_cache_root
from patchpilot_intelligence_evals.verification_seal import (
    SealError,
    check_attempt_id,
    classify_filesystem_entry,
)

_STATES = frozenset({"quarantine", "rejected"})


class CleanupError(ValueError):
    """Cleanup failed closed. The message is a code."""

    def __init__(self, code: str, reclaimed_bytes: int = 0) -> None:
        super().__init__(code)
        self.code = code
        self.reclaimed_bytes = reclaimed_bytes


def cleanup_attempt(
    cache: Path,
    attempt_id: str,
    *,
    state: str,
    repository: Path | None = None,
    referenced_attempt_ids: frozenset[str] = frozenset(),
    unlink: Callable[[Path], None] | None = None,
) -> dict[str, Any]:
    """Delete one named attempt, or refuse it. Rejection records stay."""
    root = validate_cache_root(cache, repository=repository)
    try:
        check_attempt_id(attempt_id)
    except SealError as exc:
        raise CleanupError(exc.code) from exc
    if state == "verified":
        if attempt_id in referenced_attempt_ids:
            raise CleanupError("verified-referenced")
        raise CleanupError("verified-immutable")
    if state not in _STATES:
        raise CleanupError("cleanup-escape")
    parent = root / state
    target = parent / attempt_id
    if target.is_symlink():
        raise CleanupError("symlink-escape")
    if target.exists() and not _confined(parent, target):
        raise CleanupError("cleanup-escape")
    if not target.exists():
        return {"status": "already-clean", "reclaimedBytes": 0, "preservedRejectionRecord": False}
    if not target.is_dir():
        raise CleanupError("special-file")
    files = _files(target, keep_rejection=state == "rejected")
    if not files and state == "rejected":
        return {
            "status": "already-clean",
            "reclaimedBytes": 0,
            "preservedRejectionRecord": (target / "rejection.json").is_file(),
        }
    deleter = unlink or _unlink
    reclaimed = 0
    for path, logical in files:
        try:
            deleter(path)
        except OSError as exc:
            raise CleanupError("partial-cleanup", reclaimed) from exc
        reclaimed += logical
    _remove_empty_directories(target, keep_root=state == "rejected", reclaimed=reclaimed)
    return {
        "status": "clean",
        "reclaimedBytes": reclaimed,
        "preservedRejectionRecord": state == "rejected",
    }


def _files(target: Path, *, keep_rejection: bool) -> list[tuple[Path, int]]:
    found: list[tuple[Path, int]] = []
    for dirpath, dirnames, filenames in os.walk(target, followlinks=False):
        current = Path(dirpath)
        if current.is_symlink():
            raise CleanupError("symlink-escape")
        kept: list[str] = []
        for dirname in sorted(dirnames):
            path = current / dirname
            _refuse_entry(path)
            kept.append(dirname)
        dirnames[:] = kept
        for filename in sorted(filenames):
            path = current / filename
            _refuse_entry(path)
            if keep_rejection and path.name == "rejection.json" and path.parent == target:
                continue
            found.append((path, os.lstat(path).st_size))
    return sorted(found, key=lambda item: item[0].as_posix())


def _refuse_entry(path: Path) -> None:
    kind = classify_filesystem_entry(path)
    if kind in {"symlink", "dangling-symlink"}:
        raise CleanupError("symlink-escape")
    if kind is not None:
        raise CleanupError(kind)


def _remove_empty_directories(target: Path, *, keep_root: bool, reclaimed: int) -> None:
    directories: list[Path] = []
    for dirpath, dirnames, _filenames in os.walk(target, followlinks=False):
        for dirname in dirnames:
            directories.append(Path(dirpath) / dirname)
    for directory in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        if directory.is_symlink():
            raise CleanupError("symlink-escape", reclaimed)
        try:
            directory.rmdir()
        except OSError as exc:
            raise CleanupError("partial-cleanup", reclaimed) from exc
    if not keep_root:
        try:
            target.rmdir()
        except OSError as exc:
            raise CleanupError("partial-cleanup", reclaimed) from exc


def _confined(parent: Path, target: Path) -> bool:
    resolved_parent = parent.resolve()
    resolved = target.resolve()
    return resolved == resolved_parent or resolved_parent in resolved.parents


def _unlink(path: Path) -> None:
    path.unlink()
