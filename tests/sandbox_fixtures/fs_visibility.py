"""Filesystem visibility fixture. It prints statuses, not sentinel contents."""

from __future__ import annotations

import json
import os
import socket
from pathlib import Path


def _exists(path: str) -> bool:
    try:
        return Path(path).exists()
    except OSError:
        return False


def _write_failed(path: str) -> bool:
    try:
        Path(path).write_text("x", encoding="utf-8")
    except OSError:
        return True
    return False


def main() -> None:
    request = json.loads(Path("/config/request.json").read_text(encoding="utf-8"))
    mountinfo = Path("/proc/self/mountinfo").read_text(encoding="utf-8")
    report: dict[str, object] = {
        "artifact": _exists("/artifacts/marker"),
        "config": _exists("/config/request.json"),
        "artifactWriteBlocked": _write_failed("/artifacts/new"),
        "configWriteBlocked": _write_failed("/config/new"),
        "resultWrite": Path("/results").is_dir(),
        "gold": _exists("/gold/marker"),
        "prior": _exists("/prior/marker"),
        "siblingPatchpilot": _exists("/siblings/patchpilot"),
        "siblingNeural": _exists("/siblings/neural-from-scratch"),
        "home": _exists("/home"),
        "root": _exists("/root"),
        "ssh": _exists("/.ssh") or _exists("/root/.ssh"),
        "aws": _exists("/.aws"),
        "azure": _exists("/.azure"),
        "gcloud": _exists("/.config/gcloud"),
        "kube": _exists("/.kube"),
        "gitCredentials": _exists("/.git-credentials"),
        "npm": _exists("/.npmrc"),
        "corpus": _exists("/corpus"),
        "etc": _exists("/etc"),
        "homeInMounts": "/home/" in mountinfo,
        "numericUidOption": "uid=" in mountinfo,
        "procBinfmt": "binfmt_misc" in mountinfo,
        "singleUidMap": len(Path("/proc/self/uid_map").read_text(encoding="utf-8").splitlines())
        == 1,
        "env": sorted(os.environ),
    }
    try:
        Path("/results/out.txt").write_text("ok", encoding="utf-8")
        report["resultCreated"] = True
    except OSError:
        report["resultCreated"] = False
    try:
        Path("/artifacts/escape").read_bytes()
        report["symlinkEscaped"] = True
    except OSError:
        report["symlinkEscaped"] = False
    report["network"] = _network(int(request["port"]), str(request["unixSocket"]))
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":"))
    Path("/results/report.json").write_text(encoded, encoding="utf-8")
    print(encoded)


def _network(port: int, unix_path: str) -> dict[str, str]:
    return {
        "ipv4": _tcp(socket.AF_INET, ("192.0.2.1", 9)),
        "ipv6": _tcp(socket.AF_INET6, ("2001:db8::1", 9, 0, 0)),
        "loopback": _tcp(socket.AF_INET, ("127.0.0.1", port)),
        "dns": _dns(),
        "unix": _unix(unix_path),
        "localLoopback": _tcp(socket.AF_INET, ("127.0.0.1", 9)),
    }


def _tcp(family: int, address: tuple[object, ...]) -> str:
    handle = socket.socket(family, socket.SOCK_STREAM)
    handle.settimeout(0.3)
    try:
        handle.connect(address)
    except Exception as exc:
        return type(exc).__name__
    finally:
        handle.close()
    return "reached"


def _dns() -> str:
    try:
        socket.getaddrinfo("example.invalid", 9)
    except Exception as exc:
        return type(exc).__name__
    return "reached"


def _unix(path: str) -> str:
    handle = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        handle.connect(path)
    except Exception as exc:
        return type(exc).__name__
    finally:
        handle.close()
    return "reached"


if __name__ == "__main__":
    main()
