"""Path, link, special-file, and cleanup confinement."""

from __future__ import annotations

import os
import socket
import stat
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.atomic_promotion import prepare_attempt
from patchpilot_intelligence_evals.cache_cleanup import CleanupError, cleanup_attempt
from patchpilot_intelligence_evals.verification_seal import SealError, classify_mode, seal_directory


def _cache(tmp_path: Path) -> Path:
    root = tmp_path / "cache"
    root.mkdir()
    return root


def test_rejected_file_types(tmp_path: Path) -> None:
    directory = tmp_path / "types"
    directory.mkdir()
    (directory / "note.txt").write_bytes(b"abc")
    expected = [{"relativeName": "note.txt", "logicalBytes": 3, "sha256": None}]
    os.mkfifo(directory / "pipe")
    with pytest.raises(SealError) as caught:
        seal_directory(directory, expected, attempt_id="attempt-1")
    assert caught.value.code == "fifo"
    (directory / "pipe").unlink()
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(os.fspath(directory / "channel.sock"))
    sock.close()
    with pytest.raises(SealError) as caught:
        seal_directory(directory, expected, attempt_id="attempt-1")
    assert caught.value.code == "socket"
    (directory / "channel.sock").unlink()
    target = directory / "note.txt"
    os.link(target, directory / "other.txt")
    with pytest.raises(SealError) as caught:
        seal_directory(directory, expected, attempt_id="attempt-1")
    assert caught.value.code == "hard-link-uniqueness"
    assert classify_mode(stat.S_IFCHR | 0o600, 1) == "device-file"
    assert classify_mode(stat.S_IFBLK | 0o600, 1) == "device-file"
    assert classify_mode(stat.S_IFREG | 0o600, 1) is None


def test_cleanup_is_explicit_confined_and_idempotent(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    prepare_attempt(cache, "attempt-1", {"note.txt": b"synthetic", "other.txt": b"more"})
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"keep")
    (cache / "quarantine" / "attempt-1" / "escape.txt").symlink_to(outside)
    with pytest.raises(CleanupError) as caught:
        cleanup_attempt(cache, "attempt-1", state="quarantine")
    assert caught.value.code == "symlink-escape"
    assert outside.read_bytes() == b"keep"
    (cache / "quarantine" / "attempt-1" / "escape.txt").unlink()
    first = cleanup_attempt(cache, "attempt-1", state="quarantine")
    assert first["status"] == "clean"
    assert first["reclaimedBytes"] > len(b"synthetic")
    assert not (cache / "quarantine" / "attempt-1").exists()
    second = cleanup_attempt(cache, "attempt-1", state="quarantine")
    assert second["status"] == "already-clean"
    assert second["reclaimedBytes"] == 0


def test_partial_cleanup_and_verified_refusal(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    prepare_attempt(cache, "attempt-1", {"note.txt": b"one", "other.txt": b"two"})
    seen: list[Path] = []

    def fail_second(path: Path) -> None:
        seen.append(path)
        if len(seen) == 2:
            raise OSError("stop")
        path.unlink()

    with pytest.raises(CleanupError) as caught:
        cleanup_attempt(cache, "attempt-1", state="quarantine", unlink=fail_second)
    assert caught.value.code == "partial-cleanup"
    assert caught.value.reclaimed_bytes > 0
    finished = cleanup_attempt(cache, "attempt-1", state="quarantine")
    assert finished["status"] == "clean"
    with pytest.raises(CleanupError) as caught:
        cleanup_attempt(cache, "attempt-1", state="verified")
    assert caught.value.code == "verified-immutable"
    with pytest.raises(CleanupError) as caught:
        cleanup_attempt(
            cache,
            "attempt-1",
            state="verified",
            referenced_attempt_ids=frozenset({"attempt-1"}),
        )
    assert caught.value.code == "verified-referenced"


def test_rejected_cleanup_preserves_the_rejection_record(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    prepare_attempt(cache, "attempt-1", {"note.txt": b"one"})
    rejection = cache / "rejected" / "attempt-1"
    rejection.parent.mkdir()
    (cache / "quarantine" / "attempt-1").rename(rejection)
    (rejection / "rejection.json").write_text("{}\n", encoding="utf-8")
    result = cleanup_attempt(cache, "attempt-1", state="rejected")
    assert result["preservedRejectionRecord"] is True
    assert (rejection / "rejection.json").is_file()
    assert not (rejection / "note.txt").exists()
    repeated = cleanup_attempt(cache, "attempt-1", state="rejected")
    assert repeated["status"] == "already-clean"
    assert (rejection / "rejection.json").is_file()


def test_cleanup_refuses_paths_outside_the_cache(tmp_path: Path) -> None:
    cache = _cache(tmp_path)
    outside = tmp_path / "elsewhere" / "attempt-1"
    outside.mkdir(parents=True)
    (outside / "note.txt").write_bytes(b"keep")
    (cache / "quarantine").mkdir()
    (cache / "quarantine" / "attempt-1").symlink_to(outside)
    with pytest.raises(CleanupError) as caught:
        cleanup_attempt(cache, "attempt-1", state="quarantine")
    assert caught.value.code == "symlink-escape"
    assert (outside / "note.txt").read_bytes() == b"keep"
