"""Filesystem identity, fsync, and renameat2 behavior."""

from __future__ import annotations

import errno
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.filesystem_identity import (
    IdentityError,
    _rename_error,
    device_equal,
    logical_and_allocated,
    rename_noreplace,
)


def test_same_directory_device_matches_without_recording_it(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    left.mkdir()
    right.mkdir()
    assert device_equal(left, right) is True
    (left / "file.txt").write_bytes(b"abc")
    logical, allocated = logical_and_allocated(left / "file.txt")
    assert logical == 3
    assert allocated >= 0


def test_rename_noreplace_rejects_an_existing_destination(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    (source / "file.txt").write_bytes(b"abc")
    rename_noreplace(source, destination)
    assert destination.is_dir()
    assert not source.exists()
    assert (destination / "file.txt").read_bytes() == b"abc"
    other = tmp_path / "other"
    other.mkdir()
    with pytest.raises(IdentityError) as caught:
        rename_noreplace(other, destination)
    assert caught.value.code == "destination-collision"
    assert other.is_dir()
    assert (destination / "file.txt").read_bytes() == b"abc"


def test_rename_errno_mapping() -> None:
    assert _rename_error(errno.EXDEV) == "cross-device"
    assert _rename_error(errno.EEXIST) == "destination-collision"
    assert _rename_error(errno.EINVAL) == "filesystem-capability-unsupported"
    assert _rename_error(errno.EIO) == "rename-failure"
