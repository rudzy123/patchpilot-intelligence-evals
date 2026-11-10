"""Network and environment fixture. It prints status names, not secret values."""

from __future__ import annotations

import json
import os
import socket
from pathlib import Path


def main() -> None:
    request = json.loads(Path("/config/request.json").read_text(encoding="utf-8"))
    report = {
        "env": sorted(os.environ),
        "ipv4": _tcp(socket.AF_INET, ("192.0.2.1", 9)),
        "ipv6": _tcp(socket.AF_INET6, ("2001:db8::1", 9, 0, 0)),
        "loopback": _tcp(socket.AF_INET, ("127.0.0.1", int(request["port"]))),
        "localLoopback": _tcp(socket.AF_INET, ("127.0.0.1", 9)),
        "dns": _dns(),
        "unix": _unix(str(request["unixSocket"])),
    }
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":"))
    Path("/results/report.json").write_text(encoded, encoding="utf-8")
    print(encoded)


def _tcp(family: int, address: tuple[object, ...]) -> str:
    handle = socket.socket(family, socket.SOCK_STREAM)
    handle.settimeout(0.3)
    try:
        handle.connect(address)
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


def _unix(path: str) -> str:
    handle = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        handle.connect(path)
    except OSError as exc:
        return type(exc).__name__
    finally:
        handle.close()
    return "reached"


if __name__ == "__main__":
    main()
