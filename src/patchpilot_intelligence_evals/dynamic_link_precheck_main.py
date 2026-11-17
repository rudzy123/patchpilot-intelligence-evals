"""Sandbox child for the dynamic-link precheck.

The parent copies this file to ``/fixture/main.py``. It loads the verified
runtime library, resolves ``OrtGetApiBase``, and exits. It does not obtain the
session API table and it does not call Run.
"""

from __future__ import annotations

import ctypes
import json
from pathlib import Path

_LIBRARY = "/verified-runtime/libonnxruntime.so.1.31.1"
_RUNTIME_NAME = "libonnxruntime.so.1.31.1"
_BANNED = (
    "/home/",
    "neural-from-scratch",
    "patchpilot-intelligence-evals",
    "quarantine",
    "site-packages",
)


def main() -> int:
    """Load the runtime library inside the measurement sandbox and close it."""
    report: dict[str, object] = {
        "apiVersion": None,
        "createSessionCalled": False,
        "exportedSymbols": [],
        "getApiCalled": False,
        "libraryClosed": False,
        "mappedBasenames": [],
        "modelSessionCreated": False,
        "network": _network(),
        "providerLoaded": False,
        "runInvoked": False,
        "symbolBoundary": "violated",
        "unexpectedPath": False,
    }
    try:
        _load(report)
    except OSError:
        report["symbolBoundary"] = "violated"
    _write(report)
    version = report["apiVersion"]
    held = (
        report["symbolBoundary"] == "held"
        and report["libraryClosed"] is True
        and report["providerLoaded"] is False
        and report["unexpectedPath"] is False
        and report["createSessionCalled"] is False
        and report["getApiCalled"] is False
        and report["runInvoked"] is False
        and report["modelSessionCreated"] is False
        and isinstance(version, str)
        and "1.31.1" in version
    )
    return 0 if held else 4


def _load(report: dict[str, object]) -> None:
    library = ctypes.CDLL(_LIBRARY)
    symbol = getattr(library, "OrtGetApiBase", None)
    if symbol is None:
        return
    report["exportedSymbols"] = ["OrtGetApiBase"]
    symbol.argtypes = []
    symbol.restype = ctypes.c_void_p
    base_pointer = symbol()
    if not base_pointer:
        _finish_close(library, report)
        return
    version_type = ctypes.CFUNCTYPE(ctypes.c_char_p)
    base = ctypes.cast(base_pointer, ctypes.POINTER(ctypes.c_void_p * 2)).contents
    version_pointer = base[1]
    if not isinstance(version_pointer, int) or version_pointer == 0:
        _finish_close(library, report)
        return
    version_text = version_type(version_pointer)()
    if version_text is not None:
        report["apiVersion"] = version_text.decode("utf-8", "replace")[:40]
    maps = Path("/proc/self/maps").read_text(encoding="utf-8")
    names = _basenames(maps)
    report["mappedBasenames"] = names
    report["providerLoaded"] = any("providers" in name for name in names)
    report["unexpectedPath"] = _unexpected(maps)
    report["libraryClosed"] = _close(library, maps)
    version = report["apiVersion"]
    if (
        isinstance(version, str)
        and "1.31.1" in version
        and report["libraryClosed"] is True
        and report["providerLoaded"] is False
        and report["unexpectedPath"] is False
        and _RUNTIME_NAME in names
    ):
        report["symbolBoundary"] = "held"


def _finish_close(library: ctypes.CDLL, report: dict[str, object]) -> None:
    maps = ""
    path = Path("/proc/self/maps")
    if path.is_file():
        maps = path.read_text(encoding="utf-8")
        report["mappedBasenames"] = _basenames(maps)
    report["libraryClosed"] = _close(library, maps)


def _basenames(maps: str) -> list[str]:
    names: set[str] = set()
    for line in maps.splitlines():
        parts = line.split()
        if len(parts) < 6 or parts[-1].startswith("["):
            continue
        name = Path(parts[-1]).name
        if ".so" in name:
            names.add(name)
    return sorted(names)


def _unexpected(maps: str) -> bool:
    for line in maps.splitlines():
        parts = line.split()
        if len(parts) < 6 or parts[-1].startswith("["):
            continue
        path = parts[-1]
        if any(token in path for token in _BANNED):
            return True
        name = Path(path).name
        if "onnxruntime" in name and name != _RUNTIME_NAME:
            return True
    return False


def _close(library: ctypes.CDLL, maps: str) -> bool:
    handle = getattr(library, "_handle", None)
    if not isinstance(handle, int):
        return False
    libdl = _libdl(maps)
    if libdl is None:
        return False
    libdl.dlclose.argtypes = [ctypes.c_void_p]
    libdl.dlclose.restype = ctypes.c_int
    return bool(libdl.dlclose(handle) == 0)


def _libdl(maps: str) -> ctypes.CDLL | None:
    for line in maps.splitlines():
        parts = line.split()
        if len(parts) >= 6 and parts[-1].endswith("/libdl.so.2"):
            return ctypes.CDLL(parts[-1])
    return None


def _network() -> dict[str, str]:

    return {"dns": _dns(), "ipv4": _tcp("192.0.2.1"), "localLoopback": _tcp("127.0.0.1")}


def _tcp(address: str) -> str:
    import socket

    handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    handle.settimeout(0.3)
    try:
        handle.connect((address, 9))
    except OSError as exc:
        return type(exc).__name__
    finally:
        handle.close()
    return "reached"


def _dns() -> str:
    import socket

    try:
        socket.getaddrinfo("example.invalid", 9)
    except OSError as exc:
        return type(exc).__name__
    return "reached"


def _write(report: dict[str, object]) -> None:
    Path("/results/report.json").write_text(
        json.dumps(report, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
