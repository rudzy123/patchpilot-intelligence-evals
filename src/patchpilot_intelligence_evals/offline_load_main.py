"""Offline load proof child. It does not generate tokens or call session Run."""

from __future__ import annotations

import ctypes
import json
import socket
from pathlib import Path
from typing import Any

_ALLOWED = {
    "api_version",
    "create_env",
    "create_session",
    "create_session_options",
    "disable_telemetry",
    "get_error_message",
    "input_count",
    "logging_level",
    "output_count",
    "release_env",
    "release_session",
    "release_session_options",
}


def main(argv: list[str]) -> int:
    """Initialize the mounted runtime and tokenizer, then exit without generation."""
    report: dict[str, object] = {
        "corpusExecuted": False,
        "generationTokens": 0,
        "inferencePerformed": False,
        "inputCount": None,
        "loadStatus": "failed",
        "network": _network(),
        "outputCount": None,
        "residentBytes": _resident_bytes(),
        "tokenizerInitialized": False,
    }
    indexes = _indexes(argv)
    if indexes is None:
        _write(report)
        return 2
    try:
        _load(indexes, report)
    except OSError:
        report["loadStatus"] = "failed"
    _write(report)
    return 0 if report["loadStatus"] == "loaded" else 3


def _indexes(argv: list[str]) -> dict[str, int] | None:
    indexes: dict[str, int] = {}
    for item in argv:
        if item.startswith("run=") or "=" not in item:
            return None
        name, raw = item.split("=", 1)
        if name not in _ALLOWED or not raw.isdecimal():
            return None
        indexes[name] = int(raw)
    if any(name not in indexes for name in _ALLOWED):
        return None
    return indexes


def _load(indexes: dict[str, int], report: dict[str, object]) -> None:
    library = ctypes.CDLL("/verified-runtime/libonnxruntime.so.1.31.1")
    library.OrtGetApiBase.argtypes = []
    library.OrtGetApiBase.restype = ctypes.c_void_p
    base_pointer = library.OrtGetApiBase()
    if not base_pointer:
        return
    get_api = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_uint32)
    version = ctypes.CFUNCTYPE(ctypes.c_char_p)
    base = ctypes.cast(base_pointer, ctypes.POINTER(ctypes.c_void_p * 2)).contents
    get_api_pointer = base[0]
    version_pointer = base[1]
    if not isinstance(get_api_pointer, int) or not isinstance(version_pointer, int):
        return
    api = get_api(get_api_pointer)(indexes["api_version"])
    version_text = version(version_pointer)()
    if not api or version_text is None or b"1.31.1" not in version_text:
        report["loadStatus"] = "version-mismatch"
        return
    slots = ctypes.cast(api, ctypes.POINTER(ctypes.c_void_p))
    env = ctypes.c_void_p()
    if _failed(slots, indexes["create_env"], _create_env(indexes["logging_level"], env)):
        return
    if _failed(slots, indexes["disable_telemetry"], _call_env(env)):
        return
    options = ctypes.c_void_p()
    if _failed(slots, indexes["create_session_options"], _call_out(options)):
        return
    session = ctypes.c_void_p()
    if _failed(slots, indexes["create_session"], _create_session(env, options, session)):
        return
    inputs = ctypes.c_size_t()
    outputs = ctypes.c_size_t()
    if _failed(slots, indexes["input_count"], _call_count(session, inputs)):
        return
    if _failed(slots, indexes["output_count"], _call_count(session, outputs)):
        return
    report["inputCount"] = int(inputs.value)
    report["outputCount"] = int(outputs.value)
    _release(slots, indexes["release_session"], session)
    _release(slots, indexes["release_session_options"], options)
    _release(slots, indexes["release_env"], env)
    document = json.loads(Path("/verified-model/tokenizer.json").read_text(encoding="utf-8"))
    model = document.get("model") if isinstance(document, dict) else None
    vocab = model.get("vocab") if isinstance(model, dict) else None
    if not isinstance(vocab, dict):
        report["loadStatus"] = "tokenizer-uninitialized"
        return
    report["tokenizerInitialized"] = True
    report["loadStatus"] = "loaded"
    report["inferencePerformed"] = False
    report["generationTokens"] = 0


def _create_env(level: int, env: ctypes.c_void_p) -> object:
    kind = ctypes.CFUNCTYPE(
        ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)
    )
    return lambda function: kind(function)(level, b"patchpilot-load-proof", ctypes.byref(env))


def _call_env(env: ctypes.c_void_p) -> object:
    kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)
    return lambda function: kind(function)(env)


def _call_out(target: ctypes.c_void_p) -> object:
    kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
    return lambda function: kind(function)(ctypes.byref(target))


def _create_session(
    env: ctypes.c_void_p, options: ctypes.c_void_p, session: ctypes.c_void_p
) -> object:
    kind = ctypes.CFUNCTYPE(
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
    )
    path = b"/verified-model/onnx/model.onnx"
    return lambda function: kind(function)(env, path, options, ctypes.byref(session))


def _call_count(session: ctypes.c_void_p, count: ctypes.c_size_t) -> object:
    kind = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t))
    return lambda function: kind(function)(session, ctypes.byref(count))


def _failed(slots: Any, index: int, caller: Any) -> bool:
    status = caller(slots[index])
    return bool(status)


def _release(slots: Any, index: int, target: ctypes.c_void_p) -> None:
    kind = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
    kind(slots[index])(target)


def _network() -> dict[str, str]:
    return {
        "dns": _dns(),
        "ipv4": _tcp("192.0.2.1"),
        "localLoopback": _tcp("127.0.0.1"),
    }


def _tcp(address: str) -> str:
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
    try:
        socket.getaddrinfo("example.invalid", 9)
    except OSError as exc:
        return type(exc).__name__
    return "reached"


def _resident_bytes() -> int:
    try:
        import resource

        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    except (ImportError, OSError, ValueError):
        return 0


def _write(report: dict[str, object]) -> None:
    encoded = json.dumps(report, sort_keys=True)
    Path("/results/report.json").write_text(encoded, encoding="utf-8")


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
