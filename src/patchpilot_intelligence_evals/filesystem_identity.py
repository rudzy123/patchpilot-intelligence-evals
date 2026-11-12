"""Same-filesystem identity, fsync, and renameat2.

Linux rename(2) renames a directory atomically on one filesystem and returns
EXDEV across filesystems. renameat2 with RENAME_NOREPLACE returns EEXIST when
the destination exists. fsync(2) on a file does not persist that file's
directory entry; the parent directory is synced separately. st_size is the
logical length. st_blocks counts 512-byte allocated units.
"""

from __future__ import annotations

import ctypes
import errno
import os
import stat
from pathlib import Path

AT_FDCWD = -100
RENAME_NOREPLACE = 1


class IdentityError(ValueError):
    """A filesystem primitive failed closed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def device_equal(left: Path, right: Path) -> bool:
    """Compare device identity. The numeric device id is not returned."""
    return os.lstat(left).st_dev == os.lstat(right).st_dev


def logical_and_allocated(path: Path) -> tuple[int, int]:
    """Return logical size and allocated bytes without following a link."""
    info = os.lstat(path)
    return info.st_size, info.st_blocks * 512


def write_new_file(path: Path, payload: bytes) -> None:
    """Create one regular file and fsync its bytes. An existing path fails."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, 0o644)
    except OSError as exc:
        raise IdentityError("synchronization-failure") from exc
    try:
        view = payload
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise IdentityError("synchronization-failure")
            view = view[written:]
        os.fsync(descriptor)
    except OSError as exc:
        raise IdentityError("synchronization-failure") from exc
    finally:
        os.close(descriptor)


def fsync_file(path: Path) -> None:
    """Fsync a regular file opened without following a final symlink."""
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        raise IdentityError("synchronization-failure") from exc
    try:
        os.fsync(descriptor)
    except OSError as exc:
        raise IdentityError("synchronization-failure") from exc
    finally:
        os.close(descriptor)


def fsync_directory(path: Path) -> None:
    """Fsync a real directory. A symlink directory fails closed."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise IdentityError("synchronization-failure") from exc
    try:
        os.fsync(descriptor)
    except OSError as exc:
        raise IdentityError("synchronization-failure") from exc
    finally:
        os.close(descriptor)


def rename_noreplace(source: Path, destination: Path) -> None:
    """Rename without replacing an existing destination."""
    _renameat2(source, destination, RENAME_NOREPLACE)


def rename_replace_file(source: Path, destination: Path) -> None:
    """Atomically replace one metadata file. Directories are rejected."""
    if _is_directory(source) or _is_directory(destination):
        raise IdentityError("rename-failure")
    _renameat2(source, destination, 0)


def _is_directory(path: Path) -> bool:
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return False
    return stat.S_ISDIR(info.st_mode)


def _rename_error(error: int) -> str:
    """Map a renameat2 errno to a closed failure category."""
    if error == errno.EXDEV:
        return "cross-device"
    if error in {errno.EEXIST, errno.ENOTEMPTY, errno.EISDIR}:
        return "destination-collision"
    if error == errno.EINVAL:
        return "filesystem-capability-unsupported"
    return "rename-failure"


def _renameat2(source: Path, destination: Path, flags: int) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    function = getattr(libc, "renameat2", None)
    if function is None:
        raise IdentityError("filesystem-capability-unsupported")
    function.argtypes = (
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    )
    function.restype = ctypes.c_int
    ctypes.set_errno(0)
    result = function(
        AT_FDCWD,
        os.fsencode(source),
        AT_FDCWD,
        os.fsencode(destination),
        flags,
    )
    if result == 0:
        return
    raise IdentityError(_rename_error(ctypes.get_errno()))
