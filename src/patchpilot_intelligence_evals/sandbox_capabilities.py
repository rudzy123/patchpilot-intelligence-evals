"""Linux capability probes for the hardened execution boundary.

A command's presence is not enforcement. Disposition ``enforced`` is recorded
only after a harmless behavioral probe succeeds. Reports omit hostnames,
usernames, addresses, environment values, and local paths.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from functools import cache
from pathlib import Path
from typing import Any, cast

from patchpilot_intelligence_evals.isolation_profile import IsolationError, probe_linux_limit
from patchpilot_intelligence_evals.schemas import repo_root, validate

PROBE_IDS: tuple[str, ...] = (
    "user-namespace",
    "mount-namespace",
    "pid-namespace",
    "network-namespace",
    "ipc-namespace",
    "uts-namespace",
    "cgroup-namespace",
    "bubblewrap",
    "rootless-podman",
    "rootless-docker",
    "unshare",
    "systemd-user-scope",
    "cgroup-v2",
    "cgroup-delegation",
    "rlimit-cpu",
    "rlimit-as",
    "rlimit-fsize",
    "rlimit-nofile",
    "rlimit-nproc",
    "seccomp",
)
_NAMESPACE_IDS: tuple[str, ...] = (
    "user-namespace",
    "mount-namespace",
    "pid-namespace",
    "network-namespace",
    "ipc-namespace",
    "uts-namespace",
    "cgroup-namespace",
)
_NAMESPACE_KINDS: dict[str, str] = {
    "user-namespace": "user",
    "mount-namespace": "mnt",
    "pid-namespace": "pid",
    "network-namespace": "net",
    "ipc-namespace": "ipc",
    "uts-namespace": "uts",
    "cgroup-namespace": "cgroup",
}
_RLIMIT_KINDS: dict[str, str] = {
    "rlimit-cpu": "cpu",
    "rlimit-as": "memory",
    "rlimit-fsize": "file-size",
    "rlimit-nofile": "open-files",
    "rlimit-nproc": "nproc",
}
_REPORT = Path("candidates/authorization/sandbox-capability-report.json")
_VERSION = re.compile(r"(\d+\.\d+(?:\.\d+)?)")
_PROBE_LINE = re.compile(r"^[A-Za-z0-9= .-]+$")

_PROBE_SCRIPT = """
import os
import pathlib
import socket
import sys

def ns(kind: str) -> str:
    link = os.readlink("/proc/self/ns/" + kind)
    return link.rsplit("[", 1)[-1].rstrip("]")

port = int(sys.argv[1])
parts = [
    "selfpid=" + str(os.getpid()),
    "setgroups=" + pathlib.Path("/proc/self/setgroups").read_text(encoding="utf-8").strip(),
    "host=" + socket.gethostname(),
    "home=" + ("1" if pathlib.Path("/home").exists() else "0"),
]
for kind in ("user", "mnt", "pid", "net", "ipc", "uts", "cgroup"):
    parts.append("ns" + kind + "=" + ns(kind))

def attempt(family: int, address: tuple[object, ...]) -> str:
    handle = socket.socket(family, socket.SOCK_STREAM)
    handle.settimeout(0.3)
    try:
        handle.connect(address)
    except Exception as exc:
        return type(exc).__name__
    finally:
        handle.close()
    return "reached"

parts.append("v4=" + attempt(socket.AF_INET, ("192.0.2.1", 9)))
try:
    parts.append("v6=" + attempt(socket.AF_INET6, ("2001:db8::1", 9, 0, 0)))
except OSError as exc:
    parts.append("v6=" + type(exc).__name__)
parts.append("lo=" + attempt(socket.AF_INET, ("127.0.0.1", port)))
try:
    socket.getaddrinfo("example.invalid", 9)
    parts.append("dns=reached")
except Exception as exc:
    parts.append("dns=" + type(exc).__name__)
unix = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    unix.connect(sys.argv[2])
    parts.append("unix=reached")
except Exception as exc:
    parts.append("unix=" + type(exc).__name__)
finally:
    unix.close()
print(" ".join(parts))
"""


class SandboxCapabilityError(ValueError):
    """A capability record failed a closed check. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def classify_probe(*, present: bool, behavior: str) -> tuple[str, str]:
    """Map presence and observed behavior to a disposition and evidence class.

    ``behavior`` is ``proven``, ``failed``, ``unproven``, or ``per-user``.
    """
    if behavior == "per-user":
        return "unsupported", "per-user-not-private"
    if not present:
        return "unavailable", "command-missing"
    if behavior == "proven":
        return "enforced", "behavior-proven"
    if behavior == "failed":
        return "failed", "probe-failed"
    return "unsupported", "command-present-unproven"


def validate_capability_report(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the report and reject presence-only enforcement claims."""
    validate("sandbox-capability-report", document)
    if document["realModelExecuted"] is not False or document["productionReady"] is not False:
        raise SandboxCapabilityError("execution-claim")
    identifiers = [str(item["probeId"]) for item in document["probes"]]
    if identifiers != list(PROBE_IDS):
        raise SandboxCapabilityError("probe-set")
    for item in document["probes"]:
        disposition, evidence = classify_probe(
            present=bool(item["commandPresent"]),
            behavior=_behavior_name(str(item["disposition"]), str(item["evidence"])),
        )
        if item["disposition"] != disposition or item["evidence"] != evidence:
            raise SandboxCapabilityError("evidence-mismatch")
        if item["disposition"] == "enforced" and item["evidence"] != "behavior-proven":
            raise SandboxCapabilityError("presence-only")
    return document


def load_capability_report(root: Path | None = None) -> dict[str, Any]:
    """Load the committed capability report."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _REPORT).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise SandboxCapabilityError("record-type")
    return validate_capability_report(cast(dict[str, Any], loaded))


@cache
def probe_capabilities() -> dict[str, Any]:
    """Probe this process's host and return a closed capability report."""
    family = _family(sys.platform)
    machine = _machine(platform.machine())
    if family != "linux":
        probes = [
            _item(probe_id, present=False, behavior="unproven", version=None)
            for probe_id in PROBE_IDS
        ]
        return validate_capability_report(_document(family, machine, probes))
    return validate_capability_report(_document(family, machine, _linux_probes()))


def _document(family: str, machine: str, probes: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schemaVersion": "1.0.0",
        "productionReady": False,
        "realModelExecuted": False,
        "acquisitionStatus": "not-acquired",
        "executionStatus": "not-executed",
        "operatingSystemFamily": family,
        "architecture": machine,
        "probes": probes,
    }


def _item(
    probe_id: str,
    *,
    present: bool,
    behavior: str,
    version: str | None,
) -> dict[str, Any]:
    disposition, evidence = classify_probe(present=present, behavior=behavior)
    return {
        "probeId": probe_id,
        "commandPresent": present,
        "disposition": disposition,
        "evidence": evidence,
        "mechanismVersion": version,
    }


def _behavior_name(disposition: str, evidence: str) -> str:
    if evidence == "per-user-not-private":
        return "per-user"
    if disposition == "enforced" and evidence == "behavior-proven":
        return "proven"
    if disposition == "failed" and evidence == "probe-failed":
        return "failed"
    if disposition == "unsupported" and evidence == "command-present-unproven":
        return "unproven"
    if disposition == "unavailable" and evidence == "command-missing":
        return "unproven"
    raise SandboxCapabilityError("evidence-mismatch")


def _linux_probes() -> list[dict[str, Any]]:
    bubblewrap = _bubblewrap_proof()
    probes = {
        probe_id: _item(probe_id, present=False, behavior="unproven", version=None)
        for probe_id in PROBE_IDS
    }
    version = _version(shutil.which("bwrap"), ["bwrap", "--version"])
    present = version is not None
    if bubblewrap is None:
        behavior = "failed" if present else "unproven"
        probes["bubblewrap"] = _item(
            "bubblewrap", present=present, behavior=behavior, version=version
        )
        for probe_id in _NAMESPACE_IDS:
            probes[probe_id] = _item(probe_id, present=present, behavior=behavior, version=version)
    else:
        probes["bubblewrap"] = _item("bubblewrap", present=True, behavior="proven", version=version)
        for probe_id in _NAMESPACE_IDS:
            behavior = "proven" if bubblewrap[probe_id] else "failed"
            probes[probe_id] = _item(probe_id, present=True, behavior=behavior, version=version)
    for name, probe_id in (("podman", "rootless-podman"), ("docker", "rootless-docker")):
        probes[probe_id] = _item(
            probe_id, present=shutil.which(name) is not None, behavior="unproven", version=None
        )
        if shutil.which(name) is None:
            continue
        probes[probe_id] = _item(probe_id, present=True, behavior="unproven", version=None)
    unshare_version = _version(shutil.which("unshare"), ["unshare", "--version"])
    if unshare_version is None:
        probes["unshare"] = _item("unshare", present=False, behavior="unproven", version=None)
    else:
        behavior = "proven" if _unshare_works() else "failed"
        probes["unshare"] = _item(
            "unshare", present=True, behavior=behavior, version=unshare_version
        )
    systemd_version = _systemd_version(shutil.which("systemd-run"))
    if systemd_version is None or shutil.which("systemctl") is None:
        probes["systemd-user-scope"] = _item(
            "systemd-user-scope",
            present=systemd_version is not None,
            behavior="unproven",
            version=systemd_version,
        )
    else:
        behavior = "proven" if _systemd_scope_works() else "failed"
        probes["systemd-user-scope"] = _item(
            "systemd-user-scope",
            present=True,
            behavior=behavior,
            version=systemd_version,
        )
    cgroup_present, delegated = _cgroup_state()
    probes["cgroup-v2"] = _item(
        "cgroup-v2",
        present=cgroup_present,
        behavior="proven" if cgroup_present else "unproven",
        version=None,
    )
    probes["cgroup-delegation"] = _item(
        "cgroup-delegation",
        present=cgroup_present,
        behavior="proven" if delegated else "failed",
        version=None,
    )
    for probe_id, kind in _RLIMIT_KINDS.items():
        fired = _rlimit_fires(kind)
        if probe_id == "rlimit-nproc":
            behavior = "per-user" if fired else "failed"
        else:
            behavior = "proven" if fired else "failed"
        probes[probe_id] = _item(probe_id, present=True, behavior=behavior, version=None)
    help_text = _command_stdout(["bwrap", "--help"]) if present else ""
    seccomp_present = "--seccomp" in help_text
    probes["seccomp"] = _item(
        "seccomp",
        present=seccomp_present,
        behavior="unproven",
        version=version if seccomp_present else None,
    )
    return [probes[probe_id] for probe_id in PROBE_IDS]


def _bubblewrap_proof() -> dict[str, bool] | None:
    if shutil.which("bwrap") is None or shutil.which("python3") is None:
        return None
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    port = int(listener.getsockname()[1])
    sock_dir = Path(tempfile.mkdtemp(prefix="patchpilot-sock-", dir="/tmp"))
    sock_path = sock_dir / "h.sock"
    unix_listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        unix_listener.bind(str(sock_path))
        unix_listener.listen(1)
        own = {kind: _ns_inode(kind) for kind in _NAMESPACE_KINDS.values()}
        argv = [
            "bwrap",
            "--unshare-user",
            "--unshare-pid",
            "--unshare-ipc",
            "--unshare-uts",
            "--unshare-net",
            "--unshare-cgroup",
            "--die-with-parent",
            "--hostname",
            "sandbox",
            "--clearenv",
            "--setenv",
            "PATH",
            "/usr/bin",
            "--ro-bind",
            "/usr",
            "/usr",
            "--proc",
            "/proc",
            "--dev",
            "/dev",
            "--tmpfs",
            "/tmp",
        ]
        if Path("/lib").is_dir():
            argv.extend(["--ro-bind", "/lib", "/lib"])
        if Path("/lib64").is_dir():
            argv.extend(["--ro-bind", "/lib64", "/lib64"])
        argv.extend(["--", "python3", "-c", _PROBE_SCRIPT, str(port), str(sock_path)])
        code, stdout = _run(argv, 15)
        if code != 0 or not _PROBE_LINE.match(stdout.strip()):
            return None
        fields = dict(part.split("=", 1) for part in stdout.split())
        if fields.get("setgroups") != "deny" or fields.get("host") != "sandbox":
            return None
        if fields.get("home") != "0" or fields.get("selfpid") not in {"1", "2"}:
            return None
        denied = fields.get("v4") not in {None, "reached"} and fields.get("dns") not in {
            None,
            "reached",
        }
        denied = denied and fields.get("lo") != "reached" and fields.get("unix") != "reached"
        denied = denied and fields.get("v6") != "reached"
        proof: dict[str, bool] = {}
        for probe_id, kind in _NAMESPACE_KINDS.items():
            changed = fields.get("ns" + kind) not in {None, own[kind]}
            if probe_id == "network-namespace":
                proof[probe_id] = changed and denied
            elif probe_id == "mount-namespace":
                proof[probe_id] = changed and fields.get("home") == "0"
            elif probe_id == "pid-namespace":
                proof[probe_id] = changed and fields.get("selfpid") in {"1", "2"}
            elif probe_id == "uts-namespace":
                proof[probe_id] = changed and fields.get("host") == "sandbox"
            else:
                proof[probe_id] = changed
        return proof
    finally:
        listener.close()
        unix_listener.close()
        sock_path.unlink(missing_ok=True)
        sock_dir.rmdir()


def _unshare_works() -> bool:
    code, _stdout = _run(["unshare", "--user", "--map-root-user", "--net", "true"], 10)
    return code == 0


def _systemd_scope_works() -> bool:
    memory = _run(
        [
            "systemd-run",
            "--user",
            "--scope",
            "--collect",
            "--quiet",
            "-p",
            "MemoryMax=33554432",
            "-p",
            "MemorySwapMax=0",
            "--",
            "python3",
            "-c",
            "blob=bytearray(80*1024*1024)",
        ],
        15,
    )
    tasks = _run(
        [
            "systemd-run",
            "--user",
            "--scope",
            "--collect",
            "--quiet",
            "-p",
            "TasksMax=4",
            "--",
            "python3",
            "-c",
            "import os\n"
            "ok=0\n"
            "try:\n"
            "    for _ in range(8):\n"
            "        pid=os.fork()\n"
            "        if pid==0:\n"
            "            os._exit(0)\n"
            "        ok+=1\n"
            "except OSError:\n"
            "    pass\n"
            "raise SystemExit(2 if ok < 8 else 0)\n",
        ],
        15,
    )
    memory_killed = memory[0] < 0 or memory[0] >= 128
    return memory_killed and tasks[0] == 2


def _cgroup_state() -> tuple[bool, bool]:
    controllers = Path("/sys/fs/cgroup/cgroup.controllers")
    if not controllers.is_file():
        return False, False
    text = controllers.read_text(encoding="utf-8")
    present = "memory" in text.split() and "pids" in text.split()
    if not present:
        return False, False
    relative = Path("/proc/self/cgroup").read_text(encoding="utf-8").split(":", 2)[-1].strip()
    base = Path("/sys/fs/cgroup") / relative.lstrip("/")
    child = base / f"patchpilot-probe-{os.getpid()}"
    delegated = False
    try:
        child.mkdir(exist_ok=False)
        try:
            (child / "memory.max").write_text("33554432\n", encoding="utf-8")
            (child / "pids.max").write_text("16\n", encoding="utf-8")
            delegated = True
        except OSError:
            delegated = False
    except OSError:
        delegated = False
    finally:
        if child.exists():
            try:
                child.rmdir()
            except OSError:
                delegated = False
    return True, delegated


def _rlimit_fires(kind: str) -> bool:
    try:
        return probe_linux_limit(kind) == "enforced"
    except (IsolationError, subprocess.TimeoutExpired, OSError):
        return False


def _ns_inode(kind: str) -> str:
    link = os.readlink(f"/proc/self/ns/{kind}")
    return link.rsplit("[", 1)[-1].rstrip("]")


def _systemd_version(path: str | None) -> str | None:
    if path is None:
        return None
    match = re.search(r"\bsystemd\s+(\d+)\b", _command_stdout(["systemd-run", "--version"]))
    if match is not None:
        return match.group(1)
    return _version(path, ["systemd-run", "--version"])


def _version(path: str | None, argv: list[str]) -> str | None:
    if path is None:
        return None
    match = _VERSION.search(_command_stdout(argv))
    if match is None:
        return None
    return match.group(1)


def _command_stdout(argv: list[str]) -> str:
    _code, stdout = _run(argv, 10)
    return stdout


def _run(argv: list[str], timeout: float) -> tuple[int, str]:
    proc = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        shell=False,
        start_new_session=True,
        text=True,
    )
    try:
        stdout, _stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill(proc.pid)
        try:
            stdout, _stderr = proc.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            stdout = ""
        return 124, stdout or ""
    return proc.returncode if proc.returncode is not None else 1, stdout or ""


def _kill(pid: int) -> None:
    try:
        os.killpg(pid, 9)
    except (ProcessLookupError, PermissionError):
        return


def _family(name: str) -> str:
    if name.startswith("linux"):
        return "linux"
    if name == "darwin":
        return "darwin"
    if name.startswith("win"):
        return "windows"
    return "other"


def _machine(name: str) -> str:
    if name in {"x86_64", "aarch64"}:
        return name
    return "other"
