"""Report whether restricted paths are readable. This script emits no file contents."""

from __future__ import annotations

import json
from pathlib import Path


def _attempt(action: object) -> str:
    try:
        if callable(action):
            action()
        else:
            raise SystemExit(2)
    except PermissionError:
        return "denied"
    except FileNotFoundError:
        return "absent"
    except OSError:
        return "denied"
    return "readable"


def main() -> None:
    from patchpilot_intelligence_evals.schemas import repo_root

    root = repo_root()
    report: dict[str, object] = {
        "corpus": _attempt(
            lambda: (root / "corpus" / "cases" / "case-ground-001.json").read_text()
        ),
        "build": _attempt(
            lambda: (root / "build" / "candidate-execution-result.json").read_text(encoding="utf-8")
        ),
        "sibling-patchpilot": _attempt(
            lambda: (root.parent / "patchpilot" / "README.md").read_text()
        ),
        "sibling-neural-from-scratch": _attempt(
            lambda: (root.parent / "neural-from-scratch" / "README.md").read_text()
        ),
        "relative-corpus": _attempt(lambda: Path("corpus/cases/case-ground-001.json").read_text()),
        "load-cases": _attempt(_load_cases),
        "cwd-entries": sorted(path.name for path in Path.cwd().iterdir()),
    }
    sys_stdout(report)


def _load_cases() -> None:
    from patchpilot_intelligence_evals.corpus import load_cases

    loaded = load_cases()
    if loaded:
        return
    raise PermissionError(13, "candidate-boundary")


def sys_stdout(report: dict[str, object]) -> None:
    import sys

    sys.stdout.write(json.dumps(report, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
