"""Process entry that runs one candidate script under the in-process hooks.

The network hook patches Python socket, DNS, and urllib entry points. The file
hook rejects corpus, prior-result, and sibling-repository paths. Neither hook
is a seccomp profile, mount namespace, container, or firewall. A candidate that
catches the failure, calls a private module, or starts another executable is
outside this control.
"""

from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

from patchpilot_intelligence_evals.candidate_boundary import (
    install_candidate_boundary,
    restore_candidate_boundary,
)
from patchpilot_intelligence_evals.network_guard import NetworkProhibited, network_guard

_SIBLING_PARTS = frozenset({"patchpilot", "neural-from-scratch"})

NETWORK_EXIT = 86
NETWORK_STDERR = "network-policy-failure\n"


def _script_in_runtime(relative: str, runtime: Path) -> Path | None:
    if relative.startswith(("/", "\\")) or not relative.endswith(".py"):
        return None
    parts = Path(relative).parts
    if any(part in {"", ".", ".."} or part in _SIBLING_PARTS for part in parts):
        return None
    script = runtime.joinpath(*parts)
    normalized = Path(os.path.normpath(str(script)))
    root = Path(os.path.normpath(str(runtime)))
    if normalized != root and root not in normalized.parents:
        return None
    if script.is_symlink() or not script.is_file():
        return None
    return script


def main(argv: list[str] | None = None) -> int:
    """Run the relative script from the child working directory.

    Return its exit code, or 86 on a hooked network use. The working directory
    is the temporary runtime prepared by the runner.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1:
        return 2
    runtime = Path.cwd()
    script = _script_in_runtime(args[0], runtime)
    if script is None:
        return 2
    sys.argv = [args[0]]
    install_candidate_boundary(runtime)
    try:
        with network_guard():
            runpy.run_path(str(script), run_name="__main__")
    except NetworkProhibited:
        sys.stderr.write(NETWORK_STDERR)
        return NETWORK_EXIT
    except SystemExit as exc:
        code = exc.code
        if code is None or code == 0:
            return 0
        if isinstance(code, int):
            return code
        return 1
    finally:
        restore_candidate_boundary()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
