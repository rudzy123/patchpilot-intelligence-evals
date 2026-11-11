"""Synthetic adapter fixture. The live boundary is skipped when it is unavailable."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from patchpilot_intelligence_evals.corpus import load_cases
from patchpilot_intelligence_evals.hardened_execution import host_supports_boundary
from patchpilot_intelligence_evals.protocol import build_request
from patchpilot_intelligence_evals.runtime_adapter_contract import execution_configuration
from patchpilot_intelligence_evals.runtime_cache import (
    place_quarantine as place_runtime,
)
from patchpilot_intelligence_evals.runtime_cache import (
    promote_attempt as promote_runtime,
)
from patchpilot_intelligence_evals.schemas import repo_root
from patchpilot_intelligence_evals.synthetic_runtime_adapter import invoke_synthetic

_DIGEST = "b" * 64
_LIBRARY = "libonnxruntime.so.1.31.1"
_FIXTURE = repo_root() / "tests" / "sandbox_fixtures" / "synthetic_runtime_adapter.py"


def _request() -> dict[str, object]:
    return build_request(load_cases()[0], _DIGEST)


def _runtime(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    root = tmp_path / "runtime"
    root.mkdir()
    library = b"\x7fELFsynthetic-runtime"
    license_bytes = b"synthetic-mit\n"
    notice = b"synthetic-notice\n"
    identity = b'{"runtimeId":"onnxruntime","telemetry":"disabled","versionTag":"v1.31.1"}'
    files = {
        _LIBRARY: library,
        "LICENSE": license_bytes,
        "ThirdPartyNotices.txt": notice,
        "runtime-identity.json": identity,
    }
    roles = {
        _LIBRARY: ("shared-library", "elf"),
        "LICENSE": ("license", "not-executable"),
        "ThirdPartyNotices.txt": ("notice", "not-executable"),
        "runtime-identity.json": ("configuration", "not-executable"),
    }
    place_runtime(root, "runtime-ok", files)
    expected = [
        {
            "fileName": name,
            "role": roles[name][0],
            "expectedBytes": len(payload),
            "upstreamSha256": hashlib.sha256(payload).hexdigest(),
            "executableFormat": roles[name][1],
        }
        for name, payload in files.items()
    ]
    manifest = promote_runtime(root, "runtime-ok", expected)
    return root / "verified" / "runtime-ok", manifest


def test_synthetic_fixture_runs_through_the_hardened_boundary(tmp_path: Path) -> None:
    if not host_supports_boundary():
        pytest.skip("unsupported-capability")
    runtime_dir, runtime_manifest = _runtime(tmp_path)
    result = invoke_synthetic(
        fixture=_FIXTURE,
        request=_request(),
        execution=execution_configuration(),
        runtime_directory=runtime_dir,
        runtime_manifest=runtime_manifest,
        config_dir=tmp_path / "config",
    )
    assert result["status"] == "ok"
    assert result["responseStatus"] == "unavailable"
    assert result["realModelExecuted"] is False
    assert result["productionReady"] is False
    assert result["argvUsesShell"] is False
    staged = list((tmp_path / "config").iterdir())
    assert {path.name for path in staged} == {"execution.json", "request.json"}
