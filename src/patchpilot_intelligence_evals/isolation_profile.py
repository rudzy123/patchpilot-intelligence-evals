"""Real-candidate isolation profile and harmless Linux limit probes.

The fixture runner is unchanged. These probes run a separate child and do not
execute a model. Resource limits are not a container, a user namespace, or an
operating-system sandbox.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from patchpilot_intelligence_evals.schemas import repo_root, validate

_PROFILE = Path("candidates/authorization/real-candidate-isolation-profile.json")
_PROBE_KINDS = frozenset({"cpu", "file-size", "memory", "nproc", "open-files"})


class IsolationError(ValueError):
    """An isolation record or probe failed. The message is a code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def validate_profile(document: dict[str, Any]) -> dict[str, Any]:
    """Validate the profile and its blocker flag."""
    validate("real-candidate-isolation-profile", document)
    if document["operatingSystemSandboxClaimed"] is not False:
        raise IsolationError("sandbox-claim")
    identifiers: list[str] = []
    blocking = False
    for control in document["controls"]:
        identifiers.append(str(control["controlId"]))
        deferred = control["disposition"] == "deferred-blocker"
        if bool(control["acquisitionBlocking"]) is not deferred:
            raise IsolationError("blocker-flag")
        blocking = blocking or deferred
    if len(identifiers) != len(set(identifiers)):
        raise IsolationError("duplicate-control")
    if document["acquisitionBlocked"] is not blocking:
        raise IsolationError("acquisition-blocked")
    return document


def load_profile(root: Path | None = None) -> dict[str, Any]:
    """Load the committed isolation profile."""
    base = root if root is not None else repo_root()
    loaded = json.loads((base / _PROFILE).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise IsolationError("record-type")
    return validate_profile(loaded)


def has_acquisition_blocker(document: dict[str, Any] | None = None) -> bool:
    """Return whether the profile withholds Track 6 acquisition."""
    profile = document if document is not None else load_profile()
    checked = validate_profile(profile)
    return bool(checked["acquisitionBlocked"])


def probe_linux_limit(kind: str) -> str:
    """Run one harmless child and return ``enforced`` when the limit fires."""
    if kind not in _PROBE_KINDS:
        raise IsolationError("unknown-probe")
    if not sys.platform.startswith("linux"):
        raise IsolationError("unavailable")
    script = _SCRIPTS[kind]
    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        shell=False,
        capture_output=True,
        start_new_session=True,
        timeout=10,
    )
    if completed.returncode not in {2} and completed.returncode >= 0:
        raise IsolationError("limit-not-enforced")
    return "enforced"


_SCRIPTS: dict[str, str] = {
    "file-size": (
        "import os, resource, signal, tempfile\n"
        "descriptor, path = tempfile.mkstemp()\n"
        "os.close(descriptor)\n"
        "signal.signal(signal.SIGXFSZ, signal.SIG_IGN)\n"
        "resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))\n"
        "try:\n"
        "    with open(path, 'wb') as handle:\n"
        "        handle.write(b'x')\n"
        "except OSError:\n"
        "    os.unlink(path)\n"
        "    raise SystemExit(2)\n"
        "os.unlink(path)\n"
        "raise SystemExit(0)\n"
    ),
    "open-files": (
        "import os, resource\n"
        "used = len(os.listdir('/proc/self/fd'))\n"
        "target = used + 1\n"
        "hard = resource.getrlimit(resource.RLIMIT_NOFILE)[1]\n"
        "ceiling = target if hard == resource.RLIM_INFINITY else max(hard, target)\n"
        "resource.setrlimit(resource.RLIMIT_NOFILE, (target, ceiling))\n"
        "opened = []\n"
        "try:\n"
        "    while True:\n"
        "        opened.append(open('/dev/null', 'rb'))\n"
        "except OSError:\n"
        "    raise SystemExit(2)\n"
    ),
    "cpu": (
        "import resource\nresource.setrlimit(resource.RLIMIT_CPU, (1, 1))\nwhile True:\n    pass\n"
    ),
    "memory": (
        "import resource\n"
        "limit = 64 * 1024 * 1024\n"
        "resource.setrlimit(resource.RLIMIT_AS, (limit, limit))\n"
        "try:\n"
        "    blob = bytearray(128 * 1024 * 1024)\n"
        "except MemoryError:\n"
        "    raise SystemExit(2)\n"
        "del blob\n"
        "raise SystemExit(0)\n"
    ),
    "nproc": (
        "import os, resource\n"
        "resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))\n"
        "try:\n"
        "    pid = os.fork()\n"
        "except OSError:\n"
        "    raise SystemExit(2)\n"
        "if pid == 0:\n"
        "    os._exit(0)\n"
        "raise SystemExit(0)\n"
    ),
}
